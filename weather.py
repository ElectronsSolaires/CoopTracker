import utils
import requests
import json
import pandas as pd
import time

def get_data_weather_hist(start_date, end_date, row_site, cfg):
    df_prod = pd.DataFrame()
    for single_date in utils.daterange(start_date, end_date):
        site = cfg.df_sites.iloc[row_site]['PREFIX']
        print("Getting weither data from openweathermap for site "+ site)
        d = round(time.mktime(single_date.timetuple()))+7200
        response = requests.get('https://api.openweathermap.org/data/2.5/onecall/timemachine?lat='+str(cfg.df_sites.iloc[row_site]['LAT'])+'&lon=' + str(cfg.df_sites.iloc[row_site]['LON']) + '&dt=' + str(d) + '&units=metric&appid=' + str(cfg.APIK_OWM))
        if(response.status_code != 200):
            raise Exception("Error while getting weither data for site : " + site + ", status code : "+ str(response.status_code))
        j = json.loads(response.text)
        if single_date == start_date:
            df_prod = pd.DataFrame(j['hourly'])
        else:
            df_prod = df_prod.append(pd.DataFrame(j['hourly']))
    return df_prod
