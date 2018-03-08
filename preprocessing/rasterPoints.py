"""

Use the NED raster to find centerpoints for all raster cells

"""

import arcpy
from arcpy import env
from arcpy.sa import *
from datetime import datetime

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

        # Set environment settings
        env.workspace = "F:/soilCarbon/inputData/grid/"

        # Set local variables
        ned_raster = 'F:/soilCarbon/inputData/elevation/ned.tif'

        # Set local variables
        out_folder_path = "F:/soilCarbon/inputData/grid/"
        out_fgdb_name = "fgdb.gdb"
        center_points = out_folder_path + out_fgdb_name + '/centers'

        arcpy.CreateFileGDB_management(out_folder_path, out_fgdb_name)

        print 'starting RasterToPoint_conversion'
        arcpy.RasterToPoint_conversion(ned_raster, center_points, 'VALUE')
        print 'finished RasterToPoint_conversion'

    except LicenseError:
        print 'ArcGIS extension license unavailable'
    except Exception as e:
        print e
    finally:
        # Check the Spatial Analyst Extension license in
        print 'Checking in ArcGIS Spatial Analyst extension license'
        status = arcpy.CheckInExtension("Spatial")
        print 'CheckInExtension complete: ' + status
        print 'Done'
