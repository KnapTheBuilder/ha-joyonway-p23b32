# Joyonway Spa Integration Plan — Unified RS485 / PB55x Controllers

> **Goal:** A single Home Assistant integration supporting multiple Joyonway
> RS485/PB55x controller models via model adapters, starting with validated,
> read-only P25B85 support.
>
> **Fork base:** `KnapTheBuilder/ha-joyonway-p23b32`
> **Primary test hardware:** P25B85 + PB554 + Elfin EW11
> **Preferred integration domain:** `joyonway_spa` (neutral multi-model domain)

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

### Frame structure and indexing

Terminology used in this plan:

- **Raw/wire frame:** bytes exactly as received from TCP, including pseudo-escape
  sequences such as `1B 11`.
- **Logical frame:** frame after applying the selected model adapter's unescape
  policy. Adapter byte maps are indexed against logical frames unless explicitly
  stated otherwise.
- **Important:** frame boundaries must be detected on raw bytes first, then the
  adapter-specific unescape policy is applied. Do not unescape the continuous TCP
  stream before finding `0x1A ... 0x1D` boundaries, because unescaping can
  introduce interior delimiter bytes.

```
byte[0]  = 0x1A (start)
byte[1]  = destination address
byte[2]  = source address
byte[3]  = length-like field (often 0x3C for broadcasts; exact semantics TBD)
byte[4..N] = payload
byte[N+1..N+4] = CRC/checksum (4 bytes, algorithm unknown)
byte[last] = 0x1D (end)
```

⚠️ **Length validation caution:** The KDy sample has `byte[3] = 0x3C`, but the
raw and fully-unescaped total byte counts do not yet cleanly prove the length
formula. Initial validators should check delimiters, minimum size, model
signature, and malformed escapes, but should not reject otherwise-plausible
frames solely because an assumed length formula fails.

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

All indexes below are intended to be **logical-frame indexes after the P25B85
full-frame unescape policy**. Local captures must validate this map before it is
used by the Home Assistant adapter.

