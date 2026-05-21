"""
# 2026-05-21 | Module | Joyonway pseudo-escape decoder (KDy table) | Depend: rien
Implementation correcte du pseudo-escape pour la famille 1A/1D Joyonway.

Table d'unescape selon KDy (post #90 du forum HA community) :
    0x1B 0x11  ->  0x1A
    0x1B 0x13  ->  0x1C
    0x1B 0x14  ->  0x1D
    0x1B 0x15  ->  0x1E
    0x1B 0x0B  ->  0x1B

Toute autre sequence 0x1B XX n'est PAS transformee (laissee telle quelle).

S'applique aux controleurs :
- Joyonway P23B32 V2 (2019)
- Joyonway P20B29-2032 V183
- Joyonway P25B85

NE S'APPLIQUE PAS au P69B133 (protocole 0x7E/CRC-8 different).

Source : https://community.home-assistant.io/t/joyonway-spa-control/582344/90

Auteur : Christophe Knap (KnapTheBuilder)
Licence : MIT
"""

from __future__ import annotations

# Table KDy (post #90)
ESCAPE_TABLE = {
    0x11: 0x1A,
    0x13: 0x1C,
    0x14: 0x1D,
    0x15: 0x1E,
    0x0B: 0x1B,
}

# Inverse pour escape (construction de trames a envoyer)
ESCAPE_TABLE_REVERSE = {v: k for k, v in ESCAPE_TABLE.items()}

ESCAPE_MARKER = 0x1B
FRAME_START = 0x1A
FRAME_END = 0x1D


def unescape_frame(frame: bytes | bytearray) -> bytes:
    """
    Applique la table d'unescape KDy a une trame brute.

    Args:
        frame: trame brute incluant les delimiteurs

    Returns:
        bytes: trame avec sequences 0x1B XX resolues

    Examples:
        >>> unescape_frame(bytes.fromhex("1a1b110c1d"))
        b'\\x1a\\x1a\\x0c\\x1d'
        >>> unescape_frame(bytes.fromhex("1a1b14091d"))
        b'\\x1a\\x1d\\t\\x1d'
    """
    if not frame:
        return b""

    result = bytearray()
    i = 0
    n = len(frame)
    while i < n:
        if frame[i] == ESCAPE_MARKER and i + 1 < n:
            next_byte = frame[i + 1]
            if next_byte in ESCAPE_TABLE:
                result.append(ESCAPE_TABLE[next_byte])
                i += 2
                continue
        result.append(frame[i])
        i += 1
    return bytes(result)


def escape_payload(payload: bytes | bytearray) -> bytes:
    """
    Applique l'inverse de la table KDy pour construire une trame a envoyer.

    Args:
        payload: payload SANS delimiteurs externes

    Returns:
        bytes: payload avec 0x1B XX prepended pour chaque byte critique
    """
    if not payload:
        return b""

    result = bytearray()
    for byte in payload:
        if byte in ESCAPE_TABLE_REVERSE:
            result.append(ESCAPE_MARKER)
            result.append(ESCAPE_TABLE_REVERSE[byte])
        else:
            result.append(byte)
    return bytes(result)


def extract_frames(raw_data: bytes) -> list[bytes]:
    """
    Extrait toutes les trames delimitees 0x1A...0x1D d'un blob brut.
    NE FAIT PAS l'unescape (a appliquer separement).

    Args:
        raw_data: contenu binaire brut (capture nc)

    Returns:
        Liste de trames brutes (avec delimiteurs)
    """
    frames = []
    i = 0
    n = len(raw_data)
    while i < n:
        if raw_data[i] == FRAME_START:
            j = i + 1
            while j < n:
                if raw_data[j] == FRAME_END:
                    frames.append(raw_data[i:j + 1])
                    i = j + 1
                    break
                j += 1
            else:
                break
        else:
            i += 1
    return frames


def decode_b4_broadcast(unescaped_frame: bytes) -> dict | None:
    """
    Decode un broadcast B4 selon la logique du parser KDy (post #90).

    Args:
        unescaped_frame: trame deja passee par unescape_frame()

    Returns:
        dict avec champs decodes, ou None si trame trop courte
    """
    if len(unescaped_frame) < 30:
        return None

    temp_f = unescaped_frame[9]
    setpoint_f = unescaped_frame[16]
    pump_flags = unescaped_frame[12]
    heating_byte = unescaped_frame[14]
    light_flags = unescaped_frame[17]

    heating_state_map = {
        0x50: "circulation",
        0x54: "heating",
        0x40: "cooldown",
        0xC1: "ozonator_active",
    }
    heating_state = heating_state_map.get(heating_byte, "off_or_manual_disabled")

    return {
        "water_temp_fahrenheit": temp_f,
        "water_temp_celsius": round((temp_f - 32) * 5 / 9, 1),
        "setpoint_fahrenheit": setpoint_f,
        "setpoint_celsius": round((setpoint_f - 32) * 5 / 9, 1),
        "filtering": bool(pump_flags & 0x02),
        "massage": bool(pump_flags & 0x04),
        "light": bool(light_flags & 0x01),
        "heating_state": heating_state,
        "heating_byte_raw": f"0x{heating_byte:02X}",
    }


