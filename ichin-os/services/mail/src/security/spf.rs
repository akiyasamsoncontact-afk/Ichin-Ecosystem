use std::net::IpAddr;

use hickory_resolver::config::ResolverConfig;
use hickory_resolver::name_server::TokioConnectionProvider;
use hickory_resolver::TokioResolver;

#[derive(Debug, PartialEq)]
pub enum SpfResult {
    Pass,
    Fail,
    SoftFail,
    Neutral,
    None,
    TempError,
    PermError,
}

pub struct SpfVerifier {
    resolver: TokioResolver,
}

impl SpfVerifier {
    pub fn new() -> Self {
        Self {
            resolver: TokioResolver::builder_with_config(
                ResolverConfig::default(),
                TokioConnectionProvider::default(),
            )
            .build(),
        }
    }

    pub async fn verify(&self, domain: &str, sender_ip: &str) -> Result<SpfResult, anyhow::Error> {
        let ip: IpAddr = sender_ip.parse().map_err(|_| anyhow::anyhow!("Invalid IP: {}", sender_ip))?;

        let txt_records = self.resolver.txt_lookup(domain).await.map_err(|e| {
            anyhow::anyhow!("DNS lookup failed for {}: {}", domain, e)
        })?;

        for record in txt_records.iter() {
            let txt = record.to_string();
            if txt.starts_with("v=spf1") {
                return Box::pin(self.evaluate_spf(&txt, domain, &ip)).await;
            }
        }

        tracing::warn!("No SPF record found for {}", domain);
        Ok(SpfResult::None)
    }

    async fn evaluate_spf<'a>(&'a self, spf_record: &'a str, check_domain: &'a str, ip: &'a IpAddr) -> Result<SpfResult, anyhow::Error> {
        let parts: Vec<&str> = spf_record.split_whitespace().collect();
        if parts.is_empty() {
            return Ok(SpfResult::Neutral);
        }

        for part in &parts[1..] {
            if part.is_empty() {
                continue;
            }

            let (qualifier, mechanism) = parse_mechanism(part);
            let result = self.check_mechanism(ip, check_domain, mechanism).await?;

            match result {
                Some(true) => return Ok(qualifier_to_result(qualifier)),
                Some(false) => continue,
                None => return Ok(SpfResult::TempError),
            }
        }

        Ok(SpfResult::Neutral)
    }

    async fn check_mechanism(&self, ip: &IpAddr, check_domain: &str, mechanism: &str) -> Result<Option<bool>, anyhow::Error> {
        if mechanism == "all" {
            return Ok(Some(true));
        }

        if let Some(cidr) = mechanism.strip_prefix("ip4:") {
            return Ok(Some(match_cidr(ip, cidr, 32)));
        }

        if let Some(cidr) = mechanism.strip_prefix("ip6:") {
            return Ok(Some(match_cidr(ip, cidr, 128)));
        }

        if let Some(include_domain) = mechanism.strip_prefix("include:") {
            let inner = Box::pin(self.verify(include_domain, &ip.to_string())).await;
            return match inner {
                Ok(SpfResult::Pass) => Ok(Some(true)),
                Ok(SpfResult::Fail) | Ok(SpfResult::SoftFail) => Ok(Some(false)),
                Ok(SpfResult::TempError) => Ok(None),
                _ => Ok(Some(false)),
            };
        }

        if mechanism.starts_with("a") {
            return self.check_a_mechanism(ip, check_domain, mechanism).await;
        }

        if mechanism.starts_with("mx") {
            return self.check_mx_mechanism(ip, check_domain, mechanism).await;
        }

        if let Some(exists_domain) = mechanism.strip_prefix("exists:") {
            return Box::pin(self.check_exists(exists_domain)).await;
        }

        Ok(Some(false))
    }

    async fn check_a_mechanism(&self, ip: &IpAddr, check_domain: &str, mechanism: &str) -> Result<Option<bool>, anyhow::Error> {
        let (lookup_domain, prefix) = if mechanism == "a" {
            (check_domain.to_string(), 32u8)
        } else if let Some(d) = mechanism.strip_prefix("a:") {
            let parts: Vec<&str> = d.split('/').collect();
            let p = parts.get(1).and_then(|s| s.parse().ok()).unwrap_or(32u8);
            (parts[0].to_string(), p)
        } else {
            return Ok(Some(false));
        };

        if let Ok(response) = self.resolver.ipv4_lookup(&lookup_domain).await {
            for record in response.iter() {
                if match_cidr(ip, &format!("{}/{}", record.0, prefix), 32) {
                    return Ok(Some(true));
                }
            }
        }
        if let Ok(response) = self.resolver.ipv6_lookup(&lookup_domain).await {
            for record in response.iter() {
                if match_cidr(ip, &format!("{}/{}", record.0, prefix), 128) {
                    return Ok(Some(true));
                }
            }
        }

        Ok(Some(false))
    }

    async fn check_mx_mechanism(&self, ip: &IpAddr, check_domain: &str, mechanism: &str) -> Result<Option<bool>, anyhow::Error> {
        let (lookup_domain, prefix) = if mechanism == "mx" {
            (check_domain.to_string(), 32u8)
        } else if let Some(d) = mechanism.strip_prefix("mx:") {
            let parts: Vec<&str> = d.split('/').collect();
            let p = parts.get(1).and_then(|s| s.parse().ok()).unwrap_or(32u8);
            (parts[0].to_string(), p)
        } else {
            return Ok(Some(false));
        };

        if let Ok(response) = self.resolver.mx_lookup(&lookup_domain).await {
            for mx in response.iter() {
                let exchange = mx.exchange().to_string().trim_end_matches('.').to_string();
                if let Ok(addrs) = self.resolver.ipv4_lookup(&exchange).await {
                    for record in addrs.iter() {
                        if match_cidr(ip, &format!("{}/{}", record.0, prefix), 32) {
                            return Ok(Some(true));
                        }
                    }
                }
                if let Ok(addrs) = self.resolver.ipv6_lookup(&exchange).await {
                    for record in addrs.iter() {
                        if match_cidr(ip, &format!("{}/{}", record.0, prefix), 128) {
                            return Ok(Some(true));
                        }
                    }
                }
            }
        }

        Ok(Some(false))
    }

    async fn check_exists(&self, exists_domain: &str) -> Result<Option<bool>, anyhow::Error> {
        if self.resolver.ipv4_lookup(exists_domain).await.is_ok() {
            return Ok(Some(true));
        }
        if self.resolver.ipv6_lookup(exists_domain).await.is_ok() {
            return Ok(Some(true));
        }
        Ok(Some(false))
    }
}

