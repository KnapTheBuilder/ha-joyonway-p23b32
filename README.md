# ha-joyonway-p23b32

Home Assistant custom integration for the **Joyonway P23B32** spa controller via RS485 over a **USR-W610** WiFi bridge.

Developed and tested by [@KnapTheBuilder](https://github.com/KnapTheBuilder), with contributions from [@KDy](https://community.home-assistant.io/u/kdy) and [@Gaet78](https://community.home-assistant.io/u/gaet78).

Discussion thread: [JoyOnWay Spa Control — HA Community](https://community.home-assistant.io/t/joyonway-spa-control/582344)

---

## Requirements

| Item | Details |
|---|---|
| Spa controller | Joyonway P23B32 (physically validated) |
| RS485 bridge | USR-W610 (WiFi, TCP Server mode, port 8899) |
| Home Assistant | 2024.1.0 or later |
| Python | 3.12+ (Python 3.14 asyncio fix included) |

---

## Hardware wiring

> **Warning: Opening the spa electrical enclosure is done at your own risk. Always cut the power before any intervention.**

The USR-W610 connects to the RS485 bus inside the spa controller box:

```
Spa P23B32 RS485 bus  <-->  USR-W610 terminals A / B
```

Configure the USR-W610 in **TCP Server** mode, port **8899**, baud rate **9600**, 8N1.

---

## Installation

### Via HACS (recommended)

1. In HACS, go to **Integrations** and click the three dots in the top right.
2. Select **Custom repositories**.
3. Add `https://github.com/KnapTheBuilder/ha-joyonway-p23b32` with category **Integration**.
4. Install **Joyonway P23B32 Spa**.
5. Restart Home Assistant.

### Manual

Copy the `custom_components/joyonway_p23b32` folder into your HA `config/custom_components/` directory and restart.

---

## Configuration

After restart, go to **Settings > Devices & Services > Add integration** and search for **Joyonway**.

Enter:
- **IP address**: IP of your USR-W610 on your local network
- **TCP port**: `8899` (default)

---

## Entities created

### Sensors

| Entity | Description | Unit |
|---|---|---|
| `sensor.joyonway_p23b32_water_temperature` | Current water temperature | °C |
| `sensor.joyonway_p23b32_setpoint` | Target temperature setpoint | °C |

### Binary sensors

| Entity | Description |
|---|---|
| `binary_sensor.joyonway_p23b32_filtration` | Filtration pump active |
| `binary_sensor.joyonway_p23b32_pompe_gauche` | Left jets pump |
| `binary_sensor.joyonway_p23b32_pompe_droite` | Right jets pump |
| `binary_sensor.joyonway_p23b32_bulleur` | Blower (air bubbles) |
| `binary_sensor.joyonway_p23b32_lumiere` | Light |
| `binary_sensor.joyonway_p23b32_chauffage` | Heater active |
| `binary_sensor.joyonway_p23b32_w610_connection` | USR-W610 connectivity |

### Buttons (one-shot commands)

| Entity | Action |
|---|---|
| Light ON / Light OFF | Toggle light |
| Left jets ON / OFF | Toggle left pump |
| Right jets ON / OFF | Toggle right pump |
| Blower ON / OFF | Toggle blower |
| Filtration | Start filtration cycle |
| All OFF | Emergency stop (all equipment) |

---

## Protocol details

The integration communicates directly over TCP with the USR-W610, which bridges to the spa's RS485 bus.

**Broadcast frame** (emitted by the spa controller every ~30s):

| Byte (from signature) | Content |
|---|---|
| 9 | Water temperature in °F |
| 12 | Pump byte 1: bit 0x04=left jets, bit 0x10=right jets |
| 14 | Pump byte 2: bit 0x01=filtration, bit 0x08=blower, bit 0x10=heater |
| 16 | Setpoint in °F |
| 17 | Light byte: bit 0x01=light |

Frame signature: `1A FF 01 3C D2 B4 FF 08 02`

**Ozonator byte**: not yet identified. If you have a P23B32 with ozonator and can capture RS485 frames, please open an issue.

---

## Known limitations

- Ozonator / UV sanitizer state: not decoded (help welcome)
- Filter schedule status: differs between manual and scheduled runs (bytes 34-36, under investigation)
- Tested only on P23B32 controller. Other Joyonway models may require protocol adaptation.

---

## License

MIT
