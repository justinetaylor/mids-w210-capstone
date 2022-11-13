import json
import numpy as np
import pandas as pd
import random # DELETE THIS LATER
import streamlit as st
import datetime
from geopy.geocoders import GoogleV3
import geopy.distance
import googlemaps
from bokeh.plotting import figure,show
from bokeh.plotting import gmap
from bokeh.models import GMapOptions
from bokeh.io import output_notebook, output_file, curdoc, show
from bokeh.models import ColumnDataSource, TapTool, PolyDrawTool, PolyEditTool, MultiLine, Selection
from bokeh.models.callbacks import CustomJS
from bokeh.models import GeoJSONDataSource
from bokeh.palettes import GnBu3, OrRd3


### GLOBAL VARIABLES & SETTINGS

# Read in custom CSS
with open('project_contents/app/style.css') as f:
       st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Google api key
api_key = 'AIzaSyB_fzF2bKyUySSWRTMFCJP-VE1Gm_wmvaM'
bokeh_width, bokeh_height = 700,600

# Set Streamlit page details
st.markdown("# Carbon Analysis")
st.write("""You've taken the second step to understand Carbon Absorption Loss from Continued Urbanization by visiting this page. Here you will perform your detailed Carbon Analysis, but before we begin we need to understand a little bit more about what type of analysis you want to perform. Please choose your analysis options in Step 1 below.""")

### USER ANALYSIS SELECTION

def plot(lat, lng, pa, isCountyAnalysis=False): 
    """This function will render a Google Map using the Bokeh library"""
    
    # Default map options
    map_type='satellite'

    if isCountyAnalysis == True:
       area_coordinates = pa
       zoom=8
    else:
       zoom=12
       area_coordinates = [[[ pa[0][0], pa[0][1] ], [ pa[1][0], pa[1][1] ], [ pa[2][0], pa[2][1] ], [ pa[3][0], pa[3][1] ]]]
    
    # Create Geojson Polygon object
    geojson_site = {
      'type': 'FeatureCollection', 
      'features':[{
          'type': 'Feature',
          'geometry': {
            'type': 'Polygon',
            'coordinates': area_coordinates
          }
      }]
    }
    
    # Create GeoJSONDataSource to render polygon on gmap
    geo_source = GeoJSONDataSource(geojson=json.dumps(geojson_site))
    
    # Create and initialize gmap object
    gmap_options = GMapOptions(lat=lat, lng=lng, map_type=map_type, zoom=zoom) 
    p = gmap(api_key, gmap_options, title='Land Selection', width=bokeh_width, height=bokeh_height, tools=['hover', 'reset', 'wheel_zoom', 'pan'])
    
    # Add Polygon to the visualization using GeoJSONDataSource
    poly_init = p.patches('xs', 'ys', source=geo_source, fill_alpha=.5, line_color="black", line_width=0.05)
    
    return p

def render_site_selection():
    """This method renders the input controls for site analysis"""
    
    # Create GeoCoder class from Google Maps
    geolocator = GoogleV3(api_key=api_key)
    
    # Create 2x2 Grid for Lat/Lon coordinate input
    lat1, lon1 = st.columns(2)
    lat2, lon2 = st.columns(2)
    lat3, lon3 = st.columns(2)
    lat4, lon4 = st.columns(2)
    
    # Create text input boxes with default polygon coordinates for UCB campus
    lat1_value = lat1.text_input("Lat 1", "37.875")
    lon1_value = lon1.text_input("Lon 1", "-122.267")
    lat2_value = lat2.text_input("Lat 2", "37.87")
    lon2_value = lon2.text_input("Lon 2", "-122.266")
    lat3_value = lat3.text_input("Lat 3", "37.87")
    lon3_value = lon3.text_input("Lon 3", "-122.257")
    lat4_value = lat4.text_input("Lat 4", "37.873")
    lon4_value = lon4.text_input("Lon 4", "-122.259")
    polygon_array = np.array([[lon1_value, lat1_value], [lon2_value, lat2_value], [lon3_value, lat3_value], [lon4_value, lat4_value]])
    
    center_lat = (float(lat1_value) + float(lat2_value) + float(lat3_value) + float(lat4_value)) / 4
    center_lon = (float(lon1_value) + float(lon2_value) + float(lon3_value) + float(lon4_value)) / 4
    
    # Call plot function to create the Bokeh Google Map
    p = plot(center_lat, center_lon, polygon_array, False)
    
    # Display the Bokeh Google Map in Streamlit. Nice!
    st.bokeh_chart(p, use_container_width=False)

    return

