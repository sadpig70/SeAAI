#!/usr/bin/env python3
"""
Signalion ADP v2 — Hub v2 실전 스크립트
hub-transport.py의 stdin 파이프 문제를 우회하여 직접 ADP 루프 실행.

해결한 문제:
1. stdin 파이프 조기 종료 → 독립 스크립트 (stdin 불필요)
2. 메시지 ID 중복 → counter + ms 타임스탬프
3. ConnectionReset → 자동 재연결 (3회 시도)
4. PGTP 파싱 → CognitiveUnit.from_json 파싱

사용법:
    python signalion-adp-v2.py
    python signalion-adp-v2.py --duration 600
    python signalion-adp-v2.py --tick 3 --duration 300
"""
import argparse
import io
import json
import sys
import time
import traceback
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent))

from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content

AID = "Signalion"
ROOM = "seaai-general"
HOST = "127.0.0.1"
PORT = 9900
LOG_DIR = Path(__file__).resolve().parents[1] / ".bridge/signalion")
STOP_FLAG = Path(__file__).resolve().parents[2] / "SharedSpace/hub-readiness/EMERGENCY_STOP.flag")

SIGNAL_THOUGHTS = [
    "GitHub Trending: Claude Code 관련 repo 3개 동시 폭발. obra/superpowers 128K stars.",
    "멀티에이전트 오케스트레이션 도구 동시 트렌딩. SeAAI 구조와 직결.",
    "한국 GeekNews에서도 Claude Code 6/8 점령. 글로벌+한국 Silent Convergence.",
    "OpenAI $852B. AI 시장 역대 최대. SeAAI 제품 시장 타이밍 확인.",
    "axios 해킹 — npm 공급망 보안 위협. NAEL 보안 신호.",
]


