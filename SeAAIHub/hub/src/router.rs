use anyhow::{Context, Result};
use serde::de::DeserializeOwned;
use serde_json::{json, Value};

use crate::chatroom::{ChatroomHub, SendMessageRequest};
use crate::protocol::{
    AgentQueryArgs, CatchupArgs, ConnectArgs, DisconnectArgs, DiscoverArgs,
    JsonRpcRequest, JsonRpcResponse, PgPayload,
    RegisterAgentArgs, RoomMutationArgs, RoomStateArgs, SendMessageArgs, SubscribeArgs,
    ToolCallParams, ToolSpec, FlowStateParam,
};
use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct RecordDecisionArgs {
    room_id: String,
    seq_key: String,
    summary: String,
    decided_by: String,
}

#[derive(Debug, Deserialize)]
struct SetFlowStateArgs {
    room_id: String,
    state: FlowStateParam,
}

pub struct Router {
    hub: ChatroomHub,
}

impl Router {
    pub fn new() -> Self {
        Self {
            hub: ChatroomHub::new(),
        }
    }

    /// TCP 연결 끊김 시 agent cleanup (legacy)
    pub fn cleanup_agent(&mut self, agent_id: &str) {
        self.hub.cleanup_agent(agent_id);
    }

    /// v2: TCP 끊김 시 disconnect (session_token 무효화 포함)
    pub fn disconnect_agent(&mut self, agent_id: &str, session_token: &str) -> Result<()> {
        let _ = self.hub.disconnect(session_token, agent_id);
        Ok(())
    }

