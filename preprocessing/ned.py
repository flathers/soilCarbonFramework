"""

Get an extracted mosaic of the elevation data

"""

import arcpy
from arcpy import env
from arcpy.sa import *

import glob

class LicenseError(Exception):
    pass


def mosaic(workspace, out_location, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/data-management-toolbox/mosaic-to-new-raster.htm
    # Description: Mosaics rasters together

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    in_rasters = ';'.join(glob.glob(workspace + '*.tif'))
    coordinate_system = arcpy.SpatialReference("NAD 1983 Contiguous USA Albers")
    data_type = '32_BIT_SIGNED'
    cell_size = '30'
    bands = '1'

    # Execute MosaicToNewRaster
    arcpy.MosaicToNewRaster_management(in_rasters, out_location, out_raster,
        coordinate_system, data_type, cell_size, bands)


def extract(workspace, in_raster, mask, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/extract-by-mask.htm

    # Set environment settings
    env.workspace = workspace

    # Execute ExtractByMask
    outExtractByMask = ExtractByMask(in_raster, mask)

    # Save the output
    outExtractByMask.save(out_raster)
    arcpy.BuildPyramids_management(out_raster)


def fill_sinks(workspace, in_raster, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/fill.htm

    # Set environment settings
    env.workspace = workspace

    # Execute ExtractByMask
    outFill = Fill(in_raster)

    # Save the output
    outFill.save(out_raster)
    arcpy.BuildPyramids_management(out_raster)


def flow_direction(workspace, in_raster, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/flow-direction.htm
    # Description: Creates a raster of flow direction from each cell to its
    #    steepest downslope neighbor.
    # Requirements: Spatial Analyst Extension

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    inSurfaceRaster = in_raster

    # Execute FlowDirection
    outFlowDirection = FlowDirection(inSurfaceRaster, "NORMAL")

    # Save the output
    outFlowDirection.save(out_raster)
    arcpy.BuildPyramids_management(out_raster)


def flow_accumulation(workspace, in_raster, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/flow-accumulation.htm
    # Description: Creates a raster of accumulated flow to each cell.
    # Requirements: Spatial Analyst Extension

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    inFlowDirRaster = in_raster
    inWeightRaster = ''
    dataType = 'INTEGER'

    # Execute FlowDirection
    outFlowAccumulation = FlowAccumulation(inFlowDirRaster, inWeightRaster, dataType)

    # Save the output
    outFlowAccumulation.save(out_raster)
    arcpy.BuildPyramids_management(out_raster)


def slope(workspace, in_raster, out_raster):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/slope.htm
    # Description: Identifies the rate of maximum change
    #              in z-value from each cell.
    # Requirements: Spatial Analyst Extension

    # Set environment settings
    env.workspace = workspace

    # Set local variables
    inRaster = in_raster
    outMeasurement = 'DEGREE'

    # Execute Slope
    slopeDeg = Slope(inRaster, outMeasurement)

    slopeRad = Times(slopeDeg, math.pi / 180)

    # Save the output
    slopeRad.save(out_raster)
    arcpy.BuildPyramids_management(out_raster)


def topographic_wetness_index(workspace, flow_accumulation_raster, slope_raster, out_raster):
    # Description: Computes topographic wetness index using flow accumulation
    #              and slope after Quin et al. 1991 (note that we assume 30m
    #              cell size, so cell_size_squared = 30^2 = 900)
    #
    # Quinn, P. F. B. J., et al.
    # "The prediction of hillslope flow paths for distributed hydrological
    # modelling using digital terrain models."
    # Hydrological processes 5.1 (1991): 59-79.
    # DOI: 10.1002/hyp.3360050106
    #
    # Requirements: Spatial Analyst Extension

    # Set environment settings
    env.workspace = workspace

    # Execute math processors
    # Note that each one of these creates a raster file in the workspace,
    # but we only save the last one.
    cell_size_squared = 900
    tan_slope_raster = Tan(slope_raster)
    squared_flow_accumulation_raster = Times(flow_accumulation_raster, cell_size_squared)
    quotient = Divide(squared_flow_accumulation_raster, tan_slope_raster)
    twi = Ln(quotient)

    # We need to normalize the twi values: (twi - twi_min) / (twi_max - twi_min)
    twi_min_result = arcpy.GetRasterProperties_management(twi, "MINIMUM")
    twi_max_result = arcpy.GetRasterProperties_management(twi, "MAXIMUM")
    twi_min = float(twi_min_result.getOutput(0))
    twi_max = float(twi_max_result.getOutput(0))
    twi_top = Minus(twi, twi_min)
    twi_bottom = twi_max - twi_min
    twi_norm = Divide(twi_top, twi_bottom)

    # Save the output
    twi_norm.save(out_raster)
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
        base_input_path = 'F:/soilCarbon/extractedData/elevation/'
        base_output_path = 'F:/soilCarbon/inputData/elevation/'
        mask = 'F:/soilCarbon/extractedData/boundaries/envelope/envelope.shp'
        mosaic_raster = 'nedMosaic.tif'
        ned_raster = 'ned.tif'
        filled_raster = 'nedf'
        slope_raster = 'slope'
        flow_direction_raster = 'flowdir'
        flow_accumulation_raster = 'flowacc'
        topographic_wetness_index_raster = 'twi'

        # Build mosaic
        print 'Building NED mosaic'
        mosaic(base_input_path, base_output_path, mosaic_raster)

        # Extract
        print 'Extracting by mask'
        extract(base_output_path, mosaic_raster, mask, ned_raster)

        # Extract
        print 'Filling sinks'
        fill_sinks(base_output_path, ned_raster, filled_raster)

        # Compute derived rasters: slope, flow direction and accumulation, twi
        print 'Computing slope raster'
        slope(base_output_path,
            filled_raster,
            base_output_path + slope_raster)

        print 'Computing flow direction raster'
        flow_direction(base_output_path,
            filled_raster,
            base_output_path + flow_direction_raster)

        print 'Computing flow accumulation raster'
        flow_accumulation(base_output_path,
            flow_direction_raster,
            base_output_path + flow_accumulation_raster)

        print 'Computing topographic wetness index raster'
        topographic_wetness_index(base_output_path,
            flow_accumulation_raster,
            slope_raster,
            base_output_path + topographic_wetness_index_raster)

    except LicenseError:
        print 'ArcGIS extension license unavailable'
    except Exception as e:
        print e
    finally:
        # Check the Spatial Analyst Extension license in
        print 'Checking in ArcGIS Spatial Analyst extension license'
        status = arcpy.CheckInExtension("Spatial")
        print 'CheckInExtension complete: ' + status
