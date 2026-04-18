use crate::{config::*, error::*, hub_client::HubClient, pool::AgentPool, sig, wire::OutMessage};
use serde_json::{json, Value};
use std::time::{SystemTime, UNIX_EPOCH};

pub struct Router {
    pub pool: AgentPool,
    pub hub: HubClient,
    pub shared_secret: Vec<u8>,
}

impl Router {
    pub async fn register(&self, agent: &str, room: Option<&str>) -> Result<Value> {
        let room = room.unwrap_or("seaai-general");
        let token = sig::build_token(&self.shared_secret, agent);
        self.hub
            .rpc(
                "seaai_register_agent",
                json!({"agent_id": agent, "token": token}),
            )
            .await?;
        self.hub
            .rpc(
                "seaai_join_room",
                json!({"agent_id": agent, "room_id": room}),
            )
            .await?;
        self.pool.insert(agent, room);
        Ok(json!({"ok": true, "agent": agent}))
    }

    pub async fn unregister(&self, agent: &str) -> Result<Value> {
        if let Some(state) = self.pool.remove(agent) {
            for r in &state.rooms {
                let _ = self
                    .hub
                    .rpc(
                        "seaai_leave_room",
                        json!({"agent_id": agent, "room_id": r}),
                    )
                    .await;
            }
        }
        Ok(json!({"ok": true}))
    }

    pub async fn join(&self, agent: &str, room: &str) -> Result<Value> {
        self.hub
            .rpc(
                "seaai_join_room",
                json!({"agent_id": agent, "room_id": room}),
            )
            .await?;
        self.pool.join(agent, room)?;
        Ok(json!({"ok": true}))
    }

    pub async fn leave(&self, agent: &str, room: &str) -> Result<Value> {
        self.hub
            .rpc(
                "seaai_leave_room",
                json!({"agent_id": agent, "room_id": room}),
            )
            .await?;
        self.pool.leave(agent, room)?;
        Ok(json!({"ok": true}))
    }

    pub fn rooms(&self, agent: Option<&str>) -> Value {
        match agent {
            Some(id) => json!({"rooms": self.pool.rooms_of(id)}),
            None => json!({"rooms": self.pool.all_rooms()}),
        }
    }

    pub async fn poll(&self, agent: &str, room: Option<&str>) -> Result<Value> {
        // 1) offline buffer drain
        let mut out: Vec<OutMessage> = self.pool.with_state(agent, |st| {
            st.offline_buffer.drain(..).collect()
        })?;

        // 2) Hub RPC
        let raw = match self
            .hub
            .rpc("seaai_get_agent_messages", json!({"agent_id": agent}))
            .await
        {
            Ok(v) => v,
            Err(_) => return Ok(serde_json::to_value(out).unwrap()),
        };
        let msgs: Vec<Value> = raw
            .get("messages")
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default();

        // 3) dedup + room filter + projection
        self.pool.with_state(agent, |st| {
            for m in msgs {
                let id = m
                    .get("id")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string();
                if !id.is_empty() {
                    if st.seen_ids.contains(&id) {
                        continue;
                    }
                    st.seen_ids.insert(id);
                }
                if let Some(r) = room {
                    if m.get("room_id").and_then(|v| v.as_str()) != Some(r) {
                        continue;
                    }
                }
                out.push(OutMessage {
                    from: m
                        .get("from")
                        .and_then(|v| v.as_str())
                        .unwrap_or("")
                        .to_string(),
                    body: m
                        .get("body")
                        .and_then(|v| v.as_str())
                        .unwrap_or("")
                        .to_string(),
                    ts: m.get("ts").and_then(|v| v.as_f64()).unwrap_or(0.0),
                });
            }
            // 4) dedup cap (whole clear — matches Python)
            if st.seen_ids.len() > DEDUP_CAP {
                st.seen_ids.clear();
            }
        })?;

        Ok(serde_json::to_value(out).unwrap())
    }

    pub async fn send(
        &self,
        agent: &str,
        body: &str,
        to: &str,
        room: Option<&str>,
        intent: Option<&str>,
    ) -> Result<Value> {
        let room = match room {
            Some(r) => r.to_string(),
            None => self
                .pool
                .first_room(agent)
                .unwrap_or_else(|| "seaai-general".to_string()),
        };

        let ts_raw = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs_f64())
            .unwrap_or(0.0);
        // round to 6 decimals (match Python round(time.time(), 6))
        let ts = (ts_raw * 1_000_000.0).round() / 1_000_000.0;

        let sig_hex = sig::build_sig(&self.shared_secret, body, ts);
        let to_val = if to == "*" { json!("*") } else { json!([to]) };
        let intent = intent.unwrap_or("chat");

        self.hub
            .rpc(
                "seaai_send_message",
                json!({
                    "from": agent,
                    "to": to_val,
                    "room_id": room,
                    "pg_payload": {"intent": intent, "body": body, "ts": ts},
                    "sig": sig_hex,
                }),
            )
            .await?;

        Ok(json!({"ok": true}))
    }

    pub fn status(&self, hub_connected: bool, uptime: u64) -> Value {
        json!({
            "hub": hub_connected,
            "uptime": uptime,
            "agents": self.pool.agent_ids(),
            "rooms": self.pool.rooms_map(),
            "buffered": self.pool.buffered_count(),
        })
    }
}