def build_setpoint_frame(target_celsius: float) -> bytes:
    """
    Construit une trame de commande consigne thermostat.

    BASE : trame validee par Yannickt26 (post #110).
    byte 15 = setpoint en Fahrenheit = round((C * 9/5) + 32)

    AVERTISSEMENT IMPORTANT :
    Le CRC aux positions 17-20 doit etre captura pour chaque valeur de consigne
    sur ton propre spa, OU recalcul (mais l'algorithme de CRC n'est PAS encore
    deduit avec certitude). En attendant, cette fonction sort la trame template
    avec un CRC placeholder a remplacer par le CRC reel observe.

    Args:
        target_celsius: temperature cible en Celsius (15.5 a 40)

    Returns:
        bytes : trame avec byte 15 setpoint correct mais CRC a verifier
    """
    if not 15.5 <= target_celsius <= 40:
        raise ValueError(f"Setpoint hors plage 15.5-40C : {target_celsius}")

    setpoint_f = round((target_celsius * 9 / 5) + 32)

    # Trame template basee sur Yannickt26 SETPOINT_38C (post #110)
    # byte 15 = setpoint_f, bytes 17-20 = CRC (a remplacer par CRC capture)
    frame = bytearray.fromhex("1a0130103ca100a10000808002040000009620000000001d")
    frame[15] = setpoint_f

    return bytes(frame)


# Tests integres
def _run_tests() -> None:
    """Tests integres pour valider l'implementation."""
    print("=== Tests unescape KDy ===")

    # Test 1 : 1B 11 -> 1A
    result = unescape_frame(bytes.fromhex("1b11"))
    assert result == bytes([0x1A]), f"Test 1: {result.hex()}"
    print(f"Test 1 OK : 1B 11 -> 1A ({result.hex()})")

    # Test 2 : 1B 13 -> 1C
    result = unescape_frame(bytes.fromhex("1b13"))
    assert result == bytes([0x1C]), f"Test 2: {result.hex()}"
    print(f"Test 2 OK : 1B 13 -> 1C ({result.hex()})")

    # Test 3 : 1B 14 -> 1D
    result = unescape_frame(bytes.fromhex("1b14"))
    assert result == bytes([0x1D]), f"Test 3: {result.hex()}"
    print(f"Test 3 OK : 1B 14 -> 1D ({result.hex()})")

    # Test 4 : 1B 15 -> 1E
    result = unescape_frame(bytes.fromhex("1b15"))
    assert result == bytes([0x1E]), f"Test 4: {result.hex()}"
    print(f"Test 4 OK : 1B 15 -> 1E ({result.hex()})")

    # Test 5 : 1B 0B -> 1B
    result = unescape_frame(bytes.fromhex("1b0b"))
    assert result == bytes([0x1B]), f"Test 5: {result.hex()}"
    print(f"Test 5 OK : 1B 0B -> 1B ({result.hex()})")

    # Test 6 : 1B XX non documente reste tel quel
    result = unescape_frame(bytes.fromhex("1bff"))
    assert result == bytes([0x1B, 0xFF]), f"Test 6: {result.hex()}"
    print(f"Test 6 OK : 1B FF non transforme ({result.hex()})")

    # Test 7 : trame reelle Yannickt26 post #109
    raw = bytes.fromhex(
        "1aff013cd2b4ff08015d04d4006f2000630002491b1511000c1b171b15000c"
        "1b171b150c1b171b1500fe4f00000000000000000000001b110514141b111f"
        "0300df4e83aa1d"
    )
    unescaped = unescape_frame(raw)
    assert unescaped[5] == 0xB4, f"Test 7: type byte = {unescaped[5]:02X}"
    decoded = decode_b4_broadcast(unescaped)
    assert decoded is not None, "Test 7: decode failed"
    print(f"Test 7 OK : B4 reel Yannickt26 decode :")
    print(f"   Temp eau     : {decoded['water_temp_celsius']}C ({decoded['water_temp_fahrenheit']}F)")
    print(f"   Consigne     : {decoded['setpoint_celsius']}C ({decoded['setpoint_fahrenheit']}F)")
    print(f"   Heating state: {decoded['heating_state']}")
    print(f"   Light        : {decoded['light']}")

    # Test 8 : build setpoint frame
    frame38 = build_setpoint_frame(38)
    assert frame38[15] == 0x64, f"Test 8 SP38: byte 15 = {frame38[15]:02X}"
    print(f"Test 8 OK : setpoint 38C -> byte 15 = 0x{frame38[15]:02X}")

    frame10 = build_setpoint_frame(10) if 10 >= 15.5 else None
    # 10 hors plage, attendu exception
    try:
        build_setpoint_frame(10)
        assert False, "Test 9 should have raised"
    except ValueError:
        print("Test 9 OK : setpoint hors plage refuse (10C < 15.5C)")

    print("=== Tous les tests passent ===")


if __name__ == "__main__":
    _run_tests()
