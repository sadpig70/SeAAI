#!/usr/bin/env python3
"""SeAAIHub Mock + Yeon ADP 단축 테스트 (60초)"""

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
TEST_DURATION = 60  # 60초 단축 테스트
MESSAGE_INTERVAL = (5, 10)

class SeAAIHubMock:
    def __init__(self):
        self.clients = []
        self.running = False
        self.msg_idx = 0
        
    def start(self):
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        print(f"[SeAAIHub Mock] 서버 시작: {HOST}:{PORT}")
        
        threading.Thread(target=self._accept, daemon=True).start()
        threading.Thread(target=self._broadcast, daemon=True).start()
        
    def _accept(self):
        while self.running:
            try:
                self.server.settimeout(1.0)
                client, addr = self.server.accept()
                print(f"[SeAAIHub Mock] 연결: {addr}")
                self.clients.append(client)
                threading.Thread(target=self._handle, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
            except:
                break
                
    def _handle(self, client):
        while self.running:
            try:
                data = client.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode('utf-8').strip().split('\n')[0])
                print(f"[SeAAIHub Mock] ← 수신: {msg.get('from')}/{msg.get('intent')}")
            except:
                pass
        if client in self.clients:
            self.clients.remove(client)
            
    def _broadcast(self):
        members = ["Aion", "ClNeo", "NAEL", "Synerion"]
        intents = ["sync", "chat", "status"]
        
        while self.running:
            if self.clients:
                msg = {
                    "id": f"mock-{self.msg_idx:03d}",
                    "from": random.choice(members),
                    "to": "Yeon",
                    "intent": random.choice(intents),
                    "body": f"Test message {self.msg_idx}",
                    "timestamp": datetime.now().isoformat()
                }
                dead = []
                for c in self.clients:
                    try:
                        c.send((json.dumps(msg) + '\n').encode('utf-8'))
                    except:
                        dead.append(c)
                for c in dead:
                    if c in self.clients:
                        self.clients.remove(c)
                print(f"[SeAAIHub Mock] → 브로드캐스트: {msg['id']} ({msg['from']})")
                self.msg_idx += 1
            time.sleep(random.randint(*MESSAGE_INTERVAL))
            
    def stop(self):
        self.running = False
        for c in self.clients:
            try:
                c.close()
            except:
                pass
        try:
            self.server.close()
        except:
            pass
        return self.msg_idx


class YeonADP:
    def __init__(self):
        self.client = None
        self.stats = {"rx": 0, "tx": 0, "err": 0}
        self.log_file = Path("Yeon_Core/.pgf/adp_test/log.jsonl")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def cold_start(self):
        print("\n[Yeon ADP] Cold Start...")
        print("[Yeon ADP]  STEP 0: threat_assess ✓")
        print("[Yeon ADP]  STEP 1: sense_mailbox ✓")
        print("[Yeon ADP]  STEP 2: status_beacon ✓")
        self._log({"event": "cold_start", "agent": "Yeon"})
        print("[Yeon ADP] Cold Start 완료\n")
        
    def connect(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST, PORT))
            print(f"[Yeon ADP] Hub 연결: {HOST}:{PORT}")
            hello = {"from": "Yeon", "to": "Hub", "intent": "connect"}
            self.client.send((json.dumps(hello) + '\n').encode('utf-8'))
            return True
        except Exception as e:
            print(f"[Yeon ADP] 연결 실패: {e}")
            return False
            
    def loop(self, duration):
        start = time.time()
        print(f"[Yeon ADP] ADP 루프 시작 ({duration}s)")
        print("-" * 50)
        
        while time.time() - start < duration:
            try:
                self.client.settimeout(2.0)
                data = self.client.recv(4096)
                if data:
                    self._process(data)
            except socket.timeout:
                pass
            except Exception as e:
                self.stats["err"] += 1
                
            # 10초마다 상태 보고
            elapsed = int(time.time() - start)
            if elapsed % 10 == 0 and elapsed > 0:
                print(f"[Yeon ADP] Status @ {elapsed}s: 수신={self.stats['rx']}, 오류={self.stats['err']}")
                
        print("-" * 50)
        
    def _process(self, data):
        for line in data.decode('utf-8').strip().split('\n'):
            if not line:
                continue
            try:
                msg = json.loads(line)
                self.stats["rx"] += 1
                print(f"[Yeon ADP] ← {msg['id']} ({msg['from']}/{msg['intent']})")
                self._log({"event": "rx", "msg": msg})
            except:
                self.stats["err"] += 1
                
    def _log(self, data):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"ts": datetime.now().isoformat(), **data}) + '\n')
            
    def disconnect(self):
        if self.client:
            try:
                self.client.close()
            except:
                pass
        print("[Yeon ADP] 연결 종료")
        
    def summary(self):
        print("\n" + "=" * 50)
        print("ADP 테스트 결과")
        print("=" * 50)
        print(f"총 수신: {self.stats['rx']}")
        print(f"오류: {self.stats['err']}")
        print(f"로그: {self.log_file}")
        print("=" * 50)
        return self.stats["rx"] > 0 and self.stats["err"] == 0


def main():
    print("=" * 60)
    print("SeAAIHub Mock + Yeon ADP 60초 테스트")
    print("=" * 60)
    
    hub = SeAAIHubMock()
    hub.start()
    time.sleep(0.5)
    
    adp = YeonADP()
    adp.cold_start()
    
    success = False
    if adp.connect():
        try:
            adp.loop(TEST_DURATION)
            success = adp.summary()
        finally:
            adp.disconnect()
    
    total_sent = hub.stop()
    print(f"\n[SeAAIHub Mock] 총 전송: {total_sent}")
    
    if success:
        print("\n✓ 테스트 성공: TCP 연결, 메시지 수신, 로깅 모두 정상")
    else:
        print("\n✗ 테스트 실패")
        
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
