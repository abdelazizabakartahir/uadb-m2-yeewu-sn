import os
import hashlib
import pandas as pd
import pandera as pa
from pandera import Column, Check

# ==============================================================================
# COUCHE DE SÉCURITÉ : ANONYMISATION DES DONNÉES (PII)
# ==============================================================================
# J'utilise os.getenv pour récupérer le sel depuis l'environnement système.
# Si la variable n'existe pas, le script s'arrête (Fail-Fast) pour éviter toute fuite.
SALT = os.getenv("PII_SALT")
if not SALT:
    raise ValueError("[ERREUR SECURITE] La variable d'environnement PII_SALT est manquante.")

def anonymize_pii(valeur: str) -> str:
    """
    Hache une donnée sensible (ex: Nom + CIN) en utilisant SHA-256.
    Le sel (SALT) est ajouté avant le hachage pour contrer les attaques 
    par dictionnaire (Rainbow Tables).
    Retourne une chaîne hexadécimale de 16 caractères.
    """
    if not valeur:
        return ""
    salted_value = f"{valeur}_{SALT}"
    return hashlib.sha256(salted_value.encode('utf-8')).hexdigest()[:16]

# ==============================================================================
# COUCHE DE VALIDATION : SCHEMA PANDERA STRICT
# ==============================================================================
# Pandera vérifie que les types (str, float, int) et les plages de valeurs sont 
# respectés. Si une donnée est corrompue, Pandera lèvera une erreur.
foncier_schema = pa.DataFrameSchema({
    "parcelle_id": Column(str, Check.str_matches(r"^SN-[A-Z]{3}-[0-9]{5}$")),
    "region": Column(str, Check.isin(["Dakar", "Thiès", "Saint-Louis", "Mbour", "Ziguinchor", "Kaolack"])),
    "superficie_m2": Column(float, Check.in_range(50.0, 50000.0)),
    "type_titre": Column(str, Check.isin(["Bail", "Titre Foncier", "Délibération", "Droit Coutumier"])),
    "proprietaire_hash": Column(str, Check.str_length(16)),
    "longitude": Column(float, Check.in_range(-17.6, -11.3)), # Coordonnées du Sénégal
    "latitude": Column(float, Check.in_range(12.3, 16.7)),
    "nombre_revendications": Column(int, Check.in_range(1, 10)),
    "is_zone_litigieuse": Column(int, Check.isin([0, 1])),
    "risque_conflit_score": Column(float, Check.in_range(0.0, 1.0))
})

if __name__ == "__main__":
    print("[INFO] Schéma Pandera Yeewu-SN chargé et prêt pour la validation.")