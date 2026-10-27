import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==============================================================================
# GÉNÉRATION DES IMAGES STATIQUES 
# ==============================================================================

# Chargement des données
df = pd.read_csv("../data/foncier_simulated.csv") 

# Création du dossier de destination s'il n'existe pas
os.makedirs("../dashboard", exist_ok=True)

# ------------------------------------------------------------------------------
# 1. Graphique : Nombre de litiges par région
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6)) # Format paysage
# sns.countplot compte le nombre de lignes pour chaque région, séparées par le statut de litige
sns.countplot(data=df, x='region', hue='is_zone_litigieuse', palette={0: '#2ecc71', 1: '#e74c3c'})
plt.title("Nombre de Parcelles et Litiges par Région - Yeewu-SN", fontweight='bold')
plt.xlabel("Région", fontweight='bold')
plt.ylabel("Nombre de Parcelles", fontweight='bold')
plt.legend(title="Litige Confirmé", labels=['Non (0)', 'Oui (1)'])
plt.xticks(rotation=30) # Rotation pour éviter que les noms se chevauchent
plt.tight_layout()

# Sauvegarde de l'image
plt.savefig("../dashboard/parcelles_par_region.png", dpi=300)
plt.close() # Fermeture de la figure pour libérer la mémoire

# ------------------------------------------------------------------------------
# 2. Graphique : Distribution du score de risque
# ------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
# sns.histplot affiche la fréquence des scores de risque avec une courbe de tendance (KDE)
sns.histplot(df['risque_conflit_score'], bins=20, color='#3498db', kde=True)
# Ligne rouge pointillée pour matérialiser le seuil critique
plt.axvline(0.70, color='red', linestyle='--', label='Zone Critique (>= 0.70)')
plt.title("Distribution du Score de Risque Foncier - Yeewu-SN", fontweight='bold')
plt.xlabel("Score de Risque (0 à 1)", fontweight='bold')
plt.ylabel("Fréquence", fontweight='bold')
plt.legend()
plt.tight_layout()

# Sauvegarde de l'image
plt.savefig("../dashboard/distribution_risque.png", dpi=300)
plt.close()

print("Succès : Les graphiques PNG ont été générés dans le dossier /dashboard/")