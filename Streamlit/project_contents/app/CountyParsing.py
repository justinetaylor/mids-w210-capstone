from operator import sub
import pandas as pd
import numpy as np
import json
from bokeh.models import GeoJSONDataSource
import math
import geemap
import pandas as pd
import ee 
from area_change import AreaChange
import joblib
import nltk
import sklearn

def plot(lat, lng, pa): #terrain
    """This function will render a Google Map using the Bokeh library"""
    
    # Default map options
    zoom=14
    map_type='satellite'
    
    # Create Geojson Polygon object
    geojson_site = {
      'type': 'FeatureCollection', 
      'features':[{
          'type': 'Feature',
          'geometry': {
            'type': 'Polygon',
            'coordinates': pa
          }
      }]
    }

    # 'coordinates': [[[ pa[0][0], pa[0][1] ], [ pa[1][0], pa[1][1] ], [ pa[2][0], pa[2][1] ], [ pa[3][0], pa[3][1] ]]]
    
    # Create GeoJSONDataSource to render polygon on gmap
    geo_source = GeoJSONDataSource(geojson=json.dumps(geojson_site))

    return geo_source

# Read in json data form text file and do work with it
with open('NorthernCaliforniaCounties.txt') as f: #project_contents/app/NorthernCaliforniaCounties.txt
    data = json.load(f)
    county = "Sonoma" # Contra Costa (44x1) Glenn (1x1923x2) Yuba (1,4355,2)
    num_counties = len(data["features"])
    county_list = list()
    county_coordinates_list = list()

    # Get list of counties
    for i in range(num_counties):
        county_list.append(data["features"][i]["properties"]["ADM2_NAME"])

    county_list.sort()

    # Get coordinates for county
    for i in range(num_counties):
        if data["features"][i]["properties"]["ADM2_NAME"] == county:

            if "coordinates" in data["features"][i]["geometry"]:

                county_coordinates = np.array(data["features"][i]["geometry"]["coordinates"])

                print("success, first level presence of coordinates:", county_coordinates.shape)
                
                if len(county_coordinates.shape) == 2:

                    num_coordinates = county_coordinates.shape[0]
                    transformed_coordinates = list()
                    print("Number of coordinates:", num_coordinates)

                    for i in range(num_coordinates):

                        # Get the sub array of coordinates
                        sub_coordinates = county_coordinates[i]

                        transformed_coordinates.extend(sub_coordinates[0])

                        print("Length of sub coordinates:", sub_coordinates.shape[0])

                        #if i == 1:
                        #    print(sub_coordinates[0])
                        #    print("only 2 here")
                        #    print(transformed_coordinates)
                        print(i)

                    print("length of transformed coordinates:", len(transformed_coordinates))
                    wrapping_list = list()
                    wrapping_list.append(transformed_coordinates)

                    print("transformed length", len(wrapping_list))

                    county_coordinates_array = np.asarray(transformed_coordinates)
                    center_county = county_coordinates_array.mean(axis=0)
                    lat_center = float(center_county[1])
                    lon_center = float(center_county[0])
                    geo_json_results = plot(lat_center, lon_center, transformed_coordinates)

                    print(lat_center)
                    print(lon_center)
                    print(geo_json_results)

                else:

                    # Run plot command to generage geo_json data structure
                    #print(county_coordinates_2)
                    #print("untransformed length", len(transformed_coordinates))

                    # Extract data directly into array and lists
                    county_coordinates_list = data["features"][i]["geometry"]["coordinates"]
                    county_coordinates_array = np.array(data["features"][i]["geometry"]["coordinates"])

                    # Computer center of the county
                    center_county = county_coordinates_array[0].mean(axis=0)
                    lat_center = float(center_county[1])
                    lon_center = float(center_county[0])

                    geo_json_results = plot(lat_center, lon_center, county_coordinates_list)

                    print(lat_center)
                    print(lon_center)
                    print(geo_json_results)

            else:
                print("failure, no first level coordinates")

                county_coordinates = np.array(data["features"][i]["geometry"]["geometries"])
                num_geometries = county_coordinates.shape[0]

                # Enumerate through list of geometries
                for i in range(num_geometries):
                   # Get the sub array of coordinates and append to single growing list
                   sub_coordinates = county_coordinates[i]["coordinates"]
                   
                   num_sub_coordinates = len(sub_coordinates[0])

                   if num_sub_coordinates == 2:
                       #print(sub_coordinates[0])
                       #print(num_sub_coordinates)
                       county_coordinates_list.extend(sub_coordinates)
                   else:
                       county_coordinates_list.extend(sub_coordinates[0])
                   
                   #for j in range(num_sub_coordinates):
                   #    print(sub_coordinates[0][j])
                   #    county_coordinates_list.extend(sub_coordinates[0][j])
                     
                # Conver list to array to compute center lat and lon
                wrapping_list = list()
                wrapping_list.append(county_coordinates_list)
                county_coordinates_array = np.asarray(county_coordinates_list)

                print(county_coordinates_array)

                center_county = county_coordinates_array.mean(axis=0)
                lat_center = float(center_county[1])
                lon_center = float(center_county[0])

                # Call plot function to create the Bokeh Google Map
                geo_json_results = plot(lat_center, lon_center, wrapping_list)

                print(lat_center)
                print(lon_center)
                print(geo_json_results)
                

    # Test pa
    #pa = np.array([["-122.267", "37.875"], ["-122.266", "37.87"], ["-122.257", "37.87"], ["-122.259", "37.873"]])
    #coordinates = [[[ pa[0][0], pa[0][1] ], [ pa[1][0], pa[1][1] ], [ pa[2][0], pa[2][1] ], [ pa[3][0], pa[3][1] ]]]
    #print("type of pa", type(coordinates))

