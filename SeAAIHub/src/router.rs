use anyhow::{Context, Result};
use serde::de::DeserializeOwned;
use serde_json::{json, Value};

use crate::chatroom::{ChatroomHub, SendMessageRequest};
use crate::protocol::{
    AgentQueryArgs, CatchupArgs, DiscoverArgs, JsonRpcRequest, JsonRpcResponse, PgPayload,
    RegisterAgentArgs, RoomMutationArgs, RoomStateArgs, SendMessageArgs, SubscribeArgs,
    ToolCallParams, ToolSpec,
};

pub struct Router {
    hub: ChatroomHub,
}

impl Router {
    pub fn new() -> Self {
        Self {
            hub: ChatroomHub::new(),
        }
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
            "seaai_join_room" => {
                let args: RoomMutationArgs = self.parse_args(call.arguments)?;
                self.hub.join_room(&args.agent_id, &args.room_id)?;
                Ok(self.tool_success(json!({
                    "agent_id": args.agent_id,
                    "room_id": args.room_id,
                    "joined": true
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
                let result = self.hub.send_message(SendMessageRequest {
                    id: args.id,
                    from: args.from,
                    room_id: args.room_id,
                    payload: args.pg_payload,
                    sig: args.sig,
                })?;
                Ok(self.tool_success(self.to_tool_result(result)?))
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
                let mailbox = self.hub.agent_messages(&args.agent_id)?;
                Ok(self.tool_success(serde_json::to_value(mailbox)?))
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
        let result = self.hub.send_message(SendMessageRequest {
            id: payload.id,
            from: payload.from,
            room_id: payload.room_id,
            payload: payload.pg_payload,
            sig: payload.sig,
        })?;

        Ok(json!({
            "delivered_to": result.delivered_to,
            "room_id": result.room_id,
            "message_id": result.message_id
        }))
    }

    fn tool_specs(&self) -> Vec<ToolSpec> {
        vec![
            ToolSpec {
                name: "seaai_register_agent".to_string(),
                description: "Authenticate an agent with an HMAC token. Any agent_id accepted.".to_string(),
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
            "structuredContent": value,
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
        let messages = &inbox_response.result.unwrap()["structuredContent"]["messages"];
        assert_eq!(messages.as_array().unwrap().len(), 1);
    }
}
