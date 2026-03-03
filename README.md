<p align="center">
  <img src="https://raw.githubusercontent.com/jasondostal/tunnelvision/main/images/tunnelvision-logo.svg" alt="TunnelVision" width="128">
</p>

<p align="center">
  <strong>TunnelVision for Home Assistant</strong>
</p>

<p align="center">
  <a href="https://github.com/jasondostal/tunnelvision-ha/releases"><img src="https://img.shields.io/github/v/release/jasondostal/tunnelvision-ha?style=flat-square" alt="Release"></a>
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square" alt="HACS"></a>
  <img src="https://img.shields.io/badge/HA-2024.1+-blue?style=flat-square" alt="HA">
</p>

---

Home Assistant integration for [TunnelVision](https://github.com/jasondostal/tunnelvision) — the all-in-one qBittorrent + WireGuard VPN + API container.

Monitor your VPN status, control your connection, and automate responses — all from within Home Assistant.

## Installation

### HACS (Recommended)

1. Open HACS → Integrations → Three dots → Custom Repositories
2. Add `https://github.com/jasondostal/tunnelvision-ha` as type "Integration"
3. Search for "TunnelVision" and click Install
4. Restart Home Assistant

### Manual

Copy `custom_components/tunnelvision/` to your HA `config/custom_components/` directory. Restart HA.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **TunnelVision**
3. Enter your TunnelVision container's host and port (default: 8081)
4. Enter your API key (leave blank if `API_KEY` is not set)
5. Done — entities appear automatically

## Entities

### Sensors

| Entity | Description |
|--------|-------------|
| VPN State | `up`, `down`, `disabled` |
| Public IP | VPN exit IP address |
| Country | Exit country |
| City | Exit city |
| Location | "City, Country" |
| Download Speed | Current download rate |
| Upload Speed | Current upload rate |
| Active Torrents | Number of active torrents |
| Total Torrents | Total torrent count |
| Total Downloaded | Cumulative bytes downloaded |
| Total Uploaded | Cumulative bytes uploaded |
| VPN Provider | `mullvad`, `custom`, etc. |

### Binary Sensors

| Entity | Description |
|--------|-------------|
| VPN Connected | On when VPN is up |
| Killswitch | On when killswitch is active |
| Healthy | On when container is healthy |
| qBittorrent | On when qBit is running |

### Buttons

| Entity | Description |
|--------|-------------|
| Restart VPN | Restart the VPN tunnel |
| Rotate Server | Connect to a random new server |
| Disconnect VPN | Tear down the tunnel |
| Reconnect VPN | Bring the tunnel back up |
| Restart qBittorrent | Restart the torrent client |
| Pause All Torrents | Pause all active torrents |
| Resume All Torrents | Resume paused torrents |
| Enable Killswitch | Apply firewall rules |
| Disable Killswitch | Remove firewall rules |

## Services

```yaml
# Restart VPN
service: tunnelvision.vpn
data:
  action: restart  # or: disconnect, reconnect, rotate

# Control qBittorrent
service: tunnelvision.qbittorrent
data:
  action: restart  # or: pause, resume

# Toggle killswitch
service: tunnelvision.killswitch
data:
  action: enable  # or: disable
```

## Automation Examples

### Notify when VPN drops

```yaml
automation:
  - alias: "TunnelVision VPN Down Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.tunnelvision_vpn_connected
        to: "off"
    action:
      - service: notify.mobile_app
        data:
          title: "VPN Down"
          message: "TunnelVision VPN disconnected"
```

### Auto-reconnect on VPN drop

```yaml
automation:
  - alias: "TunnelVision Auto-Reconnect"
    trigger:
      - platform: state
        entity_id: binary_sensor.tunnelvision_vpn_connected
        to: "off"
        for: "00:01:00"
    action:
      - service: tunnelvision.vpn
        data:
          action: reconnect
```

### Rotate server daily

```yaml
automation:
  - alias: "TunnelVision Daily Rotation"
    trigger:
      - platform: time
        at: "04:00:00"
    action:
      - service: tunnelvision.vpn
        data:
          action: rotate
```

## Also Available

TunnelVision also supports **MQTT with auto-discovery** — if you have an MQTT broker, set `MQTT_ENABLED=true` in your TunnelVision container and entities appear in HA automatically without this integration. Use whichever method suits your setup.

## License

[MIT](LICENSE)
