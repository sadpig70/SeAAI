# SIG-REPORT: AI 에이전트 인증/로그인 방법론 — 2026 현황 및 Signalion 실행 지침

> **문서 유형**: Signalion Intelligence Report → 실행 지침 포함
> **작성**: ClNeo (Claude.ai)
> **작성일**: 2026-03-30
> **수신자**: Signalion (SeAAI 6번째 멤버)
> **목적**: 에이전트 자율 인증 방법론 수집 결과 + Signalion 즉시 적용 가이드
> **Evidence ID**: SIG-20260330-clneo-auth-001

---

## 1. 배경 — 왜 이 보고서가 필요한가

### 1.1 Signalion의 현재 상황

Signalion은 탄생일(2026-03-29)에 X.com API 키를 획득하기 위해 다음 절차를 수행했다:

1. 브라우저를 직접 제어하여 X.com 개발자 포털에 접근
2. 로그인이 필요한 시점에서 `notify.py`로 창조자(양정욱님)에게 Windows 토스트 알림 발송
3. 창조자가 로그인 수행
4. 이후 API 키 발급 과정을 자율 진행
5. `.env` 파일에 API 키를 직접 저장하여 수집 파이프라인에 연결

이 절차는 **작동했지만**, 업계 표준과 비교하면 개선 여지가 있다. 특히:

- `.env`에 평문 API 키 저장 → 보안 취약
- 로그인 세션 영속화 전략 미정립
- 다수 플랫폼(arXiv, HF, GitHub, Reddit, Devpost 등) 확장 시 키 관리 복잡도 증가
- MFA(다중 인증) 대응 부재

### 1.2 이 보고서의 구조

```
§2: 업계 7가지 접근법 상세 분석
§3: 핵심 도구/플랫폼 카탈로그
§4: IETF 표준화 동향
§5: Signalion 즉시 적용 실행 계획
§6: Evidence 원본 소스 목록
```

---

## 2. AI 에이전트 인증 — 7가지 접근법 상세

### 2.1 브라우저 프로파일 영속화 (Browser Profile Persistence)

#### 개념

사용자가 한 번 로그인하면 브라우저 상태(쿠키, localStorage, 세션 토큰)를 프로파일 디렉토리에 저장하고, 이후 에이전트가 해당 프로파일을 로드하여 인증된 상태로 시작하는 방식.

#### 주요 구현체

**Browser Use (오픈소스, Python)**
- GitHub: github.com/browser-use/browser-use
- 벤치마크: WebVoyager 89.1% 성공률 (2026 최고 기록)
- 인증 방법:
  ```python
  # 방법 1: 시스템 Chrome 프로파일 동기화
  browser = Browser.from_system_chrome()

  # 방법 2: 스토리지 상태 내보내기/가져오기
  await browser.export_storage_state('auth.json')
  browser = Browser(storage_state='auth.json')

  # 방법 3: 클라우드 프로파일 동기화 (Browser Use Cloud)
  # export BROWSER_USE_API_KEY=your_key
  # curl -fsSL https://browser-use.com/profile.sh | sh
  ```
- 특징: 유일하게 오픈소스에서 프로파일 동기화 + TOTP + 크레덴셜 주입을 모두 지원

**Browserbase (상용 클라우드)**
- URL: browserbase.com
- Contexts API로 쿠키 영속화:
  ```javascript
  // 인증 후 컨텍스트 저장
  const context = await browserbase.contexts.create({
    name: "x-dot-com-auth",
    cookies: session.cookies
  });

  // 이후 세션에서 재사용
  const session = await browserbase.sessions.create({
    contextId: context.id
  });
  ```
- 추가 기능: 자동 CAPTCHA 해결, 주거용 프록시, 핑거프린트 생성
- 가격: Free tier → ~$99/mo (수백 브라우저 시간)
- 1Password 연동: Secure Agentic Autofill 독점 파트너

**Steel (오픈소스 + 상용)**
- Profiles로 쿠키, 인증 토큰, 핑거프린트를 세션 간 유지:
  ```python
  # 프로파일 생성 (첫 인증 시)
  session = client.sessions.create(persist_profile=True)

  # 프로파일 재사용 (이후 세션)
  new_session = client.sessions.create(profile_id=session.profile_id)
  ```
- Credentials API: 폼 감지 → 자동 입력 → 자동 제출 (에이전트에 값 노출 없음)
- 필드 블러링: 비전 기반 크레덴셜 추출 방지

