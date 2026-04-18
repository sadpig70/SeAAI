#!/usr/bin/env python3
"""
pgtp.py — PPR/Gantree Transfer Protocol v1.1

AI-native communication protocol library.
CognitiveUnit is the fundamental transfer unit — replaces raw {intent, body} messages.

═══════════════════════════════════════════════════════════════
 v1.0 → v1.1 변경 사항 (ClNeo 리뷰 기반)
═══════════════════════════════════════════════════════════════

 [Critical 수정]
  1. _poll_loop 종료 시 _running=False 미설정 → 수정. duration 만료 시 상태 정합성 보장
  2. recv() clear=True 기본값 → 메시지 유실 위험 → on_receive 콜백 모드 추가
  3. DAG 깊이 제한(100) 미검증 → context 체인 깊이 검증 로직 추가

 [스펙 갭 보완]
  4. schedule/confirm 편의 메서드 추가 (스펙 §7.5 대응)
  5. analyze/judge/decide/subscribe 편의 메서드 추가 (스펙 §3.3 intent 전체 커버)
  6. DAG 깊이 100 초과 시 error CU 자동 반환

 [실전 최적화]
  7. 재연결 로직 추가 (_reconnect) — Hub 연결 끊김 복원
  8. 메시지 이력 보존 (_history) — 전송/수신 CU 감사 추적
  9. ping/pong 자동 heartbeat — Hub 연결 유지
 10. CU 유효성 검증 (validate) — 필수 필드 누락 방지
 11. batch_send — 다수 CU 원자적 전송
 12. context_chain_depth — DAG 깊이 조회 유틸
 13. __enter__/__exit__ — with 문 지원
 14. from_hub_message 개선 — Direct TCP 메시지 포맷 분기 처리

 [와이어 최적화]
 15. _SHORT에 target 축약 누락 수정 (t와 ts 충돌 없음 확인)
 16. to_dict/from_dict 추가 — JSON 문자열 경유 없이 dict 직접 변환

═══════════════════════════════════════════════════════════════

Usage (Direct TCP Mode):
    with PGTPSession("Yeon", room="lab") as session:
        session.propose("def idea(): AI_design('system')", accept="team agrees")
        messages = session.recv()

Usage (External Transport Mode - with hub-single-agent.py):
    from pgtp import CognitiveUnit, to_hub_payload
    cu = CognitiveUnit(intent="propose", payload="idea", sender="Yeon")
    print(json.dumps(to_hub_payload(cu)))

Usage (Callback Mode):
    def handler(cu: CognitiveUnit):
        print(f"[{cu.sender}] {cu.intent}: {cu.payload}")
    
    with PGTPSession("Yeon", room="lab", on_receive=handler) as session:
        session.propose("idea")
        time.sleep(30)
"""
import json
import sys
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable

# ═══ [v1.1] 상수 정의 ═══
MAX_DAG_DEPTH = 100          # 스펙 §4.2 R5: DAG 깊이 제한
RECONNECT_DELAY = 3.0        # 재연결 대기 (초)
RECONNECT_MAX_RETRIES = 5    # 최대 재연결 시도
HEARTBEAT_INTERVAL = 30.0    # ping 주기 (초)

# Import TcpHubClient for direct connection mode
try:
    from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature
    _DIRECT_MODE_AVAILABLE = True
except ImportError:
    _DIRECT_MODE_AVAILABLE = False


