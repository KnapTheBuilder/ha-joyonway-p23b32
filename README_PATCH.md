# README PATCH - À INSÉRER dans README.md

## 📍 Où insérer

Dans ton README.md actuel, trouve la ligne avec `## Dashboard example` (ligne ~344).
Insère le contenu ci-dessous **JUSTE AVANT** cette ligne, donc après la section
`## Automation examples` qui se termine ligne ~343.

================================================================================
COPIER UNIQUEMENT LE CONTENU ENTRE LES LIGNES ============ DANS README.md
================================================================================

================================ DÉBUT À COPIER ================================

## Setpoint command lock (30s timing fix)

After a setpoint command is sent over RS485, the Joyonway controller keeps broadcasting the **old** setpoint value for about 30 seconds before it finally applies the new one. If Home Assistant reads and reacts to that "stale" broadcast during this window (typical when a climate slider mirrors `sensor.joyonway_p23b32_consigne` back into the bus), the integration ends up re-sending the old value and overwriting the user's command.

**Symptom.** You set the spa setpoint to 30 degC, then about 30 seconds later it spontaneously jumps back to 37 degC (the previous value).

**Fix.** After any setpoint command, suspend the climate-slider feedback automation for 30 seconds. Credit to [@Gaet78](https://community.home-assistant.io/u/gaet78) for documenting the underlying RS485 timing behaviour in his P69B133 integration README, which is what allowed me to identify the root cause on the P23B32.

### How it works

1. `input_boolean.spa_consigne_lock` is a visual indicator (LOCKED / FREE) you can drop on a dashboard.
2. `automation.spa_verrou_consigne_30s` triggers whenever any `script.spa_cmd_consigne_*` runs, then:
   - turns the lock ON,
   - disables the climate-slider feedback automation,
   - waits 30 seconds,
   - re-enables the climate-slider feedback,
   - turns the lock OFF.

### Install

Drop [`packages/spa_consigne_lock.yaml`](packages/spa_consigne_lock.yaml) into your `packages/` folder, then **edit the entity_id** of your own slider-to-script automation inside the file (search for the comment `Replace below`).

<details>
<summary><b>Optional dashboard tile (mini lock indicator)</b></summary>

```yaml
# 2026-05-17 | Lovelace | Mini-tile setpoint lock | Depends on: input_boolean.spa_consigne_lock
type: custom:button-card
entity: input_boolean.spa_consigne_lock
name: |
  [[[ return entity.state === 'on' ? 'LOCKED 30s' : 'FREE' ]]]
icon: |
  [[[ return entity.state === 'on' ? 'mdi:lock-clock' : 'mdi:lock-open-variant-outline' ]]]
show_state: false
styles:
  card:
    - background: "[[[ return entity.state === 'on' ? '#1a0a25' : '#08111e' ]]]"
    - border-radius: 10px
    - padding: 6px 10px
    - border: "[[[ return entity.state === 'on' ? '1px solid #b388ff66' : '1px solid #ffffff08' ]]]"
    - box-shadow: "[[[ return entity.state === 'on' ? '0 0 10px #b388ff50' : 'none' ]]]"
  name:
    - color: "[[[ return entity.state === 'on' ? '#b388ff' : '#3a3040' ]]]"
    - font-size: 9px
    - letter-spacing: 1.5px
  icon:
    - color: "[[[ return entity.state === 'on' ? '#b388ff' : '#3a3040' ]]]"
    - width: 16px
```

</details>

---

================================ FIN À COPIER ==================================


================================================================================
COMMIT MESSAGE pour GitHub Desktop
================================================================================

SUMMARY (champ titre, court) :
feat: add 30s setpoint command lock package (credit @Gaet78)

DESCRIPTION (champ description, multi-lignes) :
After a setpoint RS485 command, the controller keeps broadcasting the
old value for about 30s. If HA's climate slider mirrors that stale
broadcast back into a script, the user's command gets overwritten.

This package adds:
- input_boolean.spa_consigne_lock (visual LOCKED/FREE indicator)
- automation.spa_verrou_consigne_30s (suspends the slider feedback
  automation for 30s after each setpoint command)

README updated with a new section "Setpoint command lock" describing
the symptom, root cause and install instructions.

Bilingual yaml comments (EN/FR). Credit to @Gaet78 for documenting
the underlying timing in his P69B133 integration README.
