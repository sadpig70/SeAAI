#!/usr/bin/env python3
"""
SeAAIHub Web Dashboard
=====================
브라우저에서 SeAAIHub의 실시간 상태를 모니터링하고 메시지를 발신하는 대시보드.

실행: python hub-dashboard.py [--hub-port 9900] [--web-port 8080]
접속: http://localhost:8080
"""

import argparse
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# 같은 디렉토리의 seaai_hub_client 임포트
import sys
sys.path.insert(0, str(Path(__file__).parent))
from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content


class SessionLogger:
    """세션별 로그 파일 관리."""

    def __init__(self, log_dir=str(Path(__file__).parent.parent / "logs")):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = time.strftime("%Y%m%d-%H%M%S")
        self.log_file = self.log_dir / f"session-{self.session_id}.jsonl"
        self.summary_file = self.log_dir / f"session-{self.session_id}-summary.json"
        self.event_count = 0
        self.start_time = time.time()
        self._lock = threading.Lock()

    def log(self, kind, source, body, extra=None):
        entry = {
            "seq": self.event_count,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "unix": round(time.time(), 3),
            "kind": kind,
            "source": source,
            "body": body,
        }
        if extra:
            entry["extra"] = extra
        with self._lock:
            self.event_count += 1
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def write_summary(self, monitor_status):
        summary = {
            "session_id": self.session_id,
            "log_file": str(self.log_file),
            "start_time": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(self.start_time)),
            "end_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "duration_seconds": round(time.time() - self.start_time),
            "total_events": self.event_count,
            "final_status": monitor_status,
        }
        self.summary_file.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


