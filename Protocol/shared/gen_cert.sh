#!/usr/bin/env bash
# Generate self-signed TLS 1.3 cert for ICHINP testing
set -euo pipefail

openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 3650 -nodes \
  -subj "/CN=ICHINP Experimental" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

chmod 600 key.pem
echo "Generated cert.pem and key.pem"
