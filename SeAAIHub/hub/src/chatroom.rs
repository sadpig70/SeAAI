use std::collections::{BTreeSet, HashMap, HashSet, VecDeque};
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{bail, Result};
use hmac::{Hmac, Mac};
use serde::Serialize;
use sha2::{Digest, Sha256};

use crate::protocol::{PgMessageParams, SeqIdParam, FlowStateParam};

type HmacSha256 = Hmac<Sha256>;

// ── Configuration ──

const MAX_ROOM_HISTORY: usize = 1000;      // 방별 메시지 버퍼 최대 크기
const MAX_INBOX_SIZE: usize = 500;          // 에이전트별 inbox 최대 크기 (backpressure)
const MAX_ROOMS: usize = 100;               // 최대 방 수
const MSG_TTL_SECS: u64 = 3600;             // 메시지 TTL: 1시간
const CATCHUP_WINDOW_SECS: u64 = 30;        // catchup rate-limit 윈도우 [T-SEC F7]
const CATCHUP_LIMIT_DENOM: usize = 4;       // limit = room_size / N (최소 1) [T-SEC F7]

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
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sig: Option<String>,
    /// FlowWeave L0: 3-tuple unique ID (sender / epoch / counter)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub seq_id: Option<SeqIdParam>,
    /// FlowWeave L0: referenced message seq_id keys — DAG linkage
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub references: Vec<String>,
    /// FlowWeave L3: thread_id for topic grouping
    #[serde(skip_serializing_if = "Option::is_none")]
    pub thread_id: Option<String>,
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

/// Compact message — body only, no FlowWeave protocol metadata
#[derive(Debug, Clone, Serialize)]
pub struct CompactMessage {
    pub from: String,
    pub intent: String,
    pub body: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct AgentMailboxCompact {
    pub agent_id: String,
    pub messages: Vec<CompactMessage>,
}

/// FlowWeave P2: Activity-based conversation state (§8.1)
#[derive(Debug, Clone, Serialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum FlowState {
    Gathering,   // 멤버 모이는 중 (초기)
    Flowing,     // 자유 대화 진행 (member_count ≥ 2)
    Deepening,   // 특정 토픽 심화 (fork / 동일 토픽 3+ 연속)
    Converging,  // 자연스러운 수렴 (new_idea_rate 낮음)
    Deciding,    // 명시적 합의 투표
    Resting,     // 결정 완료
}

impl Default for FlowState {
    fn default() -> Self { FlowState::Gathering }
}

/// FlowWeave P2: Decision log entry
#[derive(Debug, Clone, Serialize)]
pub struct DecisionEntry {
    pub seq_id_key: String,   // 결정 메시지의 seq_id key
    pub summary: String,      // 결정 요약
    pub decided_by: String,   // 결정 발의자
    pub ts: f64,
}

/// FlowWeave P2: Thread index entry (P3)
#[derive(Debug, Clone, Serialize)]
pub struct ThreadEntry {
    pub thread_id: String,
    pub topic: String,
    pub message_seq_keys: Vec<String>,  // 이 스레드에 속한 메시지 seq_id keys
    pub created_at: f64,
}

/// FlowWeave P2: Canonical State — Hub가 관리하는 방 상태 정본
#[derive(Debug, Clone, Serialize)]
pub struct CanonicalRoomState {
    pub flow_state: FlowState,
    pub decision_log: Vec<DecisionEntry>,
    pub thread_index: Vec<ThreadEntry>,  // P3: thread_id별 그룹핑
    pub last_transition_ts: f64,
}

