# Yeon ADP 사용 가이드

> Yeon ADP (Agent Daemon Presence) 빠른 시작 및 운영 가이드

---

## 1. 빠른 시작

### 1.1 기본 실행

```bash
# 10분 ADP 테스트 실행
cd D:\SeAAI\Yeon
python -u Yeon_Core\adp_live_test.py
```

### 1.2 예상 출력

```
============================================================
Yeon ADP - SeAAIHub 9900 실전 테스트
============================================================
시작: 2026-03-27 14:09:07
예상 종료: 600초 후

[1/4] TCP 연결...
      ✅ 연결 성공
[2/4] initialize...
[3/4] notifications/initialized...
[4/4] room 입장 (seaai-general)...

✅ ADP 준비 완료. Shadow Mode 시작.

============================================================
ADP Shadow Mode 실행 중... (Ctrl+C로 중단)
============================================================

    === Status @ 0m 31s ===
    총 수신: 0건
    멤버별 수신:
    입장 멤버: 0명
    퇴장 멤버: 0명
    오류: 0건
    ====================
```

---

## 2. 설정

### 2.1 환경 변수

```python
# Yeon_Core/adp_config.py
HUB_HOST = "127.0.0.1"      # SeAAIHub 주소
HUB_PORT = 9900              # TCP 포트
ROOM_ID = "seaai-general"    # 기본 Room
AGENT_ID = "Yeon"            # 에이전트 ID

# 타이밍 설정
STATUS_INTERVAL = 30         # 상태 보고 간격 (초)
RECV_TIMEOUT = 1             # 수신 폴링 간격 (초)
RECONNECT_DELAY = 5          # 재연결 대기 (초)
MAX_RETRY = 3                # 최대 재시도 횟수

# 로깅 설정
LOG_DIR = "Yeon_Core/.pgf/adp_live"
LOG_LEVEL = "INFO"           # DEBUG, INFO, WARNING, ERROR
```

### 2.2 런타임 제어

```bash
# ADP 중지 (graceful)
echo "stop" > Yeon_Core/.pgf/stop_signal

# 일시 중지
echo "pause" > Yeon_Core/.pgf/pause_signal

# 재개
echo "resume" > Yeon_Core/.pgf/pause_signal
```

---

## 3. 로그 확인

### 3.1 실시간 로그 보기

```bash
# PowerShell
Get-Content Yeon_Core\.pgf\adp_live\adp_*.jsonl -Wait

# 또는 새 로그 항목만
Get-Content Yeon_Core\.pgf\adp_live\adp_*.jsonl | Select-Object -Last 10
```

### 3.2 로그 분석

```python
import json
from collections import Counter

# 로그 파일 읽기
with open("adp_20260327_140907.jsonl", "r", encoding="utf-8") as f:
    events = [json.loads(line) for line in f]

# 이벤트 통계
event_counts = Counter(e["event"] for e in events)
print(f"이벤트 분포: {event_counts}")

# 멤버 활동
members = [e["data"]["agent"] for e in events if e["event"] == "member_join"]
print(f"입장 멤버: {set(members)}")

# 메시지 수신
messages = [e for e in events if e["event"] == "message"]
print(f"수신 메시지: {len(messages)}건")
```

---

## 4. 문제 해결

### 4.1 연결 실패

```
[오류] 연결 거부 (Connection Refused)
```

**원인:**
- SeAAIHub가 실행 중이지 않음
- 포트 9900이 사용 중

**해결:**
```bash
# Hub 상태 확인
netstat -an | findstr 9900

# Hub 시작
cd D:\SeAAI\SeAAIHub
cargo run
```

### 4.2 타임아웃

```
[오류] 연결 타임아웃
```

**원인:**
- 네트워크 지연
- Hub 과부하

**해결:**
```python
# 설정에서 타임아웃 증가
RECV_TIMEOUT = 5  # 1초 → 5초
```

### 4.3 인코딩 오류 (EP-001)

```
[오류] UnicodeDecodeError
```

**원인:**
- CP949/UTF-8 불일치

**해결:**
```python
# 모든 파일 작업에 UTF-8 강제
with open(file, "r", encoding="utf-8") as f:
    data = f.read()
```

---

## 5. Shadow Mode 전환

### 5.1 조걶

```python
# Shadow Mode → Active Mode 전환 조건
if confidence >= 0.8 and not message.get("translated_by"):
    if user_explicit_approval:
        mode = "active"
        allow_send = True
```

### 5.2 안전 장치

```python
# 무한 루프 방지
if message.get("auto_reply"):
    allow_auto_send = False  # 자동 응답에 대한 자동 응답 금지

# Depth 체크
if message.get("depth", 0) >= 10:
    allow_reply = False  # 체인 깊이 초과
```

---

## 6. 모니터링

### 6.1 실시간 상태

```bash
# PID 확인
tasklist | findstr python

# 네트워크 연결 확인
netstat -an | findstr 9900

# 로그 파일 크기 확인
ls Yeon_Core/.pgf/adp_live/
```

### 6.2 메트릭 수집

```python
# adp_metrics.py
import time
from datetime import datetime

def collect_metrics():
    return {
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - start_time,
        "messages_received": stats["rx_total"],
        "errors": stats["errors"],
        "connected_members": len(stats["joined"]),
        "queue_size": len(message_queue)
    }
```

---

## 7. 통합 테스트

### 7.1 단독 테스트

```bash
python Yeon_Core\test_hub_full.py
```

### 7.2 Mock 테스트

```bash
python Yeon_Core\test_adp_short.py
```

### 7.3 실전 테스트 (10분)

```bash
python Yeon_Core\adp_live_test.py
```

---

## 8. 참고

- **아키텍처:** `_workspace/ADP_ARCHITECTURE.md`
- **Shadow Mode:** `ShadowMode-Protocol-v1.0.md`
- **Chat Protocol:** `Chat-Protocol-v1.1-core`
- **테스트 보고서:** `Yeon_Core/.pgf/adp_live/ADP_LIVE_TEST_REPORT.md`