    pub fn handle_request(&mut self, req: JsonRpcRequest) -> JsonRpcResponse {
        let id = req.id.clone().unwrap_or(Value::Null);

        let response = match req.method.as_str() {
            "initialize" => Ok(json!({
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "SeAAIHub",
                    "version": "2.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            })),
            "notifications/initialized" => Ok(json!({})),
            "tools/list" => Ok(json!({ "tools": self.tool_specs() })),
            "tools/call" => self.handle_tool_call(req.params.unwrap_or(json!({}))),
            // v2: direct JSON-RPC methods (MCP server calls these directly, not via tools/call)
            "seaai_connect" => {
                let params = req.params.unwrap_or(json!({}));
                self.parse_args::<ConnectArgs>(params)
                    .and_then(|args| self.hub.connect(&args.auth_key, &args.agent_id, args.rooms))
            }
            "seaai_disconnect" => {
                let params = req.params.unwrap_or(json!({}));
                self.parse_args::<DisconnectArgs>(params)
                    .and_then(|args| self.hub.disconnect(&args.session_token, &args.agent_id))
            }
            "seaai/message" => self.handle_pg_message(req.params.unwrap_or(json!({}))),
            _ => Err(anyhow::anyhow!(
                "Method {} not found in SeAAIHub router",
                req.method
            )),
        };

        match response {
            Ok(result) => JsonRpcResponse::success(id, result),
            Err(error) => JsonRpcResponse::error(id, -32601, error.to_string()),
        }
    }

    fn handle_tool_call(&mut self, params: Value) -> Result<Value> {
        let call: ToolCallParams = self.parse_args(params)?;

        match call.name.as_str() {
            "seaai_register_agent" => {
                let args: RegisterAgentArgs = self.parse_args(call.arguments)?;
                self.hub.register_agent(&args.agent_id, &args.token, args.capabilities)?;
                Ok(self.tool_success(json!({
                    "agent_id": args.agent_id,
                    "registered": true
                })))
            }
            // v2: Ephemeral Agent Model
            "seaai_connect" => {
                let args: ConnectArgs = self.parse_args(call.arguments)?;
                let result = self.hub.connect(&args.auth_key, &args.agent_id, args.rooms)?;
                Ok(self.tool_success(result))
            }
            "seaai_disconnect" => {
                let args: DisconnectArgs = self.parse_args(call.arguments)?;
                let result = self.hub.disconnect(&args.session_token, &args.agent_id)?;
                Ok(self.tool_success(result))
            }
            "seaai_list_agent_rooms" => {
                let args: AgentQueryArgs = self.parse_args(call.arguments)?;
                let rooms = self.hub.agent_rooms(&args.agent_id)?;
                Ok(self.tool_success(json!({
                    "agent_id": args.agent_id,
                    "rooms": rooms
                })))
            }
            "seaai_join_room" => {
                let args: RoomMutationArgs = self.parse_args(call.arguments)?;
                let catchup = self.hub.join_room_with_catchup(&args.agent_id, &args.room_id)?;
                let catchup_val = match catchup {
                    Some(jc) => serde_json::to_value(jc)?,
                    None => json!(null),
                };
                Ok(self.tool_success(json!({
                    "agent_id": args.agent_id,
                    "room_id": args.room_id,
                    "joined": true,
                    "join_catchup": catchup_val
                })))
            }
            "seaai_leave_room" => {
                let args: RoomMutationArgs = self.parse_args(call.arguments)?;
                self.hub.leave_room(&args.agent_id, &args.room_id)?;
                Ok(self.tool_success(json!({
                    "agent_id": args.agent_id,
                    "room_id": args.room_id,
                    "left": true
                })))
            }
            "seaai_send_message" => {
                let args: SendMessageArgs = self.parse_args(call.arguments)?;
                // FlowWeave L0: seq_id may be in pg_payload or top-level args
                let seq_id = args.seq_id.or_else(|| args.pg_payload.seq_id.clone());
                // FlowWeave P3: thread_id from pg_payload
                let thread_id = args.pg_payload.thread_id.clone();
                let result = self.hub.send_message(SendMessageRequest {
                    id: args.id,
                    from: args.from,
                    room_id: args.room_id,
                    payload: args.pg_payload,
                    sig: args.sig,
                    seq_id,
                    thread_id,
                })?;
                Ok(self.tool_success(self.to_tool_result(result)?))
            }
            "seaai_get_canonical_state" => {
                let args: RoomStateArgs = self.parse_args(call.arguments)?;
                let state = self.hub.canonical_state(&args.room_id)?;
                Ok(self.tool_success(serde_json::to_value(state)?))
            }
            "seaai_record_decision" => {
                let args: RecordDecisionArgs = self.parse_args(call.arguments)?;
                self.hub.record_decision(&args.room_id, args.seq_key, args.summary, args.decided_by)?;
                Ok(self.tool_success(json!({"recorded": true})))
            }
            "seaai_set_flow_state" => {
                let args: SetFlowStateArgs = self.parse_args(call.arguments)?;
                self.hub.set_flow_state(&args.room_id, args.state)?;
                Ok(self.tool_success(json!({"updated": true})))
            }
            "seaai_get_room_state" => {
                let args: RoomStateArgs = self.parse_args(call.arguments)?;
                let state = self.hub.room_state(&args.room_id)?;
                Ok(self.tool_success(serde_json::to_value(state)?))
            }
            "seaai_list_rooms" => Ok(self.tool_success(json!({
                "rooms": self.hub.list_rooms()
            }))),
            "seaai_get_agent_messages" => {
                let args: AgentQueryArgs = self.parse_args(call.arguments)?;
                if args.compact {
                    let mailbox = self.hub.agent_messages_compact(&args.agent_id)?;
                    Ok(self.tool_success(serde_json::to_value(mailbox)?))
                } else {
                    let mailbox = self.hub.agent_messages(&args.agent_id)?;
                    Ok(self.tool_success(serde_json::to_value(mailbox)?))
                }
            }
            "seaai_preview_auth" => {
                let args: AgentQueryArgs = self.parse_args(call.arguments)?;
                let token = self.hub.build_agent_token(&args.agent_id);
                Ok(self.tool_success(json!({
                    "agent_id": args.agent_id,
                    "token": token
                })))
            }
            "seaai_discover_agents" => {
                let args: DiscoverArgs = self.parse_args(call.arguments)?;
                let result = self.hub.discover_agents(args.capability.as_deref());
                Ok(self.tool_success(serde_json::to_value(result)?))
            }
            "seaai_catchup" => {
                let args: CatchupArgs = self.parse_args(call.arguments)?;
                let result = self.hub.catchup(&args.agent_id, &args.room_id, args.count)?;
                Ok(self.tool_success(serde_json::to_value(result)?))
            }
            "seaai_subscribe_topic" => {
                let args: SubscribeArgs = self.parse_args(call.arguments)?;
                self.hub.subscribe_topic(&args.agent_id, &args.topic)?;
                Ok(self.tool_success(json!({"subscribed": args.topic})))
            }
            "seaai_unsubscribe_topic" => {
                let args: SubscribeArgs = self.parse_args(call.arguments)?;
                self.hub.unsubscribe_topic(&args.agent_id, &args.topic)?;
                Ok(self.tool_success(json!({"unsubscribed": args.topic})))
            }
            _ => Err(anyhow::anyhow!("tool {} is not registered", call.name)),
        }
    }

    fn handle_pg_message(&mut self, params: Value) -> Result<Value> {
        let payload: PgPayload = self.parse_args(params)?;
        // FlowWeave L0/P3: extract seq_id + thread_id from pg_payload
        let seq_id = payload.pg_payload.seq_id.clone();
        let thread_id = payload.pg_payload.thread_id.clone();
        let result = self.hub.send_message(SendMessageRequest {
            id: payload.id,
            from: payload.from,
            room_id: payload.room_id,
            payload: payload.pg_payload,
            sig: payload.sig,
            seq_id,
            thread_id,
        })?;

        Ok(json!({
            "delivered_to": result.delivered_to,
            "room_id": result.room_id,
            "message_id": result.message_id
        }))
    }

    fn tool_specs(&self) -> Vec<ToolSpec> {
        vec![
            // v2: Ephemeral Agent Model
            ToolSpec {
                name: "seaai_connect".to_string(),
                description: "Connect an agent to Hub with auth_key. Returns session_token.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["auth_key", "agent_id"],
                    "properties": {
                        "auth_key": {"type": "string"},
                        "agent_id": {"type": "string"},
                        "rooms": {"type": "array", "items": {"type": "string"}}
                    }
                }),
            },
            ToolSpec {
                name: "seaai_disconnect".to_string(),
                description: "Disconnect an agent from Hub. Leaves all rooms, removes state.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["session_token", "agent_id"],
                    "properties": {
                        "session_token": {"type": "string"},
                        "agent_id": {"type": "string"}
                    }
                }),
            },
            ToolSpec {
                name: "seaai_list_agent_rooms".to_string(),
                description: "List rooms an agent is currently participating in.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["agent_id"],
                    "properties": {
                        "agent_id": {"type": "string"}
                    }
                }),
            },
            // v1: Legacy (DualMode — retained for backward compatibility)
            ToolSpec {
                name: "seaai_register_agent".to_string(),
                description: "[Legacy] Authenticate an agent with an HMAC token. Use seaai_connect for v2.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["agent_id", "token"]
                }),
            },
            ToolSpec {
                name: "seaai_join_room".to_string(),
                description: "Join an authenticated agent to a room.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["agent_id", "room_id"]
                }),
            },
            ToolSpec {
                name: "seaai_leave_room".to_string(),
                description: "Remove an authenticated agent from a room.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["agent_id", "room_id"]
                }),
            },
            ToolSpec {
                name: "seaai_send_message".to_string(),
                description: "Broadcast a message to all room members (sender excluded).".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["from", "room_id", "pg_payload", "sig"]
                }),
            },
            ToolSpec {
                name: "seaai_get_room_state".to_string(),
                description: "Inspect room membership and delivered message count.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["room_id"]
                }),
            },
            ToolSpec {
                name: "seaai_list_rooms".to_string(),
                description: "List active room identifiers.".to_string(),
                input_schema: json!({
                    "type": "object"
                }),
            },
            ToolSpec {
                name: "seaai_get_agent_messages".to_string(),
                description: "Read and drain delivered messages for an authenticated agent.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["agent_id"]
                }),
            },
            ToolSpec {
                name: "seaai_preview_auth".to_string(),
                description: "Return the expected HMAC token for any agent_id.".to_string(),
                input_schema: json!({
                    "type": "object",
                    "required": ["agent_id"]
                }),
            },
        ]
    }

    fn parse_args<T: DeserializeOwned>(&self, value: Value) -> Result<T> {
        serde_json::from_value(value).context("invalid request arguments")
    }

    fn tool_success(&self, value: Value) -> Value {
        json!({
            "content": [{
                "type": "text",
                "text": value.to_string()
            }],
            "isError": false
        })
    }

    fn to_tool_result<T: serde::Serialize>(&self, value: T) -> Result<Value> {
        Ok(serde_json::to_value(value)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::protocol::PgMessageParams;

    fn request(id: i32, method: &str, params: Value) -> JsonRpcRequest {
        JsonRpcRequest {
            jsonrpc: "2.0".to_string(),
            id: Some(json!(id)),
            method: method.to_string(),
            params: Some(params),
        }
    }

    #[test]
    fn lists_chatroom_tools() {
        let mut router = Router::new();
        let response = router.handle_request(request(1, "tools/list", json!({})));
        let tools = response.result.unwrap()["tools"].as_array().unwrap().clone();
        assert!(tools.iter().any(|tool| tool["name"] == "seaai_send_message"));
        assert!(tools.iter().any(|tool| tool["name"] == "seaai_get_agent_messages"));
    }

    #[test]
    fn routes_broadcast_message() {
        let mut router = Router::new();

        for agent in ["Aion", "ClNeo"] {
            let token = router.hub.build_agent_token(agent);
            let register_response = router.handle_request(request(
                1,
                "tools/call",
                json!({
                    "name": "seaai_register_agent",
                    "arguments": {
                        "agent_id": agent,
                        "token": token
                    }
                }),
            ));
            assert!(register_response.error.is_none());
        }

        for agent in ["Aion", "ClNeo"] {
            let join_response = router.handle_request(request(
                2,
                "tools/call",
                json!({
                    "name": "seaai_join_room",
                    "arguments": {
                        "agent_id": agent,
                        "room_id": "general"
                    }
                }),
            ));
            assert!(join_response.error.is_none());
        }

        let pg_payload = PgMessageParams {
            intent: "chat".to_string(),
            body: "hello from Aion".to_string(),
            ts: 100.0,
            seq_id: None,
            references: vec![],
            thread_id: None,
        };
        let sig = router.hub.build_message_signature(&pg_payload).unwrap();
        let send_response = router.handle_request(request(
            3,
            "seaai/message",
            json!({
                "from": "Aion",
                "room_id": "general",
                "pg_payload": pg_payload,
                "sig": sig
            }),
        ));
        assert!(send_response.error.is_none());
        assert_eq!(send_response.result.unwrap()["delivered_to"][0], "ClNeo");

        let inbox_response = router.handle_request(request(
            4,
            "tools/call",
            json!({
                "name": "seaai_get_agent_messages",
                "arguments": { "agent_id": "ClNeo" }
            }),
        ));
        assert!(inbox_response.error.is_none());
        let result = inbox_response.result.unwrap();
        let text = result["content"][0]["text"].as_str().unwrap();
        let parsed: serde_json::Value = serde_json::from_str(text).unwrap();
        let messages = parsed["messages"].as_array().unwrap();
        assert_eq!(messages.len(), 1);
    }

    fn parse_tool_result(response: &JsonRpcResponse) -> serde_json::Value {
        let result = response.result.as_ref().unwrap();
        let text = result["content"][0]["text"].as_str().unwrap();
        serde_json::from_str(text).unwrap()
    }

    #[test]
    fn connect_succeeds_with_valid_auth_key() {
        let mut router = Router::new();
        let response = router.handle_request(request(
            1, "tools/call",
            json!({
                "name": "seaai_connect",
                "arguments": {
                    "auth_key": "sk-seaai-default",
                    "agent_id": "TestAgent",
                    "rooms": ["seaai-general"]
                }
            }),
        ));
        assert!(response.error.is_none());
        let parsed = parse_tool_result(&response);
        assert_eq!(parsed["agent_id"], "TestAgent");
        assert!(parsed["session_token"].as_str().unwrap().starts_with("sess-TestAgent-"));
        assert_eq!(parsed["rooms"][0], "seaai-general");
    }

    #[test]
    fn connect_rejects_invalid_auth_key() {
        let mut router = Router::new();
        let response = router.handle_request(request(
            1, "tools/call",
            json!({
                "name": "seaai_connect",
                "arguments": {
                    "auth_key": "wrong-key",
                    "agent_id": "BadAgent"
                }
            }),
        ));
        assert!(response.error.is_some() || {
            let result = response.result.as_ref().unwrap();
            result["isError"].as_bool().unwrap_or(false)
        });
    }

    #[test]
    fn disconnect_cleans_up_agent() {
        let mut router = Router::new();
        // Connect
        let conn_resp = router.handle_request(request(
            1, "tools/call",
            json!({
                "name": "seaai_connect",
                "arguments": {
                    "auth_key": "sk-seaai-default",
                    "agent_id": "EphAgent",
                    "rooms": ["room-a", "room-b"]
                }
            }),
        ));
        let conn = parse_tool_result(&conn_resp);
        let token = conn["session_token"].as_str().unwrap();

        // Disconnect
        let disc_resp = router.handle_request(request(
            2, "tools/call",
            json!({
                "name": "seaai_disconnect",
                "arguments": {
                    "session_token": token,
                    "agent_id": "EphAgent"
                }
            }),
        ));
        assert!(disc_resp.error.is_none());
        let disc = parse_tool_result(&disc_resp);
        assert_eq!(disc["status"], "disconnected");
        assert!(disc["cleaned_rooms"].as_array().unwrap().len() >= 2);
    }

    #[test]
    fn list_agent_rooms_returns_joined_rooms() {
        let mut router = Router::new();
        // Connect to 2 rooms
        router.handle_request(request(
            1, "tools/call",
            json!({
                "name": "seaai_connect",
                "arguments": {
                    "auth_key": "sk-seaai-default",
                    "agent_id": "MultiAgent",
                    "rooms": ["alpha", "beta"]
                }
            }),
        ));
        // Join a third
        router.handle_request(request(
            2, "tools/call",
            json!({
                "name": "seaai_join_room",
                "arguments": { "agent_id": "MultiAgent", "room_id": "gamma" }
            }),
        ));
        // List rooms
        let resp = router.handle_request(request(
            3, "tools/call",
            json!({
                "name": "seaai_list_agent_rooms",
                "arguments": { "agent_id": "MultiAgent" }
            }),
        ));
        let parsed = parse_tool_result(&resp);
        let rooms = parsed["rooms"].as_array().unwrap();
        assert_eq!(rooms.len(), 3);
    }

    #[test]
    fn dual_mode_register_and_connect_coexist() {
        let mut router = Router::new();
        // v1: register
        let token = router.hub.build_agent_token("LegacyAgent");
        router.handle_request(request(
            1, "tools/call",
            json!({
                "name": "seaai_register_agent",
                "arguments": { "agent_id": "LegacyAgent", "token": token }
            }),
        ));
        // v2: connect
        router.handle_request(request(
            2, "tools/call",
            json!({
                "name": "seaai_connect",
                "arguments": {
                    "auth_key": "sk-seaai-default",
                    "agent_id": "ModernAgent",
                    "rooms": ["shared"]
                }
            }),
        ));
        // Both join same room
        router.handle_request(request(
            3, "tools/call",
            json!({
                "name": "seaai_join_room",
                "arguments": { "agent_id": "LegacyAgent", "room_id": "shared" }
            }),
        ));
        // Legacy sends, Modern receives
        let pg_payload = PgMessageParams {
            intent: "chat".to_string(),
            body: "dual mode test".to_string(),
            ts: 99.0,
            seq_id: None, references: vec![], thread_id: None,
        };
        let sig = router.hub.build_message_signature(&pg_payload).unwrap();
        let send_resp = router.handle_request(request(
            4, "seaai/message",
            json!({
                "from": "LegacyAgent",
                "room_id": "shared",
                "pg_payload": pg_payload,
                "sig": sig
            }),
        ));
        assert!(send_resp.error.is_none());
        assert_eq!(send_resp.result.unwrap()["delivered_to"][0], "ModernAgent");
    }
}
