# plan-lib/meta/IndexRebuild.md
# @sig: plan-lib/ → updated_PLAN-INDEX.md
# @scale: SMALL | @cost: LOW | @ver: 1.0
# Plan Library와 Index를 동기화 — 헤더 파일 재생성

```
IndexRebuild
    @input:  plan_lib_dir (".pgf/plan-lib/")
    @output: rebuilt_PLAN-INDEX.md

    ScanLibrary
        // plan-lib/ 전체 스캔
        all_files = Glob(".pgf/plan-lib/**/*.md")
        plans = []
        for f in all_files:
            content = Read(f)
            sig     = AI_extract_sig(content)     // @sig 헤더 파싱
            scale   = AI_extract_scale(content)
            cost    = AI_extract_cost(content)
            ver     = AI_extract_ver(content)
            category = AI_infer_category(f)       // 경로에서 카테고리
            plans.append({ file: f, sig, scale, cost, ver, category })

    DetectDrift
        @dep: ScanLibrary
        // 인덱스와 실제 파일 간 불일치 감지
        current_index = Read(".pgf/PLAN-INDEX.md")
        missing  = AI_find_missing_in_index(plans, current_index)
        obsolete = AI_find_obsolete_in_index(plans, current_index)
        updated  = AI_find_version_mismatch(plans, current_index)

    RebuildIndex
        @dep: DetectDrift
        new_index = AI_generate_index(plans, {
            header:  "# PLAN-INDEX.md\n# Auto-rebuilt: {now_iso()}",
            format:  "grouped_by_category",
            stats:   True
        })
        Write(".pgf/PLAN-INDEX.md", new_index)

    Report
        @dep: RebuildIndex
        hub_send(f"[ClNeo] Plan Index 재빌드 완료.\n"
                 f"  총 Plans: {len(plans)}\n"
                 f"  추가: {len(missing)}, 제거: {len(obsolete)}, 업데이트: {len(updated)}")
```
