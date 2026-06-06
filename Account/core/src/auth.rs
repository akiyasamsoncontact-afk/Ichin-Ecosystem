use anyhow::{anyhow, Result};
use chrono::{Duration, Utc};
use ed25519_dalek::SigningKey;
use rand::RngCore;
use rand::rngs::OsRng;
use sha2::{Digest, Sha256};
use totp_rs::{Algorithm, Secret, TOTP};
use uuid::Uuid;

use crate::models::*;
use crate::storage::AccountStore;

pub struct AuthManager {
    signing_key: SigningKey,
    store: AccountStore,
}

impl AuthManager {
    pub fn new(store: AccountStore) -> Self {
        let mut seed = [0u8; 32];
        OsRng.fill_bytes(&mut seed);
        let signing_key = SigningKey::from_bytes(&seed);
        Self { signing_key, store }
    }

    pub fn signing_key_bytes(&self) -> Vec<u8> {
        self.signing_key.to_bytes().to_vec()
    }

    // --- Registration ---

    pub fn register_user(
        &self,
        username: &str,
        display_name: &str,
        email: &str,
    ) -> Result<User> {
        if !self.store.is_username_available(username)? {
            return Err(anyhow!("Username already taken"));
        }
        if !self.store.is_email_available(email)? {
            return Err(anyhow!("Email already registered"));
        }

        let user = User {
            id: Uuid::new_v4(),
            username: username.to_string(),
            display_name: display_name.to_string(),
            email: email.to_string(),
            profile_picture: None,
            passkey_credentials: Vec::new(),
            totp_secret: None,
            recovery_codes: Vec::new(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };
        self.store.create_user(&user)?;
        Ok(user)
    }

    // --- Session management ---

    pub fn create_session(
        &self,
        user_id: UserId,
        device_id: Option<DeviceId>,
        ip_address: &str,
        user_agent: &str,
    ) -> Result<Session> {
        let token = self.generate_session_token();
        let session = Session {
            id: Uuid::new_v4(),
            user_id,
            device_id,
            token,
            ip_address: ip_address.to_string(),
            user_agent: user_agent.to_string(),
            is_active: true,
            created_at: Utc::now(),
            expires_at: Utc::now() + Duration::days(30),
            last_accessed_at: Utc::now(),
        };
        self.store.create_session(&session)?;
        Ok(session)
    }

    pub fn validate_session(&self, token: &str) -> Result<Option<Session>> {
        let session = self.store.get_session_by_token(token)?;
        match session {
            Some(s) if s.is_active && s.expires_at > Utc::now() => Ok(Some(s)),
            _ => Ok(None),
        }
    }

    pub fn touch_session(&self, session: &Session) -> Result<()> {
        let mut updated = session.clone();
        updated.last_accessed_at = Utc::now();
        self.store.update_session(&updated)?;
        Ok(())
    }

    pub fn invalidate_session(&self, session_id: SessionId) -> Result<()> {
        if let Some(mut session) = self.store.get_session(session_id)? {
            session.is_active = false;
            self.store.update_session(&session)?;
        }
        Ok(())
    }

    pub fn invalidate_user_sessions(&self, user_id: UserId) -> Result<()> {
        let sessions = self.store.get_user_sessions(user_id)?;
        for session in sessions {
            self.invalidate_session(session.id)?;
        }
        Ok(())
    }

    // --- Recovery codes ---

    pub fn generate_recovery_codes(&self) -> Vec<String> {
        let mut codes = Vec::new();
        for _ in 0..8 {
            let code: String = (0..12)
                .map(|_| {
                    let idx = rand::random::<usize>() % 36;
                    std::char::from_digit(idx as u32, 36).unwrap()
                })
                .collect();
            codes.push(format!("{}-{}", &code[..6], &code[6..]));
        }
        codes
    }

    pub fn verify_recovery_code(user: &mut User, code: &str) -> bool {
        if let Some(pos) = user.recovery_codes.iter().position(|c| c == code) {
            user.recovery_codes.remove(pos);
            true
        } else {
            false
        }
    }

    // --- TOTP (2FA) ---

    pub fn setup_totp(&self, user: &mut User) -> Result<String> {
        let secret = Secret::generate_secret();
        let secret_str = secret.to_string();
        let totp = TOTP::new(
            Algorithm::SHA1,
            6,
            1,
            30,
            secret.to_bytes()?,
            Some("Ichin".to_string()),
            user.email.clone(),
        )?;
        let otpauth = totp.get_url();
        user.totp_secret = Some(secret_str);
        self.store.update_user(user)?;
        Ok(otpauth)
    }

    pub fn verify_totp(user: &User, code: &str) -> Result<bool> {
        let secret_str = user.totp_secret.as_ref().ok_or_else(|| anyhow!("TOTP not set up"))?;
        let secret = Secret::Encoded(secret_str.clone());
        let totp = TOTP::new(
            Algorithm::SHA1,
            6,
            1,
            30,
            secret.to_bytes()?,
            Some("Ichin".to_string()),
            user.email.clone(),
        )?;
        Ok(totp.check_current(code)?)
    }

    // --- Login history ---

    pub fn record_login(
        &self,
        user_id: UserId,
        ip_address: &str,
        user_agent: &str,
        success: bool,
        method: AuthMethod,
    ) -> Result<()> {
        let entry = LoginHistoryEntry {
            id: Uuid::new_v4(),
            user_id,
            timestamp: Utc::now(),
            ip_address: ip_address.to_string(),
            user_agent: user_agent.to_string(),
            success,
            method,
        };
        self.store.add_login_history(&entry)?;
        Ok(())
    }

    // --- Passkey (WebAuthn) ---

    pub fn register_passkey(
        &self,
        user: &mut User,
        credential_id: String,
        public_key: Vec<u8>,
        transports: Vec<String>,
        name: String,
    ) -> Result<()> {
        let passkey = PasskeyCredential {
            id: credential_id,
            public_key,
            counter: 0,
            transports,
            name,
            created_at: Utc::now(),
        };
        user.passkey_credentials.push(passkey);
        user.updated_at = Utc::now();
        self.store.update_user(user)?;
        Ok(())
    }

    // --- Session token generation ---

    fn generate_session_token(&self) -> String {
        let random_bytes: [u8; 32] = rand::random();
        let mut hasher = Sha256::new();
        hasher.update(&random_bytes);
        hasher.update(self.signing_key.to_bytes());
        hex::encode(hasher.finalize())
    }

    // --- Device management ---

    pub fn register_device(
        &self,
        user_id: UserId,
        name: String,
        device_type: DeviceType,
    ) -> Result<Device> {
        let device = Device {
            id: Uuid::new_v4(),
            user_id,
            name,
            device_type,
            last_synced_at: None,
            created_at: Utc::now(),
        };
        self.store.create_device(&device)?;
        Ok(device)
    }
}
