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

topsApp_create.py -d datadir -m masterdate -s slavedate -dem dempath -o outdir
            
''')
    parser.add_argument('-d','--rawdir', type=str, required=False, help='raw data dir', dest='rdir')
    parser.add_argument('-m','--masterd', type=str, required=True, help='master data date', dest='master')
    parser.add_argument('-s','--slaved',type=str, required=True, help='slave data date', dest='slave')
    parser.add_argument('-dem','--dem',type=str, default=None, help='dem file path', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
    
   
    inps = parser.parse_args()
    if (not inps.master or not inps.slave):
        print('User did not provide master or slave data dates')
        sys.exit(0)

    return inps


def SENTINEL1_topsapp_xml_generator(rawdir, masterdate, slavedate, demfile=None, outdir='.'):
    '''
    Generation of topsApp.xml for ALOS raw data.

    Inputs:
         masterdate = 8-digital master date 
         slavedate = 8-digital slave date
         demfile = full path to the dem file
         outdir = Directory in which you want topsApp.xml created
    '''
    #####Initialize a component named tops
    topsinsar = xml.Component('topsinsar')
    topsinsar['sensor name'] = 'SENTINEL1'
    if swaths: 
        topsinsar['swaths'] = swaths    

    ####Python dictionaries become components
    ####Master info
    master = {} 
    mastersafe = glob.glob(rawdir + '/S1?_IW*' + masterdate + '*') #list
#    master['safe']  =  mastersafe[0]      #Can be a string returned by another function
    master['safe']  =  list(map(lambda x: '$SAFEdir$/' + os.path.basename(x), mastersafe))
#    master['swath number'] = swath_number
    master['output directory'] = masterdate 
    master['orbit directory'] = Orbit_dir    #Can parse file names and use date
    if Auxil_dir != '':
        master['auxiliary data directory'] = Auxil_dir    #Can parse file names and use date

    ####Slave info
    slave = {}
    slavesafe = glob.glob(rawdir + '/*' + slavedate + '*') #list
#    slave['safe']  =  slavesafe[0]      #Can be a string returned by another function
    slave['safe']  =  list(map(lambda x: '$SAFEdir$/' + os.path.basename(x), slavesafe))
#    slave['swath number'] = swath_number
    slave['output directory'] = slavedate 
    slave['orbit directory'] = Orbit_dir    #Can parse file names and use date
    if Auxil_dir != '':
        slave['auxiliary data directory'] = Auxil_dir    #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components

    topsinsar['SAFEdir'] = xml.Constant(os.path.abspath(rawdir))

    topsinsar['master'] = master
    topsinsar['slave'] = slave

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
    topsApp_create_ALOS.py -m masterdate -s slavedate -dem dempath -o outdir
    '''

    if len(sys.argv) == 1:
        print("topsApp_create_ALOS.py -d dir -m masterdate -s slavedate -dem dempath -o outdir")
        sys.exit()
    elif len(sys.argv) > 1:
        inps = cmdLineParse()
        if inps.rdir is None:
            rawdir = Safe_dir
        else:
            rawdir = inps.rdir;
        masterdate = inps.master;
        slavedate = inps.slave;
        demfile = inps.dem;
        xml_dir = inps.out;

    ####Example where no DEM is provided in the input file.
    SENTINEL1_topsapp_xml_generator(rawdir, masterdate, slavedate, demfile, outdir= os.path.abspath(xml_dir))
