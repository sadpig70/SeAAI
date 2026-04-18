pub mod control_plane;
pub mod diagnostics;
pub mod types;

pub use control_plane::BrowserControlPlane;
pub use diagnostics::{
    build_recovery_advice, classify_browser_diagnosis, diagnose_socket_health,
    probe_browser_doctor, probe_socket_health, BrowserDiagnosis, BrowserDoctorReport,
    BrowserHealthProbe, BrowserSocketHealth,
};
pub use types::{
    BrowserActionPlan, BrowserDialogPlan, BrowserProfileInfo, BrowserProfileListing,
    BrowserSessionRecord, BrowserSnapshotRecord, BrowserSnapshotRef, BrowserTabRecord,
    BrowserTarget, BrowserUploadPlan, RefMode, SnapshotFormat,
};
