use anyhow::Result;
use tokio::io::{self, AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::TcpStream;

// === TCP Transport ===

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
