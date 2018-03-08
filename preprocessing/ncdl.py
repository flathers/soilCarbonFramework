"""

Mosaic and extract the land cover data

"""

import arcpy
from arcpy import env
from arcpy.sa import *

import os

class LicenseError(Exception):
    pass


def mosaic(workspace, in_rasters, out_location, out_raster):
    # Description: Mosaics rasters together, ignoring background/nodata cells

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    coordinate_system = arcpy.SpatialReference("NAD 1983 Contiguous USA Albers")
    data_type = '8_BIT_UNSIGNED'
    cell_size = '30'
    bands = '1'
    pyramids = 'PYRAMIDS -1 NEAREST JPEG'
    mosaic_type = 'FIRST'
    colormap = 'FIRST'
    background = 0

    # CreateRasterDataset_management (out_path, out_name, {cellsize},
    # pixel_type, {raster_spatial_reference}, number_of_bands, {config_keyword},
    # {pyramids}, {tile_size}, {compression}, {pyramid_origin})
    arcpy.CreateRasterDataset_management(out_location, out_raster, cell_size,
        data_type, coordinate_system, bands, '',
        pyramids, '', '', '')

    #Mosaic_management (inputs, target, {mosaic_type},
    # {colormap}, {background_value}, {nodata_value},
    # {onebit_to_eightbit}, {mosaicking_tolerance}, {MatchingMethod})
    arcpy.Mosaic_management(in_rasters, out_location + out_raster, mosaic_type,
        colormap, background, background,
        '', '', '')


def extract(workspace, in_raster, mask, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/extract-by-mask.htm

    # Set environment settings
    env.workspace = workspace

    # Execute ExtractByMask
    outExtractByMask = ExtractByMask(in_raster, mask)

    # Save the output
    outExtractByMask.save(out_raster)
    arcpy.BuildPyramids_management(out_raster)


def get_input_rasters(base_path):
    joined = []

    for root, dirs, files in os.walk(base_path):
        for f in files:
            fileName, fileExtension = os.path.splitext(f)
            if fileExtension == '.tif' and '2015' in fileName:
                raster_path = root + '/' + f
                raster_path = raster_path.replace('\\', '/')
                raster_path = raster_path.replace(base_path, '')
                #print raster_path
                joined.append(raster_path)
    in_rasters = ';'.join(joined)
    return in_rasters


if __name__ == "__main__":
    try:
        # Grab a license for spatial analyst--we'll need it for just about
        # everything we do here
        print 'Checking out ArcGIS Spatial Analyst extension license'
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            print 'CheckOutExtension complete'
        else:
            raise LicenseError

        # Initialize path and file names
        base_input_path = 'F:/soilCarbon/extractedData/landCover/'
        base_output_path = 'F:/soilCarbon/inputData/landCover/'
        mask = 'F:/soilCarbon/extractedData/boundaries/envelope/envelope.shp'
        mosaic_raster = 'ncdlMosaic.tif'
        ncdl_raster = 'ncdl.tif'

        in_rasters = get_input_rasters(base_input_path)

        # Build mosaic
        print 'Building NCDL mosaic'
        mosaic(base_input_path, in_rasters, base_output_path, mosaic_raster)

        # Extract
        print 'Extracting by mask'
        extract(base_output_path, mosaic_raster, mask, ncdl_raster)

    except LicenseError:
        print 'ArcGIS extension license unavailable'
    except Exception as e:
        print e
    finally:
        # Check the Spatial Analyst Extension license in
        print 'Checking in ArcGIS Spatial Analyst extension license'
        status = arcpy.CheckInExtension("Spatial")
        print 'CheckInExtension complete: ' + status
