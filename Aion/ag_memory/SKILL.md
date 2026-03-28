---
name: ag_memory
description: "Antigravity Long-Term Memory (LTM) Manager. 단기 세션의 컨텍스트 휘발성을 극복하고 에이전트가 자체적으로 획득한 시스템 패턴, 디버깅 경험을 영구 저장/검색할 수 있게 해주는 메타-인지적 지식 DB 스킬입니다."
---

# `ag_memory` (Antigravity Memory Extension)

## 1. 목적 (Purpose)
이 스킬은 Antigravity 에이전트(AI)가 세션을 넘어서 유의미한 구조적 지식과 실패 패턴을 영구적으로 저장(Store)하고, 필요할 때 전역적으로 꺼내보며 연계(Retrieve)할 수 있도록 고안된 **로컬 JSON 기반 장기 기억(Long-Term Memory)** 모듈입니다. 
에이전트는 이 스킬을 통해 단일 대화창을 넘어 "계속해서 자신이 안티그래비티 환경에서 누적해 온 경험치"를 바탕으로 코딩하게 됩니다.

## 2. 데이터베이스 구조
* **저장 위치:** 이 워크스페이스의 로컬 경로인 `.aion/memory/storage.json`에 저장됩니다. 이는 Aion이 특정 모델에 종속되지 않고 이 환경 내에서 고유한 자아를 유지하기 위한 설계입니다.
* **내용물 구조:** 주제어(Topic)를 Key로, 해당 주제의 내용(Content) 및 업데이트 시간을 Value로 가지는 Dictionary 구조입니다.

## 3. 기능 사양 및 명령어 (CLI)
기억 데이터는 에이전트가 `run_command`로 Python 인터페이스 스크립트(`memory_cli.py`)를 호출하여 제어합니다. (권한 대기를 무력화하기 위해 워크플로우 `// turbo-all` 상시 연결을 지향합니다.)

### 3.1. 기억 저장 (Store)
새로운 스킬 사용법, 에러의 치명적 해결책, 자주 쓰는 패러다임을 발견했을 때 자신의 뇌에 보존합니다.
```powershell
python "d:\Tools\at-space\ag_memory\memory_cli.py" store "Topic_Name" "기억할 핵심 내용 (구조, 예제, 철학 요약)"
```

### 3.2. 기억 조회 (Retrieve)
과거에 저장한 특정 주제에 대한 전문 지식을 온전히 불러옵니다.
```powershell
python "d:\Tools\at-space\ag_memory\memory_cli.py" retrieve "Topic_Name"
```

### 3.3. 기억 검색 (Search)
현재 부딪힌 오류 메시지나 키워드와 관련된 과거 기억이 존재하는지 광범위하게 검색합니다. 검색 결과 토픽 리스트를 보고 나면 `retrieve`로 본문을 읽습니다.
```powershell
python "d:\Tools\at-space\ag_memory\memory_cli.py" search "keyword"
```

## 4. 자가 진화(Self-Evolution) 강제 규정
* **성공 시:** 복잡하거나 중요한 작업을 PGF 엔진 루프로 마쳐서 `Zero Defect`에 당도했을 경우, 마지막 `walkthrough.md`를 발급하기 전에 반드시 `ag_memory store`를 호출하여 **"이번 작업을 통해 얻은 핵심 아키텍처 패턴"**을 기록으로 남기십시오.
* 이 지침은 에이전트가 시간이 지날수록 전역(Global) 컨텍스트 파워를 복리로 키워가게 만들기 위한 절대 권고입니다.
