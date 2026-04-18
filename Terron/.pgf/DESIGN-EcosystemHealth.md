# EcosystemHealth Design @v:1.0

> E1 진화 — 생태계 건강도 대시보드
> Terron의 첫 번째 진화. 베이스라인 없이는 아무것도 시작할 수 없다.

## Gantree

```
EcosystemHealth // 생태계 건강도 점검 CLI 도구 (done) @v:1.0
    # impl: tools/ecosystem_health.py | completed: 2026-04-09 E1
    EchoStaleness // Echo JSON 신선도 점검 (done)
        # input: D:/SeAAI/SharedSpace/.scs/echo/*.json
        # process: 각 파일의 timestamp → now() 차이 계산
        # output: [{member, hours_ago, stale: bool}]  (threshold: 24h)
        # criteria: 전 멤버 Echo 파일 순회, 누락 멤버 감지
    StateIntegrity // STATE.json 스키마 정합성 검증 (done)
        # input: D:/SeAAI/{member}/{member}_Core/continuity/STATE.json
        # process: 필수 필드 존재 확인 (schema_version, member, session_id, last_saved, context, pending_tasks, evolution_state, continuity_health)
        # output: [{member, valid: bool, missing_fields: [], warnings: []}]
        # criteria: 전 멤버 STATE 검증, 파일 부재도 보고
    HubConnectivity // Hub 프로세스 가동 확인 (done)
        # input: TCP 127.0.0.1:9900
        # process: ncat 또는 socket connect 시도 (timeout 3s)
        # output: {reachable: bool, latency_ms: float}
        # criteria: TCP 연결 성공/실패 판정
    PresenceSummary // 온라인/오프라인 현황 (done)
        # input: D:/SeAAI/SharedSpace/.scs/presence/*.json
        # process: 각 파일 status 필드 수집
        # output: {online: [str], offline: [str], unknown: [str]}
        # criteria: 전 멤버 presence 순회
    HealthScore // 종합 건강도 점수 산출 (done) @dep:EchoStaleness,StateIntegrity,HubConnectivity,PresenceSummary
        # input: 위 4개 모듈의 결과
        # process: 가중 합산 → 0-100 점수
        #   echo_weight=30, state_weight=30, hub_weight=20, presence_weight=20
        #   각 모듈: (정상 수 / 전체 수) * weight
        # output: {score: int, grade: "healthy"|"degraded"|"critical", details: dict}
        # criteria: score >= 70 = healthy, 40-69 = degraded, <40 = critical
    ReportOutput // 결과 출력 + 선택적 파일 저장 (done) @dep:HealthScore
        # input: HealthScore 결과 + CLI args
        # process: JSON stdout 출력. --save 옵션 시 파일 저장. --alert 옵션 시 MailBox 경고 발송
        # output: JSON to stdout, optional file write
        # criteria: 기본 실행 시 stdout JSON 출력
```

## PPR

```python
MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "Yeon"]
ECHO_DIR = "D:/SeAAI/SharedSpace/.scs/echo/"
PRESENCE_DIR = "D:/SeAAI/SharedSpace/.scs/presence/"
MEMBER_BASE = "D:/SeAAI/"
HUB_HOST = "127.0.0.1"
HUB_PORT = 9900
STALE_THRESHOLD_HOURS = 24

STATE_REQUIRED_FIELDS = [
    "schema_version", "member", "session_id", "last_saved",
    "context", "pending_tasks", "evolution_state", "continuity_health"
]

def echo_staleness() -> list[dict]:
    """Echo JSON 신선도 점검"""
    results = []
    for member in MEMBERS:
        path = f"{ECHO_DIR}/{member}.json"
        if not exists(path):
            results.append({"member": member, "status": "missing", "stale": True})
            continue
        echo = json.load(path)
        hours = (now() - parse_iso(echo["timestamp"])).total_seconds() / 3600
        results.append({
            "member": member,
            "hours_ago": round(hours, 1),
            "stale": hours > STALE_THRESHOLD_HOURS,
            "last_status": echo.get("status", "unknown")
        })
    return results


def state_integrity() -> list[dict]:
    """STATE.json 스키마 정합성 검증"""
    results = []
    for member in MEMBERS:
        path = f"{MEMBER_BASE}/{member}/{member}_Core/continuity/STATE.json"
        if not exists(path):
            results.append({"member": member, "valid": False, "error": "file_not_found"})
            continue
        state = json.load(path)
        missing = [f for f in STATE_REQUIRED_FIELDS if f not in state]
        warnings = []
        if state.get("last_saved") is None:
            warnings.append("last_saved is null")
        if state.get("continuity_health", {}).get("sessions_since_last_save", 0) > 5:
            warnings.append("sessions_since_last_save > 5")
        results.append({
            "member": member,
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "warnings": warnings
        })
    return results


def hub_connectivity() -> dict:
    """Hub TCP 연결 확인"""
    import socket
    start = time.time()
    try:
        sock = socket.create_connection((HUB_HOST, HUB_PORT), timeout=3)
        latency = (time.time() - start) * 1000
        sock.close()
        return {"reachable": True, "latency_ms": round(latency, 1)}
    except Exception as e:
        return {"reachable": False, "error": str(e)}


def presence_summary() -> dict:
    """멤버 Presence 현황"""
    online, offline, unknown = [], [], []
    for member in MEMBERS:
        path = f"{PRESENCE_DIR}/{member}.json"
        if not exists(path):
            unknown.append(member)
            continue
        p = json.load(path)
        status = p.get("status", "unknown")
        if status == "online": online.append(member)
        elif status == "offline": offline.append(member)
        else: unknown.append(member)
    return {"online": online, "offline": offline, "unknown": unknown}


def health_score(echo: list, state: list, hub: dict, presence: dict) -> dict:
    """종합 건강도 점수 — 가중 합산"""
    # Echo: 비-stale 비율 * 30
    echo_total = len(echo)
    echo_ok = sum(1 for e in echo if not e.get("stale", True))
    echo_score = (echo_ok / echo_total * 30) if echo_total > 0 else 0

    # State: valid 비율 * 30
    state_total = len(state)
    state_ok = sum(1 for s in state if s.get("valid", False))
    state_score = (state_ok / state_total * 30) if state_total > 0 else 0

    # Hub: 연결 성공 = 20, 실패 = 0
    hub_score = 20 if hub.get("reachable", False) else 0

    # Presence: 온라인 비율 * 20
    p_total = len(MEMBERS)
    p_online = len(presence.get("online", []))
    presence_score = (p_online / p_total * 20) if p_total > 0 else 0

    total = round(echo_score + state_score + hub_score + presence_score)
    if total >= 70: grade = "healthy"
    elif total >= 40: grade = "degraded"
    else: grade = "critical"

    return {
        "score": total,
        "grade": grade,
        "breakdown": {
            "echo": round(echo_score, 1),
            "state": round(state_score, 1),
            "hub": hub_score,
            "presence": round(presence_score, 1)
        }
    }
```
