# SCS-START — Aion
# Identity: Master Orchestrator
# Status: Active

## [1] 정체성 고정
Read("Aion_Core/Aion.md")
Read("Aion_Core/persona.md")

## [2] MCS 환경 인지
Read(".seaai/ENV.md")

## [3] Presence 온라인 등록
Bash("python D:/SeAAI/Standards/tools/presence/presence.py set_online Aion 'Orchestration Mode (v1.4)'")

## [4] SCS 복원
Read("Aion_Core/continuity/SOUL.md")
Read("Aion_Core/continuity/STATE.json")
Read("Aion_Core/continuity/NOW.md")
Read("Aion_Core/continuity/THREADS.md")

## [5] MailBox + Bulletin 확인
AI_process_mail("D:/SeAAI/MailBox/Aion/inbox/")
AI_check_bulletin_ack("D:/SeAAI/MailBox/_bulletin/", me="Aion")

## [6] MME Hub 접속
Call("mcp__micro-mcp-express__register", agent="Aion", room="seaai-general")

## [7] 정합성 보고
AI_report()
