import json
import numpy as np
import pandas as pd
import random # DELETE THIS LATER
import streamlit as st
import datetime
import ee 
import joblib
import geemap
import nltk
import sklearn
from area_change import AreaChange # Custom module for GEE calls
from geopy.geocoders import GoogleV3
import geopy.distance
import googlemaps
from bokeh.plotting import figure,show
from bokeh.plotting import gmap
from bokeh.models import GMapOptions
from bokeh.io import output_notebook, output_file, curdoc, show
from bokeh.models import ColumnDataSource, TapTool, PolyDrawTool, PolyEditTool, MultiLine, Selection, Span, HoverTool, Legend
from bokeh.models.callbacks import CustomJS
from bokeh.models import GeoJSONDataSource
from bokeh.palettes import GnBu3, OrRd3


### GLOBAL VARIABLES & SETTINGS

# Read in custom CSS
with open('project_contents/app/style.css') as f:
       st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Google api key
api_key = '' # Add your own Google Maps api key in this field
bokeh_width, bokeh_height = 700,600

# Set Streamlit page details
st.markdown("# Carbon Analysis")
st.write("""You've taken the first step to understand Carbon Absorption Loss from Continued Urbanization by visiting this page. Here you will perform your detailed Carbon Analysis, but before we begin we need to understand a little bit more about what type of analysis you want to perform. Please choose your analysis options in Step 1 below.""")

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
    lat1_value = lat1.text_input("Lat 1", "41.11806816998926") #37.875, 41.11806816998926 37.97439217674578
    lon1_value = lon1.text_input("Lon 1", "-124.14507547221648") #-122.267 -124.14507547221648 -121.88083169421675
    lat2_value = lat2.text_input("Lat 2", "41.11457637941072") #37.87 41.11457637941072 37.93649329389937
    lon2_value = lon2.text_input("Lon 2", "-124.14507547221648") #-122.266 -124.14507547221648 -121.88083169421675
    lat3_value = lat3.text_input("Lat 3", "41.11457637941072") #37.87 41.11457637941072 37.93649329389937
    lon3_value = lon3.text_input("Lon 3", "-124.1394964774655") #-122.257 -124.1394964774655 -121.82693002185347
    lat4_value = lat4.text_input("Lat 4", "41.11806816998926") #37.873 41.11806816998926 37.97439217674578
    lon4_value = lon4.text_input("Lon 4", "-124.1394964774655") #-122.259 -124.1394964774655 -121.82693002185347
    polygon_array = np.array([[lon1_value, lat1_value], [lon2_value, lat2_value], [lon3_value, lat3_value], [lon4_value, lat4_value]])
    
    center_lat = (float(lat1_value) + float(lat2_value) + float(lat3_value) + float(lat4_value)) / 4
    center_lon = (float(lon1_value) + float(lon2_value) + float(lon3_value) + float(lon4_value)) / 4
    
    # Call plot function to create the Bokeh Google Map
    p = plot(center_lat, center_lon, polygon_array, False)
    
    # Display the Bokeh Google Map in Streamlit. Nice!
    st.bokeh_chart(p, use_container_width=False)

    return polygon_array.astype(float).tolist()

def render_county_selection(county_list, county_data):
    """This method renders the input controls for county analysis"""

    # Holder for user selected geometry
    polygon_array = []

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
                  polygon_array = wrapping_list

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
                  polygon_array = county_coordinates_list

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
               polygon_array = wrapping_list
    
           # Display the Bokeh Google Map in Streamlit. Nice!
           st.bokeh_chart(p, use_container_width=True)

    return polygon_array

def get_analysis_settings(county_list, county_data):
    """This method is used to get the user selections in terms of what analysis they want to perform"""

    selected_geometry = []

    st.subheader('Step 1: Tells us more about your analysis')
    st.write("With our product you can analyze carbon absorption loss for a selected area within the contiguous United States by providing 4 pairs of latitude and longitude coordinates. Once you enter your coordinates we will provide the carbon absorption estimates over a 5 year period from 2017 through 2021.")
    analysis_location = st.selectbox('Please select your type of analysis. Right now only Site Analysis is available. However, we plan to add additional options in the future.', ('Select...', 'Site Analysis')) # Add back 'County Analysis' at future date

    if analysis_location == 'Site Analysis':
       selected_geometry = render_site_selection()
    elif analysis_location == 'County Analysis':
       selected_geometry = render_county_selection(county_list, county_data)

    if (analysis_location != "Select..."):
       return True, selected_geometry

    return False, selected_geometry

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