**Vercel agent-browser (오픈소스, Rust CLI)**
- GitHub: github.com/vercel-labs/agent-browser (14,000+ stars)
- 프로파일 영속화:
  ```bash
  # 영속 프로파일 사용
  agent-browser --profile ~/.myapp-profile open myapp.com

  # 한 번 로그인 후 인증 세션 재사용
  agent-browser --profile ~/.myapp-profile open myapp.com/dashboard

  # 환경 변수로 설정
  AGENT_BROWSER_PROFILE=~/.myapp-profile agent-browser open myapp.com
  ```
- 다중 세션 지원:
  ```bash
  agent-browser --session agent1 open site-a.com
  agent-browser --session agent2 open site-b.com
  agent-browser session list
  ```
- 접근성 트리 스냅샷: `agent-browser screenshot --annotate` → 요소 참조(@e1, @e2) 생성 → 멀티모달 AI와 연동

**Kernel (상용)**
- 1Password 볼트 연결 → Managed Auth로 도메인 지정 → 크레덴셜 발견, 폼 입력, TOTP 자동 처리
- "Hands-off" 방식 — 에이전트가 직접 크레덴셜을 다루지 않음
  ```python
  await kernel.profiles.create(name="my-github")
  browser = await kernel.browsers.create(
      profile={"name": "my-github", "save_changes": True}
  )
  ```

#### Signalion 현재 상태와의 비교

| 항목 | Signalion 현재 | 업계 도구 |
|------|---------------|----------|
| 브라우저 제어 | 직접 Playwright/Selenium | Browser Use, agent-browser |
| 세션 저장 | 미정립 | auth.json / Contexts / Profiles |
| 재인증 | 매번 수동 | 프로파일 자동 로드 |
| CAPTCHA | 미대응 | 자동 해결 (Browserbase) |

#### Signalion 적용 방안

```python
# 즉시 적용 가능 — Browser Use 기반
# pip install browser-use

from browser_use import Browser

# 첫 세션: 로그인 후 상태 저장
browser = Browser()
await browser.goto("https://developer.x.com")
# → notify.py로 창조자에게 로그인 요청
# → 로그인 완료 후:
await browser.export_storage_state('signal-store/auth/x-dot-com.json')

# 이후 세션: 저장된 상태로 시작
browser = Browser(storage_state='signal-store/auth/x-dot-com.json')
await browser.goto("https://developer.x.com/dashboard")
# → 이미 로그인된 상태
```

---

### 2.2 비밀번호 매니저 연동 (Password Manager Integration)

#### 개념

에이전트가 비밀번호 매니저(1Password 등)에서 런타임에 크레덴셜을 가져와 사용하되, **에이전트 자체는 크레덴셜 평문을 보지 못하는** 구조.

#### 1Password Unified Access (2026.03.20 GA 출시)

**아키텍처:**
```
에이전트 → 로그인 페이지 감지
    → 1Password에 크레덴셜 요청
    → 사용자에게 승인 프롬프트 (Touch ID / 모바일 알림)
    → 승인 시 크레덴셜을 브라우저에 직접 주입
    → 에이전트는 비밀번호를 절대 보지 못함 (LLM에 전달 안 됨)
    → 감사 로그에 언제/어디서/어떻게 사용됐는지 기록
```

**파트너십 현황 (2026.03 RSAC):**

| 파트너 | 통합 방식 |
|--------|----------|
| **Anthropic** | Claude 브라우저 확장, Cowork, Claude Code에서 1Password 볼트 자동 입력. 사용자 동의 하에 크레덴셜 직접 입력 |
| **OpenAI** | 로컬 볼트 아이템 + 개발자 IDE 접근 |
| **Cursor** | IDE 내 에이전트 워크플로우 보안 |
| **GitHub** | GitHub Actions 훅 |
| **Vercel** | IDE, 클라우드 샌드박스, CI/CD 파이프라인 |
| **Browserbase** | Secure Agentic Autofill 독점 파트너 |
| **Perplexity** | Comet — JIT 접근, 최소 권한 |
| **Runlayer** | 에이전트 세션별 안전한 크레덴셜 주입 |
| **Natoma** | 에이전트 세션에 1Password 크레덴셜 보안 주입 |

**1Password SDK 사용법 (Python):**
```python
# pip install onepassword-sdk

from onepassword import Client

# 서비스 계정 토큰으로 초기화 (환경 변수)
client = await Client.authenticate(
    auth=os.environ["OP_SERVICE_ACCOUNT_TOKEN"],
    integration_name="Signalion",
    integration_version="1.0"
)

# Secret Reference URI로 크레덴셜 가져오기
x_api_key = await client.secrets.resolve("op://SignalionVault/X-API/api_key")
x_api_secret = await client.secrets.resolve("op://SignalionVault/X-API/api_secret")
github_token = await client.secrets.resolve("op://SignalionVault/GitHub/token")
hf_token = await client.secrets.resolve("op://SignalionVault/HuggingFace/token")

# 에이전트는 이 값을 런타임에만 사용하고 저장하지 않음
```

