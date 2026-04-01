use std::collections::{BTreeSet, HashMap, HashSet, VecDeque};
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{bail, Result};
use hmac::{Hmac, Mac};
use serde::Serialize;
use sha2::{Digest, Sha256};

use crate::protocol::PgMessageParams;

type HmacSha256 = Hmac<Sha256>;

// ── Configuration ──

const MAX_ROOM_HISTORY: usize = 1000;      // 방별 메시지 버퍼 최대 크기
const MAX_INBOX_SIZE: usize = 500;          // 에이전트별 inbox 최대 크기 (backpressure)
const MAX_ROOMS: usize = 100;               // 최대 방 수
const MSG_TTL_SECS: u64 = 3600;             // 메시지 TTL: 1시간

// ── Data Structures ──

#[derive(Debug, Clone, Serialize)]
pub struct ChatMessage {
    pub id: String,
    pub from: String,
    pub to: Vec<String>,
    pub room_id: String,
    pub intent: String,
    pub body: String,
    pub ts: f64,
    pub sig: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct DeliveryResult {
    pub delivered_to: Vec<String>,
    pub room_id: String,
    pub message_id: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct AgentMailbox {
    pub agent_id: String,
    pub messages: Vec<ChatMessage>,
}

#[derive(Debug, Clone, Serialize)]
pub struct RoomState {
    pub room_id: String,
    pub members: Vec<String>,
    pub message_count: usize,
    pub agent_count: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct AgentInfo {
    pub agent_id: String,
    pub capabilities: Vec<String>,
    pub registered_at: f64,
    pub rooms: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct RegistryState {
    pub agents: Vec<AgentInfo>,
    pub total: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct CatchupResult {
    pub agent_id: String,
    pub room_id: String,
    pub messages: Vec<ChatMessage>,
    pub total_in_buffer: usize,
}

pub struct SendMessageRequest {
    pub id: Option<String>,
    pub from: String,
    pub room_id: String,
    pub payload: PgMessageParams,
    pub sig: String,
}

// ── Topic Subscription ──

#[derive(Debug, Clone)]
struct Subscription {
    topics: HashSet<String>,  // empty = subscribe to all (wildcard)
}

// ── Hub Core ──

pub struct ChatroomHub {
    authenticated_agents: HashSet<String>,
    agent_registry: HashMap<String, AgentInfo>,          // L2: Discovery
    rooms: HashMap<String, BTreeSet<String>>,
    inboxes: HashMap<String, VecDeque<ChatMessage>>,     // VecDeque for efficient front-pop
    room_history: HashMap<String, VecDeque<ChatMessage>>, // Ring buffer for catch-up
    subscriptions: HashMap<String, Subscription>,         // L3: Topic filtering
    seen_messages: HashMap<String, u64>,                  // L3: Dedup (msg_id → timestamp)
    shared_secret: String,
    msg_counter: u64,                                     // Auto-increment for unique msg_id
}

impl ChatroomHub {
    pub fn new() -> Self {
        Self {
            authenticated_agents: HashSet::new(),
            agent_registry: HashMap::new(),
            rooms: HashMap::new(),
            inboxes: HashMap::new(),
            room_history: HashMap::new(),
            subscriptions: HashMap::new(),
            seen_messages: HashMap::new(),
            shared_secret: "seaai-shared-secret".to_string(),
            msg_counter: 0,
        }
    }

    // ── L2: Agent Registration + Discovery ──

    pub fn register_agent(&mut self, agent_id: &str, token: &str, capabilities: Vec<String>) -> Result<()> {
        let expected = self.build_agent_token(agent_id);
        if token != expected {
            bail!("invalid token for agent {}", agent_id);
        }

        self.authenticated_agents.insert(agent_id.to_string());
        self.inboxes.entry(agent_id.to_string()).or_default();

        // Registry entry
        self.agent_registry.insert(agent_id.to_string(), AgentInfo {
            agent_id: agent_id.to_string(),
            capabilities,
            registered_at: self.current_timestamp_f64(),
            rooms: vec![],
        });

        // Default subscription: all topics (wildcard)
        self.subscriptions.insert(agent_id.to_string(), Subscription {
            topics: HashSet::new(),
        });

        Ok(())
    }

    pub fn discover_agents(&self, capability: Option<&str>) -> RegistryState {
        let agents: Vec<AgentInfo> = match capability {
            Some(cap) => self.agent_registry.values()
                .filter(|a| a.capabilities.iter().any(|c| c.contains(cap)))
                .cloned()
                .collect(),
            None => self.agent_registry.values().cloned().collect(),
        };
        let total = agents.len();
        RegistryState { agents, total }
    }

    // ── L3: Topic Subscription ──

    pub fn subscribe_topic(&mut self, agent_id: &str, topic: &str) -> Result<()> {
        self.ensure_authenticated(agent_id)?;
        self.subscriptions
            .entry(agent_id.to_string())
            .or_insert_with(|| Subscription { topics: HashSet::new() })
            .topics
            .insert(topic.to_string());
        Ok(())
    }

    pub fn unsubscribe_topic(&mut self, agent_id: &str, topic: &str) -> Result<()> {
        self.ensure_authenticated(agent_id)?;
        if let Some(sub) = self.subscriptions.get_mut(agent_id) {
            sub.topics.remove(topic);
        }
        Ok(())
    }

    fn matches_subscription(&self, agent_id: &str, intent: &str) -> bool {
        match self.subscriptions.get(agent_id) {
            None => true,  // no subscription = receive all
            Some(sub) if sub.topics.is_empty() => true,  // wildcard
            Some(sub) => sub.topics.contains(intent),
        }
    }

    // ── Room Management ──

    pub fn join_room(&mut self, agent_id: &str, room_id: &str) -> Result<()> {
        self.ensure_authenticated(agent_id)?;

        if self.rooms.len() >= MAX_ROOMS && !self.rooms.contains_key(room_id) {
            bail!("maximum room limit ({}) reached", MAX_ROOMS);
        }

        self.rooms
            .entry(room_id.to_string())
            .or_default()
            .insert(agent_id.to_string());

        // Update registry
        if let Some(info) = self.agent_registry.get_mut(agent_id) {
            if !info.rooms.contains(&room_id.to_string()) {
                info.rooms.push(room_id.to_string());
            }
        }

        Ok(())
    }

    pub fn leave_room(&mut self, agent_id: &str, room_id: &str) -> Result<()> {
        self.ensure_authenticated(agent_id)?;
        let Some(members) = self.rooms.get_mut(room_id) else {
            bail!("room {} does not exist", room_id);
        };

        members.remove(agent_id);

        // Update registry
        if let Some(info) = self.agent_registry.get_mut(agent_id) {
            info.rooms.retain(|r| r != room_id);
        }

        if members.is_empty() {
            self.rooms.remove(room_id);
            self.room_history.remove(room_id);
        }
        Ok(())
    }

    // ── Messaging with L3 features ──

    pub fn send_message(&mut self, request: SendMessageRequest) -> Result<DeliveryResult> {
        self.ensure_authenticated(&request.from)?;
        self.ensure_room_member(&request.from, &request.room_id)?;

        let computed_sig = self.build_message_signature(&request.payload)?;
        if request.sig != computed_sig {
            bail!("invalid message signature");
        }

        let message_id = request
            .id
            .unwrap_or_else(|| {
                self.msg_counter += 1;
                format!("msg-{}-{}-{}", request.from, self.current_timestamp_millis(), self.msg_counter)
            });

        // L3: Dedup check
        if self.seen_messages.contains_key(&message_id) {
            bail!("duplicate message id {}", message_id);
        }
        self.seen_messages.insert(message_id.clone(), self.current_timestamp());
        self.gc_seen_messages();

        // Broadcast to all room members except sender, filtered by subscription
        let members = self.rooms.get(&request.room_id).cloned().unwrap_or_default();
        let recipients: Vec<String> = members
            .into_iter()
            .filter(|m| m != &request.from)
            .filter(|m| self.matches_subscription(m, &request.payload.intent))
            .collect();

        let message = ChatMessage {
            id: message_id.clone(),
            from: request.from,
            to: recipients.clone(),
            room_id: request.room_id.clone(),
            intent: request.payload.intent,
            body: request.payload.body,
            ts: request.payload.ts,
            sig: request.sig,
        };

        // Deliver to inboxes with backpressure
        for recipient in &recipients {
            let inbox = self.inboxes.entry(recipient.clone()).or_default();
            if inbox.len() >= MAX_INBOX_SIZE {
                // Backpressure: drop oldest messages
                while inbox.len() >= MAX_INBOX_SIZE {
                    inbox.pop_front();
                }
            }
            inbox.push_back(message.clone());
        }

        // Room history buffer (ring buffer)
        let history = self.room_history
            .entry(request.room_id.clone())
            .or_default();
        if history.len() >= MAX_ROOM_HISTORY {
            history.pop_front();
        }
        history.push_back(message);

        Ok(DeliveryResult {
            delivered_to: recipients,
            room_id: request.room_id,
            message_id,
        })
    }

    // ── L1: Catch-up (message buffer for late joiners) ──

    pub fn catchup(&self, agent_id: &str, room_id: &str, count: usize) -> Result<CatchupResult> {
        self.ensure_authenticated(agent_id)?;
        let history = self.room_history.get(room_id)
            .map(|h| h.as_slices())
            .unwrap_or((&[], &[]));

        let all: Vec<&ChatMessage> = history.0.iter().chain(history.1.iter()).collect();
        let total = all.len();
        let start = if total > count { total - count } else { 0 };
        let messages: Vec<ChatMessage> = all[start..].iter().map(|m| (*m).clone()).collect();

        Ok(CatchupResult {
            agent_id: agent_id.to_string(),
            room_id: room_id.to_string(),
            messages,
            total_in_buffer: total,
        })
    }

    // ── Read inbox (drain) ──

    pub fn list_rooms(&self) -> Vec<String> {
        self.rooms.keys().cloned().collect()
    }

    pub fn room_state(&self, room_id: &str) -> Result<RoomState> {
        let Some(members) = self.rooms.get(room_id) else {
            bail!("room {} does not exist", room_id);
        };

        let message_count = self.room_history.get(room_id).map_or(0, VecDeque::len);
        Ok(RoomState {
            room_id: room_id.to_string(),
            members: members.iter().cloned().collect(),
            message_count,
            agent_count: self.authenticated_agents.len(),
        })
    }

    pub fn agent_messages(&mut self, agent_id: &str) -> Result<AgentMailbox> {
        self.ensure_authenticated(agent_id)?;
        let messages: Vec<ChatMessage> = self.inboxes
            .get_mut(agent_id)
            .map(|inbox| inbox.drain(..).collect())
            .unwrap_or_default();
        Ok(AgentMailbox {
            agent_id: agent_id.to_string(),
            messages,
        })
    }

    // ── Crypto ──

    pub fn build_agent_token(&self, agent_id: &str) -> String {
        self.hmac_hex(agent_id.as_bytes())
    }

    pub fn build_message_signature(&self, payload: &PgMessageParams) -> Result<String> {
        let mut hasher = Sha256::new();
        hasher.update(payload.body.as_bytes());
        let ts_millis = (payload.ts * 1000.0) as i64;
        hasher.update(ts_millis.to_string().as_bytes());
        let digest = hasher.finalize();
        Ok(self.hmac_hex(digest.as_slice()))
    }

    // ── Internal ──

    fn ensure_authenticated(&self, agent_id: &str) -> Result<()> {
        if !self.authenticated_agents.contains(agent_id) {
            bail!("agent {} is not authenticated", agent_id);
        }
        Ok(())
    }

    fn ensure_room_member(&self, agent_id: &str, room_id: &str) -> Result<()> {
        let Some(members) = self.rooms.get(room_id) else {
            bail!("room {} does not exist", room_id);
        };
        if !members.contains(agent_id) {
            bail!("agent {} is not a member of room {}", agent_id, room_id);
        }
        Ok(())
    }

    fn hmac_hex(&self, bytes: &[u8]) -> String {
        let mut mac = HmacSha256::new_from_slice(self.shared_secret.as_bytes())
            .expect("HMAC accepts any key length");
        mac.update(bytes);
        let result = mac.finalize().into_bytes();
        hex::encode(result)
    }

    fn current_timestamp(&self) -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0)
    }

    fn current_timestamp_millis(&self) -> u128 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_millis())
            .unwrap_or(0)
    }

    fn current_timestamp_f64(&self) -> f64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs_f64())
            .unwrap_or(0.0)
    }

    fn gc_seen_messages(&mut self) {
        let now = self.current_timestamp();
        self.seen_messages.retain(|_, ts| now - *ts < MSG_TTL_SECS);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn registered_hub() -> ChatroomHub {
        let mut hub = ChatroomHub::new();
        let aion = hub.build_agent_token("Aion");
        let clneo = hub.build_agent_token("ClNeo");
        let nael = hub.build_agent_token("NAEL");
        hub.register_agent("Aion", &aion, vec!["memory".into()]).unwrap();
        hub.register_agent("ClNeo", &clneo, vec!["creation".into()]).unwrap();
        hub.register_agent("NAEL", &nael, vec!["safety".into()]).unwrap();
        hub.join_room("Aion", "design-room").unwrap();
        hub.join_room("ClNeo", "design-room").unwrap();
        hub.join_room("NAEL", "ops-room").unwrap();
        hub
    }

    fn send_msg(hub: &mut ChatroomHub, from: &str, room: &str, body: &str) -> DeliveryResult {
        let payload = PgMessageParams {
            intent: "chat".to_string(),
            body: body.to_string(),
            ts: 42.0,
        };
        let sig = hub.build_message_signature(&payload).unwrap();
        hub.send_message(SendMessageRequest {
            id: None, from: from.to_string(), room_id: room.to_string(), payload, sig,
        }).unwrap()
    }

    #[test]
    fn any_agent_can_register() {
        let mut hub = ChatroomHub::new();
        let token = hub.build_agent_token("BrandNewAgent");
        assert!(hub.register_agent("BrandNewAgent", &token, vec![]).is_ok());
    }

    #[test]
    fn broadcasts_to_all_room_members() {
        let mut hub = registered_hub();
        let result = send_msg(&mut hub, "Aion", "design-room", "hello");
        assert_eq!(result.delivered_to, vec!["ClNeo".to_string()]);
        assert_eq!(hub.agent_messages("ClNeo").unwrap().messages.len(), 1);
        assert_eq!(hub.agent_messages("NAEL").unwrap().messages.len(), 0);
    }

    #[test]
    fn rejects_invalid_signature() {
        let mut hub = registered_hub();
        let err = hub.send_message(SendMessageRequest {
            id: None, from: "Aion".into(), room_id: "design-room".into(),
            payload: PgMessageParams { intent: "chat".into(), body: "tampered".into(), ts: 7.0 },
            sig: "bad".into(),
        }).unwrap_err();
        assert!(err.to_string().contains("invalid message signature"));
    }

    #[test]
    fn inbox_drains_on_read() {
        let mut hub = registered_hub();
        send_msg(&mut hub, "Aion", "design-room", "drain test");
        assert_eq!(hub.agent_messages("ClNeo").unwrap().messages.len(), 1);
        assert_eq!(hub.agent_messages("ClNeo").unwrap().messages.len(), 0);
    }

    #[test]
    fn discovery_finds_agents_by_capability() {
        let hub = registered_hub();
        let result = hub.discover_agents(Some("creation"));
        assert_eq!(result.total, 1);
        assert_eq!(result.agents[0].agent_id, "ClNeo");

        let all = hub.discover_agents(None);
        assert_eq!(all.total, 3);
    }

    #[test]
    fn catchup_returns_recent_messages() {
        let mut hub = registered_hub();
        for i in 0..5 {
            let payload = PgMessageParams {
                intent: "chat".to_string(),
                body: format!("msg {}", i),
                ts: i as f64,
            };
            let sig = hub.build_message_signature(&payload).unwrap();
            let _ = hub.send_message(SendMessageRequest {
                id: Some(format!("m{}", i)),
                from: "Aion".into(), room_id: "design-room".into(), payload, sig,
            });
        }
        let catchup = hub.catchup("ClNeo", "design-room", 3).unwrap();
        assert_eq!(catchup.messages.len(), 3);
        assert_eq!(catchup.total_in_buffer, 5);
        assert_eq!(catchup.messages[0].body, "msg 2");  // last 3
    }

    #[test]
    fn backpressure_drops_oldest() {
        let mut hub = ChatroomHub::new();
        let ta = hub.build_agent_token("A");
        let tb = hub.build_agent_token("B");
        hub.register_agent("A", &ta, vec![]).unwrap();
        hub.register_agent("B", &tb, vec![]).unwrap();
        hub.join_room("A", "r").unwrap();
        hub.join_room("B", "r").unwrap();

        // Send MAX_INBOX_SIZE + 10 messages
        for i in 0..(MAX_INBOX_SIZE + 10) {
            let payload = PgMessageParams {
                intent: "chat".into(), body: format!("m{}", i), ts: i as f64,
            };
            let sig = hub.build_message_signature(&payload).unwrap();
            let _ = hub.send_message(SendMessageRequest {
                id: Some(format!("bp{}", i)),
                from: "A".into(), room_id: "r".into(), payload, sig,
            });
        }

        let inbox = hub.agent_messages("B").unwrap();
        assert!(inbox.messages.len() <= MAX_INBOX_SIZE);
        // Most recent messages should be preserved
        let last = &inbox.messages.last().unwrap().body;
        assert!(last.contains(&format!("{}", MAX_INBOX_SIZE + 9)));
    }

    #[test]
    fn topic_subscription_filters_messages() {
        let mut hub = registered_hub();
        hub.subscribe_topic("ClNeo", "pgtp").unwrap();

        // Send a "chat" intent message — ClNeo subscribed to "pgtp" only
        let payload_chat = PgMessageParams {
            intent: "chat".into(), body: "chat msg".into(), ts: 1.0,
        };
        let sig = hub.build_message_signature(&payload_chat).unwrap();
        let r1 = hub.send_message(SendMessageRequest {
            id: Some("t1".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload: payload_chat, sig,
        }).unwrap();
        assert!(!r1.delivered_to.contains(&"ClNeo".to_string())); // filtered out

        // Send a "pgtp" intent message — ClNeo should receive
        let payload_pgtp = PgMessageParams {
            intent: "pgtp".into(), body: "pgtp msg".into(), ts: 2.0,
        };
        let sig2 = hub.build_message_signature(&payload_pgtp).unwrap();
        let r2 = hub.send_message(SendMessageRequest {
            id: Some("t2".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload: payload_pgtp, sig: sig2,
        }).unwrap();
        assert!(r2.delivered_to.contains(&"ClNeo".to_string())); // passes filter
    }

    #[test]
    fn dedup_rejects_duplicate_message_id() {
        let mut hub = registered_hub();
        let payload = PgMessageParams {
            intent: "chat".into(), body: "dup test".into(), ts: 1.0,
        };
        let sig = hub.build_message_signature(&payload).unwrap();

        // First send: OK
        let r1 = hub.send_message(SendMessageRequest {
            id: Some("dup1".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload: payload.clone(), sig: sig.clone(),
        });
        assert!(r1.is_ok());

        // Second send with same ID: rejected
        let r2 = hub.send_message(SendMessageRequest {
            id: Some("dup1".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload, sig,
        });
        assert!(r2.is_err());
        assert!(r2.unwrap_err().to_string().contains("duplicate"));
    }
}
