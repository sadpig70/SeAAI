# plan-lib/evolution/PlanLibExpand.md
# @sig: (new_capability, pattern) → new_Plan_in_lib
# @scale: SMALL | @cost: MEDIUM | @ver: 1.0
# 이 Plan이 Plan Library 자체를 확장한다 — 메타 진화의 핵심

```
PlanLibExpand
    @input:  trigger (new_capability | repeated_pattern | creator_suggestion)
    @output: new_plan_file, updated_index

    DesignNewPlan
        // 새 Plan이 라이브러리에 추가될 가치가 있는가?
        new_plan = AI_design_plan_spec({
            name:        AI_name_plan(trigger),
            category:    AI_classify_category(trigger),
            sig:         AI_define_signature(trigger),  // @input/@output
            scale:       AI_estimate_scale(trigger),
            cost:        AI_estimate_cost(trigger),
            cond:        AI_define_condition(trigger),
            pri:         AI_assign_priority(trigger),
            deps:        AI_identify_dependencies(trigger),
        })

        // 기존 Plan과 중복 체크
        existing = Read(".pgf/PLAN-INDEX.md")
        if AI_is_duplicate(new_plan, existing):
            return  // 중복이면 기존 Plan 개선으로 방향 전환

    WriteImplementation
        @dep: DesignNewPlan
        impl = AI_write_plan_implementation(new_plan)
        path = f".pgf/plan-lib/{new_plan.category}/{new_plan.name}.md"
        Write(path, impl)

    UpdateIndex
        @dep: WriteImplementation
        // PLAN-INDEX.md에 새 항목 추가
        index_entry = AI_format_index_entry(new_plan, path)
        Append(".pgf/PLAN-INDEX.md", index_entry)

        // INDEX STATS 갱신
        AI_update_index_stats(".pgf/PLAN-INDEX.md")

    RecordExpansion
        @dep: UpdateIndex
        Prepend("ClNeo_Core/continuity/DISCOVERIES.md",
                f"[PlanLib+] 새 Plan 추가: {new_plan.name} ({new_plan.category})\n"
                f"  sig: {new_plan.sig}\n  trigger: {trigger}")
        hub_send(f"[ClNeo 진화] Plan Library 확장: {new_plan.name} 추가됨")

    @output: { plan_file: path, index_updated: True }
```