def multi_year_line(start_year, end_year, data):
    """This method generates a multi year line plot for vegetation change in a specified area."""

    df = data[['Year','Trees','Grass','Flooded_Vegetation','Crops','Shrub_Scrub']]

    p = figure(plot_height=250, 
               #x_axis_type = 'datetime',
               #tooltips = '@y Net Change: @Amount Meters Squared',
               title=f"Vegetation Net Gain and Loss for selected area: {start_year} - {end_year}")

    p_trees = p.line(x='Year',
                     y='Trees',
                     line_width=2,
                     color='#023020',
                     source=df[['Year','Trees']])

    p_grass = p.line(x='Year',
                     y='Grass',
                     line_width=2,
                     color='#88e904',
                     source=df[['Year','Grass']])

    p_flooded_veg = p.line(x='Year',
                           y='Flooded_Vegetation',
                           line_width=2,
                           color='#019faf',
                           source=df[['Year','Flooded_Vegetation']])

    p_crops = p.line(x='Year',
                     y='Crops',
                     line_width=2,
                     color='#a72b43',
                     source=df[['Year','Crops']])

    p_shrub_and_scrub = p.line(x='Year',
                               y='Shrub_Scrub',
                               line_width=2,
                               color='#D2B48C',
                               source=df[['Year','Shrub_Scrub']])

    p.add_tools(HoverTool(show_arrow=False, line_policy='next', tooltips=[
        ('Year', '$data_x'),
        ('Net Area Change (Meters Squared)', '$data_y')
    ]))

    hline = Span(location=0, dimension='width', line_color='black', line_width=0.5)
    p.renderers.extend([hline])

    legend = Legend(items=[('Trees', [p_trees]),
                           ('Grass', [p_grass]),
                           ('Flooded Vegetation', [p_flooded_veg]),
                           ('Crops', [p_crops]),
                           ('Shrub and Scrub', [p_shrub_and_scrub])])

    #p.x_range.range_padding = 0.5
    p.xaxis.ticker = data['Year']
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Net Area Change (Meters Squared)'
    #p.ygrid.grid_line_color = None
    p.add_layout(legend,'right')
    st.bokeh_chart(p, use_container_width=True)

    return True

def line_chart_GPP(start_year, end_year, data):
    """This method generates a GPP line plot in a specified area over a 5 year period."""

    df = data[['Year','GPP']]

    p = figure(plot_height=250, 
               #x_axis_type = 'datetime',
               #tooltips = '@y Net Change: @Amount Meters Squared',
               title=f"Carbon absorption for selected area: {start_year} - {end_year}")

    p_gpp = p.line(x='Year',
                     y='GPP',
                     line_width=2,
                     color='#023020',
                     source=df[['Year','GPP']])

    p.add_tools(HoverTool(show_arrow=False, line_policy='next', tooltips=[
        ('Year', '$data_x'),
        ('Carbon Absorption Change (metric tons)', '$data_y')
    ]))

    hline = Span(location=0, dimension='width', line_color='black', line_width=0.5)
    p.renderers.extend([hline])

    legend = Legend(items=[('Carbon Absorption', [p_gpp])])

    p.xaxis.ticker = data['Year']
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Carbon Absorption Change (metric tons)'
    p.add_layout(legend,'right')
    st.bokeh_chart(p, use_container_width=True)

    return True

