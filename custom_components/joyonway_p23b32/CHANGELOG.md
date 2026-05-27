# Changelog

## v0.3.0 - 2026-05-27

Major release: dynamic setpoint generation via @alexbde CRC-32 algorithm, native climate platform, and bidirectional switch platform.

### Added

- `crc.py` : CRC-32 @alexbde algorithm (polynomial 0x04C11DB7, init 0x00000000, XorOut 0x552D22C8, MSB-first non-reflected, 32-bit word byte-swap pre-step). Cross-validated 9/11 frames on P23B32 V2 and P20B29-2032 V183.
- `climate.py` : native Home Assistant thermostat platform, range 15.5 to 40 C, step 0.5 C, setpoints generated dynamically by the CRC algorithm (no more static capture table).
- `switch.py` : 4 bidirectional switches (light, left pump, right pump, blower) mirroring the broadcast state.
- `build_setpoint_frame(temp_c)` helper in `rs485.py`, replacing the static Fahrenheit capture table.
- `docs/protocol.md` : full RS-485 protocol documentation (frame structure, escape table, CRC algorithm).
- 23 unit tests covering CRC, unescape round-trip and setpoint frame generation.

### Changed

- `send_command()` now accepts `consigne_c` in Celsius. Legacy `consigne_f` kept as compatibility shim.
- `manifest.json` bumped from 0.2.0 to 0.3.0, keys in canonical alphabetical order for hassfest.
- `hacs.json` cleaned (invalid keys removed).
- README expanded with credits, hardware notes and supported controllers table.

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

Major release: multi-model support based on community findings.

### Added

- Multi-controller support: P23B32 V2, P20B29-2032 V183, P25B85 (same 1A/1D protocol family)
- Sensor platform: water temperature, setpoint, heating state (in Celsius natively)
- Correct unescape implementation based on @KDy table (post #90)
  - `1B 11 -> 1A`, `1B 13 -> 1C`, `1B 14 -> 1D`, `1B 15 -> 1E`, `1B 0B -> 1B`
- B4 broadcast parser based on @KDy code
- Setpoint command frame templates from @Yannickt26 (post #110)
- Bilingual README (EN/FR) with PB555 manual prerequisites
- 9 validated buttons (light, pumps, blower, filtration)

### Changed

- Renamed display name to "Joyonway Spa" (multi-model)
- `manifest.json` bumped to 0.2.0
- `hacs.json` cleaned (removed invalid `render_readme` key)

### Fixed

- Unescape function was previously implemented incorrectly (simple "remove 0x1B"). Now uses the correct KDy table.

---

## v0.1.1 - 2026-05-13

HACS validation fixes.

### Fixed

- `manifest.json` keys sorted alphabetically for hassfest
- `hacs.json` validation
- Brand assets added

---

## v0.1.0 - 2026-05-10

Initial release. P23B32 V2 only, basic sensor and button support.
