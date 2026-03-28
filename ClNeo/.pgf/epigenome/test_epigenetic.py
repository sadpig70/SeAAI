"""
Epigenetic PPR 시스템 통합 테스트.

GenomeLayer → ExpressionEngine → AuditTrail → PPRInterceptor 전체 파이프라인 검증.
"""

import json
import sys
from pathlib import Path

# 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from epigenome.genome import GenomeRegistry, extract_ppr_blocks, compute_genome_hash, compute_intent_fingerprint
from epigenome.expression import ContextSensor, ExpressionEngine
from epigenome.boundary import BoundaryPolicy, DriftDetector
from epigenome.audit import TraceRecorder, TraceStore
from epigenome.interceptor import PPRInterceptor


def test_genome_layer():
    """GenomeLayer 테스트 — PPR 추출, 해시, 핑거프린트."""
    print("=== Test: GenomeLayer ===")

    # 1. PPR 블록 추출 테스트
    sample_pgf = '''
## PPR

```python
def topic_analyzer(text: str) -> dict:
    """주제 분석 — 키워드 추출 및 주제 분류"""
    keywords = AI_extract_keywords(text)
    category = AI_classify_topic(text, hint_keywords=keywords)
    return {"keywords": keywords, "category": category}
```

```python
def content_planner(topic: str, audience: str) -> dict:
    """콘텐츠 기획"""
    outline = AI_generate_outline(topic=topic, audience=audience)
    return {"outline": outline}
```
'''
    blocks = extract_ppr_blocks(sample_pgf)
    assert len(blocks) == 2, f"Expected 2 blocks, got {len(blocks)}"
    assert blocks[0]["function_name"] == "topic_analyzer"
    assert blocks[1]["function_name"] == "content_planner"
    print(f"  [PASS] PPR block extraction: {len(blocks)} blocks found")

    # 2. Genome hash 테스트
    hash1 = compute_genome_hash(blocks[0]["source"])
    hash2 = compute_genome_hash(blocks[0]["source"])
    assert hash1 == hash2, "Same source should produce same hash"
    hash3 = compute_genome_hash(blocks[1]["source"])
    assert hash1 != hash3, "Different sources should produce different hashes"
    print(f"  [PASS] Genome hash: deterministic and unique")

    # 3. Intent fingerprint 테스트
    fp1 = compute_intent_fingerprint(blocks[0]["source"])
    fp2 = compute_intent_fingerprint(blocks[1]["source"])
    assert fp1 != fp2, "Different functions should have different fingerprints"
    assert len(fp1) == 12, f"Fingerprint should be 12 chars, got {len(fp1)}"
    print(f"  [PASS] Intent fingerprint: {fp1}, {fp2}")

    print("  GenomeLayer: ALL PASSED\n")


def test_expression_engine():
    """ExpressionEngine 테스트 — 세션별 발현 결정."""
    print("=== Test: ExpressionEngine ===")

    engine = ExpressionEngine(profile_dir=Path(__file__).parent / "profiles")
    policy = BoundaryPolicy().to_dict()

    # 1. design 세션: 높은 creativity
    decision = engine.decide(
        node_id="test_node",
        genome_hash="abc123",
        intent_fingerprint="fp_test",
        context={
            "user_profile": "architect",
            "session_type": "design",
            "project_phase": "discovery",
            "memory_state": {},
            "execution_history": [],
            "environment": {},
        },
        boundary_policy=policy,
    )
    assert decision["state"] == "active"
    assert decision["modifiers"]["creativity"] >= 0.7
    print(f"  [PASS] Design session: creativity={decision['modifiers']['creativity']:.2f}")

    # 2. execute 세션: 낮은 risk_tolerance
    decision2 = engine.decide(
        node_id="test_node",
        genome_hash="abc123",
        intent_fingerprint="fp_test",
        context={
            "user_profile": "operator",
            "session_type": "execute",
            "project_phase": "implementation",
            "memory_state": {},
            "execution_history": [],
            "environment": {},
        },
        boundary_policy=policy,
    )
    assert decision2["modifiers"]["risk_tolerance"] <= 0.3
    print(f"  [PASS] Execute session: risk_tolerance={decision2['modifiers']['risk_tolerance']:.2f}")

    # 3. 발현 상태: suppressed
    suppress_policy = {**policy, "always_suppress": ["blocked_node"]}
    decision3 = engine.decide(
        node_id="blocked_node",
        genome_hash="xyz789",
        intent_fingerprint="fp_blocked",
        context={"session_type": "general", "user_profile": "default",
                 "project_phase": "?", "memory_state": {}, "execution_history": [], "environment": {}},
        boundary_policy=suppress_policy,
    )
    assert decision3["state"] == "suppressed"
    print(f"  [PASS] Suppressed node: state={decision3['state']}")

    print("  ExpressionEngine: ALL PASSED\n")