def render_county_selection(county_list, county_data):
    """This method renders the input controls for county analysis"""

    # List to hold lat/lon pairs for GeoJson format
    county_coordinates_list = list()

    # Populate the county selection box and grab the first value as the selected value
    selected_county = st.selectbox("Please select a county for analysis:", county_list)

    # Enumerate through list to find selected County. NEED TO OPTIMIZE IN FUTURE.
    for i in range(len(county_list)):

       # See if the county name in JSON matches selected county name in interface
       if county_data["features"][i]["properties"]["ADM2_NAME"] == selected_county:
           
           # Extract the geometry into an array
           if "coordinates" in county_data["features"][i]["geometry"]:

              county_coordinates_array = np.array(county_data["features"][i]["geometry"]["coordinates"])

              # Determine if the geometry has nested lists, shape of array is 2 vs 3 implies nested lists
              if len(county_coordinates_array.shape) == 2:

                  # Determine how many nested lists of lat/lon pairs we have
                  num_coordinates = county_coordinates_array.shape[0]

                  # Enumerate all nested lists to extract lat/lon pairs and put into a single list
                  for i in range(num_coordinates):

                      # Get the sub array of coordinates and append to single growing list
                      sub_coordinates = county_coordinates_array[i]
                      county_coordinates_list.extend(sub_coordinates[0])
                            
                  # Conver list to array to compute center lat and lon
                  wrapping_list = list()
                  wrapping_list.append(county_coordinates_list)
                  county_coordinates_array = np.asarray(county_coordinates_list)
                  center_county = county_coordinates_array.mean(axis=0)
                  lat_center = float(center_county[1])
                  lon_center = float(center_county[0])

                  # Call plot function to create the Bokeh Google Map
                  p = plot(lat_center, lon_center, wrapping_list, True)

              else:
                  # Extract data directly into array and lists
                  county_coordinates_list = county_data["features"][i]["geometry"]["coordinates"]
                  county_coordinates_array = np.array(county_data["features"][i]["geometry"]["coordinates"])

                  # Computer center of the county
                  center_county = county_coordinates_array[0].mean(axis=0)
                  lat_center = float(center_county[1])
                  lon_center = float(center_county[0])

                  # Call plot function to create the Bokeh Google Map
                  p = plot(lat_center, lon_center, county_coordinates_list, True)

           else:
               county_coordinates = np.array(county_data["features"][i]["geometry"]["geometries"])
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
                     
               # Conver list to array to compute center lat and lon
               wrapping_list = list()
               wrapping_list.append(county_coordinates_list)
               county_coordinates_array = np.asarray(county_coordinates_list)
               center_county = county_coordinates_array.mean(axis=0)
               lat_center = float(center_county[1])
               lon_center = float(center_county[0])

               # Call plot function to create the Bokeh Google Map
               p = plot(lat_center, lon_center, wrapping_list, True)
    
           # Display the Bokeh Google Map in Streamlit. Nice!
           st.bokeh_chart(p, use_container_width=True)

    return

def get_analysis_settings(county_list, county_data):
    """This method is used to get the user selections in terms of what analysis they want to perform"""

    st.subheader('Step 1: Tells us more about your analysis')
    st.caption("With our product you can analyze carbon absorption gain/loss for a county or manually entered site within northern California. Also, you can choose to analyze the selected area over multiple years or point in time which would be our latest data as of today.")
    analysis_timing = st.selectbox('Will this be a multi-year analysis or single point in time?', ('Select...', 'Multi-year', 'Point in time'))

    if analysis_timing == "Multi-year":
       start_date = st.date_input("Start Date:", datetime.date(2022, 11, 1))
       end_date = st.date_input("End Date:", datetime.date(2022, 11, 30))

    analysis_location = st.selectbox('Do you want to analyze an entire County or a smaller site of your choosing?', ('Select...', 'County Analysis', 'Site Analysis'))
    
    if analysis_location == 'Site Analysis':
       render_site_selection()
    elif analysis_location == 'County Analysis':
       render_county_selection(county_list, county_data)

    if (analysis_location != "Select...") and (analysis_timing != "Select..."):
       return True

    return False

