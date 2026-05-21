"""
# 2026-05-21 | Config Flow | UI de configuration Joyonway | Depend: const, HA core
Flow de configuration pour ha-joyonway-p23b32 v0.2.

Demande a l'utilisateur :
- IP du pont USR-W610 (port 8899 par defaut)
- Modele de controleur (optionnel, info uniquement pour v0.2)
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CONTROLLER_MODEL,
    CONF_W610_HOST,
    CONF_W610_PORT,
    DEFAULT_PORT,
    DOMAIN,
    SUPPORTED_MODELS,
)

_LOGGER = logging.getLogger(__name__)


class JoyonwayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow Joyonway."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """
        # 2026-05-21 | Step | Configuration initiale | Depend: vol schema
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_W610_HOST]
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Joyonway Spa ({host})",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_W610_HOST): str,
                vol.Optional(CONF_W610_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_CONTROLLER_MODEL, default=SUPPORTED_MODELS[0]): vol.In(
                    SUPPORTED_MODELS
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
