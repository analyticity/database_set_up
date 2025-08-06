import csv

import pandas as pd
from psycopg2.extras import execute_values
from connection_to_db import CONN_BRNO


def calculate_update_count(row):
    try:
        delta = (pd.to_datetime(row['last_updated']) - pd.to_datetime(row['published_at'])).total_seconds()
        return int(max(1, round(delta / 120)))
    except:
        return 1


def insert_jams_from_csv(csv_path, conn):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []

        for row in reader:
            update_count = calculate_update_count(row)

            # Pripravenie dát pre INSERT
            record = (
                int(float(row['id'])) if row['id'] else None,
                int(row['uuid']),
                row['country'],
                row['city'],
                row['turn_type'],
                row['street'],
                row['end_node'] if row['end_node'] else None,
                row['start_node'] if row['start_node'] else None,
                int(row['road_type']) if row['road_type'] else None,
                row['blocking_alert_uuid'] if row['blocking_alert_uuid'] else None,

                int(row['jam_level_max']) if row['jam_level_max'] else None,
                float(row['jam_level_avg']) if row['jam_level_avg'] else None,

                int(row['speed_kmh_min']) if row['speed_kmh_min'] else None,
                float(row['speed_kmh_avg']) if row['speed_kmh_avg'] else None,

                int(row['jam_length_max']) if row['jam_length_max'] else None,
                float(row['jam_length_avg']) if row['jam_length_avg'] else None,

                float(row['speed_max']) if row['speed_max'] else None,
                float(row['speed_avg']) if row['speed_avg'] else None,

                int(row['delay_max']) if row['delay_max'] else None,
                float(row['delay_avg']) if row['delay_avg'] else None,

                update_count,

                row['jam_line'],  # WKT alebo hex WKB ako string

                row['published_at'],
                row['last_updated'] if row['last_updated'] else None,
                row['active'].lower() == 'true'
            )
            records.append(record)

    with conn.cursor() as cur:
        sql = """
        INSERT INTO jams (
            id, uuid, country, city, turn_type, street,
            end_node, start_node, road_type, blocking_alert_uuid,
            jam_level_max, jam_level_avg,
            speed_kmh_min, speed_kmh_avg,
            jam_length_max, jam_length_avg,
            speed_max, speed_avg,
            delay_max, delay_avg,
            update_count, jam_line,
            published_at, last_updated, active
        )
        VALUES %s
        ON CONFLICT (uuid, published_at) DO NOTHING
        """

        execute_values(cur, sql, records)
        conn.commit()
        print(f"{len(records)} záznamov vložených do 'jams'")


def insert_jams_simplified(csv_path, conn):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []

        for row in reader:
            record = (
                int(float(row['id'])) if row['id'] else None,
                int(row['uuid']),
                row['country'],
                row['city'],
                row['turn_type'] if row['turn_type'] else None,
                row['street'],
                row['end_node'] if row['end_node'] else None,
                row['start_node'] if row['start_node'] else None,
                int(row['road_type']) if row['road_type'] else None,
                row['blocking_alert_uuid'] if row['blocking_alert_uuid'] else None,

                int(row['jam_level']) if row['jam_level'] else None,
                float(row['jam_level']) if row['jam_level'] else None,

                int(row['speed_kmh']) if row['speed_kmh'] else None,
                float(row['speed_kmh']) if row['speed_kmh'] else None,

                int(row['jam_length']) if row['jam_length'] else None,
                float(row['jam_length']) if row['jam_length'] else None,

                float(row['speed']) if row['speed'] else None,
                float(row['speed']) if row['speed'] else None,

                int(row['delay']) if row['delay'] else None,
                float(row['delay']) if row['delay'] else None,

                1,  # update_count default

                row['jam_line'],

                row['published_at'],
                row['last_updated'] if row['last_updated'] else None,
                row['active'].lower() == 'true'
            )
            records.append(record)

    with conn.cursor() as cur:
        sql = """
        INSERT INTO jams (
            id, uuid, country, city, turn_type, street,
            end_node, start_node, road_type, blocking_alert_uuid,
            jam_level_max, jam_level_avg,
            speed_kmh_min, speed_kmh_avg,
            jam_length_max, jam_length_avg,
            speed_max, speed_avg,
            delay_max, delay_avg,
            update_count, jam_line,
            published_at, last_updated, active
        )
        VALUES %s
        ON CONFLICT (uuid, published_at) DO NOTHING
        """

        execute_values(cur, sql, records)
        conn.commit()
        print(f"{len(records)} záznamov vložených zo súboru {csv_path}")


if __name__ == '__main__':
    insert_jams_simplified("../data/brno_jams.csv", CONN_BRNO)