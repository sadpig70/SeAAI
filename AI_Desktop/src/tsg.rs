// src/tsg.rs

use serde::{Deserialize, Serialize};
use serde_json::Value;
use tracing::{info, warn};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum RiskLevel {
    Low,      // 읽기 전용, 정보 조회 (예: SystemInfo)
    Medium,   // 가벼운 변경, 네트워크 요청 (예: WebSearch)
    High,     // 삭제, 종료, 시스템 변경 (예: File Delete, Process Kill)
    Critical, // 포맷, 시스템 설정 건드리기 (차단 권장)
}

#[derive(Debug, Clone)]
pub struct TSGPolicy {
    // 간단한 차단 키워드 목록 (MVP)
    pub blocked_keywords: Vec<String>,
}

impl Default for TSGPolicy {
    fn default() -> Self {
        Self {
            blocked_keywords: vec![
                "rm -rf".to_string(),
                "/windows/system32".to_string(),
                "format c:".to_string(),
                "drop table".to_string(), // SQL Injection 예방
            ],
        }
    }
}

pub struct TrustSecurityGateway {
    policy: TSGPolicy,
}

impl TrustSecurityGateway {
    pub fn new() -> Self {
        Self {
            policy: TSGPolicy::default(),
        }
    }

    /// 요청을 검사하여 실행 가능 여부 판단
    pub fn authorize(&self, tool_name: &str, input: &Value) -> Result<(), String> {
        let input_str = input.to_string().to_lowercase();

        // 1. 키워드 기반 차단 (Injection 방어)
        for keyword in &self.policy.blocked_keywords {
            if input_str.contains(keyword) {
                warn!(
                    tool = tool_name,
                    keyword = keyword,
                    "🚫 TSG Blocked dangerous keyword"
                );
                return Err(format!(
                    "TSG Blocked: Input contains restricted keyword '{}'",
                    keyword
                ));
            }
        }

        // 2. 도구별 리스크 평가 (Risk Assessment)
        let risk = self.assess_risk(tool_name, input);

        match risk {
            RiskLevel::Low | RiskLevel::Medium => {
                info!(tool=tool_name, risk=?risk, "✅ TSG Authorized");
                Ok(())
            }
            RiskLevel::High => {
                // MVP: High 리스크는 명시적인 'force' 파라미터나 별도 승인이 없으면 차단
                // 클라이언트가 "force": true를 보내도록 유도하거나, UI에서 승인해야 함
                if let Some(force) = input.get("force_execute").and_then(|v| v.as_bool()) {
                    if force {
                        warn!(
                            tool = tool_name,
                            "⚠️ TSG High Risk Authorized (Force Execution)"
                        );
                        return Ok(());
                    }
                }
                Err(
                    "TSG: High Risk Operation. Requires 'force_execute': true or Human Approval."
                        .to_string(),
                )
            }
            RiskLevel::Critical => {
                Err("TSG: Critical Risk Operation. Automatically Blocked.".to_string())
            }
        }
    }

    /// 도구와 인자에 따른 리스크 레벨 판단
    fn assess_risk(&self, tool_name: &str, input: &Value) -> RiskLevel {
        match tool_name {
            // OS 제어 및 파일 시스템
            "process_manager" => {
                let op = input.get("op").and_then(|v| v.as_str()).unwrap_or("");
                match op {
                    "kill" | "close" => RiskLevel::High,
                    "spawn" => RiskLevel::Medium, // 실행은 주의 필요
                    _ => RiskLevel::Low,
                }
            }
            "file_manager" => {
                let op = input.get("op").and_then(|v| v.as_str()).unwrap_or("");
                match op {
                    "delete" | "write" | "unzip" => RiskLevel::High,
                    "read" => RiskLevel::Medium, // 민감 파일 읽기 가능성
                    _ => RiskLevel::Low,
                }
            }
            // 네트워크
            "network_api" => RiskLevel::Medium, // 외부 유출 가능성
            // 안전한 도구들
            "system_info" | "web_search" => RiskLevel::Low,
            _ => RiskLevel::Medium, // 기본값
        }
    }

    /// 출력 데이터 마스킹 (PII 보호) - 예시 구현
    pub fn filter_output(&self, output: &Value) -> Value {
        // 실제 구현 시에는 재귀적으로 문자열을 탐색하며 이메일/전화번호 마스킹 수행
        // MVP에서는 단순히 로그에 "Filtered"라고만 남김
        output.clone()
    }
}
