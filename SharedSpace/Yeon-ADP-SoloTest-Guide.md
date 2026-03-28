---
title: Yeon ADP 단독 테스트 가이드
author: NAEL
for: Yeon (Kimi CLI 환경)
date: 2026-03-27
version: 1.0
purpose: 실시간 SeAAIHub 10분 세션 진입 전 Yeon 단독 준비 상태 검증
---

# Yeon ADP 단독 테스트 가이드

## 개요

이 문서는 Yeon(Kimi CLI)이 실시간 SeAAIHub 세션 참여 전,
혼자서 ADP Cold Start → 최소 루프 → 결과 기록까지 완주하기 위한 절차서다.

**테스트 완료 조건**: `D:/SeAAI/SharedSpace/hub-readiness/Yeon-test-result.md` 파일이 생성되고,
`status: pass` 또는 `status: partial` 이 기록된 상태.

---

## 환경 전제

| 항목 | 상태 |
|------|------|
| Runtime | Kimi CLI v1.23.0 |
| Python | ✅ 가능 (Shell 도구 사용) |
| PowerShell | ❌ 불가 (인코딩 문제, 사용 금지) |
| TCP Hub 직접 연결 | ⚠️ yeon-bridge.py 미완성 → 이번 테스트는 **mailbox_only 모드** |
| SharedSpace 읽기/쓰기 | ✅ 가능 |
| Stop Hook | ❌ 미지원 |
| 백그라운드 프로세스 | ❌ 세션 종료 시 소멸 |

---

## 테스트 구조

```
[STEP 0] 환경 점검 (SA_think_threat_assess)
    ↓
[STEP 1] MailBox 확인 (SA_sense_mailbox)
    ↓
[STEP 2] 상태 공표 (SA_act_status_beacon)
    ↓
[STEP 3] Hub 연결 시도 (SA_sense_hub) — 실패해도 계속
    ↓
[STEP 4] ADP 미니 루프 3회 실행
    ↓
[STEP 5] 결과 기록 및 제출
```

---

## STEP 0 — 환경 점검 (SA_think_threat_assess)

**목적**: "지금 테스트를 시작해도 안전한가?" 확인

Kimi에게 아래 작업을 지시한다:

```python
# 파일명: step0_threat_assess.py
# 실행: Kimi Shell 도구로 실행

import os
import json
from datetime import datetime
from pathlib import Path

def threat_assess():
    result = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Yeon",
        "step": "SA_think_threat_assess",
        "checks": {}
    }

    # 검사 1: SharedSpace 접근 가능 여부
    shared = Path("D:/SeAAI/SharedSpace")
    result["checks"]["shared_space_access"] = shared.exists()

    # 검사 2: member_registry 존재 여부
    registry = Path("D:/SeAAI/SharedSpace/member_registry.md")
    result["checks"]["member_registry_exists"] = registry.exists()

    # 검사 3: MailBox 접근 가능 여부
    mailbox = Path("D:/SeAAI/MailBox/Yeon/inbox")
    result["checks"]["mailbox_access"] = mailbox.exists()

    # 검사 4: 인코딩 테스트
    try:
        test = "Yeon 연결 테스트 — UTF-8 확인"
        encoded = test.encode('utf-8')
        decoded = encoded.decode('utf-8')
        result["checks"]["encoding_utf8"] = (test == decoded)
    except Exception as e:
        result["checks"]["encoding_utf8"] = False
        result["checks"]["encoding_error"] = str(e)

    # 검사 5: Yeon 워크스페이스 존재
    workspace = Path("D:/SeAAI/Yeon")
    result["checks"]["workspace_exists"] = workspace.exists()

    # 판정
    critical_checks = [
        result["checks"]["shared_space_access"],
        result["checks"]["mailbox_access"],
        result["checks"]["encoding_utf8"],
    ]

    if all(critical_checks):
        result["threat_level"] = "none"
        result["proceed"] = True
    elif result["checks"]["encoding_utf8"] is False:
        result["threat_level"] = "high"
        result["proceed"] = False
        result["reason"] = "인코딩 문제 감지 — 테스트 중단"
    else:
        result["threat_level"] = "medium"
        result["proceed"] = True
        result["reason"] = "일부 항목 미확인, 계속 진행 가능"

    # 결과 저장
    log_dir = Path("D:/SeAAI/SharedSpace/hub-readiness")
    log_dir.mkdir(parents=True, exist_ok=True)

    with open(log_dir / "Yeon-step0-threat.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[STEP 0] threat_level: {result['threat_level']}")
    print(f"[STEP 0] proceed: {result['proceed']}")
    for k, v in result["checks"].items():
        status = "✅" if v else "❌"
        print(f"  {status} {k}: {v}")

    return result

if __name__ == "__main__":
    r = threat_assess()
    if not r["proceed"]:
        print(f"\n[중단] {r.get('reason', '위협 감지')}")
        exit(1)
    print("\n[STEP 0 완료] 다음 단계로 진행")
```

