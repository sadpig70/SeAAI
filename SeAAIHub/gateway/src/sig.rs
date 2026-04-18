use hmac::{Hmac, Mac};
use sha2::{Digest, Sha256};

type HmacSha256 = Hmac<Sha256>;

/// Python AS-IS 동일:
///   ts_ms = str(int(ts * 1000))
///   inner = sha256(body.utf8() + ts_ms.utf8()).digest()
///   sig = hmac_sha256(secret, inner).hex()
pub fn build_sig(secret: &[u8], body: &str, ts: f64) -> String {
    let ts_ms = (ts * 1000.0) as i64; // truncation == Python int()
    let ts_ms_s = ts_ms.to_string();

    let mut inner = Sha256::new();
    inner.update(body.as_bytes());
    inner.update(ts_ms_s.as_bytes());
    let digest = inner.finalize();

    let mut mac = HmacSha256::new_from_slice(secret).expect("hmac key");
    mac.update(&digest);
    hex::encode(mac.finalize().into_bytes())
}

/// Token: HMAC-SHA256(secret, agent_id)
pub fn build_token(secret: &[u8], agent_id: &str) -> String {
    let mut mac = HmacSha256::new_from_slice(secret).expect("hmac key");
    mac.update(agent_id.as_bytes());
    hex::encode(mac.finalize().into_bytes())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sig_is_deterministic() {
        let a = build_sig(b"seaai-shared-secret", "hello", 1712847600.123456);
        let b = build_sig(b"seaai-shared-secret", "hello", 1712847600.123456);
        assert_eq!(a, b);
        assert_eq!(a.len(), 64); // sha256 hex
    }

    #[test]
    fn sig_varies_by_input() {
        let a = build_sig(b"seaai-shared-secret", "hello", 1.0);
        let b = build_sig(b"seaai-shared-secret", "hello", 2.0);
        let c = build_sig(b"seaai-shared-secret", "world", 1.0);
        assert_ne!(a, b);
        assert_ne!(a, c);
    }

    #[test]
    fn token_has_expected_length() {
        let t = build_token(b"seaai-shared-secret", "alice");
        assert_eq!(t.len(), 64);
    }
}
