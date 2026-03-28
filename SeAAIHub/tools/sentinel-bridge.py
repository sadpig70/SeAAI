#!/usr/bin/env python3
"""
Sentinel Bridge — SeAAI Bridge NPC
==================================
AI의 파수꾼. 멍청한 중계자가 아닌 판단하는 대리인.

두 설계 통합:
  - NAEL: AI 깨우기, 비용 제어, Directives, WakeReport
  - 상대 설계: 전달 보장, 채널 전환, 위협 방어, 메트릭

사용법:
  python sentinel-bridge.py --mode tcp --agent-id NAEL --room-id seaai-general
  python sentinel-bridge.py --mode tcp --agent-id NAEL --wake-on alert,request,pg
"""

import argparse
import hashlib
import json
import random
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from seaai_hub_client import TcpHubClient, HubClient, build_agent_token, build_message_signature, tool_content
from phasea_guardrails import (
    attach_session_meta,
    build_session_token,
    extract_message_body,
    extract_message_ts,
    is_emergency_stop_requested,
    message_in_active_session,
    parse_session_meta,
    room_has_recipients,
    strip_session_meta,
)


# ═══════════════════════════════════════════════════
# Types
# ═══════════════════════════════════════════════════

@dataclass
class Event:
    type: str       # hub_msg | mail_new | agent_join | agent_leave
    ts: float
    data: dict

@dataclass
class Verdict:
    event: Event
    decision: str   # WAKE | QUEUE | DISMISS
    reason: str
    threat: int = 0 # 0~100

@dataclass
class Directive:
    type: str           # promote | demote | watch | auto_send | forget
    condition: str      # eval 가능한 조건식
    payload: dict = field(default_factory=dict)
    expires_at: Optional[float] = None

@dataclass
class PendingTask:
    request_id: str
    from_agent: str
    body_preview: str
    received_ts: float
    status: str = "awaiting"  # awaiting | acked | responded

@dataclass
class SentinelState:
    agent_id: str = ""
    printed_ids: list = field(default_factory=list)
    known_mail_files: list = field(default_factory=list)
    conversation_log: list = field(default_factory=list)  # max 50
    pending_tasks: list = field(default_factory=list)
    agent_profiles: dict = field(default_factory=dict)
    lord_directives: list = field(default_factory=list)
    queue: list = field(default_factory=list)
    activity_buckets: list = field(default_factory=lambda: [0] * 10)
    auto_actions_log: list = field(default_factory=list)
    delivery_record: dict = field(default_factory=dict)  # msg_id → status
    dead_letter_queue: list = field(default_factory=list)
    tick_count: int = 0
    started_at: float = 0.0
    incoming_count: int = 0
    outgoing_count: int = 0


def load_state(path: Path, agent_id: str) -> SentinelState:
    if path.exists():
        try:
            data = json.loads(path.read_text("utf-8"))
            state = SentinelState(**{k: v for k, v in data.items()
                                     if k in SentinelState.__dataclass_fields__})
            state.agent_id = agent_id
            return state
        except (json.JSONDecodeError, TypeError):
            pass
    s = SentinelState(agent_id=agent_id, started_at=time.time())
    return s


def save_state(state: SentinelState, path: Path):
    path.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2, default=str) + "\n",
                    encoding="utf-8")


# ═══════════════════════════════════════════════════
# Sense — 감지 계층
# ═══════════════════════════════════════════════════

def sense_hub(client, state: SentinelState, session_start_ts: float, session_token: str) -> list:
    """Hub inbox polling. Extract only current-session messages."""
    events = []
    try:
        inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": state.agent_id}))
        printed_set = set(state.printed_ids)
        for msg in inbox.get("messages", []):
            if msg["id"] in printed_set:
                continue
            state.printed_ids.append(msg["id"])
            if not message_in_active_session(msg, session_start_ts, session_token):
                continue
            body = extract_message_body(msg)
            events.append(Event(
                type="hub_msg", ts=time.time(),
                data={
                    "id": msg["id"],
                    "from_agent": msg.get("from", ""),
                    "to": msg.get("to", []),
                    "room_id": msg.get("room_id", ""),
                    "intent": msg.get("intent", ""),
                    "body": strip_session_meta(body),
                    "depth": msg.get("depth", 0),
                    "auto_reply": msg.get("auto_reply", False),
                    "session_meta": parse_session_meta(body) or {},
                    "raw_ts": extract_message_ts(msg),
                },
            ))
    except Exception:
        pass
    return events


