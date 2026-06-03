# 2026-05-14 | RS485 | Trames d'envoi + lecture broadcast | FIX Python 3.14 asyncio.get_running_loop()
# 2026-05-16 | FIX | Restauration MASK_CHAUFFAGE=0x10 et filtration=pb2&MASK_FILTRATION
# 2026-05-27 | v0.3.0 | build_consigne_frame() delegue a crc.py (algorithme @alexbde)
"""Trames RS485 Joyonway P23B32 : envoi commandes + lecture broadcast etat."""
from __future__ import annotations

import asyncio
import logging

from .const import (
    CMD_LUMIERE_ON, CMD_LUMIERE_OFF,
    CMD_POMPE_GAUCHE_ON, CMD_POMPE_GAUCHE_OFF,
    CMD_POMPE_DROITE_ON, CMD_POMPE_DROITE_OFF,
    CMD_BULLEUR_ON, CMD_BULLEUR_OFF,
    CMD_FILTRATION, CMD_ALL_OFF, CMD_CONSIGNE,
    TCP_TIMEOUT, REPEAT_COUNT, REPEAT_INTERVAL,
)
# v0.3.0 - import CRC alexbde pour generation dynamique de la consigne
from .crc import build_consigne_frame as _build_consigne_frame_crc

_LOGGER = logging.getLogger(__name__)

# ============================================================
# TRAMES DE COMMANDE (envoi) - validees physiquement le 11/05
# ============================================================
FRAMES: dict[str, bytes] = {
    CMD_LUMIERE_ON:       bytes.fromhex("1a0130103ca100a100000040400204000081edbaa01b141d"),
    CMD_LUMIERE_OFF:      bytes.fromhex("1a0130103ca100a1000000404002040000805a20cdc11d"),
    CMD_POMPE_GAUCHE_ON:  bytes.fromhex("1a0130103ca100a10604000002040000008b3ee4131d"),
    CMD_POMPE_GAUCHE_OFF: bytes.fromhex("1a0130103ca100a106000000020400000008bd10331d"),
    CMD_POMPE_DROITE_ON:  bytes.fromhex("1a0130103ca100a1181000000204000000" "40d12de01d"),
    CMD_POMPE_DROITE_OFF: bytes.fromhex("1a0130103ca100a1180000000204000000" "4cdfff631d"),
    CMD_BULLEUR_ON:       bytes.fromhex("1a0130103ca100a1000004040204000000" "0f7f1b11761d"),
    CMD_BULLEUR_OFF:      bytes.fromhex("1a0130103ca100a1000004000204000000" "fcc2864f1d"),
    CMD_FILTRATION:       bytes.fromhex("1a0130103ca400a1620500160017000600" "fc7954c61d"),
    CMD_ALL_OFF:          bytes.fromhex("1a0130083caa0002138ce4268b1d"),
}


def build_consigne_frame(temp_f: int) -> bytes:
    """Construit la trame de consigne thermostat pour une temperature en F.

    v0.3.0 : delegue a crc.py qui utilise l'algorithme @alexbde.
    Avant : CRC statique hardcode (incorrect pour la plupart des temperatures).
    Apres : CRC calcule dynamiquement, valide cross-modeles (P23B32 V2, P20B29).
    """
    return _build_consigne_frame_crc(temp_f)


# ============================================================
# LECTURE BROADCAST (parse trames recues du W610)
# ============================================================
# Byte 12: 0x04=pompe_gauche, 0x10=pompe_droite (relatif a byte 0 signature)
# Byte 14: 0x01=filtration, 0x08=bulleur, 0x10=chauffage
# Byte 17: 0x01=lumiere
BROADCAST_SIGNATURE = bytes([0x1A, 0xFF, 0x01, 0x3C, 0xD2, 0xB4, 0xFF, 0x08, 0x02])
FRAME_MIN_LENGTH = 20
IDX_WATER_TEMP = 9
IDX_PUMP_BYTE1 = 12
IDX_PUMP_BYTE2 = 14
IDX_SETPOINT = 16
IDX_LIGHT_BYTE = 17
MASK_POMPE_GAUCHE = 0x04
MASK_POMPE_DROITE = 0x10
MASK_FILTRATION = 0x01
MASK_BULLEUR = 0x08
# 2026-05-16 FIX: 0x10 confirme par trame heater (byte14=0x31=0x20+0x10+0x01)
MASK_CHAUFFAGE = 0x10
MASK_LUMIERE = 0x01


def fahrenheit_to_celsius(f):
    """Convertit F en C avec gestion des valeurs invalides."""
    if f == 0 or f > 200:
        return None
    return round((f - 32) * 5 / 9, 1)


async def read_spa_status(host: str, port: int, timeout: float = 5.0):
    """Lit une trame d'etat broadcast du W610.

    FIX Python 3.14: utilise asyncio.get_running_loop() au lieu de get_event_loop().
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
    except (OSError, asyncio.TimeoutError) as err:
        _LOGGER.debug("W610 connexion impossible: %s", err)
        return None
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    try:
        buf = bytearray()
        while loop.time() < deadline:
            try:
                chunk = await asyncio.wait_for(reader.read(512), timeout=1.0)
                if not chunk:
                    break
                buf.extend(chunk)
                idx = buf.find(BROADCAST_SIGNATURE)
                if idx != -1 and len(buf) >= idx + FRAME_MIN_LENGTH:
                    return _parse(buf, idx)
                if len(buf) > 4096:
                    buf = buf[-1024:]
            except asyncio.TimeoutError:
                continue
        _LOGGER.debug("W610 timeout: %d octets lus, pas de trame complete", len(buf))
        return None
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


def _parse(buf, idx):
    """Decode une trame broadcast 0xB4 a partir de l'index de signature."""
    tf = buf[idx + IDX_WATER_TEMP]
    pb1 = buf[idx + IDX_PUMP_BYTE1]
    pb2 = buf[idx + IDX_PUMP_BYTE2]
    sf = buf[idx + IDX_SETPOINT]
    lb = buf[idx + IDX_LIGHT_BYTE]
    return {
        "water_temperature": fahrenheit_to_celsius(tf),
        "setpoint":          fahrenheit_to_celsius(sf),
        "pompe_gauche":      bool(pb1 & MASK_POMPE_GAUCHE),
        "pompe_droite":      bool(pb1 & MASK_POMPE_DROITE),
        # 2026-05-16 FIX: restaure pb2 & MASK_FILTRATION (byte14 bit0x01)
        "filtration":        bool(pb2 & MASK_FILTRATION),
        "chauffage":         bool(pb2 & MASK_CHAUFFAGE),
        "bulleur":           bool(pb2 & MASK_BULLEUR),
        "lumiere":           bool(lb & MASK_LUMIERE),
        "raw_pb1": pb1, "raw_pb2": pb2, "raw_lb": lb,
    }


# ============================================================
# ENVOI COMMANDES
# ============================================================
async def send_command(
    host: str,
    port: int,
    command: str,
    consigne_f: int | None = None,
    repeat: int = REPEAT_COUNT,
    interval: float = REPEAT_INTERVAL,
) -> bool:
    """Envoie une commande RS485 au W610 (avec repetition pour fiabilite).

    Pour CMD_CONSIGNE, fournir consigne_f en Fahrenheit (60..104).
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
        _LOGGER.debug("Commande %s envoyee (%d repetitions, %d bytes)", command, repeat, len(frame))
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
