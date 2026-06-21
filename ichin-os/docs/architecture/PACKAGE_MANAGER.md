# Ichin Package Manager & .ichinpkg Format

## Native Package Format: .ichinpkg

### Package Structure

```
package-v1.ichinpkg
├── manifest.json          # Package metadata and declarations
├── signature.sig          # Cryptographic signature (Ed25519)
├── certificate.pem        # Developer certificate
├── payload.tar.zst        # Compressed application files
│   ├── bin/
│   ├── lib/
│   ├── share/
│   └── data/
├── sandbox.json           # Sandbox permissions manifest
└── delta/                 # Delta update metadata (optional)
    ├── v1-to-v2.diff
    └── metadata.json
```

### Manifest Format (manifest.json)

```json
{
  "package": "com.ichin.app",
  "name": "Application Name",
  "version": "1.0.0",
  "architecture": "x86_64",
  "os": "ichin",
  "format_version": 1,
  "description": "Description of the application",
  "developer": {
    "name": "Developer Name",
    "id": "dev-id",
    "certificate_fingerprint": "sha256:..."
  },
  "dependencies": [
    {"package": "com.ichin.runtime", "version": ">=2.0"},
    {"package": "com.ichin.sdk", "version": ">=1.5"}
  ],
  "ai_capabilities": {
    "requires_ai": true,
    "required_capabilities": ["text-generation", "embeddings"],
    "minimum_model": "llama-3.2-3b",
    "local_only": false
  },
  "permissions": [
    "network",
    "filesystem.read",
    "notifications"
  ],
  "size": 25165824,
  "checksum": "sha256:...",
  "install_size": 52428800,
  "categories": ["productivity", "writing"],
  "themes": ["light", "dark"],
  "languages": ["en", "ja", "es"],
  "updates": {
    "channel": "stable",
    "auto_update": true,
    "delta_support": true
  }
}
```

### Sandbox Manifest (sandbox.json)

```json
{
  "version": 1,
  "sandbox": {
    "type": "user-namespace",
    "network": {
      "access": "filtered",
      "allowed_hosts": ["*.ichin.ai", "api.example.com"],
      "blocked_hosts": ["*.tracking.com"]
    },
    "filesystem": {
      "read": ["$HOME/Documents", "$HOME/Downloads"],
      "write": ["$HOME/Documents/app-name"],
      "blocked": ["$HOME/.ssh", "$HOME/.gnupg"]
    },
    "devices": {
      "microphone": false,
      "camera": false,
      "gpu": true
    },
    "ai": {
      "local_models": true,
      "cloud_models": false,
      "max_context": 4096
    },
    "resources": {
      "max_memory": "512MB",
      "max_cpu": 0.5,
      "max_disk": "100MB"
    }
  }
}
```

## Package Manager CLI

```bash
ichin pkg install ./app.ichinpkg     # Install local package
ichin pkg install com.ichin.app      # Install from repository
ichin pkg remove com.ichin.app       # Uninstall
ichin pkg update com.ichin.app       # Update specific package
ichin pkg update --all               # Update all packages
ichin pkg info com.ichin.app         # Show package info
ichin pkg list                       # List installed packages
ichin pkg search "note taking"       # Search packages
ichin pkg verify com.ichin.app       # Verify package integrity
ichin pkg rollback com.ichin.app     # Rollback to previous version
ichin pkg export com.ichin.app       # Export as .ichinpkg
ichin pkg repair                     # Repair broken installation
```

## Repository Management

```bash
ichin repo add stable https://repo.ichin.ai/stable
ichin repo remove stable
ichin repo list
ichin repo update
```

## Compatibility Subsystem

### Supported formats:
- **Native**: `.ichinpkg`
- **Linux**: Flatpak, AppImage, Snap (optional), deb, rpm, tar.gz
- **Windows**: exe, msi, bat (via Wine/Proton isolation layer)

### Compatibility layer design:
- Each foreign binary runs in a dedicated Wine prefix
- Filesystem mapped through FUSE bridge
- Registry emulated via SQLite
- DirectX translated to Vulkan via DXVK/VKD3D
- Windows APIs mapped to Linux equivalents via custom shim
- All foreign processes sandboxed with seccomp + AppArmor
