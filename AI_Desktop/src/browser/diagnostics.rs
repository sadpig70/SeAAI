use serde::{Deserialize, Serialize};
use std::net::{TcpListener, ToSocketAddrs};

const WINSOCK_MARKERS: &[&str] = &[
    "WSALookupServiceBegin failed with: 10108",
    "WSALookupServiceBegin failed with: 10106",
    "BuildSecurityDescriptor",
];
const ACCESS_DENIED_MARKERS: &[&str] = &[
    "platform_channel.cc:170",
    "액세스가 거부되었습니다. (0x5)",
];

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum BrowserDiagnosis {
    DnsFailure,
    WinsockProviderFault,
    SocketBindFailure,
    BrowserBinaryMissing,
    DriverMissing,
    CdpAttachFailed,
    ProfileLockConflict,
    EdgePlatformChannelAccessDenied,
    HeadlessTimeout,
    ActionRefNotFound,
    ActionExecutionFailed,
    UploadPathDenied,
    RemoteCdpAuthFailed,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserHealthProbe {
    pub ok: bool,
    pub mode: String,
    pub diagnosis: Option<BrowserDiagnosis>,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserSocketHealth {
    pub getaddrinfo: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,
    pub bind: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bind_port: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bind_message: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserDoctorReport {
    pub probe_source: String,
    pub socket_health: BrowserSocketHealth,
    pub diagnosis: Option<BrowserDiagnosis>,
    pub recovery_advice: Vec<String>,
}

pub fn classify_browser_diagnosis(stderr: &str, timed_out: bool) -> Option<BrowserDiagnosis> {
    if WINSOCK_MARKERS.iter().any(|marker| stderr.contains(marker)) {
        return Some(BrowserDiagnosis::WinsockProviderFault);
    }
    if ACCESS_DENIED_MARKERS.iter().any(|marker| stderr.contains(marker)) {
        return Some(BrowserDiagnosis::EdgePlatformChannelAccessDenied);
    }
    if stderr.contains("NameResolutionError") || stderr.contains("getaddrinfo failed") {
        return Some(BrowserDiagnosis::DnsFailure);
    }
    if stderr.contains("Unable to bind to IPv4 or IPv6") {
        return Some(BrowserDiagnosis::SocketBindFailure);
    }
    if timed_out {
        return Some(BrowserDiagnosis::HeadlessTimeout);
    }
    None
}

pub fn probe_socket_health() -> BrowserSocketHealth {
    let mut result = BrowserSocketHealth {
        getaddrinfo: "ok".to_string(),
        message: None,
        bind: "ok".to_string(),
        bind_port: None,
        bind_message: None,
    };

    if let Err(err) = ("127.0.0.1", 80).to_socket_addrs() {
        result.getaddrinfo = format!("error:{}", err.raw_os_error().unwrap_or(-1));
        result.message = Some(err.to_string());
    }

    match TcpListener::bind(("127.0.0.1", 0)) {
        Ok(listener) => {
            result.bind_port = listener.local_addr().ok().map(|addr| addr.port());
        }
        Err(err) => {
            result.bind = format!("error:{}", err.raw_os_error().unwrap_or(-1));
            result.bind_message = Some(err.to_string());
        }
    }

    result
}

pub fn diagnose_socket_health(socket_health: &BrowserSocketHealth) -> Option<BrowserDiagnosis> {
    if socket_health.getaddrinfo != "ok" {
        return Some(BrowserDiagnosis::DnsFailure);
    }
    if socket_health.bind != "ok" {
        if socket_health.bind.starts_with("error:10106") || socket_health.bind.starts_with("error:10108") {
            return Some(BrowserDiagnosis::WinsockProviderFault);
        }
        return Some(BrowserDiagnosis::SocketBindFailure);
    }
    None
}

pub fn build_recovery_advice(diagnosis: Option<&BrowserDiagnosis>, socket_health: &BrowserSocketHealth) -> Vec<String> {
    let mut advice = Vec::new();

    if socket_health.getaddrinfo != "ok" {
        advice.push("Fix DNS resolution in the current host session before retrying external navigation.".to_string());
    }
    if socket_health.bind != "ok" {
        advice.push("Repair Winsock/socket provider state for this process; local bind must succeed before Selenium or CDP fallback can work.".to_string());
    }

    match diagnosis {
        Some(BrowserDiagnosis::WinsockProviderFault) => {
            advice.push("Reset Winsock/TCP stack and restart the operator session if this process still carries stale network provider state.".to_string());
        }
        Some(BrowserDiagnosis::SocketBindFailure) => {
            advice.push("Treat this as a host blocker; browser automation cannot allocate a free local port until bind succeeds in this exact process context.".to_string());
        }
        Some(BrowserDiagnosis::DnsFailure) => {
            advice.push("Confirm that the current session resolves external hosts before retrying live navigation or screenshot flows.".to_string());
        }
        _ => {}
    }

    advice.dedup();
    advice
}

pub fn probe_browser_doctor() -> BrowserDoctorReport {
    let socket_health = probe_socket_health();
    let diagnosis = diagnose_socket_health(&socket_health);
    let recovery_advice = build_recovery_advice(diagnosis.as_ref(), &socket_health);

    BrowserDoctorReport {
        probe_source: "rust-browser-state-cli".to_string(),
        socket_health,
        diagnosis,
        recovery_advice,
    }
}

#[cfg(test)]
mod tests {
    use super::{build_recovery_advice, classify_browser_diagnosis, diagnose_socket_health, BrowserDiagnosis, BrowserSocketHealth};

    #[test]
    fn classifies_winsock() {
        let stderr = "WSALookupServiceBegin failed with: 10106";
        assert_eq!(
            classify_browser_diagnosis(stderr, false),
            Some(BrowserDiagnosis::WinsockProviderFault)
        );
    }

    #[test]
    fn classifies_timeout() {
        assert_eq!(
            classify_browser_diagnosis("", true),
            Some(BrowserDiagnosis::HeadlessTimeout)
        );
    }

    #[test]
    fn diagnoses_socket_bind_failure() {
        let socket_health = BrowserSocketHealth {
            getaddrinfo: "ok".to_string(),
            message: None,
            bind: "error:10106".to_string(),
            bind_port: None,
            bind_message: Some("winsock broken".to_string()),
        };
        assert_eq!(
            diagnose_socket_health(&socket_health),
            Some(BrowserDiagnosis::WinsockProviderFault)
        );
        let advice = build_recovery_advice(Some(&BrowserDiagnosis::WinsockProviderFault), &socket_health);
        assert!(advice.iter().any(|item| item.contains("Winsock")));
    }
}
