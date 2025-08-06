import os
import json
import pandas as pd
import re
import logging
from datetime import datetime, timedelta

# === Constants ===
DATA_DIR = "data_JMK"
OUTPUT_DIR = "outputs_full"
FILENAME_PATTERN = re.compile(r"data_JMK_(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})")

# Configure logging
LOG_FILE = "loading_data_to_one_file.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# In-memory store
data_store = {"alerts": {}, "jams": {}}


def extract_timestamp_from_filename(filename):
    """
    Extracts timestamp from a filename based on the expected pattern.

    @param filename: name of the file
    @return: datetime object representing the timestamp
    """
    match = FILENAME_PATTERN.search(filename)
    if not match:
        return None
    date, hour, minute, second = match.groups()
    return datetime.strptime(f"{date} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")


def load_json_file(filepath):
    """
    Loads JSON content from a file.

    @param filepath: full path to the file
    @return: parsed JSON dictionary
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def update_alert(alert, file_timestamp_millis):
    """
    Updates or creates an alert record in memory.

    @param alert: alert data from the current file
    @param file_timestamp_millis: timestamp in milliseconds from file name
    """
    uuid = alert["uuid"]
    existing = data_store["alerts"].get(uuid)

    if existing:
        for field in ["country", "city", "type", "subtype", "street", "reportDescription"]:
            new_val = alert.get(field, "")
            old_val = existing.get(field, "")
            if new_val != old_val:
                logging.info(f"ALERT uuid={uuid} field={field}: {old_val} -> {new_val}")
            existing[field] = new_val

        for field in ["reportRating", "confidence", "reliability"]:
            new_val = alert.get(field, -1)
            if new_val > existing.get(field, -1):
                logging.info(f"ALERT uuid={uuid} field={field}: {existing[field]} -> {new_val}")
                existing[field] = new_val

        for field in ["roadType", "magvar"]:
            new_val = alert.get(field, -1)
            if new_val != existing.get(field, -1):
                logging.info(f"ALERT uuid={uuid} field={field}: {existing[field]} -> {new_val}")
            existing[field] = new_val

        new_loc = alert.get("location")
        if new_loc != existing.get("location"):
            logging.info(f"ALERT uuid={uuid} location updated")
            existing["location"] = new_loc

        existing["lastupdated"] = file_timestamp_millis
        existing["finished"] = False
    else:
        logging.info(f"ALERT uuid={uuid} added as new")
        data_store["alerts"][uuid] = {
            "uuid": uuid,
            "country": alert.get("country", ""),
            "city": alert.get("city", ""),
            "reportRating": alert.get("reportRating", -1),
            "reportByMunicipalityUser": alert.get("reportByMunicipalityUser", ""),
            "confidence": alert.get("confidence", -1),
            "reliability": alert.get("reliability", -1),
            "type": alert.get("type", ""),
            "subtype": alert.get("subtype", ""),
            "roadType": alert.get("roadType", -1),
            "magvar": alert.get("magvar", -1),
            "street": alert.get("street", ""),
            "reportDescription": alert.get("reportDescription", ""),
            "location": alert.get("location", None),
            "pubMillis": alert.get("pubMillis", file_timestamp_millis),
            "lastupdated": alert.get("pubMillis", file_timestamp_millis),
            ""
            "": False
        }


def update_jam_metrics(existing, jam, uc):
    """
    Updates metric fields in a jam (max, min, avg calculations).

    @param existing: existing jam record
    @param jam: new jam data
    @param uc: update count
    """
    def update(field, kind):
        value = jam.get(field, -1)
        if kind == "max":
            existing[f"{field}_max"] = max(existing.get(f"{field}_max", -1), value)
        elif kind == "min":
            existing[f"{field}_min"] = min(existing.get(f"{field}_min", float("inf")), value)
        existing[f"{field}_sum"] = existing.get(f"{field}_sum", 0) + value
        existing[f"{field}_avg"] = existing[f"{field}_sum"] / uc

    update("level", "max")
    update("speedKMH", "min")
    update("length", "max")
    update("speed", "max")
    update("delay", "max")


def update_jam(jam, file_timestamp_millis):
    """
    Updates or creates a jam record in memory.

    @param jam: jam data from the current file
    @param file_timestamp_millis: timestamp in milliseconds from file name
    """
    jam_id = jam["id"]
    existing = data_store["jams"].get(jam_id)

    if existing:
        existing["updateCount"] += 1
        uc = existing["updateCount"]

        for field in ["street", "blockingAlertUuid", "roadType", "startNode", "endNode"]:
            new_val = jam.get(field, "")
            if new_val != existing.get(field, ""):
                logging.info(f"JAM id={jam_id} field={field}: {existing[field]} -> {new_val}")
            existing[field] = new_val

        if len(jam.get("line", [])) > len(existing.get("line", [])):
            logging.info(f"JAM id={jam_id} line updated: longer line")
            existing["line"] = jam.get("line", [])

        new_segments = jam.get("segments", [])
        old_segments = existing.get("segments", [])
        old_ids = {s.get("ID") for s in old_segments}
        added = [s for s in new_segments if s.get("ID") not in old_ids]
        if added:
            logging.info(f"JAM id={jam_id} added {len(added)} new segments")
            old_segments.extend(added)
        existing["segments"] = old_segments

        update_jam_metrics(existing, jam, uc)

        existing["lastupdated"] = file_timestamp_millis
        existing["finished"] = False
    else:
        logging.info(f"JAM id={jam_id} added as new")
        data_store["jams"][jam_id] = {
            "id": jam_id,
            "uuid": jam.get("uuid", ""),
            "country": jam.get("country", ""),
            "city": jam.get("city", ""),
            "turnType": jam.get("turnType", ""),
            "street": jam.get("street", ""),
            "blockingAlertUuid": jam.get("blockingAlertUuid", ""),
            "roadType": jam.get("roadType", ""),
            "startNode": jam.get("startNode", ""),
            "endNode": jam.get("endNode", ""),
            "line": jam.get("line", []),
            "segments": jam.get("segments", []),
            "updateCount": 1,
            "pubMillis": jam.get("pubMillis", file_timestamp_millis),
            "lastupdated": jam.get("pubMillis", file_timestamp_millis),
            "finished": False,
            "level_max": jam.get("level", -1),
            "level_sum": jam.get("level", -1),
            "level_avg": jam.get("level", -1),
            "speedKMH_min": jam.get("speedKMH", -1),
            "speedKMH_sum": jam.get("speedKMH", -1),
            "speedKMH_avg": jam.get("speedKMH", -1),
            "length_max": jam.get("length", -1),
            "length_sum": jam.get("length", -1),
            "length_avg": jam.get("length", -1),
            "speed_max": jam.get("speed", -1),
            "speed_sum": jam.get("speed", -1),
            "speed_avg": jam.get("speed", -1),
            "delay_max": jam.get("delay", -1),
            "delay_sum": jam.get("delay", -1),
            "delay_avg": jam.get("delay", -1)
        }


def process_file(filepath):
    """
    Processes a single JSON file, updating alerts and jams in memory.

    @param filepath: path to the JSON file
    """
    timestamp = extract_timestamp_from_filename(os.path.basename(filepath))
    if not timestamp:
        return

    file_timestamp_millis = int(timestamp.timestamp() * 1000)
    data = load_json_file(filepath)

    for alert in data.get("alerts", []):
        update_alert(alert, file_timestamp_millis)

    for jam in data.get("jams", []):
        update_jam(jam, file_timestamp_millis)


def handle_missing_files(file_timestamps):
    """
    Handles large gaps between files to mark jams/alerts as finished.

    @param file_timestamps: list of file timestamps (datetime objects)
    """
    file_timestamps.sort()
    for i in range(len(file_timestamps) - 1):
        gap = file_timestamps[i + 1] - file_timestamps[i]
        if gap > timedelta(hours=1):
            last_ts_millis = int(file_timestamps[i].timestamp() * 1000)
            for alert in data_store["alerts"].values():
                if not alert["finished"]:
                    alert["lastupdated"] = last_ts_millis
            for jam in data_store["jams"].values():
                if not jam["finished"]:
                    jam["lastupdated"] = last_ts_millis


def save_data():
    """
    Saves alerts and jams filtered by city to JSON output files.
    """
    alerts_df = pd.DataFrame(data_store["alerts"].values())
    jams_df = pd.DataFrame(data_store["jams"].values())

    alerts_df = alerts_df[alerts_df["city"] == "Brno"]
    jams_df = jams_df[jams_df["city"] == "Brno"]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    alerts_df.to_json(os.path.join(OUTPUT_DIR, "alerts_full.json"), orient="records", indent=4)
    jams_df.to_json(os.path.join(OUTPUT_DIR, "jams_full.json"), orient="records", indent=4)


def main():
    """
    Main script execution. Processes files, handles gaps and saves output.
    """
    timestamps = []
    for filename in sorted(os.listdir(DATA_DIR)):
        if filename.endswith(".json") and FILENAME_PATTERN.match(filename):
            fullpath = os.path.join(DATA_DIR, filename)
            ts = extract_timestamp_from_filename(filename)
            if ts:
                timestamps.append(ts)
                process_file(fullpath)

    handle_missing_files(timestamps)
    save_data()


if __name__ == "__main__":
    main()