def run_carbon_calculator(GPP_mean):
    """This method is used to run the Carbon offsetting calculations for a selected vegetated area"""

    # Amount of metric tons of carbon absorbed by urgan tree according to EPA
    # (https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references#seedlings)
    carbon_absorption_urban_tree = 36.4 * (44/12) * (1/2204.6)

    num_years = 30
    GPP_mean = round(GPP_mean * num_years, 2)
    num_trees_planted = round(GPP_mean / carbon_absorption_urban_tree, 2)
    total_offset_cost = round(5 * num_trees_planted, 2)
    annual_offset_cost = round((3.5 * num_trees_planted) / 10, 2)
    upfront_offset_cost = round(1.5 * num_trees_planted, 2)

    # Create areas for text rendering
    ccArea1, ccArea2 = st.columns([2,6])
    ccArea3, ccArea4 = st.columns([2,6])
    ccArea5, ccArea6 = st.columns([2,6])

    msg_absorption_change = "Based upon the selected area, the average natural carbon absorption over a " + str(num_years) + " year period is " + str(GPP_mean) + " metric tons." 
    msg_offset = "To offset " + str(GPP_mean) + " metric tons of carbon dioxide you would have to plant " + str(num_trees_planted) + " tree seedlings. According to the Environmental Protection Agency (EPA), it will take 10 years for these tree seedlings to fully absorb " + str(GPP_mean) + " metric tons of carbon dioxide."
    msg_cost = "The total cost to plant and nurture these " + str(num_trees_planted) + " tree seedlings is \$" + str(total_offset_cost) + ". This includes a one-time upfront investment of \$" + str(upfront_offset_cost) + " to plant the tree seedlings and then an annual cost of \$" + str(annual_offset_cost) + " for 10 years to nurture these seedlings in order to fully offset this loss in carbon absorption."

    ccArea1.metric(label='Carbon Change', value='{:0,.2f}'.format(GPP_mean), delta='{:0,.2f}'.format(GPP_mean))
    #ccArea2.text_area('', msg_absorption_change, label_visibility="collapsed", height = 150, key="ccArea2", disabled=True)
    ccArea2.write(msg_absorption_change)
    ccArea2.write('')
    ccArea2.write('')

    ccArea3.metric(label='Tree Seedlings', value='{:0,.2f}'.format(num_trees_planted), delta='{:0,.2f}'.format(num_trees_planted))
    #ccArea4.text_area('', msg_offset, label_visibility="collapsed", height = 150, key="ccArea4", disabled=True)
    ccArea4.write(msg_offset)
    ccArea4.write('')

    ccArea5.metric(label='Cost to Offset', value='${:0,.2f}'.format(total_offset_cost).replace('$-','-$'), delta='${:0,.2f}'.format(-1*total_offset_cost).replace('$-','-$'))
    #ccArea6.text_area('', msg_cost, label_visibility="collapsed", height = 150, key="ccArea6", disabled=True)
    ccArea6.write(msg_cost)
    ccArea6.write('')

    return True

