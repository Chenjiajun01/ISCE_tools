#!/usr/bin/env python3
import isce
from isceobj.XmlUtil import FastXML as xml
import os, sys, glob
import argparse

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Create ALOS input xmlfile for insarApp'
    '''

Example: 

insarApp_create_ALOS.py -m masterdir -s slavedir -dem dempath -o outdir
            
''')
    parser.add_argument('-m','--masterd', type=str, required=True, help='master data folder path', dest='master')
    parser.add_argument('-s','--slaved',type=str, required=True, help='slave data folder path', dest='slave')
    parser.add_argument('-dem','--dem',type=str, default=None, help='dem file path', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
    
   
    inps = parser.parse_args()
    if (not inps.master or not inps.slave):
        print('User did not provide master or slave data path')
        sys.exit(0)

    return inps


def ALOS_insarapp_xml_generator(masterdir, slavedir, demfile=None, outdir='.'):
    '''
    Generation of insarApp.xml for ALOS raw data.

    Inputs:
         masterdir = full path to master folder
         slavedir = full path to slave folder
         demfile = full path to the dem file
         outdir = Directory in which you want insarApp.xml created
    '''
    #####Initialize a component named insar
    insar = xml.Component('insar')

    ####Python dictionaries become components
    ####Master info
    master = {} 
    masterimg = glob.glob(masterdir + '/IMG-HH*') #list
    masterled = glob.glob(masterdir + '/LED-*')
    master['IMAGEFILE']  =      masterimg[0]      #Can be a string returned by another function
    master['LEADERFILE'] =      masterled[0]      #Can be a string returned by another function
    master['output'] = 'master.slc'    #Can parse file names and use date

    ####Slave info
    slave = {}
    slaveimg = glob.glob(slavedir + '/IMG-HH*')
    slaveled = glob.glob(slavedir + '/LED-*')
    slave['IMAGEFILE']  =  slaveimg[0]            #Can be a string returned by another function
    slave['LEADERFILE'] =  slaveled[0]            #Can be a string returned by another function
    slave['output'] = 'slave.slc'     #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components
    insar['master'] = master
    insar['slave'] = slave

    ####Set properties
    insar['sensor name'] = 'ALOS2'
    insar['doppler method'] = 'useDEFAULT'
    insar['range looks'] = 2
    insar['azimuth looks'] = 4
    insar['slc offset method'] = 'ampcor'
    insar['filter strength'] = 0.6
    insar['unwrap'] = 'True'
    insar['unwrapper name'] = 'snaphu_mcf'
#    insar['geocode bounding box'] = [19.1, 19.45, -155.45, -154.7]
    insar['geocode list'] = 'filt_topophase.flat filt_topophase.unw los.rdr topophase.cor phsig.cor'

    #####Catalog example
    ####Use xml.catalog to distinguish Catalog entries
    if demfile is not None:
        insar['dem'] = xml.Catalog(demfile + '.xml') 

    ####Components include a writeXML method
    ####Write insarApp.xml in output directory
    insar.writeXML(os.path.join(outdir, 'insarApp.xml'), root='insarApp')

    return

if __name__ == '__main__':
    '''
    Usage example
    insarApp_create_ALOS.py -m masterdir -s slavedir -dem dempath -o outdir
    '''

    if len(sys.argv) == 1:
        print("insarApp_create_ALOS.py -m masterdir -s slavedir -dem dempath -o outdir")
        sys.exit(0)
    elif len(sys.argv) > 1:
        inps = cmdLineParse()
        masterdir = inps.master;
        slavedir = inps.slave;
        dempath = inps.dem;
        int_dir = inps.out;

    ####Example where no DEM is provided in the input file.
    if dempath == None:
        ALOS_insarapp_xml_generator(os.path.abspath(masterdir), os.path.abspath(slavedir), demfile= None, outdir= os.path.abspath(int_dir))
    else: 
        ALOS_insarapp_xml_generator(os.path.abspath(masterdir), os.path.abspath(slavedir), demfile= os.path.abspath(dempath), outdir= os.path.abspath(int_dir))
