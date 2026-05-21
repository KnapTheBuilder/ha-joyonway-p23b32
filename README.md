# Joyonway Spa Home Assistant Integration v0.2

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Home Assistant integration for Joyonway spa controllers (1A/1D protocol family)**

**Integration Home Assistant pour controleurs de spa Joyonway (famille protocole 1A/1D)**

---

# English

## Supported controllers

| Model | Status | Validated by |
|-------|--------|--------------|
| Joyonway P23B32 V2 (2019) | Validated | @KnapTheBuilder |
| Joyonway P20B29-2032 V183 | Validated | @Yannickt26 |
| Joyonway P25B85 | Validated | @KDy, @old-man |

All three share the SAME RS485 protocol (0x1A/0x1D delimiters, 38400 baud, KDy pseudo-escape table).

For P69B133 (Balboa-like protocol, 0x7E delimiters, 115200 baud), use @gaet78's integration:
https://github.com/gaet78/homeassistant-joyonway-hacs-

## What this integration does

### v0.2.0 features

- **Sensor platform**: water temperature, setpoint, heating state, raw F values
- **Button platform**: 9 validated commands (light, pumps, blower, filtration)
- **Coordinator**: TCP polling via USR-W610 bridge with correct unescape
- **Multi-model support**: same integration for P23B32 V2 / P20B29 / P25B85

### Coming in v0.3

- Climate platform (setpoint write with on-board CRC handling)
- Binary sensors (filtering, light, heater states)
- More command frames (ozonator, etc.)

## Prerequisites

### Hardware
- USR-W610 RS485-to-WiFi bridge connected to the spa controller
- W610 configured in **Transparent TCP mode** (NOT Modbus)
- 38400 baud 8N1

### Spa panel configuration
**Manual heater control requires**: activate "Thermostat manuel" in your PB555 panel menu.
Without this, no software can pilot the heater.

Source: PB555 manual (French), cited by @KDy on the community thread.

## Installation

### Via HACS (recommended)

1. HACS > Integrations > 3-dot menu > Custom repositories
2. Add `https://github.com/KnapTheBuilder/ha-joyonway-p23b32` as Integration
3. Install "Joyonway Spa"
4. Restart Home Assistant
5. Settings > Devices & Services > Add Integration > "Joyonway"
6. Enter your W610 IP (default port 8899)

### Manual installation

1. Copy `custom_components/joyonway_p23b32/` to your HA `config/custom_components/`
2. Restart Home Assistant
3. Add integration via UI

## Entities created

After setup, these entities are available:

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.water_temperature` | sensor | Water temp in Celsius |
| `sensor.setpoint` | sensor | Thermostat setpoint in Celsius |
| `sensor.heating_state` | sensor | off / heating / circulation / cooldown / ozonator_active |
| `button.light_on` | button | Light ON |
| `button.light_off` | button | Light OFF |
| `button.pump_left_on` | button | Left pump ON |
| `button.pump_left_off` | button | Left pump OFF |
| `button.pump_right_on` | button | Right pump ON |
| `button.pump_right_off` | button | Right pump OFF |
| `button.blower_on` | button | Blower ON |
| `button.blower_off` | button | Blower OFF |
| `button.filtration` | button | Filtration |

## Credits

This integration exists thanks to:
- **@KDy** (unescape table, B4 parser, PB555 manual)
- **@Yannickt26** (P20B29 captures, setpoint frames)
- **@gaet78** (Joyonway HACS pioneer, P69B133 reference)
- **@Neuro** (ESP32 prototype)
- **@old-man** (P25B85 confirmation)

Community thread: https://community.home-assistant.io/t/joyonway-spa-control/582344

## License

[MIT](LICENSE)

---

# Francais

## Controleurs supportes

| Modele | Statut | Valide par |
|--------|--------|------------|
| Joyonway P23B32 V2 (2019) | Valide | @KnapTheBuilder |
| Joyonway P20B29-2032 V183 | Valide | @Yannickt26 |
| Joyonway P25B85 | Valide | @KDy, @old-man |

Les trois partagent le MEME protocole RS485 (delimiteurs 0x1A/0x1D, 38400 bauds, table pseudo-escape KDy).

Pour P69B133 (protocole Balboa-like, delimiteurs 0x7E, 115200 bauds), utiliser l'integration @gaet78 :
https://github.com/gaet78/homeassistant-joyonway-hacs-

## Pre-requis

### Materiel
- Pont RS485-WiFi USR-W610 connecte au controleur du spa
- W610 configure en **mode TCP Transparent** (PAS Modbus)
- 38400 bauds 8N1

### Configuration du panneau du spa
**Le controle manuel du chauffage necessite** : activer "Thermostat manuel" dans le menu du panneau PB555.
Sans cela, aucun logiciel ne peut piloter le chauffage.

Source : manuel PB555 (francais), cite par @KDy sur le thread communautaire.

## Installation via HACS

1. HACS > Integrations > menu 3 points > Custom repositories
2. Ajouter `https://github.com/KnapTheBuilder/ha-joyonway-p23b32` comme Integration
3. Installer "Joyonway Spa"
4. Redemarrer Home Assistant
5. Parametres > Appareils et services > Ajouter une integration > "Joyonway"
6. Renseigner l'IP de ton W610 (port 8899 par defaut)

## Remerciements

Cette integration existe grace a :
- **@KDy** (table d'unescape, parser B4, manuel PB555)
- **@Yannickt26** (captures P20B29, trames consigne)
- **@gaet78** (pionnier HACS Joyonway, reference P69B133)
- **@Neuro** (prototype ESP32)
- **@old-man** (confirmation P25B85)

Thread communautaire : https://community.home-assistant.io/t/joyonway-spa-control/582344
