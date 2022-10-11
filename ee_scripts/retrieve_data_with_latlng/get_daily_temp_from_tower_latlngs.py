"""
Objective: get weather data every day for every site
"""
import ee
service_account = "calucapstone@ee-calucapstone.iam.gserviceaccount.com"
credentials = ee.ServiceAccountCredentials(service_account, '.private-key.json')
ee.Initialize(credentials)


north_america = ee.ImageCollection("IDAHO_EPSCOR/GRIDMET")
                          .filter(ee.Filter.date('2016-01-01', '2022-08-01')).select([
                          'tmmn',
                           'tmmx',
                           'pr',
                           'rmax',
                           'rmin',
                          ]);

# Load the LatLng table
# TODO: UPDATE THIS! We want SITE_ID and DATE so we don't have to get unnecessary data
pt_table = ee.FeatureCollection("projects/ee-calucapstone/assets/wanted_sites_asset")

# Compute the mean temperature
def zonalStats(ft):
  # Get LatLng from row of table. Create geometry from it.
  geometry = ee.Geometry.Point([ft.get("LONGITUDE"), ft.get("LATITUDE")])

  # Create a polygon around the point
  geometryBuffered = ee.Feature(geometry).buffer(1000).bounds().geometry()
  boundedCollection =  north_america.filter(ee.Filter.bounds(geometryBuffered))
  
  reducedImgs = boundedCollection.map(function(image):
    means = image.reduceRegion(reducer=ee.Reducer.mean(), 
                             geometry=geometryBuffered)
    return ee.Feature(geometryBuffered, means).set("date",ee.Algorithms.String(ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')), "SITE_ID",ft.get("SITE_ID"))
  )
  return reducedImgs

us_stats = pt_table.map(zonalStats).flatten()

task = ee.batch.Export.table.toDrive(
		  collection= us_stats,
		  description='temperature_for_towers',
		  fileNamePrefix= 'daily_temperature_for_towers',
		  fileFormat= 'CSV')

task.start()
