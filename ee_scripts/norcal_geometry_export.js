/*
Run in the online code editor at code.earthengine.google.com
*/

var county_names = ['Del Norte', 'Humboldt', 'Modoc', 'Siskiyou', 'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa', 'El Dorado', 'Glenn', 'Lake', 'Lassen', 'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Placer', 'Plumas', 'Sacramento', 'San Benito', 'San Francisco', 'San Joaquin', 'San Mateo', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tuolumne', 'Yolo', 'Yuba', 'Del Norte', 'Humboldt', 'Modoc', 'Siskiyou', 'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa', 'El Dorado', 'Glenn', 'Lake', 'Lassen', 'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Placer', 'Plumas', 'Sacramento', 'San Benito', 'San Francisco', 'San Joaquin', 'San Mateo', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tuolumne', 'Yolo', 'Yuba', 'Del Norte', 'Humboldt', 'Modoc', 'Siskiyou', 'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa', 'El Dorado', 'Glenn', 'Lake', 'Lassen', 'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Placer', 'Plumas', 'Sacramento', 'San Benito', 'San Francisco', 'San Joaquin', 'San Mateo', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tuolumne', 'Yolo', 'Yuba', 'Del Norte', 'Humboldt', 'Modoc', 'Siskiyou', 'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa', 'El Dorado', 'Glenn', 'Lake', 'Lassen', 'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Placer', 'Plumas', 'Sacramento', 'San Benito', 'San Francisco', 'San Joaquin', 'San Mateo', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tuolumne', 'Yolo', 'Yuba', 'Del Norte', 'Humboldt', 'Modoc', 'Siskiyou', 'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa', 'El Dorado', 'Glenn', 'Lake', 'Lassen', 'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Placer', 'Plumas', 'Sacramento', 'San Benito', 'San Francisco', 'San Joaquin', 'San Mateo', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tuolumne', 'Yolo', 'Yuba']
var level_two_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level2");

var northern_counties = level_two_boundaries.filter(
                    ee.Filter.and(
                        ee.Filter.eq("ADM1_NAME", "California"), 
                        ee.Filter.inList("ADM2_NAME",county_names))
                    )
                    

Map.addLayer(northern_counties)
Export.table.toDrive({
  collection: northern_counties,
  description:'ExportOfGeometries',
  fileFormat: 'GeoJSON',
   selectors: ['ADM2_NAME', '.geo']
});
