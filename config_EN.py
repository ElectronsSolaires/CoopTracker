 #!/usr/bin/env python3
##########################################################################################
# CoopTracker
#  - Dashboard for Enercitif
#    All cooperatives are mentored by Energie Partagée: https://energie-partagee.org
# License: CC-BY-SA 4.0
##########################################################################################

import locale
import pandas as pd
from datetime import datetime
import auth as auth

mapbox_access_token = auth.mapbox_access_token
locale.setlocale(locale.LC_ALL, 'fr_FR')
NEXTCLOUD = False
NEXTCLOUD_USERNAME = ''
NEXTCLOUD_PASSWORD = ''
NEXTCLOUD_REPO= ''
token_epice = auth.token_epice
APIK_OWM=auth.APIK_OWM
EH_WhPerYear = 1465000 #inhabitant equivalent (1465 kWH / habitant / year)


###########################
# Cooperatives
###########################
df_coops = pd.DataFrame(columns=['COOP', 'COOPSNAME', 'COOPSITE', 'LAT', 'LON', 'GEOJSON', 'CSV_Societaries'])
df_coops = df_coops.append({'COOP':"EnerCit'IF", 'COOPSNAME':'EN', 'COOPSITE':'https://enercitif.org', 'LAT':'48.856800698876825','LON':'2.339480252881264', 'GEOJSON':'arrondissements.geojson', 'CSV_Societaries':'http://jeremie.leguay.free.fr/ES/societairesEN.csv'}, ignore_index=True)

###########################
# Sites
###########################
df_sites = pd.DataFrame(columns=['COOP', 'COOPSITE', 'EPID', 'SNAME', 'LNAME', 'TYPE', 'DATEINST', 'CITY','LAT','LON','PeakPW'])

# Enercitif
df_sites = df_sites.append({'COOP':"EnerCit'IF",  'COOPSITE':'https://enercitif.org', 'EPID': '5126', 'PREFIX':'T0001', 'SNAME': 'Parmentier', 'LNAME': 'Ecole Parmentier', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 11, 16, 0,0,0), 'CITY':'Paris, 75010', 'LAT':'48.87197','LON':'2.369587', 'PeakPW':'99'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3549', 'PREFIX':'T0002', 'SNAME': 'Emile Anthoine', 'LNAME': 'Centre Sportif Emile Anthoine', 'TYPE':'Centre Sportif', 'DATEINST': datetime(2021, 4, 20, 0,0,0), 'CITY':'Paris, 75015', 'LAT':'48.8557293055556','LON':'2.29115902777778', 'PeakPW':'99.2'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '4825', 'PREFIX':'T0003', 'SNAME': 'Lamoricière', 'LNAME': 'Ecole élémentaire Lamoricière', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2022, 2, 10, 0,0,0), 'CITY':'Paris, 75012', 'LAT':'48.844902','LON':'2.412325', 'PeakPW':'30'}, ignore_index=True)
#df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3555', 'PREFIX':'EN04', 'SNAME': 'Elsa Triolet', 'LNAME': 'Collège Elsa Triolet', 'TYPE':'Collège', 'DATEINST': datetime(2021, 1, 15, 0,0,0), 'CITY':'Paris, 75013', 'LAT':'48.8310904722222','LON':'2.36230730555556', 'PeakPW':'96.2'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3543', 'PREFIX':'T0005', 'SNAME': 'Maurice Genevoix', 'LNAME': 'Ecole Maurice Genevoix', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 1, 6, 0,0,0), 'CITY':'Paris, 75018', 'LAT':'48.894423','LON':'2.36056925', 'PeakPW':'35.6'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3559', 'PREFIX':'T0006', 'SNAME': 'André Citroën', 'LNAME': 'Collège André Citroën', 'TYPE':'Collège', 'DATEINST': datetime(2021, 2, 10, 0,0,0), 'CITY':'Paris, 75015', 'LAT':'48.8392859444444','LON':'2.27844536111111', 'PeakPW':'35.8'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF",  'COOPSITE':'https://enercitif.org','EPID': '3545', 'PREFIX':'T0007', 'SNAME': 'Georges Brassens', 'LNAME': 'Collège Georges Brassens', 'TYPE':'Collège', 'DATEINST': datetime(2021, 1, 6, 0,0,0), 'CITY':'Paris, 75019', 'LAT':'48.8845927777778','LON':'2.38651155555556', 'PeakPW':'35.2'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3560', 'PREFIX':'T0008', 'SNAME': 'Louis Lumière', 'LNAME': "Centre d'animation Louis Lumière", 'TYPE':"Centre d'animation", 'DATEINST': datetime(2021, 2, 25, 0,0,0), 'CITY':'Paris, 75020', 'LAT':'48.86040575','LON':'2.41169213888889', 'PeakPW':'35.8'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '4801', 'PREFIX':'T0009', 'SNAME': 'Maryse Hilsz', 'LNAME': 'Ecole Maryse Hilsz', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 7, 27, 0,0,0), 'CITY':'Paris, 75020', 'LAT':'48.8506346220386','LON':'2.41327161226846', 'PeakPW':'35.6'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org', 'EPID': '5442', 'PREFIX':'T0102', 'SNAME': 'Nativité', 'LNAME': 'HLM rue de la Nativité', 'TYPE':'HLM', 'DATEINST': datetime(2022, 2, 14, 0,0,0), 'CITY':'Paris, 75012','LAT':'48.835225','LON':'2.386057', 'PeakPW':'36.0'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org', 'EPID': '5445', 'PREFIX':'T0103', 'SNAME': 'Curial', 'LNAME': 'HLM Rue Curial', 'TYPE':'HLM', 'DATEINST': datetime(2022, 2, 16, 0,0,0), 'CITY':'Paris, 75018','LAT':'48.89','LON':'2.37', 'PeakPW':'34.1'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '5321', 'PREFIX':'T0106', 'SNAME': 'Evangile', 'LNAME': "Ecole élémentaire de l'Evangile", 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2022, 1, 12, 0,0,0), 'CITY':'Paris, 75018', 'LAT':'48.895577','LON':'2.3629', 'PeakPW':'35.7'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '5322', 'PREFIX':'T0105', 'SNAME': 'Le Cargo', 'LNAME': "Hôtel d'entreprises Le Cargo", 'TYPE': "Hôtel d'entreprises", 'DATEINST': datetime(2022, 2, 8, 0,0,0), 'CITY':'Paris, 75019', 'LAT':'48.88','LON':'2.38', 'PeakPW':'113.78'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '5635', 'PREFIX':'T0107', 'SNAME': 'Panoyaux', 'LNAME': "HLM Panoyaux", 'TYPE': "HLM", 'DATEINST': datetime(2022, 3, 10, 0,0,0), 'CITY':'Paris, 75020', 'LAT':'48.87','LON':'2.39', 'PeakPW':'9.0'}, ignore_index=True)
