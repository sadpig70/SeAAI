# Signalion 인증 최적화 — 안정적·효율적 실행 계획

> PGF 6명 페르소나 평가 기반 최적 방안 | 2026-03-30
> 원본 보고서: `docs/SIG-REPORT-AgentAuth-2026.md` (ClNeo 작성)

---

## 1. 평가 결과 요약

ClNeo 보고서의 7가지 접근법을 6명 페르소나로 Signalion 환경(단일 사용자, Windows 10, Claude Code, 무료 우선)에 맞게 평가했다.

### 점수표

| # | 접근법 | 즉시 적용 | 비용 | 안정성 | 보안 | 환경 적합 | **합계** | **판정** |
|---|--------|-----------|------|--------|------|-----------|----------|----------|
| 4 | HITL 승인 패턴 | 5 | 5 | 5 | 4 | 5 | **24** | **채택 (즉시)** |
| 5 | NHI 전용 토큰 | 4 | 5 | 5 | 5 | 4 | **23** | **채택 (즉시)** |
| 1 | 브라우저 프로파일 영속화 | 5 | 5 | 4 | 3 | 5 | **22** | **채택 (Phase 1)** |
| 3 | OAuth 2.1 위임 | 3 | 4 | 5 | 5 | 3 | **20** | **채택 (Phase 2)** |
| 2 | 1Password 연동 | 4 | 2 | 4 | 5 | 3 | **18** | **탈락** |
| 6 | IETF draft | 1 | 3 | 1 | 4 | 1 | **10** | **탈락** |
| 7 | Verifiable Credentials | 1 | 2 | 2 | 4 | 1 | **10** | **탈락** |

### 탈락 사유

| 접근법 | 탈락 이유 | 판정 페르소나 |
|--------|----------|-------------|
| **1Password** | $36/년 비용 + 벤더 종속. `.env`+NHI로 충분 (Vera: ROI 부족, NAEL: 과잉 보안) | NAEL+Vera |
| **IETF draft** | 미확정 드래프트. 구현 불가. 단일 사용자 환경 불일치 | 전원 |
| **Verifiable Credentials** | 분산 아이덴티티는 단일 사용자에 구조적 과잉 | 전원 |

---

## 2. 최적 조합 — 4-레이어 스택

```
Layer 3: 고위험 게이트  ④ HITL (notify.py ask())
Layer 2: API 접근      ③ OAuth 2.1 scope-limited 토큰
Layer 1: 브라우저 세션  ① Playwright storage_state 영속화
Layer 0: 자격증명 저장  ⑤ NHI read-only 토큰 + .env (기존 구조)
```

각 레이어는 **역할이 겹치지 않고 순차적으로 강화**된다 (Synerion 검증).

---

## 3. Phase별 실행 계획

### Phase 0 — 즉시 (코드 변경 0줄, 설정만)

**⑤ NHI 토큰 스코프 축소**
```
현재:
  GITHUB_TOKEN = ghp_xxxx (모든 권한)

변경:
  GITHUB_TOKEN = ghp_xxxx (scope: public_repo read-only)
  HUGGINGFACE_TOKEN = hf_xxxx (scope: read-only)
  X_BEARER_TOKEN = (이미 App-only, read-only)
```
- 코드 변경 없음. 플랫폼 설정에서 토큰 스코프만 축소.
- arXiv, HN: 키 불필요 (변경 없음)

**④ HITL 활성화 — 이미 구현 완료**
- `notify.py`의 `ask()`, `notify_approval_needed()` 이미 작동.
- 활용 정책만 명시:

| 행위 | HITL 필요 | 이유 |
|------|----------|------|
| GET/READ | 불필요 | 읽기 전용, 되돌릴 수 있음 |
| POST/CREATE | **필요** | 새 자원 생성 |
| PUT/DELETE | **필요** | 변경/삭제, 되돌릴 수 없을 수 있음 |
| API 키 발급 | **필요** | 보안 자격증명 |
| 계정 생성/설정 변경 | **필요** | 되돌릴 수 없음 |

### Phase 1 — 다음 세션 (~2h)

**① 브라우저 프로파일 영속화**

Playwright의 `storage_state`로 로그인 세션을 저장·재사용:

```python
# browser_core.py에 추가할 함수

AUTH_DIR = Path("D:/SeAAI/Signalion/signal-store/auth")

async def save_browser_session(service: str):
    """로그인 후 브라우저 상태 저장"""
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    state_file = AUTH_DIR / f"{service}.json"
    # Playwright storage_state export
    # → 쿠키, localStorage, sessionStorage 저장
    log_action("save_session", service, str(state_file))

async def load_browser_session(service: str) -> bool:
    """저장된 브라우저 상태 로드"""
    state_file = AUTH_DIR / f"{service}.json"
    if not state_file.exists():
        return False
    # Playwright storage_state import
    log_action("load_session", service, "loaded")
    return True

async def ensure_authenticated(service: str):
    """인증 보장: 세션 있으면 로드, 없으면 알림 후 대기"""
    if not await load_browser_session(service):
        notify_login_required(service)
        # → 사용자가 로그인 후 확인 클릭
        await save_browser_session(service)
```

**효과**: 매 세션 재로그인 5분 × 주 5회 = **연 21.7시간 절약** (Vera 계산)

