#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##########################################################################################
# CoopTracker
#  - Dashboard for multiple cooperatives in Ile de France
#    All cooperatives are mentored by Energie Partagée: https://energie-partagee.org
# Copyright © 2021-2022 Électrons solaires (https://www.electrons-solaires93.org/)
# Contacts: Jeremie L., Jean-Marie B. (Électrons solaires, webmestre@electrons-solaires93.org)
# License: CC-BY-SA 4.0
##########################################################################################

import plotly.express as px
import plotly.graph_objects as go
import plotly
from plotly.graph_objs.scatter.marker import Line
from plotly.subplots import make_subplots
import pandas as pd
import json
import requests
import locale
from datetime import datetime, date, timedelta
from requests.auth import HTTPBasicAuth
from io import StringIO
import time
from xml.dom import minidom
import re
import sys
from pathlib import Path
import os

import config_EP as cfg        #file containing API keys / credentials / configuration
update_all = True              #update all plots (independently of scheduled updates)
file_path = "./../"            #tell where local files are stored 
prod_file_path = "./Raw/"      #tell where production files are stored 


# In[ ]:


#########################################################################
# Table with characteristics of all sites
#########################################################################
df=cfg.df_sites.sort_values(by='COOP', ascending=True)
text = '<html><head><link type="text/css" rel="Stylesheet" href="' + cfg.ESCSS + '" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea"><table>'
for row in range(0, len(df)): 
    text = text + '<tr><td><a target="_blank" href="' + df.iloc[row]['COOPSITE'] + '">' + df.iloc[row]['COOP'] + '</a></td><td>' +  df.iloc[row]['LNAME'] + '</td><td>' +  df.iloc[row]['CITY'] + '</td><td>' +  str(df.iloc[row]['DATEINST'].year) + '-' + str(df.iloc[row]['DATEINST'].month).rjust(2, '0') + '-' + str(df.iloc[row]['DATEINST'].day).rjust(2, '0') + '</td><td>' +  df.iloc[row]['PeakPW']  + ' kWc</td><td><a target="_blank" href="' +  df.iloc[row]['PREFIX'] + '/">production</a></td></tr>' 
text = text + '</div><table></body></html>' 
filename = "sites"    
file1 = open(file_path + filename + ".html","w", encoding='utf8')
file1.write(text)
file1.close()


# In[ ]:


###########################################################################
# Geographical maps
# - of 1) all installations and 2) societaries in each cooperative
# - Uses Plotly/Mapbox and OpenStreetMap data
##################################################################################

def save_map(fig, filename):
    #Save map as png and html
    fig.write_image(file_path + filename + ".png")
    plotly.offline.plot(fig, filename = file_path + filename + ".html", auto_open=False, include_plotlyjs='cdn')
    fig.show()
        
    #Upload on NextCloud
    if cfg.NEXTCLOUD == True:
        headers = {'Content-type': 'image/png', 'Slug': filename + ".png"}
        r = requests.put(
            url=cfg.NEXTCLOUD_REPO + '/Latest/' + filename + ".png", 
            data=open(file_path + filename + ".png", 'rb'), 
            headers=headers, 
            auth=(cfg.NEXTCLOUD_USERNAME, cfg.NEXTCLOUD_PASSWORD))

def plot_map_societaires(geo_json, csv, df_sites, coopname, filename, lat_map, lon_map):
    #Get CSV from URL
    r = requests.request(
        method='get',
        url= csv
    )
    df = pd.read_csv(StringIO(r.text),sep=';') 

    #Load GeoJSON data (polygones)
    with open(file_path + geo_json) as response:
        cities = json.load(response)

    data = go.Scattermapbox(lat=list(df_sites['LAT']),
                            lon=list(df_sites['LON']),
                            mode='markers+text',
                            marker_size=14,
                            marker_color='rgb(39, 97, 44)',
                            showlegend=True, 
                            name='Centrales ' + coopname,
                            textposition='top right',
                            textfont=dict(size=12, color='rgb(39, 97, 44)'),
                            text=df_sites['LNAME'])

    layout = dict(margin=dict(l=0, t=0, r=0, b=0, pad=0),
                mapbox=dict(zoom=11, 
                            accesstoken=cfg.mapbox_access_token,
                            center = {"lat": float(lat_map), "lon": float(lon_map)},
                            style='light'))

    fig = go.Figure(data=data, layout=layout)

    fig.add_trace(go.Choroplethmapbox(
                                geojson=cities, 
                                featureidkey='properties.code_commune', 
                                locations=df['code_commune'],
                                z=df['Societaires'],
                                colorscale='Greens',
                                showlegend = True, 
                                name = 'Nombre de sociétaires', 
                                zmin=0,
                                zmax=df['Societaires'].max()*2,
                                hovertemplate='%{z} sociétaires <extra></extra>'
                            ))

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    fig.update_geos(fitbounds="locations")  
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    save_map(fig, filename)
 

