"""

Use the envelope to extract polygons from other boundaries files

"""

import arcpy
from arcpy import env
from arcpy.sa import *

import csv
import os
import shutil


def check_create_dir(path):
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)


def extract_by_mask(workspace, source_fc, mask_fc, out_fc):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/slope.htm
    # Description: Identifies the rate of maximum change
    #              in z-value from each cell.

    # Set environment settings
    env.workspace = workspace

    arcpy.MakeFeatureLayer_management(source_fc, 'source_lyr')
    arcpy.SelectLayerByLocation_management ('source_lyr', 'intersect', mask_fc)
    arcpy.CopyFeatures_management('source_lyr', out_fc)
    arcpy.Delete_management('source_lyr')


if __name__ == "__main__":
    try:
        # Initialize path and file names
        base_input_path = 'F:/soilCarbon/extractedData/boundaries/'
        base_output_path = 'F:/soilCarbon/inputData/boundaries/'

        mask = base_input_path + 'envelope/envelope.shp'
        counties_in = base_input_path + 'counties/tl_2012_us_county.shp'
        counties_out = base_output_path + 'counties/counties'
        states_in = base_input_path + 'states/statesp020.shp'
        states_out = base_output_path + 'states/states'

        # Process the boundaries files
        check_create_dir(counties_out)
        extract_by_mask(base_input_path,
            counties_in,
            mask,
            counties_out)

        check_create_dir(states_out)
        extract_by_mask(base_input_path,
            states_in,
            mask,
            states_out)
        # states comes with no projection information,
        # but it's in the same projection as counties
        shutil.copyfile(counties_out + '.prj', states_out + '.prj')

        shutil.copytree(base_input_path + 'envelope',
            base_output_path + 'envelope')

        shutil.copytree(base_input_path + 'studyArea',
            base_output_path + 'studyArea')

    except Exception as e:
        print e
    finally:
        print 'Done'
