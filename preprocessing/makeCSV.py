"""

Build a .csv representation of the covariate grid for use in R

"""

import arcpy
from arcpy import env

import csv
import sys
import time

if __name__ == "__main__":
    base_path = 'F:/soilCarbon/inputData/grid/fgdb.gdb/'
    input_table = 'outTable'
    output_file = 'F:/soilCarbon/inputData/grid/grid.csv'
    table = 'outTable'
    arcpy.env.workspace = base_path

    csv_out = output_file

    #Get field names
    fields = [x.name for x in arcpy.ListFields(table)]

    start = time.time()
    counter = 0

    with open(csv_out, "wb") as f:
        wr = csv.writer(f)
        wr.writerow(fields)
        with arcpy.da.SearchCursor(table, fields) as cursor:
            for row in cursor:
                counter += 1
                wr.writerow(row)

    end = time.time() - start

    print "{0} rows written in {1} seconds".format(counter, end)
