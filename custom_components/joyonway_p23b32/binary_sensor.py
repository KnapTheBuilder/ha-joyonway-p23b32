# 2026-05-13 | Binary Sensor | Etats spa + connectivite W610 | Depend: coordinator.data
"""Binary sensors Joyonway P23B32 : etats equipements + connectivite W610."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

BS = [
    ("filtration", "Filtration", "mdi:pump", None),
    ("pompe_gauche", "Pompe jets gauche", "mdi:pump", None),
    ("pompe_droite", "Pompe jets droite", "mdi:turbine", None),
    ("bulleur", "Bulleur", "mdi:weather-windy", None),
    ("lumiere", "Lumiere", "mdi:lightbulb", None),
    ("chauffage", "Chauffage", "mdi:fire", BinarySensorDeviceClass.HEAT),
]


async def async_setup_entry(hass, entry, async_add_entities):
    """Configure les binary sensors depuis le config entry."""
    c = hass.data[DOMAIN][entry.entry_id]
    entities = [JoyonwayBS(c, entry, k, n, i, d) for k, n, i, d in BS]
    entities.append(JoyonwayConn(c, entry))
    async_add_entities(entities)


def _di(entry):
    """Construit le DeviceInfo commun a tous les binary sensors."""
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": "Joyonway P23B32",
        "manufacturer": "Joyonway",
        "model": "P23B32",
        "configuration_url": f"http://{entry.data[CONF_HOST]}",
    }


class JoyonwayBS(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor lisant un bit d'etat dans coordinator.data."""

    def __init__(self, c, entry, key, name, icon, dc):
        """Initialise le binary sensor."""
        super().__init__(c)
        self._key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_class = dc
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = _di(entry)

    @property
    def is_on(self):
        """Retourne True si le bit d'etat est arme."""
        return self.coordinator.data.get(self._key, False) if self.coordinator.data else None

    @property
    def available(self) -> bool:
        """Retourne True si le coordinator est en ligne."""
        return self.coordinator.available


class JoyonwayConn(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor exposant la connectivite TCP au W610."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_name = "Connexion W610"
    _attr_icon = "mdi:wifi-check"

    def __init__(self, c, entry):
        """Initialise le sensor de connectivite."""
        super().__init__(c)
        self._attr_unique_id = f"{entry.entry_id}_connectivity"
        self._attr_device_info = _di(entry)

    @property
    def is_on(self) -> bool:
        """Retourne True si le coordinator considere le W610 en ligne."""
        return self.coordinator.available
