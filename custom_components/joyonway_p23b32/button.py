"""
# 2026-05-21 | Plateforme | Buttons one-shot equipements Joyonway | Depend: coordinator, COMMANDS
Boutons one-shot pour les commandes validees forum :
- Lumiere ON/OFF
- Pompe gauche ON/OFF
- Pompe droite ON/OFF
- Bulleur ON/OFF
- Filtration

Trames cross-validees sur P23B32 V2 (KnapTheBuilder) et P20B29 (Yannickt26).

Auteur : Christophe Knap (KnapTheBuilder)
Licence : MIT
"""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COMMANDS, DOMAIN
from .coordinator import JoyonwayCoordinator

_LOGGER = logging.getLogger(__name__)


# 2026-05-21 | Config | Descriptions des boutons exposes | Depend: COMMANDS dans const
BUTTON_CONFIG = [
    ("light_on", "Lumiere ON", "LIGHT_ON", "mdi:lightbulb-on"),
    ("light_off", "Lumiere OFF", "LIGHT_OFF", "mdi:lightbulb-off"),
    ("pump_left_on", "Pompe gauche ON", "PUMP_LEFT_ON", "mdi:pump"),
    ("pump_left_off", "Pompe gauche OFF", "PUMP_LEFT_OFF", "mdi:pump-off"),
    ("pump_right_on", "Pompe droite ON", "PUMP_RIGHT_ON", "mdi:pump"),
    ("pump_right_off", "Pompe droite OFF", "PUMP_RIGHT_OFF", "mdi:pump-off"),
    ("blower_on", "Bulleur ON", "BLOWER_ON", "mdi:weather-windy"),
    ("blower_off", "Bulleur OFF", "BLOWER_OFF", "mdi:weather-windy-variant"),
    ("filtration", "Filtration", "FILTRATION", "mdi:filter"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    # 2026-05-21 | Setup | Enregistrement plateforme button | Depend: coordinator
    """
    coordinator: JoyonwayCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        JoyonwayButton(coordinator, entry, key, name, command_id, icon)
        for key, name, command_id, icon in BUTTON_CONFIG
    ]
    async_add_entities(entities)


class JoyonwayButton(ButtonEntity):
    """
    # 2026-05-21 | Entite | Bouton one-shot equipement spa | Depend: JoyonwayCoordinator
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: JoyonwayCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        command_id: str,
        icon: str,
    ) -> None:
        self._coordinator = coordinator
        self._command_id = command_id
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """
        # 2026-05-21 | Action | Pression bouton -> envoi commande | Depend: coordinator.send_command
        """
        command_hex = COMMANDS.get(self._command_id)
        if not command_hex:
            _LOGGER.error("Commande inconnue : %s", self._command_id)
            return
        success = await self._coordinator.send_command(command_hex)
        if success:
            _LOGGER.info("Bouton %s : commande envoyee", self._command_id)
            # Forcer un refresh pour voir l'effet
            await self._coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Bouton %s : envoi echoue", self._command_id)
