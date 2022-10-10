# Objective: get the elevation from latitude and longitude

import ee
service_account = "calucapstone@ee-calucapstone.iam.gserviceaccount.com"
credentials = ee.ServiceAccountCredentials(service_account, '.private-key.json')
ee.Initialize(credentials)

# Load the LatLng table
pt_table = ee.FeatureCollection('projects/ee-calucapstone/assets/wanted_sites_asset')

us_elevation = ee.Image('USGS/3DEP/10m')

# Compute the mean elevation in area
def zonalStats (ft):
  # Get LatLng from row of table. Create geometry from it.
  geometry = ee.Geometry.Point([ft.get('LONGITUDE'),ft.get('LATITUDE')])
  # Create a polygon around the point
  geometryBuffered = ee.Feature(geometry).buffer(5).bounds().geometry()

  # Reduce the image to one by taking the mean across space
  average = us_elevation.clip(geometryBuffered).reduceRegion(reducer=ee.Reducer.mean(),scale=5)
   
  # Create and return a feature 
  # (this is an EE requirement)
  f =  ee.Feature(geometry, average)

  # Set site id so we can join the data later
  f = f.set('SITE_ID', ft.get('SITE_ID'))

  return f


us_stats = pt_table.map(zonalStats)

# Export to table
task = ee.batch.Export.table.toDrive(
  collection=us_stats,
  description='elevation_for_towers',
  fileNamePrefix='elevation_for_towers_in_us_10m_test',
  fileFormat='csv')

task.start()