#print("setting geometry")
#geometry =  transformed_coordinates
#geometry =  [[-124.14507547221648, 41.11806816998926],
#          [-124.14507547221648, 41.11457637941072],
#          [-124.1394964774655, 41.11457637941072],
#          [-124.1394964774655, 41.11806816998926]]
#print(geometry)
#print("geometry set")
#year_list = [2017, 2018, 2019, 2020, 2021]

#with open(r'sonoma_geometry.txt', 'w') as fp:
#    fp.write(str(geometry))

# Create an instance of AreaChange class
#ac = AreaChange()

# Estimate the area of vegetation change for each type
#change_list = ac.get_area_of_change(geometry, year)

#print(change_list)

# get all data needed for inference
#result = ac.get_climate_data_for_change(geometry, year)

# examine results
#print(result.describe())

#print("Number of days", len(result['gridmet_date'].unique()))
#result['latlng_pair'] = result['latitude'].apply(str) +  result['longitude'].apply(str)
#print("Number of pixels that changed", len(pd.unique(result['latlng_pair'])))   

#result.drop(columns=['gridmet_date', 'change', 'quarter'], inplace=True) # 'gridmet_date', 'change', 'quarter', 'latlng_pair', 
#result = result.reindex(columns=['srad', 'tmmn', 'tmmx', 'vpd', 'Fpar_500m', 'Lai_500m', 'latitude', 'longitude', 'elevation', 'water_mean', 'trees_mean', 'grass_mean', 'flooded_vegetation_mean', 'crops_mean', 'shrub_and_scrub_mean', 'built_mean', 'bare_mean', 'snow_and_ice_mean', 'label_mode'])
#result['Fpar_500m'] = result['Fpar_500m'].astype("float64")
#result['Lai_500m'] = result['Lai_500m'].astype("float64")
#result['label_mode'] = result['label_mode'].astype("category")

#result.rename(columns={"latitude": "LATITUDE_x", "longitude": "LONGITUDE_x", "elevation": "ee_elevation", "label_mode": "label_argmax_numeric"}, inplace=True)

#print(result.columns)

#np_result = result.to_numpy()
#print("Shape of results", np_result.shape)


#print('The nltk version is {}.'.format(nltk.__version__))
#print('The scikit-learn version is {}.'.format(sklearn.__version__))

#print(np_result[0:20,])
#print(result.dtypes)

#saved_knn = joblib.load('GPP_boost_mod.pkl')

