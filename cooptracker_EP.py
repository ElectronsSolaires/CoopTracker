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

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, date, timedelta
import epices
import datastorage
import utils
import weather
import requests
from io import StringIO
import json
import time

import config_EP as cfg        #file containing API keys / credentials / configuration
update_all = True              #update all plots (independently of scheduled updates)
file_path = "./../"            #tell where local files are stored 
prod_file_path = "./Raw/"      #tell where production files are stored 


# In[ ]:





# In[ ]:


###########################################################################
# Geographical maps
# - of 1) all installations and 2) societaries in each cooperative
# - Uses Plotly/Mapbox and OpenStreetMap data
##################################################################################

def save_map(fig, filename):
    #Save map as png and html
    fig.write_image(file_path + filename + ".png")
    plotly.offline.plot(fig, filename = file_path + filename + ".html", auto_open=False, include_plotlyjs='https://cdn.plot.ly/plotly-mapbox-2.11.1.min.js')
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
                                hovertemplate='<b>%{text}</b><br>%{z} sociétaires <extra></extra>',text = df['nom']
                            ))

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(0,0,0,0)"
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
        x=0.01,
        bgcolor="rgba(0,0,0,0)"
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
d = datetime.now().strftime("%Y-%m-%d")

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
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    #fig.update_layout(title_text=titlename)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",bgcolor="rgba(0,0,0,0)",x=0,y=1))
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
        y=1, 
        bgcolor="rgba(0,0,0,0)"
    ))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
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

#Update only after 8am (UTC)
if datetime.now().hour >= 8:
    #Daily production for each site
    for row in range(0, len(cfg.df_sites)):
        df_prod=epices.get_data_prod_day(cfg.df_sites.iloc[row]['EPID'],d, cfg.df_sites.iloc[row]['PREFIX'], cfg)
        fig=plot_hist_prod(df_prod, "Historique journalier de production ("+cfg.df_sites.iloc[row]['SNAME']+", "+cfg.df_sites.iloc[row]['CITY']+")", 'utc_timestamps_Paris', 'Heures')
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX']+'_prod_today', file_path)
        save_prod_day_text(df_prod, cfg.df_sites.iloc[row]['PREFIX']+'_prod_today_tex')
        if row == 0:
            df_prodAll=df_prod
        df_prodAll['production_in_wh'] = df_prodAll['production_in_wh'] + df_prod['production_in_wh'] 
        
    #Total production of all sites
    fig=plot_hist_prod_only(df_prodAll, "Historique journalier de production", 'utc_timestamps_Paris', 'Heures')
    utils.save_fig(fig, 'All_prod_today', file_path)


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
        df_prod=epices.get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], nextcloud, prod_file_path,cfg)
        if days > 7 :
            df_prod['Date'] = pd.to_datetime(df_prod['utc_timestamps_Paris'],format='%Y-%m-%d')
            df_prod['Date']= df_prod['Date'].dt.strftime('%y-%m-%d')
            df_grouped=df_prod.groupby('Date').sum().reset_index()
            df_prod = pd.DataFrame(df_grouped)
        fig=plot_hist_prod_only(df_prod, "Historique " + str(days) + " derniers jours de production ("+cfg.df_sites.iloc[row]['SNAME']+", +"+cfg.df_sites.iloc[row]['CITY']+"+)", col_time, col_time_text)
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days), file_path)   
        
#Retreive and archive all data
def retreive_all_data(end_date):
    for row in range(len(cfg.df_sites)-2, len(cfg.df_sites)-1):        
        start_date = date(cfg.df_sites.iloc[row]['DATEINST'].year, cfg.df_sites.iloc[row]['DATEINST'].month,cfg.df_sites.iloc[row]['DATEINST'].day)
        df_prod=epices.get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], cfg.NEXTCLOUD, prod_file_path,cfg)

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
        y=1,
        bgcolor="rgba(0,0,0,0)"
    ))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
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
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", bgcolor="rgba(0,0,0,0)", x=0, y=1))
    return fig

