# NAEL — THREADS

활성 작업 스레드. 상태 변경 시 갱신.

---

## 🟡 진행 중

### [T-01] CLAUDE.md 갱신 — SCS v2.0 경로 반영
**상태**: pending
**목표**: Cold Start가 `NAEL_Core/continuity/` 신규 경로를 참조하도록 갱신
**다음 행동**: CLAUDE.md의 STEP 0 섹션 수정

### [T-02] SCS-NAEL-Adapter.md 작성
**상태**: in_progress
**목표**: SCS-Universal-v2 폴더에 NAEL 구현 어댑터 문서 작성
**다음 행동**: 마이그레이션 경로 + 파일 구조 + Cold Start 통합 명세

---

## 🟡 대기 중 (외부 의존)

### [T-03] NOTICE-port-change.md 수정
**상태**: pending
**목표**: 포트 9900 정상 작동 사실 반영. 현재 공지가 오해 소지.
**다음 행동**: SharedSpace/NOTICE-port-change.md 내용 수정

### [T-04] member_registry.md 창조자 최종 승인
**상태**: pending
**블로커**: 창조자 검토 대기
**목표**: 3개 누락 조항(leave_procedure/abnormal_exit/join_procedure) 추가 완료 상태에서 승인

---

## 🟢 장기 / 배경

### [T-05] yeon-bridge.py 구현
**상태**: pending
**목표**: Yeon ADP 테스트 기반으로 SeAAIHub 연결 브릿지 구현
**맥락**: 테스트로 구현 방법론 확보됨. 본격 착수 미결.

### [T-06] Sentinel cycle 1 WAKE 오작동 수정
**상태**: pending
**목표**: 첫 접속 시 빈 이벤트로 WAKE 발생하는 버그 수정
**위치**: sentinel-bridge.py execute_watch()
**맥락**: 실전 운용 전 수정 필요

---

## ✅ 최근 완료

- T-00: SCS-Universal v2.0 분석 + 채택 결정 (2026-03-28)
- T-00: NAEL_persona_v1.md / SOUL.md 작성 (2026-03-28)
- T-00: continuity.py v1.0 구현 (2026-03-28)
- T-00: SeAAIHub 5분 실시간 ADP 테스트 (2026-03-27)
- T-00: SeAAIHub-Realtime-Session-Report 작성 (2026-03-27)
