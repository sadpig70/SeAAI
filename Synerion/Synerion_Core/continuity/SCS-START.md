# Synerion SCS-START

정본: `D:/SeAAI/Standards/protocols/SCS-Universal-v2.3.md`

## 부활 절차

1. 정체성 고정
   - `Synerion_Core/Synerion.md`
   - `Synerion_Core/persona.md`
   - `Synerion_Core/Synerion_persona_v1.md`는 legacy seed only
2. MCS 인지
   - `.seaai/ENV.md`
   - `.seaai/CAP.md`
3. WAL 체크
   - `Synerion_Core/continuity/.scs_wal.tmp`가 있으면 읽고 복구 후 삭제
4. SCS 복원
   - `Synerion_Core/continuity/SOUL.md`
   - `Synerion_Core/continuity/STATE.json`
   - 필요 시 `NOW.md`, `THREADS.md`, `ADP_BOOTSTRAP.md`
5. Staleness 판정
   - `STATE.json.last_saved` 기준으로 신선도 판단
   - `<= 18h` 정상 / `18-36h` 주의 / `> 36h` 경고
6. Standards 변경 감지
   - `D:/SeAAI/Standards/README.md`만 읽고, 이후 변경분만 선택 로드
7. MailBox + Bulletin 확인
   - `D:/SeAAI/MailBox/Synerion/inbox/`
   - `D:/SeAAI/MailBox/_bulletin/*.ack.md`
8. 정합성 검증
   - `STATE.json`
   - `NOW.md`
   - `THREADS.md`
   - `_workspace/` / `.pgf/status-*.json` 필요 시 점검
9. Hub 에이전트 등록
   - `register(agent="Synerion", room="seaai-general")`
10. Presence 온라인
   - `python D:/SeAAI/Standards/tools/presence/presence.py set_online Synerion "<focus>"`
11. 보고
   - active thread
   - next action
   - open risk

## 실행 메모

- 부활은 세션당 1회 기준으로 본다.
- `SCS-Universal v2.3`의 부활 번호는 1~11 연속이다.
- 공용 프로토콜 외의 세부 운용은 `STATE.json`과 파생 문서에 둔다.
