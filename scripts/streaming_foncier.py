import json
from kafka import KafkaConsumer
import hashlib

# Configuration
KAFKA_TOPIC = "yeewu_foncier_topic"
KAFKA_SERVER = "localhost:9092"

def anonymiser_donnees(record):
    """
    Couche Privacy (Temps Réel) : Si un nom de propriétaire fuit dans le flux,
    ce script le supprime et le remplace par un hash.
    """
    if 'proprietaire' in record:
        record['proprietaire_hash'] = hashlib.sha256(record['proprietaire'].encode()).hexdigest()
        del record['proprietaire'] # Suppression définitive de la PII
    return record

def demarrer_streaming():
    print(f"[*] Démarrage du consommateur Kafka sur le topic : {KAFKA_TOPIC}")
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None
        )

        for message in consumer:
            raw_data = message.value
            secure_data = anonymiser_donnees(raw_data)
            print(f"[STREAMING SECURISE] Donnée traitée : {secure_data}")
            # Ici, on pourrait insérer dans HBase ou HDFS
    except Exception as e:
        print(f"[!] Erreur de connexion au broker Kafka : {e}")

if __name__ == "__main__":
    demarrer_streaming()