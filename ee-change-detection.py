import ee
import geemap 
import sys
from IPython.core.magic import line_magic, line_cell_magic, Magics, magics_class



"""

This class is stateless. 
It takes parameters, returns data, and doesn't store anything. 
Usage: 

"""

class ChangeDetector:

  # class variables
  no_data_value = -1

  big_labels = ee.List([0,1,2,3,4,5,6,7,8,
  100,101,102,103,104,105,106,107,108,
  200,201,202,203,204,205,206,207,208,
  300,301,302,303,304,305,306,307,308,
  400,401,402,403,404,405,406,407,408,
  500,501,502,503,504,505,506,507,508,
  600,601,602,603,604,605,606,607,608,
  700,701,702,703,704,705,706,707,708,
  800,801,802,803,804,805,806,807,808])

  adjusted_labels = ee.List([0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,1,1,0,
  0,0,0,0,0,0,2,2,0,
  0,0,0,0,0,0,3,3,0,
  0,0,0,0,0,0,4,4,0,
  0,0,0,0,0,0,5,5,0,
  0,6,7,8,9,10,0,0,0, 
  0,6,7,8,9,10,0,0,0,
  0,0,0,0,0,0,0,0,0])

  # meteorological definitions
  seasons = {'spring': ['-03-02', '-05-31'], 
             'summer': ['-06-01', '-09-01'], 
             'fall': ['-09-02', '-11-30'], 
             'winter_a': ['-12-01', '-12-31'], 
             'winter_b': ['-01-01', '-03-01'] 
            }

  def __init__(self):
    # initialize earth engine
    ee.Initialize()
    # authenticate earth engine
    ee.Authenticate()


  def get_image(self, ear, region_of_interest, season):
    # create composite
    dwCol = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterBounds(region_of_interest).filter(ee.Filter.date(year+"-01-01", year+"12-31"))
    dwCol_mode = dwCol.select('label').mode().unmask(no_data_value).clip(region_of_interest).rename('label_'+year)
    return dwCol_mode


  def compute_seasonal_change(self, start_date, end_date, region_of_interest):
    """
    Args:
    start_year: ex. "2016-01-01"
    end_year: ex. "2017-01-01"

    Returns: 
    data: list of lists matching the schema in storage.py
    """
    dwComposite_A = self.get_image(start_date)
    dwComposite_B = self.get_image(end_date)
    dwComposite_C = dwComposite_A.select('label_'+year_a).multiply(100).add(dwComposite_B).select('label_'+year_b).rename('big_change')
    dwComposite_C = dwComposite_C.remap(bigLabels, adjustedLabels).rename('adjusted_change')


    # TODO: Take the "adjusted_change" band and (1) count how many pixels have each label. 
    # Create a list of lists that has the schema that matches the one in storage
    return 


  def get_region(self, geometry_type, name):
    """
    Args:
    geometry_type: ex."COUNTY" or "ZIPCODE"
    name: ex. "Alameda" or "94545"

    Returns:
    region_of_interest: polygon
    """
    region_of_interest = None
    if geometry_type == "ZIPCODE":
      region_of_interest = ee.FeatureCollection("TIGER/2010/ZCTA5").filter(ee.Filter.eq("GEOID10", name))
    elif geometry_type == "COUNTY":
      region_of_interest = ee.FeatureCollection("FAO/GAUL/2015/level2").filter(ee.Filter.eq("ADM2_NAME", name))
    else:
      print("Invalid geometry type")
    return region_of_interest


region_of_interest = get_region("COUNTY", "Alameda")
winter_a_change = compute_seasonal_change('2016'+seasons['winter_a'][0],'2016'+seasons['winter_a'][1], region_of_interest)
spring_change= compute_seasonal_change('2016'+seasons['spring'][0],'2016'+seasons['spring'][1], region_of_interest)
summer_change= compute_seasonal_change('2016'+seasons['summer'][0],'2016'+seasons['summer'][1], region_of_interest)
fall_change = compute_seasonal_change('2016'+seasons['fall'][0],'2016'+seasons['fall'][1], , region_of_interest)
winter_b_change = compute_seasonal_change('2016'+seasons['winter_b'][0],'2016'+seasons['winter_b'][1], region_of_interest)

# TODO: sum all and store in database
# TODO: debug / make sure this runs 