#saved_knn.predict(np_result[0:20,])
#predicted_results = saved_knn.predict(result)
#print(predicted_results.shape)
#print(predicted_results[0:10,])

print("1. Setting geometry")

geometry =  [[-124.14507547221648, 41.11806816998926],
          [-124.14507547221648, 41.11457637941072],
          [-124.1394964774655, 41.11457637941072],
          [-124.1394964774655, 41.11806816998926]]

print("type of geometry", type(geometry))

print("2. Get biome data and run model predictions")

year_list = [2017, 2018, 2019, 2020, 2021]
result_list = []
area_change_list = []

# Load model
saved_knn = joblib.load('GPP_boost_mod.pkl')

# Get biome data and run predictions for all 5 years
for i in range(len(year_list)):

    ac = AreaChange()
    year = year_list[i]

    change_list = change_list = ac.get_area_of_change(geometry, year)
    area_change_list.append(change_list)

    print("Area change for year", year, "is:")
    print(change_list)

    result = ac.get_climate_data_for_change(geometry, year)

    #print(result.describe())

    result = result.reindex(columns=['srad', 'tmmn', 'tmmx', 'vpd', 'Fpar_500m', 'Lai_500m', 'latitude', 'longitude', 'elevation', 'water_mean', 'trees_mean', 'grass_mean', 'flooded_vegetation_mean', 'crops_mean', 'shrub_and_scrub_mean', 'built_mean', 'bare_mean', 'snow_and_ice_mean', 'label_mode'])
    result['Fpar_500m'] = result['Fpar_500m'].astype("float64")
    result['Lai_500m'] = result['Lai_500m'].astype("float64")
    result['label_mode'] = result['label_mode'].astype("category")
    result.rename(columns={"latitude": "LATITUDE_x", "longitude": "LONGITUDE_x", "elevation": "ee_elevation", "label_mode": "label_argmax_numeric"}, inplace=True)

    print("Size of data for year", year, "is:", len(result))

    predicted_results = saved_knn.predict(result)

    print("Number of model predictions for year", year, "is", predicted_results.shape)
    
    GPP_value = np.sum(predicted_results)
    result_list.append(GPP_value)

    #result["GPP_Prediction"] = predicted_results.tolist()
    #print(result["label_argmax_numeric"].unique())

    print("GPP for year", year, "is", GPP_value)


# Where 0-10 have the following mapping:
# 0  other
# 1  trees_gained
# 2  grass_gained
# 3  flooded_vegetation_gained
# 4  crops_gained
# 5  shrub_and_scrub_gained
# 6  trees_lost
# 7  grass_lost
# 8  flooded_veg_lost
# 9  crops_lost
# 10 shrub_and_scrub_lost

sum_trees = 0
sum_grass = 0
sum_flooeded_vegetation = 0
sum_crops = 0
sum_shrub_scrub = 0
sum_other = 0

for i in range(len(year_list)):
    area_change = area_change_list[i]

    for j in range(len(area_change)):

        dict_area = area_change[j]
        change_key = dict_area.get('change')

        if change_key == 1:
            sum_trees += dict_area.get('sum')
        elif change_key == 2:
            sum_grass += dict_area.get('sum')
        elif change_key == 3:
            sum_flooeded_vegetation += dict_area.get('sum')
        elif change_key == 4:
            sum_crops += dict_area.get('sum')
        elif change_key == 5:
            sum_shrub_scrub += dict_area.get('sum')
        elif change_key == 6:
            sum_trees -= dict_area.get('sum')
        elif change_key == 7:
            sum_grass -= dict_area.get('sum')
        elif change_key == 8:
            sum_flooeded_vegetation -= dict_area.get('sum')
        elif change_key == 9:
            sum_crops -= dict_area.get('sum')
        elif change_key == 10:
            sum_shrub_scrub -= dict_area.get('sum')
            
    print("Changes for year", year, "are the following:")
    print("Trees", sum_trees)
    print("Grass", sum_grass)
    print("Flooded Vegetation", sum_flooeded_vegetation)
    print("Crops", sum_crops)
    print("Shrub and Scrub", sum_shrub_scrub)





