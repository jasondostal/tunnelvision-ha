# Roadmap

## Done

### v0.1.0 — Initial Release
- [x] Config flow with connection validation and API key support
- [x] DataUpdateCoordinator polling every 15 seconds
- [x] 12 sensors, 4 binary sensors, 9 buttons
- [x] 3 services for automations
- [x] Device grouping under single TunnelVision device

### v0.2.0 — Switches + Real-Time Updates
- [x] Switch entity for VPN (connect/disconnect toggle)
- [x] Switch entity for killswitch (on/off toggle)
- [x] Removed redundant buttons (disconnect, reconnect, killswitch enable/disable)
- [x] SSE (Server-Sent Events) for instant entity refresh
- [x] IoT class upgraded from `local_polling` to `local_push`

### v0.3.0 — v2.5.0 Service Support
- [x] DNS state sensor + binary sensor
- [x] HTTP proxy state sensor + binary sensor
- [x] SOCKS proxy state sensor + binary sensor
- [x] Forwarded port sensor (PIA/ProtonVPN NAT-PMP)
- [x] Entity count: 30 (16 sensors, 7 binary sensors, 5 buttons, 2 switches)

## Future

- [ ] HACS default repository listing
- [ ] Diagnostics download (config, entity states, coordinator data)
- [ ] Configurable polling interval in integration options
- [ ] Options flow for reconfiguration without removal
- [ ] Event entities for VPN state changes (connect, disconnect, rotate)
- [ ] Connection history as HA statistics
- [ ] Translations (community-contributed)
- [ ] Energy dashboard integration (bytes transferred as "energy" equivalent)