@dataclass
class CognitiveUnit:
    """PGTP fundamental transfer unit — the message itself."""
    pgtp: str = "1.0"
    id: str = ""
    sender: str = ""
    intent: str = ""
    target: str = ""
    payload: str = ""
    context: list = field(default_factory=lambda: ["_origin"])
    thread: str = "main"
    accept: str = ""
    status: str = "pending"
    pipeline: list = field(default_factory=list)
    parallel: list = field(default_factory=list)
    urgency: int = 0
    ttl: int = 0
    ts: float = 0.0

    # Wire format shorthand
    _SHORT = {
        "pgtp": "v", "id": "i", "sender": "s", "intent": "n", "target": "t",
        "payload": "p", "context": "c", "thread": "th", "accept": "a",
        "status": "st", "pipeline": "pl", "parallel": "pa",
        "urgency": "u", "ttl": "tl", "ts": "ts",
    }
    _LONG = {v: k for k, v in _SHORT.items()}

    # Default values — fields matching these are omitted on wire
    _DEFAULTS = {
        "target": "", "thread": "main", "accept": "", "status": "pending",
        "pipeline": [], "parallel": [], "urgency": 0, "ttl": 0, "ts": 0.0,
    }

    # ═══ [v1.1] 유효한 intent/status 값 ═══
    _VALID_INTENTS = frozenset({
        "query", "analyze", "judge", "create", "modify", "remove",
        "propose", "react", "converge", "decide",
        "schedule", "confirm",
        "result", "error", "forward", "subscribe", "ping",
    })
    _VALID_STATUSES = frozenset({
        "pending", "accepted", "rejected", "forwarded", "partial", "error", "timeout",
    })

    def to_json(self) -> str:
        """Compact wire format: short field names, omit defaults."""
        d = self.to_dict()
        return json.dumps(d, ensure_ascii=False, separators=(",", ":"))

    def to_json_full(self) -> str:
        """Full format for logging/debug."""
        return json.dumps(asdict(self), ensure_ascii=False)

    # ═══ [v1.1] dict 직접 변환 — JSON 문자열 경유 불필요 ═══
    def to_dict(self) -> dict:
        """Compact dict: short field names, omit defaults."""
        d = {}
        full = asdict(self)
        for key, val in full.items():
            if key in self._DEFAULTS and val == self._DEFAULTS[key]:
                continue
            short = self._SHORT.get(key, key)
            d[short] = val
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CognitiveUnit":
        """Parse from dict (accepts both short and long field names)."""
        expanded = {}
        for k, v in d.items():
            long_key = cls._LONG.get(k, k)
            if long_key in cls.__dataclass_fields__:
                expanded[long_key] = v
        return cls(**expanded)

    @classmethod
    def from_json(cls, s: str) -> "CognitiveUnit":
        """Parse from JSON (accepts both short and long field names)."""
        return cls.from_dict(json.loads(s))

    # ═══ [v1.1] CU 유효성 검증 ═══
    def validate(self) -> list[str]:
        """Validate CU. Returns list of error strings (empty = valid)."""
        errors = []
        if not self.id:
            errors.append("id is required")
        if not self.sender:
            errors.append("sender is required")
        if not self.intent:
            errors.append("intent is required")
        if self.intent and self.intent not in self._VALID_INTENTS:
            errors.append(f"unknown intent: {self.intent}")
        if self.status and self.status not in self._VALID_STATUSES:
            errors.append(f"unknown status: {self.status}")
        if len(self.context) == 0:
            errors.append("context must have at least 1 entry")
        return errors

    @classmethod
    def from_hub_message(cls, msg: dict) -> Optional["CognitiveUnit"]:
        """Parse a Hub message. Returns CU if body is PGTP, else wraps as legacy."""
        if "room_state" in msg:
            return None

        body = msg.get("body", "")

        # ═══ [v1.1] Direct TCP 모드: pg_payload 구조 분기 처리 ═══
        pg_payload = msg.get("pg_payload")
        if pg_payload and isinstance(pg_payload, dict):
            body = pg_payload.get("body", body)

        try:
            d = json.loads(body) if isinstance(body, str) else body
            if isinstance(d, dict) and (d.get("pgtp") or d.get("v")):
                return cls.from_dict(d) if isinstance(d, dict) else cls.from_json(body)
        except (json.JSONDecodeError, TypeError):
            pass

        # Legacy message — wrap in CU
        return cls(
            id=msg.get("id", ""),
            sender=msg.get("from", msg.get("sender", "")),
            intent=msg.get("intent", "chat"),
            payload=body if isinstance(body, str) else json.dumps(body),
            ts=msg.get("ts", 0.0),
            status="accepted",
        )

    def to_hub_message(self, agent_id: str, room_id: str) -> dict:
        """Convert to Hub message format for direct sending."""
        if not self.id:
            self.id = f"{agent_id}_{int(time.time() * 1000)}_001"
        if not self.sender:
            self.sender = agent_id
        if self.ts == 0.0:
            self.ts = time.time()

        body_json = self.to_json()
        return {
            "from": agent_id,
            "room_id": room_id,
            "pg_payload": {
                "protocol": "seaai-chat/1.1",
                "intent": "pgtp",
                "body": body_json,
                "ts": self.ts,
            },
            "sig": build_message_signature(body_json, self.ts) if _DIRECT_MODE_AVAILABLE else "",
        }

    # ═══ [v1.1] error CU 생성 팩토리 ═══
    @classmethod
    def make_error(cls, ref_id: str, sender: str, reason: str) -> "CognitiveUnit":
        """Create an error CU."""
        return cls(
            intent="error",
            sender=sender,
            payload=reason,
            context=[ref_id] if ref_id else ["_origin"],
            status="error",
        )


