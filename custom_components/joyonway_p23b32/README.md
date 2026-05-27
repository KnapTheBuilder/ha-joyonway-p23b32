# ha-joyonway-p23b32

Home Assistant custom integration for the Joyonway **P23B32** spa controller
over RS-485, exposed to the network through a USR-W610 (or equivalent)
TCP-to-RS485 bridge.

> Native HA entities for temperature, setpoint, equipment states, equipment
> control, and a full climate (thermostat) platform with dynamically
> generated setpoint frames - no per-temperature capture required.

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
![Version](https://img.shields.io/badge/version-0.3.0-blue)
![HA](https://img.shields.io/badge/Home%20Assistant-2023.6%2B-blue)

## Features

- **Sensors** : water temperature, thermostat setpoint
- **Binary sensors** : left/right pumps, blower, filtration, heater, light, bridge connectivity
- **Switches** : light, left pump, right pump, blower (bidirectional, mirrored from RS-485 broadcast)
- **Buttons** : individual ON/OFF commands plus "All OFF" emergency stop
- **Climate** : full HA thermostat with dynamic setpoint generation (15.5 C - 40 C, 0.5 C step)
- **Config flow** : add the integration through the HA UI ; no YAML required

## Hardware

| Component | Purpose |
| --- | --- |
| Joyonway P23B32 controller | Spa main board (RS-485 master) |
| USR-W610 bridge | RS-485 to TCP (any equivalent works, e.g. Elfin EW11) |
| Home Assistant Green / OS / Container | Any install supporting HACS or custom_components |

The bridge must expose **38400 baud 8N1** on the spa's RS-485 bus and listen
on a TCP socket (default port 8899).

## Installation

### Via HACS (custom repository)

1. HACS - Integrations - Custom repositories
2. Add `https://github.com/KnapTheBuilder/ha-joyonway-p23b32` as **Integration**
3. Install **Joyonway P23B32 Spa**
4. Restart Home Assistant
5. **Settings - Devices & services - Add integration** - search for *Joyonway*

### Manual

```bash
cd /config
git clone https://github.com/KnapTheBuilder/ha-joyonway-p23b32 \
  --branch main /tmp/joyonway
cp -r /tmp/joyonway/custom_components/joyonway_p23b32 custom_components/
```

Restart HA, then add the integration from the UI.

## Configuration

Through the UI only. You'll be asked for :

- **Bridge IP** : the W610 / Elfin / equivalent IP address
- **TCP port** : default `8899`

That's it. The integration probes the bridge before saving and aborts if it
isn't reachable.

## How the protocol works

The Joyonway panel broadcasts a status frame (`0xB4`) on the RS-485 bus
roughly every 500 ms. The integration listens for that frame, decodes a few
key bytes, and exposes them as HA entities.

Outbound commands are RS-485 frames captured from the original touch panel
and re-emitted by the integration. The CRC-32 algorithm has been reverse
engineered (see Credits below), which makes it possible to generate **any**
setpoint mathematically without having to capture every individual
temperature first.

For full protocol details see [`docs/protocol.md`](docs/protocol.md).

## Credits

This integration would not exist without the work of several people on the
[Home Assistant community thread](https://community.home-assistant.io/t/joyonway-spa-control/582344) :

- **@KDy** - pseudo-escape table, broadcast byte map, Python reading script,
  oscilloscope confirmation of the 38400 baud rate
- **@alexbde** - reverse-engineered the CRC-32 algorithm (poly `0x04C11DB7`,
  XorOut `0x552D22C8`, with 32-bit word byte-swap pre-processing)
- **@Yannickt26** - P20B29 setpoint captures that made the cross-model
  CRC validation possible
- **@Neuro**, **@old-man**, **@Gaet78** - additional captures and the related
  P69B133 integration

The CRC algorithm and pseudo-escape table are direct ports of the algorithms
documented in that thread. Variable naming and integration design adapted
for the P23B32 V2 controller.

## License

MIT - see [LICENSE](LICENSE).
