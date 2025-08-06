import csv
from psycopg2.extras import execute_values

from connection_to_db import CONN_BRNO


def insert_nehody_from_csv(csv_path, conn):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []

        for row in reader:
            try:
                record = (
                    int(row['p1']),
                    row['p36'],
                    row['p37'],
                    row['p2a'],
                    int(row['p2b']) if row['p2b'] else None,
                    int(row['p6']) if row['p6'] else None,
                    int(row['p7']) if row['p7'] else None,
                    int(row['p8']) if row['p8'] else None,
                    int(row['p9']) if row['p9'] else None,
                    int(row['p10']) if row['p10'] else None,
                    int(row['p11']) if row['p11'] else None,
                    int(row['p12']) if row['p12'] else None,
                    int(row['p13a']) if row['p13a'] else None,
                    int(row['p13b']) if row['p13b'] else None,
                    int(row['p13c']) if row['p13c'] else None,
                    int(row['p14']) if row['p14'] else None,
                    int(row['p15']) if row['p15'] else None,
                    int(row['p16']) if row['p16'] else None,
                    int(row['p17']) if row['p17'] else None,
                    int(row['p18']) if row['p18'] else None,
                    int(row['p19']) if row['p19'] else None,
                    int(row['p20']) if row['p20'] else None,
                    int(row['p21']) if row['p21'] else None,
                    int(row['p22']) if row['p22'] else None,
                    int(row['p23']) if row['p23'] else None,
                    int(row['p24']) if row['p24'] else None,
                    int(row['p27']) if row['p27'] else None,
                    int(row['p28']) if row['p28'] else None,
                    int(row['p34']) if row['p34'] else None,
                    int(row['p35']) if row['p35'] else None,
                    row['p39'] if row['p39'] else None,
                    int(row['p44']) if row['p44'] else None,
                    int(row['p45a']) if row['p45a'] else None,
                    row['p47'] if row['p47'] else None,
                    int(row['p48a']) if row['p48a'] else None,
                    int(row['p49']) if row['p49'] else None,
                    int(row['p50a']) if row['p50a'] else None,
                    int(row['p50b']) if row['p50b'] else None,
                    int(row['p51']) if row['p51'] else None,
                    int(row['p52']) if row['p52'] else None,
                    int(row['p53']) if row['p53'] else None,
                    int(row['p55a']) if row['p55a'] else None,
                    int(row['p57']) if row['p57'] else None,
                    int(row['p58']) if row['p58'] else None,
                    int(row['p5a']) if row['p5a'] else None,
                    int(row['p8a']) if row['p8a'] else None,
                    int(row['p11a']) if row['p11a'] else None,
                    float(row['x']) if row['x'] else None,
                    float(row['y']) if row['y'] else None,
                    row['geom'],
                    row['geog']
                )
                records.append(record)
            except Exception as e:
                print(f"Chyba pri spracovaní riadku:\n{row}\n{e}")

    with conn.cursor() as cur:
        sql = """
        INSERT INTO nehody (
            p1, p36, p37, p2a, p2b, p6, p7, p8, p9, p10, p11, p12,
            p13a, p13b, p13c, p14, p15, p16, p17, p18, p19, p20, p21,
            p22, p23, p24, p27, p28, p34, p35, p39, p44, p45a, p47,
            p48a, p49, p50a, p50b, p51, p52, p53, p55a, p57, p58,
            p5a, p8a, p11a, x, y, geom, geog
        )
        VALUES %s
        ON CONFLICT (p1) DO NOTHING
        """

        execute_values(cur, sql, records)
        conn.commit()
        print(f"{len(records)} nehôd vložených zo súboru {csv_path}")


if __name__ == "__main__":
    insert_nehody_from_csv("../data/brno_nehody.csv", CONN_BRNO)