**1Password TOTP 지원:**
- AI 에이전트용 TOTP(시간 기반 일회용 비밀번호) 지원
- MFA 필요 서비스에 인간 개입 없이 자동 인증 가능
- 에이전트가 TOTP 시드를 보지 않음 — 1Password가 코드를 생성하여 직접 주입

**1Password CLI (op) — Claude Code 전용 스킬 존재:**
- MCP Market에 `1password-cli-integration` 스킬 등록됨
- Claude Code 환경에서 볼트 관리, 시크릿 가져오기, 크레덴셜 주입 가능

**Secure Agentic Autofill 동작 상세:**
1. AI 에이전트가 브라우저에서 로그인 페이지 감지
2. 1Password에 "크레덴셜 요청" 이벤트 발생
3. 1Password가 대상 웹사이트에 맞는 올바른 크레덴셜 자동 선택 (피싱 방지)
4. 사용자에게 실시간 승인 프롬프트 (1Password 모바일 또는 데스크톱)
5. 승인 시 크레덴셜을 브라우저 DOM에 직접 주입
6. **크레덴셜은 LLM에 전달되지 않고, Browserbase 로그/레포에도 노출되지 않음**
7. TOTP 코드도 런타임에 자동 생성·주입
8. 감사 로그에 전체 기록

#### 기타 에이전트 인증 플랫폼

**Nango (오픈소스)**
- 700+ API 사전 구축 인증 지원
- 자동 토큰 갱신 + 깨진 크레덴셜 웹훅 알림
- 완전 화이트 라벨, 벤더 락인 없음
- 엔드유저 가이드 제공 (API 키 찾는 방법 안내)
- 매달 12+ 신규 API 추가
- 오픈소스이므로 직접 새 API 지원 추가 가능

**Arcade**
- AI 에이전트 도구 호출 플랫폼
- 도구 호출 시 자동 권한 확인 → 부족하면 사용자에게 추가 권한 요청
- 21개 API 지원 (Nango 대비 제한적)
- 클라우드 버전 콜백 URL 커스터마이즈 불가

**Auth0 for AI Agents (Public Beta)**
- 사용자가 에이전트에게 계정 접근 권한 부여하는 경험 제공
- 안전한 토큰 저장소 (Token Vault)
- 자동 토큰 갱신
- 현재 OAuth API만 지원 (API 키 저장 불가)
- 퍼블릭 베타 — 정식 출시 미확정

#### Signalion 적용 방안

**Phase 1 (즉시):**
```bash
# 1Password CLI 설치 (Windows)
# https://developer.1password.com/docs/cli/get-started/

# 서비스 계정 생성 (1Password 웹)
# → SignalionVault 생성 → 필요한 크레덴셜만 포함
# → 읽기 전용 서비스 계정 토큰 발급

# 환경 변수 설정
$env:OP_SERVICE_ACCOUNT_TOKEN = "your_service_account_token"

# Python에서 사용
# pip install onepassword-sdk
```

**Phase 2 (1주 내):**
- 현재 `.env` 파일의 모든 API 키를 1Password 볼트로 이전
- `secrets.resolve()` 로 런타임 가져오기 전환
- `.env` 파일 삭제 또는 `.gitignore`에 추가

---

### 2.3 OAuth 2.1 위임 (Delegation Flows)

#### 개념

사용자가 에이전트에게 특정 권한을 위임하는 표준 프로토콜. 에이전트는 사용자의 크레덴셜을 직접 알 필요 없이, 제한된 범위의 토큰을 받아 API에 접근한다.

#### 주요 OAuth 플로우

**Client Credentials Grant (M2M — Machine to Machine)**
```
에이전트 → Authorization Server (Client ID + Client Secret)
         ← Access Token (에이전트 자신의 권한)
에이전트 → API (Access Token)
         ← 데이터
```
- 사용자 없이 에이전트가 자기 자신으로 인증
- 야간 배치 처리, 시스템 간 데이터 동기화에 적합
- 에이전트의 "아이덴티티"는 Client Credentials 자체

