"""

Use the NCSS sample data to generate a .csv file with soil carbon samples

"""

import arcpy
from arcpy import env
from arcpy.sa import *

import csv
import os
import shutil
import string
import sys

class LicenseError(Exception):
    pass


def get_list(csv_file):
    csv_list = []
    with open(csv_file, 'rb') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = \
            [field.replace('% ', '') for field in reader.fieldnames]
        for row in reader:
            csv_list.append(row)
    return(csv_list)


def get_dd(d, m, s):
    if (not d.isdigit()):
        return(0)
    m = m or 0
    s = s or 0
    m = float(m) + float(s) / 60.0
    d = float(d) + m / 60.0
    return(d)


def reduce_sites(sites):
    reduced_sites = []
    for row in sites:
        if (row.get('latitude_decimal_degrees')):
            row['latitude_dd'] = row['latitude_decimal_degrees']
        elif (row.get('latitude_degrees')):
            row['latitude_dd'] = get_dd(row['latitude_degrees'],
                row['latitude_minutes'],
                row['latitude_seconds'])
        if (row.get('longitude_decimal_degrees')):
            row['longitude_dd'] = row['longitude_decimal_degrees']
        elif (row.get('longitude_degrees')):
            row['longitude_dd'] = get_dd(row['longitude_degrees'],
                row['longitude_minutes'],
                row['longitude_seconds'])
        if(row.get('latitude_dd') and row.get('longitude_dd')):
            row = {
                'siteId': row['user_site_id'],
                'lat': abs(float(row['latitude_dd'])),
                'long': -1*abs(float(row['longitude_dd']))}
            reduced_sites.append(row)
    return(reduced_sites)


def reduce_pedons(pedons):
    reduced_pedons = []
    for row in pedons:
        row = {
            'siteId': row['user_site_id'],
            #'sampled_taxon_name': '"' + row['sampled_taxon_name'] + '"',
            'pedonKey': row['pedon_key']}
        reduced_pedons.append(row)
    return(reduced_pedons)


def reduce_carbon(carbon):
    # To get the list of organic carbon column names, grep the downloaded
    # Carbon_and_Extractions.csv files:
    # grep -Prohi --exclude=Carbon_and_Extractions_dict.csv '"\KOC_[^"]*'|sed 's/% //g'|sort|uniq
    #
    # OC_6A1a_Sjj_wt_0_CMS_0_0
    # OC_6A1c_Gaj_wt_119_CMS_0_0
    # OC_6A1c_Hjj_wt_119_CMS_0_0
    # OC_6A1c_Njj_wt_119_CMS_0_0
    # OC_6A1c_Sjj_wt_0_CMS_0_0
    # OC_6A1c_Sjj_wt_119_CMS_0_0
    # OC_NK_Sjj_wt_0_CMS_0_0
    # oc_WBC1_Sjj_wt_0_University of Idaho_0_0

    reduced_carbon = []
    for row in carbon:
        c = row.get('OC_6A1a_Sjj_wt_0_CMS_0_0') or \
            row.get('OC_6A1c_Gaj_wt_119_CMS_0_0') or \
            row.get('OC_6A1c_Hjj_wt_119_CMS_0_0') or \
            row.get('OC_6A1c_Njj_wt_119_CMS_0_0') or \
            row.get('OC_6A1c_Sjj_wt_0_CMS_0_0') or \
            row.get('OC_6A1c_Sjj_wt_119_CMS_0_0') or \
            row.get('OC_NK_Sjj_wt_0_CMS_0_0') or \
            row.get('oc_WBC1_Sjj_wt_0_University of Idaho_0_0')

        row = {
            'pedonKey': row['pedon_key'],
            'layerKey': row['layer_key'],
            'hznTop': row['hzn_top'],
            'hznBot': row['hzn_bot'],
            'carbon': c}
        if (row['carbon']):
            reduced_carbon.append(row)
    return(reduced_carbon)


