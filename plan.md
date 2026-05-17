# Joyonway Spa Integration Plan — Unified P25B85 / P23B32

> **Goal:** A single Home Assistant integration supporting multiple Joyonway
> controller models via model adapters, starting with read-only P25B85 support.
>
> **Fork base:** `KnapTheBuilder/ha-joyonway-p23b32`
> **Primary test hardware:** P25B85 + PB554 + Elfin EW11

---

## 1. Hardware (your spa)

- **Spa:** Home Deluxe White Marble (outdoor whirlpool, rigid/hardshell)
- **Controller:** Joyonway P25B85, PCB `P2325B0003 R05`
- **Touchpad:** PB554 color screen
- **Bridge:** Elfin EW11, RS-485 → WiFi, TCP server `192.168.188.58:8899`
- **UART:** 38400 8N1 (confirmed by KDy via logic analyzer, 26µs bit time)
- **Pump:** ONE dual-speed pump (short-press cycles: low → high → off)
  - Low speed = filtration / circulation
  - High speed = massage jets (20-min auto-off)
- **Light:** RGB LED, 9 states cycling via button press (R→G→Y→B→V→C→W→Off)
- **Heater:** 2kW resistive, thermostat-controlled (no direct ON/OFF command)
- **UV lamp:** connected in place of ozonator (same connector on controller)
- **Blower:** connector exists on P25B85 but NOT wired on this spa

### Compatible controllers (same protocol family, same baud rate)

All require PB553/PB554/PB555 color touchpad:

| Model  | Equipment                                     | Tested by                           |
|--------|-----------------------------------------------|-------------------------------------|
| P25B85 | 1 dual-speed pump, light, heater, UV/ozone    | KDy, you (alex)                     |
| P23B32 | 2 jet pumps, blower, circ pump, light, heater | christopheknap                      |
| P20B29 | Similar to P23B32                             | Yannickt26                          |
| P25B37 | Unknown equipment layout                      | c0mpleX (9600 captures, wrong baud) |

---

## 2. Protocol (from KDy + christopheknap community findings)

### Framing

- **Baud rate:** 38400 8N1
- **Start delimiter:** `0x1A`
- **End delimiter:** `0x1D`

### Pseudo-escaping (within frame payload)

