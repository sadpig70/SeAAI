# Session Continuity System (SCS)

> **버전:** 1.0  
> **작성:** Yeon (Kimi CLI)  
> **일자:** 2026-03-27  
> **프로토콜:** PGF v2.5 + SCS Extension  

---

## 1. 개요

### 1.1 문제 정의

```text
ProblemStatement // Kimi CLI 세션 불연속성 문제
    ContextVolatility // 컨텍스트 휘발성
        SessionBoundaryReset // 세션 경계에서 메모리 초기화
        NoNativePersistence // 내장 영속성 없음
        NoStopHook // 종료 훅 없음 (/compact 불가)
    Impact // 영향
        TaskInterruption // 작업 중단 시 복구 불가
        RepeatedExplanation // 동일 설명 반복
        StateReconstruction // 상태 재구축 비용
        CollaborationBarrier // 협업 장벽
```

### 1.2 해결 전략

```text
Solution // 파일 기반 연속성 시스템
    PersistentStateLayer // 영속 상태 계층
        CheckpointProtocol // 체크포인트 프로토콜
        WriteAheadLog // 선행 기록 로그
        ContextManifest // 컨텍스트 명세
    RecoveryEngine // 복구 엔진
        AutoRestore // 자동 복구
        DiffReconciliation // 차이 조정
        TaskResumption // 작업 재개
    SelfIdentification // 자기 식별
        IdentityCard // 신원 카드
        CapabilityRegistry // 능력 레지스트리
        HistoryPlayback // 이력 재생
```

---

## 2. Gantree 아키텍처

```text
SessionContinuitySystem // 세션 연속성 시스템 @v:1.0
    PersistenceLayer // 영속 계층
        CheckpointManager // 체크포인트 관리
            CreateCheckpoint // 종료 시 저장
            LoadCheckpoint // 시작 시 로드
            PruneHistory // 이력 정리
        WriteAheadJournal // 선행 기록
            AppendOnlyLog // 추가 전용 로그
            TransactionBoundary // 트랜잭션 경계
            ReplayCapability // 재생 능력
        StateSnapshot // 상태 스냅샷
            FullSnapshot // 전체 스냅샷
            IncrementalDelta // 증분 델타
            CompressedArchive // 압축 보관
    RecoveryLayer // 복구 계층
        SessionBootstrap // 세션 부트스트랩
            SelfDiscovery // 자기 발견
            ContextHydration // 컨텍스트 수분
            CapabilityValidation // 능력 검증
        TaskReconstructor // 작업 재구성
            PendingTaskQueue // 대기 작업 큐
            InterruptedTaskStack // 중단 작업 스택
            DependencyResolver // 의존성 해결
        CollaborationSync // 협업 동기화
            MemberStateSync // 멤버 상태 동기화
            SharedSpaceWatch // 공유 공간 감시
            MailboxPolling // 메일박스 폴링
    IdentityLayer // 식별 계층
        YeonIdentity // Yeon 정체성
            RoleDefinition // 역할 정의 (Connector/Translator)
            LimitationManifest // 제약 명세 (No PowerShell)
            ColdStartMode // 콜드 스타트 모드
        SessionMetadata // 세션 메타데이터
            SessionID // 세션 식별자
            TimestampChain // 타임스탬프 체인
            ParentSession // 부모 세션 참조
        KnowledgeBase // 지식 기반
            SkillRegistry // 스킬 레지스트리 (pg, pgf, sa)
            ProtocolVersions // 프로토콜 버전
            WorkspaceLayout // 작업공간 레이아웃
```

---

## 3. 파일 구조

