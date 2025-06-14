import requests
import json
import pandas as pd
import time
import utils as utils
from datetime import  date

def get_data_prod_day(site, d, prefix, cfg):
    if site == str(9999): #FSMV
        response = requests.get('https://tools.fsmv.fr/graph/fsmv_api.php?energy_type=prod&date='+d)
        print(str(response.text).find("No Record"))
        if response.status_code != 200 and response.status_code != 404:
            raise Exception("Error while getting data for site : " + site + ", status code : "+ str(response.status_code))
        elif response.status_code == 200 and str(response.text).find('No Record Found')!=-1:
            p = 0
        else:
            #read production and convert it into EPICE's dayly prod format (one hour contains the full day prod)
            j_fsmv = json.loads(response.text)
            print(j_fsmv)
            p = j_fsmv['energy']['value'] * 1000
        f = open("FSMV-template-prod.json",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("DATE",d)
        j = json.loads(newdata.replace("PRODDAY",str(p)))
    else:
        response = requests.get('https://api.epices-energie.fr/v1/site_hourly_production?site_id='+ str(site) +'&date='+d, headers=cfg.token_epice)
        if(response.status_code != 200):
            raise Exception("Error while getting data for site : " + site + ", status code : "+ str(response.status_code))
        j = json.loads(response.text)
    df_prod = pd.DataFrame(j['site_hourly_production']['hourly_productions'])
    if len(df_prod) == 0:
        #no data for this days
        print("no data for day:" + str(d) + " site: " + site)
    else:
        df_prod['utc_timestamps_Paris'] = pd.to_datetime(df_prod['utc_timestamps'])
        df_prod['utc_timestamps_Paris'] = df_prod['utc_timestamps_Paris'].dt.tz_convert('Europe/Paris')
    return df_prod

#Retreive and archive all data
def retreive_all_data(site,end_date,cfg,prod_file_path):
    start_date = date(site['DATEINST'].year, site['DATEINST'].month,site['DATEINST'].day)
    df_prod=get_data_prod_hist(start_date, end_date, site['EPID'], site['PREFIX'], cfg.NEXTCLOUD,prod_file_path,cfg)

def get_data_prod_hist(start_date, end_date, site, prefix_backup, nextcloud,prod_file_path,cfg):
    df_prod = pd.DataFrame()
    for single_date in utils.daterange(start_date, end_date):
        d = single_date.strftime("%Y-%m-%d")
        if site == str(9999): #FSMV
            print("Getting data from FSMV for date "+d+" date site "+ site)
            response = requests.get('https://tools.fsmv.fr/graph/fsmv_api.php?energy_type=prod&date='+d)
            if response.status_code != 200 and response.status.code != 404:
                raise Exception("Error while getting data for site : " + site + ", status code : "+ str(response.status_code))
            elif response.status_code == 200 and str(response.text).find('No Record Found')!=-1: #no data yet
                p = 0
            else:
                #read production and convert it into EPICE's dayly prod format (one hour contains the full day prod)
                j_fsmv = json.loads(response.text)
                p = j_fsmv['energy']['value'] * 1000
            f = open("FSMV-template-prod.json",'r')
            filedata = f.read()
            f.close()
            newdata = filedata.replace("DATE",d)
            filedata = newdata.replace("PRODDAY",str(p))
            j = json.loads(filedata)
        else:
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
            #f.write(response.text)
            #f.close()
            json.dump(j,f)

    return df_prod
