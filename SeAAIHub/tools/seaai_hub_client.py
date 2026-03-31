#!/usr/bin/env python3
import hashlib
import hmac
import json
import socket
import subprocess


SHARED_SECRET = b"seaai-shared-secret"


class HubClient:
    """stdio 모드: Hub를 자식 프로세스로 실행"""
    def __init__(self, command, cwd):
        self.proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self._id = 0
        self._sock = None

    def close(self):
        if self.proc.stdin:
            self.proc.stdin.close()
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)

    def request(self, method, params=None, expect_response=True):
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._id if expect_response else None,
            "method": method,
            "params": params or {},
        }
        line = json.dumps(payload, ensure_ascii=False)
        assert self.proc.stdin is not None
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

        if not expect_response:
            return None

        assert self.proc.stdout is not None
        response_line = self.proc.stdout.readline()
        if not response_line:
            stderr = ""
            if self.proc.stderr is not None:
                stderr = self.proc.stderr.read()
            raise RuntimeError(f"Hub closed unexpectedly. stderr={stderr}")
        response = json.loads(response_line)
        if response.get("error"):
            raise RuntimeError(response["error"]["message"])
        return response["result"]

    def initialize(self):
        return self.request("initialize", {})

    def tool(self, name, arguments):
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def send_pg_message(self, payload):
        return self.request("seaai/message", payload)


class TcpHubClient:
    """TCP 모드: 외부에서 실행 중인 Hub에 TCP 소켓으로 연결"""
    def __init__(self, host="127.0.0.1", port=9900):
        self._host = host
        self._port = port
        self._id = 0
        self._sock = None
        self._rfile = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))
        self._rfile = self._sock.makefile("r", encoding="utf-8")

    def close(self):
        if self._rfile:
            self._rfile.close()
        if self._sock:
            self._sock.close()

    def request(self, method, params=None, expect_response=True):
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._id if expect_response else None,
            "method": method,
            "params": params or {},
        }
        line = json.dumps(payload, ensure_ascii=False) + "\n"
        self._sock.sendall(line.encode("utf-8"))

        if not expect_response:
            return None

        response_line = self._rfile.readline()
        if not response_line:
            raise RuntimeError("Hub TCP connection closed unexpectedly.")
        response = json.loads(response_line)
        if response.get("error"):
            raise RuntimeError(response["error"]["message"])
        return response["result"]

    def initialize(self):
        return self.request("initialize", {})

    def tool(self, name, arguments):
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def send_pg_message(self, payload):
        return self.request("seaai/message", payload)


def tool_content(result):
    return result.get("structuredContent", {})


def build_agent_token(agent_id):
    return hmac.new(SHARED_SECRET, agent_id.encode("utf-8"), hashlib.sha256).hexdigest()


def build_message_signature(body, ts):
    """Sign message body + timestamp. Canonical ts: integer milliseconds."""
    ts_millis = str(int(float(ts) * 1000))
    digest = hashlib.sha256()
    digest.update(body.encode("utf-8"))
    digest.update(ts_millis.encode("utf-8"))
    return hmac.new(SHARED_SECRET, digest.digest(), hashlib.sha256).hexdigest()