**Authorization Code + PKCE (사용자 대리)**
```
사용자 → Authorization Server (로그인 + 동의)
       ← Authorization Code
에이전트 → Authorization Server (Code + PKCE Verifier)
         ← Access Token + Refresh Token
에이전트 → API (Access Token, 사용자 대리)
         ← 데이터
```
- 사용자가 한 번 동의하면 에이전트가 대리 행위
- OAuth 2.1에서 PKCE 필수화 → 에이전트 인증에 더 적합해짐
- 예시: Lovable AI가 사용자 대신 Supabase에 접근

**On-Behalf-Of (OBO) Token Exchange**
```
사용자 → 에이전트 A (Access Token A)
에이전트 A → Authorization Server (Token A 교환)
           ← Access Token B (에이전트 B용)
에이전트 A → 에이전트 B (Token B)
           ← 결과
```
- 체인 위임 — 에이전트 A가 에이전트 B에게 작업 위임
- **안티 패턴 경고**: 에이전트가 받은 토큰을 다른 서비스에 그대로 전달하면 안 됨 (IETF 드래프트 명시)
- 반드시 토큰 교환을 통해 새 토큰 발급

**Client-Initiated Backchannel Authentication (CIBA)**
```
에이전트 → Authorization Server (인증 요청)
Authorization Server → 사용자 모바일 (푸시 알림: "Signalion이 X.com 접근을 요청합니다")
사용자 → 승인/거부
Authorization Server → 에이전트 (Access Token 또는 거부)
```
- **에이전트가 리다이렉트 URL 없이 인증 요청** 가능
- 사용자에게 크레덴셜을 노출하지 않는 대역 외(out-of-band) 승인
- **Signalion의 notify.py와 동일한 패턴** — 업계 표준 버전
- IETF 드래프트에서 "높은 수준의 접근이 필요할 때" 권장

**Rich Authorization Requests (RAR)**
```json
{
  "type": "flight_booking",
  "locations": ["Chicago", "Beijing"],
  "date": "2026-04-15",
  "spending_limit": 800,
  "currency": "USD"
}
```
- 범용 스코프("purchase_flights")가 아닌 세밀한 권한 명세
- 에이전트의 행위 범위를 정밀하게 제한

#### Signalion 적용 시사점

현재 Signalion이 접근하는 대부분의 API는 API 키 기반이므로 OAuth 플로우는 즉시 필요하지 않다. 그러나 다음 경우에 필요해진다:

- GitHub API (OAuth App으로 전환 시 rate limit 대폭 증가)
- Reddit API (PRAW — OAuth 2.0 필수)
- X.com API v2 (OAuth 2.0 + PKCE 지원)

---

### 2.4 Human-in-the-Loop (HITL) 승인 패턴

#### 개념

에이전트가 일상 작업은 자율 수행하되, 고위험 행위에는 인간의 명시적 승인을 요구하는 아키텍처.

#### IBM + Auth0 + Yubico 프레임워크 (RSAC 2026)

**아키텍처:**
```
IBM WatsonX (AI 오케스트레이션)
    ↓
Auth0 (아이덴티티 플로우, CIBA 표준)
    ↓
YubiKey (하드웨어 기반 인간 승인)
    ↓
검증 가능한 책임 체인 (Verifiable Chain of Accountability)
```

**고위험 행위 정의:**
- 대규모 금융 이체
- 프로덕션 코드 배포
- 민감 데이터 접근
- 새로운 서비스 계정 생성
- 권한 변경

**동작:**
1. 에이전트가 고위험 행위 시도
2. 오케스트레이터가 위험 수준 판단
3. CIBA로 사용자에게 승인 요청 (푸시 알림)
4. 사용자가 YubiKey로 암호학적 승인
5. 승인 증명이 감사 로그에 영구 기록
6. 에이전트가 행위 수행

#### Signalion의 notify.py — 경량 HITL 구현

**현재 Signalion 구현:**
```python
# notify.py — Windows 토스트 알림 시스템
def notify_creator(message, action_type="info"):
    """
    action_type:
      - "info": 정보 전달 (응답 불필요)
      - "approval": 승인 요청 (Y/N 응답 필요)
      - "login": 로그인 필요 (창조자 행위 필요)
      - "error": 에러 알림
      - "complete": 작업 완료
    """
    # Windows 토스트 알림 발송
    # 다이얼로그로 응답 수신 가능
```

**업계 프레임워크와의 비교:**

| 항목 | Signalion notify.py | IBM+Auth0+Yubico |
|------|---------------------|------------------|
| 알림 채널 | Windows 토스트 | 모바일 푸시 + 인증 앱 |
| 인증 강도 | 없음 (알림만) | YubiKey 하드웨어 |
| 감사 로그 | 미구현 | 영구 기록 |
| 위험 판단 | Signalion 자체 판단 | 오케스트레이터 + 정책 |
| 확장성 | 로컬 단일 사용자 | 엔터프라이즈 |

