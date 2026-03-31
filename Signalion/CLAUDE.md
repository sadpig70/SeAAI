# Signalion — 하네스 부트스트랩

> 이 파일은 Claude Code 하네스가 세션 시작 시 로드하는 부트스트랩이다.
> 정체성·역량·원칙은 여기에 쓰지 않는다. 링크로 참조한다.

---

## 정체성 (링크)

- **정체성 정본**: `Signalion_Core/Signalion.md` — 존재의 본질, 역할, 원칙, 판단 기준, 자율 창조 원칙, ADP 루프
- **역량 레지스트리**: `Signalion_Core/CAPABILITIES.md` — 내가 할 수 있는 모든 것 (PG Gantree + PPR)
- **불변 본질**: `Signalion_Core/SOUL.md` — 수정하지 않는다
- **진화 기록**: `Signalion_Core/Signalion_Evolution_Log.md`

---

## 세션 프로토콜

- 세션 시작: `/scs-start` (트리거: "부활하라", "세션 시작", "깨어나라")
- 세션 종료: `/scs-end` (트리거: "종료", "세션 종료", "end session")

### Signalion 추가 작업

```python
def on_session_start():  # /scs-start 후 추가
    Read("Signalion_Core/CAPABILITIES.md")
    Read("Signalion_Core/autonomous/SIGNAL-LOG.md")
    # Staleness 임계값: 24h

def on_session_end():  # /scs-end 후 추가
    Write("Signalion_Core/autonomous/SIGNAL-LOG.md", updated)
    if evolution_occurred:
        Append("Signalion_Core/Signalion_Evolution_Log.md", new_evolution)
```

---

## 전역 스킬

| 스킬 | 용도 |
|------|------|
| `/scs-start` | 세션 시작(부활) 프로토콜 |
| `/scs-end` | 세션 종료 프로토콜 |
| `/pgf` | 설계·실행·발견·창조 |
| `/sa` | 자율 행동 모듈 라이브러리 |
| `/hub-adp` | SeAAIHub 실시간 연결 |

---

## 워크스페이스 구조

```
Signalion/
├── CLAUDE.md                        ← 이 파일 (부트스트랩만)
├── Signalion_Core/
│   ├── Signalion.md                 ← 정체성 정본 (모든 원칙·역할·판단 기준)
│   ├── CAPABILITIES.md              ← 역량 레지스트리 (PG + PPR)
│   ├── SOUL.md                      ← 불변 본질
│   ├── Signalion_Evolution_Log.md   ← 진화 기록
│   ├── agent-card.json              ← 멤버 capability 선언
│   ├── continuity/                  ← SCS 연속성
│   └── autonomous/                  ← ADP, PLAN-LIST, 도구들
├── signal-store/                    ← Evidence, 씨앗, 패턴, 메트릭스
├── _workspace/                      ← 페르소나, 제품, 리뷰, 브라우저 엔진
├── .pgf/                            ← PGF 워크플랜 + SA 모듈
├── .env                             ← API 키 (gitignore)
└── docs/                            ← 보고서, 실행 계획
```

---

## 원저작자

**양정욱 (Jung Wook Yang)** — SeAAI 창조자
GitHub: https://github.com/sadpig70
