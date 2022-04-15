#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##########################################################################################
# CoopTracker
#  - Dashboard for one cooperative 
# Copyright © 2021 Électrons solaires (https://www.electrons-solaires93.org/)
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

import config as cfg           #file containing API keys / credentials / configuration
update_all = True              #update all plots (independently of scheduled updates)
file_path = "./../"            #tell where local files are stored 
prod_file_path = "./Raw/"      #tell where production files are stored 


# In[ ]:


###########################################################################
# Geographical map of societaries
# - Reads societaires.csv file with "nom;code_commune;Societaires" fields
# - Uses Plotly/Mapbox and OpenStreetMap data
##################################################################################

#Updated once a day at 3am (UTC)
if datetime.now().hour == 3 or update_all == True:
    #Get CSV from URL
    r = requests.request(
        method='get',
        url= cfg.CSV_SOCIETARIES
    )
    df = pd.read_csv(StringIO(r.text),sep=';') 

    #Load GeoJSON data (polygones)
    with open(file_path + cfg.GEOJSON_DATA) as response:
        cities = json.load(response)

    data = go.Scattermapbox(lat=list(cfg.df_sites['LAT']),
                            lon=list(cfg.df_sites['LON']),
                            mode='markers+text',
                            marker_size=14,
                            marker_color='rgb(39, 97, 44)',
                            showlegend=True, 
                            name='Centrales ' + cfg.COOPNAME,
                            textposition='top right',
                            textfont=dict(size=12, color='rgb(39, 97, 44)'),
                            text=cfg.df_sites['LNAME'])

    layout = dict(margin=dict(l=0, t=0, r=0, b=0, pad=0),
                mapbox=dict(zoom=11, 
                            accesstoken=cfg.mapbox_access_token,
                            center = {"lat": cfg.COOPLAT, "lon": cfg.COOPLON},
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

    #Save map as png and html
    filename = 'societaires'
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
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",bgcolor="rgba(0,0,0,0)", x=0,y=1))
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
    file1 = open(file_path + filename + ".html","w", encoding='utf8')
    file1.write(text)
    file1.close()

#Update only after 8am (UTC)
if datetime.now().hour >= 8:
    #Daily production for each site
    for row in range(0, len(cfg.df_sites)):
        df_prod=epices.get_data_prod_day(cfg.df_sites.iloc[row]['EPID'],d, cfg.df_sites.iloc[row]['PREFIX'],cfg)
        fig=plot_hist_prod(df_prod, "Historique journalier de production ("+cfg.df_sites.iloc[row]['SNAME']+", "+cfg.df_sites.iloc[row]['CITY']+")", 'utc_timestamps_Paris', 'Heures')
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX']+'_prod_today',file_path)
        save_prod_day_text(df_prod, cfg.df_sites.iloc[row]['PREFIX']+'_prod_today_tex')
        if row == 0:
            df_prodAll=df_prod
        df_prodAll['production_in_wh'] = df_prodAll['production_in_wh'] + df_prod['production_in_wh'] 
        
    #Total production of all sites
    fig=plot_hist_prod_only(df_prodAll, "Historique journalier de production", 'utc_timestamps_Paris', 'Heures')
    utils.save_fig(fig, 'All_prod_today',file_path)


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
        fig=utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days), file_path)        