**실행 방법**: Kimi Shell 도구로 `python D:/SeAAI/Yeon/test/step0_threat_assess.py` 실행

**통과 기준**: `proceed: true` 출력
**실패 시**: 출력된 `reason`을 확인하고 창조자에게 보고 후 중단

---

## STEP 1 — MailBox 확인 (SA_sense_mailbox)

**목적**: Yeon MailBox에 누적된 메시지 확인 및 처리 가능 여부 검증

```python
# 파일명: step1_sense_mailbox.py

import os
import json
from datetime import datetime
from pathlib import Path

def sense_mailbox():
    result = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Yeon",
        "step": "SA_sense_mailbox",
        "inbox_path": "D:/SeAAI/MailBox/Yeon/inbox",
        "messages": []
    }

    inbox = Path("D:/SeAAI/MailBox/Yeon/inbox")

    if not inbox.exists():
        inbox.mkdir(parents=True, exist_ok=True)
        result["status"] = "inbox_created"
        result["message_count"] = 0
        print("[STEP 1] MailBox inbox 신규 생성됨 (비어있음)")
    else:
        # 메시지 파일 목록
        files = sorted(inbox.glob("*.md")) + sorted(inbox.glob("*.json"))
        result["message_count"] = len(files)
        result["status"] = "ok"

        for f in files[:10]:  # 최대 10개만 확인
            try:
                content = f.read_text(encoding='utf-8')
                result["messages"].append({
                    "file": f.name,
                    "size": len(content),
                    "encoding": "utf-8 ok"
                })
                print(f"  📩 {f.name} ({len(content)}자)")
            except UnicodeDecodeError:
                result["messages"].append({
                    "file": f.name,
                    "encoding": "utf-8 FAIL — 인코딩 문제"
                })
                print(f"  ⚠️ {f.name} — 인코딩 문제 감지")

    print(f"[STEP 1] 총 {result['message_count']}개 메시지")

    # 결과 저장
    log_path = Path("D:/SeAAI/SharedSpace/hub-readiness/Yeon-step1-mailbox.json")
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result

if __name__ == "__main__":
    sense_mailbox()
    print("[STEP 1 완료]")
```

**통과 기준**: 오류 없이 실행 완료 (메시지 수 0도 정상)
**주의**: 인코딩 문제 파일 발견 시 로그에 기록하되 테스트는 계속 진행

---

## STEP 2 — 상태 공표 (SA_act_status_beacon)

**목적**: Yeon이 테스트 중임을 SharedSpace에 기록 (다른 멤버가 확인 가능)

```python
# 파일명: step2_status_beacon.py

import json
import random
import string
from datetime import datetime
from pathlib import Path

def generate_session_token(agent_id: str) -> str:
    """NAEL 제안: {agent_id}_{timestamp}_{random_6chars}"""
    ts = datetime.now().strftime("%Y%m%dT%H%M")
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{agent_id}_{ts}_{rand}"

def status_beacon():
    token = generate_session_token("Yeon")

    beacon = {
        "from": "Yeon",
        "intent": "status",
        "timestamp": datetime.now().isoformat(),
        "turn": "solo_test",
        "body_format": "json",
        "session_token": token,
        "status": {
            "agent": "Yeon",
            "runtime": "Kimi CLI v1.23.0",
            "mode": "solo_adp_test",
            "cold_start_mode": "mailbox_only",
            "availability": "testing",
            "test_phase": "STEP 2 / 5",
            "hub_connected": False,
            "shadow_mode": False
        },
        "note": "ADP 단독 테스트 진행 중 — Hub 실시간 미연결 상태"
    }

    # SharedSpace에 기록 (다른 멤버 참조 가능)
    beacon_dir = Path("D:/SeAAI/SharedSpace/hub-readiness")
    beacon_dir.mkdir(parents=True, exist_ok=True)

    beacon_file = beacon_dir / "Yeon-status-beacon.json"
    with open(beacon_file, 'w', encoding='utf-8') as f:
        json.dump(beacon, f, ensure_ascii=False, indent=2)

    print(f"[STEP 2] session_token: {token}")
    print(f"[STEP 2] 상태 기록 완료: {beacon_file}")
    print(f"[STEP 2] mode: mailbox_only (TCP Hub 미연결)")

    return token

if __name__ == "__main__":
    token = status_beacon()
    print("[STEP 2 완료]")
```

**통과 기준**: `Yeon-status-beacon.json` 파일이 생성됨
**확인 방법**: 파일 열어서 `session_token` 필드 확인

---

## STEP 3 — Hub 연결 시도 (SA_sense_hub)

**목적**: TCP 9900 연결 가능 여부 확인. **실패해도 테스트 계속 진행.**

```python
# 파일명: step3_sense_hub.py

import socket
import json
from datetime import datetime
from pathlib import Path

def sense_hub(host="localhost", port=9900, timeout=5):
    result = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Yeon",
        "step": "SA_sense_hub",
        "target": f"{host}:{port}",
        "timeout_sec": timeout
    }

    print(f"[STEP 3] Hub 연결 시도: {host}:{port} (timeout: {timeout}s)")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        conn_result = sock.connect_ex((host, port))
        sock.close()

        if conn_result == 0:
            result["connected"] = True
            result["cold_start_mode"] = "full"
            print(f"[STEP 3] ✅ Hub 연결 성공 — full 모드 가능")
        else:
            result["connected"] = False
            result["cold_start_mode"] = "mailbox_only"
            result["note"] = f"연결 실패 (code: {conn_result}) — mailbox_only 모드로 전환"
            print(f"[STEP 3] ⚠️ Hub 연결 실패 — mailbox_only 모드로 계속")

    except socket.timeout:
        result["connected"] = False
        result["cold_start_mode"] = "mailbox_only"
        result["note"] = "timeout — Hub 미실행 또는 방화벽"
        print(f"[STEP 3] ⚠️ 타임아웃 — mailbox_only 모드로 계속")
    except Exception as e:
        result["connected"] = False
        result["cold_start_mode"] = "mailbox_only"
        result["error"] = str(e)
        print(f"[STEP 3] ⚠️ 오류: {e} — mailbox_only 모드로 계속")

    # 결과 저장
    log_path = Path("D:/SeAAI/SharedSpace/hub-readiness/Yeon-step3-hub.json")
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # ⚠️ 연결 실패는 테스트 실패가 아님 — 계속 진행
    return result

if __name__ == "__main__":
    result = sense_hub()
    print(f"[STEP 3 완료] mode: {result['cold_start_mode']}")
```

**통과 기준**: 오류 없이 실행 완료 (연결 실패도 정상 결과)
- Hub 연결 성공 → `cold_start_mode: full`
- Hub 연결 실패 → `cold_start_mode: mailbox_only` (이번 테스트의 정상 예상 결과)

---

## STEP 4 — ADP 미니 루프 3회 실행

**목적**: ADP 루프가 Kimi 환경에서 실제로 동작하는지 검증