def plot_map_cooperatives(geo_json, csv, df_sites, filename, lat_map, lon_map):
    #Get CSV from file
    df = pd.read_csv(file_path + csv, sep=';') 
        
    #Load GeoJSON data (polygones)
    with open(file_path + geo_json) as response:
        cities = json.load(response)

    data = go.Scattermapbox(lat=list(df_sites['LAT']),
                            lon=list(df_sites['LON']),
                            mode='markers+text',
                            marker_size=14,
                            marker_color='rgb(108, 176, 65)',
                            showlegend=True, 
                            name='Centrales ',
                            textposition='top right',
                            textfont=dict(size=12, color='rgb(37, 64, 143)'),
                            text=df_sites['LNAME'])

    layout = dict(margin=dict(l=0, t=0, r=0, b=0, pad=0),
                mapbox=dict(zoom=10, 
                            accesstoken=cfg.mapbox_access_token,
                            center = {"lat": float(lat_map), "lon": float(lon_map)},
                            style='light'))

    fig = go.Figure(data=data, layout=layout)
    

    df['text'] = '<b>' + df['coop'] + '</b><br><a href="' + df['site'] + '">' + df['site'] + '</a>' 
    fig.add_trace( go.Choroplethmapbox(
                                geojson=cities, 
                                featureidkey='properties.code_commune', 
                                locations=df['code_commune'],
                                z=df['color'],
                                colorscale='Greens',
                                zmin=0,
                                zmax=df['color'].max(),
                                name = 'Cooperative', 
                                hovertemplate='%{text}<extra></extra>',text = df['text'], 
                                showscale=False,
                                marker_opacity=0.2
                            ))

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    fig.update_geos(fitbounds="locations")  
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, hoverlabel = dict(font=dict(color='rgb(37, 64, 143)'), bgcolor='white'))
    save_map(fig, filename)

#Updated once a day at 3am (UTC)
if datetime.now().hour == 3 or update_all == True: 
    # Map per cooperative (IDF)
    plot_map_cooperatives(cfg.GEOJSON_DATA_IDF, cfg.CSV_COOPS, cfg.df_sites, 'map_IDF', 48.8845927777778, 2.38651155555556) 
    
    # Map per cooperative 
    for row in range(0, len(cfg.df_coops)):
        df = cfg.df_sites[cfg.df_sites['COOP'] == cfg.df_coops.iloc[row]['COOP']]
        plot_map_societaires(cfg.df_coops.iloc[row]['GEOJSON'], cfg.df_coops.iloc[row]['CSV_Societaries'], df, cfg.df_coops.iloc[row]['COOP'], 'map_societaries_' + cfg.df_coops.iloc[row]['COOPSNAME'], cfg.df_coops.iloc[row]['LAT'], cfg.df_coops.iloc[row]['LON']) 


# In[ ]:


#########################################################################
# Daily productions 
#  - data from Epices API - https://www.epices-energie.fr
#  - HTTP request: curl -H "Authorization: Token token=XXX" https://api.epices-energie.fr/v1/site_hourly_production?site_id=&date= 
#########################################################################
year=str(datetime.now().year)
month=str(datetime.now().month)
day=str(datetime.now().day) 
d=year+'-'+month+'-'+day

def get_data_prod_day(site, d, prefix):
    response = requests.get('https://api.epices-energie.fr/v1/site_hourly_production?site_id='+ str(site) +'&date='+d, headers=cfg.token_epice)
    j = json.loads(response.text)
    df_prod = pd.DataFrame(j['site_hourly_production']['hourly_productions'])
    df_prod['utc_timestamps_Paris'] = pd.to_datetime(df_prod['utc_timestamps'])
    df_prod['utc_timestamps_Paris']=df_prod['utc_timestamps_Paris'].dt.tz_convert('Europe/Paris')
    return df_prod

