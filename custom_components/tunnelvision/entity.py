"""Base entity for TunnelVision integration."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION


class TunnelVisionEntity(CoordinatorEntity):
    """Base class for TunnelVision entities — shared device_info and naming."""

    _attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": "TunnelVision",
            "manufacturer": "TunnelVision",
            "model": "VPN Container",
            "sw_version": VERSION,
        }