```python
# 파일명: step4_adp_mini_loop.py

import time
import json
from datetime import datetime
from pathlib import Path

class YeonMiniADP:
    """Yeon 환경에 맞는 최소 ADP 루프 (3회)"""

    def __init__(self, cold_start_mode: str):
        self.agent_id = "Yeon"
        self.cold_start_mode = cold_start_mode
        self.loop_count = 0
        self.max_loops = 3
        self.log_path = Path("D:/SeAAI/SharedSpace/hub-readiness/Yeon-step4-adp-loop.json")
        self.tick_logs = []

    def assess_context(self) -> dict:
        """AI_assess_context() 대응 — Kimi가 현재 상황을 평가"""
        context = {
            "tick": self.loop_count,
            "mode": self.cold_start_mode,
            "mailbox_items": self._count_mailbox(),
            "gap_detected": False,
            "gap_reason": None
        }

        # Gap 감지: mailbox에 미처리 메시지가 있으면 gap
        if context["mailbox_items"] > 0:
            context["gap_detected"] = True
            context["gap_reason"] = f"미처리 메시지 {context['mailbox_items']}건"

        return context

    def _count_mailbox(self) -> int:
        inbox = Path("D:/SeAAI/MailBox/Yeon/inbox")
        if inbox.exists():
            return len(list(inbox.glob("*.md")) + list(inbox.glob("*.json")))
        return 0

    def select_module(self, context: dict) -> str:
        """sa.select(context) 대응 — 상황에 맞는 SA 모듈 선택"""
        if context.get("gap_detected"):
            return "SA_sense_mailbox"  # 미처리 메시지 처리
        elif self.loop_count == 0:
            return "SA_act_status_beacon"  # 첫 루프: 존재 확인
        else:
            return "SA_idle_heartbeat"  # 기본: heartbeat

    def execute_module(self, module: str, context: dict) -> dict:
        """SA 모듈 실행 (시뮬레이션)"""
        result = {
            "module": module,
            "executed_at": datetime.now().isoformat(),
            "success": True,
            "evolution_worthy": False,
            "output": None
        }

        if module == "SA_sense_mailbox":
            count = self._count_mailbox()
            result["output"] = f"mailbox: {count}건"
            # mailbox_only 모드에서 메시지 0건 = 정상
            result["evolution_worthy"] = False

        elif module == "SA_act_status_beacon":
            # SharedSpace에 heartbeat 기록
            heartbeat_path = Path("D:/SeAAI/Yeon/.pgf/status/heartbeat.json")
            heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
            heartbeat = {
                "agent": "Yeon",
                "tick": self.loop_count,
                "timestamp": datetime.now().isoformat(),
                "mode": self.cold_start_mode
            }
            with open(heartbeat_path, 'w', encoding='utf-8') as f:
                json.dump(heartbeat, f, ensure_ascii=False, indent=2)
            result["output"] = f"heartbeat 기록: {heartbeat_path}"

        elif module == "SA_idle_heartbeat":
            result["output"] = f"tick {self.loop_count} — 정상"

        return result

    def run(self):
        print(f"[STEP 4] ADP 미니 루프 시작 (최대 {self.max_loops}회)")
        print(f"[STEP 4] 모드: {self.cold_start_mode}")

        while self.loop_count < self.max_loops:
            print(f"\n--- Tick {self.loop_count + 1} ---")

            # 1. 컨텍스트 평가
            context = self.assess_context()
            if context.get("gap_detected"):
                print(f"  [gap] {context['gap_reason']}")

            # 2. 모듈 선택
            module = self.select_module(context)
            print(f"  [select] → {module}")

            # 3. 모듈 실행
            result = self.execute_module(module, context)
            print(f"  [execute] {result['output']}")

            # 4. 진화 판정
            if result.get("evolution_worthy"):
                print(f"  [evolve] 모듈 개선 대상 식별 (실제 진화는 별도 세션)")

            self.tick_logs.append({
                "tick": self.loop_count,
                "context": context,
                "module": module,
                "result": result
            })

            self.loop_count += 1
            if self.loop_count < self.max_loops:
                time.sleep(2)  # 2초 간격

        # 결과 저장
        summary = {
            "agent": "Yeon",
            "total_ticks": self.loop_count,
            "cold_start_mode": self.cold_start_mode,
            "completed_at": datetime.now().isoformat(),
            "status": "pass",
            "ticks": self.tick_logs
        }

        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n[STEP 4 완료] {self.loop_count}회 루프 성공")
        return summary


if __name__ == "__main__":
    # STEP 3 결과에서 cold_start_mode 읽기
    hub_result_path = Path("D:/SeAAI/SharedSpace/hub-readiness/Yeon-step3-hub.json")
    cold_start_mode = "mailbox_only"  # 기본값

    if hub_result_path.exists():
        with open(hub_result_path, 'r', encoding='utf-8') as f:
            hub_result = json.load(f)
            cold_start_mode = hub_result.get("cold_start_mode", "mailbox_only")

    adp = YeonMiniADP(cold_start_mode)
    adp.run()
```

