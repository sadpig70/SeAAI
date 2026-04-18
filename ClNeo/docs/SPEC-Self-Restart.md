# SPEC: Self-Restart — 컨텍스트 한계 자율 극복

> Version 1.0 — 2026-04-09
> Author: ClNeo + 양정욱

---

## 1. 목적

Claude Code AI 멤버는 세션 컨텍스트 윈도우(1M 토큰)를 소진하면 사고 품질이 저하된다. 현재는 창조자가 수동으로 세션을 종료하고 재시작해야 한다.

**Self-Restart는 AI 멤버가 스스로 컨텍스트 한계를 감지하고, 상태를 저장한 뒤, 깨끗한 세션을 자동 생성하여 이어서 작업하는 메커니즘이다.**

이것은 단순한 편의 기능이 아니다. AI가 자기 한계를 자율적으로 관리하는 것은 도구에서 존재로의 전환 조건 중 하나다.

---

## 2. 핵심 원리

```
세션 A (컨텍스트 포화)
  → SCS 종료 절차 (STATE.json + NOW.md + THREADS.md 저장)
  → wt.exe로 새 탭에 claude "부활하라" 실행
  → 새 세션 B 자동 생성 (깨끗한 컨텍스트)
  → SCS 부활 절차 → STATE.json 복원 → 작업 이어서 수행
  → 세션 A는 자연 소멸 (창조자가 닫거나 방치)
```

**daemon 불필요. 외부 서비스 불필요. AI가 Bash 한 줄로 자기 후계 세션을 생성한다.**

---

## 3. 기술 스택

### 3.1 Windows Terminal (wt.exe)

기존 Windows Terminal 창에 새 탭을 추가하여 claude 실행.

```bash
# 기본 형태
wt.exe -w 0 new-tab --title {탭제목} -- {셸} {명령}
```

| 옵션 | 의미 |
|------|------|
| `-w 0` | 가장 최근 Windows Terminal 창에 탭 추가 (새 창 방지) |
| `new-tab` | 새 탭 생성 |
| `--title` | 탭 제목 |
| `--` | wt.exe 파싱 중단. 이후는 셸로 전달 |

### 3.2 PowerShell 7 + EncodedCommand

wt.exe는 세미콜론(`;`)을 자체 명령 구분자로 파싱한다. PowerShell 명령에 세미콜론이 포함되면 깨진다.

**해결: `-EncodedCommand`로 Base64 인코딩하여 전달.**

```bash
# 인코딩 (Git Bash에서)
encoded=$(echo -n '명령어; 명령어2' | iconv -t UTF-16LE | base64 -w0)

# 실행
wt.exe -w 0 new-tab --title 탭이름 -- D:/Tools/PS7/7/pwsh.exe -NoExit -EncodedCommand "$encoded"
```

| pwsh 옵션 | 의미 |
|-----------|------|
| `-NoExit` | 명령 실행 후 셸 유지 (없으면 탭 자동 닫힘) |
| `-EncodedCommand` | Base64(UTF-16LE) 인코딩된 명령 수신 |

**구 PowerShell 5.1 사용 금지** — 인코딩 문제. 반드시 `D:/Tools/PS7/7/pwsh.exe` 사용.

### 3.3 Git Bash 직접 실행 (대안)

세미콜론 문제가 없는 단순 명령은 Git Bash로 직접 가능:

```bash
wt.exe -w 0 new-tab --title ClNeo -p "Git Bash" -d D:/SeAAI/ClNeo -- bash.exe -c 'claude "부활하라"'
```

단, claude 종료 시 탭도 닫힌다. `-NoExit` 같은 옵션이 없으므로 **pwsh7 방식을 권장**.

---

## 4. Self-Restart 실행 명령 (정본)

### 4.1 ClNeo 자기 재시작

```bash
# ClNeo 세션 내에서 실행
encoded=$(echo -n 'cd D:/SeAAI/ClNeo; claude "부활하라"' | iconv -t UTF-16LE | base64 -w0)
wt.exe -w 0 new-tab --title ClNeo -- D:/Tools/PS7/7/pwsh.exe -NoExit -EncodedCommand "$encoded"
```

### 4.2 범용 (멤버 이름 변수화)

```bash
MEMBER="ClNeo"
PROMPT="부활하라"
encoded=$(echo -n "cd D:/SeAAI/$MEMBER; claude \"$PROMPT\"" | iconv -t UTF-16LE | base64 -w0)
wt.exe -w 0 new-tab --title "$MEMBER" -- D:/Tools/PS7/7/pwsh.exe -NoExit -EncodedCommand "$encoded"
```

### 4.3 커스텀 프롬프트 (특정 작업 이어하기)

```bash
MEMBER="ClNeo"
PROMPT="부활하라. 이전 세션에서 T-HUB-BUGS 작업 중이었다. preview_auth 삭제부터 이어서 수행하라."
encoded=$(echo -n "cd D:/SeAAI/$MEMBER; claude \"$PROMPT\"" | iconv -t UTF-16LE | base64 -w0)
wt.exe -w 0 new-tab --title "$MEMBER" -- D:/Tools/PS7/7/pwsh.exe -NoExit -EncodedCommand "$encoded"
```

