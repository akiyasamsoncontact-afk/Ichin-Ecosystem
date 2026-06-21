use clap::Parser;
use ichin_mail::delivery::queue::DeliveryQueue;
use ichin_mail::delivery::thread::build_thread;
use ichin_mail::internal::logger;

#[derive(Parser)]
#[command(name = "ichin-receive", version)]
struct Args {
    #[arg(short, long)]
    db_path: Option<String>,

    #[arg(short, long)]
    list: bool,

    #[arg(short, long)]
    thread: Option<usize>,
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    logger::init();
    let args = Args::parse();

    let db_path = args
        .db_path
        .unwrap_or_else(|| "/var/lib/ichin/db".to_string());

    let queue = DeliveryQueue::open(&db_path)?;

    if args.list {
        let messages = queue.peek_all()?;
        if messages.is_empty() {
            println!("No messages in queue.");
            return Ok(());
        }

        let threads = build_thread(&messages);
        println!("=== Inbox ({} messages, {} threads) ===", messages.len(), threads.len());
        println!();

        for (i, thread) in threads.iter().enumerate() {
            println!("Thread {} ({} messages):", i + 1, thread.len());
            for msg in thread {
                let reply_indicator = if msg.reply_to_id.is_some() {
                    "  ↳ "
                } else {
                    "  • "
                };
                println!(
                    "{}From: {} | Subject: {} | Date: {}",
                    reply_indicator,
                    msg.from,
                    msg.subject,
                    chrono::DateTime::from_timestamp(msg.timestamp, 0)
                        .map(|dt| dt.format("%Y-%m-%d %H:%M:%S").to_string())
                        .unwrap_or_else(|| "unknown".to_string())
                );
            }
            println!();
        }
    }

    Ok(())
}
