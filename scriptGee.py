# %%
#importando libs
import ee
from geemap import Map, ee_export_image
import datetime

from api.service.map import retrieve_dates

def getTifImage(start_date, end_date):
  #Inicializando o gee
  service_account = 'testscheduler@tfg-gee-scheduler.iam.gserviceaccount.com'
  credentials = ee.ServiceAccountCredentials(service_account, 'google-credentials.json')
  ee.Initialize(credentials)

  
  #Carregando limites do municipio de santo Antonio
  roi = ee.FeatureCollection('projects/tfg-gee-scheduler/assets/limiteSantoAntonio')


  #Centralizando o mapa na longitude/latitude/zoom desejados
  mapObject = Map(center=[-20.95,-44.92],zoom=11)


  #Obtendo as imagens da coleção
  img = (ee.ImageCollection('LANDSAT/LC08/C02/T1_RT_TOA')
  .filterMetadata('CLOUD_COVER', 'less_than', 50)
  .filterDate(start_date, end_date)
  .mosaic()
  .clip(roi))


  #Função NDVI
  ndvi = img.normalizedDifference(['B5', 'B4'])
  #Expressão NDVI QUAD
  ndviQUAD = img.expression(
    ' - 8.712 + (17.325 * ndvi) - (8.739 * ndvi**2) ',
    {
      'ndvi': ndvi,    
    })


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


  #Adicionando segundo Layer
  vis_params2 = {
    'bands': ['B5', 'B4', 'B2'],
    'max': 1,
    'gamma': 1
  }
  mapObject.addLayer(img, vis_params2)



  imgName = 'STA_NDVI_date.tif'
  now = datetime.datetime.now()
  now_string = now.strftime("%d_%m_%Y")
  imgName = imgName.replace('date',now_string)
  pathImg = './images/'+imgName

  import boto3
  session = boto3.session.Session()
  from decouple import config
  s3 = session.client(
      service_name='s3',
      aws_access_key_id=config('aws_access_key_id'),
      aws_secret_access_key=config('aws_secret_access_key')
  )

  ee_export_image(ndviQUAD, pathImg, scale=30, crs=None, region=roi.geometry())

  with open(pathImg, "rb") as f:
      s3.upload_fileobj(f, 'bucket-regador', imgName)

dates = retrieve_dates()
today = datetime.datetime.today()
lastImg = max(dates)
dayDiff = today - lastImg
if(dayDiff.days >= 17):
  getTifImage((lastImg+datetime.timedelta(days=1)).strftime("%Y-%m-%d") , (today+datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
else:
  print(f'Ainda faltam ${17 - dayDiff.days} dias para atualização das imagems do LANDSAT8')