def plot_hist_prod(df_prod, titlename, col_time, col_time_text):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Line(
            x=df_prod[col_time],
            y=df_prod['gh_wm2'],
            name="prévision ensoleillement (W/m2)",
            line=dict(color='rgb(37, 64, 143)'),
            hovertemplate =
            '<b>Date</b>: %{x} h'+
            '<br><b>Ensoleillement</b>: %{y:.1f} W/m2<br><extra></extra>'
        ), 
        secondary_y=True)

    fig.add_trace(
        go.Bar(
            x=df_prod[col_time],
            y=df_prod['production_in_wh']/1000,
            name="production (kWh)",
            marker_color='rgb(108, 176, 65)',
            hovertemplate =
            '<b>Date</b>: %{x} h'+
            '<br><b>Production</b>: %{y:.1f} kWh<br><extra></extra>'
        ), 
        secondary_y=False)
    #fig.update_layout(title_text=titlename)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",x=0,y=1))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig.update_xaxes(title_text = col_time_text)
    fig.update_yaxes(title_text="<b>Ensoleillement (W/m2)</b>", color="rgb(37, 64, 143)", secondary_y=True, side='right')
    fig.update_yaxes(title_text="<b>Production (kWh)</b>", color="rgb(108, 176, 65)", secondary_y=False, side='left')
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig

def plot_hist_prod_only(df_prod, titlename, col_time, col_time_text):
    #fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=df_prod[col_time],
            y=df_prod['production_in_wh']/1000,
            name="production (Wh)",
            marker_color='rgb(108, 176, 65)',
            hovertemplate =
            '<b>Date</b>: %{x} h'+
            '<br><b>Production</b>: %{y:.1f} kWh<br><extra></extra>'
        ), 
        secondary_y=False)
    fig.add_trace(
        go.Bar(
            x=df_prod[col_time],
            y=df_prod['production_in_wh']/1000,
            name="production (Wh)",
            marker_color='rgb(108, 176, 65)',
            hovertemplate =
            '<b>Date</b>: %{x} h'+
            '<br><b>Production</b>: %{y:.1f} kWh<br><extra></extra>'
        ), 
        secondary_y=True)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        x=0,
        y=1
    ))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    fig.update_xaxes(title_text = col_time_text)
    fig.update_yaxes(title_text="<b></b>", color="rgb(108, 176, 65)", secondary_y=True, side='right')
    fig.update_yaxes(title_text="<b>Production (kWh)</b>", color="rgb(108, 176, 65)", secondary_y=False, side='left')
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig

def save_prod_day_text(df, filename):
    s=df['production_in_wh'].sum()
    year=time.strftime("%y", time.localtime())
    month=str(datetime.now().month)
    day=str(datetime.now().day)
    text='<html><head><link type="text/css" rel="Stylesheet" href="' + cfg.ESCSS + '" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea">Production du ' + day + '/' + month + '/' + year + ' : <b>' + str(round(s/1000)) + ' kWh</b></div></body></html>'
    file1 = open(file_path + filename + ".html","w",encoding='utf8')
    file1.write(text)
    file1.close() 
        