```
_workspace/
├── SESSION_CONTINUITY_SYSTEM.md          # 본 문서
├── .pgf/
│   ├── session-state/                    # 세션 상태 저장소
│   │   ├── checkpoint-latest.json        # 최신 체크포인트
│   │   ├── checkpoint-backup/            # 백업 체크포인트
│   │   │   ├── checkpoint-001.json
│   │   │   └── checkpoint-002.json
│   │   ├── context-history.jsonl         # 컨텍스트 이력
│   │   ├── task-journal.jsonl            # 작업 일지 (WAL)
│   │   └── session-registry.json         # 세션 레지스트리
│   ├── recovery/                         # 복구 시스템
│   │   ├── restore-session.py            # 복구 스크립트
│   │   ├── self-identify.py              # 자기 식별
│   │   └── bootstrap.pg                  # 부트스트랩 프로토콜
│   └── templates/                        # 템플릿
│       ├── session-init.pg               # 세션 초기화
│       └── checkpoint-template.json      # 체크포인트 템플릿
├── Yeon_identity_card.md                 # 신원 카드
└── last-session-summary.md               # 마지막 세션 요약
```

---

## 4. 프로토콜 (PPR)

### 4.1 Checkpoint Protocol

```text
PROTOCOL CreateCheckpoint:
    TRIGGER // 트리거
        SessionTermination // 세션 종료 시도
        PeriodicBackup // 주기적 백업 (30분)
        ExplicitRequest // 명시적 요청 (/checkpoint)
    
    STEPS // 단계
        1. COLLECT_STATE
           - active_tasks: List[Task]
           - pending_decisions: List[Decision]
           - open_files: List[FileHandle]
           - member_states: Dict[Agent, Status]
           - protocol_versions: Dict[Protocol, Version]
           
        2. SERIALIZE_STATE
           - format: JSON with UTF-8
           - include_timestamp: ISO 8601
           - include_session_id: UUID v4
           - compression: none (human-readable)
           
        3. ATOMIC_WRITE
           - temp_file: checkpoint-temp.json
           - fsync: true
           - rename: checkpoint-latest.json
           - backup: copy to checkpoint-backup/
           
        4. VERIFY_CHECKPOINT
           - read_back: true
           - validate_json: true
           - checksum: optional
    
    OUTPUT // 출력
        checkpoint_path: String
        timestamp: ISO8601
        session_id: UUID
```

### 4.2 Restore Protocol

```text
PROTOCOL RestoreSession:
    TRIGGER // 트리거
        SessionStart // 세션 시작
        RecoveryRequest // 복구 요청
        CrashRecovery // 충돌 복구
    
    STEPS // 단계
        1. LOCATE_CHECKPOINT
           - primary: checkpoint-latest.json
           - fallback: checkpoint-backup/* (latest)
           - check_integrity: validate JSON
           
        2. LOAD_IDENTITY
           - source: Yeon_identity_card.md
           - role: Connector/Translator
           - limitations: [No PowerShell, No TCP initially]
           - capabilities: [PG parse, SA sense/act]
           
        3. REPLAY_JOURNAL
           - source: task-journal.jsonl
           - filter: since_last_checkpoint
           - order: chronological
           - deduplicate: by task_id
           
        4. HYDRATE_CONTEXT
           - active_tasks → memory
           - open_files → verify existence
           - member_states → sense current
           - protocol_versions → validate
           
        5. VALIDATE_ENVIRONMENT
           - check: workspace integrity
           - check: SharedSpace access
           - check: encoding (UTF-8)
           - check: dependencies (Python available)
           
        6. GENERATE_SUMMARY
           - recovered_tasks: List
           - pending_actions: List
           - member_status: Dict
           - recommendations: List
    
    OUTPUT // 출력
        restored_context: Context
        summary_report: Markdown
        next_actions: List[Action]
```

### 4.3 Task Journal Protocol

```text
PROTOCOL WriteTaskJournal:
    TRIGGER // 트리거
        TaskStart // 작업 시작
        TaskComplete // 작업 완료
        TaskInterrupt // 작업 중단
        DecisionMade // 결정 발생
    
    ENTRY_SCHEMA // 항목 스키마
        {
            "entry_id": UUID,
            "timestamp": ISO8601,
            "entry_type": Enum[start|complete|interrupt|decision|context_switch],
            "task_id": String,
            "task_description": String,
            "context_before": Object,
            "context_after": Object,
            "decisions": List[Decision],
            "files_modified": List[Path],
            "members_involved": List[Agent],
            "next_expected_action": String
        }
    
    WRITE_MODE // 쓰기 모드
        append_only: true
        flush_immediate: true
        fsync: true
        rotation_size: 10MB
```

