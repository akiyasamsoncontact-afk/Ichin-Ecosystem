use crate::protocol::envelope::Envelope;

pub fn validate_envelope(envelope: &Envelope) -> Result<(), String> {
    if envelope.from.is_empty() {
        return Err("'from' address is required".to_string());
    }
    if envelope.to.is_empty() {
        return Err("'to' list is required".to_string());
    }
    if envelope.subject.is_empty() {
        return Err("'subject' is required".to_string());
    }
    if envelope.body.is_empty() {
        return Err("'body' is required".to_string());
    }
    if !envelope.from.contains('@') {
        return Err(format!("Invalid 'from' address: {}", envelope.from));
    }
    for addr in &envelope.to {
        if !addr.contains('@') {
            return Err(format!("Invalid recipient address: {}", addr));
        }
    }
    if envelope.attachments.len() > 50 {
        return Err("Too many attachments (max 50)".to_string());
    }
    for att in &envelope.attachments {
        if att.size_bytes > 100 * 1024 * 1024 {
            return Err(format!(
                "Attachment too large: {} (max 100MB)",
                att.filename
            ));
        }
    }
    Ok(())
}

pub fn validate_recipient(recipient: &str) -> Result<String, String> {
    let trimmed = recipient.trim();
    if !trimmed.contains('@') {
        return Err(format!("Invalid email address: {}", trimmed));
    }
    let parts: Vec<&str> = trimmed.split('@').collect();
    if parts.len() != 2 || parts[0].is_empty() || parts[1].is_empty() {
        return Err(format!("Invalid email address: {}", trimmed));
    }
    Ok(trimmed.to_string())
}