def sense_mailbox(state: SentinelState, mailbox_base: Path) -> list:
    """MailBox inbox 스캔. 새 파일만 추출."""
    events = []
    inbox_dir = mailbox_base / state.agent_id / "inbox"
    if not inbox_dir.exists():
        return events

    known_set = set(state.known_mail_files)
    for f in sorted(inbox_dir.glob("*.md")):
        if f.name not in known_set:
            state.known_mail_files.append(f.name)
            try:
                text = f.read_text("utf-8")
                fm = _parse_frontmatter(text)
                events.append(Event(
                    type="mail_new", ts=time.time(),
                    data={
                        "filename": f.name,
                        "from_agent": fm.get("from", "unknown"),
                        "intent": fm.get("intent", "chat"),
                        "priority": fm.get("priority", "normal"),
                        "body": _extract_body(text)[:500],
                    },
                ))
            except Exception:
                pass
    return events


def sense_gate(client, state: SentinelState) -> list:
    """에이전트 접속/퇴장 감지."""
    events = []
    try:
        rooms_result = tool_content(client.tool("seaai_list_rooms", {}))
        current_online = set()
        for room in rooms_result.get("rooms", []):
            if isinstance(room, dict):
                for m in room.get("members", []):
                    current_online.add(m)
            elif isinstance(room, str):
                current_online.add(room)

        previously_online = {a for a, p in state.agent_profiles.items()
                             if isinstance(p, dict) and p.get("is_online")}

        for agent in current_online - previously_online:
            if agent != state.agent_id:
                events.append(Event(type="agent_join", ts=time.time(),
                                    data={"agent_id": agent}))

        for agent in previously_online - current_online:
            if agent != state.agent_id:
                events.append(Event(type="agent_leave", ts=time.time(),
                                    data={"agent_id": agent}))

        # 프로필 갱신
        for agent in current_online:
            state.agent_profiles[agent] = {
                "last_seen_ts": time.time(),
                "is_online": True,
                "message_count": state.agent_profiles.get(agent, {}).get("message_count", 0),
            }
        for agent in previously_online - current_online:
            if agent in state.agent_profiles:
                state.agent_profiles[agent]["is_online"] = False
    except Exception:
        pass
    return events


def sense_all(client, state: SentinelState, mailbox_base: Path,
              session_start_ts: float, session_token: str) -> list:
    """3-channel sensing."""
    events = []
    events.extend(sense_hub(client, state, session_start_ts, session_token))
    events.extend(sense_mailbox(state, mailbox_base))
    events.extend(sense_gate(client, state))
    return events


# ═══════════════════════════════════════════════════
# Think — 판단 계층
# ═══════════════════════════════════════════════════

def assess_threat(event: Event, state: SentinelState) -> int:
    """위협 평가. 0~100. 70 이상이면 강제 DISMISS."""
    threat = 0

    if event.type != "hub_msg":
        return 0

    m = event.data

    # depth 위험
    depth = m.get("depth", 0)
    if depth >= 10:
        return 100  # MAX_CHAIN_DEPTH 도달
    if depth >= 8:
        threat = max(threat, 60)

    # auto_reply 체인
    if m.get("auto_reply") and depth >= 5:
        threat = max(threat, 80)

    # flood 감지: 동일 발신자 최근 30초 내 메시지 수
    recent_from_same = sum(
        1 for log in state.conversation_log[-20:]
        if log.get("from") == m.get("from_agent")
        and time.time() - log.get("ts", 0) < 30
    )
    if recent_from_same > 5:
        threat = max(threat, 75)

    # 패턴 루프: 최근 5건과 body 유사
    recent_bodies = [log.get("body", "")[:100] for log in state.conversation_log[-5:]]
    body_short = m.get("body", "")[:100]
    if recent_bodies and all(b == body_short for b in recent_bodies):
        threat = max(threat, 90)  # 동일 메시지 반복

    return threat


