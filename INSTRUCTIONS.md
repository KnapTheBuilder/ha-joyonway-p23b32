# Mise à jour repo ha-joyonway-p23b32 - 17/05/2026

## 📦 Contenu du ZIP

```
ha-joyonway-update/
├── INSTRUCTIONS.md                        ← CE FICHIER (lis-moi d'abord)
├── README_PATCH.md                        ← snippet à insérer dans README.md
└── packages/
    └── spa_consigne_lock.yaml             ← NOUVEAU fichier à drop dans le repo
```

## 🚀 Procédure GitHub Desktop (5 min)

### Étape 1 — Localiser ton repo local

1. Ouvre **GitHub Desktop**
2. Sélectionne le repo `ha-joyonway-p23b32`
3. Clique **File → Show in Explorer** (Windows) ou **Show in Finder** (Mac)
4. Tu es maintenant dans le dossier local du repo. Tu dois y voir :
   - `.github/`
   - `.gitignore`
   - `custom_components/`
   - `docs/`
   - `hacs.json`
   - `README.md`

### Étape 2 — Ajouter le dossier packages

1. Depuis ce ZIP, copie le dossier `packages/` (et son contenu `spa_consigne_lock.yaml`)
2. Colle-le directement à la racine de ton repo local
3. Résultat attendu : tu as maintenant `ha-joyonway-p23b32/packages/spa_consigne_lock.yaml`

### Étape 3 — Update README.md

1. Ouvre `README.md` dans un éditeur de texte (VSCode, Notepad++, Sublime, etc.)
2. Cherche la ligne `## Dashboard example` (vers la ligne 344)
3. Ouvre `README_PATCH.md` depuis ce ZIP
4. Copie UNIQUEMENT le contenu entre les lignes `==== DÉBUT À COPIER ====` et `==== FIN À COPIER ====`
5. Colle-le dans `README.md` **JUSTE AVANT** la ligne `## Dashboard example`
6. Sauvegarde `README.md`

### Étape 4 — Commit dans GitHub Desktop

1. Retourne dans GitHub Desktop
2. Tu vois 2 changements en attente dans la colonne de gauche :
   - 🟢 NEW: `packages/spa_consigne_lock.yaml`
   - 🟡 MODIFIED: `README.md`
3. En bas à gauche, remplis :
   - **Summary** : `feat: add 30s setpoint command lock package (credit @Gaet78)`
   - **Description** : copie le bloc DESCRIPTION fourni dans README_PATCH.md (en bas du fichier)
4. Clique **Commit to main**

### Étape 5 — Push

- Clique **Push origin** en haut de GitHub Desktop
- Attends la barre de progression jusqu'à confirmation

### Étape 6 — Vérification finale

1. Ouvre https://github.com/KnapTheBuilder/ha-joyonway-p23b32 dans ton navigateur
2. Vérifie que `packages/spa_consigne_lock.yaml` apparaît dans l'arborescence
3. Clique sur le README et scroll jusqu'à la section "Setpoint command lock (30s timing fix)"
4. Vérifie que le lien `packages/spa_consigne_lock.yaml` est cliquable et bien lié

## ✅ Tu peux dormir tranquille

Ton repo public est maintenant à jour avec :
- Le fix critique du verrou 30s post-consigne
- Un crédit explicite à @Gaet78 pour la découverte du timing
- Le YAML prêt à l'emploi pour quiconque utilise ton intégration

🌙 Bonne nuit Christophe — c'est une journée exceptionnelle.