#updated once a day at 2am
if datetime.now().hour == 2 or update_all == True:
    past_days_ago = datetime.now() - timedelta(days=3)
    start_date = date(past_days_ago.year, past_days_ago.month, past_days_ago.day)
    prod_hist(start_date, end_date, 3)


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
    text=""
    if int(site) == cfg.WR_ID:
        text='<html><head><link type="text/css" rel="Stylesheet" href="' + cfg.ESCSS + '" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"> <div class="textarea">Cette production correspond à la consommation hors chauffage et eau chaude sanitaire de ' + str(round(s/2.4)) + ' foyers, soit ' + str(round(s)) + ' habitants, sur les ' + str(d) + ' derniers jours <a target="_parent" href="https://www.electrons-solaires93.org/productionwaldeckrousseau/#Explication_conso_moyenne">(*)</a>.</p></div></body></html>'
    elif int(site) == cfg.JZ_ID:
        text='<html><head><link type="text/css" rel="Stylesheet" href="' + cfg.ESCSS + '" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"> <div class="textarea">Cette production correspond à la consommation hors chauffage et eau chaude sanitaire de ' + str(round(s/2.4)) + ' foyers, soit ' + str(round(s)) + ' habitants, sur les ' + str(d) + ' derniers jours <a target="_parent" href="https://www.electrons-solaires93.org/productionjeanzay/#Explication_conso_moyenne">(*)</a>.</p></div></body></html>'    
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
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom",bgcolor="rgba(0,0,0,0)", x=0, y=1))
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
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days),file_path)
        mean=round(df_prod['unhabitants_equivalents'].mean(),1)
        kwh=round(df_prod['production_in_wh'].sum(),1)
        cfg.df_sites.loc[row,"EH"] = mean
        save_prod_hist_text(cfg.df_sites.iloc[row]['EPID'], mean, kwh, days, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_tex_" + str(days))
        if row == 0:
            df_prodAll = df_prod
        df_prodAll['unhabitants_equivalents'] = df_prodAll['unhabitants_equivalents'] + df_prod['unhabitants_equivalents']
        df_prodAll['production_in_wh'] = df_prodAll['production_in_wh'] + df_prod['production_in_wh']
        meanAll = meanAll + mean
        kwhAll = kwhAll + kwh
    #Total production for all sites
    fig=plot_hist_prod_day(df_prodAll, "Historique " + str(days) + " derniers jours de production", col_time, col_time_text)
    utils.save_fig(fig, "All-prod_hist_" + str(days),file_path) 
    
    #Mean equivalent habitants for all sites
    fig=plot_hist_prod_unhabitants()
    utils.save_fig(fig,"prod_hist_unhabitants",file_path)

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
    #fig = make_subplots(specs=[[{"secondary_y": True}],[{"secondary_y": True}]], rows=2, cols=1)
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
            #legendgroup = '1'
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
            #legendgroup = '1'
        ),secondary_y=False)# row=1, col=1)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    #fig.update_xaxes(title_text = 'Jours', row=1, col=1)
    fig.update_yaxes(title_text="<b>Ensoleilement (W/m2)</b>",  color="rgb(37, 64, 143)", secondary_y=True, side='right')# row=1, col=1)
    fig.update_yaxes(title_text="<b>Nébulosité (%)</b>", color="red", secondary_y=False, side='left')# row=1, col=1)
    #fig = fig.update_layout(specs=[[{"secondary_y": True}]], row=2, col=1)
    #fig.add_trace(
    #    go.Line(
    #        x=df_prod['Date'],
    #        y=df_prod['temp'],
    #        name="température (°C)",
    #        line=dict(color='rgb(108, 176, 65)'),
    #        legendgroup = '2'
    #    ), 
    #    secondary_y=True, row=2, col=1)
    #fig.add_trace(
    #    go.Line(
    #        x=df_prod['Date'],
    #        y=df_prod['pressure'],
    #        name="pression (hPa)",
    #        line=dict(color='black'),
    #        legendgroup = '2'
    #    ), 
    #    secondary_y=False, row=2, col=1)
    fig.update_xaxes(title_text = 'Jours')# row=2, col=1)
    #fig.update_yaxes(title_text="<b>Température (°C)</b>", color="rgb(108, 176, 65)", secondary_y=True, row=2, col=1)
    #fig.update_yaxes(title_text="<b>Pression (hPa)</b>", color="black", secondary_y=False, row=2, col=1)
    #fig.update_layout(legend_tracegroupgap = 200)
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
        df_prod = weather.get_data_weather_hist(start_date, end_date, row,cfg)
        df_prodGHI=epices.get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], False, prod_file_path, cfg)
        df_prod['Date'] = pd.to_datetime(df_prod['dt'],unit='s', utc=True)
        df_prod['Date']=df_prod['Date'].dt.tz_convert('Europe/Paris')
        df_prod = df_prod.iloc[6:len(df_prod.index)-3] #remove first 6 and last 2 data points
        fig=plot_weather_hist(df_prod, df_prodGHI, "Historique meteo (" + cfg.df_sites.iloc[row]['SNAME'] +", " + cfg.df_sites.iloc[row]['CITY'] + ")")
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + '_weather_hist',file_path)


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

def plot_hist_prod_month_all(df_prodWR, df_prodJZ):
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
    text=''
    if int(site) == cfg.WR_ID:
        text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea">Cette production correspond à la consommation hors chauffage et eau chaude sanitaire de ' + str(round(s/2.4)) + ' foyers, soit ' + str(round(s)) + ' habitants, sur la même période <a target="_parent" href="https://www.electrons-solaires93.org/productionwaldeckrousseau/#Explication_conso_moyenne">(*)</a>.</p></div></body></html>'
    elif int(site) == cfg.JZ_ID:
        text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea">Cette production correspond à la consommation hors chauffage et eau chaude sanitaire de ' + str(round(s/2.4)) + ' foyers, soit ' + str(round(s)) + ' habitants, sur la même période <a target="_parent" href="https://www.electrons-solaires93.org/productionjeanzay/#Explication_conso_moyenne">(*)</a>.</p></div></body></html>'    
    else:
        #text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea">' + round(str(k/1000000),1) + ' MWh correspond à la consommation hors chauffage et eau chaude sanitaire de ' + str(round(s/2.4)) + ' foyers, soit ' + str(round(s)) + ' habitants, sur la même période <a target="_parent" href="https://www.electrons-solaires93.org/#Explication_conso_moyenne">(*)</a>.</p></div></body></html>'
        text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><center><h4 style="color:#6CB041">' + str(round(k/1000000,1)) + ' MWh </h4></center></body></html>'
    file1 = open(file_path + filename + ".html","w", encoding='utf8')
    file1.write(text)
    file1.close() 

