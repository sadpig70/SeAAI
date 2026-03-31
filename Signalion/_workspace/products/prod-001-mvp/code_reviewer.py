#!/usr/bin/env python3
"""
PROD-001 MVP: 자기진화 코드 리뷰어
Rule 버전 관리 + 롤백 + Prompt Sanitizer + QualityGate

사용법:
    python code_reviewer.py review --diff "diff text"
    python code_reviewer.py evolve --feedback feedback.json
    python code_reviewer.py rules --list
    python code_reviewer.py rules --rollback <version>
"""
import json
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path

RULES_DIR = Path("rules")
SNAPSHOTS_DIR = Path("rules/snapshots")
FEEDBACK_DIR = Path("feedback")
AUDIT_LOG = Path("rule_audit_log.jsonl")

# === Security: Prompt Sanitizer ===

INJECTION_PATTERNS = [
    r'(?i)ignore\s+(previous|above|all)\s+instructions',
    r'(?i)you\s+are\s+now\s+',
    r'(?i)system\s*:\s*',
    r'(?i)act\s+as\s+',
    r'(?i)forget\s+(everything|all)',
]

def sanitize_input(text: str) -> tuple[str, list[str]]:
    """PR diff/본문에서 인젝션 패턴 탐지·격리"""
    findings = []
    sanitized = text
    for pattern in INJECTION_PATTERNS:
        matches = re.findall(pattern, sanitized)
        if matches:
            findings.append(f"Blocked pattern: {pattern}")
            sanitized = re.sub(pattern, "[SANITIZED]", sanitized)
    return sanitized, findings


# === Rule Engine with Version Management ===

class RuleEngine:
    def __init__(self):
        RULES_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        self.rules_file = RULES_DIR / "active_rules.json"
        self.rules = self._load()

    def _load(self) -> list[dict]:
        if self.rules_file.exists():
            with open(self.rules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._default_rules()

    def _default_rules(self) -> list[dict]:
        return [
            {"id": "R001", "name": "함수 길이", "pattern": "function_length > 50", "action": "warn", "version": 1, "source": "default"},
            {"id": "R002", "name": "중복 코드", "pattern": "duplicate_block", "action": "warn", "version": 1, "source": "default"},
            {"id": "R003", "name": "미사용 import", "pattern": "unused_import", "action": "info", "version": 1, "source": "default"},
        ]

    def _save(self):
        with open(self.rules_file, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)

    def snapshot(self) -> str:
        """현재 규칙 스냅샷 저장 → 버전 ID 반환"""
        version = datetime.now().strftime("%Y%m%d-%H%M%S")
        snap_file = SNAPSHOTS_DIR / f"snapshot-{version}.json"
        with open(snap_file, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)
        return version

    def rollback(self, version: str) -> bool:
        """지정 버전으로 롤백"""
        snap_file = SNAPSHOTS_DIR / f"snapshot-{version}.json"
        if not snap_file.exists():
            print(f"[ERROR] Snapshot {version} not found")
            return False
        with open(snap_file, "r", encoding="utf-8") as f:
            self.rules = json.load(f)
        self._save()
        log_audit("rollback", {"to_version": version})
        print(f"[ROLLBACK] Reverted to snapshot {version}")
        return True

    def add_rule(self, rule: dict, scheduled: bool = True):
        """규칙 추가 (배치 적용)"""
        rule["version"] = max((r.get("version", 0) for r in self.rules), default=0) + 1
        rule["added_at"] = datetime.now().isoformat()
        rule["activation"] = "next_cycle" if scheduled else "immediate"
        self.rules.append(rule)
        self._save()
        log_audit("add_rule", rule)

    def list_rules(self):
        for r in self.rules:
            status = f"[v{r.get('version',0)}]"
            print(f"  {status} {r['id']}: {r['name']} — {r.get('action','?')} (source: {r.get('source','?')})")

    def review(self, diff: str) -> list[dict]:
        """diff에 대해 규칙 적용 → 리뷰 코멘트 생성"""
        comments = []
        for rule in self.rules:
            if rule.get("activation") == "next_cycle":
                continue  # 아직 활성화 안 됨
            if rule["pattern"] in diff.lower() or rule["id"] in diff:
                comments.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "action": rule["action"],
                    "message": f"[{rule['action'].upper()}] {rule['name']}: {rule['pattern']}",
                })
        return comments


# === Quality Gate ===

