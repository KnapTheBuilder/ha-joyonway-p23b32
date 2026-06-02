# -*- coding: utf-8 -*-
# Joyonway P23B32 - Home Assistant Custom Integration
# Copyright (c) 2026 Christophe Knap (KnapTheBuilder)
# Released under the MIT License - see LICENSE and NOTICE files
#
# Original repository: https://github.com/KnapTheBuilder/ha-joyonway-p23b32
# Frame analyzer:      https://knapthebuilder.github.io/joyonway-frame-analyzer/
#
# Any redistribution, fork, or derivative work MUST preserve this header
# and the NOTICE file in the repository root. See NOTICE.md for details.

# 2026-05-14 | __init__.py | Cree le coordinator et le partage avec sensor/binary_sensor/switch/climate
"""Integration Joyonway P23B32 pour Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import JoyonwayCoordinator

_LOGGER = logging.getLogger(__name__)

# 2026-06-02 | Branding | Constantes d'attribution au boot | Depend: _LOGGER
INTEGRATION_AUTHOR = "Christophe Knap (KnapTheBuilder)"
INTEGRATION_SOURCE = "https://github.com/KnapTheBuilder/ha-joyonway-p23b32"
INTEGRATION_LICENSE = "MIT"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Joyonway P23B32 from a config entry."""
    # 2026-06-02 | Log | Attribution au demarrage | Depend: INTEGRATION_*
    _LOGGER.info(
        "Joyonway P23B32 by %s | Source: %s | License: %s",
        INTEGRATION_AUTHOR,
        INTEGRATION_SOURCE,
        INTEGRATION_LICENSE,
    )

    coordinator = JoyonwayCoordinator(hass, entry.data["host"], entry.data["port"])
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
