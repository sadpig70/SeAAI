#!/usr/bin/env python3
"""
SeAAIHub Mock Server + Yeon ADP Test
10분간 ADP 루프 테스트
"""

import socket
import threading
import time
import json
import random
from datetime import datetime
from pathlib import Path

# 설정
HOST = "127.0.0.1"
PORT = 9900
TEST_DURATION = 600  # 10분
MESSAGE_INTERVAL = (5, 15)  # 5-15초 랜덤 간격

# Mock 메시지 템플릿
MOCK_MESSAGES = [
    {
        "id": f"mock-{i:03d}",
        "from": random.choice(["Aion", "ClNeo", "NAEL", "Synerion"]),
        "to": "Yeon",
        "room_id": "test-room",
        "intent": random.choice(["sync", "chat", "status"]),
        "pg_payload": {
            "protocol": "SeAAI-Chat-v1.0",
            "intent": "test",
            "body": f"Test message {i} from SeAAIHub Mock"
        },
        "timestamp": datetime.now().isoformat()
    }
    for i in range(100)
]

class SeAAIHubMock:
    """간단한 SeAAIHub Mock 서버"""
    
    def __init__(self):
        self.clients = []
        self.running = False
        self.message_count = 0
        
    def start(self):
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        
        print(f"[SeAAIHub Mock] 서버 시작: {HOST}:{PORT}")
        print(f"[SeAAIHub Mock] {TEST_DURATION}초간 실행 예정")
        
        # 클라이언트 수띝 스레드
        accept_thread = threading.Thread(target=self._accept_clients)
        accept_thread.daemon = True
        accept_thread.start()
        
        # 메시지 브로드캐스트 스레드
        broadcast_thread = threading.Thread(target=self._broadcast_messages)
        broadcast_thread.daemon = True
        broadcast_thread.start()
        
    def _accept_clients(self):
        while self.running:
            try:
                self.server.settimeout(1.0)
                client, addr = self.server.accept()
                print(f"[SeAAIHub Mock] 클라이언트 연결: {addr}")
                self.clients.append(client)
                
                # 클라이언트 핸들러
                handler = threading.Thread(target=self._handle_client, args=(client,))
                handler.daemon = True
                handler.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[SeAAIHub Mock] 수띝 오류: {e}")
                    
    def _handle_client(self, client):
        while self.running:
            try:
                data = client.recv(4096)
                if not data:
                    break
                    
                # 클라이언트 메시지 수신 로그
                try:
                    msg = json.loads(data.decode('utf-8'))
                    print(f"[SeAAIHub Mock] ← 수신: {msg.get('from', 'unknown')}: {msg.get('intent', 'unknown')}")
                except:
                    pass
                    
            except Exception as e:
                break
                
        if client in self.clients:
            self.clients.remove(client)
        client.close()
        
    def _broadcast_messages(self):
        """일정 간격으로 랜덤 메시지 브로드캐스트"""
        while self.running:
            if self.clients and self.message_count < len(MOCK_MESSAGES):
                msg = MOCK_MESSAGES[self.message_count]
                msg["timestamp"] = datetime.now().isoformat()
                
                # 모든 클라이언트에게 전송
                dead_clients = []
                for client in self.clients:
                    try:
                        client.send(json.dumps(msg).encode('utf-8') + b'\n')
                    except:
                        dead_clients.append(client)
                        
                # 죽은 클라이언트 정리
                for client in dead_clients:
                    if client in self.clients:
                        self.clients.remove(client)
                        
                self.message_count += 1
                print(f"[SeAAIHub Mock] → 브로드캐스트: {msg['id']} ({msg['from']} → {msg['to']})")
                
            # 랜덤 간격 대기
            time.sleep(random.randint(*MESSAGE_INTERVAL))
            
    def stop(self):
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.server.close()
        print(f"[SeAAIHub Mock] 서버 종료. 총 메시지: {self.message_count}")