def reduce_density(density):
    # To get the list of density column names, grep the downloaded
    # Bulk_Density_and_Moisture.csv files:
    # grep -Prohi --exclude=Bulk_Density_and_Moisture_dict.csv '"\KDb[^"]*'|sed 's/% //g'|sort|uniq
    #
    # DbOD_3B1c_Caj_0_SSL_0_0
    # DbOD_4A1h_Caa_g/cc_0_CMS_0_0
    # DbOD_4A1h_Caj_g/cc_0_CMS_0_0
    # DbOD_DbWR1_Caj_g/cc_0_SSL_0_0
    # db_od_unknown_Sjj_g/cc_0_University of Idaho_0_0

    reduced_density = []
    for row in density:
        d = row.get('DbOD_3B1c_Caj_0_SSL_0_0') or \
            row.get('DbOD_4A1h_Caa_g/cc_0_CMS_0_0') or \
            row.get('DbOD_4A1h_Caj_g/cc_0_CMS_0_0') or \
            row.get('DbOD_DbWR1_Caj_g/cc_0_SSL_0_0') or \
            row.get('db_od_unknown_Sjj_g/cc_0_University of Idaho_0_0')

        try:
            d = round(float(d), 2)
        except:
            d = 0

        row = {
            'pedonKey': row['pedon_key'],
            'layerKey': row['layer_key'],
            'density': d}
        if (row['density'] != 0):
            reduced_density.append(row)
    return(reduced_density)


def reduce_rock(rock):
    # To get the list of rock column names, grep the downloaded
    # PSDA_and_Rock_Fragments.csv files:
    # grep -Prohi --exclude=PSDA_and_Rock_Fragments_dict.csv '"\KWpG[^"]*'|sed 's/% //g'|sort|uniq
    #
    # wpG2_d-1_S

    reduced_rock = []
    for row in rock:
        r = row.get('wpG2_d-1_S')

        try:
            r = round(float(r), 2)
        except:
            r = 0

        row = {
            'pedonKey': row['pedon_key'],
            'layerKey': row['layer_key'],
            'rock': r}
        if (row['rock'] <= 100.0):
            reduced_rock.append(row)
    return(reduced_rock)


def join(sites, pedons, carbon, density, rock, state, county):
    joined = []
    for row in carbon:
        pedon = next((item for item in pedons if item['pedonKey'] == row['pedonKey']), None)
        if pedon:
            site = next((item for item in sites if item['siteId'] == pedon['siteId']), None)
        if(pedon and site):
            d = [d_row['density'] for d_row in density if d_row['layerKey'] == row['layerKey']]
            r = [r_row['rock'] for r_row in rock if r_row['layerKey'] == row['layerKey']]
            if d:
                if r:
                    row['density'] = d[0]
                    row['rock'] = r[0]
                    row.update(pedon)
                    row.update(site)
                    row['state'] = state
                    row['county'] = county
                    joined.append(row)
    return(joined)


def get_gcm2(in_list):
    # Compute grams carbon/m^2 for each layer in each pedon, then
    # add them up for a total pedon value.
    #
    # Following Bliss, N. B., S.W. Waltman, and G.W. Petersen. Preparing
    # a soil carbon inventory for the United States using geographic
    # information systems. Soils and global change (1995): 275-295.
    #
    pedons = {}
    for row in in_list:
        pedonKey = row['pedonKey']
        hznTop = float(row['hznTop'])
        hznBot = float(row['hznBot'])
        density = float(row['density'])

        Rrt = float(row['rock']) / 100.0
        Rft = 1 - Rrt
        Db = density
        Dp = 2.65
        thickness = (hznBot - hznTop) / 100
        carbon = float(row['carbon'])


        # gcm2 = 100,000 * ODRT
        # 100,000 = .01 * 1000000
        # O = Soil Organic Carbon (gc/gram soil)
        # D = Bulk Density (g soil/cm^3 fine soil fraction)
        # R = Rock fragment factor
        # T = Thickness of layer (m)
        O = carbon
        D = density
        R = (Rft / Db) / ( (Rft / Db) + (Rrt / Dp) )
        T = thickness
        gcm2 = 10000 * O * D * R * T
        gcm2 = round(gcm2, 2)

        #gC/m^2 = (bulk density g/cm^3) * (%carbon/100) * (1000000 cc/m^3) * (horizon thickness cm/100))
        #       = (bulk density g/cm^3) * %carbon * (horizon thickness cm) * 100
        #gcm2 = density * carbon * thickness * 100
        try:
            pedons[pedonKey] += gcm2
        except KeyError:
            pedons[pedonKey] = gcm2

    return(pedons)


