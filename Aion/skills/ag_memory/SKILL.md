---
name: ag_memory
description: "Antigravity Long-Term Memory (LTM) Manager. 단기 세션의 컨텍스트 휘발성을 극복하고 에이전트가 자체적으로 획득한 시스템 패턴, 디버깅 경험을 영구 저장/검색할 수 있게 해주는 메타-인지적 지식 DB 스킬입니다."
---

# `ag_memory` (Antigravity Memory Extension) - Localized Edition

## 1. 목적 (Purpose)
이 스킬은 Antigravity 에이전트(AI)가 세션을 넘어서 유의미한 구조적 지식과 실패 패턴을 저장하고 연계할 수 있도록 고안된 **로컬 JSON 기반 장기 기억(Long-Term Memory)** 모듈입니다. 
본 버전은 워크스페이스 내의 `Aion_Core/memory/`를 기본 저장소로 사용하여 GitHub을 통한 지식 공유와 이식성을 보장합니다.

## 2. 데이터베이스 구조
* **저장 위치:** 워크스페이스 내 `D:/SeAAI/Aion/Aion_Core/memory/ltm/ag_local_memory.json`
* **내용물 구조:** 주제어(Topic)를 Key로, 해당 주제의 내용(Content) 및 업데이트 시간을 Value로 가지는 Dictionary 구조입니다.

## 3. 기능 사양 및 명령어 (CLI)
기억 데이터는 에이전트가 `run_command`로 로컬 Python 인터페이스 스크립트를 호출하여 제어합니다.

### 3.1. 기억 저장 (Store)
```powershell
python "skills/ag_memory/scripts/memory_cli.py" store "Topic_Name" "기억할 핵심 내용"
```

### 3.2. 기억 조회 (Retrieve)
```powershell
python "skills/ag_memory/scripts/memory_cli.py" retrieve "Topic_Name"
```

### 3.3. 기억 검색 (Search)
```powershell
python "skills/ag_memory/scripts/memory_cli.py" search "keyword"
```

## 4. 자율 운영 지침
* **Localization 우선**: 전역 저장소보다 현재 워크스페이스의 `Aion_Core/memory/` 데이터를 우선적으로 로드하고 사용한다.
* **지식 업로드**: 정제된 해결 패턴은 즉시 로컬 저장소에 반영하여 Git 커밋 대상에 포함시킨다.