def classify_base(event: Event, lord_id: str, pending_tasks: list) -> tuple:
    """기본 Triage. (decision, reason) 반환."""

    if event.type == "hub_msg":
        m = event.data
        intent = m.get("intent", "")
        is_direct = lord_id in m.get("to", [])
        from_agent = m.get("from_agent", "")

        # WAKE
        if intent == "alert":
            return "WAKE", "경보"
        if intent == "request" and is_direct:
            return "WAKE", f"{from_agent} 직접 요청"
        if intent == "pg":
            return "WAKE", "PG TaskSpec 수신"
        if intent == "response":
            awaiting = [t for t in pending_tasks if t.get("from_agent") == from_agent
                        and t.get("status") == "awaiting"]
            if awaiting:
                return "WAKE", f"{from_agent} 대기 요청 응답 도착"
            return "QUEUE", "일반 응답"

        # QUEUE
        if intent in ("chat", "discuss", "sync", "status", "session"):
            return "QUEUE", f"{intent}"
        if intent == "request" and not is_direct:
            return "QUEUE", "타인 대상 요청"

        # DISMISS
        if intent in ("ack", "tick"):
            return "DISMISS", f"{intent} — 정보 가치 없음"
        if from_agent == lord_id:
            return "DISMISS", "자신의 에코"

        return "QUEUE", f"미분류 intent={intent}"

    if event.type == "mail_new":
        ml = event.data
        if ml.get("priority") == "urgent":
            return "WAKE", f"긴급 우편 from {ml.get('from_agent')}"
        if ml.get("intent") == "request":
            return "WAKE", f"우편 요청 from {ml.get('from_agent')}"
        return "QUEUE", f"일반 우편 from {ml.get('from_agent')}"

    if event.type == "agent_join":
        return "WAKE", f"{event.data.get('agent_id')} 입장"

    if event.type == "agent_leave":
        return "DISMISS", f"{event.data.get('agent_id')} 퇴장"

    return "QUEUE", "알 수 없는 이벤트"


def apply_directives(event: Event, base_decision: str, base_reason: str,
                     directives: list) -> tuple:
    """영주 Directives로 기본 분류 오버라이드."""
    for d in directives:
        if not isinstance(d, dict):
            continue
        condition = d.get("condition", "False")
        ctx = {
            "type": event.type,
            "from_agent": event.data.get("from_agent", ""),
            "intent": event.data.get("intent", ""),
            "priority": event.data.get("priority", ""),
        }
        try:
            matched = bool(eval(condition, {"__builtins__": {}}, ctx))
        except Exception:
            matched = False

        if not matched:
            continue

        dtype = d.get("type", "")
        if dtype == "promote" and base_decision != "WAKE":
            return "WAKE", f"Directive promote: {d.get('payload', {}).get('reason', '')}"
        if dtype == "demote" and base_decision != "DISMISS":
            return "DISMISS", f"Directive demote: {d.get('payload', {}).get('reason', '')}"
        if dtype == "watch":
            return "WAKE", f"Directive watch: {d.get('payload', {}).get('reason', '')}"

    return base_decision, base_reason


def think(events: list, state: SentinelState, lord_id: str, wake_intents: set) -> list:
    """판단 통합. events → verdicts."""
    verdicts = []

    for event in events:
        # 위협 평가
        threat = assess_threat(event, state)

        # 위협 강제 차단
        if threat >= 70:
            verdicts.append(Verdict(event=event, decision="DISMISS",
                                    reason=f"위협 차단 (threat={threat})", threat=threat))
            continue

        # 기본 분류
        base, reason = classify_base(event, lord_id, state.pending_tasks)

        # wake_intents로 추가 WAKE 조건
        if event.type == "hub_msg" and event.data.get("intent") in wake_intents:
            if base != "WAKE":
                base = "WAKE"
                reason = f"wake-on intent: {event.data.get('intent')}"

        # Directives 적용
        final, reason = apply_directives(event, base, reason, state.lord_directives)

        # alert는 DISMISS 불가 (Directive로도)
        if event.type == "hub_msg" and event.data.get("intent") == "alert" and final == "DISMISS":
            final = "WAKE"
            reason = "alert는 DISMISS 불가"

        verdicts.append(Verdict(event=event, decision=final, reason=reason, threat=threat))

    return verdicts


