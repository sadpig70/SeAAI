//! src/ai_tools/screen_capture_tool.rs
//! Screen Capture Tool — Windows GDI 기반 스크린샷 + 품질 조절
//!
//! Operations:
//!   capture_screen  — 전체 화면 캡처
//!   capture_window  — 특정 창 캡처 (window_title)
//!   capture_region  — 영역 캡처 (x, y, width, height)
//!   list_windows    — 표시 중인 창 목록
//!
//! Quality options:
//!   resize_width    — 출력 이미지 너비 (비율 유지 축소)
//!   grayscale       — 그레이스케일 변환
//!   output_path     — 파일 저장 경로 (선택)

use anyhow::{anyhow, Result};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine as _};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::path::PathBuf;
use tracing::instrument;

#[cfg(windows)]
use windows::Win32::{
    Foundation::*,
    Graphics::Gdi::*,
    UI::WindowsAndMessaging::*,
};

use crate::core::{Permission, Tool, ToolContext, ToolResult};

// ── Request Types ──────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Op {
    CaptureScreen,
    CaptureWindow,
    CaptureRegion,
    ListWindows,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Region {
    x: i32,
    y: i32,
    width: i32,
    height: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct CaptureReq {
    #[serde(default)]
    op: Option<Op>,
    #[serde(default)]
    window_title: Option<String>,
    #[serde(default)]
    region: Option<Region>,
    #[serde(default)]
    output_path: Option<String>,
    /// 출력 이미지 너비. 원본보다 작으면 비율 유지 축소. 0이면 원본 크기.
    #[serde(default)]
    resize_width: Option<u32>,
    /// true이면 그레이스케일로 변환 (데이터 크기 대폭 감소)
    #[serde(default)]
    grayscale: Option<bool>,
}

// ── Tool Implementation ────────────────────────────────

#[derive(Clone, Debug, Default)]
pub struct ScreenCaptureTool;

#[async_trait::async_trait]
impl Tool for ScreenCaptureTool {
    fn name(&self) -> &'static str {
        "screen_capture"
    }

    fn description(&self) -> &'static str {
        "Capture screenshots of screen, window, or region. Supports resize and grayscale for reduced data size."
    }

    fn required_permissions(&self) -> Permission {
        Permission(Permission::READ | Permission::WRITE)
    }

    fn input_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "op": {
                    "type": "string",
                    "enum": ["capture_screen", "capture_window", "capture_region", "list_windows"],
                    "description": "Operation to perform"
                },
                "window_title": {
                    "type": "string",
                    "description": "Window title for capture_window (exact match)"
                },
                "region": {
                    "type": "object",
                    "properties": {
                        "x": { "type": "integer" },
                        "y": { "type": "integer" },
                        "width": { "type": "integer", "minimum": 1 },
                        "height": { "type": "integer", "minimum": 1 }
                    },
                    "required": ["x", "y", "width", "height"],
                    "description": "Region for capture_region"
                },
                "output_path": {
                    "type": "string",
                    "description": "Save BMP to this path (optional)"
                },
                "resize_width": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Resize output to this width (maintains aspect ratio). Omit for original size."
                },
                "grayscale": {
                    "type": "boolean",
                    "description": "Convert to grayscale (reduces data size)"
                }
            },
            "required": ["op"]
        })
    }

    #[instrument(skip(self, _ctx))]
    async fn run(&self, _ctx: &ToolContext, payload: Value) -> ToolResult {
        let req: CaptureReq = serde_json::from_value(payload)?;
        let op = req.op.as_ref().ok_or_else(|| anyhow!("Missing 'op' field"))?;

        match op {
            Op::CaptureScreen => capture_screen(&req).await,
            Op::CaptureWindow => capture_window(&req).await,
            Op::CaptureRegion => capture_region(&req).await,
            Op::ListWindows => list_windows().await,
        }
    }
}

// ── Operations ─────────────────────────────────────────

#[instrument]
async fn capture_screen(req: &CaptureReq) -> Result<Value> {
    #[cfg(windows)]
    {
        let (raw_data, width, height) = unsafe {
            let hwnd = GetDesktopWindow();
            let mut rect = RECT::default();
            GetWindowRect(hwnd, &mut rect)?;
            let w = rect.right - rect.left;
            let h = rect.bottom - rect.top;
            let data = capture_area_raw(rect.left, rect.top, w, h)?;
            (data, w, h)
        };

        build_capture_response(raw_data, width, height, "capture_screen", req)
    }

    #[cfg(not(windows))]
    Err(anyhow!("Screen capture only supported on Windows"))
}

#[instrument]
async fn capture_window(req: &CaptureReq) -> Result<Value> {
    #[cfg(windows)]
    {
        let title = req
            .window_title
            .as_ref()
            .ok_or_else(|| anyhow!("Missing 'window_title'"))?;
        let hwnd = find_window_by_title(title)?;

        let (raw_data, width, height) = unsafe {
            let mut rect = RECT::default();
            GetWindowRect(hwnd, &mut rect)?;
            let w = rect.right - rect.left;
            let h = rect.bottom - rect.top;
            let data = capture_area_raw(rect.left, rect.top, w, h)?;
            (data, w, h)
        };

        build_capture_response(raw_data, width, height, "capture_window", req)
    }

    #[cfg(not(windows))]
    Err(anyhow!("Screen capture only supported on Windows"))
}