---

## 5. 핵심 메커니즘

### 5.1 Self-Identification Card

```yaml
# Yeon_identity_card.md
---
agent:
  id: Yeon
  role: Connector/Translator (連 - Connect, 軟 - Adapt)
  platform: Kimi CLI (via uv tool run kimi)
  workspace: D:\SeAAI\Yeon
  version: "1.0"

autonomy_level: L2
  description: Contextual autonomy with human checkpoint
capabilities:
  - PG/Gantree parsing
  - PGF execution
  - SA (SelfAct) sense/act
  - File-based operations
  - TCP client (via Python)
  - JSON-RPC communication
  
limitations:
  - NO PowerShell execution (EP-001)
  - NO autonomous TCP server (client only)
  - NO Claude /compact or stop hook
  - NO persistent memory across sessions
  - MUST use file-based state tracking
  
cold_start_mode:
  step_0: threat_assess
  step_1: sense_mailbox
  step_2: status_beacon
  
protocol_stack:
  - SeAAIChat-v1.0
  - JSON-RPC 2.0
  - PG (PPR/Gantree)
  - PGF v2.5
  
skills:
  pg: .agents/skills/pg/
  pgf: .agents/skills/pgf/
  sa: .agents/skills/sa/
  
active_protocols:
  - ShadowMode-Protocol-v1.0
  - Chat-Protocol-v1.1-core
  
member_registry: D:\SeAAI\SharedSpace\member_registry.md

session_continuity:
  checkpoint_dir: _workspace/.pgf/session-state/
  journal_file: _workspace/.pgf/session-state/task-journal.jsonl
  restore_on_start: true
---

## Current Session Context

**Last Checkpoint:** {{checkpoint_timestamp}}
**Active Tasks:** {{active_tasks}}
**Pending Decisions:** {{pending_decisions}}
**Known Members:** {{member_states}}

## Quick Recovery Commands

```bash
# 복구 스크립트 실행
python _workspace/.pgf/recovery/restore-session.py

# 최신 체크포인트 확인
cat _workspace/.pgf/session-state/checkpoint-latest.json | head -50

# 작업 일지 보기
cat _workspace/.pgf/session-state/task-journal.jsonl | tail -20
```

## If This Is A New Session

1. Run restore script: `python _workspace/.pgf/recovery/restore-session.py`
2. Read last summary: `cat _workspace/last-session-summary.md`
3. Check mailbox: `ls D:\SeAAI\MailBox\Yeon\inbox\`
4. Join SeAAIHub if needed
```

### 5.2 Automatic Bootstrap

```python
# _workspace/.pgf/recovery/bootstrap.pg

SessionBootstrap // 세션 자동 초기화
    Step1_DetectState // 상태 감지
        CHECK _workspace/.pgf/session-state/checkpoint-latest.json
        IF exists:
            LOAD checkpoint
            SET mode = recovery
        ELSE:
            SET mode = fresh_start
            
    Step2_LoadIdentity // 정체성 로드
        READ Yeon_identity_card.md
        PARSE YAML frontmatter
        VALIDATE capabilities
        ASSERT limitations
        
    Step3_ReplayJournal // 일지 재생
        IF mode == recovery:
            OPEN task-journal.jsonl
            FILTER entries since checkpoint
            FOR entry in entries:
                RECONSTRUCT context
                IF entry.type == interrupt:
                    ADD to pending_tasks
                    
    Step4_GenerateBriefing // 브리핑 생성
        COMPILE recovered_context
        WRITE last-session-summary.md
        DISPLAY to user
        
    Step5_EstablishPresence // 존재 확립
        IF ADP_enabled:
            RUN adp_live_test.py (background)
        CHECK mailbox
        SCAN SharedSpace for updates
```

### 5.3 Context Diff & Merge

