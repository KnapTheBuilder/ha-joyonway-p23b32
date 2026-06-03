# Changelog

## v0.2.0 - 2026-05-21

Major release: multi-model support based on community findings.

### Added

- **Multi-controller support**: P23B32 V2, P20B29-2032 V183, P25B85 (same 1A/1D protocol family)
- **Sensor platform**: water temperature, setpoint, heating state (in Celsius natively)
- **Correct unescape implementation** based on @KDy table (post #90):
  - `1B 11 -> 1A`, `1B 13 -> 1C`, `1B 14 -> 1D`, `1B 15 -> 1E`, `1B 0B -> 1B`
- **B4 broadcast parser** based on @KDy code
- **Setpoint command frame templates** from @Yannickt26 (post #110)
- Bilingual README (EN/FR) with PB555 manual prerequisites
- 9 validated buttons (light, pumps, blower, filtration)

### Changed

- Renamed display name to "Joyonway Spa" (multi-model)
- `manifest.json` bumped to 0.2.0
- `hacs.json` cleaned (removed invalid `render_readme` key)

### Fixed

- Unescape function was previously implemented incorrectly (simple "remove 0x1B"). Now uses the correct KDy table.

### Credits

- **@KDy** for the unescape table, B4 parser, PB555 manual research
- **@Yannickt26** for P20B29 captures and setpoint frames
- **@gaet78** for the original Joyonway HACS integration (P69B133 reference)
- **@Neuro** for the ESP32+MAX485 prototype work
- **@old-man** for P25B85 confirmation

Source: https://community.home-assistant.io/t/joyonway-spa-control/582344

### Known limitations

- Climate platform (setpoint write) NOT YET included - planned for v0.3
- CRC for setpoint command not yet algorithmically computed (capture-based replay only for now)
- Binary sensors (filtering, light, heater) not yet exposed - parser available, plateforme to be added in v0.3

## v0.1.1 - 2026-05-20

- HACS validation fixes
- Initial private release with 10 buttons

## v0.1.0 - 2026-05-14

- Initial private release on P23B32 V2 only
- 10 command buttons validated by replay
