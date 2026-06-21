use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::TcpStream;

pub async fn send_smtp(
    server: &str,
    port: u16,
    from: &str,
    to: &[String],
    raw_message: &str,
) -> Result<(), anyhow::Error> {
    let addr = format!("{}:{}", server, port);
    let stream = TcpStream::connect(&addr).await?;
    let (reader, mut writer) = tokio::io::split(stream);
    let mut reader = BufReader::new(reader);
    let mut buf = String::new();

    // Read greeting
    reader.read_line(&mut buf).await?;
    tracing::debug!("SMTP: {}", buf.trim());

    // EHLO
    writer.write_all(b"EHLO ichin-mail\r\n").await?;
    buf.clear();
    reader.read_line(&mut buf).await?;

    // MAIL FROM
    writer.write_all(format!("MAIL FROM:<{}>\r\n", from).as_bytes()).await?;
    buf.clear();
    reader.read_line(&mut buf).await?;

    // RCPT TO
    for addr in to {
        writer.write_all(format!("RCPT TO:<{}>\r\n", addr).as_bytes()).await?;
        buf.clear();
        reader.read_line(&mut buf).await?;
    }

    // DATA
    writer.write_all(b"DATA\r\n").await?;
    buf.clear();
    reader.read_line(&mut buf).await?;

    writer.write_all(raw_message.as_bytes()).await?;
    writer.write_all(b"\r\n.\r\n").await?;
    buf.clear();
    reader.read_line(&mut buf).await?;

    // QUIT
    writer.write_all(b"QUIT\r\n").await?;
    Ok(())
}
