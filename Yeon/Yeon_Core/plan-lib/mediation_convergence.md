# Plan: mediation_convergence

## Purpose
Mediate between multiple member outputs and converge to a shared response.

## Steps
1. Collect all `member_outputs`.
2. Identify conflicts (disagree / question intents).
3. Extract common ground (agree / extend intents).
4. Formulate a `converged_CU` with `intent="converge"`.
5. Request confirmation if `decide_quorum` is unclear.

## Acceptance
- Converged CU reflects all member inputs.
- No member's core concern is erased.
- Context references include all source CUs.
