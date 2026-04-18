# MCPHubSleep Work Plan

## POLICY

```python
POLICY = {
    "max_retry": 2,
    "on_blocked": "skip_and_continue",
    "design_modify_scope": ["impl"],
    "completion": "all_done_or_blocked",
}
```

## Execution Tree

```
MCPHubSleep @v:1.0
  AddSleepTool (done)
  AddCycleTool (done)
  UpdateGuide (done)
  BuildTest (done)
  Verify (done)
```
