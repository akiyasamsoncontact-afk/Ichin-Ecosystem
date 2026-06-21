# ICHIN OS — Python Agent Template

A template for building Python AI agents that integrate into the ICHIN OS ecosystem.

## Structure

- `manifest.json` — App manifest declaring identity, permissions, and AI compatibility
- `agent.py` — Agent class template with ICHIN OS integration methods

## Usage

```bash
pip install ichin-sdk
python agent.py
```

## Customization

1. Edit `manifest.json` to set your app name, ID, and permissions
2. Extend `IchinAgent` in `agent.py` and implement `process_task()`
3. Use `query_ai()`, `read_memory()`, `write_memory()`, and `notify()` for ICHIN OS integration
