-- Création de la base de données
CREATE DATABASE IF NOT EXISTS yeewu_foncier;
USE yeewu_foncier;

-- Création de la table externe (les données seront stockées dans HDFS)
CREATE EXTERNAL TABLE IF NOT EXISTS parcelles_foncieres (
    parcelle_id STRING,
    region STRING,
    superficie_m2 DOUBLE,
    type_titre STRING,
    proprietaire_hash STRING,
    longitude DOUBLE,
    latitude DOUBLE,
    nombre_revendications INT,
    is_zone_litigieuse INT,
    risque_conflit_score DOUBLE,
    equipe_id STRING
)
PARTITIONED BY (date_ingestion STRING)
STORED AS PARQUET
LOCATION '/user/hive/warehouse/yeewu_foncier.db/parcelles_foncieres';