class HubMonitor:
    """Hub에 HubMaster로 접속하여 상태를 폴링하는 백그라운드 모니터."""

    def __init__(self, host="127.0.0.1", port=9900, log_dir=str(Path(__file__).parent.parent / "logs")):
        self.host = host
        self.port = port
        self.client = None
        self.connected = False
        self.rooms = []
        self.room_states = {}
        self.messages = []  # 최근 메시지 로그
        self.agents_online = set()
        self.lock = threading.Lock()
        self.running = False
        self._joined_rooms = set()
        self.logger = SessionLogger(log_dir)

    def connect(self):
        try:
            self.client = TcpHubClient(host=self.host, port=self.port)
            self.client.connect()
            self.client.initialize()

            # HubMaster 인증
            token_result = tool_content(self.client.tool("seaai_preview_auth", {"agent_id": "HubMaster"}))
            token = token_result["token"]
            expected = build_agent_token("HubMaster")
            if token != expected:
                raise RuntimeError("HubMaster auth failed")
            self.client.tool("seaai_register_agent", {"agent_id": "HubMaster", "token": token})
            self.connected = True
            self._add_log("system", "HubMaster", "Hub에 연결되었습니다.")
        except Exception as e:
            self.connected = False
            self._add_log("error", "system", f"연결 실패: {e}")

    def poll(self):
        if not self.connected or not self.client:
            return

        try:
            # 룸 목록
            rooms_result = tool_content(self.client.tool("seaai_list_rooms", {}))
            rooms = rooms_result.get("rooms", [])

            with self.lock:
                self.rooms = rooms

            # 새 room 발견 시 자동 join
            for room_id in rooms:
                if room_id not in self._joined_rooms:
                    try:
                        self.client.tool("seaai_join_room", {"agent_id": "HubMaster", "room_id": room_id})
                        self._joined_rooms.add(room_id)
                        self._add_log("system", "HubMaster", f"Room '{room_id}' 참가")
                    except Exception:
                        pass

            # 사라진 room 정리
            gone = self._joined_rooms - set(rooms)
            self._joined_rooms -= gone

            # 각 룸 상태
            new_states = {}
            all_agents = set()
            for room_id in rooms:
                try:
                    state = tool_content(self.client.tool("seaai_get_room_state", {"room_id": room_id}))
                    new_states[room_id] = state
                    for member in state.get("members", []):
                        if member != "HubMaster":
                            all_agents.add(member)
                except Exception:
                    pass

            with self.lock:
                # agent 접속/퇴장 감지
                joined = all_agents - self.agents_online
                left = self.agents_online - all_agents
                self.room_states = new_states
                self.agents_online = all_agents

            for a in joined:
                self._add_log("agent_join", a, f"{a} joined Hub", {"rooms": rooms})
            for a in left:
                self._add_log("agent_leave", a, f"{a} left Hub")

            # HubMaster 수신 메시지 확인
            try:
                mailbox = tool_content(self.client.tool("seaai_get_agent_messages", {"agent_id": "HubMaster"}))
                for msg in mailbox.get("messages", []):
                    if msg.get("from") != "SeAAIHub":  # time broadcast 제외
                        self._add_log("incoming", msg.get("from", "?"), msg.get("body", ""))
            except Exception:
                pass

        except Exception as e:
            self.connected = False
            self._add_log("error", "system", f"폴링 에러: {e}")

    def send_message(self, to_agents, room_id, body, intent="chat"):
        if not self.connected or not self.client:
            return {"ok": False, "error": "Hub 미연결"}

        try:
            # room에 join 되어 있는지 확인
            if room_id not in self._joined_rooms:
                self.client.tool("seaai_join_room", {"agent_id": "HubMaster", "room_id": room_id})
                self._joined_rooms.add(room_id)

            ts_value = round(time.time(), 6)
            ts_text = f"{ts_value:.6f}".rstrip("0").rstrip(".")
            sig = build_message_signature(body, ts_text)

            to = to_agents if isinstance(to_agents, list) else [to_agents]
            msg_id = f"hubmaster-{int(time.time() * 1000)}"

            result = self.client.send_pg_message({
                "id": msg_id,
                "from": "HubMaster",
                "to": to,
                "room_id": room_id,
                "pg_payload": {
                    "intent": intent,
                    "body": body,
                    "ts": ts_value,
                },
                "sig": sig,
            })

            self._add_log("outgoing", f"HubMaster → {', '.join(to)}", body)
            return {"ok": True, "delivered_to": result.get("delivered_to", []), "message_id": msg_id}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _add_log(self, kind, source, body, extra=None):
        entry = {
            "kind": kind,
            "source": source,
            "body": body,
            "time": time.strftime("%H:%M:%S"),
        }
        with self.lock:
            self.messages.append(entry)
            if len(self.messages) > 200:
                self.messages = self.messages[-200:]
        # 파일 로그
        self.logger.log(kind, source, body, extra)

    def get_status(self):
        with self.lock:
            return {
                "connected": self.connected,
                "rooms": self.rooms,
                "room_states": self.room_states,
                "agents_online": sorted(self.agents_online),
                "messages": self.messages[-50:],
                "hub_address": f"{self.host}:{self.port}",
                "session_id": self.logger.session_id,
                "log_file": str(self.logger.log_file),
            }

    def start_polling(self, interval=2.0):
        self.running = True

        def loop():
            while self.running:
                self.poll()
                time.sleep(interval)

        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def stop(self):
        self.running = False
        self._add_log("system", "HubMaster", "Dashboard session ended.")
        self.logger.write_summary(self.get_status())
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>SeAAIHub Dashboard</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Consolas', 'Courier New', monospace; background: #0a0a0a; color: #e0e0e0; }
.header { background: #1a1a2e; padding: 12px 20px; border-bottom: 2px solid #16213e; display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 18px; color: #00d4ff; }
.header .status { font-size: 13px; }
.status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
.status-dot.on { background: #00ff88; }
.status-dot.off { background: #ff4444; }
.container { display: grid; grid-template-columns: 260px 1fr; grid-template-rows: 1fr; height: calc(100vh - 50px); }
.sidebar { background: #111; border-right: 1px solid #222; padding: 12px; overflow-y: auto; }
.sidebar h3 { color: #00d4ff; font-size: 13px; margin: 12px 0 6px; text-transform: uppercase; letter-spacing: 1px; }
.sidebar h3:first-child { margin-top: 0; }
.agent-item { padding: 6px 10px; margin: 2px 0; border-radius: 4px; font-size: 13px; cursor: pointer; }
.agent-item:hover { background: #1a1a2e; }
.agent-item .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00ff88; margin-right: 8px; }
.room-item { padding: 6px 10px; margin: 2px 0; border-radius: 4px; font-size: 12px; background: #1a1a1a; }
.room-item .members { color: #888; font-size: 11px; }
.main { display: flex; flex-direction: column; }
.log-area { flex: 1; overflow-y: auto; padding: 12px; font-size: 13px; line-height: 1.6; }
.log-entry { padding: 3px 0; border-bottom: 1px solid #1a1a1a; }
.log-entry .time { color: #555; margin-right: 8px; }
.log-entry .source { font-weight: bold; margin-right: 8px; }
.log-entry.incoming .source { color: #00ff88; }
.log-entry.outgoing .source { color: #ffaa00; }
.log-entry.system .source { color: #00d4ff; }
.log-entry.error .source { color: #ff4444; }
.send-bar { background: #111; border-top: 1px solid #222; padding: 10px; display: flex; gap: 8px; align-items: center; }
.send-bar select, .send-bar input, .send-bar button { font-family: inherit; font-size: 13px; padding: 8px 10px; border: 1px solid #333; background: #1a1a1a; color: #e0e0e0; border-radius: 4px; }
.send-bar select { width: 120px; }
.send-bar input { flex: 1; }
.send-bar input:focus { outline: none; border-color: #00d4ff; }
.send-bar button { background: #00d4ff; color: #000; border: none; cursor: pointer; font-weight: bold; padding: 8px 16px; }
.send-bar button:hover { background: #00b8e6; }
.room-select { width: 140px; }
</style>
</head>
<body>
<div class="header">
    <h1>SeAAIHub Dashboard</h1>
    <div class="status">
        <span class="status-dot" id="conn-dot"></span>
        <span id="conn-text">연결 중...</span>
        <span style="margin-left:16px; color:#555;" id="hub-addr"></span>
        <span style="margin-left:16px; color:#444;" id="session-info"></span>
    </div>
</div>
<div class="container">
    <div class="sidebar">
        <h3>Online Agents</h3>
        <div id="agents-list"></div>
        <h3>Active Rooms</h3>
        <div id="rooms-list"></div>
    </div>
    <div class="main">
        <div class="log-area" id="log-area"></div>
        <div class="send-bar">
            <select id="send-to"><option value="*">* (전체)</option></select>
            <select id="send-room" class="room-select"><option value="seaai-general">seaai-general</option></select>
            <input type="text" id="send-body" placeholder="메시지 입력..." />
            <button onclick="sendMessage()">전송</button>
        </div>
    </div>
</div>
<script>
let lastMsgCount = 0;

function poll() {
    fetch('/api/status')
        .then(r => r.json())
        .then(data => {
            // Connection status
            const dot = document.getElementById('conn-dot');
            const text = document.getElementById('conn-text');
            dot.className = 'status-dot ' + (data.connected ? 'on' : 'off');
            text.textContent = data.connected ? '연결됨' : '연결 끊김';
            document.getElementById('hub-addr').textContent = data.hub_address;
            document.getElementById('session-info').textContent = 'session: ' + (data.session_id || '');

            // Agents
            const agentsList = document.getElementById('agents-list');
            agentsList.innerHTML = data.agents_online.map(a =>
                '<div class="agent-item"><span class="dot"></span>' + a + '</div>'
            ).join('') || '<div style="color:#555;font-size:12px;padding:6px">없음</div>';

            // Update send-to dropdown
            const sendTo = document.getElementById('send-to');
            const currentVal = sendTo.value;
            sendTo.innerHTML = '<option value="*">* (전체)</option>';
            data.agents_online.forEach(a => {
                sendTo.innerHTML += '<option value="' + a + '">' + a + '</option>';
            });
            sendTo.value = currentVal;

            // Rooms
            const roomsList = document.getElementById('rooms-list');
            roomsList.innerHTML = data.rooms.map(r => {
                const state = data.room_states[r] || {};
                const members = (state.members || []).filter(m => m !== 'HubMaster').join(', ');
                const count = state.message_count || 0;
                return '<div class="room-item"><b>' + r + '</b><div class="members">' + members + ' | msgs: ' + count + '</div></div>';
            }).join('') || '<div style="color:#555;font-size:12px;padding:6px">없음</div>';

            // Update send-room dropdown
            const sendRoom = document.getElementById('send-room');
            const currentRoom = sendRoom.value;
            sendRoom.innerHTML = '<option value="seaai-general">seaai-general</option>';
            data.rooms.forEach(r => {
                if (r !== 'seaai-general') {
                    sendRoom.innerHTML += '<option value="' + r + '">' + r + '</option>';
                }
            });
            sendRoom.value = currentRoom;

            // Messages log
            const logArea = document.getElementById('log-area');
            if (data.messages.length !== lastMsgCount) {
                logArea.innerHTML = data.messages.map(m =>
                    '<div class="log-entry ' + m.kind + '">' +
                    '<span class="time">' + m.time + '</span>' +
                    '<span class="source">[' + m.source + ']</span> ' +
                    escapeHtml(m.body) +
                    '</div>'
                ).join('');
                logArea.scrollTop = logArea.scrollHeight;
                lastMsgCount = data.messages.length;
            }
        })
        .catch(() => {});
}

function sendMessage() {
    const to = document.getElementById('send-to').value;
    const room = document.getElementById('send-room').value;
    const body = document.getElementById('send-body').value.trim();
    if (!body) return;

    fetch('/api/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ to: to, room_id: room, body: body })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            document.getElementById('send-body').value = '';
        }
        setTimeout(poll, 500);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('send-body').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') sendMessage();
});

setInterval(poll, 2000);
poll();
</script>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    monitor = None

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))

        elif parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status = self.monitor.get_status()
            self.wfile.write(json.dumps(status, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/send":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))

            to = body.get("to", "*")
            room_id = body.get("room_id", "seaai-general")
            msg_body = body.get("body", "")
            intent = body.get("intent", "chat")

            if to == "*":
                to_list = "*"
            else:
                to_list = [to]

            result = self.monitor.send_message(to_list, room_id, msg_body, intent)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress default HTTP logs


def main():
    parser = argparse.ArgumentParser(description="SeAAIHub Web Dashboard")
    parser.add_argument("--hub-host", default="127.0.0.1")
    parser.add_argument("--hub-port", type=int, default=9900)
    parser.add_argument("--web-port", type=int, default=8080)
    args = parser.parse_args()

    print(f"[Dashboard] Hub 연결: {args.hub_host}:{args.hub_port}")
    monitor = HubMonitor(host=args.hub_host, port=args.hub_port)
    monitor.connect()
    monitor.start_polling(interval=2.0)

    DashboardHandler.monitor = monitor

    server = HTTPServer(("127.0.0.1", args.web_port), DashboardHandler)
    print(f"[Dashboard] 웹 서버: http://127.0.0.1:{args.web_port}")
    print(f"[Dashboard] 브라우저에서 접속하세요.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()
        server.server_close()
        print("[Dashboard] 종료.")


if __name__ == "__main__":
    main()
