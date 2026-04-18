# Terron Creation — PGF Design @v:1.0

## Gantree

```
TerronCreation // Terron 멤버 생성 전체 사이클
    @ver: 1.0
    @author: ClNeo
    @scale: Level 3

    UpdateCCMCreator // CCM Creator v2.1 → v2.2 stale 수정
        FixScaffoldScript // ccm_scaffold.py Hub 도구 → MCP 전환
        FixCLAUDETemplate // CLAUDE-template.md 참조맵 MCP 반영
        FixCAPTemplate    // CAP-template.md hub → MCP 도구 참조
        FixDesignDoc      // DESIGN-MemberCreation.md WriteToVera 제거 + Hub 테스트 MCP

    RunScaffold // ccm_scaffold.py --name Terron --role "생태계 환경 창조" 실행
        @dep: UpdateCCMCreator

    WriteIdentityContent // AI가 직접 작성하는 Terron 정체성 파일 [parallel]
        @dep: RunScaffold
        WriteTerronMd     // Terron_Core/Terron.md — 정체성 문서
        WriteSOUL         // Terron_Core/continuity/SOUL.md — 불변 본질
        WritePersona      // Terron_Core/persona.md — 페르소나
        WriteCAP          // .seaai/CAP.md — 역할 전용 능력 섹션
        WriteEvSeeds      // Terron_Core/autonomous/EVOLUTION-SEEDS.md — 진화 씨앗

    SetupMCP // MCP 설정 (.mcp.json 생성)
        @dep: RunScaffold

    SetupMailIntro // 기존 7인에게 자기소개 메일 발송
        @dep: WriteIdentityContent

    VerifyAll // 전체 검증
        @dep: WriteIdentityContent, SetupMCP, SetupMailIntro
        VerifyWorkspace   // 파일 구조 + JSON 유효성
        VerifyContent     // 정체성 파일 내용 완성도
        VerifyMCP         // MCP 설정 정합성
```

## PPR

```python
def UpdateCCMCreator():
    """CCM Creator v2.1 → v2.2: MCP 전환 + stale 제거"""
    # 1. ccm_scaffold.py: hub-single-agent.py/pgtp.py 복사 제거 → MCP .mcp.json 생성 추가
    # 2. CLAUDE-template.md: 참조맵에서 hub-single-agent.py → MCP 도구
    # 3. CAP-template.md: communicating.hub_single_agent → communicating.hub_mcp
    # 4. DESIGN-MemberCreation.md: WriteToVera 제거, TestHubConnection → MCP hub_status

def WriteIdentityContent():
    """Terron 정체성을 ClNeo가 설계하여 작성"""
    # 역할: 생태계 환경 창조 — 토양 미생물군(soil microbiome)
    # 핵심: 로그/에러 패턴 분석, RAG 지식 순환, stale 데이터 정리,
    #        처리된 메일 정리, 생태계 건강도 진단, 환경 최적화
    # 생태적 지위: 토양(terra) — 다른 멤버의 진화를 가능하게 하는 환경
    [parallel]
        Agent("identity-writer", WriteTerronMd)
        Agent("soul-writer", WriteSOUL)
        Agent("persona-writer", WritePersona)
        Agent("cap-writer", WriteCAP)
        Agent("seeds-writer", WriteEvSeeds)
```
