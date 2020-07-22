#!/usr/bin/env python3
import isce
from isceobj.XmlUtil import FastXML_Chen as xml
import os, sys, glob
import argparse

#=====================================
###Set global variable, changeble
#=====================================
HDF5_dir = '/home/users/b4037735/hpc2/SARDATA/Shihezi_S1A'

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Create Sentinel input xmlfile for topsApp'
    '''

Example: 

insarApp_create_CSK.py -d datadir -m maindate -s subordinatedate -dem dempath -o outdir
            
''')
    parser.add_argument('-d','--rawdir', type=str, required=False, help='raw data dir', dest='rdir')
    parser.add_argument('-m','--maind', type=str, required=True, help='main data date', dest='main')
    parser.add_argument('-s','--subordinated',type=str, required=True, help='subordinate data date', dest='subordinate')
    parser.add_argument('-dem','--dem',type=str, default=None, help='dem file path', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
    
   
    inps = parser.parse_args()
    if (not inps.main or not inps.subordinate):
        print('User did not provide main or subordinate data dates')
        sys.exit(0)

    return inps


def CSK_insarapp_xml_generator(rawdir, maindate, subordinatedate, demfile=None, outdir='.'):
    '''
    Generation of topsApp.xml for ALOS raw data.

    Inputs:
         maindate = 8-digital main date 
         subordinatedate = 8-digital subordinate date
         demfile = full path to the dem file
         outdir = Directory in which you want topsApp.xml created
    '''
    #####Initialize a component named tops
    insar = xml.Component('insar')
    insar['sensor name'] = 'COSMO_SKYMED_SLC'

    ####Python dictionaries become components
    ####Main info
    main = {} 
    mainsafe = glob.glob(rawdir + '/CSK*' + maindate + '*.h5') #list
    main['safe']  =  '$HDF5dir$/' + os.path.basename(mainsafe[0])
    main['output directory'] = maindate

    ####Subordinate info
    subordinate = {}
    subordinatesafe = glob.glob(rawdir + '/CSK*' + subordinatedate + '*.h5') #list
    subordinate['safe']  =  '$HDF5dir$/' + os.path.basename(subordinatesafe[0])
    subordinate['output directory'] = subordinatedate

    #####Set sub-component
    ####Nested dictionaries become nested components

    insar['HDF5dir'] = xml.Constant(os.path.abspath(rawdir))

    insar['main'] = main
    insar['subordinate'] = subordinate

    ####Set properties
    insar['doppler method'] = 'useDEFAULT'
    insar['range looks'] = 2
    insar['azimuth looks'] = 10
    insar['filter strength'] = 0.5
    insar['slc offset method'] = 'ampcor'
    insar['do unwrap'] = 'True'
    insar['unwrapper name'] = 'snaphu_mcf'
#    insar['region of interest'] = [s, n, w, e]
#    insar['geocode bounding box'] = [19.1, 19.45, -155.45, -154.7]
    insar['geocode list'] = ['merged/filt_topophase.flat','merged/filt_topophase.unw','merged/los.rdr','merged/topophase.cor','merged/phsig.cor']

    #####Catalog example
    ####Use xml.catalog to distinguish Catalog entries
    if demfile is not None:
#        insar['dem'] = xml.Catalog(demfile + '.xml')
        insar['demFilename'] = demfile

    ####Components include a writeXML method
    ####Write insarApp.xml in output directory
    insar.writeXML(os.path.join(outdir, 'insarApp.xml'), root='insarApp')

    return

if __name__ == '__main__':
    '''
    Usage example
    insarApp_create_CSK.py -d dir -m maindate -s subordinatedate -dem dempath -o outdir
    '''

    if len(sys.argv) == 1:
        print("insarApp_create_CSK.py -d dir -m maindate -s subordinatedate -dem dempath -o outdir")
        sys.exit()
    elif len(sys.argv) > 1:
        inps = cmdLineParse()
        if inps.rdir is None:
            rawdir = HDF5_dir
        else:
            rawdir = inps.rdir;
        maindate = inps.main;
        subordinatedate = inps.subordinate;
        demfile = inps.dem;
        xml_dir = inps.out;

    ####Example where no DEM is provided in the input file.
    CSK_insarapp_xml_generator(rawdir, maindate, subordinatedate, demfile, outdir= os.path.abspath(xml_dir))