#uUdated once a day at 4am (UTC)
if datetime.now().hour == 4 or update_all == True:
    #Total production for each site
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
            df_prodJZ = df_prod
        if cfg.df_sites.iloc[row]['PREFIX'] == "WR":
            df_prodWR = df_prod
        fig=plot_hist_prod_month(df_prod, "Historique (" + cfg.df_sites.iloc[row]['SNAME'] + ")", "Mois")  
        utils.save_fig(fig,cfg.df_sites.iloc[row]['PREFIX'] + "_all_data",file_path)
        duration = (datetime.now()-cfg.df_sites.iloc[row]['DATEINST'])
        days = duration.days
        if cfg.df_sites.iloc[row]['PREFIX'] == "WR":
            daysWR =days
        kwh=round(df_prod['production_in_wh'].sum(),1)
        EH = kwh / (float(cfg.EH_WhPerYear)/365.0 * days)     #inhabitant equivalent (1465 kWH / habitant / year)
        save_prod_hist_text_all(cfg.df_sites.iloc[row]['EPID'], EH, kwh, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_tex")
        #save_prod_hist_text_all(-1, EH, kwh, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_tex")

    #All sites
    fig=plot_hist_prod_month_all(df_prodWR,df_prodJZ)
    utils.save_fig(fig,"All_data_all_sites", file_path)
    kwh=round(df_prodWR['production_in_wh'].sum(),1) + round(df_prodJZ['production_in_wh'].sum(),1)
    EH = kwh / (float(cfg.EH_WhPerYear)/365.0 * daysWR)   #inhabitant equivalent 
    save_prod_hist_text_all(-1,EH, kwh, "All-prod_hist_tex")


# In[ ]:


#############################################################
# Content for monthly publishing (social networks...)
#############################################################
if datetime.now().hour == 4 or update_all == True:
    today = datetime.now()
    end_lastMonth = today.replace(day=1)
    start_lastMonth = (end_lastMonth - timedelta(days=1)).replace(day=1)    
    end_lastMonth = date(end_lastMonth.year, end_lastMonth.month, end_lastMonth.day)
    start_lastMonth = date(start_lastMonth.year, start_lastMonth.month, start_lastMonth.day)
    month = start_lastMonth.strftime("%Y-%m")
    col_time = 'Date'
    col_time_text = 'Jours'
    kwhAll = 0
    #Production of each site
    df_prodAll = pd.DataFrame()
    for row in range(0, len(cfg.df_sites)):
        df_prod = pd.DataFrame()
        for single_date in utils.daterange(start_lastMonth, end_lastMonth):
            d = single_date.strftime("%Y-%m-%d")
            each_file = "{0}-{1}-prod.json".format(cfg.df_sites.iloc[row]['PREFIX'],d)
            with open(prod_file_path + each_file) as response:
                prod = json.load(response)
                df_prod = df_prod.append(prod['site_hourly_production']['hourly_productions'])
        df_prod['utc_timestamps_Paris'] = pd.to_datetime(df_prod['utc_timestamps'])
        df_prod['utc_timestamps_Paris']=df_prod['utc_timestamps_Paris'].dt.tz_convert('Europe/Paris')
        df_prod['Date'] = df_prod['utc_timestamps_Paris'].dt.strftime('%y-%m-%d')
        df_grouped=df_prod.groupby('Date').sum().reset_index()
        df_prod = pd.DataFrame(df_grouped)
        kwh=round(df_prod['production_in_wh'].sum(),1)
        if row == 0:
            df_prodAll = df_prod
        else:
            df_prodAll['production_in_wh']  = df_prodAll['production_in_wh'] + df_prod['production_in_wh']
        kwhAll = kwhAll + kwh
    #Total production for all sites
    df_prodAll['unhabitants_equivalents'] = df_prodAll['production_in_wh'] / (float(cfg.EH_WhPerYear)/365.0)
    fig=plot_hist_prod_day(df_prodAll.dropna(how='any'), "Historique de production", col_time, col_time_text)
    utils.save_fig(fig, "All-prod_hist_last_month", file_path) 

    filename = "All-prod_hist_last_month_text"
    text='<html><head><link type="text/css" rel="Stylesheet" href="'+cfg.ESCSS+'" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body style="background-color:white;"><div class="textarea"><h3 style="color:#6CB041">Production du mois ' + month + ' : ' + str(round(kwhAll/1000000,1)) + ' MWh</h3><iframe scrolling="no" style="height:400px; width: 600px"  frameborder="0"  src="All-prod_hist_last_month.html">Browser not compatible.</iframe></div></body></html>'
    file1 = open(file_path + filename + ".html","w", encoding='utf8')
    file1.write(text)
    file1.close() 



# In[ ]:




