import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, mean_squared_error, r2_score

def train_model():
    """
    Entraîne deux modèles en parallèle :
    1. Un classifieur (Prédire s'il y a litige : Oui/Non).
    2. Un régresseur (Prédire la gravité du risque : 0.0 à 1.0).
    Cela répond aux exigences d'Accuracy/F1 ET de RMSE/R².
    """
    data_path = "data/foncier_simulated.csv"
    if not os.path.exists(data_path):
        from kafka_producer_foncier import run_simulation
        run_simulation(1000)

    df = pd.read_csv(data_path)

    # Séparation des variables explicatives (X) et des cibles (y)
    X = df[["region", "superficie_m2", "type_titre", "nombre_revendications", "longitude", "latitude"]]
    y_clf = df["is_zone_litigieuse"]  # Cible binaire
    y_reg = df["risque_conflit_score"] # Cible continue

    # Pipeline de prétraitement : Encodage des variables textuelles
    categorical_features = ["region", "type_titre"]
    numerical_features = ["superficie_m2", "nombre_revendications", "longitude", "latitude"]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )

    # Split des données (80% train, 20% test)
    X_train, X_test, y_clf_train, y_clf_test = train_test_split(X, y_clf, test_size=0.2, random_state=42)
    _, _, y_reg_train, y_reg_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)

    # --- MODÈLE 1 : CLASSIFICATION ---
    pipeline_clf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    pipeline_clf.fit(X_train, y_clf_train)
    y_clf_pred = pipeline_clf.predict(X_test)

    acc = accuracy_score(y_clf_test, y_clf_pred)
    f1 = f1_score(y_clf_test, y_clf_pred)

    # --- MODÈLE 2 : RÉGRESSION ---
    pipeline_reg = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    pipeline_reg.fit(X_train, y_reg_train)
    y_reg_pred = pipeline_reg.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))
    r2 = r2_score(y_reg_test, y_reg_pred)

    # Affichage des résultats
    print("==================================================")
    print("--- RÉSULTATS DU MODÈLE YEEWU-SN ---")
    print("==================================================")
    print("[CLASSIFICATION] Prédiction Litige (Oui/Non)")
    print(f"Accuracy : {acc:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print("\n[RÉGRESSION] Prédiction du Score de Risque (0 à 1)")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")
    print("==================================================")

    # Sauvegarde des modèles (Sérialisation)
    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline_clf, "models/model_clf_litige.pkl")
    joblib.dump(pipeline_reg, "models/model_reg_risque.pkl")
    print("[SUCCESS] Les deux modèles sont sauvegardés dans le dossier /models.")

if __name__ == "__main__":
    train_model()