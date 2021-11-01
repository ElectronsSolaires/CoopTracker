# CoopTracker 
Ce code met à jour en continu des graphiques pour suivre la production de centrales solaires gérées par le logiciel [Epices](https://www.epices-energie.fr/fr/). Il a été developé initialement au sein des [Electrons Solaires](https://www.electrons-solaires93.org), une coopérative citoyenne créé par des citoyens engagés qui installe des centrales photo-voltaïques dans la communauté de communes [Est Ensemble](https://www.est-ensemble.fr) en région parisienne. 

Ce code lit les données en provenance de plusieurs sources externes:
- L'API [Epices](https://www.epices-energie.fr/fr/) 
- [OpenWeatherMap](https://openweathermap.org)

Puis il produit des graphiques sur :
- l'historique de production 
- la production du jour
- l'historique météo 
- la distribution géographique des sociétaires

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
|
└───src
    └───cooptracker.py and .ipynb  ->  Jupyter Notebook et le fichier .py correspondant
|
└───ES -> données d'entrée spécifiques à Electrons Solaires
    └───93.geojson  ->  Polygones pour les villes de Seine Saint-Denis (93)
    └───idf.geojson  ->  Polygones pour les villes de Ile de France    
    └───convert.py ->  Utilitaire pour extraire les données
```

### Configuration
Pour utiliser CoopTracker, vous devez suivre les étapes suivantes:
 1. Configurer [Epices](https://www.epices-energie.fr/fr/) pour activater l'API
 2. Collecter les clés d'API et les accés pour :
- [Epices](https://www.epices-energie.fr/fr/): système de supervision PV.  
- [OpenWeatherMap](https://openweathermap.org): données météo libres (jour,  3 derniers jours).  
- Votre instance [NextCloud](https://nextcloud.com): pour archiver les données en JSON (optionel).
- [Mapbox](https://www.mapbox.com): librairie de cartographie. 
 3. Remplir config.py avec vos clés / accés. 
 4. Remplir config.py avec le DataFrame df_sites qui contient les données des sites de production
 5. Executer cooptracker.py sur votre serveur favori 

## Contact
Le code est la doc. Mais si vous avez des questions, vous pouvez nous contacter ici:
- webmestre@electrons-solaires93.org

### TODO

- Configurer les plots plotly en Francais
