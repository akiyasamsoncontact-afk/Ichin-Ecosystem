use crate::protocol::envelope::Envelope;

pub fn request_receipt(envelope: &mut Envelope) {
    envelope.metadata.read_receipt = Some(true);
}

pub fn has_read_receipt(envelope: &Envelope) -> bool {
    envelope.metadata.read_receipt.unwrap_or(false)
}
