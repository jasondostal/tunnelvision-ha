# Changelog

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