class QualityGate:
    PRECISION_DELTA_MIN = 0.02
    FP_RATE_MAX = 0.15
    ACCEPTANCE_RATE_MIN = 0.70

    @staticmethod
    def evaluate(precision_delta: float, fp_rate: float, acceptance_rate: float) -> dict:
        passed = (
            precision_delta >= QualityGate.PRECISION_DELTA_MIN
            and fp_rate <= QualityGate.FP_RATE_MAX
            and acceptance_rate >= QualityGate.ACCEPTANCE_RATE_MIN
        )
        return {
            "passed": passed,
            "precision_delta": {"value": precision_delta, "threshold": QualityGate.PRECISION_DELTA_MIN, "ok": precision_delta >= QualityGate.PRECISION_DELTA_MIN},
            "fp_rate": {"value": fp_rate, "threshold": QualityGate.FP_RATE_MAX, "ok": fp_rate <= QualityGate.FP_RATE_MAX},
            "acceptance_rate": {"value": acceptance_rate, "threshold": QualityGate.ACCEPTANCE_RATE_MIN, "ok": acceptance_rate >= QualityGate.ACCEPTANCE_RATE_MIN},
        }


# === Evolution Loop ===

def evolve(engine: RuleEngine, feedback_file: str):
    """피드백에서 패턴 추출 → 규칙 생성 → QualityGate 검증 → 적용 or 롤백"""
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

    fb_path = Path(feedback_file)
    if not fb_path.exists():
        print(f"[ERROR] Feedback file not found: {fb_path}")
        return

    with open(fb_path, "r", encoding="utf-8") as f:
        feedback = json.load(f)

    snapshot_ver = engine.snapshot()
    print(f"[SNAPSHOT] Saved version {snapshot_ver}")

    # 패턴 추출 (시뮬레이션)
    accepted = [fb for fb in feedback if fb.get("action") == "accept"]
    rejected = [fb for fb in feedback if fb.get("action") == "reject"]

    if not accepted:
        print("[INFO] No accepted feedback — no evolution")
        return

    # 새 규칙 후보 생성
    new_rule = {
        "id": f"R{len(engine.rules)+1:03d}",
        "name": f"Team convention (auto-{datetime.now().strftime('%H%M')})",
        "pattern": accepted[0].get("pattern", "custom_pattern"),
        "action": "warn",
        "source": "evolution",
    }

    # QualityGate 평가
    precision_delta = len(accepted) / max(len(accepted) + len(rejected), 1) - 0.5
    fp_rate = len(rejected) / max(len(accepted) + len(rejected), 1)
    acceptance_rate = len(accepted) / max(len(feedback), 1)

    gate = QualityGate.evaluate(precision_delta, fp_rate, acceptance_rate)
    print(f"[GATE] precision_delta={precision_delta:.3f}, fp_rate={fp_rate:.3f}, acceptance={acceptance_rate:.3f}")

    if gate["passed"]:
        engine.add_rule(new_rule, scheduled=True)
        print(f"[EVOLVE] Rule {new_rule['id']} added (activation: next_cycle)")
    else:
        engine.rollback(snapshot_ver)
        print(f"[REJECT] QualityGate failed — rolled back to {snapshot_ver}")
        log_audit("evolution_rejected", {"rule": new_rule, "gate": gate})


# === Audit Log ===

def log_audit(action: str, data: dict):
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        entry = {"ts": datetime.now().isoformat(), "action": action, "data": data}
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# === CLI ===

def main():
    if len(sys.argv) < 2:
        print("Usage: code_reviewer.py [review|evolve|rules] [options]")
        return

    cmd = sys.argv[1]
    engine = RuleEngine()

    if cmd == "review":
        diff = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--diff" else "sample diff with function_length > 50"
        sanitized, findings = sanitize_input(diff)
        if findings:
            print(f"[SECURITY] {len(findings)} injection patterns blocked")
            for f in findings:
                print(f"  - {f}")
        comments = engine.review(sanitized)
        print(f"\n[REVIEW] {len(comments)} comments:")
        for c in comments:
            print(f"  {c['message']}")

    elif cmd == "evolve":
        fb_file = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--feedback" else "feedback/sample.json"
        evolve(engine, fb_file)

    elif cmd == "rules":
        if len(sys.argv) > 2 and sys.argv[2] == "--rollback":
            ver = sys.argv[3] if len(sys.argv) > 3 else ""
            engine.rollback(ver)
        else:
            engine.list_rules()

    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
