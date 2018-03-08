"""

Compute mean annual temperature

"""

import arcpy
from arcpy import env
from arcpy.sa import *

import os

class LicenseError(Exception):
    pass


def calculate_mean(workspace, in_rasters, out_raster):
    # after http://pro.arcgis.com/en/pro-app/help/analysis/spatial-analyst/mapalgebra/building-complex-statements.htm
    # Description: Mosaics rasters together, ignoring background/nodata cells

    # Requirements: Spatial Analyst Extension

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    coordinate_system = arcpy.SpatialReference("NAD 1983 Contiguous USA Albers")

    mat = Raster(in_rasters.pop())
    for in_raster in in_rasters:
        mat = mat + Raster(in_raster)
    mat = mat / 10

    arcpy.ProjectRaster_management(mat, out_raster,
        coordinate_system, '', '', '', '', '')    
    
    #mat.save(out_raster)


def get_input_rasters(base_path):
    joined = []

    for root, dirs, files in os.walk(base_path):
        for f in files:
            fileName, fileExtension = os.path.splitext(f)
            if fileExtension == '.tif' and 'tmean' in fileName:
                raster_path = root + '/' + f
                raster_path = raster_path.replace('\\', '/')
                #print raster_path
                joined.append(raster_path)
    return joined


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
        base_input_path = 'F:/soilCarbon/extractedData/temperature/'
        base_output_path = 'F:/soilCarbon/inputData/temperature/'

        in_rasters = get_input_rasters(base_input_path)
        mean_raster = 'matalb.tif'

        # Build mosaic
        print 'Computing mean'
        calculate_mean(base_input_path, in_rasters, base_output_path + mean_raster)

    except LicenseError:
        print 'ArcGIS extension license unavailable'
    except Exception as e:
        print e
    finally:
        # Check the Spatial Analyst Extension license in
        print 'Checking in ArcGIS Spatial Analyst extension license'
        status = arcpy.CheckInExtension("Spatial")
        print 'CheckInExtension complete: ' + status
