use anyhow::Result;
use tokio::io::{self, AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::TcpStream;

// === Stdio Transport (기존) ===

pub struct StdioTransport {
    stdin: BufReader<io::Stdin>,
    stdout: io::Stdout,
}

impl StdioTransport {
    pub fn new() -> Self {
        Self {
            stdin: BufReader::new(io::stdin()),
            stdout: io::stdout(),
        }
    }

    pub async fn read_line(&mut self) -> Result<Option<String>> {
        let mut line = String::new();
        let bytes_read = self.stdin.read_line(&mut line).await?;
        if bytes_read == 0 {
            return Ok(None);
        }
        Ok(Some(line))
    }

    pub async fn write_response(&mut self, json: &str) -> Result<()> {
        let mut payload = String::from(json);
        if !payload.ends_with('\n') {
            payload.push('\n');
        }
        self.stdout.write_all(payload.as_bytes()).await?;
        self.stdout.flush().await?;
        Ok(())
    }
}

// === TCP Transport (신규) ===

pub struct TcpClientTransport {
    reader: BufReader<io::ReadHalf<TcpStream>>,
    writer: io::WriteHalf<TcpStream>,
}

impl TcpClientTransport {
    pub fn new(stream: TcpStream) -> Self {
        let (read_half, write_half) = io::split(stream);
        Self {
            reader: BufReader::new(read_half),
            writer: write_half,
        }
    }

    pub async fn read_line(&mut self) -> Result<Option<String>> {
        let mut line = String::new();
        let bytes_read = self.reader.read_line(&mut line).await?;
        if bytes_read == 0 {
            return Ok(None);
        }
        Ok(Some(line))
    }

    pub async fn write_response(&mut self, json: &str) -> Result<()> {
        let mut payload = String::from(json);
        if !payload.ends_with('\n') {
            payload.push('\n');
        }
        self.writer.write_all(payload.as_bytes()).await?;
        self.writer.flush().await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn stdio_read_write_basics() {
        // BufReader over byte slice simulates stdin
        let input = &b"line-1\nline-2\n"[..];
        let mut reader = BufReader::new(input);

        let mut line1 = String::new();
        let n1 = reader.read_line(&mut line1).await.unwrap();
        assert!(n1 > 0);
        assert_eq!(line1, "line-1\n");

        let mut line2 = String::new();
        let n2 = reader.read_line(&mut line2).await.unwrap();
        assert!(n2 > 0);
        assert_eq!(line2, "line-2\n");

        let mut line3 = String::new();
        let n3 = reader.read_line(&mut line3).await.unwrap();
        assert_eq!(n3, 0); // EOF
    }

    #[tokio::test]
    async fn write_response_appends_newline_once() {
        let mut writer = Vec::new();
        let mut payload = String::from("{\"ok\":true}");
        if !payload.ends_with('\n') {
            payload.push('\n');
        }
        writer.extend_from_slice(payload.as_bytes());

        let mut payload2 = String::from("{\"ok\":false}\n");
        if !payload2.ends_with('\n') {
            payload2.push('\n');
        }
        writer.extend_from_slice(payload2.as_bytes());

        let output = String::from_utf8(writer).unwrap();
        assert_eq!(output, "{\"ok\":true}\n{\"ok\":false}\n");
    }
}