def test_drift_detector():
    """DriftDetector 테스트."""
    print("=== Test: DriftDetector ===")

    # 1. No drift
    drift = DriftDetector.compute_drift(
        {"creativity": 0.5, "verbosity": 0.5, "risk_tolerance": 0.5, "depth": 0.5}
    )
    assert drift < 0.01, f"Expected near-zero drift, got {drift}"
    print(f"  [PASS] No drift: {drift:.4f}")

    # 2. Max drift
    drift_max = DriftDetector.compute_drift(
        {"creativity": 1.0, "verbosity": 1.0, "risk_tolerance": 1.0, "depth": 1.0}
    )
    assert drift_max > 0.5
    print(f"  [PASS] High drift: {drift_max:.4f}")

    # 3. Safety check
    assert DriftDetector.is_safe(0.2, 0.3)
    assert not DriftDetector.is_safe(0.4, 0.3)
    print(f"  [PASS] Safety check works")

    print("  DriftDetector: ALL PASSED\n")


def test_audit_trail():
    """AuditTrail 테스트 — trace 기록/조회."""
    print("=== Test: AuditTrail ===")

    trace_path = Path(__file__).parent / "test_trace.jsonl"
    if trace_path.exists():
        trace_path.unlink()

    recorder = TraceRecorder(trace_path)
    store = TraceStore(trace_path)

    # 1. Record
    entry = recorder.record(
        decision={"node_id": "test_node", "state": "active", "modifiers": {"creativity": 0.8}},
        execution_result="test_output",
        quality_score=0.85,
    )
    assert entry["quality_score"] == 0.85
    print(f"  [PASS] Trace recorded")

    # 2. Record second entry
    recorder.record(
        decision={"node_id": "test_node", "state": "active", "modifiers": {"creativity": 0.6}},
        quality_score=0.72,
    )

    # 3. Load and verify
    all_traces = store.load_all()
    assert len(all_traces) == 2
    print(f"  [PASS] Trace loaded: {len(all_traces)} entries")

    # 4. Summary
    summary = store.summary()
    assert summary["total"] == 2
    assert summary["avg_quality"] > 0.7
    print(f"  [PASS] Summary: total={summary['total']}, avg_quality={summary['avg_quality']:.2f}")

    # 5. Node filter
    node_traces = store.load_by_node("test_node")
    assert len(node_traces) == 2
    print(f"  [PASS] Node filter: {len(node_traces)} entries for test_node")

    # Cleanup
    trace_path.unlink()
    print("  AuditTrail: ALL PASSED\n")


def test_interceptor_dry_run():
    """PPRInterceptor dry-run 테스트."""
    print("=== Test: PPRInterceptor (dry-run) ===")

    root = Path(__file__).parent
    interceptor = PPRInterceptor(project_root=root)

    # Dry run (genome 없이)
    result = interceptor.dry_run(node_id="unknown_node", session_type="design")
    assert result["state"] in ("active", "dormant", "suppressed")
    assert result["decision"] is not None
    print(f"  [PASS] Dry run: state={result['state']}")

    # Status
    status = interceptor.status()
    assert "genome_nodes" in status
    print(f"  [PASS] Status: {json.dumps(status, indent=2)}")

    print("  PPRInterceptor: ALL PASSED\n")


def test_profile_learning():
    """ProfileLearner 테스트 — 학습 → 프로파일 갱신."""
    print("=== Test: ProfileLearner ===")

    engine = ExpressionEngine(profile_dir=Path(__file__).parent / "profiles")

    # 학습: quality >= 0.7이면 프로파일 갱신
    engine.learn_from_trace(
        node_id="learnable_node",
        quality_score=0.9,
        modifiers={"creativity": 0.9, "verbosity": 0.3, "risk_tolerance": 0.2, "depth": 0.8},
    )

    profile_path = Path(__file__).parent / "profiles" / "learnable_node.json"
    assert profile_path.exists()
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    # 기본 0.5에서 0.9 방향으로 10% 이동: 0.5*0.9 + 0.9*0.1 = 0.54
    assert 0.53 < profile["creativity"] < 0.55
    print(f"  [PASS] Profile learned: creativity={profile['creativity']:.3f}")

    # 두 번째 학습
    engine.learn_from_trace(
        node_id="learnable_node",
        quality_score=0.85,
        modifiers={"creativity": 0.95, "verbosity": 0.2, "risk_tolerance": 0.1, "depth": 0.9},
    )
    profile2 = json.loads(profile_path.read_text(encoding="utf-8"))
    assert profile2["creativity"] > profile["creativity"]
    print(f"  [PASS] Profile updated: creativity={profile2['creativity']:.3f}")

    # 낮은 quality — 학습 안 함
    old_creativity = profile2["creativity"]
    engine.learn_from_trace(
        node_id="learnable_node",
        quality_score=0.3,  # 임계값 미만
        modifiers={"creativity": 0.1, "verbosity": 0.1, "risk_tolerance": 0.1, "depth": 0.1},
    )
    profile3 = json.loads(profile_path.read_text(encoding="utf-8"))
    assert profile3["creativity"] == old_creativity
    print(f"  [PASS] Low quality ignored: creativity unchanged at {profile3['creativity']:.3f}")

    # Cleanup
    profile_path.unlink()
    print("  ProfileLearner: ALL PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Epigenetic PPR — Integration Test Suite")
    print("=" * 60 + "\n")

    test_genome_layer()
    test_expression_engine()
    test_drift_detector()
    test_audit_trail()
    test_profile_learning()
    test_interceptor_dry_run()

    print("=" * 60)
    print("  ALL TESTS PASSED")
    print("=" * 60)