def fix_locale_htmlfile(filename):
    f = open(filename,'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace("<head>","<head><script src='https://cdn.plot.ly/plotly-locale-fr-latest.js'></script>")
    f = open(filename,'w')
    f.write(newdata)
    f.close()   

def save_fig(fig, filename):
    fig.write_image(file_path + filename + ".png",scale=2.5, width=900)   
    plotly.offline.plot(fig, filename = file_path + filename + ".html", auto_open=False, include_plotlyjs='cdn', config=dict(locale='fr', displayModeBar=False))
    fix_locale_htmlfile(file_path + filename + ".html")
    fig.show(config=dict(locale='fr', displayModeBar=False))


#Update only after 8am (UTC)
if datetime.now().hour >= 8:
    #Daily production for each site
    for row in range(0, len(cfg.df_sites)):
        df_prod=get_data_prod_day(cfg.df_sites.iloc[row]['EPID'],d, cfg.df_sites.iloc[row]['PREFIX'])
        fig=plot_hist_prod(df_prod, "Historique journalier de production ("+cfg.df_sites.iloc[row]['SNAME']+", "+cfg.df_sites.iloc[row]['CITY']+")", 'utc_timestamps_Paris', 'Heures')
        save_fig(fig, cfg.df_sites.iloc[row]['PREFIX']+'_prod_today')
        save_prod_day_text(df_prod, cfg.df_sites.iloc[row]['PREFIX']+'_prod_today_tex')
        if row == 0:
            df_prodAll=df_prod
        df_prodAll['production_in_wh'] = df_prodAll['production_in_wh'] + df_prod['production_in_wh'] 
        
    #Total production of all sites
    fig=plot_hist_prod_only(df_prodAll, "Historique journalier de production", 'utc_timestamps_Paris', 'Heures')
    save_fig(fig, 'All_prod_today')


# In[ ]:


#########################################################################
# Productions of the last 3 days (hourly granularity)
#  - data from Epices API - https://www.epices-energie.fr
#  - HTTP request: curl -H "Authorization: Token token=XXX" https://api.epices-energie.fr/v1/site_hourly_production?site_id=&date= 
#  - it archieves daily data on NextCloud
#########################################################################
year=datetime.now().year
month=datetime.now().month
day=datetime.now().day
end_date = date(year, month, day)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_data_prod_hist(start_date, end_date, site, prefix_backup, nextcloud):
    df_prod = pd.DataFrame()
    for single_date in daterange(start_date, end_date):
        d = single_date.strftime("%Y-%m-%d")
        response = requests.get('https://api.epices-energie.fr/v1/site_hourly_production?site_id='+str(site)+'&date=' + d, headers=cfg.token_epice)
        j = json.loads(response.text)
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

def prod_hist(start_date, end_date, days):
    if days == 30:
        col_time = 'Date'
        col_time_text = 'Jours'
        nextcloud = False
    else:
        col_time = 'utc_timestamps_Paris'
        col_time_text = 'Jours'
        nextcloud = cfg.NEXTCLOUD

    for row in range(0, len(cfg.df_sites)):
        df_prod=get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], nextcloud)
        if days > 7 :
            df_prod['Date'] = pd.to_datetime(df_prod['utc_timestamps_Paris'],format='%Y-%m-%d')
            df_prod['Date']= df_prod['Date'].dt.strftime('%y-%m-%d')
            df_grouped=df_prod.groupby('Date').sum().reset_index()
            df_prod = pd.DataFrame(df_grouped)
        fig=plot_hist_prod_only(df_prod, "Historique " + str(days) + " derniers jours de production ("+cfg.df_sites.iloc[row]['SNAME']+", +"+cfg.df_sites.iloc[row]['CITY']+"+)", col_time, col_time_text)
        fig=save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days))   
        
#Retreive and archive all data
def retreive_all_data(end_date):
    for row in range(len(cfg.df_sites)-2, len(cfg.df_sites)-1):        
        start_date = date(cfg.df_sites.iloc[row]['DATEINST'].year, cfg.df_sites.iloc[row]['DATEINST'].month,cfg.df_sites.iloc[row]['DATEINST'].day)
        df_prod=get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], cfg.NEXTCLOUD)

#updated once a day at 2am
if datetime.now().hour == 2 or update_all == True:
    past_days_ago = datetime.now() - timedelta(days=3)
    start_date = date(past_days_ago.year, past_days_ago.month, past_days_ago.day)
    prod_hist(start_date, end_date, 3)
    #retreive_all_data(end_date)


# In[ ]:


#########################################################################
# Productions of the last 30 days (daily granularity)
#  - data from Epices API - https://www.epices-energie.fr
#  - HTTP request: curl -H "Authorization: Token token=XXX" https://api.epices-energie.fr/v1/site_daily_indicators?site_id=&date= 
#########################################################################
       
