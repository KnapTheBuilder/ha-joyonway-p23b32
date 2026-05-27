# Joyonway P23B32 Spa - Home Assistant Integration v0.3

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1.0%2B-41BDF5.svg)](https://www.home-assistant.io)

Native local integration for Joyonway spa controllers (1A/1D protocol family) via RS485 over a USR-W610 WiFi bridge.

Integration native Home Assistant pour controleurs de spa Joyonway, communication locale RS485 via pont WiFi USR-W610.

---

## English

### Supported controllers

| Model                          | Status     | Validated by              |
|--------------------------------|------------|---------------------------|
| Joyonway P23B32 V2 (2019)      | Validated  | @KnapTheBuilder           |
| Joyonway P20B29-2032 V183      | Validated  | @Yannickt26               |
| Joyonway P25B85                | Validated  | @KDy, @old-man, @alexbde  |

All three share the SAME RS485 protocol (0x1A/0x1D delimiters, 38400 baud, KDy pseudo-escape table, alexbde CRC-32).

For P69B133 (Balboa-like protocol, 0x7E delimiters, 115200 baud, CRC-8), use @gaet78's integration: https://github.com/gaet78/homeassistant-joyonway-hacs-

### Features (v0.3.0)

- **Climate platform**: native HA thermostat, 15.5 to 40 C, step 0.5 C. Setpoints generated dynamically by the @alexbde CRC-32 algorithm.
- **Switch platform**: 4 bidirectional switches (light, left pump, right pump, blower).
- **Button platform**: 10 one-shot RS485 commands.
- **Sensor platform**: water temperature, setpoint (Celsius).
- **Binary sensor platform**: filtration, pumps, blower, light, heater, W610 connectivity.
- **Coordinator**: TCP polling via USR-W610 bridge with correct KDy unescape.
- **Multi-model support**: same integration for P23B32 V2 / P20B29 / P25B85.
- **Config flow**: simple IP + port setup with TCP test.
- **Bilingual UI**: English and French translations.

### Prerequisites

**Hardware**

- USR-W610 RS485-to-WiFi bridge connected to the spa controller
- W610 in **Transparent TCP** mode (NOT Modbus)
- 38400 baud 8N1
- Static DHCP lease recommended for the W610

**Spa panel configuration**

Manual heater control requires: activate **"Thermostat manuel"** in your PB555 panel menu. Without this, no software can pilot the heater.

Source: PB555 manual (French), cited by @KDy on the community thread.

### Installation

**Via HACS (recommended)**

1. HACS > Integrations > 3-dot menu > Custom repositories
2. Add `https://github.com/KnapTheBuilder/ha-joyonway-p23b32` as **Integration**
3. Install "Joyonway P23B32 Spa"
4. Restart Home Assistant
5. Settings > Devices & Services > Add Integration > "Joyonway"
6. Enter your W610 IP (port 8899 default)

**Manual installation**

1. Copy `custom_components/joyonway_p23b32/` to your HA `config/custom_components/`
2. Restart Home Assistant
3. Add integration via UI

### Entities created

| Entity                                        | Type           | Description                                |
|-----------------------------------------------|----------------|--------------------------------------------|
| `climate.joyonway_p23b32_thermostat`          | climate        | Setpoint 15.5 to 40 C, step 0.5 C          |
| `sensor.joyonway_p23b32_temperature_eau`      | sensor         | Water temperature (Celsius)                |
| `sensor.joyonway_p23b32_consigne`             | sensor         | Setpoint (Celsius)                         |
| `binary_sensor.joyonway_p23b32_filtration`    | binary_sensor  | Filtration ON/OFF                          |
| `binary_sensor.joyonway_p23b32_chauffage`     | binary_sensor  | Heater ON/OFF (`heat` device class)        |
| `binary_sensor.joyonway_p23b32_lumiere`       | binary_sensor  | Light ON/OFF                               |
| `binary_sensor.joyonway_p23b32_pompe_gauche`  | binary_sensor  | Left jets pump                             |
| `binary_sensor.joyonway_p23b32_pompe_droite`  | binary_sensor  | Right jets pump                            |
| `binary_sensor.joyonway_p23b32_bulleur`       | binary_sensor  | Blower                                     |
| `binary_sensor.joyonway_p23b32_connexion_w610`| binary_sensor  | W610 TCP connectivity                      |
| `switch.joyonway_p23b32_lumiere`              | switch         | Light bidirectional                        |
| `switch.joyonway_p23b32_pompe_gauche`         | switch         | Left pump bidirectional                    |
| `switch.joyonway_p23b32_pompe_droite`         | switch         | Right pump bidirectional                   |
| `switch.joyonway_p23b32_bulleur`              | switch         | Blower bidirectional                       |
| `button.joyonway_p23b32_filtration`           | button         | Trigger filtration                         |
| `button.joyonway_p23b32_tout_eteindre`        | button         | All OFF emergency stop                     |

### Known limitation

- LIGHT_ON / LIGHT_OFF frames carry a 17-byte payload instead of 16. CRC validation fails on those two frames only. Replay mode still works.

### Credits

- **@alexbde** - CRC-32 reverse engineering on P25B85 (https://github.com/alexbde/ha-joyonway-p25b85)
- **@KDy** - unescape table, B4 parser, PB555 manual
- **@Yannickt26** - P20B29 captures, setpoint frames
- **@gaet78** - Joyonway HACS pioneer, P69B133 reference
- **@Neuro** - ESP32 prototype
- **@old-man** - P25B85 confirmation

Community thread: https://community.home-assistant.io/t/joyonway-spa-control/582344

### License

MIT

---

## Francais

### Controleurs supportes

| Modele                          | Statut    | Valide par                |
|---------------------------------|-----------|---------------------------|
| Joyonway P23B32 V2 (2019)       | Valide    | @KnapTheBuilder           |
| Joyonway P20B29-2032 V183       | Valide    | @Yannickt26               |
| Joyonway P25B85                 | Valide    | @KDy, @old-man, @alexbde  |

Les trois partagent le MEME protocole RS485 (delimiteurs 0x1A/0x1D, 38400 bauds, table pseudo-escape KDy, CRC-32 alexbde).

Pour P69B133 (protocole Balboa-like, delimiteurs 0x7E, 115200 bauds, CRC-8), utiliser l'integration @gaet78 : https://github.com/gaet78/homeassistant-joyonway-hacs-

### Fonctionnalites v0.3.0

- **Plateforme Climate** : thermostat HA natif, 15.5 a 40 C, pas de 0.5 C. Consignes generees dynamiquement par l'algorithme CRC-32 @alexbde (fin de la table statique).
- **Plateforme Switch** : 4 interrupteurs bidirectionnels (lumiere, pompe gauche, pompe droite, bulleur).
- **Plateforme Button** : 10 commandes RS485 one-shot.
- **Plateforme Sensor** : temperature eau, consigne (Celsius).
- **Plateforme Binary Sensor** : filtration, pompes, bulleur, lumiere, chauffage, connectivite W610.
- **Coordinator** : polling TCP via pont USR-W610 avec unescape KDy correct.
- **Multi-modeles** : meme integration pour P23B32 V2 / P20B29 / P25B85.

### Pre-requis

**Materiel**

- Pont RS485-WiFi USR-W610 connecte au controleur du spa
- W610 en mode **TCP Transparent** (PAS Modbus)
- 38400 bauds 8N1
- Bail DHCP statique recommande pour le W610

**Configuration du panneau du spa**

Le controle manuel du chauffage necessite : activer **"Thermostat manuel"** dans le menu du panneau PB555. Sans cela, aucun logiciel ne peut piloter le chauffage.

Source : manuel PB555 (francais), cite par @KDy sur le thread communautaire.

### Installation via HACS

1. HACS > Integrations > menu 3 points > Custom repositories
2. Ajouter `https://github.com/KnapTheBuilder/ha-joyonway-p23b32` comme **Integration**
3. Installer "Joyonway P23B32 Spa"
4. Redemarrer Home Assistant
5. Parametres > Appareils et services > Ajouter une integration > "Joyonway"
6. Renseigner l'IP du W610 (port 8899 par defaut)

### Limitation connue

- Les trames LIGHT_ON / LIGHT_OFF embarquent 17 octets de payload au lieu de 16. La validation CRC echoue uniquement sur ces 2 trames. Le mode replay fonctionne correctement.

### Remerciements

- **@alexbde** - Reverse engineering CRC-32 sur P25B85 (https://github.com/alexbde/ha-joyonway-p25b85)
- **@KDy** - Table d'unescape, parser B4, manuel PB555
- **@Yannickt26** - Captures P20B29, trames consigne
- **@gaet78** - Pionnier HACS Joyonway, reference P69B133
- **@Neuro** - Prototype ESP32
- **@old-man** - Confirmation P25B85

Thread communautaire : https://community.home-assistant.io/t/joyonway-spa-control/582344
