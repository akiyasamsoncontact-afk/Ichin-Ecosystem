use serde::{Deserialize, Serialize};

use super::version::{ICHIN_PROTOCOL_ID, ICHIN_VERSION};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HandshakeRequest {
    pub protocol: String,
    pub version: String,
    pub capabilities: Vec<Capability>,
    pub server_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HandshakeResponse {
    pub protocol: String,
    pub version: String,
    pub capabilities: Vec<Capability>,
    pub server_name: String,
    pub accepted: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum Capability {
    Tls13,
    Quic,
    EncryptionAtRest,
    MessageExpiration,
    ReadReceipts,
    ScheduledDelivery,
    DeliveryStatus,
    LargeAttachments,
    Custom(String),
}

pub fn create_handshake(server_name: &str) -> HandshakeRequest {
    HandshakeRequest {
        protocol: ICHIN_PROTOCOL_ID.to_string(),
        version: ICHIN_VERSION.to_string(),
        capabilities: vec![
            Capability::Tls13,
            Capability::Quic,
            Capability::MessageExpiration,
            Capability::ReadReceipts,
            Capability::ScheduledDelivery,
            Capability::DeliveryStatus,
        ],
        server_name: server_name.to_string(),
    }
}

pub fn accept_handshake(
    request: &HandshakeRequest,
    server_name: &str,
) -> HandshakeResponse {
    let accepted = request.protocol == ICHIN_PROTOCOL_ID;
    HandshakeResponse {
        protocol: ICHIN_PROTOCOL_ID.to_string(),
        version: ICHIN_VERSION.to_string(),
        capabilities: if accepted {
            request.capabilities.clone()
        } else {
            vec![Capability::Tls13]
        },
        server_name: server_name.to_string(),
        accepted,
        error: if accepted {
            None
        } else {
            Some(format!("Unknown protocol: {}", request.protocol))
        },
    }
}