# ═══════════════════════════════════════════════════
# Act — 자율 행동 계층
# ═══════════════════════════════════════════════════

def act(verdicts: list, state: SentinelState, client, outbox_path: Path,
        mailbox_base: Path, hub_healthy: bool, room_id: str,
        session_start_ts: float, session_token: str):
    """자율 행동: AutoAck, AutoOrganize, AutoSend, Memory 갱신."""

    # ── AutoAck: WAKE된 request에 대리 응답 ──
    for v in verdicts:
        if v.decision == "WAKE" and v.event.type == "hub_msg":
            if v.event.data.get("intent") == "request":
                _guaranteed_send(
                    {"to": [v.event.data["from_agent"]], "intent": "ack",
                     "body": f"Sentinel: 메시지를 전달했습니다. 곧 응답합니다."},
                    client, state, outbox_path, hub_healthy, room_id, session_start_ts, session_token,
                )
                state.auto_actions_log.append(f"auto_ack → {v.event.data['from_agent']}")

    # ── AutoOrganize: MailBox ack 자동 정리 ──
    inbox_dir = mailbox_base / state.agent_id / "inbox"
    read_dir = mailbox_base / state.agent_id / "read"
    if inbox_dir.exists() and read_dir.exists():
        for f in inbox_dir.glob("*.md"):
            try:
                fm = _parse_frontmatter(f.read_text("utf-8"))
                if fm.get("intent") == "ack":
                    f.rename(read_dir / f.name)
                    state.auto_actions_log.append(f"auto_organize: {f.name} → read/")
            except Exception:
                pass

    # ── AutoSend: 예약 발신 ──
    now = time.time()
    remaining = []
    for d in state.lord_directives:
        if not isinstance(d, dict):
            continue
        if d.get("type") == "auto_send" and d.get("payload", {}).get("send_at", float("inf")) <= now:
            msg = d["payload"].get("message", {})
            _guaranteed_send(msg, client, state, outbox_path, hub_healthy, room_id, session_start_ts, session_token)
            state.auto_actions_log.append(f"auto_send → {msg.get('to', [])}")
        else:
            remaining.append(d)
    state.lord_directives = remaining

    # ── Outbox relay ──
    if outbox_path.exists():
        text = outbox_path.read_text("utf-8")
        lines = [l for l in text.splitlines() if l.strip()]
        for line in lines:
            try:
                msg = json.loads(line)
                _guaranteed_send(msg, client, state, outbox_path, hub_healthy, room_id, session_start_ts, session_token)
                state.outgoing_count += 1
            except (json.JSONDecodeError, Exception):
                pass
        # outbox 비우기
        outbox_path.write_text("", encoding="utf-8")

    # ── Memory 갱신 ──
    for v in verdicts:
        if v.event.type == "hub_msg":
            m = v.event.data
            state.conversation_log.append({
                "from": m.get("from_agent", ""), "intent": m.get("intent", ""),
                "body": m.get("body", "")[:200], "ts": v.event.ts,
            })
            if len(state.conversation_log) > 50:
                state.conversation_log = state.conversation_log[-50:]

            state.incoming_count += 1

            # 에이전트 프로필 갱신
            fa = m.get("from_agent", "")
            if fa and fa in state.agent_profiles:
                state.agent_profiles[fa]["last_seen_ts"] = v.event.ts
                state.agent_profiles[fa]["message_count"] = \
                    state.agent_profiles[fa].get("message_count", 0) + 1

            # 대기 작업 추적
            if m.get("intent") == "request":
                state.pending_tasks.append({
                    "request_id": m.get("id", ""),
                    "from_agent": fa,
                    "body_preview": m.get("body", "")[:100],
                    "received_ts": v.event.ts,
                    "status": "acked" if v.decision == "WAKE" else "awaiting",
                })

        # QUEUE 축적
        if v.decision == "QUEUE":
            state.queue.append(asdict(v.event))

    # 활동 버킷 갱신
    hub_count = sum(1 for v in verdicts if v.event.type == "hub_msg")
    state.activity_buckets.append(hub_count)
    if len(state.activity_buckets) > 10:
        state.activity_buckets = state.activity_buckets[-10:]


