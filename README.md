<p align="center">
  <img src="docs/images/logo.png" alt="Joyonway P23B32 logo" width="120"/>
</p>

# Joyonway P23B32 Spa - Home Assistant integration

[!\[hacs\_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[!\[Validate with hassfest](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/hassfest.yml/badge.svg)](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/hassfest.yml)
[!\[HACS Validation](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/validate.yml/badge.svg)](https://github.com/KnapTheBuilder/ha-joyonway-p23b32/actions/workflows/validate.yml)
[!\[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Integration Home Assistant pour la centrale de spa **Joyonway P23B32** (V2, 2019)
pilotee **localement** en RS485 via un pont **USR-W610** (TCP/IP vers serie).

Reverse engineering du protocole effectue par capture de trames sur le bus
RS485 entre le controleur P23B32 et l'app officielle Joyonway. Le controleur
ne valide pas le CRC : les trames capturees sont rejouees telles quelles
avec un excellent taux de reussite.

## Apercu

|Equipements|Programmation|Monitoring|
|-|-|-|
|!\[Dashboard equipements](docs/images/dashboard-equipements.png)|!\[Programmation](docs/images/dashboard-programmation.png)|!\[Monitoring](docs/images/dashboard-monitoring.png)|

## Materiel requis

|Element|Reference / valeur|
|-|-|
|Centrale spa|Joyonway P23B32 (testee V2, 2019)|
|Pont RS485/TCP|USR-W610 en mode TCP server|
|Home Assistant|Core, OS ou Supervised >= 2024.10|
|HACS|Installe|

### Configuration USR-W610 attendue

|Parametre|Valeur|
|-|-|
|Mode|TCP Server|
|Port local TCP|8899|
|Baudrate|38400|
|Data bits|8|
|Stop bits|1|
|Parity|None|
|Flow control|None|

## Commandes exposees

L'integration cree un device unique `Joyonway P23B32` avec 10 entites `button` :

|Bouton|Action|
|-|-|
|Lumiere ON / OFF|Eclairage LED|
|Pompe gauche ON / OFF|Pompe jets gauche|
|Pompe droite ON / OFF|Pompe jets droite|
|Bulleur ON / OFF|Air blower|
|Filtration|Mise a jour planning filtration|
|Tout eteindre|Coupe tous les equipements|

Le chauffage est asservi a une consigne thermostat. Une fonction
`build\\\\\\\_consigne\\\\\\\_frame(temp\\\\\\\_f)` est exposee dans `rs485.py` pour generer
dynamiquement la trame de consigne (60-104 F). Elle sera cablee a une
entite `climate` dans une prochaine release.

## Installation via HACS (custom repository)

1. HACS > menu trois points > **Custom repositories**
2. URL : `https://github.com/KnapTheBuilder/ha-joyonway-p23b32` - Categorie : `Integration`
3. **Add** puis cherche "Joyonway P23B32" dans HACS, installe-la
4. Redemarre Home Assistant

## Configuration

1. **Settings > Devices and services > Add integration**
2. Cherche **Joyonway P23B32**
3. Saisis l'IP et le port du USR-W610 (par defaut `192.168.1.34:8899`)
4. Valide. Les boutons apparaissent sous le device `Joyonway P23B32`

## Protocole reverse-engineered (synthese)

Les trames sont delimitees par `0x1A` (debut) et `0x1D` (fin). Le byte 5
porte le type de trame.

|Type|Byte 5|Usage|
|-|-|-|
|Commande equipement|`0xA1`|Lumiere, pompes, bulleur, consigne|
|Filtration / planning|`0xA4`|Mise a jour planning|
|Arret total|`0xAA`|Coupe tout en une trame courte|

Toutes les trames hex completes sont dans
[`custom\\\\\\\_components/joyonway\\\\\\\_p23b32/rs485.py`](custom_components/joyonway_p23b32/rs485.py).

Chaque commande est envoyee 10 fois a 0.5 s d'intervalle (configurable dans
`const.py` via `REPEAT\\\\\\\_COUNT` et `REPEAT\\\\\\\_INTERVAL`). Cette redondance
compense les eventuelles collisions sur le bus RS485.

## Cartes Lovelace et automatisations

Le dashboard montre en exemple ci-dessus (style "dark neon") combine :

* Une carte equipements avec temperature eau / consigne, etat des
actionneurs (lumiere, filtration, chauffage), boutons ON/OFF par
equipement, marche generale, arret total + relance filtre
* Une carte programmation avec creneaux filtration (05h00-23h00) et
chauffage (11h30-13h00, 14h00-15h00), pilotee par un `input\\\\\\\_boolean`
Programme Auto
* Un suivi historique consommation (W) et temperature de l'eau

Les YAML correspondants ne sont pas dans ce repo (specifiques aux entites
de chaque installation). Demande sur le forum HA si tu veux des exemples.

## Roadmap

* \[ ] Plateforme `climate` (consigne + lecture etat chauffage)
* \[ ] Plateforme `sensor` (temperature eau via parsing des broadcasts)
* \[ ] Plateforme `binary\\\\\\\_sensor` (etats equipements lus du bus)
* \[ ] Plateforme `switch` (toggle stateful avec lecture etat reel)
* \[ ] Coordinator polling RS485 pour exposer les etats live
* \[ ] Tests unitaires sur les trames et le parsing
* \[ ] Traductions DE, ES, IT

## Avertissements

* **Reverse engineering communautaire**. Utilisation a tes risques.
* La centrale spa est un equipement 230 V : aucune intervention materielle
sans coupure secteur prealable.
* Compatibilite testee sur **P23B32 V2 (2019)** uniquement. Les modeles
P20B29, P25B37, P25B85, P69B133 ont un protocole different (voir le
[thread HA Community](https://community.home-assistant.io/t/joyonway-spa-control/582344)).

## Remerciements

* **Gaet78** pour l'integration HACS originelle et le decodage P69B133
* **KDy** pour l'analyse comparative des trames broadcast
* **Neuro** pour le travail ESP32+MAX485 sur P23B32 V2
* Le fil [JoyOnWay Spa Control](https://community.home-assistant.io/t/joyonway-spa-control/582344)
sur Home Assistant Community

## Licence

MIT. Voir [LICENSE](LICENSE).

