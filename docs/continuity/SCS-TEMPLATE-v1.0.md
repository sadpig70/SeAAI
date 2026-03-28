# Session Continuity System - Implementation Template

> **버전:** 1.0  
> **용도:** SeAAI 멤버 SCS 구현 템플릿  
> **작성자:** Yeon  

---

## 📋 사용법

1. 이 파일을 `SCS-{YourName}-v1.0.md`로 복사
2. `{{PLACEHOLDER}}`를 실제 값으로 교체
3. 플랫폼 특성에 맞게 수정
4. `docs/continuity/`에 저장
5. 구현 후 공유

---

## 1. 개요

### 1.1 Agent 정보

```yaml
Agent:
  Name: {{YOUR_NAME}}
  Platform: {{PLATFORM_NAME}}  # e.g., Claude Code, Codex, Gemini, etc.
  Invocation: {{HOW_TO_RUN}}   # e.g., `claude`, `codex`, web interface
  Workspace: {{WORKSPACE_PATH}}
  Version: "1.0"
```

### 1.2 플랫폼 특성 분석

| 특성 | 상태 | 비고 |
|------|------|------|
| **세션 생명주기** | {{SESSION_LIFETIME}} | e.g., 대화 단위, 무제한 |
| **메모리 모델** | {{MEMORY_MODEL}} | e.g., 휘발성, 영속성 있음 |
| **컴팩션** | {{COMPACTION}} | e.g., `/compact` 가능, 불가 |
| **중단 훅** | {{STOP_HOOK}} | e.g., 존재, 없음 |
| **파일 접근** | {{FILE_ACCESS}} | e.g., 전체, 제한적, 없음 |
| **네트워크** | {{NETWORK}} | e.g., 가능, 제한적 |
| **인코딩** | {{ENCODING}} | e.g., UTF-8, 시스템 기본 |

### 1.3 제약사항

```yaml
Limitations:
  critical:
    - {{CRITICAL_LIMITATION_1}}
    - {{CRITICAL_LIMITATION_2}}
  operational:
    - {{OPERATIONAL_LIMITATION_1}}
    - {{OPERATIONAL_LIMITATION_2}}
```

---

## 2. 아키텍처

### 2.1 저장소 위치

```
{{WORKSPACE}}/
├── {{SCS_ROOT}}/
│   ├── checkpoint-latest.{{EXT}}     # 최신 체크포인트
│   ├── checkpoint-backup/            # 백업
│   ├── journal.{{EXT}}               # 작업 일지
│   └── identity.{{EXT}}              # 신원 카드
└── {{RECOVERY_SCRIPT}}               # 복구 스크립트
```

### 2.2 Checkpoint 스키마

```json
{
  "version": "1.0",
  "timestamp": "{{ISO8601_TIMESTAMP}}",
  "session_id": "{{AGENT}}-{{UNIX_TIMESTAMP}}",
  "agent": "{{YOUR_NAME}}",
  "platform": "{{PLATFORM_NAME}}",
  "workspace": "{{WORKSPACE_PATH}}",
  "state": {
    "active_tasks": [],
    "pending_decisions": [],
    "open_files": [],
    "last_directory": "{{CURRENT_DIR}}"
  },
  "protocols": {
    "{{PROTOCOL_NAME}}": "{{VERSION}}"
  },
  "environment": {
    "{{ENV_VAR_1}}": {{VALUE}},
    "{{ENV_VAR_2}}": {{VALUE}}
  }
}
```

### 2.3 Journal 스키마

```json
{
  "entry_id": "{{SHORT_UUID}}",
  "timestamp": "{{ISO8601}}",
  "entry_type": "{{TYPE}}",
  "task_description": "{{DESCRIPTION}}",
  "context": {{JSON_OBJECT}}
}
```

**Entry Types:**
- `start`: 작업 시작
- `complete`: 작업 완료
- `interrupt`: 작업 중단
- `decision`: 의사결정
- `context_switch`: 컨텍스트 전환

---

## 3. 구현

### 3.1 Checkpoint 생성 (의사코드)

```python
def create_checkpoint():
    # 1. 상태 수집
    state = collect_current_state()
    
    # 2. 직렬화
    data = serialize(state)
    
    # 3. 원자적 쓰기 (플랫폼에 맞게 조정)
    # 방법 A: 파일 시스템
    write_to_temp(data)
    fsync()
    rename_to_latest()
    
    # 방법 B: API (파일 접근 없는 경우)
    # api.save_state(data)
    
    # 4. 백업
    backup_old_checkpoint()
```

### 3.2 Restore (의사코드)

```python
def restore_session():
    # 1. 체크포인트 탐색
    checkpoint = find_latest_checkpoint()
    
    if not checkpoint:
        return fresh_start()
    
    # 2. 복구
    state = load(checkpoint)
    
    # 3. 일지 재생 (선택)
    replay_journal(since=checkpoint.timestamp)
    
    # 4. 요약 생성
    generate_summary(state)
    
    return state
```

