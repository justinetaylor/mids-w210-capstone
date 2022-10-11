// Run this code in the code editor: code.earthengine.google.com

// Get the zipcode feature collection 
// It only has zipcodes in the USA
var zipcodes = ee.FeatureCollection("TIGER/2010/ZCTA5").select("ZCTA5CE10")
// Drop geometries
var noGeom = zipcodes.select({
  propertySelectors: ['ZCTA5CE10'],
  retainGeometry: false
});
// Export to drive
Export.table.toDrive({
  collection: noGeom,
  description:'zipcodes_without_geometry',
  fileFormat: 'csv'
});

// Get the county feature collection. Limit to USA only
var counties = ee.FeatureCollection("FAO/GAUL/2015/level2").filter(ee.Filter.eq("ADM0_NAME", "United States of America"))
// Drop geometries
var noGeom = counties.select({
  propertySelectors: ['ADM2_NAME', 'ADM1_NAME'],
  retainGeometry: false
});
// Export to drive
Export.table.toDrive({
  collection: noGeom,
  description:'counties_without_geometry',
  fileFormat: 'csv'
});