def prod_hist_day(start_date, end_date, days):
    col_time = 'Date'
    col_time_text = 'Jours'
    cfg.df_sites['EH'] = 0
    meanAll = 0
    kwhAll = 0
    #Production of each site
    for row in range(0, len(cfg.df_sites)):
        df_prod=datastorage.get_data_prod_hist_day(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], prod_file_path, cfg)
        fig=plot_hist_prod_day(df_prod, "Historique " + str(days) + " derniers jours de production (" + cfg.df_sites.iloc[row]['SNAME'] + ", " + cfg.df_sites.iloc[row]['CITY'] + ")", col_time, col_time_text)
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days), file_path)
        mean=round(df_prod['unhabitants_equivalents'].mean(),1)
        #kwh=round(df_prod['total_production_in_wh'].sum(),1)
        kwh=round(df_prod['production_in_wh'].sum(),1)
        cfg.df_sites.loc[row,"EH"] = mean
        save_prod_hist_text(cfg.df_sites.iloc[row]['EPID'], mean, kwh, days, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_tex_" + str(days))
        if row == 0:
            df_prodAll = df_prod
        else:
            df_prodAll['unhabitants_equivalents'] = df_prodAll['unhabitants_equivalents'] + df_prod['unhabitants_equivalents']
            df_prodAll['production_in_wh'] = df_prodAll['production_in_wh'] + df_prod['production_in_wh']
        meanAll = meanAll + mean
        kwhAll = kwhAll + kwh
        
    #Total production for all sites
    fig=plot_hist_prod_day(df_prodAll, "Historique " + str(days) + " derniers jours de production", col_time, col_time_text)
    utils.save_fig(fig, "All-prod_hist_" + str(days), file_path) 
    
    #Mean equivalent habitants for all sites
    fig=plot_hist_prod_unhabitants()
    utils.save_fig(fig,"prod_hist_unhabitants", file_path)

#updates once a day at 4am (UTC)
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
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    #fig.update_xaxes(title_text = 'Jours', row=1, col=1)
    fig.update_yaxes(title_text="<b>Ensoleilement (W/m2)</b>",  color="rgb(37, 64, 143)", secondary_y=True, side='right')# row=1, col=1)
    fig.update_yaxes(title_text="<b>Nébulosité (%)</b>", color="red", secondary_y=False, side='left')# row=1, col=1)
    fig.update_xaxes(title_text = 'Jours')
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        x=0,
        y=1,
        bgcolor="rgba(0,0,0,0)"
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
        df_prod = weather.get_data_weather_hist(start_date, end_date, row, cfg)
        df_prodGHI=epices.get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], False, prod_file_path, cfg)
        df_prod['Date'] = pd.to_datetime(df_prod['dt'],unit='s', utc=True)
        df_prod['Date']=df_prod['Date'].dt.tz_convert('Europe/Paris')
        df_prod = df_prod.iloc[6:len(df_prod.index)-3] #remove first 6 and last 2 data points
        fig=plot_weather_hist(df_prod, df_prodGHI, "Historique meteo (" + cfg.df_sites.iloc[row]['SNAME'] +", " + cfg.df_sites.iloc[row]['CITY'] + ")")
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + '_weather_hist', file_path)


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
        y=1,
        bgcolor="rgba(0,0,0,0)"
    ))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    fig.update_xaxes(title_text = xlabel)

    # Set y-axes titles
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig.update_yaxes(title_text="<b></b>", color="rgb(108, 176, 65)", secondary_y=True, side='right')
    fig.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(108, 176, 65)", secondary_y=False, side='left')
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig

def plot_hist_prod_month_all():
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_prodWR['Date'],
            y=df_prodWR['production_in_wh']/1000000,
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
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", bgcolor="rgba(0,0,0,0)",x=0, y=1))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig.update_xaxes(title_text='')
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(136, 136, 136)")
    fig.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    return fig


