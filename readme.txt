VERSION INFORMATION

The code in the 'code' subdirectory and below are the original versions
distributed with the data package, and will not be maintained or updated
after publication. For the latest version including any updates, or to
obtain other historical versions of the code, visit the GitHub repository at

https://github.com/flathers/soilCarbonFramework


CONTENTS

./code
	Within the ./code/preprocessing subdirectory is a script for producing each
	required input product. The order of most of the preprocessing steps is 
	unimportant.

		aeroradiometric.py - processes the K, Th, U data into rasters for input.

		boundaries.py - clips state and county polygon layers for cartographic
		purposes. These products are not used in analysis.

		gssurgoSOC.py - builds the SOC raster based upon GSSURGO values for input.

		makeCSV.py - exports the covariates raster to CSV for input. This script
		should be the last preprocessing step run.

		makeGrid.py - gathers the covariates from input files into a raster. This
		script produces the input product for makeCSV.py and should be run immediately
		prior.

		maPrecip.py - computes mean annual temperature for input.

		maTemp.py - computes mean annual precipitation for input.

		ncdl.py - processes the NCDL data into a raster for input.

		ncss.py - processes NCSS soil samples into a point-based shapefile for input.

		ned.py - processes the NED data into a raster for input.

		rasterPoints.py - uses the NED raster to create a centerpoints dataset based
		upon the NED grid.

	The ./code/aws.sh file contains basic shell commands required for preparing an
	Ubuntu 14.04 system to execute the statistical model in R. The model requires
	significant amounts of RAM to execute. The authors have had success on a
	machine equipped with 244 GB of RAM.

	The ./code/scorpan.R file contains the R script for executing the statistical
	model.

	The ./code/postprocessing/asc2raster.py file is the script for producing the
	final raster products. It should be run at the end.


./downloadedData
	Contains the downloaded data files. Check ./dataSources.txt to see where they
	came from. These are the originals and are kept in case of accidental changes
	to the input files.

./extractedData
	The unzipped versions of the downloaded data. These files are used as inputs
	to the preprocessor scripts.

./figures
	ArcMap documents for the figures from the journal article

./inputData
	Preprocessed data. These files are the output of the preprocessor scripts,
	and the input for the modeling process.

./outputData
	Modeled outputs. These files are the raw outputs of the R script.

	./outputData/rasters
		The raster outputs that are the product of the model.

./dataSources.txt
	Sources and some details about obtaining the downloaded data.

./license.txt
	An expression of the license for this release.




