'''
aoi.py

Functions for dealing with AOIs
'''

import ee
import geemap


def build_aoi(aoi_file):
    if aoi_file.endswith('shp'):
        aoi = geemap.shp_to_ee(aoi_file)
    elif aoi_file.endswith('json'):
        aoi = geemap.geojson_to_ee(aoi_file)

    print('Loaded {} successfully'.format(aoi_file))

    return aoi.geometry()
