import ee


def get_s2_img_col(aoi, 
                   collection_name,
                   start_date, 
                   end_date,
                   cloudy_pixel_percentage):
    # Import and filter S2
    s2_col = (ee.ImageCollection(collection_name)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloudy_pixel_percentage)))

    # Import and filter s2cloudless.
    s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        .filterBounds(aoi)
        .filterDate(start_date, end_date))

    # Join the filtered s2cloudless collection to the S2 collection by the 'system:index' property.
    return ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2_col,
        'secondary': s2_cloudless_col,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    }))


def apply_cloud_shadow_mask(img):
    # Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
    not_cld_shdw = img.select('cloudmask').Not()

    # Subset reflectance bands and update their masks, return the result.
    return img.select('B.*').updateMask(not_cld_shdw)


def add_s2cloudless(ic, cloud_thresh, cloud_buf, cloud_proj_dist):
    def add_cloud_bands(img):
        # Get s2cloudless image, subset the probability band.
        cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

        # Condition s2cloudless by the probability threshold value.
        is_cloud = cld_prb.gt(cloud_thresh).rename('clouds')

        # Add the cloud probability layer and cloud mask as image bands.
        return img.addBands(ee.Image([cld_prb, is_cloud]))

    
    def add_shadow_bands(img):
        # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
        shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')));

        # Project shadows from clouds for the distance specified by the cloud projection distance
        shadows = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, cloud_proj_dist*10)
            .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
            .select('distance')
            .mask()
            .rename('shadows'))

        # Add dark pixels, cloud projection, and identified shadows as image bands.
        return img.addBands(ee.Image([shadows]))


    def add_cloud_shadow_mask(img):
        # Add cloud component bands.
        img_cloud = add_cloud_bands(img)

        # Add cloud shadow component bands.
        img_cloud_shadow = add_shadow_bands(img_cloud)

        # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
        is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)

        # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
        # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
        is_cld_shdw = (is_cld_shdw.focal_min(2).focal_max(cloud_buf*2/20)
            .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
            .rename('cloudmask'))

        # Add the final cloud-shadow mask to the image.
        return img.addBands(is_cld_shdw)

    ic = ic.map(add_cloud_shadow_mask)
    ic = ic.map(apply_cloud_shadow_mask)
    return ic


