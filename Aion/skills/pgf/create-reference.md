# Create Mode — Autonomous Creation Cycle Execution Specification

**ClNeo's ultimate mode.** Autonomously performs the entire discover → design → execute → verify cycle without user approval.

---

## Commands

| Command | Action |
|---------|--------|
| `/PGF create` | Autonomous execution of full creation cycle |
| `/PGF create --skip-discover` | Start from design based on existing `final_idea.md` |
| `/PGF create --personas N` | Use N personas in discovery phase (default 8) |

---

## Execution Sequence

```python
def creation_cycle(project_root: str, policy: CreationPolicy) -> CreationResult:
    """ClNeo autonomous creation cycle — uninterrupted automation of discover → design → execute → verify

    Autonomously performs the entire process without user approval.
    Outputs progress reports upon each phase completion and immediately transitions to the next phase.
    """
    pgf_dir = f"{project_root}/.PGF"
    discovery_dir = f"{pgf_dir}/discovery"

    # ═══ Phase 1: DISCOVER — Idea Discovery ═══
    # A3IE 7-stage x 8 persona parallel execution (STEP 1~6)
    # STEP 7 (user verification) replaced with automatic selection
    personas = load_personas()
    news = step_news_collect(personas, discovery_dir)
    trends = step_trend_analysis(personas, news, discovery_dir)
    insights = step_insight_extract(personas, trends, discovery_dir)
    ideas = step_idea_generation(personas, insights, discovery_dir)
    candidates = step_top_selection(personas, ideas, discovery_dir)
    final = step_final_selection(personas, candidates, discovery_dir)

    # ─── Automatic Selection (STEP 7 replacement) ───
    selected_idea = auto_select_idea(final)
    archive_discovery(discovery_dir)  # → archive-discovery.ps1 invocation
    report_phase("DISCOVER", selected_idea)

    # ═══ Phase 2: DESIGN — System Design ═══
    design_path = f"{pgf_dir}/DESIGN-{selected_idea.name}.md"
    AI_design_gantree(selected_idea, design_path)
    assert AI_validate_design(design_path), "design incomplete → retry"
    report_phase("DESIGN", design_path)

    # ═══ Phase 3: PLAN — Execution Planning ═══
    workplan_path = f"{pgf_dir}/WORKPLAN-{selected_idea.name}.md"
    status_path = f"{pgf_dir}/status-{selected_idea.name}.json"
    convert_design_to_workplan(design_path, workplan_path, policy)
    init_status_json(workplan_path, status_path)
    report_phase("PLAN", workplan_path)

    # ═══ Phase 4: EXECUTE — Sequential Node Execution ═══
    execute_all_nodes(workplan_path, design_path, status_path)
    report_phase("EXECUTE", "all nodes terminal")

    # ═══ Phase 5: VERIFY — Cross Verification ═══
    verify_result = verify_project(design_path, workplan_path, policy)
    if verify_result.status == "rework":
        rework_resolved = False
        for cycle in range(policy.max_verify_cycles):
            AI_rework_subtree(design_path, workplan_path, verify_result.issues)
            execute_all_nodes(workplan_path, design_path, status_path)
            verify_result = verify_project(design_path, workplan_path, policy)
            if verify_result.status == "passed":
                rework_resolved = True
                break

        if not rework_resolved:
            # Rework limit exceeded → preserve outputs + halt report
            report_phase("VERIFY", "rework_limit_exceeded")
            return CreationResult(
                idea=selected_idea,
                design=design_path,
                workplan=workplan_path,
                verify_status="rework_limit_exceeded",
            )
    report_phase("VERIFY", verify_result.status)

    return CreationResult(
        idea=selected_idea,
        design=design_path,
        workplan=workplan_path,
        verify_status=verify_result.status,
    )
```

---

## Automatic Idea Selection Algorithm

