import geojson,geopandas

#https://perso.esiee.fr/~courivad/python_bases/15-geo.html
# filtrage
#c = geopandas.read_file("/Users/leguay/Desktop/Electrons/Python/idf.geojson")
c = geopandas.read_file("datagouv-communes.geojson")

#for dpt in ["93"]:
#    c_idf = c_idf.append(c[c["CODE"].str.startswith(dpt)])
c_idf = c[c["code_commune"].str.startswith("93")]

# écriture des données filtrées
with open("/Users/leguay/Desktop/Electrons/Python/93.geojson", "w") as f:
    geojson.dump(c_idf, f)