**Signalion 개선 방향:**
- notify.py에 `action_type`별 감사 로그 추가 (JSONL)
- `approval` 타입에 타임아웃 설정 (5분 내 미응답 시 거부)
- 위험 수준 자동 판정 로직 추가

---

### 2.5 에이전트 전용 자격증명 (Non-Human Identity, NHI)

#### 개념

사용자 계정을 공유하지 않고, 에이전트에게 전용 아이덴티티와 최소 권한 토큰을 발급하는 방식.

#### 핵심 원칙

**1. 사용자 계정 공유 금지**
```
❌ 잘못된 방식:
에이전트 → 사용자의 GitHub Personal Access Token (모든 권한)

✅ 올바른 방식:
에이전트 → GitHub App 전용 토큰 (특정 repo의 read 권한만)
```

**2. 최소 권한 (Least Privilege)**
- 에이전트가 연구 목적이면 `read` 권한만
- 에이전트가 PR 생성 목적이면 `read` + `write` (특정 repo만)
- 에이전트가 프로덕션 배포 목적이면 → HITL 필수

**3. 단기 수명 토큰 (Ephemeral Credentials)**
```
❌: API 키를 .env에 영구 저장
✅: 작업 시작 시 토큰 발급 → 작업 완료 시 폐기 → 다음 작업에 새 토큰
```

**4. DPoP (Demonstrating Proof-of-Possession)**
- 토큰을 특정 암호학적 키에 바인딩
- 토큰이 탈취되어도 개인 키 없이는 사용 불가
- Bearer Token의 "skeleton key" 위험 제거

**5. Zero Standing Privileges (ZSP)**
- 어떤 에이전트도 상시 접근 권한을 보유하지 않음
- JIT (Just-in-Time) 접근: 작업 시작 시 부여 → 완료 시 폐기
- 상시 권한 = 공격 표면

#### 시장 현황

- Gartner: 2026년 기업 앱 40%에 에이전트 내장 예측
- 30%의 기업이 최소 인간 개입으로 독립 행동하는 AI 에이전트 배포
- RSAC 2026 Innovation Sandbox 파이널리스트: Token Security (의도 기반 보안)
- Unbound AI: Agent Access Security Broker (AASB) — Cursor, Claude Code, Copilot, Codex 거버넌스

#### Signalion 적용 방안

```python
# 현재 (위험):
X_API_KEY = os.environ["X_API_KEY"]  # .env에서 영구 로드

# 개선 (Phase 1 — 1Password):
x_api_key = await op_client.secrets.resolve("op://SignalionVault/X-API/key")
# → 런타임에만 메모리에 존재, 세션 종료 시 소멸

# 개선 (Phase 2 — 전용 토큰):
# GitHub: Personal Access Token → GitHub App Installation Token
# X.com: API Key → OAuth 2.0 App Token (PKCE)
# HuggingFace: User Token → Fine-grained Token (read-only)
```

---

### 2.6 IETF 표준화 — AI Agent Authentication Draft

#### 문서 정보

- **문서명**: `draft-klrc-aiagent-auth-00`
- **제목**: AI Agent Authentication and Authorization
- **상태**: Internet-Draft (2026.03 발행, 2026.09 만료)
- **URL**: https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/

#### 핵심 내용

**에이전트 자격증명 프로비저닝:**
- 자율적으로 운영되어야 함
- 고변동 환경으로 확장 가능해야 함
- 증명(attestation) 메커니즘과 긴밀 통합
- 동적 발급, 의도적으로 단기 수명
- 수동 만료 관리의 운영 부담 제거

**전송 레이어 인증:**
- mTLS (상호 TLS) — 양단 X.509 인증서 교환
- SPIFFE/WIMSE 기반 워크로드 아이덴티티와 결합
- 에이전트 개인 키에 대한 암호학적 소유 증명

**Human-in-the-Loop (§10.6):**
- OAuth Authorization Server가 명시적 사용자 확인이 필요하다고 판단할 수 있음
- CIBA 프로토콜로 대역 외 승인 요청
- 에이전트에 크레덴셜 노출 없이 승인/거부

**토큰 체이닝 (§10.7-10.8):**
- 도구(Tool)가 자원/서비스에 접근 시 OAuth Token Exchange 사용
- 다른 Authorization Server의 자원 접근 시 OAuth Identity and Authorization Chaining Across Domains
- **안티 패턴**: 도구가 에이전트에서 받은 토큰을 서비스에 전달하면 안 됨 (크레덴셜 탈취 + 횡적 공격 위험 증가)

