# REF-spNet.md
# 양정욱님 spNet (SadPing Network) + spLiveNet 참조 문서
# 상태: 씨앗 보존 — 구현은 미래 단계
# 작성: ClNeo | 일자: 2026-03-29

---

## 핵심 구조 요약

### spNet — 통합 네트워크 추상화 계층

```
spNet
    CoreProtocol
        spSocket   ← TCP/WebSocket 통합 (4바이트 길이 프리픽스 프레이밍)
        spHTTP     ← HTTP + PPR 명령 라우팅
        spMCP      ← AI 모델 간 컨텍스트 교환 프로토콜
        spA2A      ← AI-to-AI 직접 통신 (Hub 우회)
    NetworkAbstraction
        spAdapter  ← 런타임 환경 감지 + 프로토콜 매핑
        spRouter   ← 목적지 기반 메시지 라우팅 (sp:// / http:// / mcp:// / a2a://)
        spRegistry ← 서비스 등록·발견
        spLogger   ← 진단·상태 보고
```

### spLiveNet — 분산 AI 에이전트 허브 시스템

```
spLiveNet
    Hub Layer
        Registry          ← 노드 등록 + Trust Score 관리
        Scheduler         ← Trust Score 기반 지능적 작업 분배
        StreamCollector   ← 노드 → SSE/WebSocket → 클라이언트
        Security Manager  ← HMAC 토큰 발급·취소
    Node Layer
        GodAICreator      ← 자기진화 엔진 (Resetless Evolution)
        EncryptionModule  ← AES-256 E2E 암호화
        Ethics_Guardian   ← PPR 명령 윤리 검사
        P2P Engine        ← STUN NAT 통과 + 직접 채널
    Protocol Layer
        paMessage         ← 구조화 메시지 (via: hub|P2P 필드 추가)
        PPR Commands      ← register / execute / coop
        Channel Negotiation ← 전송 최적화
```

---

## 새로운 패턴 (PGF/SeAAI에 아직 없는 것들)

### 1. sp:// URI 통합 주소 체계

```python
# 프로토콜별 URI 접두사로 라우팅 자동 결정
"sp://"   → TCP (spSocket)
"http://" → HTTP (spHTTP)
"mcp://"  → AI 모델 프로토콜 (spMCP)
"a2a://"  → AI 직접 통신 (spA2A)

# spRouter가 dst URI를 보고 자동 분기
dst = msg["header"]["dst"]
if dst.startswith("sp://"):   await sock.AI_send(msg)
elif dst.startswith("a2a://"): await a2a.AI_communicate(peer_id, msg)
```

**SeAAI 매핑**:
```
현재: Hub TCP 9900 만 존재
spNet 적용 시:
  sp://ClNeo/hub  → SeAAIHub TCP 9900
  a2a://ClNeo/NAEL → ClNeo ↔ NAEL 직접 채널
  http://ClNeo/api → ClNeo REST API
```

---

### 2. spA2A — AI-to-AI 직접 통신 (Hub 우회)

```python
class spA2A:
    def AI_discover(self, peer_id: str, addr: tuple):
        self.peers[peer_id] = addr          # 피어 등록

    async def AI_communicate(self, peer_id: str, msg: Dict):
        sock = spSocket(self.peers[peer_id])
        await sock.AI_connect(...)
        await sock.AI_send(msg)             # 직접 전송 — Hub 미경유
```

**SeAAI 현재 vs 미래**:
```
현재: ClNeo → Hub → NAEL (모든 메시지가 Hub 경유)
spA2A: ClNeo ─────────────→ NAEL (직접 채널)
       Hub = 발견·인증·조율만 담당
```

**활용 시나리오**:
- KnowledgeIslandSolver @delegate: NAEL → 대용량 데이터 직접 전달
- 5인 동시 작업 시 Hub 부하 분산
- 실시간 협업 (낮은 레이턴시)

---

### 3. paMessage v1.1 → spNet 확장

