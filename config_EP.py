 #!/usr/bin/env python3
##########################################################################################
# CoopTracker
#  - Dashboard for multiple cooperatives in Ile de France
#    All cooperatives are mentored by Energie Partagée: https://energie-partagee.org
# Copyright © 2021-2022 Électrons solaires (https://www.electrons-solaires93.org/)
# Contacts: Jeremie L, Jean-Marie B. (Électrons solaires, webmestre@electrons-solaires93.org)
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
token_epice =  auth.token_epice
APIK_OWM=auth.APIK_OWM
ESCSS = 'https://www.electrons-solaires93.org/wp-content/themes/ample-pro/style.css'
CSV_COOPS = 'cooperatives.csv'
GEOJSON_DATA_IDF = "IDF_filtered.geojson"
EH_WhPerYear = 1465000 #inhabitant equivalent (1465 kWH / habitant / year)

###########################
# Cooperatives
###########################
df_coops = pd.DataFrame(columns=['COOP', 'COOPSNAME', 'COOPSITE', 'LAT', 'LON', 'GEOJSON', 'CSV_Societaries'])
df_coops = df_coops.append({'COOP':'Electrons Solaires', 'COOPSNAME':'ES', 'COOPSITE':'https://www.electrons-solaires93.org',  'LAT':'48.886905793549025','LON':'2.4480045203663135', 'GEOJSON':'93.geojson', 'CSV_Societaries':'https://www.electrons-solaires93.org/data/societaires.csv'}, ignore_index=True)
df_coops = df_coops.append({'COOP':"EnerCit'IF", 'COOPSNAME':'EN', 'COOPSITE':'https://enercitif.org', 'LAT':'48.856800698876825','LON':'2.339480252881264', 'GEOJSON':'arrondissements.geojson', 'CSV_Societaries':'http://jeremie.leguay.free.fr/ES/societairesEN.csv'}, ignore_index=True)
df_coops = df_coops.append({'COOP':"Plaine Energie Citoyenne", 'COOPSNAME':'PEC', 'COOPSITE':'https://www.plaine-energie-citoyenne.fr', 'LAT':'48.927904500740645','LON':'2.3432568031675585', 'GEOJSON':'93.geojson', 'CSV_Societaries':'http://jeremie.leguay.free.fr/ES/societairesPEC.csv'}, ignore_index=True)
df_coops = df_coops.append({'COOP':"Sud Paris Soleil", 'COOPSNAME':'SPS', 'COOPSITE':'https://sudparis-soleil.fr', 'LAT':'48.78559575575932','LON':'2.324374052123191', 'GEOJSON':'94.geojson', 'CSV_Societaries':'http://jeremie.leguay.free.fr/ES/societairesSPS.csv'}, ignore_index=True)


###########################
# Sites
###########################
df_sites = pd.DataFrame(columns=['COOP', 'COOPSITE', 'EPID', 'SNAME', 'LNAME', 'TYPE', 'DATEINST', 'CITY','LAT','LON','PeakPW'])
# Electrons Solaires
df_sites = df_sites.append({'COOP':'Electrons Solaires', 'COOPSITE':'https://www.electrons-solaires93.org', 'EPID': '1639', 'PREFIX':'WR', 'SNAME': 'Waldeck-Rousseau', 'LNAME': 'Ecole Waldeck-Rousseau', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 2, 10, 0,0,0), 'CITY':'Les Lilas', 'LAT':'48.88189202996699','LON':'2.41970629674966', 'PeakPW':'35.7'}, ignore_index=True)
df_sites = df_sites.append({'COOP':'Electrons Solaires', 'COOPSITE':'https://www.electrons-solaires93.org', 'EPID': '4737', 'PREFIX':'JZ', 'SNAME': 'Jean-Zay', 'LNAME': 'Collège Jean Zay', 'TYPE':'Collège', 'DATEINST': datetime(2021, 6, 30, 0,0,0), 'CITY':'Bondy', 'LAT':'48.91104259300344','LON':'2.48140405564623', 'PeakPW':'99.4'}, ignore_index=True)

