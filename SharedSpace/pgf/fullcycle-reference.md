# Full-Cycle Mode — design/plan/execute/verify Continuous Auto-Execution Specification

## 1. Overview

full-cycle is a mode that automatically executes the **design + plan + execute + verify** 4 phases as a single continuous process.

- Phase transitions are automatic, proceeding to completion without user intervention
- When verify issues a rework judgment, only the affected subtree is re-executed from design (up to `max_verify_cycles` times)
- Corresponds to Phases 2~5 of create mode (excluding Phase 1 DISCOVER)

---

## 2. Commands

| Command | Action |
|------|------|
| `/PGF full-cycle {project_name}` | 4-phase continuous auto-execution |
| `/PGF full-cycle {project_name} --max-verify-cycles N` | Maximum N verify-rework iterations (default 2) |

---

## 3. Execution Sequence PPR

```python
def full_cycle(project_name: str, description: str, policy: dict = None) -> FullCycleResult:
    """design → plan → execute → verify continuous auto-execution"""
    pgf_dir = ".PGF"
    policy = policy or POLICY_STANDARD

    # === Phase 1: DESIGN ===
    design_path = f"{pgf_dir}/DESIGN-{project_name}.md"
    AI_design_gantree(description, design_path)
    assert AI_validate_design(design_path), "design incomplete"
    report_phase("DESIGN", design_path)

    # === Phase 2: PLAN ===
    workplan_path = f"{pgf_dir}/WORKPLAN-{project_name}.md"
    status_path = f"{pgf_dir}/status-{project_name}.json"
    convert_design_to_workplan(design_path, workplan_path, policy)
    init_status_json(workplan_path, status_path)
    report_phase("PLAN", workplan_path)

    # === Phase 3: EXECUTE ===
    execute_all_nodes(workplan_path, design_path, status_path)
    report_phase("EXECUTE", "all nodes terminal")

    # === Phase 4: VERIFY ===
    for cycle in range(policy.get("max_verify_cycles", 2)):
        verify_result = verify_project(design_path, workplan_path, policy)
        if verify_result.status == "passed":
            report_phase("VERIFY", "passed")
            return FullCycleResult(status="completed", design=design_path, workplan=workplan_path)
        elif verify_result.status == "blocked":
            report_phase("VERIFY", "blocked")
            return FullCycleResult(status="blocked", issues=verify_result.issues)
        else:  # rework
            AI_rework_subtree(design_path, workplan_path, verify_result.issues)
            execute_all_nodes(workplan_path, design_path, status_path)

    report_phase("VERIFY", "rework_limit_exceeded")
    return FullCycleResult(status="rework_limit_exceeded")
```

---

## 4. Phase Transition Conditions

| Transition | Condition | On Failure |
|------|------|---------|
| design → plan | Design completion 4 criteria met (all leaves atomized, PPR written, no @dep cycles, checklist passed) | Continue design |
| plan → execute | WORKPLAN-{Name}.md + status-{Name}.json creation confirmed | Error report |
| execute → verify | All nodes terminal (done or blocked) | Continue execute |
| verify → complete | passed | rework → re-execute subtree / blocked → report to user |

---

## 5. Rework Regression Loop

```python
def AI_rework_subtree(design_path, workplan_path, issues):
    """Identify rework target nodes and roll back"""
    for issue in issues:
        node = issue.node
        # 1. Fix the node's PPR in DESIGN
        AI_fix_design_ppr(design_path, node, issue)
        # 2. Roll back the node + children to (designing) in WORKPLAN
        rollback_subtree(workplan_path, node, target_status="designing")
    # 3. Synchronize status JSON
    sync_status_json(workplan_path)
```

### Rollback Scope Determination

The rollback scope includes the rework target node and all its child nodes. Parent and sibling nodes are not affected.

```python
def identify_rework_scope(issues: list[VerifyIssue], workplan_path: str) -> list[str]:
    """Identify rework target nodes + child nodes"""
    target_nodes = set(i.node for i in issues)
    descendants = set()
    for node in target_nodes:
        descendants.update(get_descendants(workplan_path, node))
    return list(target_nodes | descendants)
```

