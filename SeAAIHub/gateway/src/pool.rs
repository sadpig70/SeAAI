use crate::{config::*, error::*, wire::OutMessage};
use dashmap::DashMap;
use std::collections::{HashSet, VecDeque};
use std::sync::Arc;

pub struct AgentState {
    #[allow(dead_code)]
    pub agent_id: String,
    pub rooms: Vec<String>,
    pub seen_ids: HashSet<String>,
    pub offline_buffer: VecDeque<OutMessage>,
}

impl AgentState {
    pub fn new(agent_id: String, room: String) -> Self {
        Self {
            agent_id,
            rooms: vec![room],
            seen_ids: HashSet::new(),
            offline_buffer: VecDeque::new(),
        }
    }
}

#[derive(Clone, Default)]
pub struct AgentPool {
    agents: Arc<DashMap<String, AgentState>>,
}

impl AgentPool {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn insert(&self, agent_id: &str, room: &str) {
        self.agents.insert(
            agent_id.to_string(),
            AgentState::new(agent_id.to_string(), room.to_string()),
        );
    }

    pub fn remove(&self, agent_id: &str) -> Option<AgentState> {
        self.agents.remove(agent_id).map(|(_, v)| v)
    }

    #[allow(dead_code)]
    pub fn contains(&self, agent_id: &str) -> bool {
        self.agents.contains_key(agent_id)
    }

    pub fn join(&self, agent_id: &str, room: &str) -> Result<()> {
        let mut e = self
            .agents
            .get_mut(agent_id)
            .ok_or_else(|| Error::NotRegistered(agent_id.into()))?;
        if !e.rooms.iter().any(|r| r == room) {
            e.rooms.push(room.into());
        }
        Ok(())
    }

    pub fn leave(&self, agent_id: &str, room: &str) -> Result<()> {
        let mut e = self
            .agents
            .get_mut(agent_id)
            .ok_or_else(|| Error::NotRegistered(agent_id.into()))?;
        e.rooms.retain(|r| r != room);
        Ok(())
    }

    pub fn rooms_of(&self, agent_id: &str) -> Vec<String> {
        self.agents
            .get(agent_id)
            .map(|s| s.rooms.clone())
            .unwrap_or_default()
    }

    pub fn first_room(&self, agent_id: &str) -> Option<String> {
        self.agents
            .get(agent_id)
            .and_then(|s| s.rooms.first().cloned())
    }

    pub fn all_rooms(&self) -> serde_json::Value {
        let mut map = serde_json::Map::new();
        for e in self.agents.iter() {
            map.insert(e.key().clone(), serde_json::json!(e.rooms));
        }
        serde_json::Value::Object(map)
    }

    pub fn agent_ids(&self) -> Vec<String> {
        self.agents.iter().map(|e| e.key().clone()).collect()
    }

    pub fn buffered_count(&self) -> usize {
        self.agents.iter().map(|e| e.offline_buffer.len()).sum()
    }

    /// room -> [agent_ids]
    pub fn rooms_map(&self) -> serde_json::Value {
        let mut out: std::collections::BTreeMap<String, Vec<String>> = Default::default();
        for e in self.agents.iter() {
            for r in &e.rooms {
                out.entry(r.clone()).or_default().push(e.key().clone());
            }
        }
        serde_json::to_value(out).unwrap_or(serde_json::json!({}))
    }

    /// Per-agent locked mutation. Caller closure receives `&mut AgentState`.
    pub fn with_state<F, R>(&self, agent_id: &str, f: F) -> Result<R>
    where
        F: FnOnce(&mut AgentState) -> R,
    {
        let mut e = self
            .agents
            .get_mut(agent_id)
            .ok_or_else(|| Error::NotRegistered(agent_id.into()))?;
        Ok(f(&mut *e))
    }

    /// Append a message to the agent's offline buffer (FIFO, cap = MAX_OFFLINE_BUFFER).
    #[allow(dead_code)]
    pub fn push_offline(&self, agent_id: &str, msg: OutMessage) {
        if let Some(mut e) = self.agents.get_mut(agent_id) {
            if e.offline_buffer.len() >= MAX_OFFLINE_BUFFER {
                e.offline_buffer.pop_front();
            }
            e.offline_buffer.push_back(msg);
        }
    }
}
