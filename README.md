# CoopTracker 
Ce code met à jour en continu des graphiques pour suivre la production de centrales solaires gérées par le logiciel [Epices](https://www.epices-energie.fr/fr/). Il a été développé  au sein des [Electrons Solaires](https://www.electrons-solaires93.org), une coopérative citoyenne créée par des citoyens engagés qui installe des centrales photo-voltaïques dans la communauté de communes [Est Ensemble](https://www.est-ensemble.fr) en région parisienne. 

Ce code lit les données en provenance de plusieurs sources externes:
- L'API [Epices](https://www.epices-energie.fr/fr/) 
- [OpenWeatherMap](https://openweathermap.org)

Puis il produit des graphiques et du texte sur :
- l'historique de production 
- la production du jour
- l'historique météo 
- la répartition géographique des sociétaires

Le code existe en deux versions:
- pour une coopérative, par exemple les Electrons Solaires (cooptracker.py)
- pour un ensemble de coopératives, par exemple celles d'Ile de France (cooptracker_EP.py)

Vous trouverez des exemples de rendu ici:
- https://www.electrons-solaires93.org/
- https://www.electrons-solaires93.org/productionwaldeckrousseau/
- https://www.electrons-solaires93.org/productionjeanzay/
- https://www.electrons-solaires93.org/devenir-societaire/ (carte des sociétaires)

Voici des exemples de graphiques pour les coopératives d'Ile de France avec le soutien d'[Energie Partagée](https://energie-partagee.org):
- https://energie-partagee.ddns.net/IDF/

Le tableau de bord suivant présente des données des [Electrons Solaires](https://www.electrons-solaires93.org), de [EnerCit'IF](https://enercitif.org), de [Plaine Energie Citoyenne](https://www.plaine-energie-citoyenne.fr) et de [Sud Paris Soleil](https://sudparis-soleil.fr):
- https://energie-partagee.ddns.net/dashboard/

## Licence
Tout le contenu est sous licence [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Documentation
### Pre-requis
Le code est developpé en Python 3 avec les packages suivants: Plotly, Pandas, Requests, Kaleido, Json, Datetime. 

### Dépot de code
Ce dépot est organisé de la manière suivante:

```
CoopTracker
└─── README.md
└─── CC-BY-SA-4.0.txt
└───src
    └───cooptracker.py and .ipynb -> Jupyter Notebook et le fichier .py correspondant
    └───config.py -> Contient les clés, accés et paramètres de configuration
    └───cooptracker_EP.py and .ipynb -> Jupyter Notebook et le fichier .py correspondant
    └───config_EP.py -> Contient les clés, accés et paramètres de configuration
└───ES -> données d'entrée spécifiques pour Electrons Solaires
    └───93.geojson -> Polygones pour les villes de Seine Saint-Denis (93)
    └───idf.geojson -> Polygones pour les villes de Ile de France    
    └───convert.py -> Utilitaire pour extraire les données geojson
└───EP -> données d'entrée spécifiques aux centrales d'Ile de France soutenues par Energie Partagée
    └───93.geojson -> Polygones pour les villes de Seine Saint-Denis (93)
    └───94.geojson -> Polygones pour les villes du Val de Marne (94)
    └───IDF_filtered.geojson -> Polygones pour les villes de Ile de France (Paris, 93 et 94)  
    └───arrondissements.geojson -> Polygones pour les arrondissements de Paris
    └───cooperatives.csv -> descriptions de l'implantation géographique des coopératives 
```

### Configuration
Pour utiliser CoopTracker, vous devez suivre les étapes suivantes:
 1. Configurer [Epices](https://www.epices-energie.fr/fr/) pour activer l'API
 2. Collecter les clés d'API et les accés pour :
- [Epices](https://www.epices-energie.fr/fr/): système de supervision PV.  
- [OpenWeatherMap](https://openweathermap.org): données météo libres (jour,  3 derniers jours).  
- Votre instance [NextCloud](https://nextcloud.com): pour archiver les données en JSON (optionel).
- [Mapbox](https://www.mapbox.com): librairie de cartographie. 
 3. Remplir config.py avec vos clés / accés. 
 4. Remplir config.py avec le DataFrame df_sites qui contient les données des sites de production
 5. Executer cooptracker.py sur votre  machine ou serveur favori. 

## Contact
Le code est la doc. Mais si vous avez des questions / des suggestions, ou si vous souhaitez contribuer, vous pouvez nous contacter ici:
- webmestre@electrons-solaires93.org