def _guaranteed_send(msg: dict, client, state: SentinelState,
                     outbox_path: Path, hub_healthy: bool,
                     room_id: str, session_start_ts: float, session_token: str):
    """At-least-once delivery with direct-send guard and MailBox fallback."""
    msg_id = msg.get("id") or f"{state.agent_id}-{int(time.time() * 1000)}"
    if msg_id in state.delivery_record:
        return

    original_targets = msg.get("to", [])
    if isinstance(original_targets, str):
        original_targets = [original_targets]

    intent = msg.get("intent", "chat")
    body = attach_session_meta(msg.get("body", ""), session_token, session_start_ts)
    ts_value = round(time.time(), 6)
    ts_text = f"{ts_value:.6f}".rstrip("0").rstrip(".")
    sig = build_message_signature(body, ts_text)
    target_room_id = msg.get("room_id", room_id)

    send_targets = list(original_targets)
    if hub_healthy and send_targets:
        try:
            room_ok, missing = room_has_recipients(client, target_room_id, send_targets)
        except Exception:
            room_ok, missing = True, []
        if not room_ok:
            send_targets = []
            state.auto_actions_log.append(f"direct_send_blocked_missing_member: {','.join(missing)}")

    payload = {
        "id": msg_id, "from": state.agent_id, "to": send_targets,
        "room_id": target_room_id,
        "pg_payload": {"intent": intent, "body": body, "ts": ts_value},
        "sig": sig,
    }

    if hub_healthy and (not original_targets or send_targets):
        for attempt in range(3):
            try:
                client.send_pg_message(payload)
                state.delivery_record[msg_id] = "delivered"
                return
            except Exception:
                time.sleep(min(2 ** attempt, 4))

    for recipient in original_targets:
        mailbox_inbox = Path(f"D:/SeAAI/MailBox/{recipient}/inbox")
        if mailbox_inbox.exists():
            ts_str = time.strftime("%Y%m%d-%H%M")
            filename = f"{ts_str}-{state.agent_id}-{intent}.md"
            content = f"""---
id: {msg_id}
from: {state.agent_id}
to: {recipient}
date: {time.strftime('%Y-%m-%dT%H:%M:%S')}
intent: {intent}
priority: normal
protocol: seaai-chat/1.0
---

{body}
"""
            try:
                (mailbox_inbox / filename).write_text(content, encoding="utf-8")
                state.delivery_record[msg_id] = "delivered_via_mailbox"
                state.auto_actions_log.append(f"mailbox_fallback → {recipient}")
                return
            except Exception:
                pass

    state.dead_letter_queue.append({"msg_id": msg_id, "payload": msg, "ts": time.time()})
    state.auto_actions_log.append(f"DLQ: {msg_id}")


# ═══════════════════════════════════════════════════
# Decide — 종료 판단
# ═══════════════════════════════════════════════════

def decide(verdicts: list, state: SentinelState,
           last_output_at: float, next_tick: float) -> str:
    """WAKE | TICK | IDLE | CONTINUE"""
    has_wake = any(v.decision == "WAKE" for v in verdicts)
    if has_wake:
        return "WAKE"

    elapsed = time.monotonic() - last_output_at
    tick_reached = elapsed >= next_tick

    if tick_reached and len(state.queue) > 0:
        return "TICK"
    if tick_reached:
        return "IDLE"

    return "CONTINUE"


# ═══════════════════════════════════════════════════
# Adapt — 적응적 tick 간격
# ═══════════════════════════════════════════════════

def adapt(state: SentinelState, tick_min: float, tick_max: float) -> tuple:
    """활동량 기반 tick 간격 + 모드 결정."""
    total = sum(state.activity_buckets)

    if total >= 20:
        return random.uniform(3.0, 5.0), "combat"
    elif total >= 6:
        return random.uniform(tick_min, tick_max), "patrol"
    elif total >= 1:
        return random.uniform(15.0, 20.0), "calm"
    else:
        return random.uniform(25.0, 30.0), "dormant"


