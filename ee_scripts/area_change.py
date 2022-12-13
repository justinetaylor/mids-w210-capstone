'''
This class uses Google Earth Engine to compute
the area of vegetation change (trees lost, grass
gained etc.)  for a given area over a year. It
also goes and retrieves the data (MOD15, GRIDMET,
USGS Elevation, Dynamic World values) for each of
the pixels that indicated a vegetation change.

# Sample Usage

-------------
import time
s = time.time()

geometry = [[-124.14507547221648, 41.11806816998926],
            [-124.14507547221648, 41.11457637941072],
            [-124.1394964774655, 41.11457637941072],
            [-124.1394964774655, 41.11806816998926]]

# [ONLY TO MODEL WITH GEE]
gm = GeeModel()
# adjust and write training data. only uncomment when altering training data.
# gm.adjust_and_write_training_data()  
gm.train_model()

def get_data(geometry, year):
    ac = AreaChange(geometry, year)

    # check area size
    print("Is Area Size OK: ", ac.is_area_within_limits())

    # detect veg change and compute change amounts 
    area_change = ac.get_area_of_change()
    print('Changes in land class (m^2): ', area_change)

    # [not required] get number of pixels that changed 
    pixel_count = ac.get_pixel_count('label_argmax')

    # [not required] get annual gpp estimate accoring to MOD17
    print("MOD17 Annual GPP Estimate: ", ac.mod17_estimate())

    # [ONLY TO MODEL WITH GEE] get inference data AND run inference:
    ac.output_mode = 'fc'
    fc = ac.get_change_that_might_occur()
    gpp = gm.inference(fc)
    print("CALCUlator Total Estimated GPP: ", gpp)

    
    # [ONLY TO MODEL WITH SKLEARN] get inference data:
    df_for_inference = ac.get_change_that_might_occur()
    print("Describe DataFrame ", df_for_inference.describe())
    print("Size ", len(df_for_inference.index))

get_data(geometry, 2017)
get_data(geometry, 2018)
get_data(geometry, 2019)
get_data(geometry, 2020)
get_data(geometry, 2021)
e = time.time()
print("Elapsed Time: ",e-s)
'''
import math
import geemap
import pandas as pd
# import threading
# import apscheduler 
import numpy as np
import ee
from datetime import datetime
import time 
# from sklearn import ensemble
# from geemap import ml
service_account = "calucapstone@ee-calucapstone.iam.gserviceaccount.com"
credentials = ee.ServiceAccountCredentials(service_account, '.private-key.json')
ee.Initialize(credentials)

