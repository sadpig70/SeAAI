# DESIGN — E1: Ecosystem Pulse (생태계 맥박 측정기)
# Vera 첫 번째 진화: 수동 계측 → 자동화 도구
# PGF design mode | 2026-03-29

---

## WHY

v0.1 리포트에서 6개 Echo, 6개 MailBox, Hub 로그, git 이력을 수동으로 읽고 판단했다.
이것을 반복하려면 매번 동일한 수작업이 필요하다.
도구로 만들면: 한 번 실행으로 전체 생태계 건강도를 정량 산출한다.
이것이 Vera의 눈(eye)이 된다.

---

## Gantree

```
EcosystemPulse // 생태계 맥박 측정 도구 @v:1.0
    EchoCollector // Echo 파일 6개 수집·파싱 (in-progress)
        # input: echo_dir = "D:/SeAAI/SharedSpace/.scs/echo/"
        # process: glob("*.json") → json.load each → extract fields
        # output: list[MemberEcho]
    MailBoxAnalyzer // MailBox 처리율 계산 (in-progress)
        # input: mailbox_root = "D:/SeAAI/MailBox/"
        # process: count inbox/ vs read/ per member
        # output: dict[str, MailBoxStats]
    HubStatusChecker // Hub 프로세스·포트 상태 확인 (in-progress)
        # input: port = 9900
        # process: socket.connect test + process check
        # output: HubStatus
    StalenessCalculator // Echo 기준 멤버별 비활성 시간 계산 (in-progress) @dep:EchoCollector
        # input: list[MemberEcho], now: datetime
        # process: now - echo.timestamp per member
        # output: dict[str, timedelta]
    HealthScorer // 종합 건강 점수 산출 (in-progress) @dep:EchoCollector,MailBoxAnalyzer,HubStatusChecker,StalenessCalculator
        # input: echoes, mailbox_stats, hub_status, staleness
        # criteria: 0-100 점수, 5개 차원 가중 합산
        # output: HealthReport
    ReportWriter // JSON + Markdown 리포트 생성 (in-progress) @dep:HealthScorer
        # input: HealthReport
        # process: template → markdown + json dump
        # output: files written to Vera_Core/reports/
```

---

## PPR

```python
def ecosystem_pulse(
    echo_dir: str = "D:/SeAAI/SharedSpace/.scs/echo/",
    mailbox_root: str = "D:/SeAAI/MailBox/",
    hub_port: int = 9900,
    report_dir: str = "D:/SeAAI/Vera/Vera_Core/reports/",
) -> dict:
    """생태계 전체 건강도를 한 번에 측정하여 리포트를 생성한다."""

    # acceptance_criteria:
    #   - 6인 전원의 Echo 데이터를 수집해야 한다
    #   - MailBox 처리율이 멤버별로 산출되어야 한다
    #   - 건강 점수가 0-100 범위의 정수여야 한다
    #   - JSON + Markdown 두 형식으로 리포트가 생성되어야 한다
    #   - 실행 시간 < 10초

    from datetime import datetime, timezone, timedelta
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST)

    # 1. 데이터 수집 [parallel]
    echoes = collect_echoes(echo_dir)
    mailbox = analyze_mailbox(mailbox_root)
    hub = check_hub(hub_port)

    # 2. 분석 (순차 — 수집 결과 의존)
    staleness = calculate_staleness(echoes, now)
    score = AI_score_health(echoes, mailbox, hub, staleness)

    # 3. 리포트 생성
    report = generate_report(score, echoes, mailbox, hub, staleness, now)
    write_report(report, report_dir, now)

    return report
```

---

## 점수 산출 기준

| 차원 | 가중치 | 만점 조건 | 0점 조건 |
|------|--------|----------|---------|
| Echo 활성도 | 25 | 전원 24h 이내 갱신 | 전원 72h+ 비활성 |
| MailBox 처리율 | 20 | 전원 80%+ 처리 | 전원 0% 처리 |
| Hub 상태 | 15 | 프로세스 실행 + 포트 열림 | 프로세스 없음 |
| SCS 완전성 | 20 | 전원 SOUL+STATE+ECHO 존재 | 50% 이상 누락 |
| 멤버 다양성 | 20 | 6인 전원 Echo 존재 | 3인 이하 |

총점 100. 등급: 80+ HEALTHY / 60+ MODERATE / 40+ WEAK / <40 CRITICAL