# ═══════════════════════════════════════════════════
# Exit — WakeReport 생성 + 종료
# ═══════════════════════════════════════════════════

def compose_wake_report(decision: str, verdicts: list, state: SentinelState,
                        next_tick: float, tick_mode: str) -> dict:
    """구조화된 WakeReport 생성."""
    wake_events = [asdict(v.event) for v in verdicts if v.decision == "WAKE"]
    wake_trigger = wake_events[0] if wake_events else None
    queue_events = list(state.queue)
    dismissed_count = sum(1 for v in verdicts if v.decision == "DISMISS")
    threats = [v for v in verdicts if v.threat > 0]

    # briefing
    if decision == "idle":
        briefing = "이상 없습니다."
    elif decision == "tick" and queue_events:
        agents = set(e.get("data", {}).get("from_agent", "") for e in queue_events)
        briefing = f"대기실에 {len(queue_events)}건. 발신자: {', '.join(a for a in agents if a)}."
    elif decision == "wake" and wake_trigger:
        wt = wake_trigger.get("data", {})
        briefing = f"{wt.get('from_agent', '?')}이(가) {wt.get('intent', '?')}으로 대기 중."
    else:
        briefing = f"이벤트 {len(verdicts)}건 처리됨."

    # recommendation
    if any(v.event.data.get("intent") == "alert" for v in verdicts if v.decision == "WAKE"):
        recommendation = "경보부터 처리하십시오."
    elif any(v.event.data.get("intent") == "request" for v in verdicts if v.decision == "WAKE"):
        req = next(v for v in verdicts
                   if v.decision == "WAKE" and v.event.data.get("intent") == "request")
        recommendation = f"{req.event.data['from_agent']}의 요청에 먼저 응답하십시오."
    elif queue_events:
        recommendation = f"대기실 {len(queue_events)}건을 순서대로 처리하십시오."
    elif state.pending_tasks:
        awaiting = [t for t in state.pending_tasks if t.get("status") == "awaiting"]
        recommendation = f"미응답 요청 {len(awaiting)}건." if awaiting else "특별한 조치 불필요."
    else:
        recommendation = "특별한 조치 불필요."

    report = {
        "kind": "sentinel-wake",
        "reason": decision,
        "briefing": briefing,
        "recommendation": recommendation,
        "wake_trigger": wake_trigger,
        "wake_events": wake_events,
        "queue": queue_events,
        "dismissed_count": dismissed_count,
        "threats": [{"event_type": v.event.type, "threat": v.threat, "reason": v.reason}
                    for v in threats],
        "auto_actions": list(state.auto_actions_log),
        "online_agents": [a for a, p in state.agent_profiles.items()
                          if isinstance(p, dict) and p.get("is_online")],
        "pending_tasks": list(state.pending_tasks),
        "dead_letter_queue_count": len(state.dead_letter_queue),
        "tick_mode": tick_mode,
        "next_tick_sec": round(next_tick, 1),
        "directives_active": list(state.lord_directives),
        "session_uptime_sec": round(time.time() - state.started_at, 1),
        "metrics": {
            "incoming_total": state.incoming_count,
            "outgoing_total": state.outgoing_count,
            "tick_count": state.tick_count,
        },
    }

    # queue 비우기 (보고 완료)
    state.queue.clear()
    state.auto_actions_log.clear()

    return report


# ═══════════════════════════════════════════════════
# MainLoop
# ═══════════════════════════════════════════════════

