"""The TunnelVision integration."""

import asyncio
import json
import logging
import ssl
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_USE_SSL, CONF_VERIFY_SSL, DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "button", "switch"]


class TunnelVisionCoordinator(DataUpdateCoordinator):
    """Fetch data from TunnelVision API with SSE for instant updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        api_key: str,
        use_ssl: bool = False,
        verify_ssl: bool = True,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.host = host
        self.port = port
        self.api_key = api_key
        scheme = "https" if use_ssl else "http"
        self.base_url = f"{scheme}://{host}:{port}"
        self._ssl_context: ssl.SSLContext | bool | None = None
        if use_ssl and not verify_ssl:
            self._ssl_context = False
        self._sse_task: asyncio.Task | None = None
        self._session = async_get_clientsession(hass)

    @property
    def _headers(self) -> dict:
        h = {}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    async def _fetch(self, path: str) -> dict:
        """Fetch a single API endpoint."""
        async with self._session.get(
            f"{self.base_url}{path}",
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=10),
            ssl=self._ssl_context,
        ) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"API returned {resp.status} for {path}")
            return await resp.json()

    async def _async_update_data(self) -> dict:
        """Fetch all endpoints and merge into one dict."""
        try:
            health = await self._fetch("/api/v1/health")
            vpn = await self._fetch("/api/v1/vpn/status")
            qbt = await self._fetch("/api/v1/qbt/status")

            return {
                # Health
                "healthy": health.get("healthy", False),
                "setup_required": health.get("setup_required", False),
                "uptime_seconds": health.get("uptime_seconds", 0),
                "dns_state": health.get("dns", "disabled"),
                "http_proxy_state": health.get("http_proxy", "disabled"),
                "socks_proxy_state": health.get("socks_proxy", "disabled"),
                # VPN
                "vpn_state": vpn.get("state", "unknown"),
                "public_ip": vpn.get("public_ip", ""),
                "country": vpn.get("country", ""),
                "city": vpn.get("city", ""),
                "location": vpn.get("location", ""),
                "killswitch": vpn.get("killswitch", "disabled"),
                "transfer_rx": vpn.get("transfer_rx", 0),
                "transfer_tx": vpn.get("transfer_tx", 0),
                "provider": vpn.get("provider", "custom"),
                "forwarded_port": vpn.get("forwarded_port"),
                # qBittorrent
                "qbt_state": qbt.get("state", "unknown"),
                "download_speed": qbt.get("download_speed", 0),
                "upload_speed": qbt.get("upload_speed", 0),
                "active_torrents": qbt.get("active_torrents", 0),
                "total_torrents": qbt.get("total_torrents", 0),
                "qbt_version": qbt.get("version", ""),
            }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Cannot connect to TunnelVision: {err}") from err

    async def api_post(self, path: str) -> dict | None:
        """Send a POST command to the API."""
        async with self._session.post(
            f"{self.base_url}{path}",
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=30),
            ssl=self._ssl_context,
        ) as resp:
            if resp.status >= 400:
                _LOGGER.error("API call failed: %s %s", resp.status, await resp.text())
                return None
            return await resp.json()

    def start_sse(self):
        """Start listening to SSE stream for instant updates."""
        if self._sse_task is None or self._sse_task.done():
            self._sse_task = self.hass.async_create_task(self._sse_listener())

    def stop_sse(self):
        """Stop SSE listener."""
        if self._sse_task and not self._sse_task.done():
            self._sse_task.cancel()

    async def _sse_listener(self):
        """Subscribe to TunnelVision SSE stream, trigger refresh on events."""
        url = f"{self.base_url}/api/v1/events"
        retry_delay = 5

        while True:
            try:
                async with self._session.get(
                    url,
                    headers=self._headers,
                    timeout=aiohttp.ClientTimeout(total=0),  # No timeout for SSE
                    ssl=self._ssl_context,
                ) as resp:
                        if resp.status != 200:
                            _LOGGER.warning("SSE connection returned %s, falling back to polling", resp.status)
                            await asyncio.sleep(retry_delay)
                            continue

                        _LOGGER.info("SSE connected to %s", url)
                        retry_delay = 5  # Reset on successful connect

                        async for line in resp.content:
                            decoded = line.decode("utf-8", errors="replace").strip()
                            if decoded.startswith("data:"):
                                try:
                                    data = json.loads(decoded[5:].strip())
                                    _LOGGER.debug("SSE event received: %s", data.get("state", ""))
                                    await self.async_request_refresh()
                                except (json.JSONDecodeError, ValueError):
                                    pass

            except asyncio.CancelledError:
                _LOGGER.info("SSE listener stopped")
                return
            except Exception as err:
                _LOGGER.debug("SSE connection error: %s, retrying in %ss", err, retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)  # Exponential backoff, max 60s


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entries to newer versions."""
    if entry.version < 2:
        _LOGGER.info("Migrating TunnelVision config entry from version %s to 2", entry.version)
        new_data = {**entry.data}
        new_data.setdefault(CONF_USE_SSL, False)
        new_data.setdefault(CONF_VERIFY_SSL, True)
        hass.config_entries.async_update_entry(entry, data=new_data, version=2)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TunnelVision from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = TunnelVisionCoordinator(
        hass,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        api_key=entry.data.get(CONF_API_KEY, ""),
        use_ssl=entry.data.get(CONF_USE_SSL, False),
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, True),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Start SSE for instant updates (polling is fallback)
    coordinator.start_sse()

    # Register services
    async def handle_vpn_action(call: ServiceCall):
        action = call.data.get("action", "restart")
        actions = {
            "restart": "/api/v1/vpn/restart",
            "disconnect": "/api/v1/vpn/disconnect",
            "reconnect": "/api/v1/vpn/reconnect",
            "rotate": "/api/v1/vpn/rotate",
        }
        path = actions.get(action)
        if path:
            await coordinator.api_post(path)
            await coordinator.async_request_refresh()

    async def handle_qbt_action(call: ServiceCall):
        action = call.data.get("action", "restart")
        actions = {
            "restart": "/api/v1/qbt/restart",
            "pause": "/api/v1/qbt/pause",
            "resume": "/api/v1/qbt/resume",
        }
        path = actions.get(action)
        if path:
            await coordinator.api_post(path)
            await coordinator.async_request_refresh()

    async def handle_killswitch(call: ServiceCall):
        action = call.data.get("action", "enable")
        if action not in ("enable", "disable"):
            _LOGGER.error("Invalid killswitch action: %s", action)
            return
        path = f"/api/v1/killswitch/{action}"
        await coordinator.api_post(path)
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "vpn", handle_vpn_action)
    hass.services.async_register(DOMAIN, "qbittorrent", handle_qbt_action)
    hass.services.async_register(DOMAIN, "killswitch", handle_killswitch)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator:
        coordinator.stop_sse()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        # Unregister services when last entry is removed
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "vpn")
            hass.services.async_remove(DOMAIN, "qbittorrent")
            hass.services.async_remove(DOMAIN, "killswitch")
    return unload_ok
