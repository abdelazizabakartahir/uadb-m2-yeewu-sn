# Yeewu-SN : Plateforme d'Intelligence Foncière

**NOM :** ABDEL-AZIZ ABAKAR TAHIR
**Master 2 DSGL — UADB — 2025-2026**
**Projet Tutoré : Big Data & IA**

## Architecture du Pipeline

```text
┌─────────────┐      ┌─────────┐      ┌──────────┐      ┌────────────┐
│ Simulateur  │─────▶│  Kafka  │─────▶│   NiFi   │─────▶│   HBase    │
│ (Python/Faker)│    │ (Topic) │      │ (Stream) │      │ (Stockage) │
└─────────────┘      └─────────┘      └──────────┘      └────────────┘
       │                                                        │
       ▼                                                        ▼
┌─────────────┐      ┌─────────┐      ┌──────────┐      ┌────────────┐
│  Dashboard  │◀─────│  Hive   │◀─────│ Airflow  │◀─────│ Modèles ML │
│    (Dash)   │      │  (SQL)  │      │  (DAG)   │      │ (Double RF)│
└─────────────┘      └─────────┘      └──────────┘      └────────────┘
Fonctionnalités Clés
Privacy by Design : Aucune donnée personnelle (PII) n'est stockée en clair. Les données sont hachées (SHA-256 + Sel) dès leur génération.

Temps Réel : Ingestion continue via Apache Kafka.

Orchestration : DAG Airflow quotidien gérant l'ingestion, l'entraînement et la validation.

Double Modèle IA : Prédiction de litige (Classification) et estimation du risque (Régression).

Lancement de l'infrastructure
bash
# 1. Lancer l'infrastructure via Docker
docker compose -f docker/docker-compose.yml up -d

# 2. Accès aux interfaces
NiFi : https://localhost:8443/nifi (admin / MotDePasseComplexe123!)
Airflow : http://localhost:8080 (admin / admin)
HBase UI : http://localhost:16010
HiveServer2 : localhost:10000
Dashboard : python dashboard/dashboard_yeewu.py (puis http://127.0.0.1:8050)
Métriques du Modèle (Machine Learning)
Notre système repose sur une architecture à double Random Forest :

Classifieur (Prédiction Litige Oui/Non) :

Accuracy : 0.8900 (89%)

F1-Score : 0.8358

Régresseur (Score de risque 0.0 à 1.0) :

RMSE : 0.0958

R² : 0.8685

Livrables
scripts/ : Codes Python (Génération, Kafka, ML, Contournement HBase).

dags/ : Pipeline d'orchestration MLOps (yeewu_dag.py).

docker/ : Infrastructure conteneurisée complète.

nifi_templates/ : Flux NiFi exporté (template_nifi.json).

dashboard/ : Application web interactive (dashboard_yeewu.py) et graphiques PNG générés.

rapport/ : Rapport final détaillé (rapport.pdf).