# WORKPLAN: AI Internet Stack — 전체 구현

```gantree
AIInternetStack
├─ 1.0 L1: Infrastructure — Hub 영속화 + 메시지 버퍼 (ClNeo)
│   ├─ 1.1 chatroom.rs: 메시지 버퍼 (최근 N개 보관, drain 대신)
│   ├─ 1.2 chatroom.rs: room_history에 TTL 적용
│   └─ 1.3 빌드 + 유닛 테스트
├─ 2.0 L2: Discovery — Agent Registry (서브에이전트)
│   ├─ 2.1 registry.py: 에이전트 등록/검색/능력 광고
│   └─ 2.2 Hub 통합 (join 시 자동 등록)
├─ 3.0 L3: Messaging — Topic Pub/Sub (ClNeo + 서브에이전트)
│   ├─ 3.1 chatroom.rs: topic 기반 구독 필터
│   ├─ 3.2 backpressure: inbox 크기 제한 + 오래된 메시지 자동 삭제
│   └─ 3.3 빌드 + 유닛 테스트
├─ 4.0 L5: Application — CU 처리 강화 (서브에이전트)
│   ├─ 4.1 pgtp.py: pipeline 실행 엔진
│   └─ 4.2 pgtp.py: forward 라우팅 구현
├─ 5.0 L6: Orchestration — TeamOrchestrator 실전 구현 (서브에이전트)
│   └─ 5.1 orchestrator.py: 동적 팀 편성 + 파견 루프
├─ 6.0 통합 테스트 — 전 레이어 관통 (멀티에이전트)
│   ├─ 6.1 10에이전트 Discovery + Pub/Sub + PGTP 통합
│   ├─ 6.2 100에이전트 부하 테스트 (병목 재측정)
│   └─ 6.3 TeamOrchestrator로 실제 미니 프로젝트 수행
└─ 7.0 문서화 + 보고
    └─ 7.1 docs/pgtp/SPEC-AIInternetStack.md
```

## POLICY
max_parallel_agents: 3
max_rework: 2
