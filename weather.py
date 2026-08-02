import utils
import requests
import json
import pandas as pd
import time

_session = requests.Session()

def get_data_weather_hist(start_date, end_date, row_site, cfg):
    frames = []
    for single_date in utils.daterange(start_date, end_date):
        site = cfg.df_sites.iloc[row_site]['PREFIX']
        print("Getting weather data from openweathermap for site " + site)
        for h in range(24):
            d = round(time.mktime(single_date.timetuple())) + 7200 + h * 3600
            url = 'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat=' + str(cfg.df_sites.iloc[row_site]['LAT']) + '&lon=' + str(cfg.df_sites.iloc[row_site]['LON']) + '&dt=' + str(d) + '&units=metric&appid=' + str(cfg.APIK_OWM)
            response = None
            for attempt in range(3):
                try:
                    response = _session.get(url, timeout=15)
                    if response.status_code == 200:
                        break
                    if response.status_code in {429, 500, 502, 503, 504}:
                        time.sleep(1)
                        continue
                    raise Exception("Error while getting weather data for site : " + site + ", status code : " + str(response.status_code))
                except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as exc:
                    if attempt == 2:
                        print(f"Skipping weather data for site {site} on {d}: {exc}")
                        break
                    time.sleep(1)
            if response is None or response.status_code != 200:
                continue
            try:
                j = json.loads(response.text)
                if 'data' in j:
                    frames.append(pd.DataFrame(j['data']))
            except (ValueError, KeyError) as exc:
                print(f"Skipping weather payload for site {site} on {d}: {exc}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
