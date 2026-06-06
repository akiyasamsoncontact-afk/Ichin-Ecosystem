use clap::Parser;
use ichin_account_core::storage::AccountStore;
use ichin_mail::api::start_api_server;
use ichin_mail::delivery::queue::DeliveryQueue;
use ichin_mail::internal::config::Config;
use ichin_mail::internal::logger;
use rustls::crypto::ring as provider;
use ichin_mail::protocol::envelope::Envelope;
use ichin_mail::security::keys::KeyPair;
use ichin_mail::security::sign::sign_envelope;
use ichin_mail::spam::ReputationScorer;
use ichin_mail::storage::mailbox::Mailbox;
use ichin_mail::transport::server::IchinServer;
use ichin_mail::transport::tls::server_config;
use std::sync::Arc;

#[derive(Parser)]
#[command(name = "ichin-server", version)]
struct Args {}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    logger::init();

    let _ = provider::default_provider().install_default();

    let config = Config::from_env();

    tracing::info!("Starting Ichin Mail Server");
    tracing::info!("  Server name: {}", config.server_name);
    tracing::info!("  Listen: {}", config.listen_addr);
    tracing::info!("  API: 0.0.0.0:8080");

    // Initialize TLS
    let tls_config = server_config(&config.tls_cert_path, &config.tls_key_path)?;

    // Initialize delivery queue
    let delivery_queue = Arc::new(DeliveryQueue::open(
        &format!("{}_delivery", config.db_path.to_str().unwrap()),
    )?);

    // Initialize mailbox (user-facing storage)
    let mailbox = Arc::new(Mailbox::open(
        &format!("{}_mailbox", config.db_path.to_str().unwrap()),
    )?);

    // Initialize reputation scorer
    let reputation = Arc::new(ReputationScorer::new());

    // Generate server keys
    let server_keys = Arc::new(KeyPair::generate());
    tracing::info!("Server key ID: {}", server_keys.key_id);

    // Create Ichin protocol message handler
    let handler: ichin_mail::transport::server::MessageHandler = {
        let delivery_queue = delivery_queue.clone();
        let mailbox = mailbox.clone();
        let reputation = reputation.clone();
        let server_keys = server_keys.clone();

        Arc::new(move |data: Vec<u8>| -> Result<Vec<u8>, String> {
            let mut envelope: Envelope =
                serde_json::from_slice(&data).map_err(|e| e.to_string())?;

            ichin_mail::delivery::validate::validate_envelope(&envelope)?;
            sign_envelope(&mut envelope, &server_keys).map_err(|e| e.to_string())?;
            delivery_queue.enqueue(&envelope).map_err(|e| e.to_string())?;

            let domain = envelope.from.split('@').nth(1).unwrap_or("unknown");
            tokio::task::block_in_place(|| {
                tokio::runtime::Handle::current().block_on(async {
                    reputation.record_message(domain, false).await;
                });
            });

            // Store in mailbox
            let msg = ichin_mail::storage::mailbox::Message {
                id: envelope.message_id.to_string(),
                from_name: envelope.from.split('@').next().unwrap_or("unknown").to_string(),
                from_email: envelope.from.clone(),
                to: envelope.to.iter().map(|t| ichin_mail::storage::mailbox::Recipient {
                    name: t.clone(),
                    email: t.clone(),
                }).collect(),
                subject: envelope.subject.clone(),
                body: envelope.body.clone(),
                timestamp: envelope.timestamp,
                folder: "inbox".to_string(),
                unread: true,
                starred: false,
                attachments: envelope.attachments.iter().map(|a| ichin_mail::storage::mailbox::AttachmentRef {
                    name: a.filename.clone(),
                    size: format!("{} bytes", a.size_bytes),
                    hash: Some(a.hash.clone()),
                }).collect(),
            };
            let _ = mailbox.store_message(&msg);

            serde_json::to_vec(&serde_json::json!({
                "status": "accepted",
                "message_id": envelope.message_id.to_string(),
                "signature": envelope.signature,
                "signing_key_id": envelope.signing_key_id,
            }))
            .map_err(|e| e.to_string())
        })
    };

    // Start Ichin protocol server
    let mut ichin_server = IchinServer::bind(
        &config.listen_addr,
        tls_config,
        config.server_name.clone(),
    )
    .await?;
    ichin_server.set_handler(handler);

    // Initialize account store (shared with Account system)
    let account_store = AccountStore::new("account_data")?;

    // Start HTTP API server
    let api_mailbox = mailbox.clone();
    let api_delivery_queue = delivery_queue.clone();
    let api_server_keys = server_keys.clone();

    tokio::spawn(async move {
        if let Err(e) = start_api_server(
            "0.0.0.0:8080",
            api_mailbox,
            api_delivery_queue,
            api_server_keys,
            account_store,
        )
        .await
        {
            tracing::error!("API server error: {}", e);
        }
    });

    tracing::info!("Ichin Mail fully operational");
    ichin_server.run().await?;

    Ok(())
}
