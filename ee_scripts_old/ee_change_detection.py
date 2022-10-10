import ee
ee.Initialize()

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

  adjusted_labels = ee.List(
  [0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,1,1,0,
  0,0,0,0,0,0,2,2,0,
  0,0,0,0,0,0,3,3,0,
  0,0,0,0,0,0,4,4,0,
  0,0,0,0,0,0,5,5,0,
  0,6,7,8,9,10,0,0,0, 
  0,6,7,8,9,10,0,0,0,
  0,0,0,0,0,0,0,0,0])


  def get_image(self, year, region_of_interest):
    # create composite
    label='label_'+year
    dwCol = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterBounds(region_of_interest).filter(ee.Filter.date(year+"-01-01", year+"-12-31"))
    dwCol_mode = dwCol.select('label').mode().unmask(self.no_data_value).clip(region_of_interest).rename(label)
    return dwCol_mode

 

  def compute_change_for_label(self,label, image, region_of_interest,crs_epsg,PIXEL_SCALE_METERS):
    mask = image.select("adjusted_change").eq(ee.Number(label))
    area = image.updateMask(mask).multiply(ee.Image.pixelArea().clip(region_of_interest))
    areaSum = area.reduceRegion(reducer= ee.Reducer.sum(),
                                  geometry= region_of_interest,
                                  scale= PIXEL_SCALE_METERS,
                                  crs= crs_epsg,
                                  maxPixels= 1e9)
    return areaSum.getInfo()

  def compute_change_in_region(self, region_of_interest, year):
    # cast year to an int so we can add to it later
    int_year = int(year)
    # get the dynamic world composite image for two consecutive years
    dwComposite_A = self.get_image(year, region_of_interest)
    dwComposite_B = self.get_image(str(int_year+1), region_of_interest)

    # create a new image with a band called "big change"
    # big change is: label from the first year*100 + label from the second year
    # this will give us a numeric value for all combinations of change
    dwComposite_C = dwComposite_A.select('label_'+year).multiply(100).add(dwComposite_B.select('label_'+str(int_year+1))).rename('big_change')
    # remap those values to new classes 0-10 where 0 is a class we don't care about
    dwComposite_C = dwComposite_C.remap(self.big_labels, self.adjusted_labels).rename('adjusted_change')

    # get the area of each pixel in m^2 in this county
    pixelArea = ee.Image.pixelArea().clip(region_of_interest);

    # define pixel scale and crs_epsg (this is for reducing later)
    PIXEL_SCALE_METERS = 10;
    crs_epsg = dwComposite_A.projection().crs();

    # for each label we're interested in
    labelsOfInterest = [1,2,3,4,5,6,7,8,9,10]
    # compute the area changed
    result = {}
    for label in labelsOfInterest:
      result[label] = self.compute_change_for_label(label, dwComposite_C, region_of_interest,crs_epsg,PIXEL_SCALE_METERS)

    return result

  def compute_change_in_county(self, county, state, year):
    # filter counties based on county and state name
    place_filter = ee.Filter.And(
    ee.Filter.eq("ADM2_NAME", county),
    ee.Filter.eq('ADM1_NAME', state));
    region_of_interest = ee.FeatureCollection("FAO/GAUL/2015/level2").filter(place_filter)
    return self.compute_change_in_region(region_of_interest, year)
    

  def compute_change_in_zipcode(self, zipcode, year):
      region_of_interest = ee.FeatureCollection("TIGER/2010/ZCTA5").filter(ee.Filter.eq("ZCTA5CE10", zipcode))
      return self.compute_change_in_region(region_of_interest, year)




