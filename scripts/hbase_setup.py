import happybase

# ==============================================================================
# INITIALISATION DE LA BASE DE DONNÉES HBASE
# ==============================================================================

try:
    # Connexion via Thrift (port 9090 exposé par le conteneur Docker)
    connection = happybase.Connection(host='localhost', port=9090)
    connection.open()

    table_name = 'foncier_parcelles'
    column_family = 'data'

    # Vérification de l'existence de la table
    tables = [t.decode('utf-8') for t in connection.tables()]
    if table_name not in tables:
        connection.create_table(
            table_name,
            {column_family: dict(max_versions=1)} # On ne garde que la dernière version
        )
        print(f"[SUCCESS] Table '{table_name}' créée.")
    else:
        print(f"[INFO] La table '{table_name}' existe déjà.")

    # Insertion d'un exemple pour tester
    table = connection.table(table_name)
    exemple_donnee = {
        b'data:region': b'Dakar',
        b'data:superficie_m2': b'1500.0',
        b'data:risque_conflit_score': b'0.75',
        b'data:is_zone_litigieuse': b'1'
    }
    table.put(b'SN-DAK-00001', exemple_donnee)
    print("[INFO] Donnée d'exemple insérée et vérifiée.")

    connection.close()
except Exception as e:
    print(f"[!] Erreur lors de l'initialisation de HBase : {e}")