import ee
ee.Initialize()
ee.Authenticate()

elev = ee.Image('MERIT/DEM/v1_0_3')
slope = ee.Terrain.slope(elev)

topo = ee.Image.cat(elev, slope)
  # Computed images do not have a 'system:time_start' property add one based
  # on when the data were collected.
  .set('system:time_start', ee.Date('2000-01-01').millis())
topoCol = ee.ImageCollection([topo])


# Define parameters for the zonalStats function.
params = {
  bands: [0, 1],
  bandsRename: ['elevation', 'slope']
}


pts = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([-148.3235,64.6963	])),
  ee.Feature(ee.Geometry.Point([-149.2536,63.8784	])),
    ee.Feature(ee.Geometry.Point([-110.1777, 31.6637])),

])


function bufferPoints(radius, bounds) {
  return function(pt) {
    pt = ee.Feature(pt)
    return bounds ? pt.buffer(radius).bounds() : pt.buffer(radius)
  }
}

function zonalStats(ic, fc, params) {
  # Initialize internal params dictionary.
  _params = {
    reducer: ee.Reducer.mean(),
    scale: null,
    crs: null,
    bands: null,
    bandsRename: null,
    imgProps: null,
    imgPropsRename: null,
    datetimeName: 'datetime',
    datetimeFormat: 'YYYY-MM-dd HH:mm:ss'
  }

  # Replace initialized params with provided params.
  if (params) {
    for (param in params) {
      _params[param] = params[param] || _params[param]
    }
  }

  # Set default parameters based on an image representative.
  imgRep = ic.first()
  nonSystemImgProps = ee.Feature(null)
    .copyProperties(imgRep).propertyNames()
  if (!_params.bands) _params.bands = imgRep.bandNames()
  if (!_params.bandsRename) _params.bandsRename = _params.bands
  if (!_params.imgProps) _params.imgProps = nonSystemImgProps
  if (!_params.imgPropsRename) _params.imgPropsRename = _params.imgProps

  # Map the reduceRegions function over the image collection.
  results = ic.map(function(img) {
    # Select bands (optionally rename), set a datetime & timestamp property.
    img = ee.Image(img.select(_params.bands, _params.bandsRename))
      .set(_params.datetimeName, img.date().format(_params.datetimeFormat))
      .set('timestamp', img.get('system:time_start'))

    # Define final image property dictionary to set in output features.
    propsFrom = ee.List(_params.imgProps)
      .cat(ee.List([_params.datetimeName, 'timestamp']))
    propsTo = ee.List(_params.imgPropsRename)
      .cat(ee.List([_params.datetimeName, 'timestamp']))
    imgProps = img.toDictionary(propsFrom).rename(propsFrom, propsTo)

    # Subset points that intersect the given image.
    fcSub = fc.filterBounds(img.geometry())

    # Reduce the image by regions.
    return img.reduceRegions({
      collection: fcSub,
      reducer: _params.reducer,
      scale: _params.scale,
      crs: _params.crs
    })
    # Add metadata to each feature.
    .map(function(f) {
      return f.set(imgProps)
    })
  }).flatten().filter(ee.Filter.notNull(_params.bandsRename))

  return results
}

ptsTopo = pts.map(bufferPoints(10, false))
ptsTopoStats = zonalStats(topoCol, ptsTopo, params)
print(ptsTopoStats)

