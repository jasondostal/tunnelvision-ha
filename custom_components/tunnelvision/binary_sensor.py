"""Binary sensor platform for TunnelVision."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from __future__ import annotations

from typing import Any

from .const import DOMAIN
from .entity import TunnelVisionEntity

BINARY_SENSORS = [
    {
        "key": "vpn_state",
        "name": "VPN Connected",
        "on_value": "up",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "icon_on": "mdi:vpn",
        "icon_off": "mdi:vpn-off",
    },
    {
        "key": "killswitch",
        "name": "Killswitch",
        "on_value": "active",
        "icon_on": "mdi:shield-lock",
        "icon_off": "mdi:shield-off",
    },
    {
        "key": "healthy",
        "name": "Healthy",
        "on_value": True,
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "icon_on": "mdi:heart-pulse",
        "icon_off": "mdi:heart-broken",
    },
    {
        "key": "qbt_state",
        "name": "qBittorrent",
        "on_value": "running",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "icon_on": "mdi:harddisk",
        "icon_off": "mdi:harddisk-remove",
    },
    {
        "key": "dns_state",
        "name": "DNS",
        "on_value": "running",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "icon_on": "mdi:dns",
        "icon_off": "mdi:dns-outline",
    },
    {
        "key": "http_proxy_state",
        "name": "HTTP Proxy",
        "on_value": "running",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "icon_on": "mdi:web",
        "icon_off": "mdi:web-off",
    },
    {
        "key": "socks_proxy_state",
        "name": "SOCKS Proxy",
        "on_value": "running",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "icon_on": "mdi:sock",
        "icon_off": "mdi:close-network",
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TunnelVision binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TunnelVisionBinarySensor(coordinator, entry, s) for s in BINARY_SENSORS
    )


class TunnelVisionBinarySensor(TunnelVisionEntity, BinarySensorEntity):
    """A TunnelVision binary sensor entity."""

    def __init__(self, coordinator: Any, entry: ConfigEntry, description: dict[str, Any]):
        super().__init__(coordinator)
        self._key = description["key"]
        self._on_value = description["on_value"]
        self._icon_on = description.get("icon_on")
        self._icon_off = description.get("icon_off")
        self._attr_unique_id = f"{entry.entry_id}_{self._key}_binary"
        self._attr_name = description["name"]
        if "device_class" in description:
            self._attr_device_class = description["device_class"]

    @property
    def is_on(self):
        if self.coordinator.data:
            return self.coordinator.data.get(self._key) == self._on_value
        return False

    @property
    def icon(self):
        if self.is_on:
            return self._icon_on
        return self._icon_off
