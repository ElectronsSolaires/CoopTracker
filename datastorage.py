import pandas as pd
import utils as utils  # utils functions
import json
import os


def get_all_data(site, prod_file_path):
    """Return all stored data for a site in a dataframe
    """
    df_prod = pd.DataFrame()
    list_of_files = os.listdir(prod_file_path)  # list of files in the current directory
    for each_file in list_of_files:
        if each_file.startswith(site):  # since its all type str you can simply use startswith
            with open(prod_file_path + each_file) as response:
                prod = json.load(response)
                clean_prod_file(prod)
                df_prod = df_prod.append(prod['site_hourly_production']['hourly_productions'])

    # get prod files from NexCLoud
    # r = requests.request(
    #    method='PROPFIND',
    #    url=cfg.NEXTCLOUD_REPO + '/Raw/',
    #    auth=(cfg.NEXTCLOUD_USERNAME, cfg.NEXTCLOUD_PASSWORD)
    # )
    # dom = minidom.parseString(r.text.encode('ascii', 'xmlcharrefreplace'))
    ##print(dom.toprettyxml())
    # cells = dom.getElementsByTagName('d:href')
    # df_prod = pd.DataFrame()
    # for i in range(1,cells.length):
    #    if re.search(site, cells[i].firstChild.data):
    #        r = requests.request(
    #            method='get',
    #            url='https://www.electrons-solaires93.org/' + cells[i].firstChild.data,
    #            auth=(cfg.NEXTCLOUD_USERNAME, cfg.NEXTCLOUD_PASSWORD)
    #        )
    #        j = json.loads(r.text)
    #        if i == 1:
    #            df_prod = pd.DataFrame(j['site_hourly_production']['hourly_productions'])
    #        else:
    #            df_prod = df_prod.append(pd.DataFrame(j['site_hourly_production']['hourly_productions']))
    df_prod['Date'] = pd.to_datetime(df_prod['utc_timestamps'], format='%Y-%m-%d')
    df_prod['Date'] = df_prod['Date'].dt.strftime('%y-%m')
    df_grouped = df_prod.groupby('Date').sum().reset_index()
    df_prod = pd.DataFrame(df_grouped)
    return df_prod


def get_data_prod_hist_day(start_date, end_date, site, prefix_backup, prod_file_path, cfg):
    """Return all stored data for a site for a date range in a dataframe
    """
    # time.sleep(20)
    df_prod = pd.DataFrame()  # init dataframe
    for single_date in utils.daterange(start_date, end_date):
        d = single_date.strftime("%Y-%m-%d")
        filepath = prod_file_path + prefix_backup + '-' + d + '-prod.json'

        try:
            with open(filepath) as response:
                prod = json.load(response)
                clean_prod_file(prod)
                if single_date == start_date:
                    df_prod = pd.DataFrame(prod['site_hourly_production']['hourly_productions'])
                else:
                    df_prod = df_prod.append(pd.DataFrame(prod['site_hourly_production']['hourly_productions']))
            # response = requests.get('https://api.epices-energie.fr/v1/site_daily_indicators?site_id='+str(site)+'&date=' + d, headers=cfg.token_epice)
            # j = json.loads(response.text)
            # if single_date == start_date:
            #    df_prod = pd.DataFrame.from_dict(j, orient='index')
            # else:
            #    df_prod = df_prod.append(pd.DataFrame.from_dict(j, orient='index'))
            # df_prod=df_prod.drop("request_timestamps")
        except OSError as ex:
            print(ex)
    df_prod['utc_timestamps_Paris'] = pd.to_datetime(df_prod['utc_timestamps'])
    df_prod['utc_timestamps_Paris'] = df_prod['utc_timestamps_Paris'].dt.tz_convert('Europe/Paris')
    df_prod['Date'] = df_prod['utc_timestamps_Paris'].dt.strftime('%y-%m-%d')
    df_grouped = df_prod.groupby('Date').sum().reset_index()
    df_prod = pd.DataFrame(df_grouped)
    # correct inhabitant equivalent from Epices
    # df_prod['unhabitants_equivalents'] = df_prod['total_production_in_wh'] / (float(cfg.EH_WhPerYear)/365.0)
    df_prod['unhabitants_equivalents'] = df_prod['production_in_wh'] / (float(cfg.EH_WhPerYear) / 365.0)
    return df_prod


def clean_prod_file(prod):
    #set None production data to 0
    for hourly_production in prod['site_hourly_production']['hourly_productions']:
        if (hourly_production['production_in_wh'] is None):
            hourly_production['production_in_wh'] = 0
        if (hourly_production['satellite_reference_in_wh'] is None):
            hourly_production['satellite_reference_in_wh'] = 0
        if (hourly_production['normalized_production_in_wh'] is None):
            hourly_production['normalized_production_in_wh'] = 0