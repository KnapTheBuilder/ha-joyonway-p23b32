# 2026-05-13 | Sensor | Temperature eau et consigne en Celsius | Depend: coordinator.data
"""Sensors Joyonway P23B32 : temperature eau + consigne."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import CONF_HOST, UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

SENSORS = [
    ("water_temperature", "Temperature eau", "mdi:thermometer-water"),
    ("setpoint", "Consigne", "mdi:thermometer-chevron-up"),
]


async def async_setup_entry(hass, entry, async_add_entities):
    """Configure les sensors depuis le config entry."""
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JoyonwaySensor(c, entry, k, n, i) for k, n, i in SENSORS])


class JoyonwaySensor(CoordinatorEntity, SensorEntity):
    """Sensor de temperature lisant le coordinator."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, c, entry, key, name, icon):
        """Initialise le sensor."""
        super().__init__(c)
        self._key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Joyonway P23B32",
            "manufacturer": "Joyonway",
            "model": "P23B32",
            "configuration_url": f"http://{entry.data[CONF_HOST]}",
        }

    @property
    def native_value(self):
        """Retourne la valeur courante depuis le coordinator."""
        return self.coordinator.data.get(self._key) if self.coordinator.data else None

    @property
    def available(self) -> bool:
        """Retourne True si le coordinator est en ligne."""
        return self.coordinator.available
