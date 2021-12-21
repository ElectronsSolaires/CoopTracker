#!/usr/bin/env python3
##########################################################################################
# CoopTracker
# Copyright © 2021 Électrons solaires (https://www.electrons-solaires93.org/)
# Contacts: Jeremie L, Jean-Marie B. (Électrons solaires, webmestre@electrons-solaires93.org)
# License: CC-BY-SA 4.0
##########################################################################################

import locale
import pandas as pd
from datetime import datetime, date, timedelta

mapbox_access_token = 'XXXXX'
locale.setlocale(locale.LC_ALL, 'fr_FR')
NEXTCLOUD = False
NEXTCLOUD_USERNAME = ''
NEXTCLOUD_PASSWORD = ''
NEXTCLOUD_REPO= ''
token_epice = {'Authorization' : 'Token XXXXX'}
APIK_OWM='XXXXX'
WD_ID=1639 # Waldeck-Rousseau/1639
JZ_ID=4737 # Jean Zay/4737
ESCSS = 'https://www.electrons-solaires93.org/wp-content/themes/ample-pro/style.css'
CSV_SOCIETARIES = 'https://www.electrons-solaires93.org/data/societaires.csv'
COOPNAME = "Electrons Solaires"
COOPLAT = 48.886905793549025
COOPLON = 2.4480045203663135
GEOJSON_DATA = "93.geojson"
EH_WhPerYear = 1465000 #inhabitant equivalent (1465 kWH / habitant / year)
df_sites = pd.DataFrame(columns=['COOP', 'COOPSITE', 'EPID', 'SNAME', 'LNAME', 'TYPE', 'DATEINST', 'CITY','LAT','LON','PeakPW', 'CSV_Societaries'])

# Electrons Solaires
df_sites = df_sites.append({'COOP':'Electrons Solaires', 'COOPSITE':'https://www.electrons-solaires93.org', 'EPID': '1639', 'PREFIX':'WD', 'SNAME': 'Waldeck-Rousseau', 'LNAME': 'Ecole Waldeck-Rousseau', 'TYPE':'Ecole élémentaire', 'DATEINST': datetime(2021, 2, 10, 0,0,0), 'CITY':'Les Lilas', 'LAT':'48.88189202996699','LON':'2.41970629674966', 'PeakPW':'37.4', 'CSV_Societaries':'https://www.electrons-solaires93.org/data/societaires.csv'}, ignore_index=True)
df_sites = df_sites.append({'COOP':'Electrons Solaires', 'COOPSITE':'https://www.electrons-solaires93.org', 'EPID': '4737', 'PREFIX':'JZ', 'SNAME': 'Jean-Zay', 'LNAME': 'Collège Jean Zay', 'TYPE':'Collège', 'DATEINST': datetime(2021, 6, 30, 0,0,0), 'CITY':'Bondy', 'LAT':'48.91104259300344','LON':'2.48140405564623', 'PeakPW':'99.4', 'CSV_Societaries':'https://www.electrons-solaires93.org/data/societaires.csv'}, ignore_index=True)
