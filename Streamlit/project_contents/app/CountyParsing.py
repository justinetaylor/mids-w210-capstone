import pandas as pd
import numpy as np
import json
from bokeh.models import GeoJSONDataSource

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
with open('project_contents/app/NorthernCaliforniaCounties.txt') as f:
    data = json.load(f)
    county = "Contra Costa" # Contra Costa (44x1) Glenn (1x1923x2) Yuba (1,4355,2)
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

                print("success, first level presence of coordinates")
                
                if len(county_coordinates.shape) == 2:

                    num_coordinates = county_coordinates.shape[0]
                    transformed_coordinates = list()

                    for i in range(num_coordinates):

                        # Get the sub array of coordinates
                        sub_coordinates = county_coordinates[i]

                        transformed_coordinates.extend(sub_coordinates[0])

                        if i == 1:
                            print(sub_coordinates[0])
                            print("only 2 here")
                            print(transformed_coordinates)

                    
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

    