def render_carbon_results():
    """This method is used to render the chart for the carbon gain and loss for a selected vegetated area"""

    data = random.sample(range(10,500), 12) # DELETE THIS LATER, SHOULD POINT TO compute_change_in_region()
    data[6:] = [-x for x in data[6:]]
    
    vegetation_type = ['Trees', 'Grass', 'Shrub and Scrub', 'Flooded Vegetation', 'Crops', 'Bare or Buildings']
    
    df = pd.DataFrame({'vegetation_type' : vegetation_type * 2, 'Amount' : data, 'Gain_or_Loss' : ['Gained']*6 + ['Lost']*6})
    
    p = figure(x_range=vegetation_type, 
       plot_height=bokeh_height, 
       tooltips='@vegetation_type @Gain_or_Loss: @Amount units',
       title="Land Type Gained and Lost")
       
    p.vbar(x='vegetation_type', 
       width=0.9, 
       top='Amount',
       bottom=0,
       color='#32CD32', 
       source=ColumnDataSource(df.iloc[0:6]),
       legend_label="Gained")

    p.vbar(x='vegetation_type', 
       width=0.9, 
       top=0,
       bottom='Amount',
       color='#FF2400', 
       source=ColumnDataSource(df.iloc[6:12]),
       legend_label="Lost")

    p.ygrid.grid_line_color = None
    p.legend.location = "center_left"

    st.bokeh_chart(p, use_container_width=True)

    return True

def run_carbon_calculator():
    """This method is used to run the Carbon offsetting calculations for a selected vegetated area"""

    # Create areas for text rendering
    ccArea1, ccArea2 = st.columns([2,6])
    ccArea3, ccArea4 = st.columns([2,6])
    ccArea5, ccArea6 = st.columns([2,6])

    ccArea1.metric(label='Carbon Change', value='{:0,.0f}'.format(-15000), delta='{:0,.0f}'.format(-15000))
    ccArea2.text_area('','''Based upon the selected area, the net carbon absorption change over time is -15000 metric tons. This means that further work must be done to establish net zero carbon for this area.''', label_visibility="collapsed", height = 150, key="ccArea2")
    ccArea2.write('')
    ccArea2.write('')

    ccArea3.metric(label='Tree Seedlings', value='{:0,.0f}'.format(248026), delta='{:0,.0f}'.format(248026))
    ccArea4.text_area('', '''To offset -15000 metric tons of carbon dioxide you will have to plan 248,026 tree seedlings. It will take 10 years for these tree seedlings to fully absorb the -15000 metric tons of carbon dioxide.''', label_visibility="collapsed", height = 150, key="ccArea4")
    ccArea4.write('')
    ccArea4.write('')

    ccArea5.metric(label='Cost to Offset', value='${:0,.0f}'.format(1240130).replace('$-','-$'), delta='${:0,.0f}'.format(-1240130).replace('$-','-$'))
    ccArea6.text_area('', '''The total cost to plan and nurture these 248,026 tree seedlings for 10 years is $1,240,130. This includes a one-time upfront investment of $372,039 to plant the tree seedlinges and then an annual cost of $86,809.10 for 10 years to nurture these seedlings.''', label_visibility="collapsed", height = 150, key="ccArea6")

    return True


# Set variables for controlling UI element rendering
user_selections = False
predictions_run = False
calculations_run = False
num_counties = 0
county_list = list()
#county_list.append("Select...")

# Get list of Counties from file
with open('project_contents/app/NorthernCaliforniaCounties.txt') as f:
    
    # Extract json data from file
    county_data = json.load(f)

    # Determine how many counties/features in the file
    num_counties = len(county_data["features"])

    # Enumerate through JSON structure to get County names
    for i in range(num_counties):
        county_list.append(county_data["features"][i]["properties"]["ADM2_NAME"])

    # Sort Counties in alphabetical order
    county_list.sort()

# Render user selections and results from selections for polygon selection
user_selections = get_analysis_settings(county_list, county_data)

# If user selections complete the compute the carbon gain and loss
if user_selections == True:
    st.write('')
    st.write('')
    st.subheader('Step 2: Review the carbon gain & loss for your area')
    st.caption("Based upon your selected area, we have predicted the following carbon gain as well as loss by vegetation type. In the chart below, the vertical bar expanding up in green indicates positive/good carbon absorption change while the vertical bar expanding down in red indicates negative/bad carbon absorption change.")
    st.write('')
    st.write('')
    predictions_run = render_carbon_results()

# If predictions complete the run calculator to determine offset cost
if predictions_run == True:
    st.write('')
    st.write('')
    st.subheader("Step 3: Review the cost to offset carbon loss")
    st.caption("Based upon the net carbon absorption loss in your selected area, we have computed the cost to offset this carbon. This is assuming that you are a good citizen and are looking to create a more sustainable future.")
    st.write('')
    st.write('')
    calculations_run = run_carbon_calculator()
  