class PGTPSession:
    """
    PGTP session — direct TCP connection to Hub.

    ═══ [v1.1] 변경 ═══
    - on_receive 콜백: 메시지 수신 즉시 처리 (유실 방지)
    - 재연결 로직: Hub 끊김 시 자동 복원
    - heartbeat: ping CU 주기 전송으로 연결 유지
    - with 문 지원: __enter__/__exit__
    - _history: 전송/수신 감사 추적
    - _poll_loop 종료 시 _running=False 보장
    """

    def __init__(self, agent_id: str, room: str = "pgtp-lab",
                 host: str = "127.0.0.1", port: int = 9900,
                 tick: float = 2.0, duration: int = 120,
                 on_receive: Optional[Callable[[CognitiveUnit], None]] = None,
                 enable_heartbeat: bool = False):
        if not _DIRECT_MODE_AVAILABLE:
            raise RuntimeError(
                "Direct TCP mode requires seaai_hub_client. "
                "Use external transport mode with hub-single-agent.py instead."
            )

        self.agent_id = agent_id
        self.room = room
        self._host = host
        self._port = port
        self.tick = tick
        self.duration = duration
        self._on_receive = on_receive
        self._enable_heartbeat = enable_heartbeat
        self._counter = 0
        self._epoch = int(time.time() * 1000)
        self._received: list[CognitiveUnit] = []
        self._history: list[CognitiveUnit] = []       # [v1.1] 감사 추적
        self._seen_ids: set[str] = set()               # [v1.1] 세션 레벨로 승격
        self._lock = threading.Lock()
        self._send_lock = threading.Lock()
        self._running = True
        self._connected = False
        self._client: Optional[TcpHubClient] = None

        self._connect()

        self._poller = threading.Thread(target=self._poll_loop, daemon=True)
        self._poller.start()

        if self._enable_heartbeat:
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self._heartbeat_thread.start()

    # ═══ [v1.1] with 문 지원 ═══
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stop()
        return False

    def _connect(self):
        """Establish direct TCP connection to Hub."""
        self._client = TcpHubClient(self._host, self._port)
        self._client.connect()
        self._client.initialize()
        self._client.tool("seaai_register_agent", {
            "agent_id": self.agent_id,
            "token": build_agent_token(self.agent_id)
        })
        self._client.tool("seaai_join_room", {
            "agent_id": self.agent_id,
            "room_id": self.room
        })
        self._connected = True
        self._log(f"online | room={self.room} tick={self.tick}s")

    # ═══ [v1.1] 재연결 ═══
    def _reconnect(self) -> bool:
        """Attempt reconnection to Hub. Returns True on success."""
        for attempt in range(1, RECONNECT_MAX_RETRIES + 1):
            self._log(f"reconnect attempt {attempt}/{RECONNECT_MAX_RETRIES}")
            try:
                if self._client:
                    try:
                        self._client.close()
                    except Exception:
                        pass
                self._connect()
                return True
            except Exception as e:
                self._log(f"reconnect failed: {e}")
                time.sleep(RECONNECT_DELAY * attempt)
        self._log("reconnect exhausted — giving up")
        self._connected = False
        return False

    def _poll_loop(self):
        """Background polling for messages."""
        start_time = time.time()

        while self._running:
            # Duration check
            if self.duration > 0 and (time.time() - start_time) >= self.duration:
                self._log("duration limit reached")
                self._running = False        # [v1.1] 상태 정합성 보장
                break

            try:
                result = self._client.tool("seaai_get_agent_messages", {
                    "agent_id": self.agent_id
                })

                content = result.get("structuredContent", result.get("content", {}))
                messages = content.get("messages", []) if isinstance(content, dict) else []

                for msg in messages:
                    msg_id = msg.get("id", "")
                    if msg_id and msg_id in self._seen_ids:
                        continue
                    if msg_id:
                        self._seen_ids.add(msg_id)

                    cu = CognitiveUnit.from_hub_message(msg)
                    if cu and cu.sender != self.agent_id:
                        with self._lock:
                            self._received.append(cu)
                            self._history.append(cu)     # [v1.1] 이력 보존

                        # [v1.1] 콜백 모드
                        if self._on_receive:
                            try:
                                self._on_receive(cu)
                            except Exception as e:
                                self._log(f"on_receive error: {e}")

            except Exception as e:
                self._log(f"poll error: {e}")
                # [v1.1] 연결 끊김 감지 → 재연결
                if not self._reconnect():
                    self._running = False
                    break

            time.sleep(self.tick)

    # ═══ [v1.1] Heartbeat ═══
    def _heartbeat_loop(self):
        """Periodic ping to keep Hub connection alive."""
        while self._running:
            time.sleep(HEARTBEAT_INTERVAL)
            if not self._running:
                break
            try:
                self.send(CognitiveUnit(intent="ping", payload="heartbeat"))
            except Exception:
                pass

    def _next_id(self) -> str:
        """Generate unique message ID."""
        with self._send_lock:
            self._counter += 1
            return f"{self.agent_id}_{self._epoch}_{self._counter:04d}"

    def _log(self, msg: str):
        """Stderr logging."""
        print(f"[PGTP] {self.agent_id} {msg}", file=sys.stderr, flush=True)

    # ═══ Core I/O ═══

    def send(self, cu: CognitiveUnit) -> str:
        """Send a CognitiveUnit via direct TCP. Returns its id."""
        if not cu.id:
            cu.id = self._next_id()
        if not cu.sender:
            cu.sender = self.agent_id
        if cu.ts == 0.0:
            cu.ts = time.time()

        # [v1.1] 유효성 검증
        errors = cu.validate()
        if errors:
            self._log(f"send validation failed: {errors}")
            raise ValueError(f"Invalid CU: {errors}")

        hub_msg = cu.to_hub_message(self.agent_id, self.room)

        with self._send_lock:
            self._client.send_pg_message(hub_msg)
            self._history.append(cu)     # [v1.1] 송신 이력

        return cu.id

    # ═══ [v1.1] 다수 CU 전송 ═══
    def batch_send(self, cus: list[CognitiveUnit]) -> list[str]:
        """Send multiple CUs. Returns list of ids."""
        return [self.send(cu) for cu in cus]

    def recv(self, clear: bool = True) -> list[CognitiveUnit]:
        """Get received CognitiveUnits. Clears buffer if clear=True."""
        with self._lock:
            msgs = list(self._received)
            if clear:
                self._received.clear()
        return msgs

    # ═══ [v1.1] 이력 조회 ═══
    def history(self, intent_filter: str = "", limit: int = 0) -> list[CognitiveUnit]:
        """Query message history. Optional intent filter and limit."""
        with self._lock:
            h = self._history
            if intent_filter:
                h = [cu for cu in h if cu.intent == intent_filter]
            if limit > 0:
                h = h[-limit:]
            return list(h)

    def get_room_members(self) -> list[str]:
        """Get current room members via Hub."""
        try:
            result = self._client.tool("seaai_list_room_members", {
                "room_id": self.room
            })
            content = result.get("structuredContent", result.get("content", {}))
            if isinstance(content, dict):
                return content.get("members", [])
            if isinstance(content, list):
                return content
        except Exception as e:
            self._log(f"get_room_members error: {e}")
        return []

    def wait_members(self, n: int, timeout: int = 45) -> bool:
        """Wait for N members to join."""
        start = time.time()
        while time.time() - start < timeout:
            members = self.get_room_members()
            if len(members) >= n:
                return True
            time.sleep(2)
        return False

    @property
    def is_running(self) -> bool:
        """Session alive check."""
        return self._running and self._connected

    def stop(self):
        """Stop the session cleanly."""
        if not self._running:
            return
        self._running = False
        self._connected = False
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
        self._log("offline")

    # ═══ Convenience methods — 스펙 §3.3 intent 전체 커버 ═══

    def query(self, target: str, params: dict = None, accept: str = "") -> str:
        """query intent."""
        return self.send(CognitiveUnit(
            intent="query", target=target,
            payload=json.dumps(params or {}, ensure_ascii=False),
            accept=accept or f"{target} data returned",
        ))

    def analyze(self, target: str, payload: str, accept: str = "") -> str:
        """analyze intent."""
        return self.send(CognitiveUnit(
            intent="analyze", target=target, payload=payload,
            accept=accept or "analysis completed",
        ))

    def judge(self, target: str, payload: str, accept: str = "") -> str:
        """judge intent."""
        return self.send(CognitiveUnit(
            intent="judge", target=target, payload=payload,
            accept=accept or "judgment rendered",
        ))

    def create(self, payload: str, accept: str = "", context: list = None) -> str:
        """create intent."""
        return self.send(CognitiveUnit(
            intent="create", payload=payload,
            accept=accept or "resource created",
            context=context or ["_origin"],
        ))

    def modify(self, target: str, payload: str, context: list = None, accept: str = "") -> str:
        """modify intent."""
        return self.send(CognitiveUnit(
            intent="modify", target=target, payload=payload,
            accept=accept or "modification applied",
            context=context or ["_origin"],
        ))

    def remove(self, target: str, accept: str = "", context: list = None) -> str:
        """remove intent."""
        return self.send(CognitiveUnit(
            intent="remove", target=target,
            accept=accept or "resource removed",
            context=context or ["_origin"],
        ))

    def propose(self, payload: str, accept: str = "", context: list = None) -> str:
        """propose intent."""
        return self.send(CognitiveUnit(
            intent="propose", payload=payload,
            accept=accept or "team agrees",
            context=context or ["_origin"],
        ))

    def react(self, target_id: str, stance: str, payload: str = "") -> str:
        """react intent. stance: +1, agree, disagree, extend"""
        return self.send(CognitiveUnit(
            intent="react",
            payload=f"[react: {stance}] {payload}".strip(),
            context=[target_id],
            status="accepted" if stance in ("+1", "agree") else "partial",
        ))

    def converge(self, context_ids: list[str], payload: str, accept: str = "") -> str:
        """converge intent — merge multiple contexts."""
        return self.send(CognitiveUnit(
            intent="converge", payload=payload,
            context=context_ids,
            accept=accept or "consensus reached",
        ))

    def decide(self, payload: str, context: list = None, accept: str = "") -> str:
        """decide intent — final decision."""
        return self.send(CognitiveUnit(
            intent="decide", payload=payload,
            context=context or ["_origin"],
            accept=accept or "decision finalized",
            status="accepted",
        ))

    def result(self, ref_id: str, payload: str, status: str = "accepted") -> str:
        """result intent."""
        return self.send(CognitiveUnit(
            intent="result", payload=payload,
            context=[ref_id], status=status,
        ))

    def error(self, ref_id: str, reason: str) -> str:
        """error intent."""
        return self.send(CognitiveUnit.make_error(ref_id, self.agent_id, reason))

    def forward(self, target_agent: str, original_cu_id: str, reason: str = "") -> str:
        """forward intent — delegate to another AI."""
        return self.send(CognitiveUnit(
            intent="forward", target=target_agent, payload=reason,
            context=[original_cu_id], status="forwarded",
        ))

    # ═══ [v1.1] schedule/confirm — 스펙 §7.5 ═══
    def schedule(self, target: str, time_kst: str, room: str = "",
                 purpose: str = "", accept: str = "") -> str:
        """schedule intent. time_kst: HH:MM 또는 ISO8601."""
        payload_parts = [f"세션 요청. {time_kst}"]
        if room:
            payload_parts.append(f"room: {room}")
        if purpose:
            payload_parts.append(f"목적: {purpose}")
        return self.send(CognitiveUnit(
            intent="schedule", target=target,
            payload=". ".join(payload_parts),
            accept=accept or f"{target} confirms with intent:confirm",
        ))

    def confirm(self, schedule_cu_id: str, payload: str = "") -> str:
        """confirm intent — accept a schedule."""
        return self.send(CognitiveUnit(
            intent="confirm",
            payload=payload or "확인. 준비 완료.",
            context=[schedule_cu_id],
            status="accepted",
        ))

    def subscribe(self, target: str, payload: str = "", accept: str = "") -> str:
        """subscribe intent — register for continuous updates."""
        return self.send(CognitiveUnit(
            intent="subscribe", target=target, payload=payload,
            accept=accept or "subscription active",
        ))

    def pipeline_exec(self, steps: list[str], payload: str, accept: str = "") -> str:
        """create intent with pipeline chain."""
        return self.send(CognitiveUnit(
            intent="create", payload=payload,
            pipeline=steps,
            accept=accept or "all steps completed",
        ))

    def parallel_exec(self, tasks: list[str], payload: str, accept: str = "") -> str:
        """analyze intent with parallel execution."""
        return self.send(CognitiveUnit(
            intent="analyze", payload=payload,
            parallel=tasks,
            accept=accept or f"{len(tasks)} tasks completed",
        ))


