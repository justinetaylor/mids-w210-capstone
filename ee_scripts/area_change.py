"""
This class uses Google Earth Engine to compute
the area of vegetation change (trees lost, grass 
gained etc.)  for a given area over a year. It 
also goes and retrieves the data (MOD15, GRIDMET,
USGS Elevation, Dynamic World values) for each of 
the pixels that indicated a vegetation change. 

# Sample Usage

-------------
from area_change import AreaChange

# Example Inputs
geometry =  [[-124.14507547221648, 41.11806816998926],
          [-124.14507547221648, 41.11457637941072],
          [-124.1394964774655, 41.11457637941072],
          [-124.1394964774655, 41.11806816998926]]
year = 2018

# Create an instance of AreaChange class
ac = AreaChange()

# Estimate the area of vegetation change for each type
change_list = ac.get_area_of_change(geometry, year)
print(change_list)

# Output:
# [{'change': 0, 'sum': 1000943766.2943573}, 
# {'change': 1, 'sum': 7871904.116004944}, 
# {'change': 2, 'sum': 915519.3800354004}, 
# {'change': 4, 'sum': 5933634.289802551}, 
# {'change': 5, 'sum': 2133110.9543914795}, 
# {'change': 6, 'sum': 8753569.066741943}, 
# {'change': 7, 'sum': 116530830.96776581}, 
# {'change': 8, 'sum': 10407.224006652832}, 
# {'change': 9, 'sum': 3410677.085800171}, 
# {'change': 10, 'sum': 19004752.376182556}]


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


# get all data needed for inference
df_for_inference = ac.get_climate_data_for_change(geometry, year)

# examine results
print(df_for_inference.describe())
print("Number of days", len(df_for_inference['gridmet_date'].unique()))
df_for_inference['latlng_pair'] = df_for_inference['latitude'].apply(str) +  df_for_inference['longitude'].apply(str)
print("Number of pixels that changed", len(pd.unique(df_for_inference['latlng_pair'])))

# export 
df_for_inference.to_csv("sample_inference_export.csv", index=False)
--------------

"""
import math
import geemap
import pandas as pd
import ee 

# sign into earth engine with our credentials
service_account = "calucapstone@ee-calucapstone.iam.gserviceaccount.com"
credentials = ee.ServiceAccountCredentials(service_account, '../.private-key.json')
ee.Initialize(credentials)

