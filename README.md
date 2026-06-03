[![Joyonway P23B32 Logo](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/raw/main/custom_components/joyonway_p23b32/brand/icon@2x.png)](custom_components/joyonway_p23b32/brand/icon@2x.png)

# Joyonway P23B32 Spa for Home Assistant

**Native local integration for the Joyonway P23B32 spa controller via RS485 over a USR-W610 WiFi bridge.**

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/KnapTheBuilder/ha-joyonway-p23b32?style=for-the-badge&color=brightgreen)](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/releases)
[![License](https://img.shields.io/github/license/KnapTheBuilder/ha-joyonway-p23b32?style=for-the-badge&color=blue)](LICENSE)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1.0%2B-41BDF5.svg?style=for-the-badge&logo=home-assistant&logoColor=white)](https://www.home-assistant.io)

[![Validate with hassfest](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/hassfest.yml/badge.svg)](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/hassfest.yml)
[![HACS Validation](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/hacs.yml/badge.svg)](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/hacs.yml)

[Features](#features) · [Showcase](#showcase) · [Install](#installation) · [Config](#configuration) · [Entities](#entities) · [Automations](#automation-examples) · [Dashboard](#dashboard-example) · [Protocol](#protocol-details) · [Roadmap](#roadmap) · [Credits](#credits)

---

## Overview

This integration brings full Home Assistant control over the **Joyonway P23B32** spa controller. Communication is purely local via RS485, bridged to your network through a **USR-W610** WiFi-to-serial adapter in TCP server mode. No cloud, no Joyonway app, no internet required.

All commands have been reverse-engineered from RS485 captures and physically validated on a real P23B32 unit on 2026-05-11.

> **Discussion thread on HA Community:** [JoyOnWay Spa Control](https://community.home-assistant.io/t/joyonway-spa-control/582344)

---

## Features

- **Fully local control**, no cloud dependency, no internet required
- **Real-time monitoring** of water temperature, setpoint, all pumps, blower, light, heater
- **One-shot commands** to toggle every accessory, plus an "All OFF" emergency stop
- **Setpoint control** from 16 to 40 degrees Celsius (60 to 104 Fahrenheit)
- **Simple config flow**, just enter the IP and TCP port of the W610 bridge
- **Connectivity sensor** to detect when the W610 bridge is offline
- **Native HA device**, all entities grouped under one logical device with manufacturer info
- **English and French** UI translations included
- **HACS and hassfest validated**, ready for one-click HACS install

---

## Showcase

A real-world dashboard built on top of this integration, with thermostat, command panel, mode presets, EDF Tempo integration, and automatic scheduling:

[![Joyonway P23B32 Home Assistant dashboard example](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/raw/main/docs/screenshots/dashboard.png)](docs/screenshots/dashboard.png)

The dashboard uses Mushroom cards, custom button-card, and a circular thermostat card to expose every entity from the integration in a clean, mobile-friendly layout.

---

## Requirements

| Item | Details |
| --- | --- |
| Spa controller | Joyonway P23B32 (physically validated, other models may need protocol adaptation) |
| RS485 bridge | USR-W610 (WiFi, TCP Server mode, port 8899, 38400 8N1) |
| Home Assistant | 2024.1.0 or later |
| Network | HA and W610 on the same LAN, no internet required |

---

## Hardware wiring

> **Warning.** Opening the spa electrical enclosure exposes you to mains voltage. Always cut the power at the breaker before any intervention. If you are not comfortable with electrical work, hire a qualified electrician.

The USR-W610 connects to the RS485 bus inside the spa controller box:

```
