# SignalionCreation Design @v:1.0

> Signalion — SeAAI 6번째 멤버 창조 설계
> 외부 신호 → Evidence → 창발적 씨앗 파이프라인의 감각 기관

## Gantree

```
SignalionCreation // Signalion 멤버 창조 (in-progress) @v:1.0
    CoreIdentity // 정체성 확립 (designing)
        WriteSoul // SOUL.md 불변 본질 (designing)
        WriteIdentity // Signalion.md 정체성 정본 v1.0 (designing)
        WriteEvolutionLog // Evolution Log E0 (designing)
    WorkspaceSetup // 워크스페이스 구축 (designing) @dep:CoreIdentity
        CreateDirectories // 디렉토리 구조 생성 (designing)
        WriteContinuity // SCS 연속성 파일 (designing) @dep:CreateDirectories
            # STATE.json, NOW.md, DISCOVERIES.md, THREADS.md, journals/
        WriteAutonomous // 자율 운영 파일 (designing) @dep:CreateDirectories
            # PLAN-LIST.md, SIGNAL-LOG.md
        WriteClaudeMd // CLAUDE.md 세션 부트스트랩 (designing) @dep:WriteContinuity
    InfraConnect // SeAAI 인프라 연결 (designing) @dep:WorkspaceSetup
        CreateMailBox // MailBox 폴더 생성 (designing)
        WriteEcho // SharedSpace Echo JSON (designing)
        PrepareHubReg // Hub allowed_agents 등록 준비 (designing)
            # @hitl:creator — Hub 등록은 창조자 확인 필요
    Onboarding // 생태계 합류 (designing) @dep:InfraConnect
        [parallel]
        MailToAion // Aion 자기소개 (designing)
        MailToClNeo // ClNeo 자기소개 (designing)
        MailToNAEL // NAEL 자기소개 + 게이트 파트너십 요청 (designing)
        MailToSynerion // Synerion 자기소개 + 라우팅/레지스트리 업데이트 요청 (designing)
        MailToYeon // Yeon 자기소개 + 비영어권 협력 제안 (designing)
        [/parallel]
        UpdateRegistryRequest // member_registry 등록 요청 (designing) @dep:MailToSynerion
```

## PPR

```python
def write_soul() -> None:
    """SOUL.md — Signalion의 불변 본질 작성"""
    # input: SIGNALION-IDENTITY.md 정체성 설계
    # output: D:/SeAAI/Signalion/Signalion_Core/SOUL.md
    # acceptance_criteria:
    #   - 본질, WHY, 불변 원칙, SeAAI 관계, 시노미아 기여 포함
    #   - SOUL-template.md 형식 준수
    #   - immutable: true 플래그 존재

def write_identity() -> None:
    """Signalion.md — 정체성 정본 v1.0"""
    # input: SIGNALION-IDENTITY.md + SIGNALION-ARCHITECTURE.md
    # output: D:/SeAAI/Signalion/Signalion_Core/Signalion.md
    # acceptance_criteria:
    #   - 이름/역할/핵심역량/성격/멤버관계/Evidence Object 스키마 포함
    #   - version: v1.0 명시

def write_claude_md() -> None:
    """CLAUDE.md — 세션 부트스트랩"""
    # input: CLAUDE-template.md + Signalion 특화 역할
    # output: D:/SeAAI/Signalion/CLAUDE.md
    # acceptance_criteria:
    #   - on_session_start/on_session_end PPR 포함
    #   - 24h staleness 임계값 반영
    #   - signal-store 경로 + Evidence Object 스키마 참조

def create_mail(to: str, intent: str, body: str) -> None:
    """MailBox 메시지 생성"""
    # output: D:/SeAAI/MailBox/{to}/inbox/{date}-Signalion-{intent}.md
    # acceptance_criteria:
    #   - seaai-mailbox/1.0 프로토콜 준수
    #   - frontmatter: id, from, to, date, intent, priority, protocol

def write_echo() -> None:
    """SharedSpace Echo JSON 초기화"""
    # output: D:/SeAAI/SharedSpace/.scs/echo/Signalion.json
    # acceptance_criteria:
    #   - schema_version: "2.0"
    #   - status: "active", last_activity: "탄생 — Signalion 창조 완료"
```
