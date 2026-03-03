"""Switch platform for TunnelVision — toggleable state entities."""

import logging

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

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


class TunnelVisionVPNSwitch(CoordinatorEntity, SwitchEntity):
    """VPN connection toggle — on/off maps to connect/disconnect."""

    _attr_icon = "mdi:vpn"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_vpn_switch"
        self._attr_name = "TunnelVision VPN"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("vpn_state") == "up"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": "TunnelVision",
            "manufacturer": "TunnelVision",
            "model": "VPN Container",
        }

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/vpn/reconnect")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/vpn/disconnect")
        await self.coordinator.async_request_refresh()


class TunnelVisionKillswitchSwitch(CoordinatorEntity, SwitchEntity):
    """Killswitch toggle — on/off maps to enable/disable."""

    _attr_icon = "mdi:shield-lock"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_killswitch_switch"
        self._attr_name = "TunnelVision Killswitch"

    @property
    def is_on(self) -> bool:
        ks = self.coordinator.data.get("killswitch", "disabled")
        return ks in ("active", "gluetun")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": "TunnelVision",
            "manufacturer": "TunnelVision",
            "model": "VPN Container",
        }

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/killswitch/enable")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api_post("/api/v1/killswitch/disable")
        await self.coordinator.async_request_refresh()
