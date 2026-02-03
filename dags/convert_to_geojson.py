import geopandas as gpd

# Ler shapefile
gdf = gpd.read_file('BR_UF_2024/BR_UF_2024.shp')
gdf = gdf.to_crs("EPSG:4326")

# Salvar como GeoJSON
gdf.to_file('BR_UF_2024.geojson', driver='GeoJSON')