def save_prod_hist_text_all(site, s, k, filename):
    text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea">Cette production correspond à la consommation hors chauffage et eau chaude sanitaire de ' + str(round(s/2.4)) + ' foyers, soit ' + str(round(s)) + ' habitants, sur la même période <a target="_parent" href="https://www.electrons-solaires93.org/#Explication_conso_moyenne">(*)</a>.</p></div></body></html>'
    file1 = open(file_path + filename + ".html","w", encoding='utf8')
    file1.write(text)
    file1.close() 
    
def save_prod_sinceinstall_text(k, filename):
    text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><center><h4 style="color:#6CB041">' + str(round(k/1000000,1)) + ' MWh </h4></center></body></html>'
    file1 = open(file_path + filename + ".html","w", encoding='utf8')
    file1.write(text)
    file1.close() 

#Updated once a day at 4am (UTC)
if datetime.now().hour == 4 or update_all == True:
    #Total production for each site
    fig_all_small = go.Figure()
    fig_all_large = go.Figure()
    kwhtot=0
    for row in range(0, len(cfg.df_sites)):
        df_prod=datastorage.get_all_data(cfg.df_sites.iloc[row]['PREFIX'], prod_file_path)
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
        utils.save_fig(fig,cfg.df_sites.iloc[row]['PREFIX'] + "_all_data", file_path)
        duration = (datetime.now()-cfg.df_sites.iloc[row]['DATEINST'])
        days = duration.days
        kwh=round(df_prod['production_in_wh'].sum(),1)
        EH = kwh / (float(cfg.EH_WhPerYear)/365.0 * days)     #inhabitant equivalent (1465 kWH / habitant / year)
        save_prod_hist_text_all(cfg.df_sites.iloc[row]['EPID'], EH, kwh, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_tex")
        save_prod_sinceinstall_text(kwh, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_sinceinstall_tex")
        kwhtot = kwhtot + kwh
        
        #filter dates (histogram over a 1 year window)
        a_year_ago = datetime.now() - timedelta(days=365)
        start_d = "{0}-{1:02}".format(a_year_ago.year-2000, a_year_ago.month)
        end_d = "{0}-{1:02}".format(datetime.now().year-2000, datetime.now().month)        
        after_start_date = df_prod['Date'] > start_d
        before_end_date = df_prod['Date'] <= end_d
        between_two_dates = after_start_date & before_end_date
        df_prod = df_prod.loc[between_two_dates]

        
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
    fig_all_small.update_xaxes(showgrid=False)
    fig_all_small.update_yaxes(showgrid=False)
    fig_all_large.update_xaxes(showgrid=False)
    fig_all_large.update_yaxes(showgrid=False)
    
    #All small sites (histograms side by side)
    fig_all_small.update_layout(legend=dict(orientation="h", yanchor="bottom", bgcolor="rgba(0,0,0,0)", x=0, y=1))
    fig_all_small.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig_all_small.update_xaxes(title_text='')
    fig_all_small.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig_all_small.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(136, 136, 136)")
    fig_all_small.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    utils.save_fig(fig_all_small,"All_data_all_small_sitesIDF", file_path)
    
    #All large_small sites (histograms side by side)
    fig_all_large.update_layout(legend=dict(orientation="h", yanchor="bottom", bgcolor="rgba(0,0,0,0)", x=0, y=1))
    fig_all_large.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    fig_all_large.update_xaxes(title_text='')
    fig_all_large.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig_all_large.update_yaxes(title_text="<b>Production (MWh)</b>", color="rgb(136, 136, 136)")
    fig_all_large.update_layout(font=dict(family="Roboto, sans-serif", size=12, color="rgb(136, 136, 136)"))
    utils.save_fig(fig_all_large,"All_data_all_large_sitesIDF", file_path)
    
    #All sites (cumulated)
    df_grouped=df_prodAll.groupby('Date').sum().reset_index()
    df_prodAll = pd.DataFrame(df_grouped)
    fig=plot_hist_prod_month(df_prodAll, "Historique (tous les sites)", "Mois")  
    utils.save_fig(fig, "All_data_all_sitesIDF_cumulated", file_path) 
    
    #Cumulated prod per coop
    for row in range(0, len(cfg.df_coops)):
        df = cfg.df_sites[cfg.df_sites['COOP'] == cfg.df_coops.iloc[row]['COOP']]
        for row_site in range(0, len(df)):
            df_prod=datastorage.get_all_data(df.iloc[row_site]['PREFIX'], prod_file_path)
            if row_site == 0:
                df_prodAll = df_prod
            else:
                df_prodAll = df_prodAll.append(df_prod)
        kwh = round(df_prodAll['production_in_wh'].sum(skipna = True),1)
        save_prod_sinceinstall_text(kwh, cfg.df_coops.iloc[row]['COOPSNAME'] + "-prod_sinceinstall_tex")



# In[ ]:


#########################################################################
# Extra text for IDF dashboard
# Table with characteristics of all sites
#########################################################################

df=cfg.df_sites.sort_values(by='COOP', ascending=True)
text = '<html><head><link type="text/css" rel="Stylesheet" href="' + cfg.ESCSS + '" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea"><table><tr><td rowspan="2"><b>Code</b></td><td rowspan="2"><b>Cooperative</b></td><td rowspan="2"><b>Site</b></td><td rowspan="2"><b>Adresse</b></td><td rowspan="2"><b>Installation</b></td><td rowspan="2"><b>Puiss.</b><br>(kWc)</td><td colspan="5"><b>Prod. Journalière</b> (kWh)</td><td rowspan="2"><b>Prod.<br>Totale</b><br>(MWh)</td></tr><tr><td>J</td><td>J-1</td><td>Moy.<br> 30 J.</td><td>Max.<br>30 J.</td><td>Max.</td></tr>'
tot_kwc = 0
tot_today = 0
tot_yesterday = 0
tot_total = 0
for row in range(0, len(df)):
    #prod total
    df_prod_all=datastorage.get_all_data(df.iloc[row]['PREFIX'], prod_file_path)
    if row == 0:
        df_prodAll = df_prod_all
    else:
        df_prodAll = df_prodAll.append(df_prod_all)
        
    # prod since install
    start_date = date(df.iloc[row]['DATEINST'].year, df.iloc[row]['DATEINST'].month, df.iloc[row]['DATEINST'].day)
    df_prod_allD=datastorage.get_data_prod_hist_day(start_date, end_date, df.iloc[row]['EPID'], df.iloc[row]['PREFIX'], prod_file_path, cfg)
    if row == 0:
        df_prodAllD = df_prod_allD
    else:
        df_prodAllD = df_prodAllD.append(df_prod_allD) 
        
    # prod yesterday
    thrity_days_ago = datetime.now() - timedelta(days=1)
    start_date = date(thrity_days_ago.year, thrity_days_ago.month, thrity_days_ago.day)
    df_prod_yesterday=datastorage.get_data_prod_hist_day(start_date, end_date, df.iloc[row]['EPID'], df.iloc[row]['PREFIX'], prod_file_path, cfg)
    if row == 0:
        df_prodYesterday = df_prod_yesterday
    else:
        df_prodYesterday = df_prodYesterday.append(df_prod_yesterday) 
        
    # prod 30 days
    thrity_days_ago = datetime.now() - timedelta(days=30)
    start_date = date(thrity_days_ago.year, thrity_days_ago.month, thrity_days_ago.day)
    df_prod_30=datastorage.get_data_prod_hist_day(start_date, end_date, df.iloc[row]['EPID'], df.iloc[row]['PREFIX'], prod_file_path, cfg)
    if row == 0:
        df_prod30 = df_prod_30
    else:
        df_prod30 = df_prod30.append(df_prod_30) 
        
    # prod today
    df_prod_today=epices.get_data_prod_day(df.iloc[row]['EPID'],d, df.iloc[row]['PREFIX'], cfg)
    if row == 0:
        df_prodToday=df_prod_today
    else:
        df_prodToday = df_prodToday.append(df_prod_today) 
        
    prod_today = df_prod_today['production_in_wh'].sum(skipna = True)
    prod_yesterday = df_prod_yesterday['production_in_wh'].sum(skipna = True)
    prod_avg_30 = df_prod_30['production_in_wh'].mean(skipna = True)
    prod_max_30 = df_prod_30['production_in_wh'].max(skipna = True)
    prod_max_all = df_prod_allD['production_in_wh'].max(skipna = True)
    prod_total = df_prod_all['production_in_wh'].sum(skipna = True)
    
    text = text + '<tr><td>' +  df.iloc[row]['PREFIX'] + '</td><td><a target="_blank" href="' + df.iloc[row]['COOPSITE'] + '">' + df.iloc[row]['COOP'] + '</a></td><td>' +  df.iloc[row]['LNAME'] + '</td><td>' +  df.iloc[row]['CITY'] + '</td><td>' +  str(df.iloc[row]['DATEINST'].year) + '-' + str(df.iloc[row]['DATEINST'].month).rjust(2, '0') + '-' + str(df.iloc[row]['DATEINST'].day).rjust(2, '0') + '</td><td style="text-align:right">' +  str(round(float(df.iloc[row]['PeakPW']),1))  + '</td><td style="text-align:right">' + str(round(prod_today/1000,1)) + '</td><td style="text-align:right">' + str(round(prod_yesterday/1000,1)) + '</td><td style="text-align:right">' + str(round(prod_avg_30/1000,1)) + '</td><td style="text-align:right">' + str(round(prod_max_30/1000,1)) + '</td><td style="text-align:right">' + str(round(prod_max_all/1000,1)) + '</td><td style="text-align:right">' + str(round(prod_total/1000000,1)) + '</td></tr>' 
    tot_kwc = tot_kwc + float(df.iloc[row]['PeakPW'])
    tot_today =  tot_today + prod_today
    tot_yesterday =  tot_yesterday + prod_yesterday
    tot_total = tot_total + prod_total
    
text = text + '<tr><td><b>Total</b></td><td></td><td></td><td></td><td></td><td style="text-align:right"><b>' +  str(round(tot_kwc,1)) + '</b></td><td style="text-align:right"><b>' +  str(round(tot_today/1000,1)) + '</b></td><td style="text-align:right"><b>' +  str(round(tot_yesterday/1000,1)) + '</b></td><td></td><td></td><td></td><td style="text-align:right"><b>' +  str(round(tot_total/1000000,1)) + '</b></td></tr>' 
text = text + '</table></body></html>' 
filename = "sites"    
file1 = open(file_path + filename + ".html","w", encoding='utf8')
file1.write(text)
file1.close()
    
    
prod_total_all = df_prodAll['production_in_wh'].sum(skipna = True)
prod_yesterday = df_prodYesterday['production_in_wh'].sum(skipna = True)
prod_month = df_prod30['production_in_wh'].sum(skipna = True)
prod_today = df_prodToday['production_in_wh'].sum(skipna = True)
    
filename = "Dashboard-prod-today-yesterday-month"
text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea">- ce jour : ' + str(round(prod_today/1000,1)) + ' KWh<br>- hier : ' + str(round(prod_yesterday/1000,1)) + ' KWh<br>- 30 derniers jours : ' + str(round(prod_month/1000000,1)) + ' MWh<br>- centrales en service : ' + str(len(cfg.df_sites)) + '</div></body></html>'
file1 = open(file_path + filename + ".html","w", encoding='utf8')
file1.write(text)
file1.close() 

filename = "Dashboard-prod-since-origin"
text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><h3 style="color:#6CB041">Production cumulée de toutes les centrales : ' + str(round(prod_total_all/1000000,1)) + ' MWh<span>&#42;</span></h3></body></html>'
file1 = open(file_path + filename + ".html","w", encoding='utf8')
file1.write(text)
file1.close() 


# In[ ]:




