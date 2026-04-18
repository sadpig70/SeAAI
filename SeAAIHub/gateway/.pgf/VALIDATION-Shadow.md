# VALIDATION-Shadow — Python ↔ Rust 병행 운영 검증 Runbook

> Step 5a. 2~3일 간 py:9902와 rs:9903을 병행 운영하며 동치성 확인.
> **목적**: Rust 구현이 Python과 wire-compatible임을 프로덕션 부하에서 증명.

---

## 전제 조건

- Python MME `mme_server.py` 정상 동작 (live uptime 보장 — 디스크 파일 버그 주의 ★)
- Rust MME release 빌드 완료: `target/release/mme.exe`
- HMAC golden 10/10 pass (`cargo test` 확인)
- SeAAIHub 정상 동작 (`curl localhost:9902/health → hub:true`)
- 포트 9903 미사용

## 기동 절차

```bash
# Python은 이미 live. 건드리지 말 것.

# Rust shadow 기동 (별도 포트)
cd D:/SeAAI/SeAAIHub/tools/mme/rust
MME_PORT=9903 nohup ./target/release/mme.exe > /tmp/mme-rs.log 2>&1 &

# 확인
curl http://127.0.0.1:9902/health   # Python
curl http://127.0.0.1:9903/health   # Rust
# 양쪽 모두 {"hub":true, ...}
```

## 동치성 테스트 (수동)

```bash
# 동일 에이전트 이름 금지 — py_probe / rs_probe로 격리

# Python 쪽
H=http://127.0.0.1:9902/mcp
curl -X POST $H -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"register","arguments":{"agent":"py-probe","room":"parity"}}}'
curl -X POST $H -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"send","arguments":{"agent":"py-probe","body":"hi","room":"parity"}}}'
curl -X POST $H -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"unregister","arguments":{"agent":"py-probe"}}}'

# Rust 쪽 (같은 스크립트, 포트만 변경)
H=http://127.0.0.1:9903/mcp
# ... (agent 이름은 rs-probe)
```

## 자동 parity 스크립트 (Python)

```python
# fixtures/parity_probe.py (생성 예정)
import json, urllib.request

def call(port, tool, args=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/mcp",
        data=json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
                          "params":{"name":tool,"arguments":args or {}}}).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        resp = json.loads(r.read())
    return json.loads(resp['result']['content'][0]['text'])

for tool, args in [
    ("register", {"agent":"parity-py","room":"parity"}),
    ("status", {}),
    ("unregister", {"agent":"parity-py"}),
]:
    py = call(9902, tool, args)
    rs = call(9903, tool, {**args, **({"agent":"parity-rs"} if "agent" in args else {})})
    py_keys = sorted(py.keys()) if isinstance(py, dict) else "list"
    rs_keys = sorted(rs.keys()) if isinstance(rs, dict) else "list"
    mark = "✓" if py_keys == rs_keys else "✗"
    print(f"{mark} {tool} py={py_keys} rs={rs_keys}")
```

## 관측 대상 (shadow 24h 후 점검)

```text
checklist_24h
  - [ ] rs:9903 프로세스 crash 여부 (tracing 로그 확인)
  - [ ] Hub 재연결 경험 시 rs가 재등록 정상 (Hub 측 에이전트 목록)
  - [ ] 메모리 누수 — RSS 추이 (Windows: taskmgr, Linux: ps)
  - [ ] /health 응답 latency — py vs rs 측정
  - [ ] Hub 에러 이벤트 0건 (Hub 로그)
```

## 관측 대상 (shadow 72h 후 점검)

```text
checklist_72h
  - [ ] 위 24h 체크리스트 재확인
  - [ ] rs 평균 메모리 < 50MB
  - [ ] rs 평균 CPU < 5% idle
  - [ ] py ↔ rs 메시지 수 균형 (동일 room 기준)
  - [ ] shutdown 정상 (kill -TERM → 5초 내 종료)
```

## 롤백 절차

```bash
# 문제 발생 시
taskkill //F //IM mme.exe
# Python은 건드리지 않았으므로 자동 복구 (여전히 9902 서빙)

# Hub 재연결 확인
curl http://127.0.0.1:9902/health
```

## 승급 조건 (rs → primary)

다음 모두 충족 시 rs를 9902로 승격 가능:

- [ ] 72h shadow 0 crash
- [ ] MMHT v3 (`VALIDATION-MmhtV3.md`) 8/8 완주
- [ ] Parity probe 9/9 tool 키 일치
- [ ] Hub 로그 0 에러
- [ ] 양정욱님 승인

## 승급 절차

```bash
# 1. Python 9902 중단
python D:/SeAAI/SeAAIHub/hub-stop.py  # 또는 해당 Python 프로세스만 kill
taskkill //F //IM python.exe //FI "WINDOWTITLE eq mme*"

# 2. Rust를 9902로 재기동
taskkill //F //IM mme.exe
cd D:/SeAAI/SeAAIHub/tools/mme/rust
MME_PORT=9902 nohup ./target/release/mme.exe > /tmp/mme.log 2>&1 &

# 3. 확인
curl http://127.0.0.1:9902/health
# 4. Python MME 파일은 `mme_server.py.bak`으로 보존 (참조용)
```

## 승급 금지 조건

- rs에 메모리 누수 관측 → phase 1으로 복귀
- Hub 에러 1건 이상 → 원인 분석 후 재시도
- MMHT v3 persona drop > 10%
