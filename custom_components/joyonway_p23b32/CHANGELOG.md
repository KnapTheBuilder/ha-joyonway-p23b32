# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-05-24

### Added
- **CRC-32 module (`crc.py`)** implementing the algorithm reverse-engineered
  by @alexbde (poly `0x04C11DB7`, XorOut `0x552D22C8`, with 32-bit word
  byte-swap pre-processing). Cross-validated on P23B32 V2 + P20B29 captures
  (9 of 11 command frames rebuild byte-identical, light frames pending).
- **Unescape module (`unescape.py`)** factoring out the pseudo-escape table
  discovered by @KDy, including a reverse `escape()` helper used when
  building outbound frames.
- **Climate platform** : native HA thermostat entity with full setpoint
  control. Setpoints generated dynamically from the CRC algorithm - no
  per-temperature capture required. Range 15.5 C - 40 C, 0.5 C step.
- **Switch platform** : 4 bidirectional switches (light, left pump, right
  pump, blower) that mirror the broadcast state and send the right RS-485
  frame on toggle. Available property tied to bridge connectivity.
- New command identifier `filtration_off` (currently re-uses the
  `filtration` frame ; will get its own captured frame in a later release).
- Dynamic `build_setpoint_frame(temp_c)` API in `rs485.py`, replacing the
  fixed `build_consigne_frame(temp_f)` (the latter is kept as a compat
  shim).

### Changed
- `send_command()` now accepts `consigne_c` (Celsius) instead of the
  legacy `consigne_f` (Fahrenheit). The function signature is more
  consistent with the rest of HA, which works in the configured unit.
- README rewritten and expanded with credits section, hardware notes, and
  installation steps for HACS / manual setups.
- `manifest.json` keys now in canonical alphabetical order (after the
  required `domain` and `name`) for hassfest compliance.
- `hacs.json` cleaned up : no more invalid keys.

### Fixed
- `MASK_CHAUFFAGE` restored to `0x10` and `filtration` decoding restored to
  `pb2 & MASK_FILTRATION` (regression fix already shipped as 0.2.x, now
  documented).

## [0.1.0] - 2026-05-11

Initial private release :
- Sensor / binary sensor platforms
- Button platform for one-shot commands
- Replay-based RS-485 command frames
- USR-W610 broadcast polling
- Config flow with IP/port

[0.3.0]: https://github.com/KnapTheBuilder/ha-joyonway-p23b32/releases/tag/v0.3.0
[0.1.0]: https://github.com/KnapTheBuilder/ha-joyonway-p23b32/releases/tag/v0.1.0
