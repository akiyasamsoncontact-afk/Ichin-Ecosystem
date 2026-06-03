use uuid::Uuid;

use crate::protocol::envelope::Envelope;

pub fn is_reply(envelope: &Envelope) -> bool {
    envelope.reply_to_id.is_some()
}

pub fn get_thread_id(envelope: &Envelope) -> Option<Uuid> {
    envelope.reply_to_id
}

pub fn build_thread(messages: &[Envelope]) -> Vec<Vec<&Envelope>> {
    let mut threads: Vec<Vec<&Envelope>> = Vec::new();
    let mut used = vec![false; messages.len()];

    for i in 0..messages.len() {
        if used[i] {
            continue;
        }

        let mut thread = vec![&messages[i]];
        used[i] = true;

        if let Some(reply_to) = messages[i].reply_to_id {
            for j in 0..messages.len() {
                if !used[j] && messages[j].message_id == reply_to {
                    thread.insert(0, &messages[j]);
                    used[j] = true;
                    break;
                }
            }
        }

        for j in 0..messages.len() {
            if !used[j] {
                if let Some(reply_to) = messages[j].reply_to_id {
                    if reply_to == messages[i].message_id {
                        thread.push(&messages[j]);
                        used[j] = true;
                    }
                }
            }
        }

        threads.push(thread);
    }

    threads
}
