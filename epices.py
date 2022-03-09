import requests
import json
import pandas as pd
import time
import utils as utils
from datetime import  date

def get_data_prod_day(site, d, prefix, cfg):
    response = requests.get('https://api.epices-energie.fr/v1/site_hourly_production?site_id='+ str(site) +'&date='+d, headers=cfg.token_epice)
    if(response.status_code != 200):
        raise Exception("Error while getting data for site : " + site + ", status code : "+ str(response.status_code))
    j = json.loads(response.text)
    df_prod = pd.DataFrame(j['site_hourly_production']['hourly_productions'])
    df_prod['utc_timestamps_Paris'] = pd.to_datetime(df_prod['utc_timestamps'])
    df_prod['utc_timestamps_Paris']=df_prod['utc_timestamps_Paris'].dt.tz_convert('Europe/Paris')
    return df_prod

#Retreive and archive all data
def retreive_all_data(site,end_date,cfg,prod_file_path):
    start_date = date(site['DATEINST'].year, site['DATEINST'].month,site['DATEINST'].day)
    df_prod=get_data_prod_hist(start_date, end_date, site['EPID'], site['PREFIX'], cfg.NEXTCLOUD,prod_file_path,cfg)

def get_data_prod_hist(start_date, end_date, site, prefix_backup, nextcloud,prod_file_path,cfg):
    df_prod = pd.DataFrame()
    for single_date in utils.daterange(start_date, end_date):
        d = single_date.strftime("%Y-%m-%d")
        print("Getting data from epice for date "+d+" date site "+ site)
        response = requests.get('https://api.epices-energie.fr/v1/site_hourly_production?site_id='+str(site)+'&date=' + d, headers=cfg.token_epice)
        if(response.status_code != 200):
            raise Exception("Error while getting data for site : " + site + ", status code : "+ str(response.status_code))
        j = json.loads(response.text)
        if len(j['site_hourly_production']['hourly_productions']) == 0:
            #no data for this days
            print("no data for day:" + str(d))
        else:
            if single_date == start_date:
                df_prod = pd.DataFrame(j['site_hourly_production']['hourly_productions'])
            else:
                df_prod = df_prod.append(pd.DataFrame(j['site_hourly_production']['hourly_productions']))
            df_prod['utc_timestamps_Paris'] = pd.to_datetime(df_prod['utc_timestamps'])
            df_prod['utc_timestamps_Paris']=df_prod['utc_timestamps_Paris'].dt.tz_convert('Europe/Paris')
            time.sleep(1)
            filename = prefix_backup + '-' + d + "-prod.json"
            if nextcloud == True:
                #Upload raw data on NextCloud (used for archiving data over time)
                headers = {'Content-type': 'application/json', 'Slug': filename}
                r = requests.put(
                    url=cfg.NEXTCLOUD_REPO + '/Raw/' + filename,
                    data=response.text,
                    headers=headers,
                    auth=(cfg.NEXTCLOUD_USERNAME, cfg.NEXTCLOUD_PASSWORD))
            f = open(prod_file_path + filename,'w')
            f.write(response.text)
            f.close()

    return df_prod