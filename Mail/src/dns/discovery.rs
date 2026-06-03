use hickory_resolver::config::ResolverConfig;
use hickory_resolver::name_server::TokioConnectionProvider;
use hickory_resolver::TokioResolver;

pub struct ServerEndpoint {
    pub hostname: String,
    pub port: u16,
    pub priority: u16,
    pub weight: u16,
}

pub struct DnsDiscovery {
    resolver: TokioResolver,
}

impl DnsDiscovery {
    pub fn new() -> Self {
        Self {
            resolver: TokioResolver::builder_with_config(
                ResolverConfig::default(),
                TokioConnectionProvider::default(),
            ).build(),
        }
    }

    pub async fn discover_mx(&self, domain: &str) -> Result<Vec<ServerEndpoint>, anyhow::Error> {
        let mx_records = self.resolver.mx_lookup(domain).await?;
        let mut endpoints = Vec::new();

        for mx in mx_records.iter() {
            let exchange = mx.exchange().to_string();
            let exchange_trimmed = exchange.trim_end_matches('.');
            endpoints.push(ServerEndpoint {
                hostname: exchange_trimmed.to_string(),
                port: 443,
                priority: mx.preference(),
                weight: 0,
            });
        }

        endpoints.sort_by_key(|e| e.priority);
        Ok(endpoints)
    }

    pub async fn discover_ichin_srv(&self, domain: &str) -> Result<Vec<ServerEndpoint>, anyhow::Error> {
        let srv_name = format!("_ichin._tcp.{}", domain);
        let srv_records = self.resolver.srv_lookup(&srv_name).await;

        match srv_records {
            Ok(records) => {
                let mut endpoints = Vec::new();
                for srv in records.iter() {
                    let target = srv.target().to_string();
                    let target_trimmed = target.trim_end_matches('.');
                    endpoints.push(ServerEndpoint {
                        hostname: target_trimmed.to_string(),
                        port: srv.port(),
                        priority: srv.priority(),
                        weight: srv.weight(),
                    });
                }
                endpoints.sort_by_key(|e| e.priority);
                Ok(endpoints)
            }
            Err(_) => {
                tracing::info!("No Ichin SRV record found for {}, falling back to MX", domain);
                self.discover_mx(domain).await
            }
        }
    }

    pub async fn resolve(&self, hostname: &str) -> Result<Vec<std::net::IpAddr>, anyhow::Error> {
        let ips = self.resolver.lookup_ip(hostname).await?;
        Ok(ips.iter().collect())
    }
}