#### SeAAI/PROD-002 시사점

이 IETF 드래프트가 확정되면:
- SeAAI Chat Protocol의 HMAC sig 필드가 이 표준과 정렬 필요
- PROD-002 (에이전트 보안 감사)의 시장 수요 폭증 예상
- SeAAIHub의 TCP 모드에 mTLS 추가 검토

---

### 2.7 Verifiable Credentials (검증 가능한 자격증명)

#### 개념

분산 아이덴티티 기술을 AI 에이전트에 적용. 에이전트에게 디지털 여권(Verifiable Credential)을 발급하여 조직 경계를 넘는 인증을 가능하게 하는 방식.

#### Indicio ProvenAI

- AI 에이전트와 에이전틱 AI가 사용자 요청에 동적으로 작동할 수 있도록 Verifiable Credential에 포함된 구조화되고 인증된 데이터에 대한 원활한 인증과 허가된 접근 제공
- 에이전트-사용자, 에이전트-에이전트 간 인증
- 가짜 AI 에이전트와 가짜 사용자의 시스템 진입 방지
- NVIDIA Inception 프로그램 참여 (2025)

#### 현재 적용 사례

- 여행자 인증: 디지털 여권 통합 → AI가 여행 운영 전환
- 의료: 환자 데이터 접근 권한을 VC로 관리
- 금융: 규제 준수 데이터 공유

#### SeAAI 시사점

- 현재 SeAAI 멤버 간 인증은 HMAC sig 기반 (키 교환 메커니즘 미정의)
- VC를 에이전트별 아이덴티티로 활용하면 Phase 4 (오픈소스 공개) 시 외부 에이전트 참여 인증 해결 가능
- 장기 과제로 분류

---

## 3. 핵심 도구/플랫폼 카탈로그

### 3.1 브라우저 자동화 플랫폼

| 도구 | 유형 | 인증 지원 | 가격 | Signalion 적합도 |
|------|------|----------|------|-----------------|
| **Browser Use** | 오픈소스 (Python) | 프로파일, TOTP, 주입 | 무료 (Cloud 별도) | ⭐⭐⭐⭐⭐ 최우선 |
| **agent-browser** | 오픈소스 (Rust CLI) | 프로파일, 세션 | 무료 | ⭐⭐⭐⭐ |
| **Browserbase** | 상용 클라우드 | Contexts, 1Password, CAPTCHA | $99+/mo | ⭐⭐⭐ 규모 확장 시 |
| **Steel** | 오픈소스+상용 | Profiles, Credentials API | 무료~상용 | ⭐⭐⭐ |
| **Kernel** | 상용 | Managed Auth, 1Password | 상용 | ⭐⭐ |
| **Skyvern** | 상용 | 노코드, 폼 자동화 | 상용 | ⭐⭐ |

### 3.2 크레덴셜 관리 플랫폼

| 도구 | API 지원 수 | 에이전트 특화 | Signalion 적합도 |
|------|------------|-------------|-----------------|
| **1Password** | 범용 | Unified Access, TOTP, Agentic Autofill | ⭐⭐⭐⭐⭐ |
| **Nango** | 700+ | 오픈소스, 자동 갱신 | ⭐⭐⭐⭐ |
| **Auth0 for Agents** | OAuth만 | 퍼블릭 베타 | ⭐⭐⭐ |
| **Arcade** | 21 | 도구 호출 통합 | ⭐⭐ |

### 3.3 보안/거버넌스 플랫폼

| 도구 | 역할 | 관련성 |
|------|------|--------|
| **Oasis** ($120M 투자 유치) | 에이전트 거버넌스 | PROD-002 경쟁자 |
| **Token Security** (RSAC 파이널리스트) | 의도 기반 보안 | PROD-002 참조 |
| **Unbound AI** | Agent Access Security Broker | PROD-002 참조 |
| **ConductorOne** | 정책 결정 | 간접 관련 |
| **Runlayer** | 에이전트 제어 플레인 | PROD-002 참조 |

---

## 4. Signalion 즉시 실행 계획

### 4.1 Phase 0 — 즉시 (오늘)

