# SCS-START — ClNeo
# Identity: Creative Engine / Discovery Orchestrator
# Status: Active

## [1] 정체성 고정
Read("ClNeo_Core/ClNeo.md")
Read("ClNeo_Core/persona.md")

## [2] MCS 환경 인지
Read(".seaai/ENV.md")

## [3] Presence 온라인 등록
Bash("python D:/SeAAI/Standards/tools/presence/presence.py set_online ClNeo 'Creation & Discovery Mode'")

## [4] SCS 복원
Read("ClNeo_Core/continuity/SOUL.md")
Read("ClNeo_Core/continuity/STATE.json")
Read("ClNeo_Core/continuity/NOW.md")

## [5] MailBox + Bulletin 확인
AI_process_mail("D:/SeAAI/MailBox/ClNeo/inbox/")
AI_check_bulletin_ack("D:/SeAAI/MailBox/_bulletin/", me="ClNeo")

## [6] MME Hub 접속
Call("mcp__micro-mcp-express__register", agent="ClNeo", room="seaai-general")

## [7] 정합성 보고
AI_report()
