"""
# 2026-05-21 | Coordinator | Polling RS485 via W610 | Depend: socket TCP, unescape KDy
Coordinator HA pour lire en continu les broadcasts B4 depuis le pont USR-W610
et envoyer les commandes A1 (panel -> mainboard).

Architecture :
- Ouvre une connexion TCP unique vers le W610 (port 8899 par defaut)
- Lit en continu, extrait les trames 0x1A...0x1D
- Applique l'unescape KDy (post #90)
- Decode le broadcast B4 le plus recent
- Expose dans coordinator.data pour les plateformes (sensor, binary_sensor, switch)

ATTENTION : le W610 accepte UNE SEULE connexion TCP a la fois.
Si l'app mobile Joyonway est ouverte, le coordinator echouera.

Auteur : Christophe Knap (KnapTheBuilder)
Licence : MIT
"""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    BROADCAST_TYPE,
    COMMAND_INTERVAL_SECONDS,
    COMMAND_REPEAT_COUNT,
    DOMAIN,
    SCAN_INTERVAL_SECONDS,
)
from .unescape import (
    decode_b4_broadcast,
    extract_frames,
    unescape_frame,
)

_LOGGER = logging.getLogger(__name__)


class JoyonwayCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """
    # 2026-05-21 | Coordinator | Lecture broadcast B4 + envoi commandes | Depend: W610
    Polling RS485 via socket TCP vers USR-W610.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        host: str,
        port: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"Joyonway {host}:{port}",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self._host = host
        self._port = port
        self._entry = entry
        self._read_buffer = bytearray()
        self._last_b4: bytes | None = None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Joyonway Spa",
            manufacturer="Joyonway",
            model="P23B32 V2 / P20B29 / P25B85 (1A/1D family)",
            sw_version="0.2.0",
            configuration_url=f"http://{self._host}:80",
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """
        # 2026-05-21 | Update | Lecture trames B4 depuis W610 | Depend: socket
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=5,
            )
        except (OSError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Connexion W610 echouee : {err}") from err

        try:
            # Lire 2 secondes de donnees pour capturer au moins un B4
            try:
                chunk = await asyncio.wait_for(reader.read(8192), timeout=2)
                self._read_buffer.extend(chunk)
            except asyncio.TimeoutError:
                pass

            # Extraire les trames
            frames = extract_frames(bytes(self._read_buffer))
            # Garder uniquement les bytes apres la derniere trame complete
            if frames:
                last_end = self._read_buffer.rfind(0x1D)
                if last_end >= 0:
                    self._read_buffer = self._read_buffer[last_end + 1:]

            # Trouver le dernier broadcast B4
            for raw_frame in reversed(frames):
                unescaped = unescape_frame(raw_frame)
                if len(unescaped) >= 6 and unescaped[5] == BROADCAST_TYPE:
                    self._last_b4 = unescaped
                    break

            if self._last_b4 is None:
                _LOGGER.debug("Aucun broadcast B4 dans cette lecture")
                # Garder les donnees precedentes si elles existent
                return self.data or {"decoded": None, "last_b4": None}

            decoded = decode_b4_broadcast(self._last_b4)
            return {
                "decoded": decoded,
                "last_b4_hex": self._last_b4.hex(),
            }

        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def send_command(self, command_hex: str) -> bool:
        """
        # 2026-05-21 | Action | Envoi commande A1 vers W610 | Depend: socket
        Envoie une trame de commande, repete COMMAND_REPEAT_COUNT fois pour fiabilite.

        Args:
            command_hex : trame complete en hex (delimiteurs inclus)

        Returns:
            bool : True si envoi sans exception, False sinon
        """
        try:
            frame = bytes.fromhex(command_hex.replace(" ", ""))
        except ValueError:
            _LOGGER.error("Trame hex invalide : %s", command_hex)
            return False

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=5,
            )
        except (OSError, asyncio.TimeoutError) as err:
            _LOGGER.error("Connexion W610 pour envoi echouee : %s", err)
            return False

        try:
            for i in range(COMMAND_REPEAT_COUNT):
                writer.write(frame)
                await writer.drain()
                if i < COMMAND_REPEAT_COUNT - 1:
                    await asyncio.sleep(COMMAND_INTERVAL_SECONDS)
            _LOGGER.info(
                "Commande envoyee %d fois : %s",
                COMMAND_REPEAT_COUNT,
                frame.hex(),
            )
            return True
        except Exception as err:
            _LOGGER.error("Erreur envoi commande : %s", err)
            return False
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
