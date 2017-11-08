# ISCE_tools
These scripts are for automatically batch processing based on ISCE;
copyright belongs to J. Chen @NCL.

These scripts are developed for my personal use, I will snowly to make it
easier for people don't understand ISCE, please do not ask for too much
from me;
 
!!! Please email j.chen26@ncl.ac.uk before sharing, also any bugs or questions;

1. ALOS-1 from ASF
2. S1 TOPS

---------------------------------------------------------------------------
1.1 Downloading ALOS-1 data from ASF
---------------------------------------------------------------------------
ASF Website: https://www.asf.alaska.edu/sar-data/palsar/download-data
Download L1.0 data of each track/orbit to folder ALOS_raw_zip

Unzip the zip data 
> Get_ALOSdataID.sh ALOS_raw_zip ALOS_raw
The zip data will be unzipped to directory ALOS_raw, and create a file named dateID.info in the same folder.
> Get_1col.sh ALOS_raw/dateID.info dates.list

---------------------------------------------------------------------------
1.2 Create processing directory and prepare DEM
---------------------------------------------------------------------------
Create a processing directory with three folders: processing, parameter, DEM
cd parameter
copy my isceBatchPrep_example.parameter to parameter/
copy my insarApp_create_ALOS_mlt.py to parameter/
copy my insarApp_thread.sh to parameter/
mv dates.list to processing/

Download DEM according to the your processing area
for 30m DEM:
> dem.py -b minLat maxLat minLon maxLon -r -c -f -s 1
for 90m DEM:
> dem.py -b minLat maxLat minLon maxLon -r -c -f -s 3

---------------------------------------------------------------------------
1.3 Sort processing folder for each pair
---------------------------------------------------------------------------
1.3.1 Set parameters in isceBatchPrep_example.parameter:
---------------------------------------------------------------------------

the Python scripts directory is the one has insarApp_create_ALOS_mlt.py;

dem should be only filename, no path;

ALOS conversion between orbit ID and date should be not changed;

the process mode of "all" means processing all data in your data directory, it requires datelist file: dates.list,
the process mode of "define" means processing date pairs you defined in "defined dates pair list file";

frame list cannot have space;

1.3.2 Set insarApp_create_ALOS_mlt.py according to your processing:
---------------------------------------------------------------------------
only change blocks of "Set properties",
you must set geocode bounding box for resample your result to same grids.

1.3.3 create processing folder
---------------------------------------------------------------------------
> loadisce
> isceBatchPrep isceBatchPrep_example.parameter

You do not need to copy isceBatchPrep to parameter file, you can set in your path or copy to anywhere as long as your machine can run it.
If run correctly, lots of folders will be created in processing/, and a date pairs list file should be in processing/,
if error occurs, please double check your setting, try to use absolute path.

---------------------------------------------------------------------------
1.4 Automatically batch processing
---------------------------------------------------------------------------
1.4.1 Set insarApp_thread.sh
---------------------------------------------------------------------------
set directories for processing and output, files for error and baseline...
set spatial baseline threshold,
set corherence mask threshold at " ${MY_SCR}/isce2phs_mask.py ... -t ",
set processing blocks as you like.

MY_SCR is the folder with isce2phs.py, you do not need to change it.

1.4.2 Processing
---------------------------------------------------------------------------
> cd processing
> ../parameter/insarApp_thread.sh datesPair

!!! It takes a few hours even a few days so please make sure you set everything correctly before running, I usually test one folder before running all.

If it runs correctly, you can get results with coherence masked unwrapped and wrapped results if you set in insarApp_thread.sh, and a baseline file and phslist file to help you run TS_AEM smoothly; 
you can also check the processing from log file, and the error pair except for large baselines will be output to a file, so you can check them and rerun ../parameter/insarApp_thread.sh datesPair_error;

If it runs with error, please check the log file and see the screen.log in the pair folder.
---------------------------------------------------------------------------
---------------------------------------------------------------------------



2. S1 from ESA Hub
---------------------------------------------------------------------------
2.1 Download IW SLC from ESA Hub
---------------------------------------------------------------------------
Data website: https://scihub.copernicus.eu/dhus/#/home
Download data of each orbit into one folder: S1_raw

**
* Precise orbits are in /home/users/b4037735/hpc2/SARDATA/orb.sentinel1.esa/poeorb;
* Orbit and auxiliary files have been set in topApp_creat_mlt.py
---------------------------------------------------------------------------
2.2 Create processing direcotry and prepare DEM
> mkdir $USERDIFINE_DIR/S1_ISCE
> cd $USERDIFINE_DIR/S1_ISCE
> mkdir process parameter dem30 dem90

** Explanation for related scripts
* isceBatchPrep is to create processing folders by calling topsApp_created_mlt.py
* topsApp_created_mlt.py is to create topsApp.py for a single pair
* topsApp_created_mlt.py is always for the latest ISCE version
* topsApp_created_mlt_old.py is for ISCE_20170403
* topsApp_thread.sh is to run the batch processing

copy my isceBatchPrep_example.parameter to parameter/
copy my insarApp_create_ALOS_mlt.py to parameter/
copy my topsApp_thread.sh to parameter/

optional: create a datelist file using Get_S1date.sh

download DEM and water mask to DEM folder
dem30:
> dem.py -b s n w e -c -f -r -s 1
dem90:
> dem.py -b s n w e -c -f -r -s 3

---------------------------------------------------------------------------
2.3 Sort processing folder for each pair (similar to 1.3)
---------------------------------------------------------------------------
set parameters in isceBatchPrep_example.parameter

check topsApp_create_mlt.py to set ISCE processing parameters,

run isceBatchPrep to create processing folders:
> loadisce
> isceBatchPrep isceBatchPrep_example.parameter
go to process directory and check if everything correct.

---------------------------------------------------------------------------
2.4 Automatically batch processing (similar to 1.4)
---------------------------------------------------------------------------
set topsApp_thread.sh

go to process directory, and run:
../parameter/insarApp_thread.sh datesPair

check the log file to see the status and check error
---------------------------------------------------------------------------
---------------------------------------------------------------------------
