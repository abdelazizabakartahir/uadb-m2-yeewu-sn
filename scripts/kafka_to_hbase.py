import json
from kafka import KafkaConsumer
import happybase
import time

# ==============================================================================
# CONTEXTE TECHNIQUE 
# ==============================================================================
# NiFi 2.x a supprimé les processeurs HBase natifs (vulnérabilités Protobuf).
# Ce script Python contourne ce problème en faisant le pont entre Kafka et HBase
# en utilisant la librairie HappyBase (qui passe par le service Thrift de HBase).

# Configuration (Ports externes pour exécution depuis la machine hôte)
KAFKA_TOPIC = "yeewu_foncier_topic"
KAFKA_SERVER = "localhost:29092" 
HBASE_HOST = "localhost"
HBASE_PORT = 9090 # Port Thrift obligatoire pour HappyBase
TABLE_NAME = "foncier_parcelles"

def process_to_hbase():
    """
    Consomme les messages Kafka en temps réel et les insère dans HBase.
    """
    print("[*] Connexion à HBase via Thrift (Port 9090)...")
    try:
        connection = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT)
        connection.open()
        table = connection.table(TABLE_NAME)
        print(f"[OK] Connecté à la table HBase : {TABLE_NAME}")
    except Exception as e:
        print(f"[!] Erreur HBase (Vérifiez que le Thrift est lancé) : {e}")
        return

    print("[*] Écoute du topic Kafka...")
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_SERVER],
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        data = message.value
        
        # HBase exige que les clés (row keys) et valeurs soient en format binaire (bytes)
        parcelle_id = data['parcelle_id'].encode()
        
        # Formatage des colonnes (Famille:Qualificateur)
        hbase_data = {
            b'data:region': str(data['region']).encode(),
            b'data:superficie_m2': str(data['superficie_m2']).encode(),
            b'data:risque_conflit_score': str(data['risque_conflit_score']).encode(),
            b'data:is_zone_litigieuse': str(data['is_zone_litigieuse']).encode(),
            b'data:type_titre': str(data['type_titre']).encode()
        }
        
        try:
            table.put(parcelle_id, hbase_data)
            print(f"[STREAMING] Parcelle {data['parcelle_id']} insérée dans HBase.")
        except Exception as e:
            print(f"[!] Erreur d'insertion : {e}")

if __name__ == "__main__":
    process_to_hbase()