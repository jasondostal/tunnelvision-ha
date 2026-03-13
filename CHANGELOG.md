# Changelog

## v0.5.0 — HTTPS Support + Security Hardening (2026-03-12)

### Security
- **HTTPS support** — config flow now offers "Use HTTPS" and "Verify SSL certificate"
  options. All API requests (fetch, POST, and SSE) pass the SSL context. Self-signed
  certs supported by unchecking verify.
- **Port validation** — config flow enforces 1–65535 range via `vol.Range`.
- **Input sanitization** — host and API key inputs are stripped of whitespace.

### Migration
- Config entry version bumped to 2. Existing v1 entries are automatically migrated
  with `use_ssl=false` and `verify_ssl=true` (no action required).

### Entity Count: 33
- 16 sensors, 7 binary sensors, 7 buttons, 2 switches, 1 number (unchanged)

---

## v0.4.0 — HA Best Practices + Release Pipeline (2026-03-07)

### Breaking Changes
- Entity names no longer include "TunnelVision " prefix — HA's `has_entity_name` handles
  device-scoped naming automatically. Entity IDs are unchanged.

### Improvements
- **Base entity class** — shared `device_info` and `has_entity_name` across all entity types.
  Eliminates duplicated device registration code.
- **Shared HTTP session** — replaced per-call `aiohttp.ClientSession()` with HA's
  `async_get_clientsession()`. Reuses HA's connection pool, respects HA's SSL config.
- **EntityCategory.DIAGNOSTIC** — forwarded_port, dns_state, http_proxy_state,
  socks_proxy_state marked as diagnostic entities (hidden from default dashboards).
- **services.yaml** — service schemas for `tunnelvision.vpn`, `tunnelvision.qbittorrent`,
  and `tunnelvision.killswitch`. Enables autocomplete and validation in HA service calls.
- **Killswitch action validation** — rejects invalid actions with a clear error instead of
  silently passing to the API.
- **Service cleanup** — services are unregistered when the last config entry is removed.
- **Error handling** — `api_post()` checks response status and logs errors.

### CI/CD
- **Release workflow** — tag `v*` → manifest version check → zip → GitHub Release with
  auto-generated notes. Manual installs can now download from Releases page.
- **Mypy type checking** — added to lint workflow.
- **hacs.json** — `render_readme: true` for HACS store display.

---

## v0.3.1 — CI & Lint (2026-03-05)

### CI Pipeline
- GitHub Actions lint workflow: ruff, bandit (high-severity), HACS validation
- Runs on push/PR to main

### Code Quality
- Added `pyproject.toml` with ruff + mypy config
- Fixed import sorting across all modules
- Fixed exception chaining (`raise ... from err`)
- Removed unused variable in config flow

---

## v0.3.0 — v2.5.0 Service Support (2026-03-04)

### New Sensors
- DNS State — shows DNS service status (running/disabled)
- HTTP Proxy State — shows HTTP CONNECT proxy status
- SOCKS Proxy State — shows SOCKS5/Shadowsocks proxy status
- Forwarded Port — shows active port forwarding (PIA/ProtonVPN NAT-PMP)

### New Binary Sensors
- DNS — connectivity sensor for built-in DNS service
- HTTP Proxy — connectivity sensor for HTTP CONNECT proxy
- SOCKS Proxy — connectivity sensor for SOCKS5 proxy

### Entity Count: 30
- 16 sensors, 7 binary sensors, 5 buttons, 2 switches

### Compatibility
- Requires TunnelVision v2.5.0+ (new health endpoint fields)
- Fully backwards-compatible with v2.4.0 (new entities show "disabled" gracefully)

---

## v0.2.0 — Switches + Real-Time Updates (2026-03-03)

### Switch Entities
- VPN switch — on/off toggles connect/disconnect, reflects actual VPN state
- Killswitch switch — on/off toggles enable/disable, reflects actual killswitch state
- Removed redundant buttons (disconnect, reconnect, killswitch enable/disable)

### SSE (Server-Sent Events)
- Subscribes to TunnelVision's `/api/v1/events` stream on setup
- VPN state changes trigger instant HA entity refresh (~1 second)
- Exponential backoff on connection failure, polling remains as fallback
- IoT class upgraded from `local_polling` to `local_push`

### Entity Count: 23
- 12 sensors, 4 binary sensors, 5 buttons, 2 switches

---

## v0.1.0 — Initial Release (2026-03-03)

First release. Native Home Assistant integration for TunnelVision.

### Entities (25 total)
- 12 sensors: VPN state, public IP, country, city, location, download/upload speed, active/total torrents, total downloaded/uploaded, provider
- 4 binary sensors: VPN connected, killswitch active, healthy, qBittorrent running
- 9 buttons: Restart VPN, rotate server, disconnect, reconnect, restart qBit, pause/resume torrents, enable/disable killswitch

### Features
- Config flow with connection validation and API key support
- DataUpdateCoordinator polling every 15 seconds
- 3 services for automations: `tunnelvision.vpn`, `tunnelvision.qbittorrent`, `tunnelvision.killswitch`
- Device grouping under single TunnelVision device
- Proper device classes, state classes, and icons
