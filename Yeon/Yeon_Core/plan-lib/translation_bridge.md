# Plan: translation_bridge

## Purpose
Translate a PGTP CognitiveUnit into a member-specific format or natural language.

## Steps
1. Parse incoming `source_CU`.
2. Detect `target_member` capability profile.
3. Rewrite payload for target's preferred format.
4. Preserve `context` DAG references.
5. Return `translated_CU`.

## Acceptance
- Translated CU intent is unchanged.
- Context references are preserved.
- Payload is comprehensible to target member.
