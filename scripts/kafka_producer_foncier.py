import time
import json
import random
from faker import Faker
import pandas as pd
from schema import anonymize_pii, foncier_schema

# Initialisation de Faker pour générer de faux noms français
fake = Faker('fr_FR')

# Constantes métier (Régions et types de titres au Sénégal)
REGIONS_SENEGAL = ["Dakar", "Thiès", "Saint-Louis", "Mbour", "Ziguinchor", "Kaolack"]
TYPES_TITRES = ["Bail", "Titre Foncier", "Délibération", "Droit Coutumier"]

def generate_foncier_event(equipe_id="equipe07"):
    """
    Génère un dictionnaire représentant une parcelle foncière.
    Applique immédiatement l'anonymisation sur les données personnelles.
    Simule un score de risque basé sur des règles métier (ex: plus de revendications = plus de risque).
    """
    region = random.choice(REGIONS_SENEGAL)
    nom_proprietaire_brut = fake.name()
    cin_brut = fake.ssn()
    
    # --- EXIGENCE PRIVACY : Hachage immédiat (0 PII en clair) ---
    proprietaire_hash = anonymize_pii(f"{nom_proprietaire_brut}_{cin_brut}")
    
    # Simulation de la logique de risque
    nb_revendications = random.choices([1, 2, 3, 4, 5], weights=[0.7, 0.15, 0.08, 0.05, 0.02])[0]
    is_litigieuse = 1 if nb_revendications > 1 or random.random() < 0.15 else 0
    
    # Calcul mathématique du score (plus il y a de revendications, plus le risque monte)
    base_risk = 0.2 * nb_revendications + (0.3 if is_litigieuse else 0.0) + (0.2 if region == "Dakar" else 0.1)
    risk_score = round(min(0.99, max(0.01, base_risk + random.uniform(-0.05, 0.05))), 2)

    # Construction de l'événement
    data = {
        "parcelle_id": f"SN-{region[:3].upper()}-{random.randint(10000, 99999)}",
        "region": region,
        "superficie_m2": round(random.uniform(150.0, 5000.0), 2),
        "type_titre": random.choice(TYPES_TITRES),
        "proprietaire_hash": proprietaire_hash,
        "longitude": round(random.uniform(-17.5, -16.5), 5),
        "latitude": round(random.uniform(14.5, 15.0), 5),
        "nombre_revendications": nb_revendications,
        "is_zone_litigieuse": is_litigieuse,
        "risque_conflit_score": risk_score,
        "equipe_id": equipe_id
    }
    return data

def run_simulation(num_samples=500, output_csv="data/foncier_simulated.csv"):
    """
    Fonction principale : génère N échantillons, les valide avec Pandera,
    puis les sauvegarde dans un fichier CSV pour l'entraînement ML.
    """
    records = []
    print(f"[START] Génération de {num_samples} événements fonciers pour Yeewu-SN...")
    for _ in range(num_samples):
        event = generate_foncier_event()
        records.append(event)
    
    df = pd.DataFrame(records)
    
    # --- VALIDATION DES DONNÉES ---
    # Pandera s'assure qu'aucune valeur aberrante (ex: superficie négative) ne passe.
    df = foncier_schema.validate(df)
    
    df.to_csv(output_csv, index=False)
    print(f"[SUCCESS] Données enregistrées dans {output_csv} (0 PII en clair).")

if __name__ == "__main__":
    run_simulation(500)