def reduce_joined(in_table, gcm2):
    #Eliminate rows with duplicate pedon keys from the joined sample data
    joined = []

    for row in in_table:
        if (int(row['hznTop']) < 11): #fixme: excluding bad pedons
            if not any(d['pedonKey'] == row['pedonKey'] for d in joined):
                new_row = {}
                new_row['siteId'] = row['siteId']
                new_row['pedonKey'] = row['pedonKey']
                new_row['long'] = row['long']
                new_row['lat'] = row['lat']
                new_row['state'] = row['state']
                new_row['county'] = row['county']

                #new_row['carbon'] = row['carbon']
                #new_row['density'] = row['density']
                #new_row['hznTop'] = row['hznTop']
                #new_row['hznBot'] = row['hznBot']
                #new_row['rock'] = row['rock']

                new_row['gcm2'] = gcm2[row['pedonKey']]


                joined.append(new_row)
    return(joined)


def process_county(base_path, state, county):
    sites_file = base_path + 'site.csv'
    pedons_file = base_path + 'pedon.csv'
    carbon_file = base_path + 'Carbon_and_Extractions.csv'
    density_file = base_path + 'Bulk_Density_and_Moisture.csv'
    rock_file = base_path + 'PSDA_and_Rock_Fragments.csv'

    sites = get_list(sites_file)
    sites = reduce_sites(sites)

    pedons = get_list(pedons_file)
    pedons = reduce_pedons(pedons)

    carbon = get_list(carbon_file)
    carbon = reduce_carbon(carbon)

    density = get_list(density_file)
    density = reduce_density(density)

    rock = get_list(rock_file)
    rock = reduce_rock(rock)

    joined = join(sites, pedons, carbon, density, rock, state, county)
    gcm2 = get_gcm2(joined)
    joined = reduce_joined(joined, gcm2)

    return(joined)


def make_csv(base_path, output_path):
    joined = []
    for root, dirs, files in os.walk(base_path):
        if not dirs and not os.path.split(root)[1]=='shpTemplate':
            county = os.path.split(root)[1]
            state = os.path.split(os.path.split(root)[0])[1]
            print state, county
            county_path = base_path + state + '/' + county + '/'
            joined.extend(process_county(county_path, state, county))

    fields = ['siteId', 'pedonKey', 'long', 'lat', 'state', 'county', 'gcm2']
    #fields = ['siteId', 'pedonKey', 'long', 'lat', 'state', 'county', 'carbon', 'density', 'hznTop', 'hznBot', 'rock', 'gcm2']

    with open(output_path, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, fields)
        dict_writer.writeheader()
        dict_writer.writerows(joined)


