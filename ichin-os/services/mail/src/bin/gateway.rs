use std::sync::Arc;

use clap::Parser;
use ichin_mail::delivery::queue::DeliveryQueue;
use ichin_mail::internal::config::Config;
use ichin_mail::internal::logger;
use ichin_mail::spam::ReputationScorer;

#[derive(Parser)]
#[command(name = "ichin-gateway", version)]
struct Args {
    #[arg(short, long)]
    listen_addr: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    logger::init();
    let args = Args::parse();
    let config = Config::from_env();

    let gateway_addr = args
        .listen_addr
        .unwrap_or(config.gateway_listen_addr);

    tracing::info!("Starting Ichin Mail SMTP Gateway on {}", gateway_addr);

    let queue = Arc::new(DeliveryQueue::open(
        config.db_path.to_str().unwrap(),
    )?);
    let reputation = Arc::new(ReputationScorer::new());

    let gateway = ichin_mail::gateway::smtp::SmtpGateway::bind(
        &gateway_addr,
        queue,
        reputation,
    )
    .await?;

    tracing::info!("SMTP Gateway running");
    gateway.run().await?;

    Ok(())
}