class AreaChange:
  # Dynamic World resolution (meters ^ 2)
  PIXEL_SCALE_METERS = 10

  # Missing data value for Earth Engine images 
  NODATA_VALUE = -1

  # We can change this color pallete. We're not currently creating 
  # images so this isn't used right now. 
  VIS_PALETTE = [
    '#DDDDDD', # grey  - 0 don't care
    '#CC6677', # indigo  - 1 lost trees 
    '#332288', # cyan - 2 lost grass  
    '#DDCC77', # teal - 3 lost flooded_veg
    '#117733', # green - 4 lost crops
    '#88CCEE', # olive - 5 lost shrub
    '#882255', # sand - 6 gained trees
    '#44AA99', # rose - 7 gained grass
    '#999933', # wine -  8 gained flooded_veg
    '#AA4499', # purple - 9 gained crops
    '#000000', # black - 10 gained shrub
    ]
      
  """
  bigLabels: imagine a pixel in a dynamic world image has 
  land class label X at time A and label Y at time B. We can 
  detect the change by multiplying the label at time A by 100 
  and adding the label at time A and time B together. If we 
  were to do that, we'd get the following possible values: 
  
  """
  bigLabels = ee.List(
    [ 0,1,2,3,4,5,6,7,8,
      100,101,102,103,104,105,106,107,108,
      200,201,202,203,204,205,206,207,208,
      300,301,302,303,304,305,306,307,308,
      400,401,402,403,404,405,406,407,408,
      500,501,502,503,504,505,506,507,508,
      600,601,602,603,604,605,606,607,608,
      700,701,702,703,704,705,706,707,708,
      800,801,802,803,804,805,806,807,808])

  """
  adjustedLabels: We don't care about most of the possible 
  changes. For example, if water stayed water....we don't care.
  However, we do care if grass went to built or if built turned into
  grass. So we set most of the list to 0 and we remap changes we care 
  to new labels. So now 1 represents trees that are now considered built. 

  See: https://docs.google.com/spreadsheets/d/1jRIu3ly6NOzFR9X5of_NDq2ZfgFpiM5AL9LdtuzXDiw/edit?usp=sharing
  """
  adjustedLabels = ee.List(
    [ 0,0,0,0,0,0,0,0,0,
      0,0,0,0,0,0,1,1,0,
      0,0,0,0,0,0,2,2,0,
      0,0,0,0,0,0,3,3,0,
      0,0,0,0,0,0,4,4,0,
      0,0,0,0,0,0,5,5,0,
      0,6,7,8,9,10,0,0,0, 
      0,6,7,8,9,10,0,0,0,
      0,0,0,0,0,0,0,0,0])

  def get_annual_change_image(self, geo, year):
    # To get the difference  of an area over a year,
    # we'll compare the time period right before the year
    # to the time period right after the year. 
    # Ex. year=20, time_a=(2017-9-1,2017-12-31), time_b=(2019-1-1, 2019-3-1)
    time_a = (str(year-1)+'-9-01', str(year-1)+'-12-31')
    time_b = (str(year+1)+'-01-01', str(year+1)+'-03-01')

    
    # get all of the dynamic world images containing this area in the first time period
    imgCol_1= (ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
                          .filterBounds(geo)
                          .filter(ee.Filter.date(time_a[0], time_a[1])))

    # get all of the dynamic world images containing this area in the second time period
    imgCol_2= (ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
                          .filterBounds(geo)
                          .filter(ee.Filter.date(time_b[0], time_b[1])))

    # select the land class bands, compute the mean over time,
    # clip the image down to just the area we want, get the maximum
    # class and choose that as the ultimate land class for the pixel
    # multiply by 100 as part of the change detection process
    img_1 = (imgCol_1
      .select(['water', 
              'trees', 
              'grass', 
              'flooded_vegetation', 
              'crops', 
              'shrub_and_scrub', 
              'built',
              'bare', 
              'snow_and_ice'])
      .reduce(ee.Reducer.mean()).unmask(self.NODATA_VALUE)
      .clip(geo)
      .toArray().arrayArgmax().arrayGet([0])
      .rename("label_1_argmax")
      .multiply(100))
    
    # same as img_1 but don't multiply by 100
    img_2 = (imgCol_2
      .select(['water', 
              'trees', 
              'grass', 
              'flooded_vegetation', 
              'crops', 
              'shrub_and_scrub', 
              'built',
              'bare', 
              'snow_and_ice'])
      .reduce(ee.Reducer.mean()).unmask(self.NODATA_VALUE)
      .clip(geo)
      .toArray().arrayArgmax().arrayGet([0])
      .rename("label_2_argmax"))
    
    # Add the two images such that one is one top of the other 
    # For more intuition on this:
    #   Imagine how an RGB image would look. One layer for red
    #   , one layer for green, and one layer for blue. Adding a 
    #   band to an image is just like adding another layer 
    dwImg_combined = img_1.addBands(img_2)   
    
    # Add the two bands together (see bigLabels above). 
    # remap the big numbers to the adjusted values. 

    change = (dwImg_combined
              .select("label_1_argmax")
              .add(dwImg_combined.select("label_2_argmax"))
              .remap(self.bigLabels, self.adjustedLabels)
              .rename("change"))

    # "mask" out any pixels with 0 values. This basically means 
    # ignore them. 
    mask = change.neq(0);
    change = change.updateMask(mask)
 
    return change

  def get_annual_gridmet_for_change(self, change_img, start_date, end_date):
    # Get min temp, max temp, vapor pressure and shortwave active radiation
    # measurements for every day of the year
    gridmet_dataset = (ee.ImageCollection("IDAHO_EPSCOR/GRIDMET")
                    .select(['tmmn', 'tmmx','vpd','srad'])
                    .filterBounds(change_img.geometry())
                    .filter(ee.Filter.date(start_date, end_date)))

    # for each day of values (i.e. each image), clip it to just the area we want
    # set the mask to the same as  the image that represents change, set the date
    # and add the "change" band
    def finalize_gridmet_img(gridmet_img):
      return (gridmet_img
            .clip(change_img.geometry())
            .updateMask(change_img.mask())
            .set("gridmet_date", gridmet_img.date().format("YYYY-MM-dd"))
            .set("gridmet_start_date_millis", gridmet_img.date().millis())
            .addBands(change_img.select("change")))

    gridmet_dataset = gridmet_dataset.map(finalize_gridmet_img)
    return gridmet_dataset


  # not being used right now, we're getting daily data
  # however, if we decide to get weekly averages instead we can use this
  def get_weekly_gridmet_for_change(self, change_img, start_date, end_date):
    # compute the time in miliseconds of a week 
    weekMillis = 7 * 24 * 60 * 60 * 1000;

    # create a list where each value is the first day of the week
    # ex. [11-7-2022, 11-14-2022, 11-21-2022] but in millisecond equivalents
    # it might sound off to represent a week as milliseconds. The actual
    # representation is the number of milliseconds since 1970-01-01T00:00:00Z.
    listMap = ee.List.sequence(ee.Date(start_date).millis(), ee.Date(end_date).millis(), weekMillis);

    # function that gets the average gridmet valeus (temperature, vapor pressure
    # shortwave active radiation) for an area over a specific week
    def reduce_to_weekly(dateMillis):
      new_start = ee.Date(dateMillis)
      # filter the gridmet dataset to the area we want in the specified week
      # there will be multiple images because gridmet has daily values
      gridmet_week = (ee.ImageCollection("IDAHO_EPSCOR/GRIDMET")
                        .filterBounds(change_img.geometry())
                        .filter(ee.Filter.date(new_start, new_start.advance(1,'week')))
                        .select(['tmmn', 'tmmx','vpd','srad']))
      # compute the average over the week
      avg = (gridmet_week
                .reduce(ee.Reducer.mean())
                .set("gridmet_start_date_millis", new_start.millis()) # set the week as a property in the image
                .set('gridmet_date', new_start.format('YYYY-MM-dd'))  # also set it in normal format 
                .clip(change_img.geometry()) # clip the image to the specific area we want 
                .updateMask(change_img.mask())) # mask out pixels we don't care about. 

      # combine this with the original change image before returning 
      # this is to make joining easier later 
      return avg.addBands(change_img.select("change")) 

    # Get the average values for each week in the time period
    gridmet_dataset = listMap.map(reduce_to_weekly)

    return gridmet_dataset 


  def get_elevation_for_change(self, change_img, start_date, end_date):
    # Get the elevation data (just one image)
    elevation_dataset = ee.Image('USGS/3DEP/10m').select('elevation')
    return (elevation_dataset
                .clip(change_img.geometry())
                .updateMask(change_img.mask())
                .addBands(change_img.select("change")))


  def get_mod15_for_change(self, change_img, start_date, end_date):
    # Get the mod dataset, which has roughly weekly values for
    # leaf area index and photosynthetically active radiation
    mod15_dataset = (ee.ImageCollection("MODIS/061/MOD15A2H")
                        .filterBounds(change_img.geometry())
                        .filter(ee.Filter.date(start_date, end_date))
                      .select(['Lai_500m','Fpar_500m']));

    # clip/set values for each image
    def finalize_mod_img(mod_img):
      return (mod_img.unmask(0.01)
          .clip(change_img.geometry())
          .updateMask(change_img.mask())
          .addBands(change_img.select("change"))
          .set("mod_start_date_millis", mod_img.date().millis())
          .set("mod_date", ee.Date(mod_img.date()).format("YYYY-MM-dd")))

    mod15_dataset = mod15_dataset.map(finalize_mod_img)
    return mod15_dataset 


  def get_dw_for_change(self, change_img, year):
    # define quarters
    quarters = [
      (str(year-1)+"-12-01",str(year)+"-03-01"),
      (str(year)+"-03-02",str(year)+"-05-31"),
      (str(year)+"-06-01",str(year)+"-08-31"),
      (str(year)+"-09-01",str(year)+"-11-30")]
    all_quarters = []
    for i, quarter_dates in enumerate(quarters):
      # get dynamic world images for the each quarter
      quarter_representation = ee.Image.constant(i+1)
      dw_dataset = (ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
                            .filterBounds(change_img.geometry())
                            .filter(ee.Filter.date(quarter_dates[0], quarter_dates[1])))
      # Get the mode label for each pixel 
      dw_quarterly_mode_label = (dw_dataset
                        .select('label')
                        .reduce(ee.Reducer.mode()).unmask(self.NODATA_VALUE)
                        .clip(change_img.geometry())
                        .updateMask(change_img.mask()).rename("label_mode"))
      # get the mean land class probabilities 
      # also add bands (date, etc)
      dw_quarterly_mean = (dw_dataset
                            .select(['water', 
                                    'trees', 
                                    'grass', 
                                    'flooded_vegetation', 
                                    'crops', 
                                    'shrub_and_scrub', 
                                    'built',
                                    'bare', 
                                    'snow_and_ice'])
                            .reduce(ee.Reducer.mean()).unmask(self.NODATA_VALUE)
                            .clip(change_img.geometry())
                            .updateMask(change_img.mask())
                            .addBands(quarter_representation.select("constant").rename('quarter'))
                            .addBands(dw_quarterly_mode_label.select("label_mode"))
                            .set("dw_start_date_millis", ee.Date(ee.List(quarter_dates).get(0)).millis())
                            .set("dw_start_date", ee.Date(ee.List(quarter_dates).get(0)).format("YYYY-MM-dd")))

      all_quarters.append(dw_quarterly_mean)

    # each image in all_quarters represents the mean land class / mode label for each pixel in the area 
    # we'll combine each image into one image collection (like a list)
    return  ee.ImageCollection.fromImages(all_quarters)  

  def get_climate_data_for_change(self, geometry, year):
    # create an ee.Geometry object from the list of latitudes and longitudes
    geo = ee.Geometry.Polygon(geometry)

    # get an image where each pixel represents any change that occurred  
    change = self.get_annual_change_image(geo, year)

    # we'll get some of the data quarterly, according to the seasons
    # ex for 2018 we'll get data for 2017-12-1 -> 2018-11-30
    start_date = str(year-1)+'-12-01'
    end_date = str(year)+'-11-30'

    # get data from each dataset 
    elev = self.get_elevation_for_change(change, start_date, end_date)
    mod15 = self.get_mod15_for_change(change, start_date, end_date)
    gridmet = self.get_annual_gridmet_for_change(change, start_date, end_date)
    dw = self.get_dw_for_change(change, year)

    # Join the data

    # add elevation and change label to all dynamic world readings
    # this is probably ideal because dynamic world has the closest
    # spatial resolution to elevation
    def add_elevation(dw_img):
      return dw_img.addBands(elev.select("elevation"))
    dw = dw.map(add_elevation)

    # join gridmet and mod
   
    # ten days in milliseconds.
    tenDaysMillis = 10 * 24 * 60 * 60 * 1000;

    # Create a time filter to define a match as overlapping timestamps.
    timeFilterGridmetMod = ee.Filter.Or(
      ee.Filter.maxDifference(
        difference= tenDaysMillis,
        leftField= 'gridmet_start_date_millis',
        rightField= 'mod_start_date_millis'
      ),
      ee.Filter.maxDifference(
        difference= tenDaysMillis,
        leftField= 'gridmet_start_date_millis',
        rightField= 'mod_start_date_millis'
      )
    );

    # Define the join.
    saveAllJoinGridmetMod = ee.Join.saveAll(
      matchesKey= 'mod_match',
      ordering= 'mod_date',
      ascending= True,
      outer= True
    );

    # Apply the join.
    GridmetModJoined = saveAllJoinGridmetMod.apply(gridmet, mod15.select(["Lai_500m","Fpar_500m"]), timeFilterGridmetMod);
    print("GridmetModJoined  size", GridmetModJoined.size().getInfo())

    # process the join
    def flatten_join_mod_gridmet(join_feature):
      img = ee.Image(join_feature)
      matches = ee.List(img.get("mod_match"))
      result = ee.Algorithms.If(matches.size(),img.addBands(matches.get(0)) ,img)
      return result

    GridmetModJoined = GridmetModJoined.map(flatten_join_mod_gridmet)
    print("GridmetModJoined  size", GridmetModJoined.size().getInfo())


    # join gridmet and mod with the dynamic world / elevation / change

    # 62 days in milliseconds.
    sixtytwoDaysMillis = 62 * 24 * 60 * 60 * 1000;

    # Create a time filter to define a match as overlapping timestamps.
    timeFilterDW = ee.Filter.Or(
      ee.Filter.maxDifference(
        difference= sixtytwoDaysMillis,
        leftField= 'gridmet_start_date_millis',
        rightField= 'dw_start_date_millis'
      ),
      ee.Filter.maxDifference(
        difference= sixtytwoDaysMillis,
        leftField= 'gridmet_start_date_millis',
        rightField= 'dw_start_date_millis'
      )
    );

    # Define the join.
    saveAllJoinDW = ee.Join.saveAll(
      matchesKey= 'dw_match',
      ordering= 'dw_start_date',
      ascending= True,
      outer= True
    );

    # Apply the join.
    # QUESTION: i is there a way to get dynamic world resolution, but gridmet frequency? 
    DWJoined = saveAllJoinDW.apply(GridmetModJoined, dw, timeFilterDW);
    print("DWJoined  size", DWJoined.size().getInfo())

    # process the join 
    def flatten_join_dw(join_feature):
      img = ee.Image(join_feature)
      matches = ee.List(img.get("dw_match"))
      result = ee.Algorithms.If(matches.size(),img.addBands(matches.get(0)) ,img)
      return result

    DWJoined = DWJoined.map(flatten_join_dw)
    print("DWJoined  size", DWJoined.size().getInfo())

    # get lat lng values for each pixel
    pixelLatLngImg = ee.Image.pixelLonLat()

    # convert images to features so we can export easily
    def convert_to_fc(img):
      # add a band for the latitude and longitude of each pixel 
      added_lat_lng =  ee.Image(img).addBands(pixelLatLngImg)
      # get all pixel values
      feature_collection = added_lat_lng.sample(
        region=  geo,
        numPixels=2000, # i dont expect we'll ever see this 
        geometries= True,  
        scale=10,
        projection='EPSG:4326',
        );
      def set_date(pixel_feature):
        return pixel_feature.set('gridmet_date', img.get('gridmet_date'))

      feature_collection = feature_collection.map(set_date)
      return feature_collection


    final_result = ee.FeatureCollection(DWJoined.map(convert_to_fc).flatten())

    # geemap can only convert 5000 features to a dataframe at a time so if the 
    # feature collection is bigger than that, we need to convert to a dataframe
    # in chuncks. 
    num_exports  = math.ceil(final_result.size().getInfo() / 5000)
    exports = []
    for i in range(num_exports):
      """
        toList takes two arguments: max features to get, offset
        so for example, if there are 7000 items, we'd first
        convert items [0-4999] to a dataframe and then
        convert items [5000-7000] to a dataframe
      """ 
      subset = ee.FeatureCollection(final_result.toList(5000, i*5000))
      # convert feature collection to pandas dataframe 
      df = geemap.ee_to_pandas(subset)
      exports.append(df)

    if len(exports) > 1:
      # concatenate the dataframes to be one 
      return pd.concat(exports, axis=0, ignore_index=True)
    elif len(exports) == 1:
      return exports[0]
    else:
      return pd.DataFrame(dict.fromkeys(['gridmet_date', 'bare_mean', 'elevation', 'grass_mean', 'label_mode',
       'crops_mean', 'built_mean', 'change', 'latitude', 'water_mean', 'vpd',
       'flooded_vegetation_mean', 'tmmn', 'Fpar_500m', 'shrub_and_scrub_mean',
       'snow_and_ice_mean', 'tmmx', 'Lai_500m', 'srad', 'trees_mean',
       'quarter', 'longitude']))



  def get_area_of_change(self, geometry, year):   
    # create an ee.Geometry object for the list of coordinates
    geo = ee.Geometry.Polygon(geometry)
    # get an image representation of the change
    change = self.get_annual_change_image(geo, year)

    # get the area of each pixel
    pixelArea = ee.Image.pixelArea().clip(change.geometry()).rename("area")
    
    # add a band that has the pixel area 
    change = change.addBands(pixelArea)
    
    # group pixels by label and compute the sum of the area 
    label_stats = change.reduceRegion(
      reducer= ee.Reducer.sum().unweighted().group(
        groupField= 0,
        groupName= 'change'
      ),
      geometry= geo,
      scale= self.PIXEL_SCALE_METERS,
      tileScale= 4,
      crs= 'EPSG:32610',
      maxPixels= 1e9
    )
    # extract the list of dictionaries 
    groups = ee.List(label_stats.get('groups'))
    return groups.getInfo()

