# 2026-05-13 | Plateforme button | Expose toutes les commandes RS485 confirmees | Dépend: rs485.py, __init__.py
"""Boutons Joyonway P23B32 (commandes one-shot via RS485)."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CMD_ALL_OFF,
    CMD_BULLEUR_OFF,
    CMD_BULLEUR_ON,
    CMD_FILTRATION,
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

# 2026-05-13 | Mapping | (cle commande, libelle UI, icone mdi) | Dépend: const.py
BUTTONS: list[tuple[str, str, str]] = [
    (CMD_LUMIERE_ON, "Lumiere ON", "mdi:lightbulb-on"),
    (CMD_LUMIERE_OFF, "Lumiere OFF", "mdi:lightbulb-off"),
    (CMD_POMPE_GAUCHE_ON, "Pompe gauche ON", "mdi:pump"),
    (CMD_POMPE_GAUCHE_OFF, "Pompe gauche OFF", "mdi:pump-off"),
    (CMD_POMPE_DROITE_ON, "Pompe droite ON", "mdi:pump"),
    (CMD_POMPE_DROITE_OFF, "Pompe droite OFF", "mdi:pump-off"),
    (CMD_BULLEUR_ON, "Bulleur ON", "mdi:chart-bubble"),
    (CMD_BULLEUR_OFF, "Bulleur OFF", "mdi:chart-bubble"),
    (CMD_FILTRATION, "Filtration", "mdi:filter"),
    (CMD_ALL_OFF, "Tout eteindre", "mdi:power-off"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Joyonway buttons from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    host: str = data["host"]
    port: int = data["port"]

    entities = [
        JoyonwayButton(entry.entry_id, host, port, cmd, label, icon)
        for cmd, label, icon in BUTTONS
    ]
    async_add_entities(entities)


class JoyonwayButton(ButtonEntity):
    """Bouton one-shot pour une commande Joyonway."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry_id: str,
        host: str,
        port: int,
        command: str,
        label: str,
        icon: str,
    ) -> None:
        """Initialise le bouton."""
        self._entry_id = entry_id
        self._host = host
        self._port = port
        self._command = command
        self._attr_name = label
        self._attr_icon = icon
        self._attr_unique_id = f"{entry_id}_{command}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Joyonway P23B32",
            manufacturer="Joyonway",
            model="P23B32",
        )

    async def async_press(self) -> None:
        """Envoie la commande RS485."""
        ok = await send_command(self._host, self._port, self._command)
        if not ok:
            _LOGGER.warning("Echec envoi commande %s", self._command)