# Enercitif
df_sites = df_sites.append({'COOP':"EnerCit'IF",  'COOPSITE':'https://enercitif.org', 'EPID': '5126', 'PREFIX':'T0001', 'SNAME': 'Parmentier', 'LNAME': 'Ecole Parmentier', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2022, 6, 9, 0,0,0), 'CITY':'Paris, 75010', 'LAT':'48.87197','LON':'2.369587', 'PeakPW':'99'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3549', 'PREFIX':'T0002', 'SNAME': 'Emile Anthoine', 'LNAME': 'Centre Sportif Emile Anthoine', 'TYPE':'Centre Sportif', 'DATEINST': datetime(2021, 4, 20, 0,0,0), 'CITY':'Paris, 75015', 'LAT':'48.8557293055556','LON':'2.29115902777778', 'PeakPW':'99.2'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '4825', 'PREFIX':'T0003', 'SNAME': 'Lamoricière', 'LNAME': 'Ecole élémentaire Lamoricière', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2022, 2, 10, 0,0,0), 'CITY':'Paris, 75012', 'LAT':'48.844902','LON':'2.412325', 'PeakPW':'30'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3555', 'PREFIX':'T0004', 'SNAME': 'Elsa Triolet', 'LNAME': 'Collège Elsa Triolet', 'TYPE':'Collège', 'DATEINST': datetime(2022, 7, 8, 0,0,0), 'CITY':'Paris, 75013', 'LAT':'48.8310904722222','LON':'2.36230730555556', 'PeakPW':'96.2'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3543', 'PREFIX':'T0005', 'SNAME': 'Maurice Genevoix', 'LNAME': 'Ecole Maurice Genevoix', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 1, 6, 0,0,0), 'CITY':'Paris, 75018', 'LAT':'48.894423','LON':'2.36056925', 'PeakPW':'35.6'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3559', 'PREFIX':'T0006', 'SNAME': 'André Citroën', 'LNAME': 'Collège André Citroën', 'TYPE':'Collège', 'DATEINST': datetime(2021, 2, 10, 0,0,0), 'CITY':'Paris, 75015', 'LAT':'48.8392859444444','LON':'2.27844536111111', 'PeakPW':'35.8'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF",  'COOPSITE':'https://enercitif.org','EPID': '3545', 'PREFIX':'T0007', 'SNAME': 'Georges Brassens', 'LNAME': 'Collège Georges Brassens', 'TYPE':'Collège', 'DATEINST': datetime(2021, 1, 6, 0,0,0), 'CITY':'Paris, 75019', 'LAT':'48.8845927777778','LON':'2.38651155555556', 'PeakPW':'35.2'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '3560', 'PREFIX':'T0008', 'SNAME': 'Louis Lumière', 'LNAME': "Centre d'animation Louis Lumière", 'TYPE':"Centre d'animation", 'DATEINST': datetime(2021, 2, 25, 0,0,0), 'CITY':'Paris, 75020', 'LAT':'48.86040575','LON':'2.41169213888889', 'PeakPW':'35.8'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '4801', 'PREFIX':'T0009', 'SNAME': 'Maryse Hilsz', 'LNAME': 'Ecole Maryse Hilsz', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 7, 27, 0,0,0), 'CITY':'Paris, 75020', 'LAT':'48.8506346220386','LON':'2.41327161226846', 'PeakPW':'35.6'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org', 'EPID': '5442', 'PREFIX':'T0102', 'SNAME': 'Nativité', 'LNAME': 'HLM rue de la Nativité', 'TYPE':'HLM', 'DATEINST': datetime(2022, 2, 14, 0,0,0), 'CITY':'Paris, 75012','LAT':'48.835225','LON':'2.386057', 'PeakPW':'36.0'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org', 'EPID': '5445', 'PREFIX':'T0103', 'SNAME': 'Curial', 'LNAME': 'HLM Rue Curial', 'TYPE':'HLM', 'DATEINST': datetime(2022, 2, 16, 0,0,0), 'CITY':'Paris, 75018','LAT':'48.89','LON':'2.37', 'PeakPW':'34.1'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '5321', 'PREFIX':'T0106', 'SNAME': 'Evangile', 'LNAME': "Ecole élémentaire de l'Evangile", 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2022, 1, 12, 0,0,0), 'CITY':'Paris, 75018', 'LAT':'48.895577','LON':'2.3629', 'PeakPW':'35.7'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '5322', 'PREFIX':'T0105', 'SNAME': 'Le Cargo', 'LNAME': "Hôtel d'entreprises Le Cargo", 'TYPE': "Hôtel d'entreprises", 'DATEINST': datetime(2022, 2, 8, 0,0,0), 'CITY':'Paris, 75019', 'LAT':'48.88','LON':'2.38', 'PeakPW':'113.78'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '5635', 'PREFIX':'T0101', 'SNAME': 'Panoyaux', 'LNAME': "HLM Panoyaux", 'TYPE': "HLM", 'DATEINST': datetime(2022, 4, 19, 0,0,0), 'CITY':'Paris, 75020', 'LAT':'48.87','LON':'2.39', 'PeakPW':'9.0'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"EnerCit'IF", 'COOPSITE':'https://enercitif.org','EPID': '6202', 'PREFIX':'T0107', 'SNAME': 'Partants', 'LNAME': "HLM Partants", 'TYPE': "HLM", 'DATEINST': datetime(2022, 11, 5, 0,0,0), 'CITY':'Paris, 75020', 'LAT':'48.87','LON':'2.4', 'PeakPW':'36.0'}, ignore_index=True)

# ENERGIE PARTAGEE INVESTISSEMENT
df_sites = df_sites.append({'COOP':"Energie Partagee", 'COOPSITE':'https://energie-partagee.org/','EPID': '509', 'PREFIX':'BM', 'SNAME': 'Mantois', 'LNAME': "Biocoop Du Mantois", 'TYPE': "Entreprise", 'DATEINST': datetime(2011, 5, 5, 0,0,0), 'CITY':'Épône, 78680', 'LAT':'48.96040344','LON':'1.81361103', 'PeakPW':'60.0'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"Energie Partagee", 'COOPSITE':'https://energie-partagee.org/','EPID': '856', 'PREFIX':'HP', 'SNAME': 'Pajol', 'LNAME': "Halle Pajol", 'TYPE': "ZAC", 'DATEINST': datetime(2013, 3, 26, 0,0,0), 'CITY':'Paris, 75018', 'LAT':'48.888352','LON':'2.362944', 'PeakPW':'465.1'}, ignore_index=True)
df_sites = df_sites.append({'COOP':"Energie Partagee", 'COOPSITE':'https://energie-partagee.org/','EPID': '857', 'PREFIX':'QT', 'SNAME': 'Quintessence', 'LNAME': "Copro Quintessence", 'TYPE': "Copro", 'DATEINST': datetime(2012, 9, 18, 0,0,0), 'CITY':'Paris, 75017', 'LAT':'48.890868','LON':'2.316446', 'PeakPW':'95.6'}, ignore_index=True)

# PLAINE ÉNERGIE CITOYENNE
df_sites = df_sites.append({'COOP':"Plaine Energie Citoyenne", 'COOPSITE':'https://www.plaine-energie-citoyenne.fr','EPID': '4218', 'PREFIX':'PCE01', 'SNAME': 'Jean Jaurès', 'LNAME': 'Ecole Jean Jaurès', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 9, 21, 0,0,0), 'CITY':'Épinay sur Seine', 'LAT':'48.9549477430581','LON':'2.32497286901782', 'PeakPW':'78.5'}, ignore_index=True)
# Sud Paris Soleil
df_sites = df_sites.append({'COOP':"Sud Paris Soleil", 'COOPSITE':'https://sudparis-soleil.fr','EPID': '4011', 'PREFIX':'SPS01', 'SNAME': 'La Plaine', 'LNAME': 'Ecole La Plaine', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 4, 21, 0,0,0), 'CITY':'Cachan', 'LAT':'48.786118','LON':'2.333903', 'PeakPW':'99.8'}, ignore_index=True)

