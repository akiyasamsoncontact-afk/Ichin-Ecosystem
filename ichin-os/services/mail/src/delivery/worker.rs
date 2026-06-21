use std::sync::Arc;
use std::time::Duration;

use tokio::time::sleep;

use crate::delivery::queue::DeliveryQueue;
use crate::dns::discovery::DnsDiscovery;
use crate::extensions::{expiration, receipts, schedule};
use crate::protocol::envelope::Envelope;
use crate::transport::client::IchinClient;
use crate::transport::tls;

const POLL_INTERVAL_SECS: u64 = 5;
const MAX_RETRIES: u32 = 3;

pub async fn start_delivery_worker(
    delivery_queue: Arc<DeliveryQueue>,
    server_keys: Arc<crate::security::keys::KeyPair>,
) {
    let dns = DnsDiscovery::new();
    let tls_config = tls::client_config().expect("Failed to build client TLS config");

    tracing::info!("Delivery worker started (poll every {}s)", POLL_INTERVAL_SECS);

    loop {
        while let Ok(Some(envelope)) = delivery_queue.dequeue() {
            if let Err(e) = process_envelope(
                &envelope,
                &delivery_queue,
                &dns,
                &tls_config,
                &server_keys,
            )
            .await
            {
                tracing::error!("Delivery worker error for {}: {}", envelope.message_id, e);
                delivery_queue
                    .update_status(
                        envelope.message_id,
                        "failed".to_string(),
                        Some(e.to_string()),
                    )
                    .await;
            }
        }

        sleep(Duration::from_secs(POLL_INTERVAL_SECS)).await;
    }
}

async fn process_envelope(
    envelope: &Envelope,
    queue: &DeliveryQueue,
    dns: &DnsDiscovery,
    tls_config: &Arc<rustls::ClientConfig>,
    server_keys: &Arc<crate::security::keys::KeyPair>,
) -> Result<(), anyhow::Error> {
    // — Extension checks —

    // 1. Expiration: skip if message has expired
    if expiration::is_expired(envelope) {
        queue
            .update_status(
                envelope.message_id,
                "expired".to_string(),
                Some("Message expired before delivery".to_string()),
            )
            .await;
        tracing::info!("Skipped expired message {}", envelope.message_id);
        return Ok(());
    }

    // 2. Scheduled delivery: re-enqueue if not yet ready
    if !schedule::is_ready_for_delivery(envelope) {
        queue.enqueue(envelope)?;
        return Ok(());
    }

    // — Delivery —
    let recipient = envelope
        .to
        .first()
        .ok_or_else(|| anyhow::anyhow!("No recipient in envelope {}", envelope.message_id))?;
    let domain = recipient
        .split('@')
        .nth(1)
        .ok_or_else(|| anyhow::anyhow!("Invalid recipient address: {}", recipient))?;

    let endpoints = dns.discover_ichin_srv(domain).await?;
    if endpoints.is_empty() {
        anyhow::bail!("No Ichin Mail servers found for domain {}", domain);
    }

    let endpoint = &endpoints[0];

    let mut client = IchinClient::new(endpoint.hostname.clone());
    let handshake = client
        .connect(
            &format!("{}:{}", endpoint.hostname, endpoint.port),
            tls_config.clone(),
        )
        .await?;

    if !handshake.accepted {
        anyhow::bail!(
            "Handshake rejected by {}: {:?}",
            endpoint.hostname,
            handshake.error
        );
    }

    client.send_json(envelope).await?;
    let response: serde_json::Value = client.recv_json().await?;
    client.close().await?;

    // 3. Read receipt: if requested, the envelope metadata already carries
    //    the flag; the receiving server will handle generating the receipt.
    if receipts::has_read_receipt(envelope) {
        tracing::info!(
            "Read receipt requested for message {}",
            envelope.message_id
        );
    }

    queue
        .update_status(
            envelope.message_id,
            "delivered".to_string(),
            None,
        )
        .await;

    tracing::info!(
        "Delivered message {} to {} (response: {:?})",
        envelope.message_id,
        domain,
        response,
    );

    Ok(())
}