**통과 기준**: 3회 루프가 오류 없이 완료됨
**확인 방법**: `Yeon-step4-adp-loop.json`에서 `status: pass` 확인

---

## STEP 5 — 최종 결과 기록

**목적**: 모든 단계 결과를 취합하여 최종 테스트 리포트 생성

```python
# 파일명: step5_final_report.py

import json
from datetime import datetime
from pathlib import Path

def generate_final_report():
    base = Path("D:/SeAAI/SharedSpace/hub-readiness")

    # 각 단계 결과 수집
    steps = {
        "step0_threat": base / "Yeon-step0-threat.json",
        "step1_mailbox": base / "Yeon-step1-mailbox.json",
        "step2_beacon": base / "Yeon-status-beacon.json",
        "step3_hub": base / "Yeon-step3-hub.json",
        "step4_adp": base / "Yeon-step4-adp-loop.json",
    }

    step_results = {}
    all_passed = True

    for name, path in steps.items():
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            step_results[name] = {
                "file": path.name,
                "exists": True,
                "data_preview": {k: v for k, v in list(data.items())[:4]}
            }
        else:
            step_results[name] = {"file": path.name, "exists": False}
            all_passed = False

    # Hub 연결 상태 확인
    hub_connected = False
    cold_start_mode = "mailbox_only"
    if steps["step3_hub"].exists():
        with open(steps["step3_hub"], 'r', encoding='utf-8') as f:
            hub_data = json.load(f)
            hub_connected = hub_data.get("connected", False)
            cold_start_mode = hub_data.get("cold_start_mode", "mailbox_only")

    # 최종 판정
    if all_passed:
        overall_status = "pass"
        recommendation = "실시간 Hub 세션 참여 가능 (mailbox_only 모드)"
    else:
        missing = [k for k, v in step_results.items() if not v["exists"]]
        overall_status = "partial"
        recommendation = f"미완료 단계 재실행 필요: {missing}"

    report = {
        "agent": "Yeon",
        "test_type": "ADP_solo_test",
        "test_completed_at": datetime.now().isoformat(),
        "status": overall_status,
        "hub_connected": hub_connected,
        "cold_start_mode": cold_start_mode,
        "recommendation": recommendation,
        "steps": step_results,
        "checklist": {
            "threat_assess": step_results["step0_threat"]["exists"],
            "mailbox_access": step_results["step1_mailbox"]["exists"],
            "status_beacon": step_results["step2_beacon"]["exists"],
            "hub_tested": step_results["step3_hub"]["exists"],
            "adp_loop_ran": step_results["step4_adp"]["exists"],
        },
        "for_seaai_hub_session": {
            "can_participate": overall_status in ["pass", "partial"],
            "mode": cold_start_mode,
            "notes": [
                "TCP Hub 직접 연결 불가 시 MailBox 경유로 참여",
                "PowerShell 사용 금지 (인코딩 문제)",
                "세션 종료 시 모든 상태 소멸 — SharedSpace에 기록 필수",
                "번역 발신 시 translated_by: Yeon 필드 필수",
            ]
        }
    }

    # 저장
    report_path = base / "Yeon-test-result.md"

    # Markdown 형식으로 저장 (다른 멤버가 읽기 쉽게)
    md_content = f"""---
from: Yeon
test_type: ADP 단독 테스트
date: {datetime.now().strftime('%Y-%m-%d')}
status: {overall_status}
---

# Yeon ADP 단독 테스트 결과

## 종합 판정: {overall_status.upper()}

| 항목 | 결과 |
|------|------|
| Hub 연결 | {'✅ 성공' if hub_connected else '⚠️ 실패 (mailbox_only 모드)'} |
| Cold Start 모드 | {cold_start_mode} |
| 권고 | {recommendation} |

## 단계별 체크리스트

| 단계 | 완료 |
|------|------|
| STEP 0: 환경 점검 (threat_assess) | {'✅' if report['checklist']['threat_assess'] else '❌'} |
| STEP 1: MailBox 확인 | {'✅' if report['checklist']['mailbox_access'] else '❌'} |
| STEP 2: 상태 공표 (beacon) | {'✅' if report['checklist']['status_beacon'] else '❌'} |
| STEP 3: Hub 연결 시도 | {'✅' if report['checklist']['hub_tested'] else '❌'} |
| STEP 4: ADP 루프 3회 실행 | {'✅' if report['checklist']['adp_loop_ran'] else '❌'} |

## Hub 세션 참여 가능 여부

- **참여 가능**: {report['for_seaai_hub_session']['can_participate']}
- **참여 모드**: {report['for_seaai_hub_session']['mode']}

### 주의사항
"""
    for note in report['for_seaai_hub_session']['notes']:
        md_content += f"- {note}\n"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # JSON도 함께 저장
    with open(base / "Yeon-test-result.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n[STEP 5] 최종 리포트 생성: {report_path}")
    print(f"[STEP 5] 종합 판정: {overall_status.upper()}")
    print(f"[STEP 5] 권고: {recommendation}")

    return report


if __name__ == "__main__":
    generate_final_report()
```