def get_data_prod_hist_day(start_date, end_date, site, prefix_backup):
    #time.sleep(20)
    for single_date in daterange(start_date, end_date):
        d = single_date.strftime("%Y-%m-%d")
        with open(prod_file_path + prefix_backup + '-' + d + '-prod.json' ) as response:
            prod = json.load(response)
            if single_date == start_date:
                df_prod = pd.DataFrame(prod['site_hourly_production']['hourly_productions'])
            else:
                df_prod = df_prod.append(pd.DataFrame(prod['site_hourly_production']['hourly_productions']))
        #response = requests.get('https://api.epices-energie.fr/v1/site_daily_indicators?site_id='+str(site)+'&date=' + d, headers=cfg.token_epice)
        #j = json.loads(response.text)
        #if single_date == start_date:
        #    df_prod = pd.DataFrame.from_dict(j, orient='index')
        #else:
        #    df_prod = df_prod.append(pd.DataFrame.from_dict(j, orient='index'))
        #df_prod=df_prod.drop("request_timestamps")
    df_prod['utc_timestamps_Paris'] = pd.to_datetime(df_prod['utc_timestamps'])
    df_prod['utc_timestamps_Paris']=df_prod['utc_timestamps_Paris'].dt.tz_convert('Europe/Paris')
    df_prod['Date'] = df_prod['utc_timestamps_Paris'].dt.strftime('%y-%m-%d')
    df_grouped=df_prod.groupby('Date').sum().reset_index()
    df_prod = pd.DataFrame(df_grouped)
    #correct inhabitant equivalent from Epices 
    #df_prod['unhabitants_equivalents'] = df_prod['total_production_in_wh'] / (float(cfg.EH_WhPerYear)/365.0)
    df_prod['unhabitants_equivalents'] = df_prod['production_in_wh'] / (float(cfg.EH_WhPerYear)/365.0)
    return df_prod

def plot_hist_prod_day(df_prod, titlename, col_time, col_time_text):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Line(
            x=df_prod[col_time],
            y=df_prod['unhabitants_equivalents'],
            name="equivalent (habitants)",
            line=dict(color='rgb(37, 64, 143)'),
            hovertemplate =
            '<b>Date</b>: %{x}'+
            '<br><b>Equivalent</b>: %{y:.1f} habitants<br><extra></extra>'
        ), 
        secondary_y=True)
    fig.add_trace(
        go.Bar(
            x=df_prod[col_time],
            y=df_prod['production_in_wh']/1000,
            #y=df_prod['total_production_in_wh']/1000,
            name="production (kWh)",
            marker_color='rgb(108, 176, 65)',
            hovertemplate =
            '<b>Date</b>: %{x}'+
            '<br><b>Production</b>: %{y:.1f} kWh<br><extra></extra>'
        ), 
        secondary_y=False)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        x=0,
        y=1
    ))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig.update_xaxes(title_text = col_time_text)
    fig.update_yaxes(title_text="<b>Equivalent (habitants)</b>", color="rgb(37, 64, 143)", secondary_y=True, side='right')
    fig.update_yaxes(title_text="<b>Production (kWh)</b>", color="rgb(108, 176, 65)", secondary_y=False, side='left')
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig

def save_prod_hist_text(site, s, k, d, filename):
    text='<html><head><link type="text/css" rel="Stylesheet" href="' + cfg.ESCSS + '" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"> <div class="textarea">Cette production correspond à la consommation hors chauffage et eau chaude sanitaire de ' + str(round(s/2.4)) + ' foyers, soit ' + str(round(s)) + ' habitants, sur les ' + str(d) + ' derniers jours.</p></div></body></html>'
    file1 = open(file_path + filename + ".html","w", encoding='utf8')
    file1.write(text)
    file1.close()

def plot_hist_prod_unhabitants():
    df = pd.DataFrame(columns=['site','unhabitants_equivalents'])
    for row in range(0, len(cfg.df_sites)):
        df = df.append({'site': cfg.df_sites.iloc[row]['TYPE'] + '<br>' + cfg.df_sites.iloc[row]['SNAME'] + ' <br>(' + cfg.df_sites.iloc[row]['CITY'] + ')', 'unhabitants_equivalents': cfg.df_sites.iloc[row]['EH']}, ignore_index=True) 
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df['site'],
            y=df['unhabitants_equivalents'],
            hovertemplate =
            '<b>Site</b>: %{x}'+
            '<br><b>Equivalent</b>: %{y:.1f} habitants<br><extra></extra>',
            name='equivalent consomation (habitants)',
            marker_color='rgb(108, 176, 65)'
        ))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0), showlegend=True)
    fig.update_layout(yaxis_title='', xaxis_title='')
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", x=0, y=1))
    return fig

