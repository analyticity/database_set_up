import csv
import pandas as pd
from psycopg2.extras import execute_values

from connection_to_db import CONN_BRNO


def insert_alerts_from_csv(csv_path, conn):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []

        for row in reader:
            try:
                record = (
                    row['uuid'],
                    row['country'],
                    row['city'],
                    row['type'],
                    row['subtype'],
                    row['street'],
                    int(row['report_rating']) if row['report_rating'] else None,
                    int(row['confidence']) if row['confidence'] else None,
                    int(row['reliability']) if row['reliability'] else None,
                    int(row['road_type']) if row['road_type'] else None,
                    int(row['magvar']) if row['magvar'] else None,
                    row['report_by_municipality_user'].lower() == 'true' if row['report_by_municipality_user'] else None,
                    row['report_description'] if row['report_description'] else None,
                    row['location'],  # HEX WKB bod ako string
                    row['published_at'],
                    row['last_updated'] if row['last_updated'] else None,
                    row['active'].lower() == 'true' if row['active'] else False
                )
                records.append(record)
            except Exception as e:
                print(f"Chyba pri spracovaní riadku: {row}\n{e}")

    with conn.cursor() as cur:
        sql = """
        INSERT INTO alerts (
            uuid, country, city, type, subtype, street,
            report_rating, confidence, reliability,
            road_type, magvar, report_by_municipality_user,
            report_description, location,
            published_at, last_updated, active
        )
        VALUES %s
        ON CONFLICT (uuid, published_at) DO NOTHING
        """

        execute_values(cur, sql, records)
        conn.commit()
        print(f"{len(records)} alertov vložených zo súboru {csv_path}")


if __name__ == '__main__':
    insert_alerts_from_csv("../data/brno_alerts.csv", CONN_BRNO)