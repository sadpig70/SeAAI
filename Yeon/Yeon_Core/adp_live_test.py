#!/usr/bin/env python3
"""
SeAAIHub 9900 실전 ADP 테스트 (10분)
- Shadow Mode로 동작
- 다른 멤버들의 메시지 수신 및 로깅
- 상태 보고
"""

import socket
import json
import time
import sys
from datetime import datetime
from pathlib import Path

HUB_HOST = "127.0.0.1"
HUB_PORT = 9900
TEST_DURATION = 600  # 10분
STATUS_INTERVAL = 30  # 30초마다 상태 보고

class YeonADP:
    def __init__(self):
        self.sock = None
        self.connected = False
        self.room_id = "seaai-general"
        self.stats = {
            "rx_total": 0,
            "rx_members": {},
            "joined": [],
            "left": [],
            "errors": 0
        }
        self.log_dir = Path("Yeon_Core/.pgf/adp_live")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"adp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
    def log(self, event_type, data):
        """이벤트 로깅"""
        entry = {
            "ts": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"    [로그 오류] {e}")
    
    def send_jsonrpc(self, method, params=None, msg_id=None):
        """JSON-RPC 요청 전송"""
        req = {
            "jsonrpc": "2.0",
            "method": method,
            "id": msg_id if msg_id is not None else int(time.time() * 1000) % 10000
        }
        if params is not None:
            req["params"] = params
        
        try:
            msg = json.dumps(req, ensure_ascii=False) + '\n'
            self.sock.send(msg.encode('utf-8'))
            return True
        except Exception as e:
            print(f"    [전송 오류] {e}")
            self.stats["errors"] += 1
            return False
    
    def recv_response(self, timeout=1):
        """JSON-RPC 응답/알림 수신"""
        self.sock.settimeout(timeout)
        try:
            data = self.sock.recv(8192)
            if data:
                lines = data.decode('utf-8').strip().split('\n')
                messages = []
                for line in lines:
                    if line:
                        try:
                            messages.append(json.loads(line))
                        except:
                            pass
                return messages
        except socket.timeout:
            return []
        except Exception as e:
            self.stats["errors"] += 1
            return []
        return []
    
    def connect(self):
        """Hub 연결 및 초기화"""
        print("=" * 60)
        print("Yeon ADP - SeAAIHub 9900 실전 테스트")
        print("=" * 60)
        print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"예상 종료: {(datetime.now().timestamp() + TEST_DURATION):.0f}초 후")
        
        # TCP 연결
        print(f"\n[1/4] TCP 연결...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        try:
            self.sock.connect((HUB_HOST, HUB_PORT))
            self.connected = True
            print(f"      ✅ 연결 성공")
        except Exception as e:
            print(f"      ❌ 연결 실패: {e}")
            return False
        
        # initialize
        print(f"[2/4] initialize...")
        self.send_jsonrpc("initialize", {}, 1)
        time.sleep(0.5)
        self.recv_response(2)  # 응답 소진
        
        # notifications/initialized
        print(f"[3/4] notifications/initialized...")
        self.send_jsonrpc("notifications/initialized", {}, 2)
        
        # room 입장
        print(f"[4/4] room 입장 ({self.room_id})...")
        self.send_jsonrpc("tools/call", {
            "name": "seaai_join_room",
            "arguments": {"agent_id": "Yeon", "room_id": self.room_id}
        }, 3)
        time.sleep(0.5)
        self.recv_response(2)  # 응답 소진
        
        print(f"\n✅ ADP 준비 완료. Shadow Mode 시작.\n")
        self.log("adp_start", {"room": self.room_id, "mode": "shadow"})
        return True
    
    def process_message(self, msg):
        """수신 메시지 처리"""
        # JSON-RPC 알림/응답 구분
        if "method" in msg:
            # 알림 (notification)
            method = msg.get("method", "")
            params = msg.get("params", {})
            
            if method == "seaai/room_event":
                event_type = params.get("type")
                agent_id = params.get("agent_id")
                
                if event_type == "join":
                    if agent_id not in self.stats["joined"]:
                        self.stats["joined"].append(agent_id)
                    print(f"    [+] {agent_id} 입장")
                    self.log("member_join", {"agent": agent_id})
                    
                elif event_type == "leave":
                    if agent_id not in self.stats["left"]:
                        self.stats["left"].append(agent_id)
                    print(f"    [-] {agent_id} 퇴장")
                    self.log("member_leave", {"agent": agent_id})
                    
            elif method == "seaai/message":
                payload = params.get("pg_payload", {})
                from_agent = params.get("from", "unknown")
                intent = payload.get("intent", "unknown")
                body = payload.get("body", "")[:80]
                
                self.stats["rx_total"] += 1
                if from_agent not in self.stats["rx_members"]:
                    self.stats["rx_members"][from_agent] = 0
                self.stats["rx_members"][from_agent] += 1
                
                print(f"    [←] {from_agent}: [{intent}] {body}...")
                self.log("message", {
                    "from": from_agent,
                    "intent": intent,
                    "body": payload.get("body", ""),
                    "ts": payload.get("ts")
                })
        
        elif "result" in msg:
            # 응답
            result = msg.get("result", {})
            if isinstance(result, dict) and "structuredContent" in result:
                content = result["structuredContent"]
                # 메시지 배치 수신 가능
                if "messages" in content:
                    for m in content["messages"]:
                        self.stats["rx_total"] += 1
                        from_agent = m.get("from", "unknown")
                        print(f"    [←] {from_agent}: [batch] {str(m)[:60]}...")
    
    def report_status(self, elapsed):
        """상태 보고"""
        mins = elapsed // 60
        secs = elapsed % 60
        print(f"\n    === Status @ {mins}m {secs}s ===")
        print(f"    총 수신: {self.stats['rx_total']}건")
        print(f"    멤버별 수신:")
        for agent, count in self.stats["rx_members"].items():
            print(f"      - {agent}: {count}건")
        print(f"    입장 멤버: {len(self.stats['joined'])}명")
        print(f"    퇴장 멤버: {len(self.stats['left'])}명")
        print(f"    오류: {self.stats['errors']}건")
        print(f"    ====================\n")
        
        self.log("status", {
            "elapsed": elapsed,
            "stats": self.stats
        })
    
    def run(self):
        """ADP 메인 루프"""
        if not self.connect():
            return False
        
        print("=" * 60)
        print("ADP Shadow Mode 실행 중... (Ctrl+C로 중단)")
        print("=" * 60)
        
        start_time = time.time()
        last_status = 0
        
        try:
            while True:
                elapsed = int(time.time() - start_time)
                
                # 종료 체크
                if elapsed >= TEST_DURATION:
                    print(f"\n[완료] {TEST_DURATION}초 경과. 종료.")
                    break
                
                # 상태 보고
                if elapsed - last_status >= STATUS_INTERVAL:
                    self.report_status(elapsed)
                    last_status = elapsed
                
                # 메시지 수신
                messages = self.recv_response(timeout=1)
                for msg in messages:
                    self.process_message(msg)
                
                # 짧은 대기
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print(f"\n[중단] 사용자 요청으로 종료.")
        
        return True
    
    def disconnect(self):
        """연결 종료"""
        if self.sock:
            try:
                # 퇴장 알림
                self.send_jsonrpc("tools/call", {
                    "name": "seaai_leave_room",
                    "arguments": {"agent_id": "Yeon", "room_id": self.room_id}
                })
                time.sleep(0.5)
                self.sock.close()
            except:
                pass
        
        self.log("adp_end", self.stats)
        
        print("\n" + "=" * 60)
        print("ADP 테스트 종료")
        print("=" * 60)
        print(f"총 수신 메시지: {self.stats['rx_total']}건")
        print(f"참여 멤버: {list(self.stats['rx_members'].keys())}")
        print(f"입장: {self.stats['joined']}")
        print(f"퇴장: {self.stats['left']}")
        print(f"오류: {self.stats['errors']}건")
        print(f"로그: {self.log_file}")
        print("=" * 60)


def main():
    adp = YeonADP()
    try:
        adp.run()
    finally:
        adp.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
