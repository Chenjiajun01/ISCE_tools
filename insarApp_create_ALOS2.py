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

insarApp_create_ALOS.py -m maindir -s subordinatedir -dem dempath -o outdir
            
''')
    parser.add_argument('-m','--maind', type=str, required=True, help='main data folder path', dest='main')
    parser.add_argument('-s','--subordinated',type=str, required=True, help='subordinate data folder path', dest='subordinate')
    parser.add_argument('-dem','--dem',type=str, default=None, help='dem file path', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
    
   
    inps = parser.parse_args()
    if (not inps.main or not inps.subordinate):
        print('User did not provide main or subordinate data path')
        sys.exit(0)

    return inps


def ALOS_insarapp_xml_generator(maindir, subordinatedir, demfile=None, outdir='.'):
    '''
    Generation of insarApp.xml for ALOS raw data.

    Inputs:
         maindir = full path to main folder
         subordinatedir = full path to subordinate folder
         demfile = full path to the dem file
         outdir = Directory in which you want insarApp.xml created
    '''
    #####Initialize a component named insar
    insar = xml.Component('insar')

    ####Python dictionaries become components
    ####Main info
    main = {} 
    mainimg = glob.glob(maindir + '/IMG-HH*') #list
    mainled = glob.glob(maindir + '/LED-*')
    main['IMAGEFILE']  =      mainimg[0]      #Can be a string returned by another function
    main['LEADERFILE'] =      mainled[0]      #Can be a string returned by another function
    main['output'] = 'main.slc'    #Can parse file names and use date

    ####Subordinate info
    subordinate = {}
    subordinateimg = glob.glob(subordinatedir + '/IMG-HH*')
    subordinateled = glob.glob(subordinatedir + '/LED-*')
    subordinate['IMAGEFILE']  =  subordinateimg[0]            #Can be a string returned by another function
    subordinate['LEADERFILE'] =  subordinateled[0]            #Can be a string returned by another function
    subordinate['output'] = 'subordinate.slc'     #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components
    insar['main'] = main
    insar['subordinate'] = subordinate

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
    insarApp_create_ALOS.py -m maindir -s subordinatedir -dem dempath -o outdir
    '''

    if len(sys.argv) == 1:
        print("insarApp_create_ALOS.py -m maindir -s subordinatedir -dem dempath -o outdir")
        sys.exit(0)
    elif len(sys.argv) > 1:
        inps = cmdLineParse()
        maindir = inps.main;
        subordinatedir = inps.subordinate;
        dempath = inps.dem;
        int_dir = inps.out;

    ####Example where no DEM is provided in the input file.
    if dempath == None:
        ALOS_insarapp_xml_generator(os.path.abspath(maindir), os.path.abspath(subordinatedir), demfile= None, outdir= os.path.abspath(int_dir))
    else: 
        ALOS_insarapp_xml_generator(os.path.abspath(maindir), os.path.abspath(subordinatedir), demfile= os.path.abspath(dempath), outdir= os.path.abspath(int_dir))
