from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os

import ee
ee.Initialize()
import geemap

from geecomp.aoi import build_aoi
from geecomp.composite import compute_composite, export_composite
from geecomp.s2 import get_s2_img_col, add_s2cloudless


def run(args):
    # build AOI
    aoi = build_aoi(args.aoi_file)

    # build image collection
    ic = get_s2_img_col(aoi,
                        args.collection,
                        args.start_date,
                        args.end_date,
                        args.cloudy_pixel_percentage)

    # apply s2cloudless
    if args.s2cloudless:
        ic = add_s2cloudless(ic,
                              args.cloud_thresh,
                              args.cloud_buf,
                              args.cloud_proj_dist)

    # compute composite
    comp = compute_composite(ic,
                             args.composite,
                             args.bands,
                             args.quality_bands,
                             args.quality_pct,
                             args.pct)

    # export composite to Google Drive
    export_composite(comp,
                     aoi,
                     args.tif_name,
                     args.crs,
                     args.resolution,
                     args.data_type,
                     args.scale_min,
                     args.scale_max)


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
                        help='Sentinel-2 GEE Collection ID',
                        default='COPERNICUS/S2')
    parser.add_argument('--start_date', type=str,
                        help='Start datetime',
                        default='2020-01-01')
    parser.add_argument('--end_date', type=str,
                        help='End datetime',
                        default='2021-01-01')
    parser.add_argument('--cloudy_pixel_percentage', type=int,
                        help='cloudy pixel percentage metadata to filter scenes by (0-100)',
                        default=60)
    parser.add_argument('--bands', type=str, nargs='+',
                        help='Bands to export',
                        default=['B4', 'B3', 'B2'])
    # ------------------- #
    # s2cloudless options #
    # ------------------- #
    parser.add_argument('--s2cloudless', action='store_true',
                        help='apply s2cloudless cloud mask')
    parser.add_argument('--cloud_thresh', type=int,
                        help='s2cloudless cloud probability threshold (0-100)',
                        default=50)
    parser.add_argument('--cloud_proj_dist', type=float,
                        help='Scaled cloud projection distance',
                        default=1)
    parser.add_argument('--cloud_buf', type=int,
                        help='Amount to dilate cloud pixels in meters',
                        default=50)
    # ----------------- #
    # composite options #
    # ----------------- #
    parser.add_argument('--composite',
                        choices=['mean',
                                 'median',
                                 'max',
                                 'min'
                                 'mosaic',
                                 'quality',
                                 'percentile'],
                        default='mean',
                        help='Select composite operation')
    # ----------------------- #
    # quality composite options 
    # ----------------------- #
    parser.add_argument('--quality_bands', nargs='+', type=str,
                        help='Band(s) to compute quality composite over',
                        default=['B8', 'B4']) # ndvi
    parser.add_argument('--quality_pct', type=int,
                        help='Percentile (0-100) for quality composite',
                        default=100) # full argmax)
    # ------------------ #
    # percentile options #
    # ------------------ #
    parser.add_argument('--pct', type=int,
                        help='Percentile (0-100) for percentile composite',
                        default=25)
    # -------------- #
    # export options #
    # -------------- #
    parser.add_argument('--crs', type=str,
                        help='CRS to export file',
                        default='EPSG:3857')
    parser.add_argument('--resolution', type=float,
                        help='Resolution to export GeoTIFF in meters',
                        default=10.0)
    parser.add_argument('--data_type', 
                        choices=['raw',
                                 'byte', # 0-255
                                 'float'], # 0-1`
                        help='Data type to export GeoTIFF',
                        default='raw')
    parser.add_argument('--scale_min', type=float,
                        help='Minimum value for scaling (raw)',
                        default=0)
    parser.add_argument('--scale_max', type=float,
                        help='Maximum value for scaling (raw)',
                        default=3000)

    args = parser.parse_args()
    
    run(args)


if __name__ == "__main__":
    main()
