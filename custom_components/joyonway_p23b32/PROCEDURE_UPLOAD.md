# Procedure upload v0.3.0 finalisation

3 fichiers a remplacer sur GitHub via le navigateur. Aucun GitHub Desktop, aucun clone necessaire.

## 1. manifest.json (bump version 0.2.0 vers 0.3.0)

URL :
https://github.com/KnapTheBuilder/ha-joyonway-p23b32/blob/main/custom_components/joyonway_p23b32/manifest.json

Procedure :
1. Clic sur le fichier
2. Clic sur l'icone crayon (Edit this file) en haut a droite
3. Selectionne TOUT (Ctrl+A) puis colle le contenu du fichier manifest.json livre
4. En bas : Commit message = `bump manifest to 0.3.0`
5. Clic Commit changes

## 2. CHANGELOG.md (ajout section v0.3.0)

URL :
https://github.com/KnapTheBuilder/ha-joyonway-p23b32/blob/main/CHANGELOG.md

Procedure :
1. Clic sur le fichier
2. Clic sur l'icone crayon
3. Selectionne tout, remplace par le contenu du CHANGELOG.md livre
4. Commit message = `changelog v0.3.0`
5. Commit changes

## 3. README.md (mise a jour v0.2 vers v0.3)

URL :
https://github.com/KnapTheBuilder/ha-joyonway-p23b32/blob/main/README.md

Procedure :
1. Clic sur le fichier
2. Clic sur l'icone crayon
3. Selectionne tout, remplace par le contenu du README.md livre
4. Commit message = `README v0.3.0 update`
5. Commit changes

## 4. Creer la Release v0.3.0

URL :
https://github.com/KnapTheBuilder/ha-joyonway-p23b32/releases/new

Procedure :
1. Choose a tag : taper `v0.3.0` puis clic sur "Create new tag: v0.3.0 on publish"
2. Target : main (par defaut)
3. Release title : `v0.3.0 - Dynamic setpoints via @alexbde CRC + climate + switch`
4. Description : copier la section "v0.3.0 - 2026-05-27" du CHANGELOG.md (titre Added/Changed/Known issue/Credits)
5. Cocher "Set as the latest release"
6. Clic Publish release

## Verification finale

Apres ces 4 etapes, va sur https://github.com/KnapTheBuilder/ha-joyonway-p23b32 et confirme que tu vois :

- Releases : v0.3.0 (en latest)
- README en haut : "Joyonway Spa - Home Assistant Integration v0.3"
- manifest.json : `"version": "0.3.0"`
- CHANGELOG.md commence par `## v0.3.0 - 2026-05-27`

HACS detectera la nouvelle release automatiquement dans les heures qui suivent et proposera la mise a jour aux utilisateurs.
