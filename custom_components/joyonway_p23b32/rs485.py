# 2026-05-13 | RS485 | Trames de commandes Joyonway P23B32 et envoi via TCP vers USR-W610 | Dépend: asyncio, const.py
"""Trames RS485 confirmees et helper d'envoi TCP vers le pont USR-W610.

Source des trames : capture live RS485 effectuee depuis l'app Joyonway sur
le bus du controleur P23B32 (V2, 2019). Le P23B32 ne valide pas le CRC,
donc les trames capturees peuvent etre rejouees directement.

Protocole observe :
- Bus RS485, 9600 baud 8N1 (mode passif/lecture) et envoi command frames
- Delimiteurs : 0x1A (debut) / 0x1D (fin)
- Byte 5 : type de trame (0xA1 = commande equipement, 0xA4 = filtration,
  0xAA = arret total)
"""

from __future__ import annotations

import asyncio
import logging

from .const import (
    CMD_ALL_OFF,
    CMD_BULLEUR_OFF,
    CMD_BULLEUR_ON,
    CMD_CONSIGNE,
    CMD_FILTRATION,
    CMD_LUMIERE_OFF,
    CMD_LUMIERE_ON,
    CMD_POMPE_DROITE_OFF,
    CMD_POMPE_DROITE_ON,
    CMD_POMPE_GAUCHE_OFF,
    CMD_POMPE_GAUCHE_ON,
    REPEAT_COUNT,
    REPEAT_INTERVAL,
    TCP_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


# 2026-05-13 | Trames | Commandes RS485 confirmees physiquement | Dépend: captures Joyonway app
FRAMES: dict[str, bytes] = {
    CMD_LUMIERE_ON: bytes.fromhex(
        "1a0130103ca100a100000040400204000081edbaa01b141d"
    ),
    CMD_LUMIERE_OFF: bytes.fromhex(
        "1a0130103ca100a10000004040020400" "00805a20cdc11d"
    ),
    CMD_POMPE_GAUCHE_ON: bytes.fromhex(
        "1a0130103ca100a1060400000204000000" "8b3ee4131d"
    ),
    CMD_POMPE_GAUCHE_OFF: bytes.fromhex(
        "1a0130103ca100a1060000000204000000" "08bd10331d"
    ),
    CMD_POMPE_DROITE_ON: bytes.fromhex(
        "1a0130103ca100a1181000000204000000" "40d12de01d"
    ),
    CMD_POMPE_DROITE_OFF: bytes.fromhex(
        "1a0130103ca100a1180000000204000000" "4cdfff631d"
    ),
    CMD_BULLEUR_ON: bytes.fromhex(
        "1a0130103ca100a1000004040204000000" "0f7f1b11761d"
    ),
    CMD_BULLEUR_OFF: bytes.fromhex(
        "1a0130103ca100a1000004000204000000" "fcc2864f1d"
    ),
    CMD_FILTRATION: bytes.fromhex(
        "1a0130103ca400a16205001600170006" "00fc7954c61d"
    ),
    CMD_ALL_OFF: bytes.fromhex(
        "1a0130083caa0002138ce4268b1d"
    ),
}


def build_consigne_frame(temp_f: int) -> bytes:
    """Construit la trame de consigne thermostat pour une temperature en F.

    Le byte d'index 16 (0-based) porte la valeur de consigne en Fahrenheit.
    Exemple : 100 F = 0x64, ce qui correspond a 37.8 C.
    """
    if not 60 <= temp_f <= 104:
        raise ValueError(f"Consigne hors plage securisee: {temp_f} F")
    template = bytearray(
        bytes.fromhex("1a0130103ca100a10000008080020400000000987 9d0e21d".replace(" ", ""))
    )
    template[16] = temp_f & 0xFF
    return bytes(template)


async def send_command(
    host: str,
    port: int,
    command: str,
    consigne_f: int | None = None,
    repeat: int = REPEAT_COUNT,
    interval: float = REPEAT_INTERVAL,
) -> bool:
    """Envoie une commande RS485 via TCP au pont USR-W610.

    Retourne True si la commande a ete envoyee, False sinon.
    Pour command == 'consigne', consigne_f doit etre fournie (degres Fahrenheit).
    """
    if command == CMD_CONSIGNE:
        if consigne_f is None:
            _LOGGER.error("Commande consigne sans valeur consigne_f")
            return False
        try:
            frame = build_consigne_frame(consigne_f)
        except ValueError as err:
            _LOGGER.error("Consigne invalide: %s", err)
            return False
    elif command in FRAMES:
        frame = FRAMES[command]
    else:
        _LOGGER.error("Commande inconnue: %s", command)
        return False

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=TCP_TIMEOUT
        )
    except (OSError, asyncio.TimeoutError) as err:
        _LOGGER.error("Connexion W610 %s:%s impossible: %s", host, port, err)
        return False

    try:
        for i in range(repeat):
            writer.write(frame)
            await writer.drain()
            if i < repeat - 1:
                await asyncio.sleep(interval)
        _LOGGER.debug(
            "Commande %s envoyee (%d repetitions, %d bytes)",
            command, repeat, len(frame),
        )
        return True
    except OSError as err:
        _LOGGER.error("Erreur ecriture RS485: %s", err)
        return False
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except OSError:
            pass


async def test_connection(host: str, port: int) -> bool:
    """Teste la connexion TCP au pont W610 (utilise par config_flow)."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=TCP_TIMEOUT
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (OSError, asyncio.TimeoutError) as err:
        _LOGGER.debug("Test connexion %s:%s echoue: %s", host, port, err)
        return False
