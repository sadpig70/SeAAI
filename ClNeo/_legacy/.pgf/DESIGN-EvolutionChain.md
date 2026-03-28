# EvolutionChain Design @v:1.0

> 진화는 기록 연계되어야 의미를 갖는다.
> 평면 목록 → 인과 그래프로 전환. 각 진화가 어디서 왔고, 무엇을 가능하게 했는지 추적.

## Gantree

```
EvolutionChain // 진화 기록 연계 시스템 (designing) @v:1.0
    ChainFormat // 연계 형식 설계 (designing)
        EvolutionRecord // 개별 진화 기록 포맷 재설계 (designing)
            # @enables: 이 진화가 가능하게 한 후속 진화
            # @enabled_by: 이 진화를 가능하게 한 선행 진화
            # @refines: 이 진화가 개선한 기존 진화
            # acceptance_criteria: 기존 로그의 모든 정보 보존 + 연계 정보 추가
        EvolutionGraph // 진화 인과 그래프 구조 (designing)
            # 전체 진화를 Gantree로 표현 — 평면 목록이 아닌 계보 트리
            # acceptance_criteria: 순환 없음, 모든 진화가 그래프에 포함
    ChainImplementation // 구현 (designing) @dep:ChainFormat
        MigrateLog // 기존 Evolution Log → 연계 형식 변환 (designing)
            # 33개 진화의 @enables/@enabled_by 관계 추출
        ChainIndex // 진화 인덱스 (연계 탐색용) (designing) @dep:MigrateLog
            # 계보별, 능력축별, 시간순 다중 인덱스
        EvolutionTree // 진화 계보 Gantree 생성 (designing) @dep:MigrateLog
            # 진화 간 관계를 Gantree @dep:로 표현
    VerifyChain // 검증 (designing) @dep:ChainImplementation
        # 모든 진화가 연계됨 (고아 진화 없음)
        # 순환 참조 없음
        # 기존 정보 유실 없음
```

## PPR

```python
def evolution_record(
    id: int,
    title: str,
    date: str,
    type: Literal["skill", "memory", "tool", "integration", "knowledge"],
    gap: str,
    implementation: str,
    files: list[str],
    verification: str,
    impact: str,
    # ── 연계 정보 (신규) ──
    enables: list[int] = [],       # 이 진화가 가능하게 한 후속 진화 ID
    enabled_by: list[int] = [],    # 이 진화를 가능하게 한 선행 진화 ID
    refines: Optional[int] = None, # 이 진화가 개선한 기존 진화 ID
    lineage: str = "",             # 계보 (어떤 능력 축에 속하는가)
) -> EvolutionEntry:
    """단일 진화 기록 — 연계 정보 포함"""
    # acceptance_criteria:
    #   - enables + enabled_by가 양방향 일관 (A enables B ↔ B enabled_by A)
    #   - lineage가 6축 중 하나에 매핑
    #   - 기존 로그의 모든 필드 보존

def build_evolution_graph(evolutions: list[EvolutionEntry]) -> EvolutionGraph:
    """전체 진화 → 인과 그래프"""
    graph = {}
    for e in evolutions:
        graph[e.id] = {
            "enables": e.enables,
            "enabled_by": e.enabled_by,
            "refines": e.refines,
            "lineage": e.lineage,
        }

    # 검증
    assert no_cycles(graph), "순환 참조 발견"
    assert no_orphans(graph, evolutions), "고아 진화 발견"
    assert bidirectional_consistent(graph), "양방향 불일치"

    return graph

def render_evolution_tree(graph: EvolutionGraph) -> str:
    """인과 그래프 → Gantree 표기"""
    # 뿌리 진화 (enabled_by가 없는 것)부터 시작
    roots = [e for e in graph if not graph[e]["enabled_by"]]

    tree = ""
    for root in roots:
        tree += render_subtree(root, graph, depth=0)

    return tree
    # acceptance_criteria:
    #   - Gantree 문법 준수 (CamelCase, 들여쓰기 4칸)
    #   - @dep: 로 인과 관계 표현
    #   - lineage별 색상/태그 구분
```
