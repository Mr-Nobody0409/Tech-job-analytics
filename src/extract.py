import requests
import json

from pathlib import Path
from datetime import datetime


def extract_jobs():

    url = "https://remotive.com/api/remote-jobs"

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def save_raw_data(data):

    raw_directory = Path("data/raw")

    raw_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    today = datetime.now().strftime("%Y-%m-%d")

    file_path = (
        raw_directory /
        f"jobs_{today}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

    print(
        f"Raw data saved: {file_path}"
    )

    return file_path


def main():

    data = extract_jobs()

    return save_raw_data(data)


if __name__ == "__main__":

    main()