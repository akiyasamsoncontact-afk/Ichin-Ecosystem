use chrono::Utc;

use crate::protocol::envelope::Envelope;

pub fn schedule_delivery(envelope: &mut Envelope, timestamp: i64) {
    envelope.metadata.scheduled_delivery = Some(timestamp);
}

pub fn is_ready_for_delivery(envelope: &Envelope) -> bool {
    match envelope.metadata.scheduled_delivery {
        Some(scheduled_at) => Utc::now().timestamp() >= scheduled_at,
        None => true,
    }
}