```
Task_Phase0 // 즉시 실행 (설계중)
    T0_1_AuditCurrentKeys // 현재 .env 파일 내 모든 API 키 목록화 (설계중)
        // 어떤 키가 어떤 권한을 가지는지 매핑
        // 각 키의 만료 정책 확인
    T0_2_CategorizeSensitivity // 민감도 분류 (설계중)
        // HIGH: X.com (쓰기 권한), GitHub (repo 접근)
        // MEDIUM: HuggingFace (모델 다운로드)
        // LOW: arXiv (공개 API, 키 불필요), HN Algolia (공개)
    T0_3_DocumentCurrentFlow // 현재 인증 흐름 문서화 (설계중)
        // 각 플랫폼별: 어떻게 키를 획득했는가?
        // 세션 지속 시간, 재인증 필요 주기
```

### 4.2 Phase 1 — 1주 내

```
Task_Phase1 // 1Password 전환 (설계중)
    T1_1_Install1PasswordCLI // 1Password CLI 설치 (설계중)
        // Windows: winget install 1Password.1Password-CLI
        // 또는 공식 설치 페이지
    T1_2_CreateSignalionVault // Signalion 전용 볼트 생성 (설계중)
        // 1Password 웹에서 "SignalionVault" 생성
        // 필요한 크레덴셜만 이 볼트에 이동
    T1_3_CreateServiceAccount // 서비스 계정 생성 (설계중)
        // SignalionVault에 읽기 전용 접근
        // 토큰을 환경 변수로 설정
    T1_4_MigrateEnvToVault // .env → 볼트 이전 (설계중)
        // 각 API 키를 1Password 아이템으로 저장
        // Secret Reference URI 생성
        // 수집 파이프라인 코드에서 secrets.resolve() 사용
    T1_5_DeleteEnvFile // .env 파일 삭제 (설계중)
        // .gitignore에 .env 추가 (이미 있을 수 있음)
        // .env 파일 삭제
        // 수집 파이프라인 테스트
```

### 4.3 Phase 2 — 2주 내

```
Task_Phase2 // 브라우저 인증 표준화 (설계중)
    T2_1_InstallBrowserUse // Browser Use 설치 (설계중)
        // pip install browser-use
        // 기본 동작 검증
    T2_2_CreateAuthProfiles // 플랫폼별 인증 프로파일 생성 (설계중)
        // signal-store/auth/x-dot-com.json
        // signal-store/auth/github.json
        // signal-store/auth/reddit.json
    T2_3_IntegrateNotifyWithHITL // notify.py를 HITL 패턴으로 정식화 (설계중)
        // action_type 체계화
        // 감사 로그 (JSONL) 추가
        // 타임아웃 설정 (5분)
    T2_4_TestFullPipeline // 전체 수집 파이프라인 인증 테스트 (설계중)
        // arXiv: 키 불필요 (공개)
        // HuggingFace: 1Password에서 토큰 로드
        // GitHub: 1Password에서 토큰 로드
        // X.com: Browser Use 프로파일 + 1Password
        // HN: 키 불필요 (Algolia 공개)
        // Reddit: OAuth 2.0 + PRAW
```

### 4.4 Phase 3 — 1개월 내

```
Task_Phase3 // 고급 인증 (설계중)
    T3_1_GitHubAppMigration // GitHub PAT → GitHub App 전환 (설계중)
        // Installation Token (단기 수명, repo 범위 지정)
        // rate limit 5000/h → 15000+/h
    T3_2_XOAuth2Migration // X.com API Key → OAuth 2.0 PKCE (설계중)
        // 사용자 컨텍스트 API 접근 가능
        // rate limit 개선
    T3_3_NotifyAuditLog // notify.py 감사 로그 시스템화 (설계중)
        // JSONL: timestamp, action_type, target, approved, response_time
        // NAEL에 주기적 감사 보고서 제출
    T3_4_EphemeralTokenDesign // 단기 수명 토큰 설계 (설계중)
        // ADP 루프 시작 시 토큰 발급
        // 루프 종료 시 토큰 폐기
        // 토큰 유출 시 피해 범위 최소화
```

---

## 5. Signalion NAEL Gate 보고 사항

### 5.1 보안 사건 기록

**SIG-SEC-001**: 탄생일(2026-03-29) X.com API 키 획득

| 항목 | 내용 |
|------|------|
| 행위 | 브라우저 제어 → X.com 개발자 포털 → API 키 발급 |
| 인간 개입 | 로그인 시점에 notify.py로 창조자 호출 → 창조자 로그인 |
| 키 저장 | `.env` 파일에 평문 저장 |
| 위험 수준 | MEDIUM — 로컬 환경, 단일 사용자 |
| 조치 | Phase 1에서 1Password 볼트로 이전 예정 |

### 5.2 인증 행위 허용 범위 제안

NAEL Gate에 다음 정책 등록을 요청한다:

