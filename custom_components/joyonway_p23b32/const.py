# 2026-05-13 | Constantes | Identifiants et cles de configuration | Dépend: aucune
"""Constants for the Joyonway P23B32 integration."""

from __future__ import annotations

DOMAIN: str = "joyonway_p23b32"

# Cles de configuration
CONF_HOST: str = "host"
CONF_PORT: str = "port"

# Valeurs par defaut (USR-W610 standard)
DEFAULT_HOST: str = "192.168.1.34"
DEFAULT_PORT: int = 8899
DEFAULT_NAME: str = "Joyonway P23B32"

# Comportement RS485
REPEAT_COUNT: int = 10
REPEAT_INTERVAL: float = 0.5
TCP_TIMEOUT: float = 5.0

# Identifiants des commandes confirmees
CMD_LUMIERE_ON: str = "lumiere_on"
CMD_LUMIERE_OFF: str = "lumiere_off"
CMD_POMPE_GAUCHE_ON: str = "pompe_gauche_on"
CMD_POMPE_GAUCHE_OFF: str = "pompe_gauche_off"
CMD_POMPE_DROITE_ON: str = "pompe_droite_on"
CMD_POMPE_DROITE_OFF: str = "pompe_droite_off"
CMD_BULLEUR_ON: str = "bulleur_on"
CMD_BULLEUR_OFF: str = "bulleur_off"
CMD_FILTRATION: str = "filtration"
CMD_ALL_OFF: str = "all_off"
CMD_CONSIGNE: str = "consigne"

# Plateformes chargees
PLATFORMS: list[str] = ["button"]
