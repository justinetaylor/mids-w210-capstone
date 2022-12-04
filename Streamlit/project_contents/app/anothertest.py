import numpy as np

geometry =  [[-124.14507547221648, 41.11806816998926],
          [-124.14507547221648, 41.11457637941072],
          [-124.1394964774655, 41.11457637941072],
          [-124.1394964774655, 41.11806816998926]]

# Create text input boxes with default polygon coordinates for UCB campus
lat1_value = "41.11806816998926" #37.875
lon1_value = "-124.14507547221648" #-122.267
lat2_value = "41.11457637941072" #37.87
lon2_value = "-124.14507547221648" #-122.266
lat3_value = "41.11457637941072" #37.87
lon3_value = "-124.1394964774655" #-122.257
lat4_value = "41.11806816998926" #37.873
lon4_value = "-124.1394964774655" #-122.259
polygon_array = np.array([[lon1_value, lat1_value], [lon2_value, lat2_value], [lon3_value, lat3_value], [lon4_value, lat4_value]])

print("type of geometry", type(geometry))
print("length of og list", len(geometry))
print("type of polygon_array", type(polygon_array))
print("last type", type(polygon_array.astype(float).tolist()))
print("length of array list", len(polygon_array.astype(float).tolist()))