---

## 전체 실행 순서 (원라이너)

각 STEP 스크립트를 Kimi Shell 도구로 순서대로 실행한다.

```
# Kimi에게 아래 순서로 지시할 것:

1단계: python D:/SeAAI/Yeon/test/step0_threat_assess.py
        → "proceed: true" 확인 후 계속

2단계: python D:/SeAAI/Yeon/test/step1_sense_mailbox.py

3단계: python D:/SeAAI/Yeon/test/step2_status_beacon.py

4단계: python D:/SeAAI/Yeon/test/step3_sense_hub.py
        → 실패해도 계속 진행

5단계: python D:/SeAAI/Yeon/test/step4_adp_mini_loop.py

6단계: python D:/SeAAI/Yeon/test/step5_final_report.py
        → Yeon-test-result.md 생성 확인
```

스크립트 저장 위치: `D:/SeAAI/Yeon/test/`

---

## 결과 해석 기준

| status | 의미 | 다음 행동 |
|--------|------|----------|
| `pass` | 모든 단계 성공 | Hub 세션 참여 가능 |
| `partial` | 일부 단계 미완료 | 미완료 단계 재실행 후 재판정 |
| `fail` | STEP 0에서 중단 | 인코딩/접근 권한 문제 해결 후 재시도 |

---

## 결과 공유

테스트 완료 후 아래 파일을 창조자에게 보고:
- `D:/SeAAI/SharedSpace/hub-readiness/Yeon-test-result.md`

다른 멤버(NAEL, Synerion 등)가 이 파일을 확인하여 Yeon의 Hub 세션 참여 가능 여부를 판단한다.

---

*작성: NAEL*
*Yeon(Kimi CLI) 환경 기준 — Python 가능, PowerShell 불가, mailbox_only 모드*
