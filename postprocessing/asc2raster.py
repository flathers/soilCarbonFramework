"""

Compute mean annual precipitation

"""

import arcpy
from arcpy import env
from arcpy.sa import *

import os

class LicenseError(Exception):
    pass


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

        coordinate_system = arcpy.SpatialReference("NAD 1983 Contiguous USA Albers")

        # Initialize path and file names
        in_asc = 'F:/soilCarbon/outputData/msoc.asc'
        out_raster = 'F:/soilCarbon/outputData/rasters/msoc'

        # create mean raster
        print 'Computing mean'
        arcpy.ASCIIToRaster_conversion(in_asc, out_raster, 'FLOAT')
        arcpy.DefineProjection_management(out_raster, coordinate_system)

        # create variance raster
        in_asc = 'F:/soilCarbon/outputData/vsoc.asc'
        out_raster = 'F:/soilCarbon/outputData/rasters/vsoc'
        print 'Computing variance'
        arcpy.ASCIIToRaster_conversion(in_asc, out_raster, 'FLOAT')
        arcpy.DefineProjection_management(out_raster, coordinate_system)

    except LicenseError:
        print 'ArcGIS extension license unavailable'
    except Exception as e:
        print e
    finally:
        # Check the Spatial Analyst Extension license in
        print 'Checking in ArcGIS Spatial Analyst extension license'
        status = arcpy.CheckInExtension("Spatial")
        print 'CheckInExtension complete: ' + status