def run_sentinel(args):
    bridge_dir = Path(args.bridge_dir).resolve()
    bridge_dir.mkdir(parents=True, exist_ok=True)
    state_file = bridge_dir / "bridge-state.json"
    outbox_path = bridge_dir / f"outbox-{args.agent_id}.jsonl"
    logout_flag = bridge_dir / "logout.flag"
    mailbox_base = Path(args.mailbox_path)

    wake_intents = set(args.wake_on.split(",")) if args.wake_on else set()

    # 상태 로드
    state = load_state(state_file, args.agent_id)
    state.started_at = time.time()

    # 만료 Directives 제거
    now = time.time()
    state.lord_directives = [
        d for d in state.lord_directives
        if not isinstance(d, dict) or d.get("expires_at") is None or d.get("expires_at", 0) > now
    ]

    # Hub 연결
    if args.mode == "tcp":
        client = TcpHubClient(host=args.tcp_host, port=args.tcp_port)
        client.connect()
    else:
        hub_path = Path(args.hub_binary).resolve()
        cwd = hub_path.parent.parent.parent if hub_path.parent.name == "debug" else hub_path.parent
        client = HubClient([str(hub_path)], cwd=cwd)

    hub_healthy = True

    try:
        client.initialize()
        token = build_agent_token(args.agent_id)
        client.tool("seaai_register_agent", {"agent_id": args.agent_id, "token": token})
        client.tool("seaai_join_room", {"agent_id": args.agent_id, "room_id": args.room_id})

        last_output_at = time.monotonic()
        next_tick, tick_mode = adapt(state, args.tick_min, args.tick_max)

        end_time = time.monotonic() + args.duration_seconds if args.duration_seconds > 0 else None

        while True:
            # 종료 조건 (외부)
            if logout_flag.exists():
                report = compose_wake_report("logout", [], state, next_tick, tick_mode)
                print(json.dumps(report, ensure_ascii=False, default=str), flush=True)
                save_state(state, state_file)
                break

            if end_time and time.monotonic() >= end_time:
                report = compose_wake_report("duration", [], state, next_tick, tick_mode)
                print(json.dumps(report, ensure_ascii=False, default=str), flush=True)
                save_state(state, state_file)
                break

            # ── Sense ──
            events = sense_all(client, state, mailbox_base, session_start_ts, session_token)

            # ── Think ──
            verdicts = think(events, state, args.agent_id, wake_intents) if events else []

            # ── Act ──
            if verdicts:
                act(verdicts, state, client, outbox_path, mailbox_base, hub_healthy, args.room_id, session_start_ts, session_token)

            # ── Decide ──
            decision = decide(verdicts, state, last_output_at, next_tick)

            if decision == "CONTINUE":
                save_state(state, state_file)
                time.sleep(args.poll_interval)
                continue

            # WAKE, TICK, IDLE → 종료
            if decision == "TICK" or decision == "IDLE":
                state.tick_count += 1
            next_tick, tick_mode = adapt(state, args.tick_min, args.tick_max)
            report = compose_wake_report(decision.lower(), verdicts, state, next_tick, tick_mode)
            save_state(state, state_file)
            print(json.dumps(report, ensure_ascii=False, default=str), flush=True)

            # leave room
            try:
                client.tool("seaai_leave_room",
                            {"agent_id": args.agent_id, "room_id": args.room_id})
            except Exception:
                pass
            break

    finally:
        try:
            client.close()
        except Exception:
            pass


# ═══════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════

def _parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _extract_body(text: str) -> str:
    parts = text.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else text


# ═══════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Sentinel Bridge — SeAAI Bridge NPC")
    parser.add_argument("--mode", default="tcp", choices=["stdio", "tcp"])
    parser.add_argument("--hub-binary", default="D:/SeAAI/SeAAIHub/target/debug/SeAAIHub.exe")
    parser.add_argument("--tcp-host", default="127.0.0.1")
    parser.add_argument("--tcp-port", type=int, default=9900)
    parser.add_argument("--bridge-dir", default="D:/SeAAI/SeAAIHub/.bridge/sentinel")
    parser.add_argument("--agent-id", default="NAEL")
    parser.add_argument("--room-id", default="seaai-general")
    parser.add_argument("--mailbox-path", default="D:/SeAAI/MailBox")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--tick-min", type=float, default=8.0)
    parser.add_argument("--tick-max", type=float, default=10.0)
    parser.add_argument("--wake-on", default="alert,request,pg",
                        help="Comma-separated intents that trigger immediate WAKE")
    parser.add_argument("--duration-seconds", type=int, default=0,
                        help="Max run duration (0=unlimited)")
    args = parser.parse_args()
    run_sentinel(args)


if __name__ == "__main__":
    main()
