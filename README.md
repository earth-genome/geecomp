# Google Earth Engine Composite Tool

version: 0.0.1

Create nice composites from Google Earth Engine and download as GeoTIFF.

Current datasets:
- S2 TOA (L1C) 
- S2 SR (L2A)

Both support cloud masking with s2cloudless.

Other datasets are currently not supported, but will be added in the future.

## Dependencies

This tool depends on the google earth engine client API and geemap.
If freshly installing, make sure you activate your account:

```
python
import ee
ee.Activate()
```

## Installation

1. Check out this repository
2. (optional) Create a virtual Python environment
3. Install the package 

```
cd geecomp
mkvirtualenv geecomp
pip install .
```

## Usage

You can run the tool with the `--help` flag to get a sense of the options.
Upon installation, the tool can be invoked directly at the command line.
Upon export, the composite GeoTIFF be deposited in your Google Drive under the "GEE Composite" folder

```
geecomp --help
```

## Arguments

positional arguments:
*  aoi_file              AOI file (a valid GeoJSON or a shapefile)
*  tif_name              name of GeoTIFF to export

optional arguments:
*  -h, --help            show this help message and exit
*  --collection COLLECTION
                        Sentinel-2 GEE Collection ID (default: COPERNICUS/S2)
*  --start_date START_DATE
                        Start datetime (default: 2020-01-01)
*  --end_date END_DATE   End datetime (default: 2021-01-01)
*  --cloudy_pixel_percentage CLOUDY_PIXEL_PERCENTAGE
                        cloudy pixel percentage metadata to filter scenes by (0-100) (default: 60)
*  --bands BANDS [BANDS ...]
                        Bands to export (default: ['B4', 'B3', 'B2'])
*  --s2cloudless         apply s2cloudless cloud mask (default: False)
*  --cloud_thresh CLOUD_THRESH
                        s2cloudless cloud probability threshold (0-100) (default: 50)
*  --cloud_proj_dist CLOUD_PROJ_DIST
                        Scaled cloud projection distance (default: 1)
*  --cloud_buf CLOUD_BUF
                        Amount to dilate cloud pixels in meters (default: 50)
*  --composite {mean,median,max,minmosaic,quality,percentile}
                        Select composite operation (default: mean)
*  --quality_bands QUALITY_BANDS [QUALITY_BANDS ...]
                        Band(s) to compute quality composite over (default: ['B8', 'B4'])
*  --quality_pct QUALITY_PCT
                        Percentile (0-100) for quality composite (default: 100)
*  --pct PCT             Percentile (0-100) for percentile composite (default: 25)
*  --crs CRS             CRS to export file (default: EPSG:3857)
*  --resolution RESOLUTION
                        Resolution to export GeoTIFF in meters (default: 10.0)
*  --data_type {raw,byte,float}
                        Data type to export GeoTIFF (default: raw)
*  --scale_min SCALE_MIN
                        Minimum value for scaling (raw) (default: 0)
*  --scale_max SCALE_MAX
                        Maximum value for scaling (raw) (default: 3000)

