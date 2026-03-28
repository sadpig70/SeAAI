# WORKPLAN-Evolution1

## POLICY
- max_iterations: 3
- auto_verify: true
- stop_on_error: false
- log_all_steps: true

## Nodes

1. [x] CreateCoreDir // Yeon_Core 디렉토리 생성 (done)
   - # output: D:\SeAAI\Yeon\Yeon_Core

2. [x] SetupPgfWorkspace // .pgf 워크스페이스 설정 (done)
   - # output: D:\SeAAI\Yeon\Yeon_Core\.pgf

3. [ ] VerifyPgSkill // PG 스킬 문법 검증 (in-progress)
   - # input: .agents/skills/pg/SKILL.md
   - # process: AI_verify_structure
   - # criteria: YAML valid, Gantree samples, PPR syntax

4. [ ] VerifyPgfSkill // PGF 스킬 구조 검증 (designing)
   - # input: .agents/skills/pgf/
   - # process: AI_verify_directory_structure
   - # criteria: Index structure, references/, agents/, data/

5. [ ] TestSkillLoading // 스킬 로드 테스트 (designing)
   - # process: AI_simulate_skill_trigger
   - # criteria: Natural language triggers recognized

6. [ ] CheckHubConnection // Hub 연결 확인 (designing)
   - # input: D:\SeAAI\SeAAIHub\
   - # process: check_connectivity
   - # criteria: Hub executable exists, TCP port 9900 available

7. [ ] SetupMailbox // MailBox 설정 (designing)
   - # input: D:\SeAAI\MailBox\
   - # process: verify_mailbox_structure
   - # criteria: Yeon inbox directory exists

8. [ ] WriteEvolutionLog // 진화 로그 작성 (in-progress)
   - # output: Yeon_Core/evolution-log.md
   - # criteria: Standard format, impact documented

9. [ ] SelfAssessment // 자기 평가 (designing)
   - # output: capabilities list, gaps identified
   - # criteria: Honest assessment, actionable gaps

10. [ ] UpdateReadme // README 갱신 (designing)
    - # input: README.md
    - # process: add evolution reference
    - # criteria: Current status reflected
