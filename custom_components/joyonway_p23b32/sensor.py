"""
# 2026-05-21 | Plateforme | Sensors Joyonway famille 1A/1D | Depend: coordinator, unescape
Plateforme sensor exposant les valeurs decodees du broadcast B4.

Capteurs crees :
- Temperature eau (Celsius)
- Consigne thermostat (Celsius)
- Etat chauffage (off / heating / cooldown / circulation / ozonator_active)
- Filtration en cours (booleen via binary_sensor)
- Lumiere allumee (booleen via binary_sensor)

Sources de validation :
- @KDy post #90 : parser B4 et table d'unescape
- @Yannickt26 post #109 : capture B4 reelle P20B29
- Tests sur trame Yannickt26 : temp eau 33.9C, consigne 37.2C coherent

Auteur : Christophe Knap (KnapTheBuilder)
Licence : MIT
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import JoyonwayCoordinator

_LOGGER = logging.getLogger(__name__)


# 2026-05-21 | Config | Descriptions des capteurs natifs | Depend: HA core
SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        name="Temperature eau",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
    ),
    SensorEntityDescription(
        key="setpoint",
        translation_key="setpoint",
        name="Consigne thermostat",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermostat",
    ),
    SensorEntityDescription(
        key="heating_state",
        translation_key="heating_state",
        name="Etat chauffage",
        icon="mdi:radiator",
    ),
    SensorEntityDescription(
        key="water_temperature_fahrenheit",
        translation_key="water_temperature_fahrenheit",
        name="Temperature eau (F)",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="setpoint_fahrenheit",
        translation_key="setpoint_fahrenheit",
        name="Consigne (F)",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermostat",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    # 2026-05-21 | Setup | Enregistrement plateforme sensor | Depend: coordinator dans hass.data
    """
    coordinator: JoyonwayCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        JoyonwaySensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class JoyonwaySensor(CoordinatorEntity[JoyonwayCoordinator], SensorEntity):
    """
    # 2026-05-21 | Entite | Capteur generique Joyonway | Depend: JoyonwayCoordinator
    Capteur generique parsant le dernier broadcast B4 unescape.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: JoyonwayCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Any:
        """Retourne la valeur du capteur."""
        if not self.coordinator.data:
            return None
        decoded = self.coordinator.data.get("decoded")
        if not decoded:
            return None

        key = self.entity_description.key
        mapping = {
            "water_temperature": "water_temp_celsius",
            "setpoint": "setpoint_celsius",
            "heating_state": "heating_state",
            "water_temperature_fahrenheit": "water_temp_fahrenheit",
            "setpoint_fahrenheit": "setpoint_fahrenheit",
        }
        return decoded.get(mapping.get(key))

    @property
    def available(self) -> bool:
        """Disponible si broadcast B4 recent valide."""
        if not super().available:
            return False
        data = self.coordinator.data
        return bool(data and data.get("decoded"))