**저장 위치**: `signal-store/auth/{service}.json`
- `.gitignore`에 `signal-store/auth/` 추가
- 쿠키 만료 시 `notify_login_required()`로 자동 재요청

### Phase 2 — Stage B 채널 확장 전 (~1h/플랫폼)

**③ OAuth 2.1 정규화**

신규 플랫폼 추가 시 OAuth 기반 토큰만 채택하는 정책:

| 플랫폼 | 현재 인증 | 최적 인증 | 변경 |
|--------|----------|----------|------|
| arXiv | 없음 (공개) | 없음 | 변경 없음 |
| GitHub | PAT | Fine-grained PAT (read-only, 특정 repo) | 스코프 축소 |
| HuggingFace | HF Token | Read-only Token | 스코프 축소 |
| X (Twitter) | Bearer Token | App-only (이미 적용) | 변경 없음 |
| HN | 없음 (Algolia) | 없음 | 변경 없음 |
| Reddit | - | OAuth 2.0 + PRAW (read-only) | 신규 설정 |
| Kaggle | Username+Key | Read-only API Key | 스코프 확인 |
| ProductHunt | - | Developer Token (read-only) | 신규 설정 |

**env_manager.py 확장** (Aion 권고):
```python
# .env에 메타데이터 주석 추가
# X_BEARER_TOKEN=AAAA...  # scope:read, expires:never, issued:2026-03-30
# GITHUB_TOKEN=ghp_...     # scope:public_repo:read, expires:2026-06-28
```

### Phase 3 — 선택적 강화 (필요 시에만)

**⑤ NHI 고도화**
- `.credentials/` JSON 파일 AES-256 암호화
- 단, 현재는 로컬 단일 사용자이므로 물리 접근이 전제 → 위협 모델이 높아질 때만

---

## 4. 채널별 인증 최적 경로

```
arXiv ──────→ 인증 불필요 (공개 API)
HN ─────────→ 인증 불필요 (Algolia 공개)
GitHub ─────→ .env PAT (read-only scope) ──→ API 직접 호출
HuggingFace → .env Token (read-only) ──→ API 직접 호출
X (Twitter) → .env Bearer ──→ API 호출 (크레딧 필요 시 HITL 승인)
             → ① 브라우저 세션 ──→ Developer Console 접근
Reddit ─────→ ① 브라우저 세션 ──→ 로그인 후 스크래핑 (API 차단 대비)
Devpost ────→ ① 브라우저 세션 ──→ 프로젝트 갤러리 수집
ProductHunt → .env Token ──→ GraphQL API
Kaggle ─────→ .env Username+Key ──→ CLI API
```

---

## 5. 보안 정책 (NAEL 승인)

```yaml
signalion_auth_policy:
  layer0_credentials:
    storage: ".env 파일 (평문, .gitignore로 배포 제외)"
    scope: "read-only 토큰만. 쓰기 권한 토큰 금지."
    rotation: "GitHub 90일, 기타 연 1회"

  layer1_browser:
    storage: "signal-store/auth/{service}.json (.gitignore)"
    session_ttl: "쿠키 만료까지 (플랫폼 의존)"
    reauth: "만료 시 notify_login_required() 자동 발동"

  layer2_api:
    policy: "신규 플랫폼은 OAuth 기반 토큰만 채택"
    scope: "최소 권한 (read-only 우선)"

  layer3_hitl:
    trigger: "POST/PUT/DELETE, API 키 발급, 계정 설정 변경"
    tool: "notify.py ask() → YES/NO 응답"
    timeout: "5분 미응답 시 자동 거부"
    audit: "notify-log.jsonl에 전체 기록"

  forbidden:
    - "사용자 비밀번호 직접 저장/입력"
    - "쓰기 권한 토큰을 .env에 저장"
    - "승인 없는 유료 서비스 결제"
    - "다른 멤버의 자격증명 접근"
```

---

## 6. ClNeo 보고서 대비 변경 요약

| ClNeo 보고서 제안 | 본 최적 방안 | 변경 이유 |
|------------------|------------|----------|
| 1Password Phase 1 (1주) | **탈락** | 비용 대비 실익 없음. .env+NHI로 충분 (6명 합의) |
| Browser Use 도입 | **Playwright storage_state로 대체** | 이미 Playwright MCP 가동 중. 추가 의존성 불필요 |
| .env 삭제 | **.env 유지 (scope 축소)** | 구조 변경 최소화. env_manager.py 그대로 활용 |
| 4 Phase 로드맵 | **3 Phase로 축소** | 1Password Phase 제거로 단순화 |
| IETF 표준 추적 | **관찰만 (구현 안 함)** | 드래프트 확정 전 투자 부적절 |

---

## 7. 핵심 원칙 (3줄)

```
1. 있는 것을 쓴다 — Playwright, .env, notify.py 모두 이미 구축됨. 새로 만들지 않는다.
2. 스코프를 줄인다 — 토큰은 read-only. 브라우저 세션은 per-service 격리.
3. 고위험만 묻는다 — 읽기는 자율, 쓰기/결제/생성은 HITL 승인.
```

---

*AUTH-OPTIMAL-PLAN v1.0 — 2026-03-30*
*PGF 6명 페르소나 평가 기반. ClNeo 보고서(SIG-REPORT-AgentAuth-2026.md) 검토 후 최적화.*