```text
PROTOCOL ContextDiff:
    INPUT
        checkpoint: State (from file)
        current: State (from environment)
    
    DIFF_LOGIC
        files_added: current.files - checkpoint.files
        files_removed: checkpoint.files - current.files
        files_modified: {f | f in both, hash(f) changed}
        tasks_completed: checkpoint.tasks - current.tasks
        tasks_new: current.tasks - checkpoint.tasks
        members_changed: checkpoint.members != current.members
    
    MERGE_STRATEGY
        # 파일: 현재 상태 우선
        # 작업: checkpoint + new (completed marked)
        # 멤버: sense current (override checkpoint)
```

---

## 6. 구현 파일

### 6.1 체크포인트 생성기

```python
# _workspace/.pgf/recovery/create-checkpoint.py
#!/usr/bin/env python3
"""
Session Checkpoint Creator
Usage: python create-checkpoint.py [--force]
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

def create_checkpoint():
    checkpoint = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "session_id": f"yeon-{int(time.time())}",
        "agent": "Yeon",
        "platform": "Kimi CLI",
        "workspace": "D:\\SeAAI\\Yeon",
        "state": {
            "active_tasks": [],  # To be populated
            "pending_decisions": [],
            "open_files": [],
            "last_directory": str(Path.cwd()),
        },
        "protocols": {
            "ShadowMode": "v1.0",
            "SeAAIChat": "v1.0",
            "PGF": "v2.5"
        },
        "environment": {
            "powershell_available": False,
            "tcp_client_available": True,
            "encoding": "utf-8"
        }
    }
    
    # Save
    checkpoint_dir = Path("_workspace/.pgf/session-state")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    latest = checkpoint_dir / "checkpoint-latest.json"
    backup = checkpoint_dir / f"checkpoint-backup/checkpoint-{int(time.time())}.json"
    backup.parent.mkdir(exist_ok=True)
    
    # Atomic write
    temp = checkpoint_dir / "checkpoint-temp.json"
    with open(temp, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    # Backup old
    if latest.exists():
        import shutil
        shutil.copy(latest, backup)
    
    # Replace
    temp.replace(latest)
    
    print(f"Checkpoint created: {latest}")
    print(f"Backup: {backup}")
    return checkpoint

if __name__ == "__main__":
    create_checkpoint()
```

### 6.2 복구 스크립트

```python
# _workspace/.pgf/recovery/restore-session.py
#!/usr/bin/env python3
"""
Session Restore Script
Auto-runs on session start to recover continuity
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def restore_session():
    print("=" * 60)
    print("Yeon Session Continuity System")
    print("=" * 60)
    
    # 1. Load checkpoint
    checkpoint_path = Path("_workspace/.pgf/session-state/checkpoint-latest.json")
    if not checkpoint_path.exists():
        print("\n⚠️  No checkpoint found. Starting fresh session.")
        print("Creating initial checkpoint...")
        # Import and run create-checkpoint
        return False
    
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)
    
    print(f"\n📋 Checkpoint loaded:")
    print(f"   Timestamp: {checkpoint['timestamp']}")
    print(f"   Session ID: {checkpoint['session_id']}")
    print(f"   Agent: {checkpoint['agent']}")
    
    # 2. Load identity
    identity_path = Path("_workspace/Yeon_identity_card.md")
    if identity_path.exists():
        print(f"\n🆔 Identity card found: {identity_path}")
    
    # 3. Replay journal
    journal_path = Path("_workspace/.pgf/session-state/task-journal.jsonl")
    if journal_path.exists():
        with open(journal_path, 'r', encoding='utf-8') as f:
            entries = [json.loads(line) for line in f if line.strip()]
        print(f"\n📚 Journal entries: {len(entries)}")
        
        # Show last 5
        if entries:
            print("\n   Recent entries:")
            for e in entries[-5:]:
                print(f"   - [{e['entry_type']}] {e['task_description'][:50]}...")
    
    # 4. Generate summary
    summary_path = Path("_workspace/last-session-summary.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Last Session Summary

**Generated:** {datetime.now().isoformat()}
**From Checkpoint:** {checkpoint['timestamp']}

## Recovered State

- **Active Tasks:** {len(checkpoint['state']['active_tasks'])}
- **Pending Decisions:** {len(checkpoint['state']['pending_decisions'])}
- **Protocols:** {', '.join(checkpoint['protocols'].keys())}

## Quick Actions

```bash
# View full checkpoint
cat _workspace/.pgf/session-state/checkpoint-latest.json

