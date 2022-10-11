"""
Objective: get the mean dynamic world probabilities for ameriflux data
"""
import ee
service_account = "calucapstone@ee-calucapstone.iam.gserviceaccount.com"
credentials = ee.ServiceAccountCredentials(service_account, '.private-key.json')
ee.Initialize(credentials)

# Load the LatLng table
pt_table = ee.FeatureCollection('projects/ee-calucapstone/assets/wanted_sites_asset')

years = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']

part_of_year = [
	('01-01', '03-01'),
	('03-02', '05-31'),
	('06-01', '09-30'),
	('10-01', '12-31'),
]

for year in years[0:1]:
	for month_day in part_of_year[0:1]:
		# Filter Dynamic World to the desired time and space
		dwCol = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filter(ee.Filter.date(year+month_day[0], year+month_day[1]))

		# Compute the mean dynamic world probabilities for a latlng over time and space
		def zonalStats(ft):
		  # Get LatLng from row of table. Create geometry from it.
		  geometry = ee.Geometry.Point([ft.get('LONGITUDE'), ft.get('LATITUDE')])
		  # Create a polygon around the point
		  geometryBuffered = ee.Feature(geometry).buffer(20).bounds().geometry()
		  # Filter the Dynamic World collection to this smaller area
		  dwArea = dwCol.filter(ee.Filter.bounds(geometry))
		  # Reduce the collection to one image by taking the mean across time
		  meanImg = dwArea.reduce(ee.Reducer.mean()).clip(geometryBuffered)
		  # Reduce the image to one by taking the mean across space
		  averages = meanImg.reduceRegion(reducer=ee.Reducer.mean(),scale= 10)
		  f = ee.Feature(geometry, averages)
		  return f.set('SITE_ID', ft.get('SITE_ID'))


		# Call zonalStats on every row of the table
		latLngStats = pt_table.map(zonalStats)

		# Export to table
		task = ee.batch.Export.table.toDrive(
		  collection= latLngStats,
		  description='DW_Mean_'+year+'_'+month_day[0],
		  fileNamePrefix= 'DW_MEAN_'+year+month_day[0]+'_'+month_day[1]+'test',
		  fileFormat= 'CSV')
		task.start()
