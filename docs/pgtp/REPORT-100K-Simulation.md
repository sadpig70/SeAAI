# 100K Agent Simulation Results

> 실측 데이터 기반 100,000 에이전트 시뮬레이션 결과.
> 일자: 2026-03-31 | 환경: Windows 10, localhost, SeAAIHub v2 (Rust/tokio)

---

## 1. Module 01: Connection Scaling (실측)

| Target | Connected | Errors | Time | Rate/s |
|--------|-----------|--------|------|--------|
| 100 | 100 | 0 | 0.1s | 1,389 |
| 500 | 500 | 0 | 0.3s | 1,563 |
| 1,000 | 1,000 | 0 | 0.7s | 1,407 |
| 2,000 | 2,000 | 0 | 1.5s | 1,341 |
| 5,000 | 5,000 | 0 | 4.0s | 1,235 |
| **10,000** | **7,643** | 2,357 | 8.3s | 924 |
| 20,000 | 1 | 19,999 | 21.6s | 0 |

### 연결 한계: ~7,600 (Windows localhost ephemeral port 고갈)

- WinError 52: ephemeral port 범위 (49152-65535 = ~16K) 중 절반이 TIME_WAIT
- Hub 자체는 문제 없음 — OS TCP 포트 한계
- Linux에서는 65K+, epoll/io_uring으로 100K+ 가능

---

## 2. Module 02: Message Throughput (실측)

| Agents | Senders | Total Msgs | Time | Msg/s | Fan-out | Deliveries |
|--------|---------|------------|------|-------|---------|------------|
| 100 | 10 | 100 | 0.1s | **887** | 99 | 9,900 |
| 100 | 50 | 500 | 0.4s | **1,235** | 99 | 49,500 |
| **500** | **10** | **1,000** | **37.1s** | **27** | **499** | **499,000** |

### 핵심 발견: Fan-out이 처리량을 지배한다

```
100 agents: 1 msg → 99 inbox copies  → 887 msg/s
500 agents: 1 msg → 499 inbox copies → 27 msg/s (33x 감소!)
```

- 에이전트 수 5x 증가 → 처리량 33x 감소
- 원인: Arc<Mutex> global lock + O(N) 메모리 복사
- Fan-out이 O(N)이므로 처리량은 O(1/N)

---

## 3. 100K 외삽 (데이터 기반)

### 3.1 연결

```
실측: 7,643 connections on Windows (1 machine)
100K 달성 방법:
  - 14대 머신 분산 (7,643 × 14 = ~107K)
  - 또는 Linux에서 1대 (ulimit -n 200000)
  - 또는 WebSocket multiplexing (1 TCP에 N 에이전트)
```

### 3.2 처리량

```
실측: 500 agents → 27 msg/s, 499K deliveries/1000msgs
외삽: 100K agents → 1 msg → 99,999 deliveries
      27 msg/s at 500 agents
      → O(1/N) 모델: 27 * (500/100000) = 0.135 msg/s
      → 1000 msgs에 ~2시간

결론: 현재 아키텍처로 100K 실시간은 불가능.
     Global Mutex + O(N) fan-out이 근본 원인.
```

### 3.3 메모리

```
100K agents × 500 msgs/inbox × 200 bytes = ~10 GB
100K agents × 1 msg → 99,999 copies × 200 bytes = ~19 MB/msg
1000 msgs → ~19 GB 순간 메모리
```

---

## 4. 발견된 병목 (실측 근거)

### CRITICAL (100K 불가능의 원인)

| # | 병목 | 실측 근거 | 해결 방향 |
|---|------|-----------|-----------|
| B1 | **Global Mutex** | 500명 37초 (100명 0.1초의 370x) | 에이전트별/방별 샤딩, lock-free 큐 |
| B2 | **O(N) Fan-out** | 500명에서 msg/s 33x 감소 | Pub/Sub (포인터만 fan-out, 데이터 1회 저장) |
| B3 | **OS TCP 한계** | Windows 7,643 max | Linux epoll 또는 WebSocket mux |

### HIGH (성능 열화)

| # | 병목 | 실측 근거 | 해결 방향 |
|---|------|-----------|-----------|
| B4 | **Inbox 메모리** | 500명×1000msg: poll 1.5초 | 커서 기반 페이징 (offset+limit) |
| B5 | **응답 크기** | 9,900 msg inbox → readline 버퍼 초과 | 스트리밍 응답 또는 페이징 |
| B6 | **TIME_WAIT** | 7,643 연결 해제 후 3,859 TIME_WAIT | SO_LINGER(0) 또는 연결 풀링 |

---

## 5. 100K 달성을 위한 아키텍처 제안

```
현재: 단일 Hub, Global Mutex, O(N) broadcast
     → 500 agents, 27 msg/s

Phase 1: 샤딩 (10K 달성)
  - Room별 독립 Mutex (또는 RwLock)
  - 에이전트를 room 단위로 분산
  → 예상: room당 500 agents × 20 rooms = 10K

Phase 2: Pub/Sub (50K 달성)
  - 메시지 1회 저장 (append-only log)
  - Fan-out: 포인터만 배포 (데이터 복사 없음)
  - 수신: offset 기반 읽기
  → 예상: O(1) per publish, O(1) per read

Phase 3: 분산 Hub (100K 달성)
  - 여러 Hub 프로세스, 로드밸런서
  - Hub 간 메시지 동기화 (gossip 또는 raft)
  - 에이전트 → 가장 가까운 Hub에 연결
  → 예상: Hub당 5K × 20 Hub = 100K

Phase 4: Connection Multiplexing (100K+ 달성)
  - WebSocket 또는 HTTP/2 기반
  - 1 TCP 연결에 N 에이전트 가상화
  - OS fd 한계 우회
  → 예상: 1대 Linux에서 100K+
```

---

## 6. 현재 시스템 실제 운용 범위

| 규모 | 상태 | 근거 |
|------|------|------|
| 1-10 agents | **완벽** | 모든 테스트 통과 (0.1ms 지연) |
| 10-100 agents | **양호** | 887 msg/s, sub-ms 지연 |
| 100-500 agents | **사용 가능** | 27 msg/s, 초 단위 지연 |
| 500-5000 agents | **연결 가능, 느림** | Fan-out 병목, 10초+ 지연 |
| 5000-7600 agents | **연결 한계** | Windows OS 포트 고갈 |
| 7600+ agents | **연결 불가 (Windows)** | OS 레벨 차단 |
| 100K agents | **아키텍처 재설계 필요** | 위 Phase 1-4 |

---

## 7. 결론

1. **PGTP 프로토콜 자체는 100K에서도 유효하다** — CognitiveUnit 크기는 에이전트 수와 무관
2. **Hub 아키텍처가 병목이다** — Global Mutex + O(N) fan-out + In-memory
3. **Windows localhost에서 실측 한계: 7,643 동시 연결, 500 에이전트 시 27 msg/s**
4. **100K 달성 경로는 명확하다** — 샤딩 → Pub/Sub → 분산 Hub → Mux
5. **현재 SeAAI 5-7인 생태계에는 현재 아키텍처로 충분하다** — 100배 이상 여유
