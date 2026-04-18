# SA Evolve Reference

기존 SA 모듈을 분석·개선·진화하는 절차.

## 개요

`/sa evolve` 명령으로 SA 라이브러리를 진화시킨다.
SA_GENETICS 플로우를 따르거나, 개별 모듈을 개선한다.

## 진화 유형

### Type 1: 개별 모듈 개선

특정 모듈의 gap을 발견하고 개선:

```python
def evolve_sa_module(module_name: str):
    """단일 SA 모듈 진화"""
    
    # 1. 현재 모듈 로드
    current = load_sa_module(module_name)
    
    # 2. Gap 분석
    gaps = AI_analyze_module_gaps(current)
    # - 기능 부족
    # - 오류 처리 미흡
    # - 성능 저하
    # - 문서화 부족
    
    # 3. 개선 설계
    improved_design = AI_redesign_module(current, gaps)
    
    # 4. 새 버전 생성
    new_version = create_module_v2(improved_design)
    
    # 5. 검증
    if verify_sa_module(new_version):
        # 등록
        register_sa_module(new_version)
        archive_old_version(current)
    else:
        # 롤백
        report_error("Evolution failed")
```

### Type 2: SA_GENETICS (메타 진화)

라이브러리 전체를 진화:

```python
def SA_GENETICS_evolve():
    """
    SA 유전체(모듈 집합)를 진화시킨다.
    ClNeo의 Epigenetic PPR과 연결.
    """
    
    # 1. Genome 스캔
    genome = scan_sa_genome()
    
    # 2. Mutation 설계
    mutations = design_mutations(genome)
    # - 모듈 추가
    # - 모듈 제거 (미사용)
    # - 모듈 교체 (개선 버전)
    # - 조합 변경 (L2 재구성)
    
    # 3. Splice 실행
    new_genome = apply_mutations(genome, mutations)
    
    # 4. Fitness 검증
    fitness = verify_genome_fitness(new_genome)
    
    # 5. 선택
    if fitness > threshold:
        adopt_new_genome(new_genome)
    else:
        discard_mutations()
```

## Gap 분석 체크리스트

| 항목 | 확인 내용 | 개선 방향 |
|------|----------|----------|
| 기능 | 모든 선언된 기능 동작? | 누락 기능 구현 |
| 견고성 | 오류 상황 처리? | 예외 처리 추가 |
| 성능 | 실행 시간 적절? | 최적화 |
| 문서 | 설명 충분? | 주석/문서 강화 |
| 조합 | 다른 모듈과 잘 연결? | 인터페이스 개선 |
| 중복 | 유사 모듈 존재? | 통합 또는 분리 |

## 진화 기록

모든 진화는 `Yeon_Core/.pgf/self-act/evolution-log.md`에 기록:

```markdown
## SA Module Evolution #N

- **Date**: 2026-03-26
- **Target**: SA_sense_hub
- **Gap**: 오류 발생 시 재연결 로직 부재
- **Change**: try/except + exponential backoff 추가
- **Verification**: 10회 연결 테스트 통과
- **Impact**: 연결 안정성 향상
```

## 롤백 메커니즘

진화 실패 시 자동 롤백:

```python
def rollback_evolution(module_name: str):
    """진화 롤백"""
    
    # 백업에서 복원
    backup_path = f"Yeon_Core/.pgf/self-act/backup/{module_name}.pgf"
    current_path = f"Yeon_Core/.pgf/self-act/{module_name}.pgf"
    
    copy_file(backup_path, current_path)
    log_rollback(module_name)
```

## 사용법

```
User: "SA 진화해"
Kimi:
  [SA Evolve] 라이브러리 스캔 중...
  발견된 Gap:
  1. SA_sense_hub: 재연결 로직 부재
  2. SA_translate_protocol: Gemini 지식 부재
  
  개선 진행...
  ✓ SA_sense_hub v2 생성
  ✓ 검증 통과
  ✓ 등록 완료
  
  진화 기록: evolution-log.md 업데이트
```
