"""Button platform for TunnelVision."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import TunnelVisionEntity

if TYPE_CHECKING:
    from . import TunnelVisionCoordinator

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


class TunnelVisionButton(TunnelVisionEntity, ButtonEntity):
    """A TunnelVision action button."""

    coordinator: "TunnelVisionCoordinator"

    def __init__(self, coordinator: "TunnelVisionCoordinator", entry: ConfigEntry, description: dict):
        super().__init__(coordinator)
        self._path = description["path"]
        self._attr_unique_id = f"{entry.entry_id}_{description['key']}"
        self._attr_name = description["name"]
        self._attr_icon = description.get("icon")
        if "device_class" in description:
            self._attr_device_class = description["device_class"]

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("TunnelVision action: %s", self._path)
        await self.coordinator.api_post(self._path)
        await self.coordinator.async_request_refresh()
