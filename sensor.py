# 2026-05-13 | Coordinator | Polling W610 et publication etat partage | Depend: rs485.read_spa_status
"""DataUpdateCoordinator pour Joyonway P23B32."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL
from .rs485 import read_spa_status

_LOGGER = logging.getLogger(__name__)


class JoyonwayCoordinator(DataUpdateCoordinator):
    """Coordinator polling le pont W610 pour l'etat du spa."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialise le coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.host = host
        self.port = port
        self._available = False

    @property
    def available(self) -> bool:
        """Retourne True si la derniere lecture a reussi."""
        return self._available

    async def _async_update_data(self):
        """Lit l'etat du spa via le W610."""
        data = await read_spa_status(self.host, self.port)
        if data is None:
            self._available = False
            raise UpdateFailed(f"Pas de reponse W610 {self.host}:{self.port}")
        self._available = True
        return data
