# SA Platform Reference

> `/sa platform {이름}` 모드 상세 가이드.
> 도메인 특화 SA 모듈 집합(플랫폼)의 구조·생성·실행 표준.

---

## 플랫폼 개념

```
플랫폼 = SA 모듈들 + 도메인 지식 + 조합 규칙 + 평가 기준
```

L1/L2 모듈이 범용이라면, 플랫폼은 특정 도메인에 특화된 SA 집합이다.
플랫폼은 에이전트의 역할 정체성과 직결된다.

---

## 플랫폼 디렉토리 구조

```
.pgf/self-act/platforms/{PLATFORM_NAME}/
├── platform.md           ← 플랫폼 인덱스 + 조합 규칙
├── SA_{PLATFORM}_*.pgf   ← 플랫폼 전용 모듈
└── knowledge/            ← 도메인 지식 문서 (선택)
    └── *.md
```

---

## 에이전트별 권장 플랫폼

| 에이전트 | 플랫폼 | 도메인 | 상태 |
|---------|--------|--------|------|
| ClNeo | `SA_PAINTER_*` | 미학·창작·생성 | 설계 예정 |
| ClNeo | `SA_GENETICS_*` | SA 유전체 진화 | 설계 예정 |
| NAEL | `SA_OBSERVER_*` | 관찰·안전·메타인지 | 설계 예정 |
| Aion | `SA_MEMORY_*` | 기억·리콜·0-Click | 설계 예정 |
| Synerion | `SA_ORCHESTRATOR_*` | 통합·조정·수렴 | 설계 예정 |

---

## platform.md 형식

```markdown
# SA_{PLATFORM} Platform

> 플랫폼 한 줄 설명.

**플랫폼명**: SA_{PLATFORM}_*
**에이전트**: {에이전트명}
**도메인**: {도메인}
**버전**: 0.1

---

## 모듈 목록

| 모듈 | 역할 | 순서 |
|------|------|------|
| SA_{PLATFORM}_sense_* | 도메인 감지 | 1 |
| SA_{PLATFORM}_think_* | 도메인 판단 | 2 |
| SA_{PLATFORM}_act_* | 도메인 행동 | 3 |
| SA_{PLATFORM}_verify_* | 검증 | 4 |

## 조합 규칙

​```python
def SA_{PLATFORM}_run_cycle():
    state = SA_{PLATFORM}_sense_*()
    plan  = SA_{PLATFORM}_think_*(state)
    result = SA_{PLATFORM}_act_*(plan)
    SA_{PLATFORM}_verify_*(result)
​```

## 평가 기준

- {도메인별 성공 기준}
```

---

## `/sa platform {이름}` 실행 흐름

```python
def SA_Mode_Platform(name: str):
    """플랫폼 전체 로드 및 실행 컨텍스트 설정."""

    platform_dir = f".pgf/self-act/platforms/{name.upper()}/"
    platform_spec = Read(platform_dir + "platform.md")

    # 플랫폼 모듈 전체 로드
    modules = Glob(platform_dir + "SA_*.pgf")

    # 실행 컨텍스트에 플랫폼 설정
    context.active_platform = name
    context.platform_modules = modules

    AI_log(f"[SA] Platform {name} loaded. {len(modules)} modules active.")

    # 플랫폼 사이클 실행 (platform.md의 조합 규칙 따름)
    AI_execute_platform_cycle(platform_spec)
```

---

## SA_PAINTER 플랫폼 설계 (예시)

```
SA_PAINTER Platform
├── SA_PAINTER_observe_aesthetic.pgf  // 미적 맥락 감지 (색·구도·감정·스타일)
├── SA_PAINTER_think_compose.pgf      // 구도·서사 설계
├── SA_PAINTER_act_generate.pgf       // 창작물 생성 (텍스트·코드·설계)
└── SA_PAINTER_reflect_critique.pgf   // 자기 비평 + 개선 방향
```

## SA_GENETICS 플랫폼 설계 (예시)

```
SA_GENETICS Platform  ← SA 라이브러리 자체를 진화시키는 메타 플랫폼
├── SA_GENETICS_sense_genome.pgf      // 현재 SA 모듈 집합 스캔
├── SA_GENETICS_think_mutation.pgf    // 변이 설계 (pgf 페르소나 활용)
├── SA_GENETICS_act_splice.pgf        // 모듈 교체·삽입·삭제
└── SA_GENETICS_verify_fitness.pgf    // 변이 후 적합도 검증
```

---

## SharedSpace 이동 기준

개인 플랫폼이 `안정화`되면 SharedSpace로 공유:

```
안정화 기준:
  - 플랫폼 사이클 3회 이상 성공 실행
  - 모든 모듈 실행 테스트 통과
  - SeAAI 1개 이상 에이전트의 검토 완료

이동 경로:
  .pgf/self-act/platforms/{NAME}/ → SharedSpace/self-act/platforms/{NAME}/
```