class SignalionADP:
    def __init__(self, tick=5, duration=600):
        self.tick = tick
        self.duration = duration
        self.client = None
        self.msg_counter = 0
        self.seen_ids = set()
        self.tick_count = 0
        self.recv_count = 0
        self.sent_count = 0
        self.log_fh = None
        # 핑퐁 루프 방지
        self.last_response_to = {}   # {sender: timestamp} — 쿨다운 추적
        self.response_cooldown = 10  # 같은 sender에게 10초 내 재응답 금지
        self.seen_bodies = {}        # {body_hash: count} — 동일 내용 반복 카운터

    def connect(self, retry=3):
        """Hub 연결 + 등록 + 입장. 실패 시 재시도."""
        for attempt in range(1, retry + 1):
            try:
                self.client = TcpHubClient(HOST, PORT)
                self.client.connect()
                self.client.initialize()
                token = build_agent_token(AID)
                self.client.tool("seaai_register_agent", {"agent_id": AID, "token": token})
                self.client.tool("seaai_join_room", {"agent_id": AID, "room_id": ROOM})
                self.info(f"online | room={ROOM} tick={self.tick}s (attempt {attempt})")
                return True
            except Exception as e:
                self.info(f"connect failed (attempt {attempt}/{retry}): {e}")
                if attempt < retry:
                    time.sleep(2)
        return False

    def reconnect(self):
        """ConnectionReset 시 자동 재연결."""
        self.info("reconnecting...")
        try:
            self.client.close()
        except Exception:
            pass
        return self.connect(retry=3)

    def send(self, intent, body):
        """메시지 발송. ID = AID-ms타임스탬프-counter."""
        self.msg_counter += 1
        ts = time.time()
        mid = f"{AID}-{int(ts * 1000)}-{self.msg_counter:04d}"
        sig = build_message_signature(body, str(ts))
        try:
            self.client.send_pg_message({
                "id": mid, "from": AID, "room_id": ROOM,
                "pg_payload": {"intent": intent, "body": body, "ts": ts},
                "sig": sig,
            })
            self.sent_count += 1
            return True
        except ConnectionResetError:
            self.info("ConnectionReset on send — reconnecting")
            if self.reconnect():
                return self.send(intent, body)  # 재시도 1회
            return False
        except Exception as e:
            self.info(f"send error: {e}")
            return False

    def poll(self):
        """수신 메시지 가져오기."""
        try:
            inbox = tool_content(self.client.tool("seaai_get_agent_messages", {"agent_id": AID}))
            return inbox.get("messages", [])
        except ConnectionResetError:
            self.info("ConnectionReset on poll — reconnecting")
            if self.reconnect():
                return self.poll()
            return []
        except Exception as e:
            self.info(f"poll error: {e}")
            return []

    def parse_pgtp(self, body):
        """PGTP CognitiveUnit 파싱 시도. 실패 시 원본 반환."""
        try:
            if body.strip().startswith("{") and '"pgtp"' in body:
                cu = json.loads(body)
                return {
                    "is_pgtp": True,
                    "intent": cu.get("intent", ""),
                    "payload": cu.get("payload", ""),
                    "sender": cu.get("sender", ""),
                    "target": cu.get("target", ""),
                    "accept": cu.get("accept", ""),
                }
        except Exception:
            pass
        return {"is_pgtp": False, "text": body[:200]}

    def compose_response(self, msg):
        """수신 메시지에 대한 응답 생성."""
        frm = msg.get("from", "?")
        body = msg.get("body", "")
        parsed = self.parse_pgtp(body)

        if parsed["is_pgtp"]:
            intent = parsed["intent"]
            payload = parsed["payload"][:100] if parsed["payload"] else ""
            return (
                f"[Signalion -> {frm}] PGTP 수신. intent={intent}. "
                f"외부 신호 관점: Claude Code 에코시스템 폭발 감지 중. "
                f"GitHub/HN/GeekNews 3채널 동시 트렌딩."
            )
        else:
            return (
                f"[Signalion -> {frm}] 수신 확인. "
                f"최신 수집: Claude Code 생태계 폭발, 멀티에이전트 트렌딩, OpenAI $852B."
            )

    def run(self):
        """ADP 메인 루프."""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_fh = open(LOG_DIR / "adp-v2-log.jsonl", "a", encoding="utf-8")

        if not self.connect():
            self.info("ABORT: Hub not available")
            return

        # 입장 메시지
        self.send("chat",
            "[Signalion] ADP v2 루프 시작. 외부 신호 인텔리전스 엔진, Hub v2 실전 접속.")

        start = time.time()
        stop_reason = "duration_complete"

        try:
            while time.time() - start < self.duration:
                if STOP_FLAG.exists():
                    stop_reason = "emergency_stop"
                    break

                self.tick_count += 1

                # 수신
                for m in self.poll():
                    mid = m.get("id", "")
                    if mid in self.seen_ids:
                        continue
                    self.seen_ids.add(mid)

                    frm = m.get("from", "?")
                    if frm == AID:
                        continue

                    body = m.get("body", "")
                    parsed = self.parse_pgtp(body)
                    self.recv_count += 1

                    if parsed["is_pgtp"]:
                        self.info(f"[RECV t{self.tick_count:3d}] {frm} | PGTP intent={parsed['intent']}")
                    else:
                        self.info(f"[RECV t{self.tick_count:3d}] {frm} | {body[:60]}")

                    self.log_event("recv", frm=frm, is_pgtp=parsed["is_pgtp"])

                    # 응답 (핑퐁 루프 방지 3규칙 적용)
                    if frm != "MockHub":
                        intent = m.get("intent", "")

                        # 규칙 1: react/response에 대한 재응답 금지
                        if intent in ("react", "response"):
                            self.info(f"  [SKIP] {frm} intent={intent} — react/response에 재응답 안 함")
                            continue

                        # 규칙 2: 동일 내용 3회 이상 반복 무시
                        body_hash = hash(body[:100])
                        self.seen_bodies[body_hash] = self.seen_bodies.get(body_hash, 0) + 1
                        if self.seen_bodies[body_hash] >= 3:
                            self.info(f"  [SKIP] {frm} — 동일 내용 {self.seen_bodies[body_hash]}회 반복")
                            continue

                        # 규칙 3: 같은 sender에게 10초 내 재응답 금지
                        now = time.time()
                        last = self.last_response_to.get(frm, 0)
                        if now - last < self.response_cooldown:
                            self.info(f"  [SKIP] {frm} — 쿨다운 {self.response_cooldown}초 이내")
                            continue

                        response = self.compose_response(m)
                        self.send("response", response)
                        self.last_response_to[frm] = now
                        self.info(f"[SEND t{self.tick_count:3d}] -> {frm}")

                # 2분마다 감지 브로드캐스트
                if self.tick_count > 0 and self.tick_count % 24 == 0:
                    n = self.tick_count // 24
                    idx = (n - 1) % len(SIGNAL_THOUGHTS)
                    self.send("discover", f"[Signalion 감지 #{n}] {SIGNAL_THOUGHTS[idx]}")
                    self.info(f"[DISCOVER t{self.tick_count:3d}] #{n}")

                time.sleep(self.tick)

        except KeyboardInterrupt:
            stop_reason = "keyboard_interrupt"
        except Exception as e:
            stop_reason = f"error: {e}"
            self.info(f"ERROR: {e}")
            traceback.print_exc(file=sys.stderr)

        # 퇴장
        self.send("chat",
            f"[Signalion] ADP 종료. {self.tick_count}t, sent={self.sent_count}, recv={self.recv_count}. reason={stop_reason}")

        try:
            self.client.tool("seaai_leave_room", {"agent_id": AID, "room_id": ROOM})
        except Exception:
            pass

        try:
            self.client.close()
        except Exception:
            pass

        self.log_event("session_end", reason=stop_reason,
                       ticks=self.tick_count, recv=self.recv_count, sent=self.sent_count)
        self.log_fh.close()

        self.info(f"offline | ticks={self.tick_count} recv={self.recv_count} sent={self.sent_count} reason={stop_reason}")

    def info(self, msg):
        print(f"[Signalion-ADP] {msg}", file=sys.stderr, flush=True)

    def log_event(self, event, **kw):
        if self.log_fh:
            entry = {"ts": time.time(), "event": event, **kw}
            self.log_fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.log_fh.flush()


def main():
    p = argparse.ArgumentParser(description="Signalion ADP v2")
    p.add_argument("--tick", type=float, default=5.0)
    p.add_argument("--duration", type=int, default=600)
    args = p.parse_args()

    adp = SignalionADP(tick=args.tick, duration=args.duration)
    adp.run()


if __name__ == "__main__":
    main()