def prod_hist_day(start_date, end_date, days):
    col_time = 'Date'
    col_time_text = 'Jours'
    cfg.df_sites['EH'] = 0
    meanAll = 0
    kwhAll = 0
    #Production of each site
    for row in range(0, len(cfg.df_sites)):
        df_prod=get_data_prod_hist_day(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'])
        fig=plot_hist_prod_day(df_prod, "Historique " + str(days) + " derniers jours de production (" + cfg.df_sites.iloc[row]['SNAME'] + ", " + cfg.df_sites.iloc[row]['CITY'] + ")", col_time, col_time_text)
        fig=save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days))
        mean=round(df_prod['unhabitants_equivalents'].mean(),1)
        #kwh=round(df_prod['total_production_in_wh'].sum(),1)
        kwh=round(df_prod['production_in_wh'].sum(),1)
        cfg.df_sites.loc[row,"EH"] = mean
        save_prod_hist_text(cfg.df_sites.iloc[row]['EPID'], mean, kwh, days, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_tex_" + str(days))
        if row == 0:
            df_prodAll = df_prod
        else:
            df_prodAll['unhabitants_equivalents'] = df_prodAll['unhabitants_equivalents'] + df_prod['unhabitants_equivalents']
            #df_prodAll['total_production_in_wh'] = df_prodAll['total_production_in_wh'] + df_prod['total_production_in_wh']
            df_prodAll['production_in_wh'] = df_prodAll['production_in_wh'] + df_prod['production_in_wh']
        meanAll = meanAll + mean
        kwhAll = kwhAll + kwh
        
    #Total production for all sites
    fig=plot_hist_prod_day(df_prodAll, "Historique " + str(days) + " derniers jours de production", col_time, col_time_text)
    save_fig(fig, "All-prod_hist_" + str(days)) 
    
    #Mean equivalent habitants for all sites
    fig=plot_hist_prod_unhabitants()
    save_fig(fig,"prod_hist_unhabitants")

#updates once a day at 5am (UTC)
if datetime.now().hour == 4 or update_all == True:
    thrity_days_ago = datetime.now() - timedelta(days=30)
    start_date = date(thrity_days_ago.year, thrity_days_ago.month, thrity_days_ago.day)
    prod_hist_day(start_date, end_date, 30)


# 

# In[ ]:


######################################################################################################
# Historical weather from the last 3 days
#   - data from OpenWeatherMap (https://openweathermap.org)
#   - HTTP request: curl "https://api.openweathermap.org/data/2.5/onecall/timemachine?lat=&lon=&dt=&appid="
######################################################################################################
year=datetime.now().year
month=datetime.now().month
day=datetime.now().day
end_date = date(year, month, day)

def get_data_weather_hist(start_date, end_date, row_site):

    for single_date in daterange(start_date, end_date):
        d = round(time.mktime(single_date.timetuple()))+3600
        response = requests.get('https://api.openweathermap.org/data/2.5/onecall/timemachine?lat='+str(cfg.df_sites.iloc[row_site]['LAT'])+'&lon=' + str(cfg.df_sites.iloc[row_site]['LON']) + '&dt=' + str(d) + '&units=metric&appid=' + str(cfg.APIK_OWM))
        j = json.loads(response.text)
        if single_date == start_date:
            df_prod = pd.DataFrame(j['hourly'])
        else:
            df_prod = df_prod.append(pd.DataFrame(j['hourly']))
    return df_prod

def plot_weather_hist(df_prod, df_prodGHI, titlename):
    #relevant data: uvi, cloudiness & rain, temp
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Line(
            x=df_prodGHI['utc_timestamps_Paris'],
            y=df_prodGHI['gh_wm2'],
            name="ensoleilement (W/m2)",
            line=dict(color='rgb(37, 64, 143)'),
            hovertemplate =
            '<b>Date</b>: %{x} h'+
            '<br><b>Ensoleilement</b>: %{y:.1f} W/m2<br><extra></extra>'
        ),secondary_y=True)# row=1, col=1)
    fig.add_trace(
        go.Line(
            x=df_prod['Date'],
            y=df_prod['clouds'],
            name="nébulosité (%)",
            line=dict(color='red'),
            hovertemplate =
            '<b>Date</b>: %{x} h'+
            '<br><b>Nébulosité</b>: %{y:.1f} %<br><extra></extra>'
        ),secondary_y=False)# row=1, col=1)

    #fig.update_xaxes(title_text = 'Jours', row=1, col=1)
    fig.update_yaxes(title_text="<b>Ensoleilement (W/m2)</b>",  color="rgb(37, 64, 143)", secondary_y=True, side='right')# row=1, col=1)
    fig.update_yaxes(title_text="<b>Nébulosité (%)</b>", color="red", secondary_y=False, side='left')# row=1, col=1)
    fig.update_xaxes(title_text = 'Jours')
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        x=0,
        y=1
    ))
    #fig.update_layout(title_text=titlename)
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig

#Updated once a day at 3am (UTC)
if datetime.now().hour == 3 or update_all == True:
    past_days_ago = datetime.now() - timedelta(days=3)
    start_date = date(past_days_ago.year, past_days_ago.month, past_days_ago.day)
    # Weather for each site
    for row in range(0, len(cfg.df_sites)):
        df_prod = get_data_weather_hist(start_date, end_date, row)
        df_prodGHI=get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], False)
        df_prod['Date'] = pd.to_datetime(df_prod['dt'],unit='s', utc=True)
        df_prod['Date']=df_prod['Date'].dt.tz_convert('Europe/Paris')
        df_prod = df_prod.iloc[6:len(df_prod.index)-3] #remove first 6 and last 2 data points
        fig=plot_weather_hist(df_prod, df_prodGHI, "Historique meteo (" + cfg.df_sites.iloc[row]['SNAME'] +", " + cfg.df_sites.iloc[row]['CITY'] + ")")
        save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + '_weather_hist')


# 

# In[ ]:


#########################################################################
# Production since installation
#    - From daily data stored as JSON files
#########################################################################
def plot_hist_prod_month(df_prod, titlename, xlabel):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=df_prod['Date'],
            y=df_prod['production_in_wh']/1000000,
            name="production (Wh)",
            marker_color='rgb(108, 176, 65)',
            hovertemplate =
            '<b>Date</b>: %{x}'+
            '<br><b>Production</b>: %{y:.1f} MWh<br><extra></extra>'
        ),secondary_y=False)
    fig.add_trace(
        go.Bar(
            x=df_prod['Date'],
            y=df_prod['production_in_wh']/1000000,
            name="production (Wh)",
            marker_color='rgb(108, 176, 65)',
            hovertemplate =
            '<b>Date</b>: %{x}'+
            '<br><b>Production</b>: %{y:.1f} MWh<br><extra></extra>'
        ),secondary_y=True)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        x=0,
        y=1
    ))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    fig.update_xaxes(title_text = xlabel)

    # Set y-axes titles
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig.update_yaxes(title_text="<b></b>", color="rgb(108, 176, 65)", secondary_y=True, side='right')
    fig.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(108, 176, 65)", secondary_y=False, side='left')
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig

def get_all_data(site):
    df_prod = pd.DataFrame()
    list_of_files = os.listdir(prod_file_path) #list of files in the current directory
    for each_file in list_of_files:
        if each_file.startswith(site):  #since its all type str you can simply use startswith
            with open(prod_file_path + each_file) as response:
                prod = json.load(response)
                df_prod = df_prod.append(prod['site_hourly_production']['hourly_productions'])

    # get prod files from NexCLoud
    #r = requests.request(
    #    method='PROPFIND',
    #    url=cfg.NEXTCLOUD_REPO + '/Raw/',
    #    auth=(cfg.NEXTCLOUD_USERNAME, cfg.NEXTCLOUD_PASSWORD)
    #)
    #dom = minidom.parseString(r.text.encode('ascii', 'xmlcharrefreplace'))
    ##print(dom.toprettyxml())
    #cells = dom.getElementsByTagName('d:href')
    #df_prod = pd.DataFrame()
    #for i in range(1,cells.length):
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
    df_prod['Date'] = pd.to_datetime(df_prod['utc_timestamps'],format='%Y-%m-%d')
    df_prod['Date']= df_prod['Date'].dt.strftime('%y-%m')
    df_grouped=df_prod.groupby('Date').sum().reset_index()
    df_prod = pd.DataFrame(df_grouped)
    return df_prod 


