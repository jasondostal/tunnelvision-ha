"""Switch platform for TunnelVision — toggleable state entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import TunnelVisionEntity

if TYPE_CHECKING:
    from . import TunnelVisionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TunnelVision switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TunnelVisionVPNSwitch(coordinator, entry),
        TunnelVisionKillswitchSwitch(coordinator, entry),
    ])


class TunnelVisionVPNSwitch(TunnelVisionEntity, SwitchEntity):
    """VPN connection toggle — on/off maps to connect/disconnect."""

    _attr_icon = "mdi:vpn"
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_name = "VPN"
    coordinator: TunnelVisionCoordinator

    def __init__(self, coordinator: TunnelVisionCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_vpn_switch"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("vpn_state") == "up"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/vpn/reconnect")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/vpn/disconnect")
        await self.coordinator.async_request_refresh()


class TunnelVisionKillswitchSwitch(TunnelVisionEntity, SwitchEntity):
    """Killswitch toggle — on/off maps to enable/disable."""

    _attr_icon = "mdi:shield-lock"
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_name = "Killswitch"
    coordinator: TunnelVisionCoordinator

    def __init__(self, coordinator: TunnelVisionCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_killswitch_switch"

    @property
    def is_on(self) -> bool:
        ks = self.coordinator.data.get("killswitch", "disabled")
        return ks in ("active", "gluetun")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/killswitch/enable")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/killswitch/disable")
        await self.coordinator.async_request_refresh()