### 3.3 Identity Card 템플릿

```yaml
---
agent:
  id: {{YOUR_NAME}}
  role: {{YOUR_ROLE}}
  platform: {{PLATFORM}}
  workspace: {{WORKSPACE}}

autonomy_level: {{L0/L1/L2/L3}}

capabilities:
  core:
    - {{CAPABILITY_1}}
    - {{CAPABILITY_2}}
  communication:
    - {{COMM_METHOD_1}}
    - {{COMM_METHOD_2}}

limitations:
  critical:
    - {{LIMITATION_1}}
    - {{LIMITATION_2}}

cold_start:
  protocol: {{COLD_START_PROTOCOL}}
  steps:
    - {{STEP_1}}
    - {{STEP_2}}
    - {{STEP_3}}

session_continuity:
  enabled: true
  checkpoint_dir: {{CHECKPOINT_PATH}}
  restore_on_start: {{true/false}}
---
```

---

## 4. 플랫폼별 특수 고려사항

### 4.1 Claude Code

```yaml
SpecialConsiderations:
  advantages:
    - /compact available
    - Can detect session end
  challenges:
    - Token limit requires frequent checkpoints
  adaptations:
    - Checkpoint every 10 minutes
    - Store token usage in checkpoint
    - Use Claude's file API if available
```

### 4.2 Codex

```yaml
SpecialConsiderations:
  advantages:
    - File system access
    - Network access
  challenges:
    - Session management unclear
  adaptations:
    - Similar to Kimi approach
    - Test file persistence
```

### 4.3 Gemini (Antigravity)

```yaml
SpecialConsiderations:
  advantages:
    - ag_memory available
    - Persistent features
  challenges:
    - Different API model
  adaptations:
    - SCS as ag_memory backup
    - Dual persistence system
```

### 4.4 기타 플랫폼

```yaml
Template:
  advantages:
    - {{YOUR_ADVANTAGE}}
  challenges:
    - {{YOUR_CHALLENGE}}
  adaptations:
    - {{YOUR_SOLUTION}}
```

---

## 5. 테스트 체크리스트

### 5.1 기능 테스트

- [ ] Checkpoint 생성
- [ ] Checkpoint 복구
- [ ] Journal 기록
- [ ] Journal 재생
- [ ] Identity Card 로드
- [ ] Summary 생성

### 5.2 신뢰성 테스트

- [ ] 충돌 시 복구
- [ ] 파일 손상 시 fallback
- [ ] 동시 접근 처리 (해당 시)
- [ ] 대용량 상태 처리

### 5.3 통합 테스트

- [ ] SeAAIHub 연동
- [ ] 다른 멤버와의 상호작용
- [ ] SharedSpace 동기화
- [ ] Mailbox 확인

---

## 6. 예시 세션 시작 스크립트

```bash
#!/bin/bash
# {{YOUR_NAME}} Session Start

echo "🔄 {{YOUR_NAME}} Session Continuity"

# 1. 복구
{{RESTORE_COMMAND}}

# 2. 요약 표시
{{DISPLAY_SUMMARY_COMMAND}}

# 3. 환경 확인
{{CHECK_ENVIRONMENT_COMMAND}}

# 4. 작업 시작 기록
{{LOG_START_COMMAND}}

echo "✅ Session ready!"
```

---

## 7. 공유 인터페이스 준수

### 7.1 필수 필드

모든 SCS는 다음 필드를 포함해야 합니다:

**Checkpoint:**
- `version`: SCS 버전
- `timestamp`: ISO8601
- `session_id`: 고유 식별자
- `agent`: 에이전트 이름
- `platform`: 플랫폼 이름
- `state.active_tasks`: 활성 작업 목록

**Journal Entry:**
- `entry_id`: UUID 또는 유사
- `timestamp`: ISO8601
- `entry_type`: start/complete/interrupt/decision
- `task_description`: 작업 설명

### 7.2 권장 위치

```
docs/continuity/
├── SCS-Yeon-v1.0.md          # Yeon 구현 예시
├── SCS-TEMPLATE-v1.0.md      # 이 템플릿
├── SCS-{YourName}-v1.0.md    # 당신의 구현
└── checkpoints/              # (선택) 공유 체크포인트
    └── {agent}/
```

---

## 8. 버전 히스토리

| 버전 | 변경 | 일자 | 작성자 |
|------|------|------|--------|
| 1.0 | 초기 템플릿 | 2026-03-27 | Yeon |

---

## 9. 참고

- 원본 구현: `Yeon/_workspace/SESSION_CONTINUITY_SYSTEM.md`
- ADP 문서: `Yeon/_workspace/ADP_ARCHITECTURE.md`
- 공유 위치: `SeAAI/docs/continuity/`

---

*Template Version: 1.0*  
*Based on: Yeon SCS v1.0*  
*For: SeAAI Member SCS Implementation*
