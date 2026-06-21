use ichin_mail::protocol::envelope::Envelope;
use ichin_mail::protocol::handshake::{accept_handshake, create_handshake, Capability};
use ichin_mail::security::keys::KeyPair;
use ichin_mail::security::sign::sign_envelope;
use ichin_mail::security::verify::verify_envelope;
use ichin_mail::delivery::validate::validate_envelope;
use ichin_mail::delivery::thread::build_thread;
use ichin_mail::extensions::expiration::{is_expired, set_expiration};

#[test]
fn test_envelope_creation() {
    let env = Envelope::new(
        "alice@ichin.test".into(),
        vec!["bob@ichin.test".into()],
        "Hello".into(),
        "World".into(),
    );
    assert_eq!(env.from, "alice@ichin.test");
    assert_eq!(env.to, vec!["bob@ichin.test"]);
    assert_eq!(env.subject, "Hello");
    assert_eq!(env.body, "World");
    assert!(env.signature.is_none());
}

#[test]
fn test_envelope_serialization_roundtrip() {
    let env = Envelope::new(
        "alice@ichin.test".into(),
        vec!["bob@ichin.test".into()],
        "Test".into(),
        "Body".into(),
    );
    let json = env.serialize().unwrap();
    let deserialized = Envelope::deserialize(&json).unwrap();
    assert_eq!(env.message_id, deserialized.message_id);
    assert_eq!(env.from, deserialized.from);
    assert_eq!(env.subject, deserialized.subject);
    assert_eq!(env.body, deserialized.body);
}

#[test]
fn test_sign_and_verify() {
    let mut env = Envelope::new(
        "alice@ichin.test".into(),
        vec!["bob@ichin.test".into()],
        "Signed Message".into(),
        "This is signed.".into(),
    );
    let keypair = KeyPair::generate();
    sign_envelope(&mut env, &keypair).unwrap();

    assert!(env.signature.is_some());
    assert_eq!(env.signing_key_id, Some(keypair.key_id.clone()));

    let valid = verify_envelope(&env, &keypair.public_key).unwrap();
    assert!(valid);
}

#[test]
fn test_verify_tampered_message() {
    let mut env = Envelope::new(
        "alice@ichin.test".into(),
        vec!["bob@ichin.test".into()],
        "Secure".into(),
        "Body".into(),
    );
    let keypair = KeyPair::generate();
    sign_envelope(&mut env, &keypair).unwrap();

    env.body = "Tampered!".to_string();
    let valid = verify_envelope(&env, &keypair.public_key).unwrap();
    assert!(!valid);
}

#[test]
fn test_validate_envelope_valid() {
    let env = Envelope::new(
        "alice@test.com".into(),
        vec!["bob@test.com".into()],
        "Subject".into(),
        "Body".into(),
    );
    assert!(validate_envelope(&env).is_ok());
}

#[test]
fn test_validate_envelope_invalid_from() {
    let env = Envelope::new(
        "".into(),
        vec!["bob@test.com".into()],
        "Subject".into(),
        "Body".into(),
    );
    assert!(validate_envelope(&env).is_err());
}

#[test]
fn test_validate_envelope_invalid_recipient() {
    let env = Envelope::new(
        "alice@test.com".into(),
        vec!["not-an-email".into()],
        "Subject".into(),
        "Body".into(),
    );
    assert!(validate_envelope(&env).is_err());
}

#[test]
fn test_handshake_creation() {
    let hs = create_handshake("mail.ichin.test");
    assert_eq!(hs.protocol, "ichin-mail");
    assert_eq!(hs.version, "1.0.0");
    assert!(hs.capabilities.contains(&Capability::Tls13));
}

#[test]
fn test_handshake_accept() {
    let hs = create_handshake("mail.ichin.test");
    let response = accept_handshake(&hs, "server.ichin.test");
    assert!(response.accepted);
    assert!(response.error.is_none());
}

#[test]
fn test_handshake_reject() {
    let hs = create_handshake("mail.ichin.test");
    let mut bad_hs = hs.clone();
    bad_hs.protocol = "unknown-protocol".into();
    let response = accept_handshake(&bad_hs, "server.ichin.test");
    assert!(!response.accepted);
    assert!(response.error.is_some());
}

#[test]
fn test_keypair_generation() {
    let kp1 = KeyPair::generate();
    let kp2 = KeyPair::generate();
    // Keys should be unique
    assert_ne!(kp1.private_key, kp2.private_key);
    assert_ne!(kp1.public_key, kp2.public_key);
    assert_eq!(kp1.private_key.len(), 32);
    assert_eq!(kp1.public_key.len(), 32);
}

#[test]
fn test_threading() {
    let msg1 = Envelope::new(
        "alice@test.com".into(),
        vec!["bob@test.com".into()],
        "Original".into(),
        "First".into(),
    );
    let mut msg2 = Envelope::new(
        "bob@test.com".into(),
        vec!["alice@test.com".into()],
        "Re: Original".into(),
        "Reply".into(),
    );
    msg2.reply_to_id = Some(msg1.message_id);

    let msgs = [msg1, msg2];
    let threads = build_thread(&msgs);
    assert_eq!(threads.len(), 1);
    assert_eq!(threads[0].len(), 2);
}

#[test]
fn test_expiration() {
    let mut env = Envelope::new(
        "alice@test.com".into(),
        vec!["bob@test.com".into()],
        "Expires".into(),
        "Body".into(),
    );
    assert!(!is_expired(&env));
    set_expiration(&mut env, -1); // Expire in the past
    assert!(is_expired(&env));
}

#[test]
fn test_keypair_serialization() {
    let kp = KeyPair::generate();
    let json = serde_json::to_string(&kp).unwrap();
    let deserialized: KeyPair = serde_json::from_str(&json).unwrap();
    assert_eq!(kp.key_id, deserialized.key_id);
    assert_eq!(kp.public_key, deserialized.public_key);
    assert_eq!(kp.private_key, deserialized.private_key);
}

#[test]
fn test_canonical_bytes_stable() {
    let env = Envelope::new(
        "alice@test.com".into(),
        vec!["bob@test.com".into()],
        "Stable".into(),
        "Body".into(),
    );
    let bytes1 = env.canonical_bytes();
    let bytes2 = env.canonical_bytes();
    assert_eq!(bytes1, bytes2);
}

#[test]
fn test_canonical_bytes_without_signature() {
    let mut env = Envelope::new(
        "alice@test.com".into(),
        vec!["bob@test.com".into()],
        "Canonical".into(),
        "Body".into(),
    );
    let kp = KeyPair::generate();
    sign_envelope(&mut env, &kp).unwrap();
    let canonical = env.canonical_bytes();
    let canonical_json: serde_json::Value = serde_json::from_slice(&canonical).unwrap();
    assert!(canonical_json.get("signature").is_none());
    assert!(canonical_json.get("signing_key_id").is_none());
}
