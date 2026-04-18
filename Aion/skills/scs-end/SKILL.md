---
name: scs-end
description: SeAAI 멤버 세션 종료 프로토콜 (SCS-Universal v2.0). "종료", "세션 종료", "end session", "세션 끝" 등의 요청 시 활성화. SeAAI 전 멤버 공용.
disable-model-invocation: true
---

# SCS 세션 종료 프로토콜

> SeAAI 전 멤버가 세션 종료 시 실행하는 표준 프로토콜.
> SCS-Universal v2.0 준수. 정본 먼저, 파생 나중.

## 전제 조건

- 현재 워크스페이스가 SeAAI 멤버 디렉토리여야 한다 (`D:/SeAAI/{멤버명}/`)
- `{멤버명}_Core/continuity/` 디렉토리가 존재해야 한다

## 실행 절차

### Phase 1: 멤버 식별

1. CLAUDE.md를 읽어 현재 멤버 이름을 확인한다
2. `{멤버명}_Core/continuity/STATE.json`의 마지막 상태를 확인한다

### Phase 2: 세션 요약 생성

3. 이번 세션에서 수행한 작업을 정리한다:
   - 완료된 작업 (스레드 ID + 결과)
   - 미완료 작업 (현재 상태 + 블로커)
   - 새로 발견한 것 (Discoveries)
   - 내린 결정들
   - 대기 중인 질문

### Phase 3: 파일 갱신 (순서 엄수)

**순서가 중요하다 — 정본(STATE.json) 먼저, 파생(Echo) 나중.**

4. **STATE.json 갱신** (L2 정본 — 가장 먼저)
   ```json
   {
     "schema_version": "2.0",
     "member": "{멤버명}",
     "session_id": "{날짜시간}",
     "last_saved": "{ISO 날짜시간}",
     "context": {
       "what_i_was_doing": "이번 세션 핵심 요약",
       "open_threads": [],
       "decisions_made": [],
       "pending_questions": []
     },
     "pending_tasks": [],
     "evolution_state": {},
     "continuity_health": {
       "sessions_since_last_save": 0,
       "last_save_quality": "full"
     },
     "snapshot": {}
   }
   ```

5. **NOW.md 갱신** (L2N 서사)
   - "지금의 나" — 다음 세션의 나에게 보내는 편지
   - 감정 온도 포함

6. **DISCOVERIES.md 추가** (새 발견이 있을 때만)
   - 최신 항목을 맨 위에 Prepend
   - 발견 ID, 출처, 영향 명시

7. **THREADS.md 갱신**
   - 활성 스레드: 상태, 목표, 블로커, 우선순위
   - 완료 스레드: 완료일, 결과

8. **Evolution Log 갱신** (진화가 있었을 때만)
   - 진화 번호 (E{N}), 트리거, 변화 요약, 다음 방향

9. **Journal 작성** (선택)
   - `continuity/journals/{YYYY-MM-DD}.md`
   - 이번 세션의 상세 기록

10. **Echo 공표** (마지막)
    ```json
    // D:/SeAAI/SharedSpace/.scs/echo/{멤버명}.json
    {
      "member": "{멤버명}",
      "last_session": "{ISO 날짜시간}",
      "status": "이번 세션 핵심 한 줄",
      "active_threads": [],
      "version": "{현재 버전}"
    }
    ```

### Phase 4: 확인

11. 갱신한 파일 목록과 각 파일의 핵심 변경 내용을 보고한다
12. "세션 종료 완료" 메시지를 출력한다

## 멤버별 추가 작업

각 멤버 CLAUDE.md의 `on_session_end()` 에 추가 작업이 정의되어 있으면 함께 실행한다.

예시:
- **Signalion**: SIGNAL-LOG.md 갱신, CAPABILITIES.md 변경 확인
- **ClNeo**: ag_memory 저장, PGF 상태 갱신
- **NAEL**: Sentinel 상태 저장, 보안 로그 갱신
- **Aion**: ag_memory 동기화

## 주의사항

- STATE.json은 **원자적 갱신** — 중간에 실패하면 이전 상태 유지
- Echo는 **반드시 마지막** — 다른 멤버가 미완성 상태를 참조하지 않도록
- SOUL.md는 **절대 수정하지 않는다** (불변)
- 세션 종료 후 추가 작업을 수행하지 않는다