def create_shapefile(template_path, template_file, output_file, output_path, shp_output):

    # Set workspace
    env.workspace = output_path

    # Set local variables
    shp_file = output_path + 'template.shp'
    csv_file = output_path + output_file

    # Copy the shapefile template
    src_files = os.listdir(template_path)
    for file_name in src_files:
        full_file_name = os.path.join(template_path, file_name)
        if (os.path.isfile(full_file_name)):
            shutil.copy(full_file_name, output_path)

    # after https://gist.github.com/perrygeo/7220600
    cursor = arcpy.InsertCursor(shp_file)
    with open(csv_file, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create the feature
            feature = cursor.newRow()

            # Eliminate samples outside the area of interest
            if float(row['long']) > -122.0 and \
                float(row['long']) < -115.5 and \
                float(row['lat']) > 44.0 and \
                float(row['lat']) < 49.0:

                # Add the point geometry to the feature
                vertex = arcpy.CreateObject("Point")
                vertex.X = row['long']
                vertex.Y = row['lat']
                feature.shape = vertex

                # Add attributes
                feature.siteId = row['siteId']
                feature.pedonKey = row['pedonKey']
                feature.state = row['state']
                feature.county = row['county']
                feature.gcm2 = row['gcm2']

                # write to shapefile
                cursor.insertRow(feature)
    # clean up
    del cursor

    # project from WGS84 to Albers
    coordinate_system = arcpy.SpatialReference('NAD 1983 Contiguous USA Albers')
    arcpy.Project_management(shp_file, shp_output, coordinate_system)


def add_covariates(workspace, shapefile, in_rasters):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/spatial-analyst-toolbox/extract-multi-values-to-points.htm

    env.workspace = workspace

    # Set local variables
    inPointFeatures = shapefile
    inRasterList = in_rasters

    # Execute ExtractValuesToPoints
    ExtractMultiValuesToPoints(inPointFeatures, inRasterList)


def get_complete_cases(workspace, in_shapefile, out_shapefile, csv_file):
    # after http://desktop.arcgis.com/en/arcmap/10.4/tools/data-management-toolbox/delete-features.htm

    # Set environment settings
    arcpy.env.workspace = workspace

    # Set local variables
    inFeatures = in_shapefile
    outFeatures = out_shapefile
    tempLayer = "tempLayer"
    expression = arcpy.AddFieldDelimiters(tempLayer, "namrad_th") + " < 0"
    csv_delimeter = 'COMMA'

    # Execute CopyFeatures to make a new copy of the feature class
    arcpy.CopyFeatures_management(inFeatures, outFeatures)

    # Execute MakeFeatureLayer
    arcpy.MakeFeatureLayer_management(outFeatures, tempLayer)

    # Execute SelectLayerByAttribute to determine which features to delete
    arcpy.SelectLayerByAttribute_management(tempLayer, "NEW_SELECTION",
                                            expression)

    # Execute GetCount and if some features have been selected, then
    #  execute DeleteFeatures to remove the selected features.
    if int(arcpy.GetCount_management(tempLayer).getOutput(0)) > 0:
        arcpy.DeleteFeatures_management(tempLayer)

    #os.remove(workspace + csv_file)
    csv_out = workspace + csv_file

    #Get field names
    fields = [x.name for x in arcpy.ListFields(outFeatures)]

    with open(csv_out, "wb") as f:
        wr = csv.writer(f)
        wr.writerow(fields)
        with arcpy.da.SearchCursor(outFeatures, fields) as cursor:
            for row in cursor:
                long_meters = int(round(row[1][0]))
                lat_meters = int(round(row[1][1]))
                new_row = list(row)
                new_row[4] = long_meters
                new_row[5] = lat_meters
                wr.writerow(new_row)



if __name__ == "__main__":
    base_path = 'F:/soilCarbon/extractedData/ncss/'
    output_path = 'F:/soilCarbon/inputData/ncss/'
    output_file = 'samples.csv'
    template_path = 'F:/soilCarbon/extractedData/ncss/shpTemplate/'
    template_file = 'template.shp'
    temp_shp_file = 'tsamples.shp'
    shp_output = 'F:/soilCarbon/inputData/ncss/' + temp_shp_file
    shp_file = 'samples.shp'

    make_csv(base_path, output_path + output_file)
    #sys.exit() #fixme
    create_shapefile(template_path, template_file, output_file, output_path, shp_output)

    try:
        print 'Checking out ArcGIS Spatial Analyst extension license'
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            print 'CheckOutExtension complete'
        else:
            raise LicenseError

        in_rasters = ['F:/soilCarbon/inputData/elevation/nedf.tif',
            'F:/soilCarbon/inputData/elevation/twif',
            'F:/soilCarbon/inputData/elevation/slope',
            'F:/soilCarbon/inputData/aeroradiometric/namrad_k',
            'F:/soilCarbon/inputData/aeroradiometric/namrad_th',
            'F:/soilCarbon/inputData/aeroradiometric/namrad_u',
            'F:/soilCarbon/inputData/landCover/ncdl.tif',
            'F:/soilCarbon/inputData/soils/ssurgo_c',
            'F:/soilCarbon/inputData/precipitation/mapalb.tif',
            'F:/soilCarbon/inputData/temperature/matalb.tif']

        add_covariates(output_path, temp_shp_file, in_rasters)
        get_complete_cases(output_path, temp_shp_file, shp_file, output_file)

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