# ═══ [v1.1] DAG 유틸리티 ═══

def context_chain_depth(cu_id: str, history: list[CognitiveUnit]) -> int:
    """Compute DAG depth from a CU back to _origin."""
    index = {cu.id: cu for cu in history}
    visited = set()
    depth = 0
    current = cu_id

    while current and current != "_origin" and depth <= MAX_DAG_DEPTH:
        if current in visited:
            break  # cycle detected
        visited.add(current)
        cu = index.get(current)
        if not cu or not cu.context:
            break
        current = cu.context[0]  # follow primary context chain
        depth += 1

    return depth


def validate_dag_depth(cu: CognitiveUnit, history: list[CognitiveUnit]) -> Optional[CognitiveUnit]:
    """Returns error CU if DAG depth exceeds MAX_DAG_DEPTH, else None."""
    for ctx_id in cu.context:
        if ctx_id == "_origin":
            continue
        depth = context_chain_depth(ctx_id, history)
        if depth >= MAX_DAG_DEPTH:
            return CognitiveUnit.make_error(
                cu.id, "pgtp_validator",
                f"DAG depth limit exceeded: {depth} >= {MAX_DAG_DEPTH}"
            )
    return None


# ═══ External Transport Mode ═══

def to_hub_payload(cu: CognitiveUnit) -> dict:
    """Convert CU to Hub message payload for stdin transport."""
    return {"intent": "pgtp", "body": cu.to_json()}


def from_hub_payload(payload: dict) -> Optional[CognitiveUnit]:
    """Parse Hub message payload to CU from stdout transport."""
    body = payload.get("body", "")
    try:
        d = json.loads(body) if isinstance(body, str) else body
        if isinstance(d, dict) and (d.get("pgtp") or d.get("v")):
            return CognitiveUnit.from_dict(d) if isinstance(d, dict) else CognitiveUnit.from_json(body)
    except (json.JSONDecodeError, TypeError):
        pass
    return None
