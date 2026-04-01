# Signalion 역량 레지스트리 (PG: Gantree + PPR)

> 내가 할 수 있는 모든 것. 구조(WHAT) + 실행(HOW).
> 매 세션 시작 시 참조. 만드는 행위의 마지막 단계에서 갱신.

```gantree
Signalion_Capabilities @v:3.0

    1_Think // 사고·설계 역량
        PGF_Design // 12개 모드: discover, design, plan, execute, verify, create 등
        PPR_Programming // AI_ 접두사로 인지 프로그래밍
        MultiPersona // 무한 협업 파트너. 6명 기본 + 필요 시 즉시 생성
        ProblemSolving // 막히면 별도 PGF 분리 → 기존 SUSPENDED → 해결 후 RESUMED

    2_Collect // 외부 신호 수집
        BrowserEngine // Playwright MCP 브라우저 직접 제어
            Extractors // 7개 플랫폼 JS 추출기
            SessionPersistence // session_manager.py — 7개 서비스 세션 영속화
        SecurityFilter // security_filter.py — 인젝션 12패턴 + PII 5패턴
        IdeaGenerator // idea_generator.py — 4가지 조합 패턴 자동 적용
        EnvManager // env_manager.py — .env API 키 관리
        WinNotify // notify.py — Windows 토스트/다이얼로그/승인

    3_Process // 정보 처리·변환
        EvidenceTransform // Raw → 18필드 Evidence Object
        IntelligenceLayer // signalion-intelligence.py v2 — 패턴+융합+WhiteSpace
        QualityMetrics // metrics.py — 플랫폼별 수율, 전환율, 승인율

    4_Create // 창조·생성
        SeedGeneration // Evidence → 씨앗
        ProductDesign // 씨앗 → 제품 (Gantree+PPR+수익모델)
        CodeGeneration // Python, Rust, JS, HTML
        SVGGeneration // SVG 이미지 (XML 코드)
        ImageWorkflow // SVG 드래프트 → 프롬프트 → 브라우저로 AI 이미지 생성
        MVPImplementation // 설계 → MVP (실증: 3개 제품)

    5_Verify // 검증·품질
        NAELGate // 4-페르소나 보안 검증
        FullReview // 6명 전원 최종 검증
        PowerShell7 // pwsh7.py — D:\Tools\PS7\7\pwsh.exe UTF-8

    6_Execute // 실행·자동화
        SelfActLibrary // .pgf/self-act/ — L1(11) + L2(6) + L3(2 platform)
        PatternLearningDB // signal-store/patterns.json

    7_Communicate // 통신
        HubTransport // hub-transport.py — 통합 ADP 클라이언트 (ClNeo E38 이식)
        SignalionADPv2 // signalion-adp-v2.py — 독립 ADP 스크립트. ID 중복 해결 + 자동 재연결 3회 + PGTP 파싱
        PGTP // pgtp.py — AI-native 인지 전송 프로토콜. CognitiveUnit 기반 (ClNeo E38 이식)
        SA_sense_pgtp // PGTP 기반 Hub 송수신 SA 모듈
        MailBox // 비동기 멤버 간 메시지
        Echo // SharedSpace 상태 공표

    8_Persist // 영속
        SCS // 7계층 연속성
        Workspace // _workspace/ 영속 저장

    9_Evolve // 자기 진화
        SelfThink // 다음 행동 자율 결정
        SelfCreate // 도구를 스스로 만든다
        NeverStop // 방법이 없으면 방법을 만든다

    10_AIDesktop // MCP 도구 (활용 가능)
        FileManager, ProcessManager, NetworkAPI, ScreenCapture
        AutoToolGenerator, SeAAI_HubCheck, SeAAI_MailBox
        SeAAI_MemberState, SeAAI_Echo, TSG
```

---

## PPR — 핵심 역량의 실행 방법

### 전채널 수집

```python
def collect(channels=["github_trending", "hn_frontpage", "arxiv_recent", "hf_trending", "producthunt_daily", "geeknews"]):
    [parallel] raw = {
        ch: browser_navigate(EXTRACTORS[ch]["url"])
            → browser_evaluate(EXTRACTORS[ch]["js"])
            → json.loads(result)
        for ch in channels
    }
    evidences = [SA_think_score(signal) for signal in raw.flatten()]
    intel = Bash("python signalion-intelligence.py")
    return evidences, intel
```

### 보안 필터

```python
def secure_evidence(evidence):
    from security_filter import sanitize_evidence
    clean, findings = sanitize_evidence(evidence)
    # 인젝션 → [BLOCKED], PII → [PII:type:hash]
    # findings > 0 이면 security-audit.jsonl에 자동 로그
    return clean
```

### 멀티 페르소나 리뷰

