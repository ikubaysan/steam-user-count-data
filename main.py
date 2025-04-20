import sys
import csv
import requests
from typing import List, Tuple
from datetime import datetime

from typing import Union, Any


def fetch_chart_data(app_id: str) -> List[Tuple[int, int]]:
    """
    Fetch hourly or daily player count data from SteamCharts for a given app ID.

    Args:
        app_id (str): Steam App ID as a string.

    Returns:
        List[Tuple[int, int]]: A list of (timestamp, player_count) pairs.
    """
    url = f"https://steamcharts.com/app/{app_id}/chart-data.json"
    response = requests.get(url)
    response.raise_for_status()
    data: Union[dict, list] = response.json()

    if isinstance(data, list):
        return data  # Already a list of [timestamp, count]
    elif isinstance(data, dict) and "data" in data:
        return data["data"]
    else:
        raise ValueError("Unexpected data format from SteamCharts.")


from datetime import datetime, timezone

def format_data(data: List[Tuple[int, int]]) -> List[Tuple[int, str, int]]:
    """
    Format raw data by converting UNIX timestamps (ms or s) to UTC strings.
    """
    formatted: List[Tuple[int, str, int]] = []
    for timestamp, count in data:
        # Convert milliseconds to seconds if needed
        if timestamp > 1e12:
            timestamp //= 1000
        dt = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        formatted.append((timestamp, dt, count))
    return formatted



def save_to_csv(data: List[Tuple[int, str, int]], filename: str) -> None:
    """
    Save formatted data to a CSV file.

    Args:
        data (List[Tuple[int, str, int]]): Formatted data to write.
        filename (str): Path to the CSV output file.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Datetime (UTC)", "PlayerCount"])
        writer.writerows(data)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python steamcharts_to_csv.py <app_id>")
        sys.exit(1)

    app_id: str = sys.argv[1]

    try:
        raw_data = fetch_chart_data(app_id)
        formatted_data = format_data(raw_data)
        filename = f"steamcharts_{app_id}.csv"
        save_to_csv(formatted_data, filename)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