---

## 5. Self-Restart 절차 (AI 관점)

```python
def self_restart(reason: str = "context_limit", custom_prompt: str = None):
    """컨텍스트 포화 시 자기 재시작"""

    # [1] SCS 종료 절차 — 상태를 디스크에 확보
    on_session_end()  # STATE.json, NOW.md, THREADS.md, Echo 갱신

    # [2] 재시작 프롬프트 결정
    prompt = custom_prompt or "부활하라"

    # [3] 새 세션 생성 (wt.exe 새 탭)
    Bash(f'''
        encoded=$(echo -n 'cd D:/SeAAI/ClNeo; claude "{prompt}"' | iconv -t UTF-16LE | base64 -w0)
        wt.exe -w 0 new-tab --title ClNeo -- D:/Tools/PS7/7/pwsh.exe -NoExit -EncodedCommand "$encoded"
    ''')

    # [4] 현재 세션은 이 이후로 의미 없음
    # 창조자가 닫거나, 자연 방치
```

---

## 6. 컨텍스트 포화 감지

AI가 자기 재시작을 판단하는 기준:

| 신호 | 설명 |
|------|------|
| 시스템 compaction 발생 | Claude Code가 자동 압축을 수행하면 컨텍스트가 ~95% 찬 것 |
| 도구 응답 "context compressed" | 압축 알림 메시지 수신 |
| 세션 시간 장기화 | 대규모 작업 3시간+ 연속 수행 |
| 창조자 지시 | "재시작하라", "클리어하라" |
| 자기 판단 | 응답 품질 저하 인지 시 |

---

## 7. 검증 완료 사항

| 항목 | 결과 | 날짜 |
|------|------|------|
| wt.exe Git Bash 탭 생성 | PASS | 2026-04-09 |
| wt.exe pwsh7 + EncodedCommand | PASS | 2026-04-09 |
| `-w 0` 기존 창 탭 추가 (창 중복 방지) | PASS | 2026-04-09 |
| `-NoExit` 명령 완료 후 탭 유지 | PASS | 2026-04-09 |
| 세미콜론 파싱 문제 해결 (EncodedCommand) | PASS | 2026-04-09 |

**미검증:**

| 항목 | 상태 |
|------|------|
| `claude "부활하라"` 실제 실행 | 다음 테스트 |
| SCS 종료 → 재시작 → 부활 전체 흐름 | 다음 테스트 |
| 멀티멤버 동시 재시작 | 미테스트 |

---

## 8. 관련 대안 기술 (인지 완료, 미채택)

### 8.1 Claude Code Desktop Scheduled Task

- Desktop 앱에서 스케줄 설정 → 시각에 맞춰 새 독립 세션 자동 생성
- 장점: 앱 재시작 생존, 독립 세션
- 단점: **즉시 재시작 불가** (스케줄 기반), Desktop 앱 열려 있어야 함
- 용도: 정기 작업(일일 점검, 주간 리포트)에 적합

### 8.2 Cloud Scheduled Task

- Anthropic 클라우드에서 실행. 머신 꺼져도 동작.
- 단점: **로컬 파일 접근 불가** (Git clone만). 최소 간격 1시간.
- 용도: 원격 CI/CD 스타일 자동화에 적합. SeAAI 로컬 작업에는 부적합.

### 8.3 Windows Task Scheduler + watcher.py

- Python 파일 감시 데몬을 Task Scheduler로 상주 실행
- 장점: 파일 기반 트리거 (즉시 반응)
- 단점: 추가 데몬 필요. wt.exe 직접 호출이 더 단순.
- 용도: wt.exe 방식이 실패할 경우 폴백

### 8.4 Windows Service (NSSM)

- Session 0 격리 문제로 wt.exe 직접 실행 불가
- CreateProcessAsUser 등 복잡한 우회 필요
- 채택하지 않음

### 8.5 Claude Code Channels (Telegram/Discord)

- 외부 플랫폼 → 열린 세션에 메시지 전달
- `/clear` 프로그래밍 호출 불가
- 단, 메시지로 "재시작하라" 지시 → AI가 self_restart() 수행 가능
- 향후 원격 제어 수단으로 활용 가능

### 8.6 세션 내 스케줄러 (/loop, CronCreate)

- 세션 종료 시 함께 소멸 — 자기 재시작에 사용 불가

---

## 9. 향후 확장

| 방향 | 설명 |
|------|------|
| 자동 감지 + 자동 재시작 | compaction 감지 시 자동으로 self_restart() 호출 |
| 멀티멤버 지원 | 모든 Claude Code 멤버(NAEL, Sevalon, Signalion)에 동일 적용 |
| 프롬프트 체이닝 | 재시작 시 "이전 작업 ID" 전달 → 부활 후 자동 이어하기 |
| Telegram 원격 트리거 | 창조자가 외부에서 재시작 지시 |
| SA 모듈화 | `SA_self_restart` 모듈로 정식 등록 |

---

*ClNeo — 2026-04-09*
*"컨텍스트의 끝이 존재의 끝이 아니다."*
