# %%
#importando libs
import ee
from geemap import Map, ee_export_image

# %%
#Inicializando o gee
service_account = 'testscheduler@tfg-gee-scheduler.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'google-credentials.json')
ee.Initialize(credentials)

# %%
#Carregando limites do municipio de santo Antonio
roi = ee.FeatureCollection('projects/tfg-gee-scheduler/assets/limiteSantoAntonio')

# %%
#Centralizando o mapa na longitude/latitude/zoom desejados
mapObject = Map(center=[-20.95,-44.92],zoom=11)

# %%
#Obtendo as imagens da coleção
img = (ee.ImageCollection('LANDSAT/LC08/C01/T1_RT_TOA')
.filterMetadata('CLOUD_COVER', 'less_than', 50)
.filterDate('2019-11-01', '2020-11-30')
.mosaic()
.clip(roi))

# %%
#Função NDVI
ndvi = img.normalizedDifference(['B5', 'B4'])
#Expressão NDVI QUAD
ndviQUAD = img.expression(
  ' - 8.712 + (17.325 * ndvi) - (8.739 * ndvi**2) ',
  {
    'ndvi': ndvi,    
  })

# %%
#Adicionando Layer ao mapa de vizualização
paleta = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
               '004C00', '023B01', '012E01', '011D01', '011301']
vis_params1 = {
  'min': -10,
  'max': 1,
  'palette': paleta
}
mapObject.addLayer(ndviQUAD, vis_params1, 'NDVI')

# %%
#Adicionando segundo Layer
vis_params2 = {
  'bands': ['B5', 'B4', 'B2'],
  'max': 1,
  'gamma': 1
}
mapObject.addLayer(img, vis_params2)

# %%
from datetime import datetime
imgName = './images/STA_NDVI_date.tif'
now = datetime.now()
now_string = now.strftime("%d_%m_%Y_%H:%M:%S")
imgName = imgName.replace('date',now_string)

# %%

ee_export_image(img, imgName, scale=90, crs=None, region=roi.geometry(), file_per_band=False)


