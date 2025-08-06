import os
from datetime import datetime
import requests
import time

from dotenv import load_dotenv
from psycopg2.extras import execute_values

from connection_to_db import CONN_BRNO, CONN_JMK, CONN_ORP_MOST
from queries import GET_ACTIVE_JAM, UPDATE_EXISTING_JAM, INSERT_NEW_JAM, INSERT_SEGMENTS, INSERT_NEW_ALERT

load_dotenv()


def to_linestring_wkt(line_points):
    return "LINESTRING(" + ", ".join(f"{pt['x']} {pt['y']}" for pt in line_points) + ")"


def to_point_wkt(location_dict):
    return f"POINT({location_dict['x']} {location_dict['y']})"


def get_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def deactivate_stale_records(conn, minutes=3):
    cur = conn.cursor()

    cur.execute("""
        UPDATE alerts
        SET active = FALSE
        WHERE active = TRUE AND last_updated < now() - interval %s;
    """, (f"{minutes} minutes",))

    cur.execute("""
        UPDATE jams
        SET active = FALSE
        WHERE active = TRUE AND last_updated < now() - interval %s;
    """, (f"{minutes} minutes",))

    conn.commit()


def process_jams(conn, jams):
    """
    :param jams: list of jam dictionaries filtered for Brno
    :param conn: dict with db connection info {dbname, user, password, host, port}
    """
    cur = conn.cursor()
    now = datetime.utcnow()

    for jam in jams:
        uuid = jam["uuid"]
        published_at = datetime.utcfromtimestamp(jam["pubMillis"] / 1000)
        jam_line = to_linestring_wkt(jam["line"])

        cur.execute(GET_ACTIVE_JAM, (uuid, published_at))
        existing = cur.fetchone()

        if existing:
            (
                jam_id, update_count, jam_level_avg, jam_level_max,
                speed_kmh_avg, speed_kmh_min,
                jam_length_avg, jam_length_max,
                speed_avg, speed_max,
                delay_avg, delay_max
            ) = existing

            new_uc = update_count + 1

            # prepočet vážených priemerov
            jam_level_avg = (jam_level_avg * update_count + jam["level"]) / new_uc
            speed_kmh_avg = (speed_kmh_avg * update_count + jam["speedKMH"]) / new_uc
            jam_length_avg = (jam_length_avg * update_count + jam["length"]) / new_uc
            speed_avg = (speed_avg * update_count + jam["speed"]) / new_uc
            delay_avg = (delay_avg * update_count + jam["delay"]) / new_uc

            cur.execute(UPDATE_EXISTING_JAM, (
                jam_level_avg, jam["level"],
                speed_kmh_avg, jam["speedKMH"],
                jam_length_avg, jam["length"],
                speed_avg, jam["speed"],
                delay_avg, jam["delay"],
                new_uc, now, uuid
            ))

        else:
            jam_data = {
                "id": jam["id"],
                "uuid": uuid,
                "country": jam.get("country"),
                "city": jam.get("city"),
                "turn_type": jam.get("turnType"),
                "street": jam.get("street"),
                "end_node": jam.get("endNode"),
                "start_node": None,  # prázdne v tvojej štruktúre
                "road_type": jam.get("roadType"),
                "blocking_alert_uuid": jam.get("blockingAlertUuid"),
                "jam_level_max": jam["level"],
                "jam_level_avg": jam["level"],
                "speed_kmh_min": jam["speedKMH"],
                "speed_kmh_avg": jam["speedKMH"],
                "jam_length_max": jam["length"],
                "jam_length_avg": jam["length"],
                "speed_max": jam["speed"],
                "speed_avg": jam["speed"],
                "delay_max": jam["delay"],
                "delay_avg": jam["delay"],
                "update_count": 1,
                "jam_line": jam_line,
                "published_at": published_at,
                "last_updated": now,
                "active": True
            }

            cur.execute(INSERT_NEW_JAM, jam_data)

        # Vloženie segmentov
        segments = jam.get("segments", [])
        if segments:
            segment_values = [
                (
                    jam["id"],
                    seg["fromNode"],
                    seg["toNode"],
                    seg["ID"],
                    seg["isForward"]
                ) for seg in segments
            ]
            execute_values(cur, INSERT_SEGMENTS, segment_values)

    conn.commit()


def process_alerts(conn, alerts):
    """
    :param alerts: list of alerts dicts filtered for Brno
    :param conn: dict with db connection info
    """
    cur = conn.cursor()
    now = datetime.utcnow()

    for alert in alerts_brno:
        uuid = alert["uuid"]
        published_at = datetime.utcfromtimestamp(alert["pubMillis"] / 1000)

        alert_data = {
            "uuid": uuid,
            "country": alert.get("country"),
            "city": alert.get("city", "Brno"),
            "type": alert.get("type"),
            "subtype": alert.get("subtype"),
            "street": alert.get("street"),
            "report_rating": alert.get("reportRating"),
            "confidence": alert.get("confidence"),
            "reliability": alert.get("reliability"),
            "road_type": alert.get("roadType"),
            "magvar": alert.get("magvar"),
            "report_by_municipality_user": alert.get("reportByMunicipalityUser", "false").lower() == "true",
            "report_description": alert.get("reportDescription", None),
            "location": to_point_wkt(alert["location"]),
            "published_at": published_at,
            "last_updated": now,
            "active": True
        }

        cur.execute(INSERT_NEW_ALERT, alert_data)

    conn.commit()


def main_loop(conn, alerts, jams):
    process_jams(conn, jams)
    process_alerts(conn, alerts)


if __name__ == "__main__":
    threshold = 5
    count = 0
    while True:
        # BRNO A JMK
        data = get_data(os.getenv("DATA_JMK"))
        alerts_brno_jmk = data.get("alerts", [])
        jams_brno_jmk = data.get("jams", [])

        # for Brno, filter only for city Brno
        alerts_brno = [alert for alert in alerts_brno_jmk if alert.get('city') == 'Brno']
        jams_brno = [jam for jam in jams_brno_jmk if jam.get('city') == 'Brno']
        print(f"[{datetime.now()}] INGESTING DATA FOR BRNO")
        main_loop(CONN_BRNO, alerts_brno, jams_brno)
        print(f"="*75)

        # for JMK - everything but city Brno
        alerts_jmk = [alert for alert in alerts_brno_jmk if alert.get('city') != 'Brno']
        jams_jmk = [jam for jam in jams_brno_jmk if jam.get('city') != 'Brno']
        print(f"[{datetime.now()}] INGESTING DATA FOR JMK")
        main_loop(CONN_JMK, alerts_jmk, jams_jmk)
        print(f"="*75)

        # ORP MOST
        data = get_data(os.getenv("DATA_ORP_MOST"))
        alerts_orp_most = data.get("alerts", [])
        jams_orp_most = data.get("jams", [])
        print(f"[{datetime.now()}] INGESTING DATA FOR ORP MOST")
        main_loop(CONN_ORP_MOST, alerts_orp_most, jams_orp_most)
        print(f"="*75)

        if count >= threshold:
            print("🧹  → Running cleanup: deactivating old alerts/jams...")
            deactivate_stale_records(CONN_BRNO)
            deactivate_stale_records(CONN_JMK)
            deactivate_stale_records(CONN_ORP_MOST)
            count = 0
            print("🧹 → Cleanup done.")

        else:
            print(f"🧹 → Skipping cleanup (run {count}/{threshold})")
            count += 1

        time.sleep(120)
