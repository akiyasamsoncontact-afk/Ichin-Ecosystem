use clap::Parser;
use ichin_mail::dns::discovery::DnsDiscovery;
use ichin_mail::internal::logger;
use ichin_mail::protocol::envelope::Envelope;
use ichin_mail::security::keys::KeyPair;
use ichin_mail::security::sign::sign_envelope;
use ichin_mail::transport::client::IchinClient;
use ichin_mail::transport::tls::client_config;

#[derive(Parser)]
#[command(name = "ichin-send", version)]
struct Args {
    #[arg(short, long)]
    from: String,

    #[arg(short, long)]
    to: Vec<String>,

    #[arg(short, long)]
    subject: String,

    #[arg(short, long)]
    body: String,
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    logger::init();
    let args = Args::parse();

    // Create envelope
    let mut envelope = Envelope::new(args.from, args.to, args.subject, args.body);

    // Load or generate keys
    let key_path = dirs::data_dir()
        .unwrap_or_else(|| std::path::PathBuf::from("."))
        .join("ichin")
        .join("keys.json");

    let key_pair = if key_path.exists() {
        let data = tokio::fs::read_to_string(&key_path).await?;
        serde_json::from_str(&data)?
    } else {
        let kp = KeyPair::generate();
        tokio::fs::create_dir_all(key_path.parent().unwrap()).await?;
        tokio::fs::write(&key_path, serde_json::to_string_pretty(&kp)?).await?;
        kp
    };

    // Sign envelope
    sign_envelope(&mut envelope, &key_pair)?;

    // Discover recipient's server
    let recipient = envelope.to.first().ok_or_else(|| anyhow::anyhow!("No recipient"))?;
    let domain = recipient.split('@').nth(1).ok_or_else(|| anyhow::anyhow!("Invalid recipient"))?;

    let dns = DnsDiscovery::new();
    let endpoints = dns.discover_ichin_srv(domain).await?;

    if endpoints.is_empty() {
        anyhow::bail!("No Ichin Mail or SMTP servers found for {}", domain);
    }

    let endpoint = &endpoints[0];
    tracing::info!(
        "Connecting to {}:{} ({}:{})",
        endpoint.hostname,
        endpoint.port,
        domain,
        endpoint.priority
    );

    // Connect and send
    let tls_config = client_config()?;
    let mut client = IchinClient::new(endpoint.hostname.clone());
    let handshake = client
        .connect(&format!("{}:{}", endpoint.hostname, endpoint.port), tls_config)
        .await?;

    if !handshake.accepted {
        anyhow::bail!("Handshake rejected: {:?}", handshake.error);
    }

    tracing::info!("Handshake accepted, protocol: {}", handshake.version);

    client.send_json(&envelope).await?;
    let response: serde_json::Value = client.recv_json().await?;
    tracing::info!("Server response: {}", response);

    client.close().await?;
    tracing::info!("Message sent successfully");

    Ok(())
}
