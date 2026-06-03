use std::sync::Arc;

use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::TcpListener;

use crate::delivery::queue::DeliveryQueue;
use crate::gateway::translate::smtp_to_ichin;
use crate::spam::ReputationScorer;

pub struct SmtpGateway {
    listener: TcpListener,
    queue: Arc<DeliveryQueue>,
    reputation: Arc<ReputationScorer>,
}

impl SmtpGateway {
    pub async fn bind(
        addr: &str,
        queue: Arc<DeliveryQueue>,
        reputation: Arc<ReputationScorer>,
    ) -> Result<Self, anyhow::Error> {
        let listener = TcpListener::bind(addr).await?;
        Ok(Self {
            listener,
            queue,
            reputation,
        })
    }

    pub async fn run(&self) -> Result<(), anyhow::Error> {
        tracing::info!("SMTP gateway listening on {}", self.listener.local_addr()?);
        loop {
            let (stream, addr) = self.listener.accept().await?;
            let queue = self.queue.clone();
            let reputation = self.reputation.clone();

            tokio::spawn(async move {
                if let Err(e) = handle_smtp(stream, queue, reputation).await {
                    tracing::error!("SMTP connection error from {}: {}", addr, e);
                }
            });
        }
    }
}

async fn handle_smtp(
    stream: tokio::net::TcpStream,
    queue: Arc<DeliveryQueue>,
    reputation: Arc<ReputationScorer>,
) -> Result<(), anyhow::Error> {
    let (reader, mut writer) = tokio::io::split(stream);
    let mut reader = BufReader::new(reader);
    let mut buf = String::new();

    // Send greeting
    writer.write_all(b"220 Ichin Mail SMTP Gateway Ready\r\n").await?;

    let mut from_addr = String::new();
    let mut to_addrs = Vec::new();
    let mut data_buf = Vec::new();
    let mut in_data = false;

    loop {
        buf.clear();
        let n = reader.read_line(&mut buf).await?;
        if n == 0 {
            return Ok(());
        }

        let line = buf.trim();
        tracing::debug!("SMTP << {}", line);

        if in_data {
            if line == "." {
                in_data = false;
                // Process the message
                let raw_msg = String::from_utf8_lossy(&data_buf);
                match smtp_to_ichin(&raw_msg, &from_addr, &to_addrs) {
                    Ok(envelope) => {
                        let domain = from_addr.split('@').nth(1).unwrap_or("unknown");
                        if let Err(e) = queue.enqueue(&envelope) {
                            tracing::error!("Failed to enqueue message: {}", e);
                            writer.write_all(b"554 Transaction failed\r\n").await?;
                        } else {
                            reputation.record_message(domain, false).await;
                            writer.write_all(b"250 OK: Message queued\r\n").await?;
                        }
                    }
                    Err(e) => {
                        tracing::error!("Failed to translate message: {}", e);
                        writer.write_all(b"554 Transaction failed\r\n").await?;
                    }
                }
                data_buf.clear();
                from_addr.clear();
                to_addrs.clear();
            } else {
                data_buf.extend_from_slice(line.as_bytes());
                data_buf.push(b'\n');
            }
            continue;
        }

        let response = if line.starts_with("EHLO") || line.starts_with("HELO") {
            "250 Ichin Mail Gateway\r\n"
        } else if line.starts_with("MAIL FROM:") {
            from_addr = line.trim_start_matches("MAIL FROM:").trim().to_string();
            from_addr = from_addr.trim_matches('<').trim_matches('>').to_string();
            "250 OK\r\n"
        } else if line.starts_with("RCPT TO:") {
            let addr = line.trim_start_matches("RCPT TO:").trim().to_string();
            let addr = addr.trim_matches('<').trim_matches('>').to_string();
            to_addrs.push(addr);
            "250 OK\r\n"
        } else if line == "DATA" {
            in_data = true;
            "354 Start mail input; end with <CRLF>.<CRLF>\r\n"
        } else if line == "QUIT" {
            writer.write_all(b"221 Bye\r\n").await?;
            return Ok(());
        } else if line == "NOOP" {
            "250 OK\r\n"
        } else if line.starts_with("RSET") {
            from_addr.clear();
            to_addrs.clear();
            data_buf.clear();
            "250 OK\r\n"
        } else {
            "500 Command not recognized\r\n"
        };

        writer.write_all(response.as_bytes()).await?;
    }
}
