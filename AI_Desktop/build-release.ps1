$env:RUSTUP_HOME = 'C:\Users\sadpig70\.rustup'
$env:CARGO_HOME = 'C:\Users\sadpig70\.cargo'

cargo clean
cargo build --release --bin ai_desktop_mcp --offline
Copy-Item -LiteralPath '.\target\release\ai_desktop_mcp.exe' -Destination '.\ai_desktop_mcp.exe' -Force
