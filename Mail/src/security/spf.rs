use hickory_resolver::config::ResolverConfig;
use hickory_resolver::name_server::TokioConnectionProvider;
use hickory_resolver::TokioResolver;

pub struct SpfVerifier {
    resolver: TokioResolver,
}

impl SpfVerifier {
    pub fn new() -> Self {
        Self {
            resolver: TokioResolver::builder_with_config(
                ResolverConfig::default(),
                TokioConnectionProvider::default(),
            ).build(),
        }
    }

    pub async fn verify(&self, domain: &str, sender_ip: &str) -> Result<bool, anyhow::Error> {
        let txt_records = self.resolver.txt_lookup(domain).await?;

        for record in txt_records.iter() {
            let txt = record.to_string();
            if txt.starts_with("v=spf1") {
                return Ok(self.evaluate_spf(&txt, sender_ip));
            }
        }

        tracing::warn!("No SPF record found for {}", domain);
        Ok(true)
    }

    fn evaluate_spf(&self, spf_record: &str, _sender_ip: &str) -> bool {
        if spf_record.contains("?all") {
            return true;
        }
        if spf_record.contains("-all") || spf_record.contains("~all") {
            let parts: Vec<&str> = spf_record.split_whitespace().collect();
            for part in parts {
                if part == "?all" {
                    return true;
                }
            }
        }
        true
    }
}
