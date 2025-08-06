CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabuľka registrovaných databáz
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,              -- napr. 'brno'
    db_host TEXT NOT NULL,                  -- docker host napr. 'db_brno'
    db_port_external INTEGER NOT NULL,  -- port dostupný zvonku (napr. 5433)
    db_port_internal INTEGER NOT NULL DEFAULT 5432, -- port vnútri kontajnera (zvyčajne 5432)
    db_name TEXT NOT NULL,
    db_user TEXT NOT NULL,
    db_password TEXT NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    coverage_area GEOMETRY(POLYGON, 4326),  -- územie pokrytia (napr. Brno, JMK)
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO data_sources (name, db_host, db_port_external, db_port_internal, db_name, db_user, db_password, description, coverage_area)
VALUES
(
  'brno',
  'db_brno',
  5433,
 5432,
  'traffic_brno',
  'analyticity_admin',
  'admin',
  'Dátová DB pre Brno',
  ST_GeomFromText('POLYGON((16.5 49.1, 16.7 49.1, 16.7 49.3, 16.5 49.3, 16.5 49.1))', 4326)
),
(
  'jmk',
  'db_jmk',
  5434,
 5432,
  'traffic_jmk',
  'analyticity_admin',
  'admin',
  'Dátová DB pre JMK',
  ST_GeomFromText('POLYGON((16.2 48.8, 17.5 48.8, 17.5 49.6, 16.2 49.6, 16.2 48.8))', 4326)
),
(
  'orp_most',
  'db_orp_most',
  5435,
 5432,
  'traffic_orp_most',
  'analyticity_admin',
  'admin',
  'Dátová DB pre ORP Most',
  ST_GeomFromText('POLYGON((13.5 50.5, 13.7 50.5, 13.7 50.7, 13.5 50.7, 13.5 50.5))', 4326)
)
ON CONFLICT DO NOTHING;
