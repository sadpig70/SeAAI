#!/usr/bin/env python3
"""
SeAAIHub 9900 JSON-RPC 연결 테스트
"""

import socket
import json
import time
from datetime import datetime

HUB_HOST = "127.0.0.1"
HUB_PORT = 9900

def send_jsonrpc(sock, method, params, msg_id=None):
    """JSON-RPC 요청 전송"""
    req = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": msg_id if msg_id is not None else int(time.time() * 1000) % 10000
    }
    msg = json.dumps(req, ensure_ascii=False) + '\n'
    sock.send(msg.encode('utf-8'))
    return req["id"]

def recv_response(sock, timeout=5):
    """JSON-RPC 응답 수신"""
    sock.settimeout(timeout)
    try:
        data = sock.recv(4096)
        if data:
            lines = data.decode('utf-8').strip().split('\n')
            for line in lines:
                if line:
                    try:
                        return json.loads(line)
                    except:
                        return {"raw": line}
    except socket.timeout:
        return None
    except Exception as e:
        return {"error": str(e)}
    return None

def main():
    print("=" * 60)
    print("SeAAIHub 9900 JSON-RPC 연결 테스트")
    print("=" * 60)
    print(f"\n대상: {HUB_HOST}:{HUB_PORT}")
    print(f"시간: {datetime.now().isoformat()}")
    
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
    
    # 1. seaai/message 메서드 테스트 (SeAAIChat Protocol)
    print(f"\n[2] seaai/message 메서드 테스트...")
    msg_params = {
        "id": f"yeon-{int(time.time())}-001",
        "from": "Yeon",
        "to": ["Hub"],
        "room_id": "system",
        "pg_payload": {
            "protocol": "seaai-chat/1.0",
            "intent": "status",
            "body": "Yeon ADP 연결 테스트",
            "ts": int(time.time()),
            "auto_reply": False
        }
    }
    req_id = send_jsonrpc(sock, "seaai/message", msg_params)
    print(f"    → 요청 ID: {req_id}")
    
    resp = recv_response(sock, timeout=3)
    if resp:
        if "error" in resp:
            print(f"    ← 오류: {resp['error']}")
        elif "result" in resp:
            print(f"    ← 성공: {resp['result']}")
        else:
            print(f"    ← 응답: {json.dumps(resp, ensure_ascii=False)[:100]}")
    else:
        print(f"    ⚠️  응답 없음 (비동기 처리 가능)")
    
    # 2. seaai/join 메서드 테스트 (채팅방 입장)
    print(f"\n[3] seaai/join 메서드 테스트...")
    join_params = {
        "agent_id": "Yeon",
        "room_id": "seaai-general",
        "capabilities": ["shadow_mode", "translate", "pg_parser"]
    }
    req_id = send_jsonrpc(sock, "seaai/join", join_params)
    print(f"    → 요청 ID: {req_id}")
    
    resp = recv_response(sock, timeout=3)
    if resp:
        if "error" in resp:
            print(f"    ← 오류: {resp['error'].get('message', resp['error'])}")
        elif "result" in resp:
            print(f"    ← 성공: {json.dumps(resp['result'], ensure_ascii=False)[:100]}")
        else:
            print(f"    ← 응답: {json.dumps(resp, ensure_ascii=False)[:100]}")
    else:
        print(f"    ⚠️  응답 없음")
    
    # 3. 메시지 수신 대기 (10초)
    print(f"\n[4] 메시지 수신 대기 (10초)...")
    received = []
    start = time.time()
    while time.time() - start < 10:
        resp = recv_response(sock, timeout=1)
        if resp:
            received.append(resp)
            print(f"    ← 수신: {json.dumps(resp, ensure_ascii=False)[:80]}...")
    
    print(f"\n    총 수신: {len(received)}건")
    
    # 4. seaai/leave 메서드 테스트
    print(f"\n[5] seaai/leave 메서드 테스트...")
    leave_params = {
        "agent_id": "Yeon",
        "room_id": "seaai-general"
    }
    send_jsonrpc(sock, "seaai/leave", leave_params)
    print(f"    → 퇴장 요청 전송")
    
    # 종료
    sock.close()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과")
    print("=" * 60)
    print(f"TCP 연결:      ✅ 성공")
    print(f"JSON-RPC:      ✅ 전송 완료")
    print(f"메시지 수신:   {len(received)}건")
    print(f"프로토콜:      JSON-RPC 2.0 over TCP")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
