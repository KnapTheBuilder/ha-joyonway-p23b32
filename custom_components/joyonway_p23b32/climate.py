# 2026-05-27 | Plateforme Climate | Thermostat HA natif Joyonway via CRC alexbde | Depend: rs485.send_command, crc.py
"""Climate platform for Joyonway P23B32 spa.

Exposes a native Home Assistant climate entity:
- current_temperature : water temperature read from coordinator broadcast
- target_temperature  : setpoint, settable from HA UI
- range : 15.5 C to 40 C, step 0.5 C

Sending a new setpoint calls rs485.send_command(CMD_CONSIGNE, consigne_f=...)
which uses the @alexbde CRC-32 algorithm (crc.py) to build the correct
A1 command frame dynamically (no static capture table).
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, CONF_HOST, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CMD_CONSIGNE,
    DOMAIN,
    MAX_TEMP_C,
    MIN_TEMP_C,
    STEP_TEMP_C,
)
from .rs485 import send_command

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Joyonway climate entity from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JoyonwayThermostat(coordinator, entry)])


class JoyonwayThermostat(CoordinatorEntity, ClimateEntity):
    """Native HA thermostat for the spa."""

    _attr_has_entity_name = True
    _attr_name = "Thermostat"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = MIN_TEMP_C
    _attr_max_temp = MAX_TEMP_C
    _attr_target_temperature_step = STEP_TEMP_C
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the thermostat."""
        super().__init__(coordinator)
        self._entry = entry
        self._host = coordinator.host
        self._port = coordinator.port
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Joyonway P23B32",
            manufacturer="Joyonway",
            model="P23B32",
            configuration_url=f"http://{entry.data[CONF_HOST]}",
        )

    @property
    def available(self) -> bool:
        """Return True if the coordinator is online."""
        return self.coordinator.available

    @property
    def current_temperature(self) -> float | None:
        """Return current water temperature in Celsius."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("water_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature (setpoint) in Celsius."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("setpoint")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature.

        Converts Celsius to Fahrenheit, clamps to 60..104 F (15.5..40 C),
        and sends CMD_CONSIGNE via rs485.send_command. The frame is built
        dynamically by the CRC-32 algorithm (crc.py).
        """
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        temperature = max(MIN_TEMP_C, min(MAX_TEMP_C, float(temperature)))
        temp_f = round((temperature * 9 / 5) + 32)
        temp_f = max(60, min(104, temp_f))

        _LOGGER.info(
            "Sending setpoint %.1f C (%d F) via CRC algorithm",
            temperature, temp_f,
        )
        ok = await send_command(self._host, self._port, CMD_CONSIGNE, consigne_f=temp_f)
        if not ok:
            _LOGGER.warning("Echec envoi consigne %.1f C", temperature)
            return

        await self.coordinator.async_request_refresh()