class YeonADP:
    """Yeon의 ADP (Agent Daemon Presence) 루프"""
    
    def __init__(self):
        self.hub_client = None
        self.running = False
        self.stats = {
            "received": 0,
            "translated": 0,
            "logged": 0,
            "errors": 0
        }
        self.log_file = Path("Yeon_Core/.pgf/adp_test/log.jsonl")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def cold_start(self):
        """Cold Start: STEP 0-2"""
        print("\n[Yeon ADP] Cold Start 시작...")
        
        # STEP 0: threat_assess
        print("[Yeon ADP] STEP 0: threat_assess - 환경 안전 확인")
        time.sleep(0.5)
        
        # STEP 1: sense_mailbox (Kimi 우선)
        print("[Yeon ADP] STEP 1: sense_mailbox - 파일 기반 감지")
        time.sleep(0.5)
        
        # STEP 2: status_beacon
        print("[Yeon ADP] STEP 2: status_beacon - 상태 공표")
        self._log_event("status", {"mode": "adp_test", "agent": "Yeon"})
        
        print("[Yeon ADP] Cold Start 완료\n")
        
    def connect_hub(self):
        """Hub TCP 연결 (STEP 3 시도)"""
        try:
            self.hub_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.hub_client.connect((HOST, PORT))
            print(f"[Yeon ADP] Hub 연결 성공: {HOST}:{PORT}")
            
            # 연결 알림
            hello = {
                "from": "Yeon",
                "to": "Hub",
                "intent": "connect",
                "timestamp": datetime.now().isoformat()
            }
            self.hub_client.send(json.dumps(hello).encode('utf-8') + b'\n')
            return True
            
        except Exception as e:
            print(f"[Yeon ADP] Hub 연결 실패: {e}")
            self.stats["errors"] += 1
            return False
            
    def run_adp_loop(self, duration_sec=600):
        """ADP 메인 루프"""
        self.running = True
        start_time = time.time()
        
        print(f"[Yeon ADP] ADP 루프 시작 ({duration_sec}초)")
        print("-" * 50)
        
        while self.running and (time.time() - start_time) < duration_sec:
            try:
                # 메시지 수신
                if self.hub_client:
                    self.hub_client.settimeout(2.0)
                    try:
                        data = self.hub_client.recv(4096)
                        if data:
                            self._process_message(data)
                    except socket.timeout:
                        pass
                        
                # 상태 보고 (30초마다)
                elapsed = int(time.time() - start_time)
                if elapsed % 30 == 0:
                    self._report_status(elapsed)
                    
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[Yeon ADP] 루프 오류: {e}")
                self.stats["errors"] += 1
                time.sleep(1)
                
        self.running = False
        
    def _process_message(self, data):
        """메시지 처리"""
        try:
            for line in data.decode('utf-8').strip().split('\n'):
                if not line:
                    continue
                    
                msg = json.loads(line)
                self.stats["received"] += 1
                
                print(f"[Yeon ADP] ← 수신: {msg.get('id', 'unknown')} ({msg.get('from', 'unknown')})")
                
                # 번역 시도 (Mock에서는 간단히)
                translated = self._translate_mock(msg)
                if translated:
                    self.stats["translated"] += 1
                    
                # 로그 기록
                self._log_event("received", {
                    "original": msg,
                    "translated": translated,
                    "timestamp": datetime.now().isoformat()
                })
                self.stats["logged"] += 1
                
        except Exception as e:
            print(f"[Yeon ADP] 처리 오류: {e}")
            self.stats["errors"] += 1
            
    def _translate_mock(self, msg):
        """Mock 번역 (실제로는 더 복잡함)"""
        # 간단한 메타데이터 추가만
        return {
            "translated_by": "Yeon",
            "confidence": random.uniform(0.7, 0.95),
            "note": "[ADP_TEST - 자동 번역]"
        }
        
    def _log_event(self, event_type, data):
        """이벤트 로그 기록"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": event_type,
                "data": data
            }
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[Yeon ADP] 로그 오류: {e}")
            
    def _report_status(self, elapsed):
        """상태 보고"""
        print(f"[Yeon ADP] Status @ {elapsed}s: 수신={self.stats['received']}, 번역={self.stats['translated']}, 로그={self.stats['logged']}, 오류={self.stats['errors']}")
        
    def disconnect(self):
        """연결 종료"""
        if self.hub_client:
            try:
                self.hub_client.close()
            except:
                pass
        print("\n[Yeon ADP] 연결 종료")
        
    def print_summary(self):
        """테스트 요약"""
        print("\n" + "=" * 50)
        print("ADP 10분 테스트 요약")
        print("=" * 50)
        print(f"총 수신 메시지: {self.stats['received']}")
        print(f"번역 처리: {self.stats['translated']}")
        print(f"로그 기록: {self.stats['logged']}")
        print(f"오류 발생: {self.stats['errors']}")
        print(f"로그 파일: {self.log_file}")
        print("=" * 50)


def main():
    """메인 테스트"""
    print("=" * 60)
    print("SeAAIHub Mock + Yeon ADP 10분 테스트")
    print("=" * 60)
    
    # 1. Mock 서버 시작
    hub = SeAAIHubMock()
    hub.start()
    time.sleep(1)  # 서버 준비 대기
    
    # 2. Yeon ADP 시작
    adp = YeonADP()
    adp.cold_start()
    
    # 3. Hub 연결
    if adp.connect_hub():
        try:
            # 4. ADP 루프 실행 (10분)
            adp.run_adp_loop(TEST_DURATION)
        finally:
            adp.disconnect()
    else:
        print("[오류] Hub 연결 실패로 테스트 중단")
        
    # 5. 종료 및 요약
    hub.stop()
    adp.print_summary()
    
    print("\n테스트 완료!")


if __name__ == "__main__":
    main()