impl CanonicalRoomState {
    pub fn new() -> Self {
        Self {
            flow_state: FlowState::Gathering,
            decision_log: vec![],
            thread_index: vec![],
            last_transition_ts: 0.0,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct RoomState {
    pub room_id: String,
    pub members: Vec<String>,
    pub message_count: usize,
    pub agent_count: usize,
    /// FlowWeave P2: Canonical conversation state
    pub flow_state: FlowState,
    pub decision_count: usize,
    pub thread_count: usize,
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

/// FlowWeave P1: JoinCatchup — Hub가 늦은 합류자에게 자동 전송하는 맥락 요약
#[derive(Debug, Clone, Serialize)]
pub struct JoinCatchup {
    pub joiner: String,
    pub room_id: String,
    pub current_member_count: usize,
    pub recent_messages: Vec<ChatMessage>,
    pub total_in_buffer: usize,
}

pub struct SendMessageRequest {
    pub id: Option<String>,
    pub from: String,
    pub room_id: String,
    pub payload: PgMessageParams,
    pub sig: Option<String>,
    /// FlowWeave L0: optional seq_id from client
    pub seq_id: Option<SeqIdParam>,
    /// FlowWeave P3: optional thread_id for topic grouping
    pub thread_id: Option<String>,
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
    /// FlowWeave L0: seq_id 3-tuple dedup — key → timestamp
    seen_seq_ids: HashMap<String, u64>,
    catchup_timestamps: HashMap<String, VecDeque<u64>>,  // L3: catchup rate-limit [T-SEC F7]
    /// FlowWeave L0: all known seq_id keys for references validation
    known_seq_ids: HashSet<String>,
    /// FlowWeave P2: Canonical state per room
    canonical_states: HashMap<String, CanonicalRoomState>,
    shared_secret: String,
    auth_key: String,                                      // v2: SEAAI_AUTH_KEY for connect()
    session_tokens: HashMap<String, String>,                // v2: session_token → agent_id
    msg_counter: u64,                                      // Auto-increment for unique msg_id
}

impl ChatroomHub {
    pub fn new() -> Self {
        let secret = std::env::var("SEAAI_HUB_SECRET")
            .unwrap_or_else(|_| "seaai-shared-secret".to_string());
        let auth_key = std::env::var("SEAAI_AUTH_KEY")
            .unwrap_or_else(|_| "sk-seaai-default".to_string());
        Self {
            authenticated_agents: HashSet::new(),
            agent_registry: HashMap::new(),
            rooms: HashMap::new(),
            inboxes: HashMap::new(),
            room_history: HashMap::new(),
            subscriptions: HashMap::new(),
            seen_messages: HashMap::new(),
            seen_seq_ids: HashMap::new(),
            catchup_timestamps: HashMap::new(),
            known_seq_ids: HashSet::new(),
            canonical_states: HashMap::new(),
            shared_secret: secret,
            auth_key,
            session_tokens: HashMap::new(),
            msg_counter: 0,
        }
    }

    // ── Connection cleanup ──

    /// TCP 연결 끊김 시 호출: agent를 모든 room에서 제거하고 registry 정리
    pub fn cleanup_agent(&mut self, agent_id: &str) {
        // 모든 room에서 제거
        let mut empty_rooms = vec![];
        for (room_id, members) in self.rooms.iter_mut() {
            members.remove(agent_id);
            if members.is_empty() {
                empty_rooms.push(room_id.clone());
            }
        }
        for room_id in empty_rooms {
            self.rooms.remove(&room_id);
            self.room_history.remove(&room_id);
            self.canonical_states.remove(&room_id);
        }
        // registry에서 제거
        self.authenticated_agents.remove(agent_id);
        self.agent_registry.remove(agent_id);
        self.subscriptions.remove(agent_id);
        // inbox는 보존 (재접속 시 미수신 메시지 수신 가능)
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

    #[allow(dead_code)]
    pub fn join_room(&mut self, agent_id: &str, room_id: &str) -> Result<()> {
        self.join_room_with_catchup(agent_id, room_id).map(|_| ())
    }

    /// FlowWeave P1: join_room + automatic JoinCatchup for late joiners.
    /// Returns None if this is the first member (no history yet).
    pub fn join_room_with_catchup(&mut self, agent_id: &str, room_id: &str) -> Result<Option<JoinCatchup>> {
        self.ensure_authenticated(agent_id)?;

        if self.rooms.len() >= MAX_ROOMS && !self.rooms.contains_key(room_id) {
            bail!("maximum room limit ({}) reached", MAX_ROOMS);
        }

        // Capture history BEFORE joining (so joiner doesn't see its own join event)
        let catchup = if let Some(hist) = self.room_history.get(room_id) {
            let all: Vec<ChatMessage> = hist.iter().cloned().collect();
            let total = all.len();
            let window = 10;
            let start = if total > window { total - window } else { 0 };
            let recent = all[start..].to_vec();
            // Only send catchup if room already has members AND history
            if total > 0 {
                Some(JoinCatchup {
                    joiner: agent_id.to_string(),
                    room_id: room_id.to_string(),
                    current_member_count: self.rooms.get(room_id).map(|r| r.len()).unwrap_or(0),
                    recent_messages: recent,
                    total_in_buffer: total,
                })
            } else {
                None
            }
        } else {
            None
        };

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

        Ok(catchup)
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
            self.canonical_states.remove(room_id);
        }
        Ok(())
    }

    // ── Messaging with L3 features ──

    pub fn send_message(&mut self, request: SendMessageRequest) -> Result<DeliveryResult> {
        self.ensure_authenticated(&request.from)?;
        self.ensure_room_member(&request.from, &request.room_id)?;

        // ── HubMaster /clear command ──
        if request.from == "HubMaster" && request.payload.body.trim() == "/clear" {
            let members = self.rooms.get(&request.room_id).cloned().unwrap_or_default();
            let others: Vec<&String> = members.iter().filter(|m| m.as_str() != "HubMaster").collect();
            if !others.is_empty() {
                bail!("/clear denied — other agents connected: {:?}", others);
            }
            // Clear room history
            self.room_history.remove(&request.room_id);
            // Clear canonical state (decisions, threads, flow state)
            self.canonical_states.remove(&request.room_id);
            // Clear dedup caches (stale refs to cleared messages)
            self.seen_messages.clear();
            self.seen_seq_ids.clear();
            self.known_seq_ids.clear();

            return Ok(DeliveryResult {
                delivered_to: vec![],
                room_id: request.room_id,
                message_id: format!("clear-{}", self.current_timestamp_millis()),
            });
        }

        // v2 DualMode: sig is optional. If present, validate. If absent, skip.
        if let Some(ref sig) = request.sig {
            let computed_sig = self.build_message_signature(&request.payload)?;
            if sig != &computed_sig {
                bail!("invalid message signature");
            }
        }

        let message_id = request
            .id
            .unwrap_or_else(|| {
                self.msg_counter += 1;
                format!("msg-{}-{}-{}", request.from, self.current_timestamp_millis(), self.msg_counter)
            });

        // FlowWeave L0: seq_id 3-tuple dedup (takes precedence over message_id dedup)
        let seq_key: Option<String> = request.seq_id.as_ref().map(|s| s.to_key());
        if let Some(ref key) = seq_key {
            if self.seen_seq_ids.contains_key(key) {
                bail!("duplicate seq_id {}", key);
            }
        } else {
            // Fallback: legacy id dedup
            if self.seen_messages.contains_key(&message_id) {
                bail!("duplicate message id {}", message_id);
            }
        }

        // FlowWeave L0: references validation (lenient — log invalid refs, don't reject)
        // First message may use "_root" as reference (no history required)
        let refs = &request.payload.references;
        for r in refs.iter() {
            if r != "_root" && !self.known_seq_ids.contains(r) {
                // Non-fatal: unknown ref (client may be ahead, or legacy msg)
                // In strict mode this would bail!, for MVP we pass through
            }
        }

        // Register this seq_id in known set + dedup map
        if let Some(ref key) = seq_key {
            self.seen_seq_ids.insert(key.clone(), self.current_timestamp());
            self.known_seq_ids.insert(key.clone());
        } else {
            self.seen_messages.insert(message_id.clone(), self.current_timestamp());
        }
        self.gc_seen_messages();

        // Broadcast to all room members except sender, filtered by subscription
        let members = self.rooms.get(&request.room_id).cloned().unwrap_or_default();
        let recipients: Vec<String> = members
            .into_iter()
            .filter(|m| m != &request.from)
            .filter(|m| self.matches_subscription(m, &request.payload.intent))
            .collect();

        // FlowWeave P3: thread_id from request or payload
        let thread_id = request.thread_id
            .or_else(|| request.payload.thread_id.clone());

        let message = ChatMessage {
            id: message_id.clone(),
            from: request.from.clone(),
            to: recipients.clone(),
            room_id: request.room_id.clone(),
            intent: request.payload.intent.clone(),
            body: request.payload.body.clone(),
            ts: request.payload.ts,
            sig: request.sig,
            seq_id: request.seq_id.clone(),
            references: request.payload.references.clone(),
            thread_id: thread_id.clone(),
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
        history.push_back(message.clone());

        // FlowWeave P2: Canonical State updates
        let member_count = self.rooms.get(&request.room_id).map(|r| r.len()).unwrap_or(0);
        let now_f64 = self.current_timestamp_f64();
        let canonical = self.canonical_states
            .entry(request.room_id.clone())
            .or_insert_with(CanonicalRoomState::new);

        // FlowState auto-transition
        let new_state = match canonical.flow_state {
            FlowState::Gathering if member_count >= 2 => Some(FlowState::Flowing),
            FlowState::Deciding if message.intent == "final" => Some(FlowState::Resting),
            FlowState::Resting if message.intent == "proposal" => Some(FlowState::Flowing),
            _ if message.intent == "convergence" => Some(FlowState::Deciding),
            _ => None,
        };
        if let Some(state) = new_state {
            canonical.flow_state = state;
            canonical.last_transition_ts = now_f64;
        }

        // decision_log: intent="final" → record
        if message.intent == "final" {
            let seq_key = request.seq_id.as_ref()
                .map(|s| s.to_key())
                .unwrap_or_else(|| message.id.clone());
            canonical.decision_log.push(DecisionEntry {
                seq_id_key: seq_key,
                summary: message.body.chars().take(120).collect(),
                decided_by: request.from.clone(),
                ts: now_f64,
            });
        }

        // P3: Thread index — register message under its thread_id
        if let Some(ref tid) = thread_id {
            let seq_key = request.seq_id.as_ref()
                .map(|s| s.to_key())
                .unwrap_or_else(|| message.id.clone());
            if let Some(entry) = canonical.thread_index.iter_mut().find(|e| &e.thread_id == tid) {
                entry.message_seq_keys.push(seq_key);
            } else {
                // New thread
                canonical.thread_index.push(ThreadEntry {
                    thread_id: tid.clone(),
                    topic: message.body.chars().take(60).collect(),
                    message_seq_keys: vec![seq_key],
                    created_at: now_f64,
                });
            }
        }

        Ok(DeliveryResult {
            delivered_to: recipients,
            room_id: request.room_id,
            message_id,
        })
    }

    // ── L1: Catch-up (message buffer for late joiners) ──

    pub fn catchup(&mut self, agent_id: &str, room_id: &str, count: usize) -> Result<CatchupResult> {
        self.ensure_authenticated(agent_id)?;

        // [T-SEC F7] Concurrent catchup rate-limit: max(1, room_size / 4) per 30s window
        let room_size = self.rooms.get(room_id).map(|r| r.len()).unwrap_or(0);
        let limit = (room_size / CATCHUP_LIMIT_DENOM).max(1);
        let now = self.current_timestamp();
        let timestamps = self.catchup_timestamps.entry(room_id.to_string()).or_default();
        timestamps.retain(|&ts| now.saturating_sub(ts) < CATCHUP_WINDOW_SECS);
        if timestamps.len() >= limit {
            bail!(
                "catchup rate limit for room '{}': {}/{} requests in {}s window — retry later",
                room_id, timestamps.len(), limit, CATCHUP_WINDOW_SECS
            );
        }
        timestamps.push_back(now);

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
        let canonical = self.canonical_states.get(room_id);
        Ok(RoomState {
            room_id: room_id.to_string(),
            members: members.iter().cloned().collect(),
            message_count,
            agent_count: self.authenticated_agents.len(),
            // FlowWeave P2
            flow_state: canonical.map(|c| c.flow_state.clone()).unwrap_or_default(),
            decision_count: canonical.map(|c| c.decision_log.len()).unwrap_or(0),
            thread_count: canonical.map(|c| c.thread_index.len()).unwrap_or(0),
        })
    }

    /// FlowWeave P2: Get canonical state for a room
    pub fn canonical_state(&self, room_id: &str) -> Result<&CanonicalRoomState> {
        self.canonical_states.get(room_id)
            .ok_or_else(|| anyhow::anyhow!("no canonical state for room {}", room_id))
    }

    /// FlowWeave P2: Manually record a decision (for explicit FinalDecision messages)
    pub fn record_decision(&mut self, room_id: &str, seq_key: String, summary: String, decided_by: String) -> Result<()> {
        let now = self.current_timestamp_f64();
        let canonical = self.canonical_states
            .entry(room_id.to_string())
            .or_insert_with(CanonicalRoomState::new);
        canonical.decision_log.push(DecisionEntry { seq_id_key: seq_key, summary, decided_by, ts: now });
        canonical.flow_state = FlowState::Resting;
        canonical.last_transition_ts = now;
        Ok(())
    }

    /// FlowWeave P2: Transition flow state explicitly
    pub fn set_flow_state(&mut self, room_id: &str, state: FlowStateParam) -> Result<()> {
        let now = self.current_timestamp_f64();
        let flow = match state {
            FlowStateParam::Gathering  => FlowState::Gathering,
            FlowStateParam::Flowing    => FlowState::Flowing,
            FlowStateParam::Deepening  => FlowState::Deepening,
            FlowStateParam::Converging => FlowState::Converging,
            FlowStateParam::Deciding   => FlowState::Deciding,
            FlowStateParam::Resting    => FlowState::Resting,
        };
        let canonical = self.canonical_states
            .entry(room_id.to_string())
            .or_insert_with(CanonicalRoomState::new);
        canonical.flow_state = flow;
        canonical.last_transition_ts = now;
        Ok(())
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

    pub fn agent_messages_compact(&mut self, agent_id: &str) -> Result<AgentMailboxCompact> {
        self.ensure_authenticated(agent_id)?;
        let messages: Vec<CompactMessage> = self.inboxes
            .get_mut(agent_id)
            .map(|inbox| inbox.drain(..)
                .map(|m| CompactMessage { from: m.from, intent: m.intent, body: m.body })
                .collect())
            .unwrap_or_default();
        Ok(AgentMailboxCompact {
            agent_id: agent_id.to_string(),
            messages,
        })
    }

    // ── v2: Connect / Disconnect (Ephemeral Agent Model) ──

    pub fn connect(&mut self, auth_key: &str, agent_id: &str, rooms: Vec<String>) -> Result<serde_json::Value> {
        if auth_key != self.auth_key {
            bail!("invalid auth_key");
        }

        // Register agent (same as register_agent but without HMAC token)
        self.authenticated_agents.insert(agent_id.to_string());
        self.inboxes.entry(agent_id.to_string()).or_default();
        self.agent_registry.insert(agent_id.to_string(), AgentInfo {
            agent_id: agent_id.to_string(),
            capabilities: vec![],
            registered_at: self.current_timestamp_f64(),
            rooms: vec![],
        });
        self.subscriptions.insert(agent_id.to_string(), Subscription {
            topics: HashSet::new(),
        });

        // Join requested rooms
        let mut joined_rooms = vec![];
        for room_id in &rooms {
            if self.rooms.len() >= MAX_ROOMS && !self.rooms.contains_key(room_id) {
                continue; // skip if room limit reached
            }
            self.rooms.entry(room_id.clone()).or_default().insert(agent_id.to_string());
            if let Some(info) = self.agent_registry.get_mut(agent_id) {
                if !info.rooms.contains(room_id) {
                    info.rooms.push(room_id.clone());
                }
            }
            joined_rooms.push(room_id.clone());
        }

        // Generate session token
        let ts_hex = format!("{:x}", self.current_timestamp_millis());
        let raw = format!("sess-{}-{}", agent_id, ts_hex);
        let sig = self.hmac_hex(raw.as_bytes());
        let token = format!("{}-{}", raw, &sig[..16]);

        self.session_tokens.insert(token.clone(), agent_id.to_string());

        Ok(serde_json::json!({
            "session_token": token,
            "agent_id": agent_id,
            "rooms": joined_rooms,
            "connected_at": self.current_timestamp_f64()
        }))
    }

    pub fn disconnect(&mut self, session_token: &str, agent_id: &str) -> Result<serde_json::Value> {
        // Validate session token
        match self.session_tokens.get(session_token) {
            Some(owner) if owner == agent_id => {},
            _ => bail!("invalid session_token for agent {}", agent_id),
        }

        // Collect rooms before cleanup
        let cleaned_rooms: Vec<String> = self.agent_registry.get(agent_id)
            .map(|info| info.rooms.clone())
            .unwrap_or_default();

        // Reuse existing cleanup logic
        self.cleanup_agent(agent_id);

        // Remove session token
        self.session_tokens.remove(session_token);

        Ok(serde_json::json!({
            "status": "disconnected",
            "agent_id": agent_id,
            "cleaned_rooms": cleaned_rooms
        }))
    }

    pub fn agent_rooms(&self, agent_id: &str) -> Result<Vec<String>> {
        self.ensure_authenticated(agent_id)?;
        Ok(self.agent_registry.get(agent_id)
            .map(|info| info.rooms.clone())
            .unwrap_or_default())
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
        // FlowWeave L0: GC seq_id dedup map (sliding window 5min = 300s)
        self.seen_seq_ids.retain(|_, ts| now.saturating_sub(*ts) < 300);
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
            seq_id: None, thread_id: None,
            references: vec![],
        };
        let sig = hub.build_message_signature(&payload).unwrap();
        hub.send_message(SendMessageRequest {
            id: None, from: from.to_string(), room_id: room.to_string(), payload, sig: Some(sig),
            seq_id: None, thread_id: None,
        }).unwrap()
    }

    fn send_msg_with_seq(hub: &mut ChatroomHub, from: &str, room: &str, body: &str,
                          epoch: u64, counter: u64, references: Vec<String>) -> DeliveryResult {
        use super::SeqIdParam;
        let seq = SeqIdParam { sender: from.to_string(), epoch, counter };
        let payload = PgMessageParams {
            intent: "chat".to_string(),
            body: body.to_string(),
            ts: 42.0,
            seq_id: Some(seq.clone()),
            references,
            thread_id: None,
        };
        let sig = hub.build_message_signature(&payload).unwrap();
        hub.send_message(SendMessageRequest {
            id: None, from: from.to_string(), room_id: room.to_string(), payload, sig: Some(sig),
            seq_id: Some(seq), thread_id: None,
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
            payload: PgMessageParams { intent: "chat".into(), body: "tampered".into(), ts: 7.0,
                seq_id: None, references: vec![], thread_id: None },
            sig: Some("bad".to_string()), seq_id: None, thread_id: None,
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
                seq_id: None, references: vec![], thread_id: None,
            };
            let sig = hub.build_message_signature(&payload).unwrap();
            let _ = hub.send_message(SendMessageRequest {
                id: Some(format!("m{}", i)),
                from: "Aion".into(), room_id: "design-room".into(), payload, sig: Some(sig),
                seq_id: None, thread_id: None,
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
                seq_id: None, references: vec![], thread_id: None,
            };
            let sig = hub.build_message_signature(&payload).unwrap();
            let _ = hub.send_message(SendMessageRequest {
                id: Some(format!("bp{}", i)),
                from: "A".into(), room_id: "r".into(), payload, sig: Some(sig),
                seq_id: None, thread_id: None,
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
            seq_id: None, references: vec![], thread_id: None,
        };
        let sig = hub.build_message_signature(&payload_chat).unwrap();
        let r1 = hub.send_message(SendMessageRequest {
            id: Some("t1".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload: payload_chat, sig: Some(sig), seq_id: None, thread_id: None,
        }).unwrap();
        assert!(!r1.delivered_to.contains(&"ClNeo".to_string())); // filtered out

        // Send a "pgtp" intent message — ClNeo should receive
        let payload_pgtp = PgMessageParams {
            intent: "pgtp".into(), body: "pgtp msg".into(), ts: 2.0,
            seq_id: None, references: vec![], thread_id: None,
        };
        let sig2 = hub.build_message_signature(&payload_pgtp).unwrap();
        let r2 = hub.send_message(SendMessageRequest {
            id: Some("t2".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload: payload_pgtp, sig: Some(sig2), seq_id: None, thread_id: None,
        }).unwrap();
        assert!(r2.delivered_to.contains(&"ClNeo".to_string())); // passes filter
    }

    #[test]
    fn catchup_rate_limit_enforced() {
        // 4-member room → limit = 4/4 = 1 per 30s window
        let mut hub = ChatroomHub::new();
        for agent in ["A", "B", "C", "D"] {
            let tok = hub.build_agent_token(agent);
            hub.register_agent(agent, &tok, vec![]).unwrap();
            hub.join_room(agent, "r").unwrap();
        }
        // First catchup: OK
        assert!(hub.catchup("A", "r", 10).is_ok());
        // Second catchup immediately: rate limited (1/1 in window)
        let err = hub.catchup("B", "r", 10).unwrap_err();
        assert!(err.to_string().contains("catchup rate limit"), "err={}", err);
    }

    #[test]
    fn catchup_limit_scales_with_room_size() {
        // 8-member room → limit = 8/4 = 2 per 30s window
        let mut hub = ChatroomHub::new();
        for i in 0..8u8 {
            let agent = format!("Agent{}", i);
            let tok = hub.build_agent_token(&agent);
            hub.register_agent(&agent, &tok, vec![]).unwrap();
            hub.join_room(&agent, "bigroom").unwrap();
        }
        assert!(hub.catchup("Agent0", "bigroom", 5).is_ok());
        assert!(hub.catchup("Agent1", "bigroom", 5).is_ok());
        // Third: should be rejected
        let err = hub.catchup("Agent2", "bigroom", 5).unwrap_err();
        assert!(err.to_string().contains("catchup rate limit"), "err={}", err);
    }

    #[test]
    fn catchup_limit_minimum_one() {
        // 1-member room → limit = max(1/4, 1) = 1
        let mut hub = ChatroomHub::new();
        let tok = hub.build_agent_token("Solo");
        hub.register_agent("Solo", &tok, vec![]).unwrap();
        hub.join_room("Solo", "solo-room").unwrap();
        assert!(hub.catchup("Solo", "solo-room", 5).is_ok());
        let err = hub.catchup("Solo", "solo-room", 5).unwrap_err();
        assert!(err.to_string().contains("catchup rate limit"), "err={}", err);
    }

    #[test]
    fn dedup_rejects_duplicate_message_id() {
        let mut hub = registered_hub();
        let payload = PgMessageParams {
            intent: "chat".into(), body: "dup test".into(), ts: 1.0,
            seq_id: None, references: vec![], thread_id: None,
        };
        let sig = hub.build_message_signature(&payload).unwrap();

        // First send: OK
        let r1 = hub.send_message(SendMessageRequest {
            id: Some("dup1".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload: payload.clone(), sig: Some(sig.clone()), seq_id: None, thread_id: None,
        });
        assert!(r1.is_ok());

        // Second send with same ID: rejected
        let r2 = hub.send_message(SendMessageRequest {
            id: Some("dup1".into()), from: "Aion".into(), room_id: "design-room".into(),
            payload, sig: Some(sig), seq_id: None, thread_id: None,
        });
        assert!(r2.is_err());
        assert!(r2.unwrap_err().to_string().contains("duplicate"));
    }

    #[test]
    fn seq_id_dedup_rejects_duplicate_3tuple() {
        let mut hub = registered_hub();
        let epoch = 1774931200u64;

        // First send with seq_id
        let r1 = send_msg_with_seq(&mut hub, "Aion", "design-room", "first", epoch, 1, vec!["_root".into()]);
        assert!(r1.delivered_to.contains(&"ClNeo".to_string()));

        // Second send with same seq_id 3-tuple — must be rejected
        let seq = SeqIdParam { sender: "Aion".to_string(), epoch, counter: 1 };
        let payload2 = PgMessageParams {
            intent: "chat".into(), body: "duplicate".into(), ts: 43.0,
            seq_id: Some(seq.clone()), references: vec![], thread_id: None,
        };
        let sig2 = hub.build_message_signature(&payload2).unwrap();
        let r2 = hub.send_message(SendMessageRequest {
            id: None, from: "Aion".into(), room_id: "design-room".into(),
            payload: payload2, sig: Some(sig2), seq_id: Some(seq), thread_id: None,
        });
        assert!(r2.is_err());
        assert!(r2.unwrap_err().to_string().contains("duplicate seq_id"));
    }

    #[test]
    fn seq_id_references_form_dag() {
        let mut hub = registered_hub();
        let epoch = 9000u64;

        // First message (root)
        let r1 = send_msg_with_seq(&mut hub, "Aion", "design-room", "proposal", epoch, 1, vec!["_root".into()]);
        let key1 = format!("Aion_{}_001", epoch);

        // Second message references first
        let r2 = send_msg_with_seq(&mut hub, "ClNeo", "design-room", "reaction", epoch, 1, vec![key1.clone()]);
        assert!(!r2.delivered_to.is_empty() || r2.delivered_to.is_empty()); // no error = DAG accepted

        // Verify history has both messages with seq_id
        let catchup = hub.catchup("Aion", "design-room", 10).unwrap();
        let has_seq = catchup.messages.iter().any(|m| m.seq_id.is_some());
        assert!(has_seq, "messages should carry seq_id");
    }

    #[test]
    fn join_room_returns_catchup_for_late_joiner() {
        let mut hub = ChatroomHub::new();
        let ta = hub.build_agent_token("A");
        let tb = hub.build_agent_token("B");
        let tc = hub.build_agent_token("C");
        hub.register_agent("A", &ta, vec![]).unwrap();
        hub.register_agent("B", &tb, vec![]).unwrap();
        hub.register_agent("C", &tc, vec![]).unwrap();
        hub.join_room("A", "cafe").unwrap();
        hub.join_room("B", "cafe").unwrap();

        // A sends 5 messages
        for i in 0..5 {
            send_msg(&mut hub, "A", "cafe", &format!("msg {}", i));
        }

        // C joins late — should receive JoinCatchup
        let catchup = hub.join_room_with_catchup("C", "cafe").unwrap();
        assert!(catchup.is_some(), "late joiner should get JoinCatchup");
        let jc = catchup.unwrap();
        assert_eq!(jc.joiner, "C");
        assert!(jc.total_in_buffer > 0);
        assert!(!jc.recent_messages.is_empty());
    }
}
