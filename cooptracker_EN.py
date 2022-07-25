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

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, date, timedelta
import epices
import datastorage
import utils
import config_EN as cfg        #file containing API keys / credentials / configuration
update_all = True          #update all plots (independently of scheduled updates)
file_path = "./temp/"            #tell where local files are stored
prod_file_path = "./Raw/"      #tell where production files are stored 

init_site = ['T0102']

year=datetime.now().year
month=datetime.now().month
day=datetime.now().day
today = date(year, month, day)

#########################################################################
# Init site data
#########################################################################

for row in range(0, len(cfg.df_sites)):
    site = cfg.df_sites.iloc[row]
    if(site['PREFIX'] in init_site):
        print('Init site data ' + str(site['PREFIX']))
        epices.retreive_all_data(site,today,cfg,prod_file_path)

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



#Update only after 8am (UTC)
if datetime.now().hour >= 8:
    #Daily production for each site
    for row in range(0, len(cfg.df_sites)):
        print('Plotting daily production for site: ' + str(cfg.df_sites.iloc[row]['PREFIX']))
        df_prod=epices.get_data_prod_day(cfg.df_sites.iloc[row]['EPID'],d, cfg.df_sites.iloc[row]['PREFIX'],cfg)
        fig=plot_hist_prod(df_prod, "Historique journalier de production ("+cfg.df_sites.iloc[row]['SNAME']+", "+cfg.df_sites.iloc[row]['CITY']+")", 'utc_timestamps_Paris', 'Heures')
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX']+'_prod_today',file_path)


# In[16]:


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
        print('Plotting 3days production for site: ' + str(cfg.df_sites.iloc[row]['PREFIX']))
        df_prod=epices.get_data_prod_hist(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], nextcloud, prod_file_path,cfg)
        if days > 7 :
            df_prod['Date'] = pd.to_datetime(df_prod['utc_timestamps_Paris'],format='%Y-%m-%d')
            df_prod['Date']= df_prod['Date'].dt.strftime('%y-%m-%d')
            df_grouped=df_prod.groupby('Date').sum().reset_index()
            df_prod = pd.DataFrame(df_grouped)
        fig=plot_hist_prod_only(df_prod, "Historique " + str(days) + " derniers jours de production ("+cfg.df_sites.iloc[row]['SNAME']+", +"+cfg.df_sites.iloc[row]['CITY']+"+)", col_time, col_time_text)
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days), file_path)

#updated once a day at 2am
if datetime.now().hour == 2 or update_all == True:
    past_days_ago = datetime.now() - timedelta(days=3)
    start_date = date(past_days_ago.year, past_days_ago.month, past_days_ago.day)
    prod_hist(start_date, end_date, 3)


# In[17]:


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

def prod_hist_day(start_date, end_date, days):
    col_time = 'Date'
    col_time_text = 'Jours'
    cfg.df_sites['EH'] = 0
    #Production of each site
    for row in range(0, len(cfg.df_sites)):
        print('Plotting 30days production for site: ' + str(cfg.df_sites.iloc[row]['PREFIX']))
        df_prod=datastorage.get_data_prod_hist_day(start_date, end_date, cfg.df_sites.iloc[row]['EPID'], cfg.df_sites.iloc[row]['PREFIX'], prod_file_path, cfg)
        fig=plot_hist_prod_day(df_prod, "Historique " + str(days) + " derniers jours de production (" + cfg.df_sites.iloc[row]['SNAME'] + ", " + cfg.df_sites.iloc[row]['CITY'] + ")", col_time, col_time_text)
        utils.save_fig(fig, cfg.df_sites.iloc[row]['PREFIX'] + "-prod_hist_" + str(days),file_path)

#updates once a day at 4am (UTC)
if datetime.now().hour == 4 or update_all == True:
    thrity_days_ago = datetime.now() - timedelta(days=30)
    start_date = date(thrity_days_ago.year, thrity_days_ago.month, thrity_days_ago.day)
    prod_hist_day(start_date, end_date, 30)


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



#uUdated once a day at 4am (UTC)
if datetime.now().hour == 4 or update_all == True:
    #Total production for each site
    for row in range(0, len(cfg.df_sites)):
        print('Plotting historical production for site: ' + str(cfg.df_sites.iloc[row]['PREFIX']))
        df_prod=datastorage.get_all_data(cfg.df_sites.iloc[row]['PREFIX'], prod_file_path)
        fig=plot_hist_prod_month(df_prod, "Historique (" + cfg.df_sites.iloc[row]['SNAME'] + ")", "Mois")
        utils.save_fig(fig,cfg.df_sites.iloc[row]['PREFIX'] + "_all_data",file_path)

