import pandas as pd

import ee
from ee_change_detection import ChangeDetector

# initialize ee library
ee.Initialize()
# authenticate earth engine (only need to do this once per session)
ee.Authenticate()

years = ['2016']

# load counties and include the state names
counties = pd.read_csv('./data/counties_without_geometry.csv')[['ADM2_NAME', 'ADM1_NAME']]

# initialize ChangeDetector class 
change_detector = ChangeDetector()
for index, row in list(counties.iterrows())[:2]:
	for year in years:
		try:
			change = change_detector.compute_change_in_county(county=row['ADM2_NAME'], 
															  state=row['ADM1_NAME'], 
															  year=year)
			print(change)
		except Exception as e: print(e)



# load zipcodes 
zipcodes = pd.read_csv('./data/zipcodes_without_geometry.csv')['ZCTA5CE10']

for index, row in list(zipcodes.iterrows())[:2]:
	for year in years:
		try:
			change = change_detector.compute_change_in_zipcode(zipcode=zipcode['ZCTA5CE10'], 
															  year=year)
			print(change)
		except Exception as e: print(e)

