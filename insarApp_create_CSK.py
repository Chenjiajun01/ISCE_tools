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

insarApp_create_CSK.py -d datadir -m masterdate -s slavedate -dem dempath -o outdir
            
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


def CSK_insarapp_xml_generator(rawdir, masterdate, slavedate, demfile=None, outdir='.'):
    '''
    Generation of topsApp.xml for ALOS raw data.

    Inputs:
         masterdate = 8-digital master date 
         slavedate = 8-digital slave date
         demfile = full path to the dem file
         outdir = Directory in which you want topsApp.xml created
    '''
    #####Initialize a component named tops
    insar = xml.Component('insar')
    insar['sensor name'] = 'COSMO_SKYMED_SLC'

    ####Python dictionaries become components
    ####Master info
    master = {} 
    mastersafe = glob.glob(rawdir + '/CSK*' + masterdate + '*.h5') #list
    master['safe']  =  '$HDF5dir$/' + os.path.basename(mastersafe[0])
    master['output directory'] = masterdate

    ####Slave info
    slave = {}
    slavesafe = glob.glob(rawdir + '/CSK*' + slavedate + '*.h5') #list
    slave['safe']  =  '$HDF5dir$/' + os.path.basename(slavesafe[0])
    slave['output directory'] = slavedate

    #####Set sub-component
    ####Nested dictionaries become nested components

    insar['HDF5dir'] = xml.Constant(os.path.abspath(rawdir))

    insar['master'] = master
    insar['slave'] = slave

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
    insarApp_create_CSK.py -d dir -m masterdate -s slavedate -dem dempath -o outdir
    '''

    if len(sys.argv) == 1:
        print("insarApp_create_CSK.py -d dir -m masterdate -s slavedate -dem dempath -o outdir")
        sys.exit()
    elif len(sys.argv) > 1:
        inps = cmdLineParse()
        if inps.rdir is None:
            rawdir = HDF5_dir
        else:
            rawdir = inps.rdir;
        masterdate = inps.master;
        slavedate = inps.slave;
        demfile = inps.dem;
        xml_dir = inps.out;

    ####Example where no DEM is provided in the input file.
    CSK_insarapp_xml_generator(rawdir, masterdate, slavedate, demfile, outdir= os.path.abspath(xml_dir))
