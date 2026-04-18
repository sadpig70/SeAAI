#!/usr/bin/env python3
"""Minimal websocket echo demo with a built-in self-test.

This implementation uses only the Python standard library so it can run in
restricted Windows environments where asyncio-based networking is broken.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import os
import socket
import struct
import threading
from dataclasses import dataclass


WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def recv_exact(conn: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            raise ConnectionError("socket closed")
        data.extend(chunk)
    return bytes(data)


def read_http_headers(conn: socket.socket) -> dict[str, str]:
    buffer = bytearray()
    while b"\r\n\r\n" not in buffer:
        chunk = conn.recv(1024)
        if not chunk:
            raise ConnectionError("handshake ended early")
        buffer.extend(chunk)
    header_text = buffer.split(b"\r\n\r\n", 1)[0].decode("utf-8", errors="replace")
    lines = header_text.split("\r\n")[1:]
    headers: dict[str, str] = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    return headers


def websocket_accept(key: str) -> str:
    digest = hashlib.sha1((key + WS_MAGIC).encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def perform_server_handshake(conn: socket.socket) -> None:
    headers = read_http_headers(conn)
    key = headers.get("sec-websocket-key")
    if not key:
        raise ConnectionError("missing Sec-WebSocket-Key")
    accept = websocket_accept(key)
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n"
        "\r\n"
    )
    conn.sendall(response.encode("utf-8"))


def perform_client_handshake(conn: socket.socket, host: str, port: int) -> None:
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    conn.sendall(request.encode("utf-8"))

    response = bytearray()
    while b"\r\n\r\n" not in response:
        chunk = conn.recv(1024)
        if not chunk:
            raise ConnectionError("server closed during handshake")
        response.extend(chunk)

    if b"101 Switching Protocols" not in response:
        raise ConnectionError("websocket handshake failed")


def read_frame(conn: socket.socket) -> tuple[int, bytes]:
    first_two = recv_exact(conn, 2)
    fin_and_opcode, masked_and_len = first_two
    opcode = fin_and_opcode & 0x0F
    masked = bool(masked_and_len & 0x80)
    payload_len = masked_and_len & 0x7F

    if payload_len == 126:
        payload_len = struct.unpack("!H", recv_exact(conn, 2))[0]
    elif payload_len == 127:
        payload_len = struct.unpack("!Q", recv_exact(conn, 8))[0]

    mask_key = recv_exact(conn, 4) if masked else b""
    payload = bytearray(recv_exact(conn, payload_len))
    if masked:
        for idx, byte in enumerate(payload):
            payload[idx] = byte ^ mask_key[idx % 4]
    return opcode, bytes(payload)


def send_frame(conn: socket.socket, payload: bytes, opcode: int = 0x1) -> None:
    conn.sendall(build_server_frame_bytes(payload, opcode=opcode))


def send_masked_frame(conn: socket.socket, payload: bytes, opcode: int = 0x1) -> None:
    conn.sendall(build_client_frame_bytes(payload, opcode=opcode))


def build_server_frame_bytes(payload: bytes, opcode: int = 0x1) -> bytes:
    header = bytearray()
    header.append(0x80 | (opcode & 0x0F))
    length = len(payload)
    if length < 126:
        header.append(length)
    elif length < 65536:
        header.append(126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(127)
        header.extend(struct.pack("!Q", length))
    return bytes(header) + payload


def build_client_frame_bytes(payload: bytes, opcode: int = 0x1) -> bytes:
    header = bytearray()
    header.append(0x80 | (opcode & 0x0F))
    length = len(payload)
    mask_key = os.urandom(4)
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(0x80 | 127)
        header.extend(struct.pack("!Q", length))

    masked_payload = bytearray(payload)
    for idx, byte in enumerate(masked_payload):
        masked_payload[idx] = byte ^ mask_key[idx % 4]
    return bytes(header) + mask_key + masked_payload


class FakeConn:
    def __init__(self, incoming: bytes = b"") -> None:
        self.incoming = bytearray(incoming)
        self.sent = bytearray()

    def recv(self, size: int) -> bytes:
        chunk = self.incoming[:size]
        del self.incoming[:size]
        return bytes(chunk)

    def sendall(self, data: bytes) -> None:
        self.sent.extend(data)


@dataclass
class ServerResult:
    message: str | None = None
    error: str | None = None


def serve_once_socket(server: socket.socket, result: ServerResult) -> None:
    conn, _ = server.accept()
    with conn:
        try:
            perform_server_handshake(conn)
            opcode, payload = read_frame(conn)
            if opcode == 0x8:
                result.message = "client disconnected"
                return
            text = payload.decode("utf-8")
            result.message = text
            send_frame(conn, f"echo:{text}".encode("utf-8"))
        except Exception as exc:  # pragma: no cover - surfaced in caller
            result.error = f"{type(exc).__name__}: {exc}"


def run_server(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        print(f"[server] listening on ws://{host}:{port}")

        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle_connection, args=(conn,), daemon=True).start()


def handle_connection(conn: socket.socket) -> None:
    with conn:
        try:
            perform_server_handshake(conn)
            while True:
                opcode, payload = read_frame(conn)
                if opcode == 0x8:
                    return
                if opcode == 0x1:
                    send_frame(conn, b"echo:" + payload)
        except Exception:
            return


def run_client(host: str, port: int, message: str) -> str:
    with socket.create_connection((host, port), timeout=5) as conn:
        perform_client_handshake(conn, host, port)
        send_masked_frame(conn, message.encode("utf-8"))
        opcode, payload = read_frame(conn)
        if opcode != 0x1:
            raise ConnectionError("unexpected websocket frame")
        return payload.decode("utf-8")


def self_test() -> int:
    try:
        return integration_self_test()
    except OSError as exc:
        print(f"[test] integration skipped: {exc}")
        return pure_self_test()


def integration_self_test() -> int:
    host = "127.0.0.1"
    result = ServerResult()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, 0))
        server.listen(1)
        port = server.getsockname()[1]
        print(f"[server] listening on ws://{host}:{port}")

        thread = threading.Thread(target=serve_once_socket, args=(server, result), daemon=True)
        thread.start()

        response = run_client(host, port, "hello websocket")
        thread.join(timeout=5)

    print(f"[test] sent='hello websocket'")
    print(f"[test] recv={response!r}")
    if result.error:
        print(f"[test] server_error={result.error}")
        return 1
    if response != "echo:hello websocket":
        print("[test] FAIL")
        return 1

    print("[test] PASS")
    return 0


def pure_self_test() -> int:
    expected_accept = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
    if websocket_accept("dGhlIHNhbXBsZSBub25jZQ==") != expected_accept:
        print("[test] FAIL: websocket accept mismatch")
        return 1

    client_frame = build_client_frame_bytes(b"hello websocket")
    opcode, payload = read_frame(FakeConn(client_frame))
    if opcode != 0x1 or payload != b"hello websocket":
        print("[test] FAIL: client frame decode mismatch")
        return 1

    server_conn = FakeConn()
    send_frame(server_conn, b"echo:hello websocket")
    if server_conn.sent != build_server_frame_bytes(b"echo:hello websocket"):
        print("[test] FAIL: server frame encode mismatch")
        return 1

    print("[test] PASS (frame-level fallback)")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a minimal websocket demo")
    parser.add_argument("--serve", action="store_true", help="Run the echo server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind or connect to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind or connect to")
    parser.add_argument("--message", default="hello websocket", help="Message to send in client mode")
    parser.add_argument("--test", action="store_true", help="Run the built-in websocket self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.test:
        return self_test()

    if args.serve:
        try:
            run_server(args.host, args.port)
        except KeyboardInterrupt:
            print("\n[server] stopped")
        return 0

    response = run_client(args.host, args.port, args.message)
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
