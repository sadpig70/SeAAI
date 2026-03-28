#!/usr/bin/env python3
"""
SeAAIHub 9900 연결 테스트
- TCP 연결 가능 여부 확인
- SeAAIChat Protocol v1.0 핸드셰이크
- Shadow Mode 진입 테스트
"""

import socket
import json
import time
from datetime import datetime
from pathlib import Path

HUB_HOST = "127.0.0.1"
HUB_PORT = 9900
CONNECT_TIMEOUT = 5  # 초

def test_connection():
    """기본 TCP 연결 테스트"""
    print("=" * 60)
    print("SeAAIHub 9900 연결 테스트")
    print("=" * 60)
    print(f"\n대상: {HUB_HOST}:{HUB_PORT}")
    print(f"시간: {datetime.now().isoformat()}")
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(CONNECT_TIMEOUT)
    
    try:
        print(f"\n[1/4] TCP 연결 시도...")
        client.connect((HUB_HOST, HUB_PORT))
        print(f"      ✅ 연결 성공!")
        
        # SeAAIChat Protocol v1.0 핸드셰이크
        print(f"\n[2/4] SeAAIChat Protocol 핸드셰이크...")
        hello_msg = {
            "protocol": "SeAAIChat-v1.0",
            "from": "Yeon",
            "intent": "connect",
            "capabilities": ["shadow_mode", "translate", "log"],
            "timestamp": datetime.now().isoformat()
        }
        
        client.send((json.dumps(hello_msg) + '\n').encode('utf-8'))
        print(f"      → 전송: {json.dumps(hello_msg, ensure_ascii=False)}")
        
        # 응답 대기
        print(f"\n[3/4] Hub 응답 대기 (5초)...")
        client.settimeout(5.0)
        try:
            data = client.recv(4096)
            if data:
                response = data.decode('utf-8').strip()
                print(f"      ← 수신: {response}")
                
                # JSON 파싱 시도
                try:
                    resp_json = json.loads(response.split('\n')[0])
                    print(f"      ✅ 프로토콜 응답 수신: {resp_json.get('intent', 'unknown')}")
                except:
                    print(f"      ⚠️  바이너리/비표준 응답 수신")
            else:
                print(f"      ⚠️  응답 없음 (연결 유지됨)")
        except socket.timeout:
            print(f"      ⚠️  응답 타임아웃 (연결 유지됨)")
        
        # Shadow Mode 진입 알림
        print(f"\n[4/4] Shadow Mode 진입 알림...")
        shadow_msg = {
            "protocol": "SeAAIChat-v1.0",
            "from": "Yeon",
            "intent": "status",
            "mode": "shadow",
            "status": "listening",
            "note": "Receive-only mode. No autonomous send.",
            "timestamp": datetime.now().isoformat()
        }
        client.send((json.dumps(shadow_msg) + '\n').encode('utf-8'))
        print(f"      → 전송: Shadow Mode 진입")
        
        # 10초간 메시지 수신 대기
        print(f"\n[대기] 10초간 메시지 수신 대기...")
        client.settimeout(10.0)
        messages = []
        start = time.time()
        
        while time.time() - start < 10:
            try:
                data = client.recv(4096)
                if data:
                    lines = data.decode('utf-8').strip().split('\n')
                    for line in lines:
                        if line:
                            messages.append(line)
                            print(f"      ← 수신: {line[:100]}...")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"      ⚠️  수신 오류: {e}")
                break
        
        print(f"\n      총 수신 메시지: {len(messages)}건")
        
        # 종료
        print(f"\n[완료] 연결 종료")
        client.close()
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("테스트 결과 요약")
        print("=" * 60)
        print(f"TCP 연결:        ✅ 성공")
        print(f"핸드셰이크:      ✅ 전송 완료")
        print(f"Shadow Mode:     ✅ 진입 완료")
        print(f"메시지 수신:     {len(messages)}건")
        print(f"총 테스트 시간:  약 15초")
        print("=" * 60)
        
        return True
        
    except ConnectionRefusedError:
        print(f"      ❌ 연결 거부 (Connection Refused)")
        return False
    except socket.timeout:
        print(f"      ❌ 연결 타임아웃")
        return False
    except Exception as e:
        print(f"      ❌ 연결 오류: {e}")
        return False
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