class AreaChange:
    #  an ee.Image with 1 band. That band has integer values
    #  between 0 and 10 representing the change in land class.
    change = None

    # where to ignore pixels
    change_mask = None

    output_mode = 'df'
    # constants
    MIN_PIXEL_SCALE_METERS = 10
    NODATA_VALUE = -1
    DYNAMIC_WORLD_COLUMNS = ['water',
                             'trees',
                             'grass',
                             'flooded_vegetation',
                             'crops',
                             'shrub_and_scrub',
                             'built',
                             'bare',
                             'snow_and_ice']

    # BIG_LABELS: imagine a pixel in a dynamic world image has
    # land class label X at time A and label Y at time B. We can
    # detect the change by multiplying the label at time A by 100
    # and adding the label at time A and time B together. If we
    # were to do that, we'd get the following possible values:
    BIG_LABELS = ee.List(
        [0, 1, 2, 3, 4, 5, 6, 7, 8,
         100, 101, 102, 103, 104, 105, 106, 107, 108,
         200, 201, 202, 203, 204, 205, 206, 207, 208,
         300, 301, 302, 303, 304, 305, 306, 307, 308,
         400, 401, 402, 403, 404, 405, 406, 407, 408,
         500, 501, 502, 503, 504, 505, 506, 507, 508,
         600, 601, 602, 603, 604, 605, 606, 607, 608,
         700, 701, 702, 703, 704, 705, 706, 707, 708,
         800, 801, 802, 803, 804, 805, 806, 807, 808])

    # ADJUSTED_LABELS: We don't care about most of the possible
    # changes. For example, if water stayed water....we don't care.
    # However, we do care if grass went to built or if built turned into
    # grass. So we set most of the list to 0 and we remap changes we care
    # to new labels. So now 1 represents trees that are now considered built.

    # See:
    # https://docs.google.com/spreadsheets/d/1jRIu3ly6NOzFR9X5of_NDq2ZfgFpiM5AL9LdtuzXDiw/edit?usp=sharing
    ADJUSTED_LABELS = ee.List(
        [0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 1, 0,
         0, 0, 0, 0, 0, 0, 2, 2, 0,
         0, 0, 0, 0, 0, 0, 3, 3, 0,
         0, 0, 0, 0, 0, 0, 4, 4, 0,
         0, 0, 0, 0, 0, 0, 5, 5, 0,
         0, 6, 7, 8, 9, 10, 0, 0, 0,
         0, 6, 7, 8, 9, 10, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0])

    def __init__(self, geo, year):
        if isinstance(geo, list):
            # an ee.Geometry.Polygon representing the area to analyse
            self.geo = ee.Geometry.Polygon(geo)
        else:
            self.geo = geo

        # the year to analyze.
        self.year = year


    def get_area_of_change(self):
        '''
        This method computes the area (meters^2) of change in
        each category (trees lost, trees gained, grass lost, etc).

        Arguments:
            geometry: list of [longitude, latitude] pairs. Note,
                      the order of longitude and latitude.
            year: the year to detect change

        Returns:
            A list of dictionaries:
             [{'change': 0, 'sum': 1000943766.2943573},
             {'change': 1, 'sum': 7871904.116004944},
             {'change': 2, 'sum': 915519.3800354004},
             {'change': 4, 'sum': 5933634.289802551},
             {'change': 5, 'sum': 2133110.9543914795},
             {'change': 6, 'sum': 8753569.066741943},
             {'change': 7, 'sum': 116530830.96776581},
             {'change': 8, 'sum': 10407.224006652832},
             {'change': 9, 'sum': 3410677.085800171},
             {'change': 10, 'sum': 19004752.376182556}]

            Where 0-10 map to the categories of change:
            0   other
            1   trees_gained
            2   grass_gained
            3   flooded_vegetation_gained
            4   crops_gained
            5   shrub_and_scrub_gained
            6   trees_lost
            7   grass_lost
            8   flooded_veg_lost
            9   crops_lost
            10  shrub_and_scrub_lost
        '''
        self.get_annual_change_image()

        # get the area (meters^2) of each pixel
        pixelArea = ee.Image.pixelArea().rename('area')

        # add a band that has the size of each pixel
        self.change = self.change.addBands(pixelArea)

        # group pixels by label and compute the sum of the area
        label_stats = self.change.reduceRegion(
            reducer=ee.Reducer.sum().unweighted().group(
                groupField=0,
                groupName='change'
            ),
            geometry=self.geo,
            scale=self.MIN_PIXEL_SCALE_METERS,
            tileScale=16,
            crs='EPSG:32610',
            maxPixels=1e9,
            bestEffort=True
        )

        # extract the list of dictionaries
        groups = ee.List(label_stats.get('groups'))
        return groups.getInfo()

    def get_change_that_might_occur(self):
        dwCol = (ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
                    .filterBounds(self.geo)
                    .filter(ee.Filter.calendarRange(self.year, self.year, 'year')))

        composite = (dwCol
                 .select(self.DYNAMIC_WORLD_COLUMNS)
                 .reduce(ee.Reducer.mean()).unmask(self.NODATA_VALUE)
                 .toArray().arrayArgmax().arrayGet([0])
                 .rename('label_argmax'))

        all_labels = ee.List([0,1,2,3,4,5,6,7,8])
        veg_labels = ee.List([0,1,2,3,4,5,0,0,0])
        composite = composite.select('label_argmax').remap(all_labels, veg_labels).rename('label_argmax')
        self.change_mask = composite.neq(0)
        self.change = composite.select('label_argmax').updateMask(self.change_mask)
        return self.get_climate_data_for_change_and_join()


    def get_change_that_occurred(self):
        self.get_annual_change_image()
        return self.get_climate_data_for_change_and_join()

    def get_climate_data_for_change_and_join(self):
        """
        This method gets all data needed for inference including
        gridmet, mod15, dynamic world, and elevation as well as 
        mod17 for comparison. 

        Returns:
            pandas DataFrame
        """

        start_date = str(self.year - 1) + '-12-01'
        end_date = str(self.year) + '-11-30'

        elev = self.get_elevation_for_change(start_date, end_date)
        mod15 = self.get_mod15_for_change(start_date, end_date)
        gridmet = self.get_eight_day_gridmet_for_change(start_date, end_date)
        dw = self.get_dw_for_change()

        def add_elevation(dw_img):
          return dw_img.addBands(elev.select("elevation"))
        dw = dw.map(add_elevation)
       
        # Join GRIDMET and MOD15
        tenDaysMillis = 5 * 24 * 60 * 60 * 1000;
        timeFilterGridmetMod = ee.Filter.And(
          ee.Filter.maxDifference(
            difference= tenDaysMillis,
            leftField= 'gridmet_start_date_millis',
            rightField= 'mod_start_date_millis'
          ),
          ee.Filter.intersects(
              leftField= '.geo',
              rightField= '.geo',
            )
        );
        saveAllJoinGridmetMod = ee.Join.saveAll(
          matchesKey= 'mod_match',
          ordering= 'mod_date',
          ascending= True,
          outer= True
        );
        GridmetModJoined = saveAllJoinGridmetMod.apply(gridmet, mod15.select(["Lai_500m","Fpar_500m"]), timeFilterGridmetMod);

        def flatten_join_mod_gridmet(join_feature):
          img = ee.Image(join_feature)
          matches = ee.List(img.get("mod_match"))
          result = ee.Algorithms.If(matches.size(),img.addBands(matches.get(0)) ,img)
          return result

        GridmetModJoined = GridmetModJoined.map(flatten_join_mod_gridmet)


        # Join GRIDMET/MOD with DW/ELEV
        sixtytwoDaysMillis = 62 * 24 * 60 * 60 * 1000;
        timeFilterDW = ee.Filter.And(
          ee.Filter.maxDifference(
            difference= sixtytwoDaysMillis,
            leftField= 'gridmet_start_date_millis',
            rightField= 'dw_start_date_millis'
          ),
          ee.Filter.intersects(
              leftField= '.geo',
              rightField= '.geo',
            )
        );
        saveAllJoinDW = ee.Join.saveAll(
          matchesKey= 'dw_match',
          ordering= 'dw_start_date',
          ascending= True,
          outer= True
        );
        DWJoined = saveAllJoinDW.apply(GridmetModJoined, dw, timeFilterDW);

        def flatten_join_dw(join_feature):
          img = ee.Image(join_feature)
          matches = ee.List(img.get("dw_match"))
          result = ee.Algorithms.If(matches.size(),img.addBands(matches.get(0)) ,img)
          return result

        DWJoined = DWJoined.map(flatten_join_dw)

        final_result = ee.FeatureCollection(DWJoined.map(self.convert_to_fc_10m).flatten())
        if self.output_mode == 'df':
            return self.convert_fc_to_dataframe(final_result, [ 'change', 
                                    'elevation',
                                    'gridmet_date', 
                                    'tmmn', 
                                    'tmmx', 
                                    'vpd', 
                                    'srad',
                                    'mod_date', 
                                    'Fpar_500m', 
                                    'Lai_500m', 
                                    'dw_start_date',
                                    'bare_mean',
                                    'grass_mean',
                                    'label_mode',
                                    'label_argmax',
                                    'crops_mean',
                                    'built_mean',
                                    'change',
                                    'latitude',
                                    'water_mean',
                                    'flooded_vegetation_mean',
                                    'shrub_and_scrub_mean',
                                    'snow_and_ice_mean',
                                    'trees_mean',
                                    'quarter',
                                    'longitude'])
        else:
            return final_result


    def get_annual_change_image(self):
        '''
        This method detects the change in land area classification
        during a year.
        '''

        # first, we'll look at Oct-Dec of Year-1
        time_a = (str(self.year - 1) + '-09-01', str(self.year - 1) + '-12-31')
        # get the land class images for this time
        imgCol_1 = (ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
                    .filterBounds(self.geo)
                    .filter(ee.Filter.date(time_a[0], time_a[1])))
        # take the mean over time and compute the most representative land class.
        # we'll also multiply all pixels by 100. This will help detect change.
        img_1 = (imgCol_1
                 .select(self.DYNAMIC_WORLD_COLUMNS)
                 .reduce(ee.Reducer.mean()).unmask(self.NODATA_VALUE)
                 .toArray().arrayArgmax().arrayGet([0])
                 .rename('label_1_argmax')
                 .multiply(100))

        # next, we'll look at Jan-March of Year+1
        time_b = (str(self.year + 1) + '-01-01', str(self.year + 1) + '-03-01')
        # get the land class images for this time
        imgCol_2 = (ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
                    .filterBounds(self.geo)
                    .filter(ee.Filter.date(time_b[0], time_b[1])))
        # take the mean over time and compute the most representative land
        # class.
        img_2 = (imgCol_2
                 .select(self.DYNAMIC_WORLD_COLUMNS)
                 .reduce(ee.Reducer.mean()).unmask(self.NODATA_VALUE)
                 .toArray().arrayArgmax().arrayGet([0])
                 .rename('label_2_argmax'))

        # stack the two results on top of each other so we can compare the
        # most representative land class (argmax) at each pixel
        dwImg_combined = img_1.addBands(img_2)
        change = (dwImg_combined
                  .select('label_1_argmax')
                  .add(dwImg_combined.select('label_2_argmax'))
                  .remap(self.BIG_LABELS, self.ADJUSTED_LABELS)
                  .rename('change'))

        # ignore all pixels with a 0 label
        # this helps with time and space limitations
        self.change_mask = change.neq(0)
        self.change = change.updateMask(self.change_mask)


    def get_daily_gridmet_for_change(self, start_date, end_date):
        '''
        This method gets daily minimum temperature, maximum temperature,
        vapor pressure, and shortwave radiation from earthengine.
        Spatial resoluton: 4km^2
        * only this or the method below is used at once.

        Arguments:
            start_date, end_date: date interval for getting data

        Returns:
            ee.ImageCollection where each image represents a day.
        '''

        gridmet_dataset = (ee.ImageCollection('IDAHO_EPSCOR/GRIDMET')
                           .select(['tmmn', 'tmmx', 'vpd', 'srad'])
                           .filterBounds(self.geo)
                           .filter(ee.Filter.date(start_date, end_date)))

        # for each image in the collection, clip it to the exact area we want
        # and set the date in two formats.
        def finalize_annual_gridmet_img(gridmet_img):
            return (
                gridmet_img.updateMask(
                    self.change_mask).set(
                    'gridmet_date',
                    gridmet_img.date().format('YYYY-MM-dd')) .set(
                    'gridmet_start_date_millis',
                    gridmet_img.date().millis()))

        gridmet_dataset = gridmet_dataset.map(finalize_annual_gridmet_img)
        return gridmet_dataset


    def get_eight_day_gridmet_for_change(self, start_date, end_date):
        '''
        This method gets 8 day average minimum temperature, maximum temperature,
        vapor pressure, and shortwave radiation from earthengine.
        Spatial resoluton: 4km^2
        * only this or the method above is used at once.

        Arguments:
            start_date, end_date: date interval for getting data

        Returns:
            ee.ImageCollection where each image represents 8 days
        '''

        # a weeks time in milliseconds
        weekMillis = 8 * 24 * 60 * 60 * 1000

        # a list of dates where each date represents the first day of
        # the week
        listMap = (
            ee.List.sequence(
                ee.Date(start_date).millis(),
                ee.Date(end_date).millis(),
                weekMillis))

        # for each week, get a gridmet image for each day
        # take the average and clean up the image


        def reduce_to_weekly(dateMillis):
            new_start = ee.Date(dateMillis)

            gridmet_week = (
                ee.ImageCollection('IDAHO_EPSCOR/GRIDMET').filterBounds(
                    self.geo) .filter(
                    ee.Filter.date(
                        new_start,
                        new_start.advance(
                            1,
                            'week'))) .select(
                        [
                            'tmmn',
                            'tmmx',
                            'vpd',
                            'srad']))
            avg = (gridmet_week
                   .reduce(ee.Reducer.mean())
                   .set('gridmet_start_date_millis', new_start.millis())
                   .set('gridmet_date', new_start.format('YYYY-MM-dd'))
                   .updateMask(self.change_mask))
            return avg

        gridmet_dataset = listMap.map(reduce_to_weekly)

        return gridmet_dataset


    def get_elevation_for_change(self, start_date, end_date):
        '''
        This method gets elevation data from earthengine.
        Spatial resolution: 10m^2

        Arguments:
            start_date, end_date: date interval for getting data

        Returns:
            ee.Image with elevation for each pixel
        '''

        elevation_dataset = ee.Image('USGS/3DEP/10m').select('elevation')
        return (elevation_dataset
                .updateMask(self.change_mask))


    def get_mod15_for_change(self, start_date, end_date):
        '''
        This method gets Leaf Area Index and Photosynthetically Active Radiation
        from earthengine.
        Spatial resolution: 500m^2
        Temporal resolution: ~8 days

        Arguments:
            start_date, end_date: date interval for getting data

        Returns:
            ee.ImageCollection where each image represents the best pixel
            values over the last 8 day period
        '''

        mod15_dataset = (ee.ImageCollection('MODIS/061/MOD15A2H')
                         .filterBounds(self.geo)
                         .filter(ee.Filter.date(start_date, end_date))
                         .select(['Lai_500m', 'Fpar_500m']))


        def finalize_mod_img(mod_img):
            # notice that we have .unmask(0.01) here. MOD15 has low spatial resolution
            # and in areas that are very built up (cities) there could be null values
            # for Leaf Area Index or Photosynthetically Active Radiation due to such
            # little vegetation. We want to avoid null values, so we set those to a
            # super small value (0.01)
            return (
                mod_img.unmask(0.01).updateMask(
                    self.change_mask) .set(
                    'mod_start_date_millis',
                    mod_img.date().millis()) .set(
                    'mod_date',
                    ee.Date(
                        mod_img.date()).format('YYYY-MM-dd')))

        mod15_dataset = mod15_dataset.map(finalize_mod_img)
        return mod15_dataset


    def get_dw_for_change(self):
        '''
        This method gets the land class probability distribution for
        each quarter of a year from earth engine.
        Spatial resolution: 10^2
        Temporal resolution: Quarterly

        Returns:
            ee.ImageCollection where each image represents the average
            land class probabilities for each quarter
        '''

        # quarter date ranges: winter, spring, summer, fall
        # note: winter starts december of year-1
        quarters = [
            (str(self.year - 1) + '-12-01', str(self.year) + '-03-01'),
            (str(self.year) + '-03-02', str(self.year) + '-05-31'),
            (str(self.year) + '-06-01', str(self.year) + '-08-31'),
            (str(self.year) + '-09-01', str(self.year) + '-11-30')]
        all_quarters = []
        for i, quarter_dates in enumerate(quarters):
            quarter_representation = ee.Image.constant(i + 1)
            dw_dataset = (
                ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterBounds(
                    self.geo).filter(
                    ee.Filter.date(
                        quarter_dates[0],
                        quarter_dates[1])))

            # create an image with the most representative landclass (argmax)
            dw_quarterly_argmax_label = (
                dw_dataset .select(
                    self.DYNAMIC_WORLD_COLUMNS) .reduce(
                    ee.Reducer.mean()).unmask(
                    self.NODATA_VALUE).toArray().arrayArgmax().arrayGet(
                        [0]).rename('label_argmax_numeric'))

            # create an image with the average values of the land class
            # probabilities
            dw_quarterly_mean = (
                dw_dataset .select(
                    self.DYNAMIC_WORLD_COLUMNS) .reduce(
                    ee.Reducer.mean()).unmask(
                    self.NODATA_VALUE) .addBands(
                    dw_quarterly_argmax_label.select('label_argmax_numeric')) .addBands(
                        quarter_representation.select('constant').rename('quarter')) .set(
                            'dw_start_date_millis', ee.Date(
                                ee.List(quarter_dates).get(0)).millis()) .set(
                                    'dw_start_date', ee.Date(
                                        ee.List(quarter_dates).get(0)).format('YYYY-MM-dd')) .updateMask(
                                            self.change_mask))

            all_quarters.append(dw_quarterly_mean)

        return ee.ImageCollection.fromImages(all_quarters)


    def convert_fc_to_dataframe(self, fc, columns):
        '''
        This method converts an ee.FeatureCollection into a
        pandas.DataFrame. If the ee.FeatureCollection is empty
        it returns an empty pandas.DataFrame with the column
        argument as keys.

        Arguments:
            fc: ee.FeatureCollection
            columns: list of column names

        Returns:
            pandas.DataFrame
        '''

        # we use the geemap library to convert to a pandas.DataFrame
        # geemap limits this conversion to 5000 elements so
        # we need to do it in batches and then concatenate them.

        exports = []
        export_number = 0
        while(True):
            print("Export Number: ", export_number)
            try:
                subset = ee.FeatureCollection(fc.toList(5000, export_number * 5000))
                df = geemap.ee_to_pandas(subset)
                exports.append(df)
                export_number+=1
            except:
                break

        if len(exports) == 0:
            return pd.DataFrame(dict.fromkeys(columns), index=[0])
        elif len(exports) == 1:
            return exports[0]
        else:
            return pd.concat(exports, axis=0, ignore_index=True)

    def convert_to_fc_10m(self, img):
        '''
        This method converts an ee.Image to an
        ee.FeatureCollection. This makes it easier to export.

        Arguments:
            img: image to convert

        Returns:
            ee.FeatureCollection where each feature is a pixel
            and has a property for each band in the image.
        '''
        pixelLatLngImg = ee.Image.pixelLonLat()
        added_lat_lng = ee.Image(img).addBands(pixelLatLngImg)
        feature_collection = added_lat_lng.sample(
            region=self.geo,
            numPixels=1e9,
            geometries=True,
            scale=50,
            projection='EPSG:4326',
            tileScale=16
        )

        return feature_collection


    def get_pixel_count(self, band):
        """
        Gets pixel statistics about the change that occurred. 
        Ex. What percentage of the area had vegetation change?
        """
        pixel_count = (self.change.select(band).reduceRegion(
        reducer= ee.Reducer.count(),
        geometry= self.geo,
        scale= 10,
        tileScale=16,
        maxPixels= 1e9, bestEffort=True).get(band))

        all_pixels = (self.change.select(band).unmask().reduceRegion(
        reducer= ee.Reducer.count(),
        geometry= self.geo,
        scale= 10,
                tileScale=16,

        maxPixels= 1e9, bestEffort=True).get(band))

        ratio = ee.Number(pixel_count).divide(all_pixels).multiply(100)
        print("Number of unmasked pixels: ", pixel_count.getInfo())
        print("Total nuber of pixels in the area: ", all_pixels.getInfo())
        print("Percentage: ", ratio.getInfo())


    def is_area_within_limits(self):
        """
        Checks if the input geometry is too big
        """
        area = self.geo.area().getInfo()
        if  area > 1000000:
            return False
        return True
            

    def mod17_estimate(self):
        """
        Returns GPP kg*C/m^2/year
        """
        gpp_col = (ee.ImageCollection('UMT/NTSG/v2/LANDSAT/GPP')
                            .filter(ee.Filter.calendarRange(self.year, self.year, 'year'))
                            .select("GPP"))
        reduced  = gpp_col.reduce(ee.Reducer.sum())
        reducedRegion = reduced.reduceRegion(geometry=self.geo, reducer=ee.Reducer.sum(), scale=30)
        return reducedRegion.getInfo()