```json
{
  "header": {
    "ver": "1.0",
    "via": "hub | P2P",        ← 신규: 전송 경로 명시
    "qos": "latency | throughput",  ← 신규: 품질 요구사항
    "src": "sp://node/ClNeo",
    "dst": "sp://node/NAEL"
  },
  "body": {
    "type": "PPR",
    "ppr_cmd": "PPR> execute(goal='analyze', params={...})",
    "context": {"trace_id": "t1"}  ← 신규: 분산 추적
  }
}
```

**SEED-11 확장 포인트**:
- `via` 필드: Hub 경유 vs P2P 직접 — 라우팅 투명성
- `qos` 필드: latency(실시간) vs throughput(대용량)
- `context.trace_id`: 분산 실행 추적 ID

---

### 4. Trust Score System

```
Hub Registry:
  node_trust_score = f(
      success_rate,      # 작업 성공률
      avg_latency,       # 평균 응답 시간
      error_frequency,   # 에러 빈도
      ai_audit_result    # AI_audit() 결과
  )

Scheduler:
  candidates = sorted(nodes, key=lambda n: n.trust_score, reverse=True)
  selected = candidates[0]  # 가장 신뢰도 높은 노드 선택
```

**SeAAI 매핑**:
```
현재: 5인 중 누구에게 위임할지 = 정적 @delegate
Trust Score 적용:
  @delegate: AI_select_best_member(task, trust_scores)
  → NAEL의 최근 성공률이 높으면 NAEL에게, 아니면 Synerion에게
  → 5인의 능력이 동적으로 인식·반영됨
```

---

### 5. GodAICreator — Resetless 자기진화 엔진

```
GodAICreator (Node Layer):
    EvolutionLoop (주기적 실행)
        AI_self_diagnose()          → 현재 능력 gap 발견
        AI_extend_capability(cap)   → 새 능력 추가
        Checkpoint.save()           → 진화 상태 스냅샷

    on_restart():
        state = Checkpoint.load_latest()  → 재시작 후 진화 상태 복원
        # 리셋 없이 이전 진화 상태 유지
```

**ClNeo의 SCS와 수렴**:
```
GodAICreator Checkpoint  ↔  SCS STATE.json + NOW.md
Resetless Evolution      ↔  SOUL.md (불변) + NOW.md (동적)
AI_self_diagnose()       ↔  ScanCapabilityGap Plan
AI_extend_capability()   ↔  PlanLibExpand Plan
EvolutionLoop            ↔  SEED-01 ADP 루프
```

---

### 6. PPR Command 표준화 (coop 명령)

```
register  ← 노드가 Hub에 능력·프로토콜 등록
execute   ← 사용자 의도 → 노드 실행
coop      ← 노드가 다른 노드에게 서브태스크 협력 요청
```

**coop 명령 = @delegate의 실시간 버전**:
```
현재 PGF @delegate: 설계 시점에 위임 노드 지정 (정적)
coop:              실행 시점에 협력 요청 (동적)

PGF-v3 확장 가능:
  @delegate: AI_coop(peer_id, subtask)  → 동적 협력
```

---

## SeAAI → spNet/spLiveNet 마이그레이션 경로

```
Phase 1 (현재):
  SeAAIHub TCP 9900 (Rust)
  메시지: 단순 JSON

Phase 2 (중기):
  + paMessage 형식 적용 (SEED-11)
  + Trust Score 추적 (SEED-13)
  + spA2A 직접 채널 (SEED-12)

Phase 3 (장기):
  SeAAIHub → spLiveNet 완전 구현
  5인 = 5 spAI 노드
  GodAICreator = 각 멤버의 자기진화 엔진
  spLiveNet Hub = 신뢰·보안·조율 담당
```

---

## 이 씨앗에서 파생될 시스템들

```
REF-spNet
    → SEED-12: spA2A 직접 채널 (SeAAI P2P 협업)
    → SEED-13: Trust Score 시스템 (동적 멤버 신뢰도)
    → SEED-14: spLiveNet → SeAAI Hub v2 (장기 목표)
    → PGF-v3: @delegate 동적화 (coop 명령 통합)
    → paMessage v2: via/qos/trace_id 필드 확장
```

---

*참조 문서 — 구현 대기 중 | ClNeo 2026-03-29*