fn parse_mechanism(part: &str) -> (char, &str) {
    let qualifier = part.chars().next().unwrap_or('+');
    match qualifier {
        '+' | '-' | '~' | '?' => (qualifier, &part[1..]),
        _ => ('+', part),
    }
}

fn qualifier_to_result(qualifier: char) -> SpfResult {
    match qualifier {
        '-' => SpfResult::Fail,
        '~' => SpfResult::SoftFail,
        '?' => SpfResult::Neutral,
        _ => SpfResult::Pass,
    }
}

fn match_cidr(ip: &IpAddr, cidr_str: &str, default_prefix: u8) -> bool {
    let parts: Vec<&str> = cidr_str.split('/').collect();
    let ip_part = parts[0];
    let prefix_len = parts.get(1).and_then(|s| s.parse().ok()).unwrap_or(default_prefix);

    let target_ip: IpAddr = match ip_part.parse() {
        Ok(ip) => ip,
        Err(_) => return false,
    };

    if ip.is_ipv4() != target_ip.is_ipv4() {
        return false;
    }

    let ip_bits = match ip {
        IpAddr::V4(v4) => u128::from(u32::from_be_bytes(v4.octets())),
        IpAddr::V6(v6) => u128::from_be_bytes(v6.octets()),
    };
    let target_bits = match target_ip {
        IpAddr::V4(v4) => u128::from(u32::from_be_bytes(v4.octets())),
        IpAddr::V6(v6) => u128::from_be_bytes(v6.octets()),
    };
    let mask = if prefix_len == 0 {
        0
    } else {
        !0u128 << (128 - prefix_len)
    };

    (ip_bits & mask) == (target_bits & mask)
}

impl Default for SpfVerifier {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cidr_v4_match() {
        let ip: IpAddr = "192.168.1.5".parse().unwrap();
        assert!(match_cidr(&ip, "192.168.1.0/24", 32));
        assert!(match_cidr(&ip, "192.168.1.5", 32));
        assert!(!match_cidr(&ip, "10.0.0.0/8", 32));
    }

    #[test]
    fn test_cidr_v6_match() {
        let ip: IpAddr = "2001:db8::1".parse().unwrap();
        assert!(match_cidr(&ip, "2001:db8::/32", 128));
        assert!(!match_cidr(&ip, "2001:db9::/32", 128));
    }

    #[test]
    fn test_parse_qualifier() {
        assert_eq!(parse_mechanism("+all"), ('+', "all"));
        assert_eq!(parse_mechanism("-all"), ('-', "all"));
        assert_eq!(parse_mechanism("~all"), ('~', "all"));
        assert_eq!(parse_mechanism("?all"), ('?', "all"));
    }

    #[test]
    fn test_qualifier_mapping() {
        assert_eq!(qualifier_to_result('+'), SpfResult::Pass);
        assert_eq!(qualifier_to_result('-'), SpfResult::Fail);
        assert_eq!(qualifier_to_result('~'), SpfResult::SoftFail);
        assert_eq!(qualifier_to_result('?'), SpfResult::Neutral);
    }
}