Documented by KDy (post #90). Required for P25B85, scope varies by model.

| Raw byte | Escaped to  |
|----------|-------------|
| `0x1A`   | `0x1B 0x11` |
| `0x1B`   | `0x1B 0x0B` |
| `0x1C`   | `0x1B 0x13` |
| `0x1D`   | `0x1B 0x14` |
| `0x1E`   | `0x1B 0x15` |

**Model difference (christopheknap post #98):** On the P23B32, only the tail
of the broadcast frame (bytes 55+, datetime zone) is pseudo-escaped. Applying
unescape to the whole frame breaks byte indexing. On P25B85, KDy applies
unescape to the full frame successfully. Keep unescape scope per-model.

### Frame structure (after unescaping)

```
byte[0]  = 0x1A (start)
byte[1]  = destination address
byte[2]  = source address
byte[3]  = length (payload bytes, excluding last 4 bytes)
byte[4..N] = payload
byte[N+1..N+4] = CRC/checksum (4 bytes, algorithm unknown)
byte[last] = 0x1D (end)
```

### Bus cycle (~50ms per frame, 12 frames per cycle)

Master (0x01) polls in order:
1. `0x10`, `0x11`, `0x12`, `0x13` — no response (unused slave slots)
2. `0x50` — no response
3. `0x40` — no response
4. `0x21`, `0x22`, `0x23` — no response (unused panel slots)
5. `0x30` — no response (WiFi module slot — we impersonate this for writes)
6. `0x20` — **panel** (master sends query, panel responds)
7. `0xFF` — **broadcast** (status frame, ~66 bytes unescaped) ← main data source

### Broadcast frame (0xFF) — P25B85 byte map

Reference frame from KDy (post #74), 0-indexed from `0x1A`:

```
1A FF 01 3C D2 B4 FF 08 03 5E 04 06 04 F5 40 00 68 01 00 12 21 12 3B 14 00 16 00 04 00 43 00 04
3B 12 00 14 00 00 00 06 4D 00 00 00 00 00 00 00 00 00 00 00 00 10 05 08 13 1B 11 12 00 00 4E 28 33
11 1D
```

| Byte      | Content                    | Notes (KDy P25B85)                                                             |
|-----------|----------------------------|--------------------------------------------------------------------------------|
| 0         | `0x1A`                     | Start                                                                          |
| 1         | `0xFF`                     | Broadcast address                                                              |
| 2         | `0x01`                     | Master address                                                                 |
| 3         | `0x3C`                     | Length                                                                         |
| 4–8       | `D2 B4 FF 08 03`           | Header (byte 8 = `0x03` for P25B85, `0x02` for P23B32)                         |
| **9**     | **Water temperature (°F)** | `0x5E` = 94°F = 34.4°C                                                         |
| 10–11     | `0x04 0x06`                | Unknown                                                                        |
| 12        | Unknown                    | P23B32 uses this for jets, but P25B85 meaning differs                          |
| **13**    | **Pump status**            | `0x02` = filtration (pump low), `0x04` = massage (pump high)                   |
| 14        | Heater area                | `0x40` idle, `0xF5` in KDy's sample                                            |
| **15**    | **Heating state**          | `0x00`=off, `0x50`=circ-only, `0x54`=heating, `0x40`=cooldown, `0xC1`=UV/ozone |
| **16**    | **Setpoint (°F)**          | `0x68` = 104°F = 40°C                                                          |
| 17        | Flags                      |                                                                                |
| **18**    | **Light / shared flags**   | bit 0 (`0x01`) = light ON; `0x80` = set during UV/heating states               |
| 19–27     | Various                    | Schedule/config data                                                           |
| **28**    | **Equipment flags**        | Mirrors byte 13 for pump (needs validation)                                    |
| **29**    | **UV/Ozone flag**          | `0x20` when UV/ozone active                                                    |
| 30–52     | Various                    |                                                                                |
| **53–58** | **Date/Time**              | year, month, day, hour, minute, second (may need unescape)                     |
| 59–end    | CRC (4 bytes) + `0x1D`     |                                                                                |

### P25B85 status combinations (KDy post #74)

| State                      | byte[13] | byte[15] | byte[18] | byte[29] |
|----------------------------|----------|----------|----------|----------|
| All off                    | `0x00`*  | `0x00`   | `0x00`   | `0x00`   |
| Light only                 | —        | —        | `0x01`   | —        |
| Filtration (pump low)      | `0x02`   | —        | —        | —        |
| Massage (pump high)        | `0x04`   | —        | —        | —        |
| UV/ozone only              | —        | `0xC1`   | `0x80`   | `0x20`   |
| UV/ozone + light           | —        | `0xC1`   | `0x81`   | `0x20`   |
| Heating stage 1 (circ)     | —        | `0x50`   | `0x80`   | `0x20`   |
| Heating stage 2 (active)   | —        | `0x54`   | `0x80`   | `0x20`   |
| Heating stage 3 (cooldown) | —        | `0x40`   | `0x80`   | `0x20`   |

*KDy did not state byte[13] for "all off" explicitly; assumed `0x00` from context.

### P23B32 differences (christopheknap posts #89, #92, #94)

| Field           | P25B85           | P23B32                                              |
|-----------------|------------------|-----------------------------------------------------|
| Header byte 8   | `0x03`           | `0x02`                                              |
| Pump low/filter | byte 13 & `0x02` | byte 17 bit `0x80`                                  |
| Left jets       | —                | byte 12 & `0x04`                                    |
| Right jets      | —                | byte 12 & `0x10`                                    |
| Blower          | —                | byte 14 & `0x08`                                    |
| Heater active   | byte 15 = `0x54` | byte 14 & `0x10` (confirmed with smart plug)        |
| Light           | byte 18 & `0x01` | byte 17 & `0x01`                                    |
| Filtration      | byte 13 & `0x02` | byte 14 & `0x01` (wrong! actually byte 17 & `0x80`) |
| Unescape scope  | full frame       | tail only (bytes 55+)                               |

### CRC safety (CRITICAL — KDy post #97)

> "A temperature change frame without a valid CRC turned on my heater, which
> could cost someone money" — KDy

**Hard rules for P25B85:**
- ❌ NEVER send frames with forged/random CRC
- ❌ NEVER modify a single byte of a captured frame (CRC will no longer match)
- ❌ NEVER construct synthetic command payloads
- ✅ ONLY replay frames captured verbatim from the physical panel
- ✅ Each captured frame must be validated against an observed state change

---

## 3. Integration Architecture

### Single integration, multi-model adapters

The integration lives in `custom_components/joyonway_p25b85/` (primary model).
A model adapter interface separates shared protocol machinery from per-model
byte semantics.

### Shared core (reuse from P23B32 fork)

- TCP client and reconnect strategy
- Frame boundary reconstruction (`0x1A ... 0x1D`) from TCP stream chunks
- Pseudo-unescape utility
- Coordinator update flow, entity dispatch, error handling
- Config flow (IP, port, model selection)

### Model adapter interface

```python
class ModelAdapter:
    """Per-model byte mapping and feature support."""
    model: str                          # e.g. "P25B85"
    broadcast_signature: bytes          # header to match
    unescape_full_frame: bool           # True for P25B85, False for P23B32

    def parse_status(self, frame: bytes) -> dict:
        """Extract state dict from unescaped broadcast frame."""

    def supported_entities(self) -> list[str]:
        """List of entity keys this model exposes."""
```

### P25B85 adapter (primary, read-only first)

Entities to expose:
- `sensor.water_temperature` — byte 9, °F → °C
- `sensor.setpoint` — byte 16, °F → °C
- `binary_sensor.pump_low` — byte 13 & `0x02` (filtration/circulation)
- `binary_sensor.pump_high` — byte 13 & `0x04` (massage/jets)
- `binary_sensor.light` — byte 18 & `0x01`
- `binary_sensor.heater` — byte 15 in (`0x50`, `0x54`, `0x40`)
- `binary_sensor.heater_active` — byte 15 == `0x54` (element actually drawing power)
- `binary_sensor.uv_lamp` — byte 15 == `0xC1` or byte 29 & `0x20`
- `binary_sensor.bridge_connection` — TCP connectivity
- `sensor.spa_datetime` — bytes 53–58 (optional, low priority)

### P23B32 adapter (preserve existing behavior)

Keep the existing P23B32 byte map as a second adapter. This ensures anyone
using the P23B32 fork can migrate without breakage.

### Bridge naming

All user-facing text says "RS485 bridge" instead of "W610" or "EW11" (bridge-agnostic).

---

## 4. Captures Needed (at the spa)

No usable captures exist. Before implementing anything beyond the capture
tool, you need to capture frames using `tools/guided_capture_38400.py`.

### Capture sequence

For each scenario, enforce: `baseline_before` → `action_active` → `baseline_after`.

| # | Action                                          | Expected byte change (from KDy)    |
|---|-------------------------------------------------|------------------------------------|
| 0 | Initial baseline (everything off)               | Reference frame                    |
| 1 | Light ON (press button, any color)              | byte 18 → `0x01`                   |
| 2 | Pump LOW (press pump button once)               | byte 13 → `0x02`                   |
| 3 | Pump HIGH (press pump button again)             | byte 13 → `0x04`                   |
| 4 | Heater active (raise setpoint above water temp) | byte 15 → `0x50` then `0x54`       |
| 5 | UV lamp (if accessible from panel)              | byte 15 → `0xC1`, byte 29 → `0x20` |
| 6 | Setpoint change (try 2–3 different °F values)   | byte 16 changes                    |

### What to validate from captures

- [ ] Confirm byte 8 = `0x03` in your broadcast header
- [ ] Confirm byte 9 = water temp °F (convert and check against panel display)
- [ ] Confirm byte 13 behavior for pump low vs pump high
- [ ] Confirm byte 15 heating stages (0x50 → 0x54 → 0x40)
- [ ] Confirm byte 16 = setpoint °F
- [ ] Confirm byte 18 bit 0 = light
- [ ] Check if pseudo-unescaping the full frame is needed or breaks indexing
- [ ] Identify any bytes that differ from KDy's mapping

---

## 5. Implementation Plan

### Phase 1: Capture tool

- [ ] Implement `tools/guided_capture_38400.py`
  - CLI with `--host`, `--port`, `--duration`, `--actions`, `--out-dir`, `--dry-run`
  - Guided prompts: baseline → action → baseline for each scenario
  - Saves raw `.bin` files + `session_manifest.json`
  - Read/capture only, no write capability
  - Python stdlib only (no pip dependencies)
- [ ] Implement `tools/frame_parser_38400.py`
  - Parses `.bin` captures into individual frames
  - Applies pseudo-unescape
  - Displays broadcast frames with annotated byte map
  - Diff mode: compare two captures side-by-side
- [ ] Add `tools/README.md` with quick-start examples
- [ ] Dry-run validation

### Phase 2: Code refactoring (adapter architecture)

- [ ] Rename integration folder to `joyonway_p25b85` with updated domain
- [ ] Extract shared frame parser from `rs485.py` into `protocol.py`
  - `find_frames(stream: bytes) -> list[bytes]`
  - `pseudo_unescape(data: bytes) -> bytes`
  - `validate_frame(frame: bytes) -> bool`
- [ ] Create `adapters/` package with `base.py`, `p25b85.py`, `p23b32.py`
- [ ] Update `coordinator.py` to use adapter interface
- [ ] Update `config_flow.py` to add model selection (default P25B85)
- [ ] Update entity files to use adapter's `supported_entities()`
- [ ] Update `manifest.json`, `const.py`, `strings.json`, translations
- [ ] Make device info dynamic (model name from adapter)

### Phase 3: Read-only P25B85 integration

- [ ] Implement P25B85 adapter `parse_status()` using KDy's byte map
- [ ] Validate byte mappings against your captures (update if they differ)
- [ ] Wire sensor entities: water_temperature, setpoint
- [ ] Wire binary_sensor entities: pump_low, pump_high, light, heater, uv_lamp, bridge_connection
- [ ] Test with live spa data
- [ ] Add heater state detail sensor (off / circulation / heating / cooldown / UV)

### Phase 4: Write commands (only after captures + validation)

- [ ] Capture command frames from panel for each action (needs spa visit)
- [ ] Build command replay table: one verified frame per action with known-good CRC
- [ ] Implement flood-inject: 10× at 0.5s intervals
- [ ] Add button entities (light toggle, pump cycle, etc.)
- [ ] Add 30s post-command read suspension (per Gaet78/christopheknap finding)
- [ ] Add write allowlist: only replay captured, CRC-verified frames
- [ ] Add safe-fail: reject writes when no captured frame exists for requested action

### Phase 5: Polish & release

- [ ] Documentation (README with safety section, protocol.md)
- [ ] HACS compatibility validation
- [ ] Auto-detect model from broadcast header byte 8
- [ ] Community testing invitation

---

## 6. Guardrails

- ❌ Don't use 9600 baud — confirmed wrong for PB55x touchpad controllers
- ❌ Don't send commands with forged CRC (P25B85: unsafe, can activate heater)
- ❌ Don't construct synthetic write frames
- ❌ Don't send a write if no captured, CRC-verified replay frame exists
- ❌ Don't bump version until Phase 3 is validated on live hardware
- ⚠️ Always capture command frames from the physical panel, never guess
- ⚠️ 30s read suspension after any write command
- ⚠️ Use bitmask checks (`value & mask`) not strict equality for status flags
- ⚠️ Keep per-model byte maps — positions are NOT universal across controllers

---

## 7. Bridge Settings (Elfin EW11)

- UART: 38400 8N1
- Flow control: RS485 half-duplex
- Protocol mode: transparent/raw (no Modbus wrapper)
- Only ONE TCP client at a time (close phone app before using HA)
- 485 switch time: 3ms default is fine; raise to 10ms if frame corruption observed

### Connectivity test

```bash
python3 -c "
import socket
s = socket.create_connection(('192.168.188.58', 8899), timeout=10)
s.settimeout(5)
d = s.recv(4096)
s.close()
print(f'OK: {len(d)} bytes, first 10: {d[:10].hex(\" \")}')"
```

---

## 8. Community Resources

| Person             | Controller     | Contribution                                                                                                                           |
|--------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **KDy**            | P25B85 + PB554 | Baud rate discovery (logic analyzer), broadcast byte map, pseudo-escape table, CRC safety warning, full MQTT read+write control        |
| **christopheknap** | P23B32 + PB555 | Full HACS integration ([GitHub](https://github.com/KnapTheBuilder/ha-joyonway-p23b32)), command frame captures, cross-model validation |
| **Gaet78**         | P69B133        | Original HACS integration (115200 baud, different protocol), 30s timing discovery                                                      |
| **c0mpleX**        | P25B37         | Frame samples (9600, wrong baud), hex extraction from screenshots                                                                      |
| **Yannickt26**     | P20B29 + WiFi  | Partial ON commands working, confirmed blower OFF frame from P23B32 works                                                              |
| **Neuro**          | P23B32         | ESP32+MAX485 setup, early captures                                                                                                     |

---

## 9. Next Steps (in order)

1. **Implement `tools/guided_capture_38400.py`** — so you can capture at the spa
2. **Implement `tools/frame_parser_38400.py`** — so you can analyze captures
3. **Go to the spa and capture** — follow the sequence in section 4
4. **Analyze captures** — validate KDy's byte map against your hardware
5. **Implement Phase 2** — refactor codebase into adapter architecture
6. **Implement Phase 3** — read-only P25B85 entities
7. **Test on live spa** — validate everything works
