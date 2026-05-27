# 2026-05-27 | Module | CRC-32 algorithme Joyonway (decouvert par @alexbde) | Depend: aucun (stdlib uniquement)
"""CRC-32 algorithm for Joyonway command frames.

Algorithm discovered and shared by @alexbde
(https://community.home-assistant.io/t/joyonway-spa-control/582344).
Original repo: https://github.com/alexbde/ha-joyonway-p25b85
Cross-validated by @KnapTheBuilder on P23B32 V2 + @Yannickt26 P20B29 captures.

Parameters
----------
- Polynomial : 0x04C11DB7 (Ethernet/zlib standard)
- Init       : 0x00000000
- XorOut     : 0x552D22C8 (Joyonway-specific, non-standard)
- Direction  : MSB-first, non-reflected
- Pre-step   : each 32-bit word of the payload is byte-swapped
  before being fed to the CRC. Characteristic of an ARM Cortex-M MCU
  feeding a hardware CRC peripheral in little-endian word order.

The CRC is stored little-endian on the wire (4 bytes between
the payload and the 0x1D end-of-frame delimiter).

Validation
----------
Tested on 11 frames (9 P23B32 V2 + 2 P20B29) : 9 OK.
Light frames (LIGHT_ON / LIGHT_OFF) currently fail because they
carry a 17-byte payload instead of 16. To be investigated.
"""
from __future__ import annotations

# Polynomial : standard Ethernet CRC-32
_POLY: int = 0x04C11DB7
_XOR_OUT: int = 0x552D22C8


def _make_table() -> list[int]:
    """Build the CRC-32 MSB-first lookup table (256 entries)."""
    table: list[int] = []
    for i in range(256):
        c = i << 24
        for _ in range(8):
            c = ((c << 1) ^ _POLY) if (c & 0x80000000) else (c << 1)
            c &= 0xFFFFFFFF
        table.append(c)
    return table


_TABLE: list[int] = _make_table()


def _crc32_msb(data: bytes, init: int = 0) -> int:
    """Compute non-reflected MSB-first CRC-32 over data."""
    crc = init
    for b in data:
        idx = ((crc >> 24) ^ b) & 0xFF
        crc = ((crc << 8) ^ _TABLE[idx]) & 0xFFFFFFFF
    return crc


def _byte_swap_words(data: bytes) -> bytes:
    """Byte-swap each 32-bit word of data.

    If the input length is not a multiple of 4, it is right-padded with
    zeros to the next multiple of 4 before swapping.
    """
    if len(data) % 4 != 0:
        data = data + b"\x00" * (4 - (len(data) % 4))
    return b"".join(data[i:i + 4][::-1] for i in range(0, len(data), 4))


def crc_joyonway(payload: bytes) -> int:
    """Return the Joyonway CRC-32 value for the given payload.

    Parameters
    ----------
    payload : bytes
        The raw command payload (16 bytes for A1 commands), WITHOUT
        the 0x1A start delimiter and WITHOUT the 0x1D end delimiter.

    Returns
    -------
    int
        32-bit unsigned CRC value. To put it on the wire, call
        ``crc.to_bytes(4, 'little')``.
    """
    swapped = _byte_swap_words(payload)
    raw_crc = _crc32_msb(swapped, init=0)
    return (raw_crc ^ _XOR_OUT) & 0xFFFFFFFF


def crc_bytes_le(payload: bytes) -> bytes:
    """Return the CRC as 4 bytes little-endian, ready to insert in frame."""
    return crc_joyonway(payload).to_bytes(4, "little")


def build_consigne_payload(temp_f: int) -> bytes:
    """Build the 16-byte A1 setpoint command payload for a Fahrenheit temp.

    Layout (reverse-engineered from @Yannickt26 captures, post #110):
    Full frame : 1A <16-byte payload> <CRC LE 4 bytes> 1D
    Payload byte 14 encodes the setpoint in Fahrenheit.

    Cross-validated: setpoint 38C -> byte 0x64 (100F) yields a frame
    byte-identical to Yannickt26's P20B29 V183 capture.
    """
    if not 60 <= temp_f <= 104:
        raise ValueError(f"Consigne hors plage: {temp_f}F (attendu 60-104)")
    return bytes([
        0x01, 0x30, 0x10, 0x3C,    # header
        0xA1, 0x00, 0xA1, 0x00,    # command + target
        0x00, 0x80, 0x80, 0x02,    # flags
        0x04, 0x00, temp_f, 0x00,  # 04 / pad / TEMP_F / pad
    ])


def build_consigne_frame(temp_f: int) -> bytes:
    """Build the complete wire frame for a setpoint command.

    Used by rs485.py to replace the legacy static-CRC implementation.
    Returns 22 bytes : 0x1A + 16-byte payload + 4-byte CRC LE + 0x1D.
    """
    payload = build_consigne_payload(temp_f)
    crc_le = crc_bytes_le(payload)
    return b"\x1A" + payload + crc_le + b"\x1D"