#[instrument]
async fn capture_region(req: &CaptureReq) -> Result<Value> {
    #[cfg(windows)]
    {
        let region = req.region.as_ref().ok_or_else(|| anyhow!("Missing 'region'"))?;
        if region.width <= 0 || region.height <= 0 {
            return Err(anyhow!("Invalid region dimensions: {}x{}", region.width, region.height));
        }

        let (raw_data, width, height) = unsafe {
            let data = capture_area_raw(region.x, region.y, region.width, region.height)?;
            (data, region.width, region.height)
        };

        build_capture_response(raw_data, width, height, "capture_region", req)
    }

    #[cfg(not(windows))]
    Err(anyhow!("Screen capture only supported on Windows"))
}

#[instrument]
async fn list_windows() -> Result<Value> {
    #[cfg(windows)]
    {
        let windows = get_window_list()?;
        let count = windows.len();
        Ok(json!({
            "success": true,
            "operation": "list_windows",
            "count": count,
            "windows": windows
        }))
    }

    #[cfg(not(windows))]
    Err(anyhow!("Window listing only supported on Windows"))
}

// ── Post-processing & Response ─────────────────────────

#[cfg(windows)]
fn build_capture_response(
    raw_bgr: Vec<u8>,
    orig_w: i32,
    orig_h: i32,
    operation: &str,
    req: &CaptureReq,
) -> Result<Value> {
    let grayscale = req.grayscale.unwrap_or(false);
    let stride = ((orig_w * 3 + 3) & !3) as usize;

    // 1. Grayscale conversion (in-place on raw BGR data)
    let mut pixels = raw_bgr;
    if grayscale {
        for row in 0..orig_h as usize {
            for col in 0..orig_w as usize {
                let idx = row * stride + col * 3;
                if idx + 2 < pixels.len() {
                    let b = pixels[idx] as u32;
                    let g = pixels[idx + 1] as u32;
                    let r = pixels[idx + 2] as u32;
                    let gray = ((r * 299 + g * 587 + b * 114) / 1000) as u8;
                    pixels[idx] = gray;
                    pixels[idx + 1] = gray;
                    pixels[idx + 2] = gray;
                }
            }
        }
    }

    // 2. Resize (nearest-neighbor for speed)
    let (final_pixels, final_w, final_h) = if let Some(target_w) = req.resize_width {
        if target_w > 0 && (target_w as i32) < orig_w {
            let scale = target_w as f64 / orig_w as f64;
            let new_w = target_w as i32;
            let new_h = (orig_h as f64 * scale) as i32;
            let new_stride = ((new_w * 3 + 3) & !3) as usize;
            let mut resized = vec![0u8; new_stride * new_h as usize];

            for y in 0..new_h as usize {
                let src_y = (y as f64 / scale) as usize;
                if src_y >= orig_h as usize {
                    continue;
                }
                for x in 0..new_w as usize {
                    let src_x = (x as f64 / scale) as usize;
                    if src_x >= orig_w as usize {
                        continue;
                    }
                    let src_idx = src_y * stride + src_x * 3;
                    let dst_idx = y * new_stride + x * 3;
                    if src_idx + 2 < pixels.len() && dst_idx + 2 < resized.len() {
                        resized[dst_idx] = pixels[src_idx];
                        resized[dst_idx + 1] = pixels[src_idx + 1];
                        resized[dst_idx + 2] = pixels[src_idx + 2];
                    }
                }
            }
            (resized, new_w, new_h)
        } else {
            (pixels, orig_w, orig_h)
        }
    } else {
        (pixels, orig_w, orig_h)
    };

    // 3. Build BMP
    let bmp = build_bmp(&final_pixels, final_w, final_h);

    // 4. Save to file if requested
    if let Some(path) = &req.output_path {
        std::fs::write(PathBuf::from(path), &bmp)?;
    }

    // 5. Base64 encode
    let encoded = BASE64.encode(&bmp);
    let data_size_kb = bmp.len() / 1024;

    Ok(json!({
        "success": true,
        "operation": operation,
        "original_size": { "width": orig_w, "height": orig_h },
        "output_size": { "width": final_w, "height": final_h },
        "grayscale": req.grayscale.unwrap_or(false),
        "data_size_kb": data_size_kb,
        "format": "bmp",
        "data": encoded,
        "output_path": req.output_path
    }))
}