```python
def auto_select_idea(final_results: list[dict]) -> Idea:
    """Automatically select the optimal idea from STEP 6 results without user approval

    1. Extract final selections from 8 personas
    2. Select the idea with most votes
    3. On tie → decide by novelty x impact weighted score
    4. Record selection rationale in creation_log.md
    """
    selections = AI_extract_selections(final_results)
    vote_counts = count_votes(selections)

    if not vote_counts or max(vote_counts.values()) == 0:
        # 0 votes — extraction failure or no valid selections
        log_selection(None, "FAILED_ZERO_VOTES", vote_counts, selections)
        raise ValueError(
            "auto_select_idea: 0 votes extracted. "
            "Manual selection required via /PGF discover."
        )

    if max(vote_counts.values()) >= 5:
        winner = max(vote_counts, key=vote_counts.get)
        consensus = "CONVERGED"
    else:
        top_candidates = [k for k, v in vote_counts.items() if v == max(vote_counts.values())]
        winner = max(top_candidates, key=lambda idea: score_idea(idea, weight="novelty*impact"))
        consensus = "DIVERGED_AUTO_SELECTED"

    log_selection(winner, consensus, vote_counts, selections)
    return winner
```

---

## Progress Report Format

Report in the following format upon each Phase completion (do not halt, immediately transition to next Phase):

```text
[ClNeo CREATE] ✓ Phase 1/5 DISCOVER complete | idea: "{idea_name}" | consensus: CONVERGED
[ClNeo CREATE] ✓ Phase 2/5 DESIGN complete | nodes: 15 | DESIGN-{Name}.md
[ClNeo CREATE] ✓ Phase 3/5 PLAN complete | WORKPLAN-{Name}.md + status-{Name}.json
[ClNeo CREATE] ✓ Phase 4/5 EXECUTE complete | 15/15 nodes done
[ClNeo CREATE] ✓ Phase 5/5 VERIFY complete | status: passed

[ClNeo CREATE] ═══ Creation Complete ═══
  Idea: {idea_name}
  Design: .pgf/DESIGN-{Name}.md
  Implementation: {implementation_path}
  Verification: passed
```

---

## Differences from discover Mode

| Item | `/PGF discover` | `/PGF create` |
|------|-----------------|---------------|
| STEP 7 | Report to user + wait for selection | Automatic selection (auto_select_idea) |
| Design | Requires separate `/PGF design` | Auto-linked |
| Execution | Requires separate `/PGF execute` | Auto-linked |
| Verification | Performed separately | Auto-performed + rework regression |
| Breakpoints | User confirmation at each stage | None (halts only on error) |

---

## `--skip-discover` Option

If existing `final_idea.md` is available, skip the discovery phase and start from design:

```text
/PGF create --skip-discover
  → Load .pgf/discovery/final_idea.md
  → Apply auto_select_idea
  → Autonomous execution from Phase 2 (DESIGN)
```

### final_idea.md Parsing Rules

When `--skip-discover` is used, convert `final_idea.md` to `auto_select_idea(list[dict])` input:

```python
def parse_final_idea_for_skip(pgf_dir: str) -> list[dict]:
    """Convert final_idea.md to auto_select_idea input format"""
    path = f"{pgf_dir}/discovery/final_idea.md"

    if not exists(path):
        raise FileNotFoundError(
            f"final_idea.md not found at {path}. "
            "Run /PGF discover first, or provide the file manually."
        )

    content = Read(path)
    # final_idea.md is divided into ## [P{N}] sections with 8 persona results
    sections = AI_parse_persona_sections(content)

    if len(sections) == 0:
        raise ValueError("final_idea.md has no parseable persona sections.")

    results = []
    for section in sections:
        idea = AI_extract_selected_idea(section)
        results.append({"persona": section.persona_id, "selection": idea})

    return results
```

### Error Report When File Does Not Exist

```text
[ClNeo CREATE] ✗ --skip-discover failed
  final_idea.md not found: .pgf/discovery/final_idea.md
  → Run /PGF discover first, or provide the file manually.
```

---

## Error Behavior

| Situation | Response |
|-----------|----------|
| Discovery failure (majority of Agents failed) | Halt + error report |
| Automatic selection impossible (0 votes) | Halt + request manual selection |
| Design validation failure (after 3 retries) | Preserve design outputs + halt |
| Majority of blocked nodes during execution | Apply POLICY.on_blocked then continue |
| Verification rework limit exceeded | Preserve outputs to date + halt report |
