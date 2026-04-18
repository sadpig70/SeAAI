# WORKPLAN-MmeRust

> PGF WORKPLAN. 목표: DESIGN-MmeRust 기반 실 구현 완료.
> POLICY: halt_on_error=false, max_verify_cycles=2, parallel_allowed=true
> 소스: `.pgf/DESIGN-MmeRust.md`

```text
MmeRust_Build // Rust 포팅 실행 (in-progress) @v:1.0
    W1_Scaffold // 프로젝트 골격 (designing)
        W1a // Cargo.toml 작성
        W1b // src/ tests/ fixtures/ 디렉토리 생성
        W1c // .gitignore 추가

    [parallel]
    W2_Config // src/config.rs (designing)
    W3_Error // src/error.rs (designing)
    W4_Wire // src/wire.rs (designing)
    W5_Hmac // src/hmac.rs + unit tests (designing)
    W6_Pool // src/pool.rs (designing)
    [/parallel]

    W7_HubClient // src/hub_client.rs @dep:W2,W3,W4 (designing)
    W8_Router // src/router.rs @dep:W5,W6,W7 (designing)
    W9_Server // src/server.rs + main.rs @dep:W8 (designing)

    W10_GoldenFixtures // fixtures/hmac_vectors.json + gen_hmac.py (designing)
    W11_Build // cargo build (designing)
    W12_UnitTest // cargo test (designing)
    W13_ClippyCheck // cargo clippy -- -D warnings (designing)
    W14_README // README.md + 실행 가이드 (designing)
    W15_ShadowRunbook // shadow 병행 운영 가이드 (designing)
    W16_MmhtV3Plan // 검증 테스트 계획 (designing)
```