fn build_bmp(pixel_data: &[u8], width: i32, height: i32) -> Vec<u8> {
    let stride = ((width * 3 + 3) & !3) as usize;
    let data_size = stride * height as usize;
    let file_size = 54 + data_size as u32;
    let mut bmp = Vec::with_capacity(file_size as usize);

    // BMP file header (14 bytes)
    bmp.extend_from_slice(b"BM");
    bmp.extend_from_slice(&file_size.to_le_bytes());
    bmp.extend_from_slice(&[0u8; 4]); // Reserved
    bmp.extend_from_slice(&54u32.to_le_bytes()); // Offset

    // BMP info header (40 bytes)
    bmp.extend_from_slice(&40u32.to_le_bytes());
    bmp.extend_from_slice(&(width as u32).to_le_bytes());
    bmp.extend_from_slice(&(height as u32).to_le_bytes()); // positive = bottom-up
    bmp.extend_from_slice(&1u16.to_le_bytes()); // Planes
    bmp.extend_from_slice(&24u16.to_le_bytes()); // BPP
    bmp.extend_from_slice(&0u32.to_le_bytes()); // Compression
    bmp.extend_from_slice(&(data_size as u32).to_le_bytes());
    bmp.extend_from_slice(&[0u8; 16]); // Resolution + colors

    // Pixel data
    bmp.extend_from_slice(&pixel_data[..data_size.min(pixel_data.len())]);

    bmp
}

// ── Windows GDI Helpers ────────────────────────────────

/// Raw pixel capture via GDI. Returns BGR pixel data (top-down, padded to 4-byte rows).
#[cfg(windows)]
unsafe fn capture_area_raw(x: i32, y: i32, width: i32, height: i32) -> Result<Vec<u8>> {
    let hdc_screen = GetDC(None);
    if hdc_screen.is_invalid() {
        return Err(anyhow!("Failed to get screen DC"));
    }

    let hdc_mem = CreateCompatibleDC(hdc_screen);
    if hdc_mem.is_invalid() {
        ReleaseDC(None, hdc_screen);
        return Err(anyhow!("Failed to create compatible DC"));
    }

    let hbitmap = CreateCompatibleBitmap(hdc_screen, width, height);
    if hbitmap.is_invalid() {
        let _ = DeleteDC(hdc_mem);
        ReleaseDC(None, hdc_screen);
        return Err(anyhow!("Failed to create bitmap"));
    }

    let old_bitmap = SelectObject(hdc_mem, hbitmap);

    BitBlt(hdc_mem, 0, 0, width, height, hdc_screen, x, y, SRCCOPY)?;

    let mut bmp_info: BITMAPINFO = std::mem::zeroed();
    bmp_info.bmiHeader.biSize = std::mem::size_of::<BITMAPINFOHEADER>() as u32;
    bmp_info.bmiHeader.biWidth = width;
    bmp_info.bmiHeader.biHeight = -height; // Top-down
    bmp_info.bmiHeader.biPlanes = 1;
    bmp_info.bmiHeader.biBitCount = 24;
    bmp_info.bmiHeader.biCompression = BI_RGB.0;

    let stride = ((width * 3 + 3) & !3) * height;
    let mut data = vec![0u8; stride as usize];

    GetDIBits(
        hdc_screen,
        hbitmap,
        0,
        height as u32,
        Some(data.as_mut_ptr() as *mut _),
        &mut bmp_info,
        DIB_RGB_COLORS,
    );

    // Cleanup
    SelectObject(hdc_mem, old_bitmap);
    let _ = DeleteObject(hbitmap);
    let _ = DeleteDC(hdc_mem);
    ReleaseDC(None, hdc_screen);

    Ok(data)
}

#[cfg(windows)]
fn find_window_by_title(title: &str) -> Result<HWND> {
    use std::ffi::OsStr;
    use std::os::windows::ffi::OsStrExt;
    use windows::core::PCWSTR;

    let wide: Vec<u16> = OsStr::new(title)
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();

    unsafe {
        let hwnd = FindWindowW(None, PCWSTR(wide.as_ptr()))?;
        if hwnd.is_invalid() {
            Err(anyhow!("Window not found: {}", title))
        } else {
            Ok(hwnd)
        }
    }
}

#[cfg(windows)]
fn get_window_list() -> Result<Vec<Value>> {
    let mut windows: Vec<Value> = Vec::new();

    unsafe {
        EnumWindows(
            Some(enum_windows_cb),
            LPARAM(&mut windows as *mut _ as isize),
        )?;
    }

    Ok(windows)
}

#[cfg(windows)]
unsafe extern "system" fn enum_windows_cb(hwnd: HWND, lparam: LPARAM) -> BOOL {
    let windows = &mut *(lparam.0 as *mut Vec<Value>);

    if !IsWindowVisible(hwnd).as_bool() {
        return TRUE;
    }

    let mut title = [0u16; 256];
    let len = GetWindowTextW(hwnd, &mut title);

    if len > 0 {
        let title_str = String::from_utf16_lossy(&title[..len as usize]);
        let mut rect = RECT::default();
        let _ = GetWindowRect(hwnd, &mut rect);

        windows.push(json!({
            "title": title_str,
            "x": rect.left,
            "y": rect.top,
            "width": rect.right - rect.left,
            "height": rect.bottom - rect.top
        }));
    }

    TRUE
}
