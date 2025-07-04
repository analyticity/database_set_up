import json
import glob
import os

# Folder where JSON files are located
json_folder = "./data_JMK/"  # <-- change to your folder

# Attributes to track
tracked_alert_fields = [
    "country", "city", "reportRating", "confidence", "reliability",
    "type", "subtype", "street", "roadType", "location", "pubMillis"
]

tracked_jam_fields = [
    "country", "level", "city", "speedKMH", "length", "delay",
    "street", "roadType", "line", "pubMillis"
]

# Historical storage
previous_alerts = {}
previous_jams = {}

# Get files in order (assuming file names include time info or order properly)
json_files = sorted(glob.glob(os.path.join(json_folder, "*.json")))

for file_path in json_files:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    timestamp = os.path.basename(file_path)

    # ---- Alerts ----
    for alert in data.get("alerts", []):
        uuid = alert["uuid"]
        current_state = {k: alert.get(k) for k in tracked_alert_fields}

        if uuid in previous_alerts:
            prev_state = previous_alerts[uuid]
            if current_state != prev_state:
                print(f"\n[ALERT CHANGE] {uuid} at {timestamp}")
                for key in tracked_alert_fields:
                    if prev_state.get(key) != current_state.get(key):
                        print(f" - {key}: {prev_state.get(key)} → {current_state.get(key)}")
        previous_alerts[uuid] = current_state

    # ---- Jams ----
    for jam in data.get("jams", []):
        uuid = jam["uuid"]
        current_state = {k: jam.get(k) for k in tracked_jam_fields}

        if uuid in previous_jams:
            prev_state = previous_jams[uuid]
            if current_state != prev_state:
                print(f"\n[JAM CHANGE] {uuid} at {timestamp}")
                for key in tracked_jam_fields:
                    if prev_state.get(key) != current_state.get(key):
                        print(f" - {key}: {prev_state.get(key)} → {current_state.get(key)}")
        previous_jams[uuid] = current_state