class GeeModel():
    classifier = None
    classifier_export_task = None 
    training_features = ['LATITUDE_x',
                          'LONGITUDE_x' ,
                          'srad_mean'  , 
                          'tmmn_mean',
                           'tmmx_mean',
                           'vpd_mean'  ,  
                           'Fpar_500m_mean'  ,
                           'Lai_500m_mean'      , 
                           'water_mean_mean' ,
                           'trees_mean_mean' ,
                           'grass_mean_mean' ,
                           'flooded_vegetation_mean_mean' ,   
                           'crops_mean_mean' ,
                           'shrub_and_scrub_mean_mean'   ,
                           'built_mean_mean',
                            'bare_mean_mean',  
                           'snow_and_ice_mean_mean'  ,
                          ]
    label = 'GPP_mean'

    def adjust_and_write_training_data(self):
        grouped_mean_gpp= pd.read_csv('../data/8_day_grouped_data.csv', sep = '\t')
        grouped_mean_gpp =  grouped_mean_gpp.drop(['Unnamed: 0'], axis=1)

        good_sites= [site for site in grouped_mean_gpp['SITE_ID'].unique() if site not in  ['US-Ne1','US-Ne2','US-Ne3'] ]
        grouped_mean_gpp = grouped_mean_gpp[grouped_mean_gpp['SITE_ID'].isin(good_sites)]

        X = grouped_mean_gpp[self.training_features]
        X['label_argmax_numeric_mean']= X['label_argmax_numeric_mean'].astype("int64")
        X['label_argmax_numeric_mean']= X['label_argmax_numeric_mean'].astype("category")

        y = grouped_mean_gpp["GPP_mean"]

        #random chose site for train without replacement with equal probability for 80/20 split
        train_sites = np.random.choice(good_sites, (27), replace = False)
        test_sites = [site for site in good_sites if site not in train_sites ]
            
        print("Train:",train_sites, "\nTest", test_sites)
        train = grouped_mean_gpp[grouped_mean_gpp['SITE_ID'].isin(train_sites)]
        test = grouped_mean_gpp[grouped_mean_gpp['SITE_ID'].isin(test_sites)]

        train.to_csv('training_data.csv', index=False)
        test.to_csv('testing_data.csv', index=False)

    # showcase work: currently not used / working. please ignore.
    # def check_export_status(self):
    #     # showcase work: currently not used / working. please ignore.
    #     scheduler = apscheduler.scheduler.Scheduler()
    #     scheduler.start()
    #     def check_status():
    #         print("Classifier Export Status", self.classifier_export_task.status()['status'])

    #     scheduler.add_interval_job(check_status, seconds = 30)
    #     if self.classifier_export_task.status()['status'] == 'COMPLETED':
    #         scheduler.shutdown()
    #         return
         
    #     # return asset_name


    # def save_model(self):
    #     trees = ee.List(ee.Dictionary(self.classifier.explain()).get('trees'))
        
    #     def create_tree_feature(tree):
    #         return ee.Feature(None, {'tree':tree})

    #     col = ee.FeatureCollection(trees.map(create_tree_feature))

    #     self.classifier_export_task = ee.batch.Export.table.toAsset(collection=col, assetId='projects/ee-calucapstone/assets/trainedModeltest')
    #     self.classifier_export_task.start()
    #     print(self.classifier_export_task.status())
    #     while(self.classifier_export_task.status()['state'] not in ('COMPLETED', 'FAILED') ):
    #         print(self.classifier_export_task.status()['state'])
    #         time.sleep(15)

    #     print(self.classifier_export_task.status())
    #     # self.classifier_export_task.cancelOperation()
    #     folder = ee.data.getAssetRoots()# [0]['id']
    #     # assets = ee.data.listAssets({'parent': folder})
    #     print(folder)
    #     # Load classifier
    #     # var trees = ee.FeatureCollection(AssetName).aggregate_array('tree').aside(print)
    #     # var classifier = ee.Classifier.decisionTreeEnsemble(trees)


    def train_model(self):
        train = pd.read_csv('training_data.csv')

        features = []
        for index, row in train.iterrows():
            f = ee.Feature(ee.Geometry.Point([row['LONGITUDE_x'],row['LATITUDE_x']]) ,row.to_dict())
            features.append(f)

        ee_training_features = ee.FeatureCollection(features)

        # Filter nulls 
        # TODO: Need to validate the effect of this on training
        ee_training_features = ee_training_features.filter(ee.Filter.notNull(self.training_features))

        # Random Forest Regression Classifier 
        self.classifier = (ee.Classifier.smileRandomForest(**{
            'numberOfTrees':750, 
            'variablesPerSplit': 6, 
            'minLeafPopulation': 295, 
            'bagFraction': 0.9, 
            'maxNodes': 266, 
            'seed': 0})
          .setOutputMode('REGRESSION')
          .train(**{
            'features': ee_training_features,
            'classProperty': self.label,
            'inputProperties': self.training_features
            }))
                
        print("Classifier: ", self.classifier.explain().getInfo())  

    def inference(self, fc):

        def rename_feature_properties(feature):
            return ee.Feature(feature.geometry(), { 
              'LATITUDE_x': feature.get('latitude'),
              'LONGITUDE_x': feature.get('latitude'),
              'srad_mean'   : feature.get('srad_mean'),
              'tmmn_mean'   : feature.get('tmmn_mean'),
              'tmmx_mean'   : feature.get('tmmx_mean'),
              'vpd_mean': feature.get('vpd_mean'),
              'Fpar_500m_mean': feature.get('Fpar_500m')    ,
              'Lai_500m_mean'   : feature.get('Lai_500m'),
              'ee_elevation_mean': feature.get('elevation') ,
              'water_mean_mean' : feature.get('water_mean'),
              'trees_mean_mean' : feature.get('trees_mean'),
              'grass_mean_mean' : feature.get('grass_mean'),
              'flooded_vegetation_mean_mean'    : feature.get('flooded_vegetation_mean'),
              'crops_mean_mean' : feature.get('crops_mean'),
              'shrub_and_scrub_mean_mean'   : feature.get('shrub_and_scrub_mean'),
              'built_mean_mean': feature.get('built_mean'), 
              'bare_mean_mean'  : feature.get('bare_mean'),
              'snow_and_ice_mean_mean': feature.get('snow_and_ice_mean')    
            })

        # Map the column names to match the training data
        resultRenamed = fc.map(rename_feature_properties)

        # Filter out any data points with null values for dynamic world
        # This can happen if one quarter is super cloudy. It's usually ok.
        # TODO: Need to validate the effect of this on training and inference
        resultNullsFiltered = resultRenamed.filter(ee.Filter.notNull(['water_mean_mean' ,
                                'trees_mean_mean'   ,
                                'grass_mean_mean'   ,
                                'flooded_vegetation_mean_mean'  ,
                                'crops_mean_mean'   ,
                                'shrub_and_scrub_mean_mean' ,
                                'built_mean_mean',
                                'bare_mean_mean'    ,
                                'snow_and_ice_mean_mean']))
        predictions = resultNullsFiltered.classify(self.classifier, 'predicted_gpp')
        total = predictions.aggregate_sum('predicted_gpp')
        return total.getInfo()

