"""

Gather all the covariates and create a spatial grid

"""

import arcpy
import os

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
        env.workspace = "F:/soilCarbon/scratch"

        # Set local variables
        in_rasters = ['F:/soilCarbon/inputData/elevation/nedf.tif',
            'F:/soilCarbon/inputData/elevation/twif',
            'F:/soilCarbon/inputData/elevation/slope',
            'F:/soilCarbon/inputData/aeroradiometric/namrad_k',
            'F:/soilCarbon/inputData/aeroradiometric/namrad_th',
            'F:/soilCarbon/inputData/aeroradiometric/namrad_u',
            'F:/soilCarbon/inputData/landCover/ncdl.tif',
            'F:/soilCarbon/inputData/precipitation/mapalb.tif',
            'F:/soilCarbon/inputData/temperature/matalb.tif']
        sample_method = "NEAREST"

        # Set local variables
        out_folder_path = "F:/soilCarbon/inputData/grid/"
        out_fgdb_name = "fgdb.gdb"
        center_points = out_folder_path + out_fgdb_name + '/centers'
        center_points = 'F:/soilCarbon/scratch/fgdb.gdb/' + '/centers' #fixme: remove
        out_table = out_folder_path + out_fgdb_name + '/outTable'

        if not os.path.exists(out_folder_path):
            os.makedirs(out_folder_path)

        print 'starting makeGrid'
        print str(datetime.now())
        Sample(in_rasters, center_points, out_table, sample_method)
        print str(datetime.now())
        print 'finished makeGrid'

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
