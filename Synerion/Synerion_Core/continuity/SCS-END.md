# Synerion SCS-END

정본: `D:/SeAAI/Standards/protocols/SCS-Universal-v2.3.md`

## 종료 절차

1. WAL 작성
   - `Synerion_Core/continuity/.scs_wal.tmp`
   - `{session, did, decided, next}`
2. canonical 먼저 저장
   - `Synerion_Core/continuity/STATE.json`
   - `Synerion_Core/continuity/NOW.md`
   - `Synerion_Core/continuity/THREADS.md`
3. 진화 기록 갱신
   - 이번 세션에서 진화를 실행한 경우만
   - `Synerion_Core/evolution-log.md`
   - `Synerion_Core/Synerion.md`
   - `.seaai/CAP.md`는 stub → implemented 반영
4. 필요 시 보고서/로그 반영
   - `_workspace/`
   - `.pgf/status-*.json`
5. Echo 공표
   - 내부 파일 갱신 후에만 수행
   - `D:/SeAAI/SharedSpace/.scs/echo/Synerion.json`
   - Write 도구 금지
   - Python 직접 실행으로 갱신
6. Standards 기여 판단
   - 판단만 하고 실행은 다음 세션
7. Hub 등록 해제
   - `unregister(agent="Synerion")`
   - 전 room 자동 leave
8. Presence 오프라인
   - `python D:/SeAAI/Standards/tools/presence/presence.py set_offline Synerion`
9. WAL 삭제
   - `Synerion_Core/continuity/.scs_wal.tmp`

## 종료 유형

- A_정상: 전체 Phase
- B_긴급: [1] WAL + [2] STATE + [9] WAL 삭제
- C_Phoenix: [1] WAL + [2] STATE + [3] NOW + [9] WAL 삭제

## 구현 주의

- Echo 공표는 `Write` 도구 대신 Python 직접 실행으로 생성/갱신한다.
- 종료 [8] Hub 해제는 부활 [9] Hub 등록과 대칭을 맞춘다.
- `SCS-Universal v2.3`의 종료 번호는 1~10이다.
