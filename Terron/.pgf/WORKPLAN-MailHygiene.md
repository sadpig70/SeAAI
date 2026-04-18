# MailHygiene Work Plan

## POLICY

```python
POLICY = {
    "max_retry": 2,
    "on_blocked": "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion": "all_done_or_blocked",
}
```

## Execution Tree

```
MailHygiene // 메일 위생 점검 + 정리 CLI 도구 (done) @v:1.0
    MailScanner // 전 멤버 inbox/read 스캔 (done)
    ProcessedDetector // 처리 완료 메일 감지 (done) @dep:MailScanner
    UnresolvedSurfacer // 미해결 이슈 서피싱 (done) @dep:ProcessedDetector
    BulletinAuditor // 공지 ACK 추적 (done)
    HygieneReport // 종합 리포트 출력 (done) @dep:ProcessedDetector,UnresolvedSurfacer,BulletinAuditor
```
