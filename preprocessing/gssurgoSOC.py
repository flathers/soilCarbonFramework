"""

Get the gssurgo carbon values for the area of interest

"""

import arcpy
from arcpy import env
from arcpy.sa import *

class LicenseError(Exception):
    pass


def mosaic(workspace, in_rasters, out_location, out_raster):
    # Description: Mosaics rasters together, ignoring background/nodata cells

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    coordinate_system = arcpy.SpatialReference("NAD 1983 Contiguous USA Albers")
    data_type = '32_BIT_SIGNED'
    cell_size = '10'
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
        '', background, background,
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


def build_attribute_table(workspace, in_raster):

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    field_name = 'mukey'
    expression = 'str(!VALUE!)'
    exp_type = 'PYTHON_9.3'

    arcpy.BuildRasterAttributeTable_management(in_raster)
    arcpy.AddField_management(in_raster, 'mukey', 'text', field_length=30)
    arcpy.CalculateField_management(in_raster, field_name, expression, exp_type)


def get_soc0_999(workspace, in_raster, value_table, out_raster):
    # Set environment settings
    env.workspace = workspace

    # Set local variables
    field_name = 'mukey'
    lookup_field = 'soc0_999'

    arcpy.JoinField_management (in_raster, field_name, value_table, field_name, lookup_field)
    #arcpy.AddJoin_management(in_raster, field_name, value_table, field_name)
    outraster = Lookup(in_raster, lookup_field)
    arcpy.CalculateStatistics_management(outraster)
    outraster.save(out_raster)
    arcpy.BuildPyramids_management(out_raster)


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
        base_input_path = 'F:/soilCarbon/extractedData/soils/'
        base_output_path = 'F:/soilCarbon/inputData/soils/'
        mask = 'F:/soilCarbon/extractedData/boundaries/envelope/envelope.shp'
        mosaic_raster = 'soilMosaic'
        clipped_raster = 'soilmu'
        soc_raster = 'ssurgo_c'
        value_table = base_input_path + 'valu_fy2016.gdb/valu1'
        in_rasters = ['F:/soilCarbon/extractedData/soils/gssurgo_g_id/gSSURGO_ID.gdb/MapunitRaster_id_10m',
                    'F:/soilCarbon/extractedData/soils/gssurgo_g_mt/gSSURGO_MT.gdb/MapunitRaster_mt_10m',
                    'F:/soilCarbon/extractedData/soils/gssurgo_g_or/gSSURGO_OR.gdb/MapunitRaster_or_10m',
                    'F:/soilCarbon/extractedData/soils/gssurgo_g_wa/gSSURGO_WA.gdb/MapunitRaster_wa_10m']

        mosaic(base_output_path, in_rasters, base_output_path, mosaic_raster)
        extract(base_output_path, mosaic_raster, mask, clipped_raster)
        build_attribute_table(base_output_path, clipped_raster)
        get_soc0_999(base_output_path, clipped_raster, value_table, soc_raster)

    except LicenseError:
        print 'ArcGIS extension license unavailable'
    except Exception as e:
        print e
    finally:
        # Check the Spatial Analyst Extension license in
        print 'Checking in ArcGIS Spatial Analyst extension license'
        status = arcpy.CheckInExtension("Spatial")
        print 'CheckInExtension complete: ' + status
