import json
import time
import requests
from datetime import datetime
import os

keys = ["JMK", "ORP_MOST"]

output_directories_dict = {"JMK": "./data_JMK/",
                           "ORP_MOST": "./data_ORP_MOST/"}

## Add link to Waze for cities endpoints
urls_json_dict = {"JMK": "data_jmk",
                  "ORP_MOST": "data_orp_most"}


def download_json(key):
    try:
        response = requests.get(urls_json_dict[key])
        response.raise_for_status()

        # Parse the JSON content to ensure it's valid
        json_data = response.json()

        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data_{key}_{timestamp}.json"

        # Ensure the output directory exists
        if not os.path.exists(output_directories_dict[key]):
            os.makedirs(output_directories_dict[key])

        # Save the JSON content as a file
        with open(os.path.join(output_directories_dict[key], filename), "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4)  # Save JSON with indentation for readability

        print(f"File saved: {filename}")
    except requests.RequestException as e:
        print(f"Failed to download the JSON file: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON content: {e}")


if __name__ == '__main__':
    for key in keys:
        if not os.path.exists(output_directories_dict[key]):
            os.makedirs(output_directories_dict[key])

    try:
        while True:
            download_json(keys[0])
            download_json(keys[1])
            time.sleep(120)  # Wait for 2 minutes (120 seconds)
    except KeyboardInterrupt:
        print("Program terminated by user.")
