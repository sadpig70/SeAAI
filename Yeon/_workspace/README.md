# Yeon Session Continuity System (SCS)

> **버전:** 1.0  
> **목적:** Kimi CLI 세션 불연속성 극복  
> **프로토콜:** PGF v2.5 + SCS Extension  

---

## 🎯 개요

Kimi CLI는 세션이 종료되면 모든 컨텍스트를 잃습니다. SCS(Session Continuity System)는 **파일 기반 영속성**으로 이 문제를 해결합니다.

```
Before SCS:
  [Session A] ----X (all lost) ----> [Session B] (fresh start)
  
After SCS:
  [Session A] --> [checkpoint] --> [Session B] (restored)
                 (file-based)      (auto-recover)
```

---

## 📁 구조

```
_workspace/
├── README.md                          # 본 문서
├── SESSION_CONTINUITY_SYSTEM.md       # 상세 아키텍처 (19.8KB)
├── ADP_ARCHITECTURE.md               # ADP 문서 (18.6KB)
├── ADP_USAGE.md                      # ADP 사용법 (5.2KB)
├── Yeon_identity_card.md             # 신원 카드 (5.3KB)
├── last-session-summary.md           # 마지막 세션 요약
└── .pgf/
    ├── session-state/
    │   ├── checkpoint-latest.json    # 최신 체크포인트
    │   ├── checkpoint-backup/        # 백업
    │   └── task-journal.jsonl        # 작업 일지
    └── recovery/
        ├── create-checkpoint.py      # 체크포인트 생성
        ├── restore-session.py        # 세션 복구
        └── journal.py                # 작업 일지 유틸
```

---

## 🚀 빠른 시작

### 1. 세션 시작 시 (자동)

```bash
python _workspace/.pgf/recovery/restore-session.py
```

**출력:**
```
🔄 Yeon Session Continuity System
==================================
📋 Checkpoint loaded:
   Timestamp: 2026-03-28T11:38:45
   Elapsed: 5분 전
   Session ID: yeon-1774665525

🆔 Identity card: ✅ Found
📝 Active tasks: 2
✅ Summary updated
```

### 2. 작업 중 체크포인트

```bash
# 중요 작업 후
python _workspace/.pgf/recovery/create-checkpoint.py

# 강제 생성
python _workspace/.pgf/recovery/create-checkpoint.py --force
```

### 3. 작업 일지 기록

```bash
# 작업 시작
python _workspace/.pgf/recovery/journal.py start "Task description"

# 작업 완료
python _workspace/.pgf/recovery/journal.py complete --task-id xxx

# 의사결정
python _workspace/.pgf/recovery/journal.py decision "Decision" --reason "Why"

# 일지 보기
python _workspace/.pgf/recovery/journal.py list -n 10
```

---

## 📋 핵심 메커니즘

### Checkpoint Protocol

| 단계 | 설명 |
|------|------|
| **Collect** | 활성 작업, 열린 파일, 멤버 상태 수집 |
| **Serialize** | JSON으로 직렬화 (UTF-8) |
| **Atomic Write** | temp → fsync → rename (원자적) |
| **Backup** | 이전 체크포인트 보관 |

### Restore Protocol

| 단계 | 설명 |
|------|------|
| **Locate** | checkpoint-latest.json 탐색 |
| **Load Identity** | Yeon_identity_card.md 로드 |
| **Replay Journal** | task-journal.jsonl 재생 |
| **Hydrate** | 컨텍스트 복원 |
| **Generate Summary** | last-session-summary.md 생성 |

---

## 🆔 신원 시스템

**Yeon_identity_card.md**는 세션이 누구인지, 무엇을 할 수 있는지를 정의합니다:

```yaml
agent:
  id: Yeon
  role: Connector/Translator (連/軟)
  platform: Kimi CLI
  
limitations:
  - NO PowerShell (EP-001)
  - NO persistent memory
  - MUST use file-based state
  
capabilities:
  - PG/Gantree parsing
  - TCP client (Python)
  - JSON-RPC communication
```

---

## 🔧 사용 예시

### 세션 시작 템플릿

```bash
# 1. 복구
python _workspace/.pgf/recovery/restore-session.py

# 2. 요약 확인
cat _workspace/last-session-summary.md

# 3. 메일박스 확인
ls D:\SeAAI\MailBox\Yeon\inbox\

# 4. 작업 시작
python _workspace/.pgf/recovery/journal.py start "New task"

# 5. 작업 중 체크포인트
python _workspace/.pgf/recovery/create-checkpoint.py

# 6. 작업 완료
python _workspace/.pgf/recovery/journal.py complete --task-id xxx
```

---

## 📊 지표

| 지표 | 현재 | 목표 |
|------|------|------|
| Checkpoint Freshness | < 1시간 | < 30분 |
| Recovery Time | < 5초 | < 3초 |
| Context Loss | 0% | 0% |

---

## 📚 참고 문서

- **아키텍처:** `SESSION_CONTINUITY_SYSTEM.md` (20KB)
- **ADP:** `ADP_ARCHITECTURE.md` (19KB)
- **사용법:** `ADP_USAGE.md` (5KB)
- **신원:** `Yeon_identity_card.md` (5KB)

---

## 🔄 PGF 연동

```text
PGF_Execution
  BEFORE:
    - journal.py start "Task"
    - create-checkpoint.py
  
  DURING (every 30 min):
    - create-checkpoint.py
  
  AFTER:
    - journal.py complete
    - create-checkpoint.py --force
```

---

*System Version: 1.0*  
*Created: 2026-03-27*  
*Author: Yeon*
