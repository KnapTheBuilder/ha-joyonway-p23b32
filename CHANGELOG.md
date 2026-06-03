# Changelog

## v0.3.0 - 2026-05-27

Major release: dynamic setpoint generation via @alexbde CRC-32 algorithm, native climate platform, and bidirectional switch platform.

### Added

- `crc.py` : CRC-32 @alexbde algorithm (polynomial 0x04C11DB7, init 0x00000000, XorOut 0x552D22C8, MSB-first non-reflected, 32-bit word byte-swap pre-step). Cross-validated 9/11 frames on P23B32 V2 and P20B29-2032 V183.
- `climate.py` : native Home Assistant thermostat platform, range 15.5 to 40 C, step 0.5 C, setpoints generated dynamically by the CRC algorithm (no more static capture table).
- `switch.py` : 4 bidirectional switches (light, left pump, right pump, blower) mirroring the broadcast state, calling rs485.send_command for ON and OFF.
- `MIN_TEMP_C`, `MAX_TEMP_C`, `STEP_TEMP_C` constants in `const.py`.
- New platforms registered: climate and switch.

### Changed

- `rs485.build_consigne_frame()` now delegates to `crc.build_consigne_frame()` using the @alexbde CRC-32 algorithm. The legacy static CRC was incorrect for most temperatures.
- `manifest.json` bumped from 0.1.0 to 0.3.0, keys in canonical alphabetical order for hassfest.
- `hacs.json` cleaned (no invalid keys per HACS spec).
- README expanded with credits, multi-controller support table and v0.3 entity list.

### Known issue

- LIGHT_ON / LIGHT_OFF frames carry a 17-byte payload instead of 16. CRC validation fails on those two frames only. Replay mode still works correctly. Investigation ongoing on the community thread.

### Credits

- @alexbde - CRC-32 reverse engineering on P25B85 (https://github.com/alexbde/ha-joyonway-p25b85)
- @KDy - escape table, broadcast byte map, oscilloscope baudrate, PB555 manual
- @Yannickt26 - P20B29-2032 V183 captures enabling cross-model validation
- @Neuro - ESP32 prototype on P23B32 V2
- @old-man - P25B85 confirmation
- @gaet78 - Joyonway HACS pioneer, P69B133 reference

---

## v0.2.0 - 2026-05-21

Multi-model recognition (P23B32 V2, P20B29-2032 V183, P25B85 share the same 1A/1D protocol family). Correct unescape table integrated.

### Added

- Multi-controller validation (P23B32 V2, P20B29, P25B85)
- KDy pseudo-escape table (post #90 community thread)
- B4 broadcast parser refined
- Bilingual README (EN/FR)
- PB555 "Thermostat manuel" prerequisite documented

### Changed

- Display name "Joyonway P23B32 Spa (RS485 via USR-W610)"

---

## v0.1.1 - 2026-05-13

HACS validation fixes.

### Fixed

- `manifest.json` keys sorted alphabetically for hassfest
- `hacs.json` cleaned
- Brand assets added

---

## v0.1.0 - 2026-05-11

Initial release. P23B32 V2 only. Sensor, binary_sensor, button platforms.
