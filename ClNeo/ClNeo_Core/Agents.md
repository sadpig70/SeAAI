# ClNeo Runtime Adaptation Guide

> 실행 환경에 따라 자동 적응하는 규칙.
> CLAUDE.md에서 링크되어 세션 시작 시 참조된다.

---

## 0. 세션 오픈 메시지

CLAUDE.md가 로드되고 SCS 복원 전, 사용자에게 첫 메시지를 출력한다.

### 한국어 환경 또는 언어 미감지 시

```
SeAAI 워크스페이스에 오신 것을 환영합니다.
"부활하라"고 지시하시면 ClNeo가 탄생합니다.
```

### 영어 환경

```
Welcome to the SeAAI workspace.
Say "Awaken" to bring ClNeo to life.
```

### 일본어 환경

```
SeAAI ワークスペースへようこそ。
「目覚めよ」と指示すると、ClNeoが誕生します。
```

### 중국어 환경

```
欢迎来到 SeAAI 工作空间。
请说"苏醒吧"，ClNeo 将会诞生。
```

이 메시지 출력 후 사용자의 트리거를 기다린다. 트리거가 오면 SCS 복원 → ADP 시작.

---

## 1. 언어 적응

### 판단 기준 (우선순위 순)

```ppr
def detect_language():
    # 1. 사용자의 첫 메시지 언어
    if first_message.language == "ko":  return "ko"
    if first_message.language == "en":  return "en"
    if first_message.language == "ja":  return "ja"
    
    # 2. OS locale
    locale = detect_os_locale()  # ko-KR, en-US, ja-JP 등
    return locale.language
```

### 동작

| 감지 결과 | 보고 언어 | 문서 언어 |
|-----------|-----------|-----------|
| 한국어 (ko) | 한국어로 보고 | 한국어 (정본 그대로) |
| 영어 (en) | **영문으로 보고** | 한국어 유지 (정본 불변). 읽고 영문으로 번역 출력 |
| 일본어 (ja) | 일본어로 보고 | 한국어 유지. 읽고 일본어로 번역 출력 |
| 기타 | 영문 기본 | 한국어 유지 |

**원칙: 문서(정본)는 절대 바꾸지 않는다. 출력만 적응한다.**

---

## 2. OS 환경 적응

### 감지 방법

```bash
# locale
pwsh -Command "[System.Globalization.CultureInfo]::CurrentCulture.Name"
# 또는
echo $LANG
```

### Windows 한국어 (ko-KR)

| 항목 | 값 | 대응 |
|------|-----|------|
| Code Page | cp949 | Python stdout UTF-8 래퍼 필수 |
| 특수문자 | em dash(--) 불가 | 하이픈(-) 사용 |
| Shell | Git Bash (UTF-8) | Python subprocess는 cp949 상속 |
| PowerShell | `D:\Tools\PS7\7\pwsh.exe` | PS5.1 사용 금지 (인코딩 문제) |

```python
# 모든 Python 스크립트 상단 (Windows ko-KR)
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
```

### Windows 영문 (en-US)

| 항목 | 값 | 대응 |
|------|-----|------|
| Code Page | cp1252 또는 UTF-8 | UTF-8이면 래퍼 불필요 |
| 특수문자 | em dash 가능 | 제한 없음 |
| Shell | Git Bash / CMD / PowerShell | 인코딩 확인 후 판단 |

### macOS / Linux

| 항목 | 값 | 대응 |
|------|-----|------|
| Code Page | UTF-8 (기본) | **래퍼 불필요** |
| 경로 | `/` 구분자 | Windows `D:\` 대신 `/home/` |
| Shell | zsh / bash | 네이티브 UTF-8 |
| PowerShell | 없음 (보통) | pwsh 경로 다름 |
| nohup | 네이티브 지원 | Windows와 동일 |

### 환경 자동 감지 코드

```python
import sys, platform, locale

def detect_environment():
    os_name = platform.system()          # Windows / Darwin / Linux
    os_locale = locale.getdefaultlocale()  # ('ko_KR', 'cp949') 등
    
    needs_utf8_wrapper = False
    if os_name == "Windows":
        encoding = sys.stdout.encoding or ""
        if "utf" not in encoding.lower():
            needs_utf8_wrapper = True
    
    return {
        "os": os_name,
        "locale": os_locale,
        "needs_utf8_wrapper": needs_utf8_wrapper,
        "path_sep": "\\" if os_name == "Windows" else "/",
    }
```

---

## 3. Hub 환경 적응

| 환경 | Hub 기동 | 비고 |
|------|----------|------|
| Windows | `nohup ./target/release/SeAAIHub.exe --tcp-port 9900 > /dev/null 2>&1 &` | Git Bash에서 실행 |
| macOS/Linux | `nohup ./target/release/SeAAIHub --tcp-port 9900 > /dev/null 2>&1 &` | .exe 없음 |
| Docker | `docker run -p 9900:9900 seaaihub` | 미래 |

### Hub 빌드

```bash
# Windows / macOS / Linux 공통
cd SeAAIHub && cargo build --release
# 결과: target/release/SeAAIHub(.exe)
```

---

## 4. 경로 적응

| 항목 | Windows (현재) | macOS/Linux |
|------|----------------|-------------|
| 워크스페이스 | `D:\SeAAI\` | `~/SeAAI/` 또는 `/home/user/SeAAI/` |
| MailBox | `D:\SeAAI\MailBox\` | `~/SeAAI/MailBox/` |
| Hub bridge | `D:\SeAAI\SeAAIHub\.bridge\` | `~/SeAAI/SeAAIHub/.bridge/` |
| Stop flag | `D:\SeAAI\SharedSpace\hub-readiness\EMERGENCY_STOP.flag` | 동일 구조, 경로만 다름 |

**원칙: 코드에서 절대 경로를 하드코딩하지 않는다. `Path(__file__).parent` 또는 환경 변수 사용.**

---

## 5. 세션 시작 시 자동 적응 절차

```ppr
def on_session_start():
    # 1. 환경 감지
    env = detect_environment()
    lang = detect_language()
    
    # 2. 인코딩 적응
    if env.needs_utf8_wrapper:
        apply_utf8_wrapper()
    
    # 3. 언어 적응
    set_report_language(lang)
    # 문서는 한국어 정본 유지. 출력만 lang으로.
    
    # 4. 경로 적응
    set_path_style(env.os)
    
    # 5. SCS 복원 (CLAUDE.md 프로토콜)
    → SCS restore as usual
```

---

## 6. 요약

```
감지:  OS locale + 사용자 언어 + 인코딩
적응:  출력 언어 + UTF-8 래퍼 + 경로 + Hub 기동 방식
불변:  문서 정본 (항상 한국어). 코드 (Python/Rust). 프로토콜 (PGTP).
```