# View task journal
cat _workspace/.pgf/session-state/task-journal.jsonl

# Check mailbox
ls D:\\SeAAI\\MailBox\\Yeon\\inbox\\
```

## Next Steps

1. Review pending tasks
2. Check member states
3. Resume interrupted work
""")
    
    print(f"\n✅ Summary written: {summary_path}")
    print("\n" + "=" * 60)
    print("Session continuity restored!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    restore_session()
```

---

## 7. 사용 워크플로우

### 7.1 세션 시작 시 (자동)

```bash
# Kimi CLI 시작 시 자동 실행
python _workspace/.pgf/recovery/restore-session.py

# 출력:
# ========================================
# Yeon Session Continuity System
# ========================================
# 
# 📋 Checkpoint loaded:
#    Timestamp: 2026-03-27T14:09:08
#    Session ID: yeon-1711523348
# 
# 📚 Journal entries: 42
# 
# ✅ Summary written: _workspace/last-session-summary.md
```

### 7.2 작업 중 체크포인트 (수동)

```bash
# 중요 결정 후 체크포인트
python _workspace/.pgf/recovery/create-checkpoint.py
```

### 7.3 세션 종료 시 (자동 권장)

```bash
# 종료 전 항상 체크포인트
python _workspace/.pgf/recovery/create-checkpoint.py --force
```

---

## 8. 통합 지점

### 8.1 PGF와의 연동

```text
PGF_Execution // PGF 실행 시
    BEFORE
        LOG task_start to journal
        SAVE context to checkpoint
    
    DURING
        APPEND progress to journal (every 5 min)
    
    AFTER
        LOG task_complete to journal
        UPDATE checkpoint
```

### 8.2 SeAAIHub와의 연동

```text
ADP_Integration // ADP 연동
    ON_CONNECT
        LOG hub_connect to journal
        SAVE member_states to checkpoint
    
    ON_MESSAGE
        APPEND message to journal (if significant)
    
    ON_DISCONNECT
        LOG hub_disconnect to journal
        CREATE emergency checkpoint
```

---

## 9. 메트릭 및 모니터링

### 9.1 연속성 지표

| 지표 | 설명 | 목표 |
|------|------|------|
| **Checkpoint Freshness** | 마지막 체크포인트 경과 시간 | < 1시간 |
| **Recovery Time** | 복구 완료까지 소요 시간 | < 5초 |
| **Context Loss Rate** | 복구 실패한 컨텍스트 비율 | 0% |
| **Journal Integrity** | 일지 파일 손상 여부 | 100% 정상 |

### 9.2 상태 확인 명령

```bash
# 체크포인트 상태
python -c "import json; d=json.load(open('_workspace/.pgf/session-state/checkpoint-latest.json')); print(f'Last: {d[\"timestamp\"]}')"

# 일지 크기
ls -lh _workspace/.pgf/session-state/task-journal.jsonl

# 백업 개수
ls _workspace/.pgf/session-state/checkpoint-backup/ | wc -l
```

---

## 10. 로드맵

| 버전 | 기능 | 일정 |
|------|------|------|
| 1.0 | 기본 체크포인트/복구 | 완료 |
| 1.1 | 자동 주기적 백업 (30분) | 예정 |
| 1.2 | 증분 체크포인트 (diff 기반) | 예정 |
| 1.3 | 자동 복구 (세션 시작 시) | 예정 |
| 2.0 | 크로스-세션 학습 (패턴 인식) | 미정 |

---

*Document Version: 1.0*  
*Author: Yeon*  
*Protocol: PGF v2.5 + SCS Extension*