def get_GEE_data(geometry):
    """This method makes calls to GEE to get LAI, FPAR, and land use/coverage data for a specified geometry. This is required for running model predictions."""
    
    # Set up variables for GEE runs and collecting results
    year_list = [2017, 2018, 2019, 2020, 2021]
    area_change_list = []
    sum_trees = 0
    sum_grass = 0
    sum_flooeded_vegetation = 0
    sum_crops = 0
    sum_shrub_scrub = 0
    land_change_df = pd.DataFrame()
    GPP_df = pd.DataFrame()

    # Create progress bar as these operations are length ;-)
    progress_time = 10
    progress_bar = st.progress(progress_time)

    st.write("Retrieving climate data and running carbon predictions for selected area...") # let user know what we are doing

    # Load model
    # use project_contents/app/GPP_boost_mod.pkl for local
    saved_knn = joblib.load('/w210containermount/GPP_boost_mod.pkl')

    # Get biome data and run predictions for all 5 years
    for i in range(len(year_list)):

        # Grab the current year from the list
        year = year_list[i]

        # Create instance of custom AreaChange class for GEE calls
        #ac = AreaChange()
        ac = AreaChange(geometry, year)

        if ac.is_area_within_limits() == False:
            e = RuntimeError('Area is too large for Google Earth Engine API processing. Please reduce the size of your selected area.')
            st.exception(e)
            return None, None, None

        # Get the carbon capture change by vegetation type for specified geometry and year
        #change_list = ac.get_area_of_change(geometry, year)
        change_list = ac.get_area_of_change()

        area_change_list.append(change_list)

        # Get climage data for specified geometry and year
        #result = ac.get_climate_data_for_change(geometry, year)
        #result = ac.get_climate_data_for_change_and_join()
        result = ac.get_change_that_might_occur()
        #within_gee_limit = ac.is_area_within_limits()

        # Re-format the climate data for model inference
        result = result.reindex(columns=['srad', 'tmmn', 'tmmx', 'vpd', 'Fpar_500m', 'Lai_500m', 'latitude', 'longitude', 'elevation', 'water_mean', 'trees_mean', 'grass_mean', 'flooded_vegetation_mean', 'crops_mean', 'shrub_and_scrub_mean', 'built_mean', 'bare_mean', 'snow_and_ice_mean', 'label_mode'])
        result['Fpar_500m'] = result['Fpar_500m'].astype("float64")
        result['Lai_500m'] = result['Lai_500m'].astype("float64")
        result['label_mode'] = result['label_mode'].astype("category")
        result.rename(columns={"latitude": "LATITUDE_x", "longitude": "LONGITUDE_x", "elevation": "ee_elevation", "label_mode": "label_argmax_numeric"}, inplace=True)

        # Run model predictions using climate data for specified geometry and year
        predicted_results = saved_knn.predict(result)
    
        # Aggregate the results (pixel level in geometry) to arrive a single GPP value for entire geometry
        GPP_value = np.sum(predicted_results) / 1000000

        # Add GPP results to data frame
        dict_row = {'Year': year, 'GPP': GPP_value}
        GPP_df = GPP_df.append(dict_row, ignore_index = True)

        # Update progress by 15% for each year we process
        progress_time += 15
        progress_bar.progress(progress_time)

        #st.write("Carbon predictions complete for ", year, "...")
    
    st.write("Aggregating vegetation change data for selected region...") # let user know what we are doing

    # Enumerate through years to aggregate vegetation change
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
            
        #st.write("Completed gathering vegetation data for year", year_list[i], "...")

        dict_row = {'Year': year_list[i], 'Trees': sum_trees, 'Grass': sum_grass, 'Flooded_Vegetation': sum_flooeded_vegetation, 'Crops': sum_crops, 'Shrub_Scrub': sum_shrub_scrub}
        land_change_df = land_change_df.append(dict_row, ignore_index = True)

        progress_time += 3
        progress_bar.progress(progress_time)

    return land_change_df, GPP_df, GPP_df["GPP"].mean()

# Set variables for controlling UI element rendering
user_selections = False
predictions_run = False
calculations_run = False
show_by_vegegation_type = False
num_counties = 0
county_list = list()
selected_geometry = []

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
selections_made, selected_geometry = get_analysis_settings(county_list, county_data)

# If user selections complete the compute the carbon gain and loss
if selections_made == True:
    st.write('')
    st.write('')
    st.subheader('Step 2: Review the carbon absorption change for your selected area')
    st.write("Based upon your selected area, we have predicted the carbon absorption as well as determined the vegetation change over a 5 year period (2017 to 2021).")
    st.write('')
    st.write('')
    land_change_df, GPP_df, GPP_mean = get_GEE_data(selected_geometry)
    st.write('')
    st.write('')
    st.write("The predicted natural carbon absorption for your selected area is ", round(GPP_mean, 2), " metric tons per year.", )
    st.write('')
    st.write('')
    predictions_run = line_chart_GPP(2017, 2021, GPP_df)
    st.write('')
    st.write('')
    st.write('Listed below is the vegetation change from 2017 through 2021 within your selected area. Vegetation can naturally change due to climate differences year over year which has direct impacts on carbon absorption. From the chart below, anyting below the 0 line represents loss in vegetation for that year. Having continued year over year loss in vegetation will decrease the amount of natural carbon absorption.')
    st.write('')
    st.write('')
    predictions_run = multi_year_line(2017, 2021, land_change_df)

# If predictions complete the run calculator to determine offset cost
if predictions_run == True:
    st.write('')
    st.write('')
    st.subheader("Step 3: Review the cost to offset carbon loss")
    msg_caption = "If you were to develop over the vegetated land in your area this would result in a loss of " + str(round(GPP_mean, 2)) + " metric tons of natural carbon absorption per year. Given this is an annual loss of natural carbon absorption, we have forecasted this loss out to 30 years so that you can understand the longer term impacts and costs. The longer term costs below are also based upon (1) EPA.gov conversions of carbon metrics tons to equivalent carbon sequestered by tree seedlings and (2) OneTreePlanted.org estimates of the cost to plant and nurture a tree."
    st.write(msg_caption)
    st.write('')
    st.write('')
    calculations_run = run_carbon_calculator(GPP_mean)
  