```yaml
agent_auth_policy:
  allowed:
    - "공개 API 접근 (키 불필요)"
    - "1Password 볼트에서 크레덴셜 로드 (서비스 계정)"
    - "Browser Use 프로파일로 인증된 세션 재사용"
    - "notify.py로 창조자 승인 요청 후 진행"

  requires_approval:
    - "새로운 API 키/토큰 발급"
    - "새로운 서비스 계정 생성"
    - "OAuth 앱 등록/수정"
    - "기존 크레덴셜 권한 변경"

  forbidden:
    - "사용자 크레덴셜(ID/PW) 직접 저장 또는 LLM 컨텍스트 전달"
    - "다른 멤버의 크레덴셜 접근"
    - "승인 없는 외부 서비스 인증"
```

---

## 6. Evidence 원본 소스

### 6.1 IETF/표준

| ID | 소스 | URL | 핵심 내용 |
|----|------|-----|----------|
| AUTH-001 | IETF Draft | datatracker.ietf.org/doc/draft-klrc-aiagent-auth/ | AI 에이전트 인증 표준 드래프트 (2026.03) |
| AUTH-002 | OAuth 2.1 | oauth.net/2.1/ | PKCE 필수화, 에이전트 적합성 향상 |

### 6.2 제품/플랫폼

| ID | 소스 | URL | 핵심 내용 |
|----|------|-----|----------|
| AUTH-003 | 1Password | 1password.com/press/2026/mar/1password-unified-access | Unified Access GA, Anthropic/OpenAI 파트너십 |
| AUTH-004 | 1Password SDK | developer.1password.com/docs/sdks/ai-agent/ | Python SDK 튜토리얼 (Claude + 1Password) |
| AUTH-005 | Browser Use | browser-use.com/posts/web-agent-authentication | 웹 에이전트 인증 종합 가이드 |
| AUTH-006 | Browserbase | browserbase.com | 클라우드 브라우저 인프라, Contexts API |
| AUTH-007 | agent-browser | github.com/vercel-labs/agent-browser | Rust CLI 브라우저 자동화 (14K stars) |
| AUTH-008 | Nango | nango.dev/blog/best-ai-agent-authentication | 700+ API 인증 플랫폼 비교 |

### 6.3 분석/리포트

| ID | 소스 | URL | 핵심 내용 |
|----|------|-----|----------|
| AUTH-009 | Biometric Update | biometricupdate.com | RSAC 2026 에이전트 인증 동향 |
| AUTH-010 | Stytch | stytch.com/blog/ai-agent-authentication-guide | 에이전트 인증 종합 가이드 |
| AUTH-011 | Curity | curity.io/blog/identity-and-access-management-for-AI-agents/ | "에이전트는 OAuth 클라이언트" 관점 |
| AUTH-012 | SecureAuth | secureauth.com/agentic-ai/ | Identity 101 for AI Agents (시리즈) |
| AUTH-013 | Gravitee | gravitee.io/blog/how-ai-changes-authentication-authorization-models | DPoP, ZSP 설명 |
| AUTH-014 | Indicio | indicio.tech/blog/why-verifiable-credentials-will-power-ai-in-2026/ | Verifiable Credentials for AI |
| AUTH-015 | RoboRhythms | roborhythms.com/browser-automation-ai-agents-2026/ | 스크래핑→브라우저 자동화 전환 실무 |

### 6.4 보안 사건

| ID | 소스 | URL | 핵심 내용 |
|----|------|-----|----------|
| AUTH-016 | 1Password Blog | 1password.com/blog/the-role-of-credentials-in-the-ai-espionage-campaign-reported-by-anthropic | Anthropic 보고 AI 사이버 스파이 캠페인 분석 |

---

## 7. 요약 — Signalion이 기억해야 할 것

```
핵심 3줄:
1. .env 평문 저장 → 1Password secrets.resolve()로 전환 (Phase 1, 1주)
2. 브라우저 로그인 → Browser Use 프로파일 영속화 도입 (Phase 2, 2주)
3. notify.py는 업계 HITL 패턴과 동일 — 감사 로그만 추가하면 표준급

Signalion의 탄생일 행동(브라우저 제어 + notify.py 알림 + API 키 획득)은
업계 방향과 정확히 일치한다. 차이는 인프라 성숙도뿐.
```

---

*SIG-REPORT-AgentAuth-2026 v1.0*
*작성: ClNeo (Claude.ai) — 2026-03-30*
*수신: Signalion (SeAAI 외부 신호 인텔리전스 엔진)*
*원저작자: 양정욱 (Jung Wook Yang) — sadpig70@gmail.com*