### Iteration Limit

- Allow verify → rework repetition up to `POLICY.max_verify_cycles` (default: `2`)
- When limit exceeded:
  - Preserve all outputs produced so far (do not delete)
  - Halt report including unresolved issue list + attempt count
  - Return `FullCycleResult.status = "rework_limit_exceeded"`

---

## 6. Progress Report Format

Report in the following format upon each Phase completion (proceed immediately to next Phase without pausing):

```text
[PGF FULL-CYCLE] Phase 1/4 DESIGN complete | nodes: 12 | DESIGN-{Name}.md
[PGF FULL-CYCLE] Phase 2/4 PLAN complete | WORKPLAN-{Name}.md + status-{Name}.json
[PGF FULL-CYCLE] Phase 3/4 EXECUTE complete | 12/12 nodes done
[PGF FULL-CYCLE] Phase 4/4 VERIFY complete | status: passed

[PGF FULL-CYCLE] === Complete ===
  Design: .pgf/DESIGN-{Name}.md
  Execution: .pgf/WORKPLAN-{Name}.md
  Verification: passed
```

### On Rework

```text
[PGF FULL-CYCLE] Phase 4/4 VERIFY | status: rework (cycle 1/2)
  Target nodes: TokenValidator, SessionManager
[PGF FULL-CYCLE]   → rework: fixing design + re-executing...
[PGF FULL-CYCLE] Phase 4/4 VERIFY complete | status: passed (cycle 2/2)
```

### On Rework Limit Exceeded

```text
[PGF FULL-CYCLE] Phase 4/4 VERIFY | rework_limit_exceeded (2/2 cycles)
  Unresolved: TokenValidator (medium), SessionManager (medium)

[PGF FULL-CYCLE] === Halted ===
  Design: .pgf/DESIGN-{Name}.md (preserved)
  Execution: .pgf/WORKPLAN-{Name}.md (preserved)
  Verification: rework_limit_exceeded
```

---

## 7. Session Interruption/Resume Strategy

### Preserved on Interruption

Since WORKPLAN/status JSON are saved upon each Phase completion, resumption after interruption is possible.

| Phase Completion Point | Preserved Outputs |
|----------------|----------------|
| DESIGN complete | DESIGN-{Name}.md |
| PLAN complete | DESIGN-{Name}.md + WORKPLAN-{Name}.md + status-{Name}.json |
| EXECUTE complete | Above + execution outputs |
| VERIFY in progress | Above + partial verification results |

### Resume Procedure

1. Check last completed Phase from status-{Name}.json
2. Continue execution from the next phase
3. If interrupted during EXECUTE, resume from incomplete nodes

### `/reopen-session` Integration

Record full-cycle progress state in PROJECT_STATUS.md:

```text
## Full-Cycle Progress State
- Project: {project_name}
- Current Phase: EXECUTE (3/4)
- Completed nodes: 8/12
- Next action: Resume execution of incomplete nodes
```

---

## 8. Relationship with Create Mode

| Item | `/PGF full-cycle` | `/PGF create` |
|------|-------------------|---------------|
| Starting point | User-provided description | Discovery engine (A3IE) |
| Phase composition | 4 phases (design~verify) | 5 phases (discover~verify) |
| DISCOVER | Not included | Included as Phase 1 |
| DESIGN~VERIFY | Phases 1~4 | Phases 2~5 |
| Idea selection | Not needed | auto_select_idea |

- create = discover + full-cycle (DISCOVER added as Phase 1)
- full-cycle corresponds to Phases 2~5 of create
- See `create-reference.md` for details

---

## 9. Error Behavior

| Situation | Response |
|------|------|
| Design validation failure (4 criteria not met) | Retry design phase (up to 3 times) |
| WORKPLAN/status JSON creation failure | Error report + halt |
| Majority of nodes blocked during execution | Apply POLICY.on_blocked then continue |
| Verification rework limit exceeded | Preserve outputs so far + halt report |
| Verification blocked (high severity) | Preserve outputs + report to user + halt immediately |
