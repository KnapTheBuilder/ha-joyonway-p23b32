# 2026-05-27 | Plateforme Switch | 4 switches bidirectionnels Joyonway | Depend: rs485.send_command
"""Switch platform for Joyonway P23B32 spa.

Exposes 4 bidirectional switches:
- switch.joyonway_p23b32_lumiere       : light
- switch.joyonway_p23b32_pompe_gauche  : left jets pump
- switch.joyonway_p23b32_pompe_droite  : right jets pump
- switch.joyonway_p23b32_bulleur       : blower (air bubbles)

State is mirrored from the broadcast (coordinator.data) and ON/OFF
commands use rs485.send_command (replay frames captured on P23B32 V2).

For one-shot commands (filtration, all_off), see the button platform.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CMD_BULLEUR_OFF,
    CMD_BULLEUR_ON,
    CMD_LUMIERE_OFF,
    CMD_LUMIERE_ON,
    CMD_POMPE_DROITE_OFF,
    CMD_POMPE_DROITE_ON,
    CMD_POMPE_GAUCHE_OFF,
    CMD_POMPE_GAUCHE_ON,
    DOMAIN,
)
from .rs485 import send_command

_LOGGER = logging.getLogger(__name__)

# (key suffix, display name, icon, state key in coordinator.data, ON command, OFF command)
SWITCHES: list[tuple[str, str, str, str, str, str]] = [
    ("lumiere",      "Lumiere",       "mdi:lightbulb",
     "lumiere",      CMD_LUMIERE_ON,       CMD_LUMIERE_OFF),
    ("pompe_gauche", "Pompe gauche",  "mdi:pump",
     "pompe_gauche", CMD_POMPE_GAUCHE_ON,  CMD_POMPE_GAUCHE_OFF),
    ("pompe_droite", "Pompe droite",  "mdi:pump",
     "pompe_droite", CMD_POMPE_DROITE_ON,  CMD_POMPE_DROITE_OFF),
    ("bulleur",      "Bulleur",       "mdi:chart-bubble",
     "bulleur",      CMD_BULLEUR_ON,       CMD_BULLEUR_OFF),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Joyonway switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        JoyonwaySwitch(
            coordinator, entry, key, name, icon, state_key, cmd_on, cmd_off
        )
        for key, name, icon, state_key, cmd_on, cmd_off in SWITCHES
    ]
    async_add_entities(entities)


class JoyonwaySwitch(CoordinatorEntity, SwitchEntity):
    """Bidirectional switch mirroring the broadcast state."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        state_key: str,
        cmd_on: str,
        cmd_off: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._host = coordinator.host
        self._port = coordinator.port
        self._key = key
        self._state_key = state_key
        self._cmd_on = cmd_on
        self._cmd_off = cmd_off

        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
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
    def is_on(self) -> bool | None:
        """Return the current state mirrored from the broadcast."""
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.get(self._state_key, False))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on by sending the ON RS485 command."""
        ok = await send_command(self._host, self._port, self._cmd_on)
        if not ok:
            _LOGGER.warning("Echec ON %s", self._key)
            return
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off by sending the OFF RS485 command."""
        ok = await send_command(self._host, self._port, self._cmd_off)
        if not ok:
            _LOGGER.warning("Echec OFF %s", self._key)
            return
        await self.coordinator.async_request_refresh()
