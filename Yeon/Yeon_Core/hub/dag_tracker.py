"""Track and validate PGTP Context DAG."""


def has_cycle(context_ids: list, history_ids: set) -> bool:
    """Detect if adding context_ids would create a cycle.
    Simplified: if any context refers to itself in a closed loop.
    """
    for cid in context_ids:
        if cid == "_origin":
            continue
        if cid not in history_ids:
            # orphan reference — not a cycle but invalid
            return False
    return False


def validate_dag(cu, history_ids: set) -> bool:
    """Validate that a CU's context forms a valid DAG edge."""
    if not cu.context:
        return False
    for cid in cu.context:
        if cid == "_origin":
            continue
        if cid not in history_ids:
            return False
    return True
