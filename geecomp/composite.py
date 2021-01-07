'''
composite.py

Functions for making composites from image collections
'''


import ee
import geemap


def compute_quality_composite(ic, bands, quality_bands, quality_pct):
    if len(quality_bands) > 1: # take a normalized difference
        def add_quality(i):
            quality = i.normalizedDifference(quality_bands).rename('quality')
            return i.addBands(quality)

        ic = ic.map(add_quality)

        if quality_pct == 100:
            comp = ic.qualityMosaic('quality')
        else:
            qpct = ic.select('quality').reduce(ee.Reducer.percentile([quality_pct]))

            def pct_quality(i):
                return i.addBands(i.select('quality').subtract(qpct).abs().multiply(-1).rename('quality_pct'))

            qpct_added = ic.map(pct_quality)
            comp = qpct_added.qualityMosaic('quality_pct')
    else: # just use the band directly
        quality_band = quality_bands[0]
        if quality_pct == 100:
            comp = ic.qualityMosiac(quality_band)
        else:
            qpct = ic.select(quality_band).reduce(ee.Reducer.percentile([quality_pct]))

            def pct_quality(i):
                return i.addBands(i.select('quality').subtract(qpct).abs().multiply(-1).rename('quality_pct'))

            qpct_added = ic.map(pct_quality)
            comp = qpct_added.qualityMosiac('quality_pct')

    return comp.select(bands)


def compute_percentile_composite(ic, bands, pct):
    comp = ic.reduce(ee.Reducer.percentile([pct]))
    bands_pct = [b+'_p{}'.format(pct) for b in bands]
    comp = comp.select(bands_pct).rename(bands)

    return comp


def compute_composite(ic, composite, bands, quality_bands, quality_pct, pct):
    if composite == 'mean':
        comp = ic.mean().select(bands)
    elif composite == 'median':
        comp = ic.median().select(bands)
    elif composite == 'max':
        comp = ic.max().select(bands)
    elif composite == 'min':
        comp = ic.min().select(bands)
    elif composite == 'mosaic':
        comp = ic.mosaic().select(bands)
    elif composite == 'quality':
        comp = compute_quality_composite(ic, bands, quality_bands, quality_pct)
    elif composite == 'percentile':
        comp = compute_percentile_composite(ic, bands, pct)

    return comp


def export_composite(comp, aoi, tif_name, crs, resolution, data_type, scale_min, scale_max):
    if data_type == 'byte':
        comp_out = comp.float().subtract(scale_min).divide(scale_max - scale_min).multiply(255).byte()
    elif data_type == 'float':
        comp_out = comp.float().subtract(scale_min).divide(scale_max - scale_min)
    elif data_type == 'raw':
        comp_out = comp

    geemap.ee_export_image_to_drive(ee_object=comp_out,
                                    description=tif_name,
                                    folder='GEE Composite',
                                    region=aoi,
                                    scale=resolution,
                                    crs=crs)
