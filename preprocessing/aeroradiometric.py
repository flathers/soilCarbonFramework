"""

Produce extract rasters for aeroradiometric data

"""

import arcpy
from arcpy import env
from arcpy.sa import *

import glob

class LicenseError(Exception):
    pass


def extract(workspace, in_raster, mask, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/extract-by-mask.htm

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    coordinate_system = arcpy.SpatialReference("NAD 1983 Contiguous USA Albers")

    # Execute ExtractByMask
    outExtractByMask = ExtractByMask(in_raster, mask)

    arcpy.ProjectRaster_management(outExtractByMask, out_raster,
        coordinate_system, '', '', '', '', '')



if __name__ == "__main__":
    try:
        # Grab a license for spatial analyst
        print 'Checking out ArcGIS Spatial Analyst extension license'
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            print 'CheckOutExtension complete'
        else:
            raise LicenseError

        # Initialize path and file names
        base_input_path = 'F:/soilCarbon/extractedData/aeroradiometric/'
        base_output_path = 'F:/soilCarbon/inputData/aeroradiometric/'
        mask = 'F:/soilCarbon/extractedData/boundaries/envelope/envelope.shp'
        k_raster = 'NAMrad_K'
        th_raster = 'NAMrad_Th'
        u_raster = 'NAMrad_U'

        # Extract K
        print 'Extracting by mask (K)'
        extract(base_input_path, k_raster + '/' + k_raster + '.flt',
            mask, base_output_path + k_raster)

        # Extract Th
        print 'Extracting by mask (Th)'
        extract(base_input_path, th_raster + '/' + th_raster + '.flt',
            mask, base_output_path + th_raster)

        # Extract U
        print 'Extracting by mask (U)'
        extract(base_input_path, u_raster + '/' + u_raster + '.flt',
            mask, base_output_path + u_raster)

    except LicenseError:
        print 'ArcGIS extension license unavailable'
    except Exception as e:
        print e
    finally:
        # Check the Spatial Analyst Extension license in
        print 'Checking in ArcGIS Spatial Analyst extension license'
        status = arcpy.CheckInExtension("Spatial")
        print 'CheckInExtension complete: ' + status
