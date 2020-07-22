#!/usr/bin/env python3
####
# Created by J. Chen @NCL in 2017
# Last updated by J. Chen @NCL 2017-10-12
####

import isce
from isceobj.XmlUtil import FastXML_Chen as xml
import os, sys, glob
import argparse

#=====================================
###Set global variable, changeble
swaths = [1,2,3]
#=====================================
Safe_dir = '/home/users/b4037735/hpc3/SARDATA/BOTSWANA_S1'
Orbit_dir = '/home/users/b4037735/hpc2/SARDATA/orb.sentinel1.esa/poeorb'
Auxil_dir = '/mnt/geodesy43/b3053922/orbitfiles/qc.sentinel1.eo.esa.int/aux_cal'

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Create Sentinel input xmlfile for topsApp'
    '''

Example: 

topsApp_create.py -d datadir -m maindate -s subordinatedate -dem dempath -o outdir
            
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


def SENTINEL1_topsapp_xml_generator(rawdir, maindate, subordinatedate, demfile=None, outdir='.'):
    '''
    Generation of topsApp.xml for ALOS raw data.

    Inputs:
         maindate = 8-digital main date 
         subordinatedate = 8-digital subordinate date
         demfile = full path to the dem file
         outdir = Directory in which you want topsApp.xml created
    '''
    #####Initialize a component named tops
    topsinsar = xml.Component('topsinsar')
    topsinsar['sensor name'] = 'SENTINEL1'
    if swaths: 
        topsinsar['swaths'] = swaths    

    ####Python dictionaries become components
    ####Main info
    main = {} 
    mainsafe = glob.glob(rawdir + '/S1?_IW*' + maindate + '*') #list
#    main['safe']  =  mainsafe[0]      #Can be a string returned by another function
    main['safe']  =  list(map(lambda x: '$SAFEdir$/' + os.path.basename(x), mainsafe))
#    main['swath number'] = swath_number
    main['output directory'] = maindate 
    main['orbit directory'] = Orbit_dir    #Can parse file names and use date
    if Auxil_dir != '':
        main['auxiliary data directory'] = Auxil_dir    #Can parse file names and use date

    ####Subordinate info
    subordinate = {}
    subordinatesafe = glob.glob(rawdir + '/*' + subordinatedate + '*') #list
#    subordinate['safe']  =  subordinatesafe[0]      #Can be a string returned by another function
    subordinate['safe']  =  list(map(lambda x: '$SAFEdir$/' + os.path.basename(x), subordinatesafe))
#    subordinate['swath number'] = swath_number
    subordinate['output directory'] = subordinatedate 
    subordinate['orbit directory'] = Orbit_dir    #Can parse file names and use date
    if Auxil_dir != '':
        subordinate['auxiliary data directory'] = Auxil_dir    #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components

    topsinsar['SAFEdir'] = xml.Constant(os.path.abspath(rawdir))

    topsinsar['main'] = main
    topsinsar['subordinate'] = subordinate

#=====================================================
#### User set properties

    topsinsar['range looks'] = 10
    topsinsar['azimuth looks'] = 2
    topsinsar['filter strength'] = 0.5
    topsinsar['esd coherence threshold'] = 0.85
    topsinsar['do unwrap'] = 'False'
    topsinsar['do unwrap 2 stage'] = 'True'
    topsinsar['unwrapper name'] = 'snaphu_mcf'
#    topsinsar['region of interest'] = [s, n, w, e]
#    topsinsar['geocode bounding box'] = [19.1, 19.45, -155.45, -154.7]
    topsinsar['geocode list'] = ['merged/filt_topophase.flat','merged/filt_topophase.unw','merged/filt_topophase_2stage.unw','merged/filt_topophase.unw.conncomp','merged/los.rdr','merged/phsig.cor']

#=====================================================

    #####Catalog example
    ####Use xml.catalog to distinguish Catalog entries
    if demfile is not None:
#        topsinsar['dem'] = xml.Catalog(demfile + '.xml')
        topsinsar['demFilename'] = demfile

    ####Components include a writeXML method
    ####Write topsApp.xml in output directory
    topsinsar.writeXML(os.path.join(outdir, 'topsApp.xml'), root='topsApp')

    return

if __name__ == '__main__':
    '''
    Usage example
    topsApp_create_ALOS.py -m maindate -s subordinatedate -dem dempath -o outdir
    '''

    if len(sys.argv) == 1:
        print("topsApp_create_ALOS.py -d dir -m maindate -s subordinatedate -dem dempath -o outdir")
        sys.exit()
    elif len(sys.argv) > 1:
        inps = cmdLineParse()
        if inps.rdir is None:
            rawdir = Safe_dir
        else:
            rawdir = inps.rdir;
        maindate = inps.main;
        subordinatedate = inps.subordinate;
        demfile = inps.dem;
        xml_dir = inps.out;

    ####Example where no DEM is provided in the input file.
    SENTINEL1_topsapp_xml_generator(rawdir, maindate, subordinatedate, demfile, outdir= os.path.abspath(xml_dir))
