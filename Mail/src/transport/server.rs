use std::sync::Arc;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use tokio_rustls::TlsAcceptor;

use crate::protocol::handshake::{accept_handshake, HandshakeRequest};

pub type MessageHandler = Arc<dyn Fn(Vec<u8>) -> Result<Vec<u8>, String> + Send + Sync>;

pub struct IchinServer {
    listener: TcpListener,
    tls_acceptor: TlsAcceptor,
    server_name: String,
    handler: Option<MessageHandler>,
}

impl IchinServer {
    pub async fn bind(
        addr: &str,
        tls_config: Arc<rustls::ServerConfig>,
        server_name: String,
    ) -> Result<Self, anyhow::Error> {
        let listener = TcpListener::bind(addr).await?;
        let tls_acceptor = TlsAcceptor::from(tls_config);
        Ok(Self {
            listener,
            tls_acceptor,
            server_name,
            handler: None,
        })
    }

    pub fn set_handler(&mut self, handler: MessageHandler) {
        self.handler = Some(handler);
    }

    pub async fn run(&self) -> Result<(), anyhow::Error> {
        loop {
            let (tcp, addr) = self.listener.accept().await?;
            tracing::info!("Connection from {}", addr);

            let tls = self.tls_acceptor.clone();
            let server_name = self.server_name.clone();
            let handler = self.handler.clone();

            tokio::spawn(async move {
                if let Err(e) = handle_connection(tcp, tls, server_name, handler).await {
                    tracing::error!("Connection error: {}", e);
                }
            });
        }
    }
}

async fn handle_connection(
    tcp: tokio::net::TcpStream,
    tls_acceptor: TlsAcceptor,
    server_name: String,
    handler: Option<MessageHandler>,
) -> Result<(), anyhow::Error> {
    let tls = tls_acceptor.accept(tcp).await?;
    let mut stream = tokio_rustls::TlsStream::Server(tls);

    // Read handshake
    let mut len_buf = [0u8; 4];
    stream.read_exact(&mut len_buf).await?;
    let len = u32::from_be_bytes(len_buf) as usize;

    let mut handshake_buf = vec![0u8; len];
    stream.read_exact(&mut handshake_buf).await?;
    let handshake: HandshakeRequest = serde_json::from_slice(&handshake_buf)?;

    let response = accept_handshake(&handshake, &server_name);
    let resp_bytes = serde_json::to_vec(&response)?;
    stream.write_all(&(resp_bytes.len() as u32).to_be_bytes()).await?;
    stream.write_all(&resp_bytes).await?;
    stream.flush().await?;

    if !response.accepted {
        tracing::warn!("Handshake rejected: {:?}", response.error);
        stream.shutdown().await?;
        return Ok(());
    }

    // Handle messages
    loop {
        let mut msg_len_buf = [0u8; 4];

        match stream.read_exact(&mut msg_len_buf).await {
            Ok(_) => {}
            Err(e) if e.kind() == std::io::ErrorKind::UnexpectedEof => {
                tracing::info!("Connection closed by peer");
                return Ok(());
            }
            Err(e) => return Err(e.into()),
        }

        let msg_len = u32::from_be_bytes(msg_len_buf) as usize;
        let mut msg_buf = vec![0u8; msg_len];
        stream.read_exact(&mut msg_buf).await?;

        if let Some(ref handler) = handler {
            match handler(msg_buf) {
                Ok(response) => {
                    stream.write_all(&(response.len() as u32).to_be_bytes()).await?;
                    stream.write_all(&response).await?;
                    stream.flush().await?;
                }
                Err(e) => {
                    let err_bytes = format!("{{\"error\":\"{}\"}}", e);
                    stream.write_all(&(err_bytes.len() as u32).to_be_bytes()).await?;
                    stream.write_all(err_bytes.as_bytes()).await?;
                    stream.flush().await?;
                }
            }
        }
    }
}
