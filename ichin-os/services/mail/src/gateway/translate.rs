use uuid::Uuid;

use crate::delivery::validate::validate_recipient;
use crate::protocol::envelope::Envelope;

pub fn smtp_to_ichin(
    raw_smtp: &str,
    from: &str,
    to: &[String],
) -> Result<Envelope, String> {
    let mut subject = String::new();
    let mut body = String::new();
    let mut in_body = false;

    for line in raw_smtp.lines() {
        if !in_body {
            if let Some(subj) = line.strip_prefix("Subject: ") {
                subject = subj.to_string();
            } else if let Some(_) = line.strip_prefix("From: ") {
                // Already have from_addr
            } else if let Some(_) = line.strip_prefix("To: ") {
                // Already have to_addrs
            } else if line.is_empty() {
                in_body = true;
            }
        } else {
            if !body.is_empty() {
                body.push('\n');
            }
            body.push_str(line);
        }
    }

    let validated_to: Result<Vec<String>, String> = to
        .iter()
        .map(|a| validate_recipient(a))
        .collect();
    let to_addrs = validated_to?;

    let mut envelope = Envelope::new(
        from.to_string(),
        to_addrs,
        subject,
        body,
    );

    // Ensure we have a message_id
    envelope.message_id = Uuid::new_v4();

    Ok(envelope)
}

pub fn ichin_to_smtp(envelope: &Envelope) -> String {
    let mut msg = format!(
        "From: {}\r\nTo: {}\r\nSubject: {}\r\nMessage-ID: <{}@ichin>\r\nDate: {}\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n{}",
        envelope.from,
        envelope.to.join(", "),
        envelope.subject,
        envelope.message_id,
        chrono::DateTime::from_timestamp(envelope.timestamp, 0)
            .map(|dt| dt.to_rfc2822())
            .unwrap_or_default(),
        envelope.body,
    );

    if let Some(ref html) = envelope.body_html {
        msg.push_str(&format!(
            "\r\n--boundary\r\nContent-Type: text/html\r\n\r\n{}",
            html
        ));
    }

    msg
}
