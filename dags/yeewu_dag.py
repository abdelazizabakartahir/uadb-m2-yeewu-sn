from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator
import os

# ==============================================================================
# CONFIGURATION GÉNÉRALE DU DAG
# ==============================================================================
default_args = {
    'owner': 'equipe07_yeewu',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1, # En cas d'échec, on réessaie 1 fois
    'retry_delay': timedelta(minutes=5),
}

def check_data_availability():
    """
    Fonction de branchement (Branching) : Vérifie si le fichier de données
    d'entraînement existe déjà dans le conteneur Airflow.
    - Si oui : on passe directement à l'entraînement.
    - Si non : on lance d'abord le simulateur de données.
    """
    # Le volume ./data de la machine hôte est monté sur /opt/airflow/data
    data_path = "/opt/airflow/data/foncier_simulated.csv"
    if os.path.exists(data_path):
        return 'train_ml_model'
    return 'generate_fresh_data'

# ==============================================================================
# DÉFINITION DU PIPELINE (DAG)
# ==============================================================================
with DAG(
    'yeewu_sn_pipeline_mlops',
    default_args=default_args,
    description='Pipeline MLOps Yeewu-SN Intelligence Foncière',
    schedule_interval='@daily', # Le pipeline tourne tous les jours à minuit
    catchup=False # Ne pas exécuter les runs passés (on part de la date d'aujourd'hui)
) as dag:

    # 1. Tâche de décision (Branchement)
    branch_task = BranchPythonOperator(
        task_id='check_data_branch',
        python_callable=check_data_availability
    )

    # 2. Tâche A : Générer les données (si absentes)
    gen_data_task = BashOperator(
        task_id='generate_fresh_data',
        bash_command='cd /opt/airflow/scripts && python3 kafka_producer_foncier.py'
    )

    # 3. Tâche B : Entraîner le modèle ML
    train_task = BashOperator(
        task_id='train_ml_model',
        bash_command='cd /opt/airflow/scripts && python3 train_conflit.py',
        # 'none_failed_min_one' permet à cette tâche de s'exécuter même si 
        # 'generate_fresh_data' a été sautée (SKIPPED) par le branchement.
        trigger_rule='none_failed' 
    )

    # --- DÉFINITION DU FLUX D'EXÉCUTION ---
    branch_task >> [gen_data_task, train_task]
    gen_data_task >> train_task