use crate::core::{Permission, Tool, ToolContext, ToolResult};
use anyhow::Result;
use chrono::Utc;
use once_cell::sync::Lazy;
use prometheus::{register_histogram, Histogram};
#[cfg(feature = "redis-support")]
use redis::aio::MultiplexedConnection as RedisConnection;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::time::Duration;
// sysinfo 크레이트 필요 (Cargo.toml에 있는지 확인 필요, 없으면 추가)
use sysinfo::System;
use tokio::{task, time::sleep};
use tracing::instrument;

/// Prometheus metrics
static CPU_PCT_HIST: Lazy<Histogram> = Lazy::new(|| {
    register_histogram!(
        "system_info_cpu_pct",
        "CPU usage percentage observed by system_info tool",
        vec![1.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 99.0, 100.0]
    )
    .expect("register histogram")
});
static MEM_USED_GB_HIST: Lazy<Histogram> = Lazy::new(|| {
    register_histogram!(
        "system_info_mem_used_gb",
        "Memory used (GiB) observed by system_info tool",
        vec![0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
    )
    .expect("register histogram")
});

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct SysReq {
    /// "snapshot" | "sample" (기본: snapshot)
    #[serde(default)]
    op: String,

    /// 샘플링 반복 횟수 (기본 1)
    #[serde(default = "default_iterations")]
    iterations: u32,

    /// 샘플링 간격(ms) (기본 1000)
    #[serde(default = "default_interval_ms")]
    interval_ms: u64,

    /// 프로세스 상위 K (0이면 미집계)
    #[serde(default)]
    topk: usize,

    /// 결과를 Redis로 적재할 URL(옵션, redis-support에서만 사용)
    #[serde(default)]
    redis_url: Option<String>,

    /// Redis key (기본 "system_info:samples")
    #[serde(default = "default_redis_key")]
    redis_key: String,

    /// CPU 변화량 최소 임계값(%) — sample 모드에서만 사용 (기본 0: 항상 기록)
    #[serde(default)]
    min_cpu_pct: f32,
}

fn default_iterations() -> u32 {
    1
}
fn default_interval_ms() -> u64 {
    1000
}
fn default_redis_key() -> String {
    "system_info:samples".to_string()
}

/// 시스템 정보 수집 툴
#[derive(Default)]
pub struct SystemInfoTool;

#[async_trait::async_trait]
impl Tool for SystemInfoTool {
    fn name(&self) -> &'static str {
        "system_info"
    }
    fn description(&self) -> &'static str {
        "Returns basic system information (OS, CPU, Memory)."
    }

    // 읽기 권한만 필요
    fn required_permissions(&self) -> Permission {
        Permission(Permission::READ)
    }

    // [NEW] MCP 스키마 정의
    fn input_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {}, // 입력 파라미터 없음
        })
    }

    async fn run(&self, _ctx: &ToolContext, _payload: Value) -> Result<Value> {
        let mut sys = System::new_all();
        sys.refresh_all();

        let info = json!({
            "os_name": System::name(),
            "os_version": System::os_version(),
            "host_name": System::host_name(),
            "cpu_count": sys.cpus().len(),
            "total_memory": sys.total_memory(),
            "used_memory": sys.used_memory(),
        });

        Ok(info)
    }
}

/// 단발 스냅샷 수집 (sysinfo 0.37 API)
async fn snapshot(topk: usize) -> Result<Value> {
    let snap = task::spawn_blocking(move || {
        let mut sys = System::new_all();

        // CPU%는 두 번 읽어야 현실적 값
        std::thread::sleep(Duration::from_millis(200));
        sys.refresh_cpu_all();

        let cpu_pct = sys.global_cpu_usage() as f64;

        let total_mem_kib = sys.total_memory();
        let used_mem_kib = sys.used_memory();
        let used_gib = (used_mem_kib as f64) / (1024.0 * 1024.0);

        // 프로세스 Top-K (선택)
        let procs: Vec<Value> = if topk > 0 {
            let mut v: Vec<_> = sys
                .processes()
                .iter()
                .map(|(pid, p)| {
                    json!({
                        "pid": pid.as_u32(),
                        "name": p.name(),
                        "cpu_pct": p.cpu_usage(),
                        "memory_kib": p.memory(),
                    })
                })
                .collect();
            v.sort_by(|a, b| {
                let ac = a.get("cpu_pct").and_then(|x| x.as_f64()).unwrap_or(0.0);
                let bc = b.get("cpu_pct").and_then(|x| x.as_f64()).unwrap_or(0.0);
                bc.partial_cmp(&ac).unwrap_or(std::cmp::Ordering::Equal)
            });
            v.truncate(topk);
            v
        } else {
            Vec::new()
        };

        CPU_PCT_HIST.observe(cpu_pct);
        MEM_USED_GB_HIST.observe(used_gib);

        Ok::<Value, anyhow::Error>(json!({
            "ts_utc": Utc::now().to_rfc3339(),
            "cpu_pct": cpu_pct,
            "mem": {
                "total_kib": total_mem_kib,
                "used_kib": used_mem_kib,
                "used_gib": used_gib
            },
            "top_processes": procs
        }))
    })
    .await??;

    Ok(snap)
}

/// 반복 샘플링 (+옵션: Redis 적재는 feature로 분리)
async fn run_sampling(req: SysReq) -> ToolResult {
    // ── Redis 연결 (feature off면 컴파일 제외 → 경고/에러 0)
    #[cfg(feature = "redis-support")]
    let mut redis_conn: Option<RedisConnection> = if let Some(url) = &req.redis_url {
        let client = redis::Client::open(url.as_str())?;
        Some(client.get_multiplexed_async_connection().await?)
    } else {
        None
    };

    #[cfg(not(feature = "redis-support"))]
    let _ = &req.redis_url; // 미사용 경고 방지

    let mut last_cpu = None::<f64>;
    let iters = req.iterations.max(1);

    for i in 0..iters {
        let snap = snapshot(req.topk).await?;
        let cpu = snap.get("cpu_pct").and_then(|v| v.as_f64()).unwrap_or(0.0);

        let pass = if req.min_cpu_pct > 0.0 {
            match last_cpu {
                None => true,
                Some(prev) => (cpu - prev).abs() >= req.min_cpu_pct as f64,
            }
        } else {
            true
        };

        if pass {
            last_cpu = Some(cpu);

            // ── Redis push (feature on일 때만)
            #[cfg(feature = "redis-support")]
            if let Some(conn) = &mut redis_conn {
                let line = snap.to_string();
                redis::cmd("LPUSH")
                    .arg(&req.redis_key)
                    .arg(line)
                    .query_async::<_, i64>(conn)
                    .await?;
            }
        }

        if i + 1 < iters {
            sleep(Duration::from_millis(req.interval_ms.max(1))).await;
        }
    }

    Ok(json!({
        "ok": true,
        "samples": iters,
        // feature 상태에 따라 일관된 필드 유지
        "pushed_to_redis": cfg!(feature = "redis-support") && req.redis_url.is_some(),
        "redis_key": req.redis_key
    }))
}
