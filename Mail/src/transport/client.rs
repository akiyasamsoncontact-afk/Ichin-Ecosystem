use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio_rustls::TlsConnector;

use crate::protocol::handshake::{create_handshake, HandshakeResponse};

pub struct IchinClient {
    stream: Option<tokio_rustls::TlsStream<TcpStream>>,
    server_name: String,
}

impl IchinClient {
    pub fn new(server_name: String) -> Self {
        Self {
            stream: None,
            server_name,
        }
    }

    pub async fn connect(
        &mut self,
        addr: &str,
        tls_config: std::sync::Arc<rustls::ClientConfig>,
    ) -> Result<HandshakeResponse, anyhow::Error> {
        let tcp = TcpStream::connect(addr).await?;
        let connector = TlsConnector::from(tls_config);
        let server_name =
            rustls::pki_types::ServerName::try_from(self.server_name.clone())
                .map_err(|_| anyhow::anyhow!("Invalid server name: {}", self.server_name))?;
        let tls = connector.connect(server_name, tcp).await?;
        self.stream = Some(tokio_rustls::TlsStream::Client(tls));

        let handshake = create_handshake(&self.server_name);
        self.send_json(&handshake).await?;
        let response: HandshakeResponse = self.recv_json().await?;
        Ok(response)
    }

    pub async fn send_json<T: serde::Serialize>(
        &mut self,
        data: &T,
    ) -> Result<(), anyhow::Error> {
        let stream = self.stream.as_mut().unwrap();
        let bytes = serde_json::to_vec(data)?;
        let len = (bytes.len() as u32).to_be_bytes();
        stream.write_all(&len).await?;
        stream.write_all(&bytes).await?;
        stream.flush().await?;
        Ok(())
    }

    pub async fn recv_json<T: serde::de::DeserializeOwned>(
        &mut self,
    ) -> Result<T, anyhow::Error> {
        let stream = self.stream.as_mut().unwrap();
        let mut len_buf = [0u8; 4];
        stream.read_exact(&mut len_buf).await?;
        let len = u32::from_be_bytes(len_buf) as usize;

        let mut buf = vec![0u8; len];
        stream.read_exact(&mut buf).await?;

        let value: T = serde_json::from_slice(&buf)?;
        Ok(value)
    }

    pub async fn close(&mut self) -> Result<(), anyhow::Error> {
        if let Some(mut stream) = self.stream.take() {
            stream.shutdown().await?;
        }
        Ok(())
    }
}
