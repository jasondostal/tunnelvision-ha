"""Button platform for TunnelVision."""

import logging

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BUTTONS = [
    {
        "key": "vpn_restart",
        "name": "Restart VPN",
        "path": "/api/v1/vpn/restart",
        "icon": "mdi:vpn",
        "device_class": ButtonDeviceClass.RESTART,
    },
    {
        "key": "vpn_rotate",
        "name": "Rotate Server",
        "path": "/api/v1/vpn/rotate",
        "icon": "mdi:earth-arrow-right",
    },
    {
        "key": "qbt_restart",
        "name": "Restart qBittorrent",
        "path": "/api/v1/qbt/restart",
        "icon": "mdi:restart",
        "device_class": ButtonDeviceClass.RESTART,
    },
    {
        "key": "qbt_pause",
        "name": "Pause All Torrents",
        "path": "/api/v1/qbt/pause",
        "icon": "mdi:pause-circle",
    },
    {
        "key": "qbt_resume",
        "name": "Resume All Torrents",
        "path": "/api/v1/qbt/resume",
        "icon": "mdi:play-circle",
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TunnelVision buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TunnelVisionButton(coordinator, entry, b) for b in BUTTONS
    )


class TunnelVisionButton(CoordinatorEntity, ButtonEntity):
    """A TunnelVision action button."""

    def __init__(self, coordinator, entry: ConfigEntry, description: dict):
        super().__init__(coordinator)
        self._path = description["path"]
        self._attr_unique_id = f"{entry.entry_id}_{description['key']}"
        self._attr_name = f"TunnelVision {description['name']}"
        self._attr_icon = description.get("icon")
        if "device_class" in description:
            self._attr_device_class = description["device_class"]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": "TunnelVision",
            "manufacturer": "TunnelVision",
            "model": "VPN Container",
            "sw_version": "0.3.0",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("TunnelVision action: %s", self._path)
        await self.coordinator.api_post(self._path)
        await self.coordinator.async_request_refresh()