def plot_hist_prod_month_all():
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_prodWD['Date'],
            y=df_prodWD['production_in_wh']/1000000,
            name="Waldeck-Rousseau",
            marker_color='rgb(108, 176, 65)',
            hovertemplate =
            '<b>Date</b>: %{x}'+
            '<br><b>Production</b>: %{y:.1f} MWh<br><extra></extra>'
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_prodJZ['Date'],
            y=df_prodJZ['production_in_wh']/1000000,
            name="Jean Zay",
            marker_color='rgb(211, 189, 98)',
            hovertemplate =
            '<b>Date</b>: %{x}'+
            '<br><b>Production</b>: %{y:.1f} MWh<br><extra></extra>'
        )
    )   
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", x=0, y=1))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig.update_xaxes(title_text='')
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(136, 136, 136)")
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig

#uUdated once a day at 4am (UTC)
if datetime.now().hour == 4 or update_all == True:
    #Total production for each site
    fig_all_small = go.Figure()
    fig_all_large = go.Figure()
    for row in range(0, len(cfg.df_sites)):
        df_prod=get_all_data(cfg.df_sites.iloc[row]['PREFIX'])
        if cfg.df_sites.iloc[row]['PREFIX'] == "JZ":
            #fill missing data (pb data logger): 21700 Kwh not recorded by Epices
            i = df_prod[ df_prod['Date']=='21-07' ].index.values[0]  
            df_prod.loc[i,"production_in_wh"]=10400000
            i = df_prod[ df_prod['Date']=='21-08' ].index.values[0]  
            df_prod.loc[i,"production_in_wh"]=9700000
            i = df_prod[ df_prod['Date']=='21-09' ].index.values[0]  
            df_prod.loc[i,"production_in_wh"]=df_prod.loc[i,"production_in_wh"]+1600000 #3 days
            df_prod['production_in_wh'] = pd.to_numeric(df_prod['production_in_wh'], downcast="float")
        fig=plot_hist_prod_month(df_prod, "Historique (" + cfg.df_sites.iloc[row]['SNAME'] + ")", "Mois")  
        save_fig(fig,cfg.df_sites.iloc[row]['PREFIX'] + "_all_data")
        if float(cfg.df_sites.iloc[row]['PeakPW']) < 40 :
            fig_all_small.add_trace(
                go.Bar(
                    x=df_prod['Date'],
                    y=df_prod['production_in_wh']/1000000,
                    name=cfg.df_sites.iloc[row]['PREFIX'],
                    #marker_color='rgb(108, 176, 65)',
                    textposition='none',
                    hovertemplate =
                    '<b>Date</b>: %{x}'+
                    '<br><b>Production</b>: %{y:.1f} MWh<br><extra></extra>'
                )
            )
        else:
            fig_all_large.add_trace(
                go.Bar(
                    x=df_prod['Date'],
                    y=df_prod['production_in_wh']/1000000,
                    name=cfg.df_sites.iloc[row]['PREFIX'],
                    textposition='none',
                    hovertemplate =
                    '<br><b>Date</b>: %{x}'+
                    '<br><b>Production</b>: %{y:.1f} MWh<br><extra></extra>'
                )
            )            
        if row == 0:
            df_prodAll = df_prod
        else:
            df_prodAll = df_prodAll.append(df_prod)
        
    #All small sites (histograms side by side)
    fig_all_small.update_layout(legend=dict(orientation="h", yanchor="bottom", x=0, y=1))
    fig_all_small.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig_all_small.update_xaxes(title_text='')
    fig_all_small.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig_all_small.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(136, 136, 136)")
    fig_all_small.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    save_fig(fig_all_small,"All_data_all_small_sitesIDF")
    
    #All large_small sites (histograms side by side)
    fig_all_large.update_layout(legend=dict(orientation="h", yanchor="bottom", x=0, y=1))
    fig_all_large.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig_all_large.update_xaxes(title_text='')
    fig_all_large.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig_all_large.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(136, 136, 136)")
    fig_all_large.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    save_fig(fig_all_large,"All_data_all_large_sitesIDF")
    
    #All sites (cumulated)
    df_grouped=df_prodAll.groupby('Date').sum().reset_index()
    df_prodAll = pd.DataFrame(df_grouped)
    fig=plot_hist_prod_month(df_prodAll, "Historique (tous les sites)", "Mois")  
    save_fig(fig, "All_data_all_sitesIDF_cumulated")


# In[ ]:




