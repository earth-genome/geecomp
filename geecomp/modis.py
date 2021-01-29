
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os

import ee
ee.Initialize()
import geemap

from geecomp.aoi import build_aoi

def export(image_object, aoi, tif_name, crs, resolution, local_dir):

    if local_dir:
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        geemap.ee_export_image(
            image_object,
            filename=os.path.join(local_dir, f'{tif_name}.tif'),
            region=aoi, scale=resolution, crs=crs, file_per_band=False)

    else:
        geemap.ee_export_image_to_drive(ee_object=image_object,
                                        description=tif_name,
                                        folder='GEE Composite',
                                        region=aoi,
                                        scale=resolution,
                                        crs=crs)

def run(args):

    vis_scales = {
        'min': args.scale_min,
        'max': args.scale_max
    }
        
    def vis(i):
        return i.visualize(**vis_scales)

    aoi = build_aoi(args.aoi_file)
    date_filter = ee.Filter.date(args.start_date, args.end_date)
    ic = ee.ImageCollection(args.collection).filter(date_filter)
    ic = ic.select(args.bands).map(vis)
    image_object = ic.reduce(ee.Reducer.first())

    # WIP: sort resolution, data_type; remove scale from this call: 
    
    export(image_object, aoi, args.tif_name, args.crs, args.resolution,
           args.local_dir)

def main():

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('aoi_file', type=str,
                        help='AOI file (a valid GeoJSON or a shapefile)')
    parser.add_argument('tif_name', type=str,
                        help='name of GeoTIFF to export')

    # ------------------ #
    # collection options #
    # ------------------ #
    parser.add_argument('--collection', type=str,
                        help='MODIS GEE Collection ID',
                        default='MODIS/006/MOD09GA')
    parser.add_argument('--start_date', type=str,
                        help='Start datetime',
                        default='2021-01-01')
    parser.add_argument('--end_date', type=str,
                        help='End datetime',
                        default='2021-02-01')
    parser.add_argument(
        '--bands', type=str, nargs='+', help='Bands to export',
        default=['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'])
    
    # -------------- #
    # export options #
    # -------------- #

    parser.add_argument('--crs', type=str,
                        help='CRS to export file',
                        default='EPSG:3857')
    parser.add_argument('--resolution', type=float,
                        help='Resolution to export GeoTIFF in meters',
                        default=500.0)
    parser.add_argument('--data_type', 
                        choices=['raw',
                                 'byte', # 0-255
                                 'float'], # 0-1`
                        help='Data type to export GeoTIFF',
                        default='raw')
    parser.add_argument('--scale_min', type=float,
                        help='Minimum value for scaling (raw)',
                        default=-100)
    parser.add_argument('--scale_max', type=float,
                        help='Maximum value for scaling (raw)',
                        default=8000)
    parser.add_argument('--local_dir', type=str,
                        help='Local directory to save to, instead of GDrive',
                        default=None)

    args = parser.parse_args()
    
    run(args)
    
if __name__ == "__main__":
    main()
