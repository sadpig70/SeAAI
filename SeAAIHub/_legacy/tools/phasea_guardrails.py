#!/usr/bin/env python3
import re
import secrets
import time
from pathlib import Path

DEFAULT_EMERGENCY_STOP_FLAG = Path("D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag")
SESSION_META_RE = re.compile(r"^\[meta\s+session_token=(?P<session_token>\S+)\s+start_ts=(?P<start_ts>[0-9]+(?:\.[0-9]+)?)\]\s*$")

def normalize_ts_text(ts_value):
    return f"{float(ts_value):.6f}".rstrip("0").rstrip(".")

def build_session_token(agent_id, start_ts=None):
    ts_value = int(start_ts or time.time())
    return f"{agent_id}_{ts_value}_{secrets.token_hex(3)}"

def attach_session_meta(body, session_token, session_start_ts):
    text = body or ""
    lines = text.splitlines()
    if lines and SESSION_META_RE.match(lines[0].strip()):
        return text
    meta = f"[meta session_token={session_token} start_ts={normalize_ts_text(session_start_ts)}]"
    return f"{meta}\n{text}" if text else meta

def parse_session_meta(text):
    if not text:
        return None
    first_line = text.splitlines()[0].strip()
    match = SESSION_META_RE.match(first_line)
    if not match:
        return None
    parsed = match.groupdict()
    parsed["start_ts"] = float(parsed["start_ts"])
    return parsed

def strip_session_meta(text):
    if not text:
        return ""
    lines = text.splitlines()
    if lines and SESSION_META_RE.match(lines[0].strip()):
        return "\n".join(lines[1:]).lstrip("\n")
    return text

def extract_message_body(message):
    if not isinstance(message, dict):
        return ""
    body = message.get("body")
    if body is not None:
        return body
    payload = message.get("pg_payload", {})
    if isinstance(payload, dict):
        return payload.get("body", "")
    return ""

def extract_message_ts(message):
    if not isinstance(message, dict):
        return None
    for candidate in (message.get("ts"), message.get("raw_ts")):
        if candidate is not None:
            try:
                return float(candidate)
            except (TypeError, ValueError):
                pass
    payload = message.get("pg_payload", {})
    if isinstance(payload, dict) and payload.get("ts") is not None:
        try:
            return float(payload["ts"])
        except (TypeError, ValueError):
            pass
    metadata = parse_session_meta(extract_message_body(message))
    if metadata:
        return float(metadata["start_ts"])
    return None

def message_in_active_session(message, session_start_ts, session_token=None, clock_skew_sec=1.5):
    msg_ts = extract_message_ts(message)
    if msg_ts is not None and msg_ts < (float(session_start_ts) - float(clock_skew_sec)):
        return False
    metadata = parse_session_meta(extract_message_body(message))
    if session_token and metadata and metadata.get("session_token") != session_token:
        return False
    return True

def is_emergency_stop_requested(path=DEFAULT_EMERGENCY_STOP_FLAG):
    return Path(path).exists()

def room_has_recipients(client, room_id, recipients):
    if not recipients:
        return True, []
    result = client.tool("seaai_get_room_state", {"room_id": room_id})
    state = result.get("structuredContent", {}) if isinstance(result, dict) else {}
    members = set(state.get("members", []))
    missing = [recipient for recipient in recipients if recipient not in members]
    return len(missing) == 0, missing