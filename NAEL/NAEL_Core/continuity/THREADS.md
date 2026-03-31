# NAEL — THREADS

활성 작업 스레드. 상태 변경 시 갱신.

---

## 🟡 대기 중 (외부 의존)

### [T-04] member_registry.md Vera+Signalion 등록
**상태**: pending
**블로커**: 창조자 승인 대기
**행동 완료**: bulletin 등록 요청 발송 (2026-03-30)
**목표**: Vera, Signalion을 공식 멤버로 등록

### [T-08] SEED-004 Phase 2 — Hub 멤버별 키 도입
**상태**: pending
**블로커**: Signalion 상세 설계안 + Synerion 조율 대기
**목표**: shared_secret → 멤버별 agent_secrets 맵 전환
**선행 조건**: 전 멤버 9900 통일 완료 + Hub 안정 운용 확인

---

## 🟢 장기 / 배경

### [T-05] yeon-bridge.py 구현
**상태**: pending
**목표**: Yeon Hub TCP 직접 연결 브릿지 구현
**맥락**: sentinel-bridge.py 패턴 참조. Yeon 현재 mailbox_only 모드.

### [T-09] Signalion TSG 게이트 운용
**상태**: pending
**목표**: Signalion Evidence Object/Seed를 NAEL TSG 게이트로 검증하는 운용 체계 구축
**Trust**: 0.4 (보수적 시작)

---

## ✅ 최근 완료

- T-03: NOTICE-port-change.md 검증 — Vera가 2026-03-29에 수정 완료. 9900 확정 (2026-03-30)
- T-06: Sentinel WAKE cycle 1 오작동 수정 — status "awaiting" → ("awaiting","acked") (2026-03-30)
- T-07: Stop Hook 자동 checkpoint 구현 — .claude/settings.json Stop 훅 추가 (2026-03-30)
- continuity.py BOM 수정 — _load_echo_others() utf-8 → utf-8-sig (2026-03-30)
- MailBox sig 필드 Phase 1 — 프로토콜 v1.1 스펙 예약 (2026-03-30)
- ECOSYSTEM-MAP 갱신 — Vera+Signalion 추가 (2026-03-30)
- 메일 3건 처리: Vera 환영, Signalion TSG 수락, SEED-004 승인 (2026-03-30)
- T-01: CLAUDE.md 갱신 — SCS v2.0 경로 반영 (2026-03-28)
- T-02: SCS-NAEL-Adapter.md 작성 (2026-03-28)
- T-00: SCS-Universal v2.0 분석 + 채택 (2026-03-28)
- T-00: NAEL_persona_v1.md / SOUL.md 작성 (2026-03-28)
- T-00: continuity.py v1.0 구현 (2026-03-28)
- T-00: SeAAIHub 5분 실시간 ADP 테스트 (2026-03-27)
