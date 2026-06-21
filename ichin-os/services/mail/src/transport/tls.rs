use std::sync::Arc;

use rustls::pki_types::{CertificateDer, PrivateKeyDer};
use rustls::ServerConfig;

pub fn load_certs(path: &str) -> Result<Vec<CertificateDer<'static>>, anyhow::Error> {
    let cert_file = std::fs::read(path)?;
    let certs = rustls_pemfile::certs(&mut cert_file.as_slice())
        .collect::<Result<Vec<_>, _>>()?;
    Ok(certs)
}

pub fn load_private_key(path: &str) -> Result<PrivateKeyDer<'static>, anyhow::Error> {
    let key_file = std::fs::read(path)?;
    let key = rustls_pemfile::private_key(&mut key_file.as_slice())?
        .ok_or_else(|| anyhow::anyhow!("No private key found in {}", path))?;
    Ok(key)
}

pub fn server_config(
    cert_path: &str,
    key_path: &str,
) -> Result<Arc<ServerConfig>, anyhow::Error> {
    let certs = load_certs(cert_path)?;
    let key = load_private_key(key_path)?;

    let config = ServerConfig::builder()
        .with_no_client_auth()
        .with_single_cert(certs, key)?;

    Ok(Arc::new(config))
}

pub fn client_config() -> Result<Arc<rustls::ClientConfig>, anyhow::Error> {
    let config = rustls::ClientConfig::builder()
        .with_root_certificates(root_certs())
        .with_no_client_auth();
    Ok(Arc::new(config))
}

fn root_certs() -> rustls::RootCertStore {
    let mut roots = rustls::RootCertStore::empty();
    if let Ok(cert_file) = std::fs::read("/etc/ssl/certs/ca-certificates.crt") {
        let certs: Vec<CertificateDer<'static>> =
            rustls_pemfile::certs(&mut cert_file.as_slice())
                .filter_map(|c| c.ok())
                .collect();
        for cert in certs {
            let _ = roots.add(cert);
        }
    }
    roots
}