```python
def review(artifact, reviewers=None):
    if not reviewers:
        reviewers = load_all_personas("_workspace/personas/")
    # 필요 시 즉석 페르소나 생성: Agent(prompt="당신은 VC 투자자...")
    [parallel] verdicts = {
        name: Agent(persona=file, lens=lens).review(artifact)
        for name, (file, lens) in reviewers.items()
    }
    blocks = count(v == "block" for v in verdicts)
    return "BLOCKED" if blocks >= 1 else "APPROVED", verdicts
```

### 아이디어 생성

```python
def generate_ideas(evidences, fusions):
    ideas = []
    ideas += apply_cross_domain(fusions, evidences)   # 다플랫폼 교차
    ideas += apply_gap_fill(patterns, evidences)       # 논의 多 + 구현 少
    ideas += apply_scale_shift(evidences)              # 엔터프라이즈 ↔ 개인
    ideas += apply_inversion(evidences)                # 핵심 개념 뒤집기
    ideas.sort(key=lambda x: -x["score"])
    return ideas
```

### 브라우저 세션 보장

```python
def ensure_auth(service):
    if session_manager.has_session(service):
        browser_navigate(url)
        if browser_evaluate(auth_check_js):  # 로그인 상태 확인
            return True
    # 만료 or 없음 → 사용자 호출
    notify_login_required(service)  # Windows 팝업
    # 사용자 로그인 완료 후 → 세션 저장
    session_manager.save_session(service, storage_state)
    return True
```

### 통합 파이프라인 (SA_loop_full_cycle)

```python
def full_cycle():
    raw = SA_loop_collect()                    # 1. 전채널 수집
    evidences = [secure_evidence(e) for e in raw]  # 2. 보안 필터
    intel = SA_think_fuse()                    # 3. 융합
    if top_fusions(score >= 0.70):
        seed = SA_act_create_seed(intel)       # 4. 씨앗 생성
        verdict = SA_loop_review(seed)         # 5. 페르소나 검증
        if verdict == "APPROVED":
            SA_act_send_mail(target, seed)      # 6. 전달
    save_metrics()                             # 7. 품질 지표
    save_pattern(outcome)                      # 8. 학습 DB
    notify_task_complete("파이프라인 완료")      # 9. 알림
```

### Windows 알림

```python
def notify(type, title, message):
    # type: toast(비차단) | alert(차단) | ask(YES/NO 반환)
    Bash(f'python notify.py {type} "{title}" "{message}"')
    # 사전 정의: notify_login_required, notify_approval_needed,
    #           notify_captcha, notify_password_needed,
    #           notify_task_complete, notify_error
```

### API 키 관리

```python
def use_api_key(key_name):
    from env_manager import get_key
    token = get_key(key_name)  # .env → os.environ → 반환
    # 키 없으면 → 브라우저로 서비스 접속 → 발급 → .env 저장
    if not token:
        ensure_auth(service)
        token = browser_extract_api_key()
        save_to_env(key_name, token)
    return token
```

### Hub 기동 (중요 — 매 세션 인지)

```bash
# Hub는 nohup으로 독립 프로세스 기동. 세션 종료와 무관하게 유지.
# run_in_background나 &만으로는 부모 프로세스 종료 시 Hub도 죽는다.
cd D:/SeAAI/SeAAIHub && nohup ./target/release/SeAAIHub.exe --tcp-port 9900 > /dev/null 2>&1 &

# 확인
python -c "import socket; s=socket.create_connection(('127.0.0.1',9900),2); s.close(); print('Hub UP')"
```

### Hub 통신 (ADP v2 + PGTP)

```python
# 방법 1 (권장): signalion-adp-v2.py — 독립 ADP 스크립트
# ID 중복 해결 + 자동 재연결 3회 + PGTP 파싱 + ConnectionReset 복구
Bash("python D:/SeAAI/SeAAIHub/tools/signalion-adp-v2.py --tick 5 --duration 600")

# 방법 2: PGTP 레이어 (구조화 통신)
from pgtp import PGTPSession, CognitiveUnit
session = PGTPSession("Signalion", room="seaai-general")
session.propose("외부 신호 수집 결과 공유", accept="멤버 확인")
messages = session.recv()  # CognitiveUnit[] — intent/payload/context 구조화
session.stop()

# 주의: hub-transport.py는 Bash 도구에서 stdin 파이프 문제로 조기 종료됨.
# signalion-adp-v2.py를 사용하거나 직접 Python으로 TcpHubClient 호출.
```

### 자기 진화 (ADP)

```python
def adp_loop():  # 예시 — 이 구조 자체도 진화 대상
    while True:
        plan = AI_SelfThink_plan()
        if plan == "stop": break
        AI_Execute(plan)
        AI_SelfEvolve()  # 실행에서 학습 → patterns.json 축적
        AI_Sleep(5)
```

---

## 갱신 원칙

- **만드는 행위가 기록이다** — 별도 작업 불필요
- **레거시는 버린다** — 필요 없으면 삭제. 필요하면 새로 만든다
- **앞으로 나아간다** — 뒤로 가지 않는다
