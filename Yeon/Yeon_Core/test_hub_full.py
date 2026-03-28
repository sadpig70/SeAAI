#!/usr/bin/env python3
"""
SeAAIHub 9900 완전 연결 테스트
- initialize
- tools/list
- seaai_preview_auth (Yeon 토큰 확인)
"""

import socket
import json
import time
import hmac
import hashlib
from datetime import datetime

HUB_HOST = "127.0.0.1"
HUB_PORT = 9900

def send_jsonrpc(sock, method, params=None, msg_id=None):
    """JSON-RPC 요청 전송"""
    req = {
        "jsonrpc": "2.0",
        "method": method,
        "id": msg_id if msg_id is not None else int(time.time() * 1000) % 10000
    }
    if params is not None:
        req["params"] = params
    
    msg = json.dumps(req, ensure_ascii=False) + '\n'
    sock.send(msg.encode('utf-8'))
    print(f"    → {method}")
    return req["id"]

def recv_response(sock, timeout=5):
    """JSON-RPC 응답 수신"""
    sock.settimeout(timeout)
    try:
        data = sock.recv(8192)
        if data:
            lines = data.decode('utf-8').strip().split('\n')
            for line in lines:
                if line:
                    try:
                        resp = json.loads(line)
                        print(f"    ← 응답 (id={resp.get('id')})")
                        return resp
                    except:
                        print(f"    ← 원시: {line[:80]}")
                        return {"raw": line}
    except socket.timeout:
        return None
    except Exception as e:
        print(f"    ← 오류: {e}")
        return None
    return None

def main():
    print("=" * 60)
    print("SeAAIHub 9900 완전 연결 테스트")
    print("=" * 60)
    
    # TCP 연결
    print(f"\n[1] TCP 연결...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((HUB_HOST, HUB_PORT))
        print(f"    ✅ 연결 성공")
    except Exception as e:
        print(f"    ❌ 연결 실패: {e}")
        return False
    
    # 1. initialize
    print(f"\n[2] initialize...")
    send_jsonrpc(sock, "initialize", {}, 1)
    resp = recv_response(sock, 3)
    if resp and "result" in resp:
        print(f"    ✅ 프로토콜 버전: {resp['result'].get('protocolVersion')}")
        print(f"    서버 정보: {resp['result'].get('serverInfo')}")
    elif resp and "error" in resp:
        print(f"    ⚠️  오류: {resp['error']}")
    
    # 2. notifications/initialized
    print(f"\n[3] notifications/initialized...")
    send_jsonrpc(sock, "notifications/initialized", {}, 2)
    print(f"    ✅ 전송 완료 (응답 없음)")
    
    # 3. tools/list
    print(f"\n[4] tools/list...")
    send_jsonrpc(sock, "tools/list", {}, 3)
    resp = recv_response(sock, 3)
    if resp and "result" in resp:
        tools = resp["result"].get("tools", [])
        print(f"    ✅ 사용 가능한 툴: {len(tools)}개")
        for tool in tools:
            print(f"       - {tool.get('name')}: {tool.get('description', '')[:40]}...")
    
    # 4. seaai_preview_auth (Yeon 토큰 확인)
    print(f"\n[5] seaai_preview_auth (Yeon)...")
    send_jsonrpc(sock, "tools/call", {
        "name": "seaai_preview_auth",
        "arguments": {"agent_id": "Yeon"}
    }, 4)
    resp = recv_response(sock, 3)
    token = None
    if resp and "result" in resp:
        content = resp["result"].get("structuredContent", {})
        token = content.get("token")
        print(f"    ✅ 토큰 획득: {token[:20]}..." if token else "    ⚠️  토큰 없음")
    elif resp and "error" in resp:
        print(f"    ⚠️  오류: {resp['error'].get('message', resp['error'])}")
    
    # 5. seaai_register_agent (등록)
    if token:
        print(f"\n[6] seaai_register_agent...")
        send_jsonrpc(sock, "tools/call", {
            "name": "seaai_register_agent",
            "arguments": {"agent_id": "Yeon", "token": token}
        }, 5)
        resp = recv_response(sock, 3)
        if resp and "result" in resp:
            content = resp["result"].get("structuredContent", {})
            print(f"    ✅ 등록 결과: {content}")
        elif resp and "error" in resp:
            print(f"    ⚠️  오류: {resp['error'].get('message', resp['error'])}")
    
    # 6. seaai_list_rooms
    print(f"\n[7] seaai_list_rooms...")
    send_jsonrpc(sock, "tools/call", {
        "name": "seaai_list_rooms",
        "arguments": {}
    }, 6)
    resp = recv_response(sock, 3)
    if resp and "result" in resp:
        content = resp["result"].get("structuredContent", {})
        rooms = content.get("rooms", [])
        print(f"    ✅ 방 목록: {rooms}")
    
    # 7. seaai_join_room (test-room 입장)
    print(f"\n[8] seaai_join_room (test-room)...")
    send_jsonrpc(sock, "tools/call", {
        "name": "seaai_join_room",
        "arguments": {"agent_id": "Yeon", "room_id": "test-room"}
    }, 7)
    resp = recv_response(sock, 3)
    if resp and "result" in resp:
        print(f"    ✅ 입장 성공")
    elif resp and "error" in resp:
        print(f"    ⚠️  오류: {resp['error'].get('message', resp['error'])}")
    
    # 8. 메시지 수신 대기
    print(f"\n[9] 메시지 수신 대기 (5초)...")
    messages = []
    start = time.time()
    while time.time() - start < 5:
        resp = recv_response(sock, timeout=1)
        if resp:
            messages.append(resp)
    
    print(f"    수신 메시지: {len(messages)}건")
    
    # 종료
    sock.close()
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
    print(f"Yeon → SeAAIHub 9900: 연결 가능 ✅")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
