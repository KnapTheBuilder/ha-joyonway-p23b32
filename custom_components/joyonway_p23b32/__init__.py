"""
# 2026-05-21 | Init | Joyonway ha-joyonway-p23b32 v0.2 | Depend: coordinator
Setup principal de l'integration Home Assistant pour la famille Joyonway 1A/1D.

Supporte :
- Joyonway P23B32 V2 (2019)
- Joyonway P20B29-2032 V183
- Joyonway P25B85

Plateformes :
- sensor (temperature, consigne, etat chauffage)
- button (10 boutons commandes equipements validees)
- climate (TODO v0.3 : setpoint write apres validation CRC)

Auteur : Christophe Knap (KnapTheBuilder)
Licence : MIT
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_W610_HOST,
    CONF_W610_PORT,
    DEFAULT_PORT,
    DOMAIN,
)
from .coordinator import JoyonwayCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    # 2026-05-21 | Setup | Initialisation integration | Depend: coordinator
    """
    host = entry.data[CONF_W610_HOST]
    port = entry.data.get(CONF_W610_PORT, DEFAULT_PORT)

    coordinator = JoyonwayCoordinator(hass, entry, host, port)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    # 2026-05-21 | Teardown | Decharge l'integration proprement | Depend: hass.data
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
