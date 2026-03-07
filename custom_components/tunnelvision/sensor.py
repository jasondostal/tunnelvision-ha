"""Sensor platform for TunnelVision."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfDataRate, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import TunnelVisionEntity

SENSORS = [
    {
        "key": "vpn_state",
        "name": "VPN State",
        "icon": "mdi:vpn",
    },
    {
        "key": "public_ip",
        "name": "Public IP",
        "icon": "mdi:ip-network",
    },
    {
        "key": "country",
        "name": "Country",
        "icon": "mdi:earth",
    },
    {
        "key": "city",
        "name": "City",
        "icon": "mdi:city",
    },
    {
        "key": "location",
        "name": "Location",
        "icon": "mdi:map-marker",
    },
    {
        "key": "download_speed",
        "name": "Download Speed",
        "icon": "mdi:download",
        "device_class": SensorDeviceClass.DATA_RATE,
        "native_unit": UnitOfDataRate.BYTES_PER_SECOND,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "upload_speed",
        "name": "Upload Speed",
        "icon": "mdi:upload",
        "device_class": SensorDeviceClass.DATA_RATE,
        "native_unit": UnitOfDataRate.BYTES_PER_SECOND,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "active_torrents",
        "name": "Active Torrents",
        "icon": "mdi:download-circle",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "total_torrents",
        "name": "Total Torrents",
        "icon": "mdi:harddisk",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "transfer_rx",
        "name": "Total Downloaded",
        "icon": "mdi:download",
        "device_class": SensorDeviceClass.DATA_SIZE,
        "native_unit": UnitOfInformation.BYTES,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "key": "transfer_tx",
        "name": "Total Uploaded",
        "icon": "mdi:upload",
        "device_class": SensorDeviceClass.DATA_SIZE,
        "native_unit": UnitOfInformation.BYTES,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "key": "provider",
        "name": "VPN Provider",
        "icon": "mdi:shield-account",
    },
    {
        "key": "forwarded_port",
        "name": "Forwarded Port",
        "icon": "mdi:lan-connect",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "dns_state",
        "name": "DNS State",
        "icon": "mdi:dns",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "http_proxy_state",
        "name": "HTTP Proxy State",
        "icon": "mdi:web",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "socks_proxy_state",
        "name": "SOCKS Proxy State",
        "icon": "mdi:sock",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TunnelVision sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TunnelVisionSensor(coordinator, entry, s) for s in SENSORS
    )


class TunnelVisionSensor(TunnelVisionEntity, SensorEntity):
    """A TunnelVision sensor entity."""

    def __init__(self, coordinator, entry: ConfigEntry, description: dict):
        super().__init__(coordinator)
        self._key = description["key"]
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._attr_name = description["name"]
        self._attr_icon = description.get("icon")
        if "device_class" in description:
            self._attr_device_class = description["device_class"]
        if "native_unit" in description:
            self._attr_native_unit_of_measurement = description["native_unit"]
        if "state_class" in description:
            self._attr_state_class = description["state_class"]
        if "entity_category" in description:
            self._attr_entity_category = description["entity_category"]

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get(self._key)
        return None
