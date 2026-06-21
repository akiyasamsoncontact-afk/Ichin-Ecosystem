use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};

use tokio::sync::Mutex;

pub struct RateLimiter {
    buckets: Arc<Mutex<HashMap<String, RateBucket>>>,
    max_requests: u32,
    window_duration: Duration,
}

struct RateBucket {
    count: u32,
    window_start: Instant,
}

impl RateLimiter {
    pub fn new(max_requests: u32, window_secs: u64) -> Self {
        Self {
            buckets: Arc::new(Mutex::new(HashMap::new())),
            max_requests,
            window_duration: Duration::from_secs(window_secs),
        }
    }

    pub async fn check(&self, key: &str) -> Result<(), RateLimitError> {
        let mut buckets = self.buckets.lock().await;
        let now = Instant::now();

        let bucket = buckets.entry(key.to_string()).or_insert(RateBucket {
            count: 0,
            window_start: now,
        });

        if now.duration_since(bucket.window_start) > self.window_duration {
            bucket.count = 0;
            bucket.window_start = now;
        }

        if bucket.count >= self.max_requests {
            return Err(RateLimitError::Exceeded);
        }

        bucket.count += 1;
        Ok(())
    }
}

#[derive(Debug, thiserror::Error)]
pub enum RateLimitError {
    #[error("Rate limit exceeded")]
    Exceeded,
}

pub struct ReputationScorer {
    scores: Arc<Mutex<HashMap<String, Reputation>>>,
}

#[derive(Debug, Clone)]
pub struct Reputation {
    pub domain: String,
    pub score: f64,
    pub messages_sent: u64,
    pub complaints: u64,
    pub last_seen: i64,
}

impl ReputationScorer {
    pub fn new() -> Self {
        Self {
            scores: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub async fn record_message(&self, domain: &str, is_spam: bool) {
        let mut scores = self.scores.lock().await;
        let entry = scores.entry(domain.to_string()).or_insert(Reputation {
            domain: domain.to_string(),
            score: 50.0,
            messages_sent: 0,
            complaints: 0,
            last_seen: chrono::Utc::now().timestamp(),
        });

        entry.messages_sent += 1;
        entry.last_seen = chrono::Utc::now().timestamp();

        if is_spam {
            entry.complaints += 1;
            entry.score = (entry.score - 5.0).max(0.0);
        } else {
            entry.score = (entry.score + 0.5).min(100.0);
        }
    }

    pub async fn get_score(&self, domain: &str) -> f64 {
        let scores = self.scores.lock().await;
        scores.get(domain).map_or(50.0, |r| r.score)
    }

    pub async fn is_trusted(&self, domain: &str) -> bool {
        self.get_score(domain).await > 60.0
    }
}