Reference frame from KDy (post #74), 0-indexed from `0x1A`:

```
1A FF 01 3C D2 B4 FF 08 03 5E 04 06 04 F5 40 00 68 01 00 12 21 12 3B 14 00 16 00 04 00 43 00 04
3B 12 00 14 00 00 00 06 4D 00 00 00 00 00 00 00 00 00 00 00 00 10 05 08 13 1B 11 12 00 00 4E 28 33
11 1D
```

| Byte      | Content                    | Notes (KDy P25B85)                                                                                                                                                                                          |
|-----------|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0         | `0x1A`                     | Start                                                                                                                                                                                                       |
| 1         | `0xFF`                     | Broadcast address                                                                                                                                                                                           |
| 2         | `0x01`                     | Master address                                                                                                                                                                                              |
| 3         | `0x3C`                     | Length                                                                                                                                                                                                      |
| 4–8       | `D2 B4 FF 08 03`           | Header (byte 8 = `0x03` for P25B85, `0x02` for P23B32)                                                                                                                                                      |
| **9**     | **Water temperature (°F)** | `0x5E` = 94°F = 34.4°C                                                                                                                                                                                      |
| 10–11     | `0x04 0x06`                | Unknown                                                                                                                                                                                                     |
| **12–13** | **Pump status candidates** | ⚠️ Needs local validation. KDy notes mention pump status at byte 13, but the reference sample contains `0x04` at byte 12 and `0xF5` at byte 13. Do not hard-code pump low/high until captures resolve this. |
| 14        | Heater area                | `0x40` idle in some notes; exact relation to bytes 12/13/15 needs validation                                                                                                                                |
| **15**    | **Heating state**          | `0x00`=off, `0x50`=circ-only, `0x54`=heating, `0x40`=cooldown, `0xC1`=UV/ozone                                                                                                                              |
| **16**    | **Setpoint (°F)**          | `0x68` = 104°F = 40°C                                                                                                                                                                                       |
| 17        | Flags                      |                                                                                                                                                                                                             |
| **18**    | **Light / shared flags**   | bit 0 (`0x01`) = light ON; `0x80` = set during UV/heating states                                                                                                                                            |
| 19–27     | Various                    | Schedule/config data                                                                                                                                                                                        |
| **28**    | **Equipment flags**        | May mirror pump status; needs validation after pump byte/index is resolved                                                                                                                                  |
| **29**    | **UV/Ozone flag**          | `0x20` when UV/ozone active                                                                                                                                                                                 |
| 30–52     | Various                    |                                                                                                                                                                                                             |
| **53–58** | **Date/Time**              | year, month, day, hour, minute, second (may need unescape)                                                                                                                                                  |
| 59–end    | CRC (4 bytes) + `0x1D`     |                                                                                                                                                                                                             |

⚠️ **Index conflict to resolve before Phase 3:** The reference sample appears to
place the pump-like value `0x04` at byte 12, while the community summary says
byte 13. The capture parser must display full byte diffs for pump-low and
pump-high captures, and the P25B85 adapter must not expose `pump_low` /
`pump_high` from a fixed index until this is confirmed on local hardware.

### P25B85 status combinations (KDy post #74)

| State                      | pump byte TBD | byte[15] | byte[18] | byte[29] |
|----------------------------|---------------|----------|----------|----------|
| All off                    | `0x00`*       | `0x00`   | `0x00`   | `0x00`   |
| Light only                 | —             | —        | `0x01`   | —        |
| Filtration (pump low)      | `0x02`        | —        | —        | —        |
| Massage (pump high)        | `0x04`        | —        | —        | —        |
| UV/ozone only              | —             | `0xC1`   | `0x80`   | `0x20`   |
| UV/ozone + light           | —             | `0xC1`   | `0x81`   | `0x20`   |
| Heating stage 1 (circ)     | —             | `0x50`   | `0x80`   | `0x20`   |
| Heating stage 2 (active)   | —             | `0x54`   | `0x80`   | `0x20`   |
| Heating stage 3 (cooldown) | —             | `0x40`   | `0x80`   | `0x20`   |

*KDy did not state the all-off pump byte explicitly; `0x00` is assumed from context.

### P23B32 differences (christopheknap posts #89, #92, #94)

| Field           | P25B85                 | P23B32                                              |
|-----------------|------------------------|-----------------------------------------------------|
| Header byte 8   | `0x03`                 | `0x02`                                              |
| Pump low/filter | pump byte TBD & `0x02` | byte 17 bit `0x80`                                  |
| Left jets       | —                      | byte 12 & `0x04`                                    |
| Right jets      | —                      | byte 12 & `0x10`                                    |
| Blower          | —                      | byte 14 & `0x08`                                    |
| Heater active   | byte 15 = `0x54`       | byte 14 & `0x10` (confirmed with smart plug)        |
| Light           | byte 18 & `0x01`       | byte 17 & `0x01`                                    |
| Filtration      | pump byte TBD & `0x02` | byte 14 & `0x01` (wrong! actually byte 17 & `0x80`) |
| Unescape scope  | full frame             | tail only (bytes 55+)                               |

⚠️ **P23B32 compatibility note:** The current fork parses P23B32 filtration as
`byte[14] & 0x01`. Community notes suggest `byte[17] & 0x80` may be the correct
filtration indicator. Preserve current fork behavior initially, or expose both
legacy/candidate values as diagnostics, until validated on P23B32 captures.

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

The unified integration should live in a neutral domain such as
`custom_components/joyonway_spa/` rather than a model-specific domain. This keeps
P25B85, P23B32, P20B29, and future PB55x-family controllers under one Home
Assistant integration.

If the existing `joyonway_p23b32` fork is migrated, document this as a breaking
domain change and provide migration guidance. Existing Home Assistant config
entries under the old domain will not automatically become entries for the new
domain without explicit migration/user action.

A model adapter interface separates shared protocol machinery from per-model
byte semantics, supported entities, and write capability.

### Shared core (reuse from P23B32 fork)

- TCP client and reconnect strategy
- Frame boundary reconstruction (`0x1A ... 0x1D`) from TCP stream chunks
- Pseudo-unescape utility
- Coordinator update flow, entity dispatch, error handling
- Config flow (IP, port, model selection)

### Model adapter interface

```text
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EntityDescription:
    platform: str                       # "sensor", "binary_sensor", "button", ...
    key: str                            # e.g. "water_temperature"
    name: str                           # user-facing name
    icon: str | None = None
    enabled_by_default: bool = True


class ModelAdapter(Protocol):
    """Per-model byte mapping and feature support."""
    model: str                          # e.g. "P25B85"
    broadcast_signature: bytes          # header to match
    unescape_full_frame: bool           # True for P25B85, False for P23B32
    supports_writes: bool               # False for P25B85 until replay captures exist

    def parse_status(self, frame: bytes) -> dict:
        """Extract state dict from unescaped broadcast frame."""

    def entity_descriptions(self) -> list[EntityDescription]:
        """List platform/key/name/device metadata for entities this model exposes."""
```

Entity metadata should be adapter-driven rather than hard-coded in `sensor.py`
and `binary_sensor.py`. A small frozen dataclass can describe the platform,
entity key, display name, icon, unit, device class, state class, entity category,
and whether a diagnostic entity is enabled by default.

### P25B85 adapter (primary, read-only first)

Entities to expose:
- `sensor.water_temperature` — byte 9, °F → °C
- `sensor.setpoint` — byte 16, °F → °C
- `binary_sensor.pump_low` — pump byte/index TBD from captures; expected mask `0x02` (filtration/circulation)
- `binary_sensor.pump_high` — pump byte/index TBD from captures; expected mask `0x04` (massage/jets)
- `binary_sensor.light` — byte 18 & `0x01`
- `binary_sensor.heater_active` — byte 15 == `0x54` (element actually drawing power)
- `sensor.heater_state` — byte 15 decoded as off / circulation / heating / cooldown / UV / unknown
- `binary_sensor.uv_lamp` — byte 15 == `0xC1` or byte 29 & `0x20`
- `binary_sensor.bridge_connection` — TCP connectivity
- `sensor.spa_datetime` — bytes 53–58 (optional, low priority)
- optional disabled-by-default diagnostic sensors for raw bytes used by the
  adapter, especially pump candidates and heater/UV bytes

Do not expose a generic `binary_sensor.heater` unless its semantics are clearly
defined. `byte[15] == 0x54` means the heating element is active; `0x50` and
`0x40` appear to be circulation/cooldown stages and should not be presented as
the heater actively drawing power.

For P25B85 Phase 3, the integration is **read-only**:
- no `button` platform
- no setpoint write controls
- no reuse of P23B32 command builders
- no synthetic frame construction

### P23B32 adapter (preserve existing behavior)

Keep the existing P23B32 byte map as a second adapter initially. This ensures
anyone using the P23B32 fork can migrate without immediate behavior changes.
Where community notes conflict with the existing fork, add diagnostics and test
captures before changing exposed entity semantics.

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
| 2 | Pump LOW (press pump button once)               | pump byte TBD → `0x02`             |
| 3 | Pump HIGH (press pump button again)             | pump byte TBD → `0x04`             |
| 4 | Heater active (raise setpoint above water temp) | byte 15 → `0x50` then `0x54`       |
| 5 | UV lamp (if accessible from panel)              | byte 15 → `0xC1`, byte 29 → `0x20` |
| 6 | Setpoint change (try 2–3 different °F values)   | byte 16 changes                    |

### What to validate from captures

- [ ] Confirm byte 8 = `0x03` in your broadcast header
- [ ] Confirm byte 9 = water temp °F (convert and check against panel display)
- [ ] Resolve pump status byte/index (byte 12 vs byte 13 conflict) for low vs high
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
  - Graceful Ctrl-C handling and per-segment metadata: timestamps, duration,
    byte count, frame count, broadcast count, notes
  - Warns about the bridge single-client limitation before starting
- [ ] Implement `tools/frame_parser_38400.py`
  - Parses `.bin` captures into individual frames
  - Detects frame boundaries on raw bytes, then applies selectable unescape
    policy: `full`, `tail`, `none`, or `auto`
  - Displays broadcast frames with annotated byte map
  - Diff mode: compare two captures side-by-side and summarize byte-value
    histograms across all broadcast frames, not only the first frame
  - Supports `--model p25b85|p23b32|auto`, `--json`, and optionally `--csv`
  - Displays both raw/wire indexes and logical indexes when escapes are present
- [ ] Add pure-stdlib tests/golden samples for frame extraction, pseudo-unescape,
      malformed escapes, KDy sample parsing, and diff output
- [ ] Add `tools/README.md` with quick-start examples
- [ ] Dry-run validation

### Phase 2: Protocol/adapters with tests

- [ ] Choose final neutral integration domain, preferably `joyonway_spa`
- [ ] Rename/create integration folder with updated domain and migration notes
- [ ] Extract shared frame parser from `rs485.py` into `protocol.py`
  - `find_frames(stream: bytes) -> list[bytes]` operating on raw bytes
  - `pseudo_unescape(data: bytes) -> bytes`
  - `validate_frame(frame: bytes) -> bool` with conservative validation only
- [ ] Create `adapters/` package with `base.py`, `p25b85.py`, `p23b32.py`
- [ ] Keep command/replay data separate from status parsing, e.g.
      `p23b32_commands.py`; do not place write frames in shared protocol code
- [ ] Add golden-frame tests for `protocol.py` and each adapter before wiring HA entities
- [ ] Update `coordinator.py` to use adapter interface
- [ ] Update `config_flow.py` to add model selection (default P25B85)
  - Store `model` in config entry data from the beginning
  - Later enhancement: auto-detect model from broadcast header byte 8
- [ ] Update entity files to use adapter's `entity_descriptions()`
- [ ] Update `manifest.json`, `const.py`, `strings.json`, translations
- [ ] Make device info dynamic (model name from adapter)
- [ ] Update `hacs.json`, README files, and bridge wording from W610/EW11-specific
      text to generic "RS485 bridge"

### Phase 3: Read-only P25B85 integration

- [ ] Implement P25B85 adapter `parse_status()` using KDy's byte map
- [ ] Validate byte mappings against your captures before exposing entities
  - Especially resolve the byte 12 vs byte 13 pump-status conflict
- [ ] Wire sensor entities: water_temperature, setpoint
- [ ] Wire binary_sensor entities: pump_low, pump_high, light, heater_active, uv_lamp, bridge_connection
- [ ] Test with live spa data
- [ ] Add heater state detail sensor (off / circulation / heating / cooldown / UV / unknown)
- [ ] Confirm P25B85 does not load the button platform and has no write path

### Phase 4: Write commands (only after captures + validation)

- [ ] Capture command frames from panel for each action (needs spa visit)
- [ ] Build command replay table: one verified frame per action with known-good CRC
- [ ] Implement flood-inject: 10× at 0.5s intervals
- [ ] Add button entities (light toggle, pump cycle, etc.)
- [ ] Add 30s post-command read suspension (per Gaet78/christopheknap finding)
- [ ] Add write allowlist: only replay captured, CRC-verified frames
- [ ] Add safe-fail: reject writes when no captured frame exists for requested action
- [ ] Require explicit per-model write enablement; P25B85 remains read-only unless
      a validated replay table is provided for matching hardware

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
- ❌ Don't load write/button entities for P25B85 during read-only phases
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
3. **Add parser/protocol tests with golden samples** — catch indexing and escape mistakes early
4. **Go to the spa and capture** — follow the sequence in section 4
5. **Analyze captures** — validate KDy's byte map and resolve pump byte conflict
6. **Implement Phase 2** — neutral-domain adapter architecture with tests
7. **Implement Phase 3** — read-only P25B85 entities, no buttons/writes
8. **Test on live spa** — validate everything works before considering replay writes
