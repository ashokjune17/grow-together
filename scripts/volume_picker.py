import time
import requests
import json
import os
from data_entry import DataEntry
from datetime import datetime

# Get the current date with the month in abbreviated form (e.g., 'aug', 'july')
current_date = datetime.now().strftime('%A-%d-%b').lower()

url = "https://scanner.tradingview.com/india/scan"

volume_in_file_path = 'input\volume.json'
volume_out_file_path = rf"output\volume_{current_date}.json"

if os.path.exists(volume_in_file_path):
    with open(volume_in_file_path, 'r') as file:
        payload = json.load(file)
else:
    raise FileNotFoundError(f"The file '{volume_in_file_path}' does not exist.")

# Initialize the dictionary to store the map
data_map = {}

# Define the mapping for the 'd' values
keys = [
    "name", "change", "close", "price_52_week_high", "high_all", "sector",
    "recommendation_mark", "rsi", "adx", "volume", "average_volume_10d_calc",
    "market_cap_basic", "cci20", "wr", "macd_day", "macd_s_day", "macd_week", "macd_s_week"
]

def main():
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        for entry in data['data']:
            symbol = entry['s'].replace("NSE:", "")
            values = entry['d']

            if len(values) != len(keys):
                print(f"Skipping entry for {symbol} due to unexpected data length: {values}")
                continue

            if symbol in data_map:
                data_map[symbol].count += 1
            else:
                data_map[symbol] = DataEntry(
                    name=values[0],
                    change=values[1],
                    close=values[2],
                    price_52_week_high=values[3],
                    high_all=values[4],
                    sector=values[5],
                    recommendation_mark=values[6],
                    rsi=values[7],
                    adx=values[8],
                    volume=values[9],
                    average_volume_10d_calc=values[10],
                    market_cap_basic=values[11],
                    cci20=values[12],
                    wr=values[13],
                    macd_day=values[14] - values[15],
                    macd_week=values[16] - values[17],
                    count=1,
                    swingTradeScore=(
                        (0.2 * values[1]) +
                        (0.2 * values[7]) +
                        (0.2 * values[8]) +
                        (0.15 * (values[9] / values[10])) +
                        (0.15 * values[12]) +
                        (0.1 * ((values[14] + values[16]) / 2))
                    )
                )
                
        for key, value in data_map.items():
            print(f"{key}")
       

        with open(volume_out_file_path, 'w', encoding='utf-8') as file:
            json.dump({
                key: {
                    'name': value.name,
                    'change': value.change,
                    'close': value.close,
                    'price_52_week_high': value.price_52_week_high,
                    'high_all': value.high_all,
                    'sector': value.sector,
                    'Analyst': value.recommendation_mark,
                    'rsi': value.rsi,
                    'adx': value.adx,
                    'volume': value.volume,
                    'average_volume_10d_calc': value.average_volume_10d_calc,
                    'market_cap_basic': value.market_cap_basic,
                    'cci20': value.cci20,
                    'wr': value.wr,
                    'macd_day': value.macd_day,
                    'macd_week': value.macd_week,
                    'count': value.count,
                    'swingTradeScore': value.swingTradeScore
                } for key, value in data_map.items()
            }, file, indent=4)

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}. Retrying after 60 seconds.")
        time.sleep(60)
        continue
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}. Skipping iteration.")
        continue
    except Exception as e:
        print(f"Unexpected error: {e}. Skipping iteration.")
        continue

if __name__ == "__main__":
    main()
