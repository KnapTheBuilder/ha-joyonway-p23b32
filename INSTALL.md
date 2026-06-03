# Installation guide - HA integration v0.2.0

## English

### Apply this update to your `ha-joyonway-p23b32` GitHub repository

This ZIP is a major update for your existing integration.

### Step 1 - Backup

GitHub Desktop > Repository > Show in Explorer > copy the folder as backup.

### Step 2 - Replace files

1. Extract this ZIP to a temporary location
2. Copy ALL files from `ha-joyonway-p23b32-v0.2/` to your repo folder
3. **Overwrite** when asked (custom_components/joyonway_p23b32/* will be updated)

### Step 3 - Test locally (recommended)

Before pushing, install the integration locally:

1. Copy `custom_components/joyonway_p23b32/` to your HA `/config/custom_components/`
2. Restart HA
3. Settings > Devices & Services > Add Integration > Joyonway
4. Enter your W610 IP
5. Verify entities appear: `sensor.water_temperature`, `sensor.setpoint`, `sensor.heating_state`, 9 buttons
6. Verify water_temperature matches what the spa panel displays

If everything works, proceed to Step 4.

### Step 4 - Commit and push (GitHub Desktop)

1. Summary: `v0.2.0 - Multi-model 1A/1D family + KDy unescape + Yannickt26 setpoint`
2. Description: copy from `CHANGELOG.md`
3. Commit to main
4. Push origin
5. Optionally: tag `v0.2.0` and create Release on GitHub

### Step 5 - Verify GitHub Actions

- hassfest workflow should be green
- HACS validation workflow should be green (or note remaining warnings)

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| Entities show "unavailable" | Check no other client (Joyonway app) is connected to W610 |
| No B4 frames decoded | Verify W610 in Transparent TCP mode, baudrate 38400 |
| Heater button does nothing | Activate "Thermostat manuel" in PB555 panel menu first |
| Wrong temperature value | Confirm your spa panel shows the same value (validates byte 9 decoding) |

---

## Francais

### Appliquer cette mise a jour a ton depot `ha-joyonway-p23b32`

Ce ZIP est une mise a jour majeure de ton integration existante.

### Etape 1 - Backup

GitHub Desktop > Repository > Show in Explorer > copier le dossier en sauvegarde.

### Etape 2 - Remplacer les fichiers

1. Extraire ce ZIP dans un dossier temporaire
2. Copier TOUS les fichiers de `ha-joyonway-p23b32-v0.2/` vers ton repo
3. **Ecraser** quand demande (custom_components/joyonway_p23b32/* sera mis a jour)

### Etape 3 - Test local (recommande)

Avant de pousser, installe l'integration en local :

1. Copier `custom_components/joyonway_p23b32/` vers ton HA `/config/custom_components/`
2. Redemarrer HA
3. Parametres > Appareils et services > Ajouter integration > Joyonway
4. Renseigner l'IP du W610
5. Verifier que les entites apparaissent : `sensor.water_temperature`, `sensor.setpoint`, `sensor.heating_state`, 9 boutons
6. Verifier que water_temperature correspond a ce qui s'affiche sur le panneau du spa

Si tout marche, passer a l'etape 4.

### Etape 4 - Commit et push (GitHub Desktop)

1. Summary : `v0.2.0 - Famille 1A/1D multi-modeles + unescape KDy + setpoint Yannickt26`
2. Description : copie depuis `CHANGELOG.md`
3. Commit to main
4. Push origin
5. Optionnel : tag `v0.2.0` et creer Release sur GitHub

### Etape 5 - Verifier GitHub Actions

- Le workflow hassfest doit etre vert
- Le workflow HACS validation doit etre vert (ou noter les warnings restants)

### Depannage

| Symptome | Solution |
|----------|----------|
| Entites "unavailable" | Verifier qu'aucun autre client (app Joyonway) n'est connecte au W610 |
| Pas de trames B4 decodees | Verifier W610 en mode TCP Transparent, baudrate 38400 |
| Bouton chauffage ne fait rien | Activer "Thermostat manuel" dans le menu du panneau PB555 |
| Temperature incorrecte | Confirmer que le panneau du spa affiche la meme valeur (valide le decodage byte 9) |
