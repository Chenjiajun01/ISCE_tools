#!/usr/bin/env python3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# last modified by J. Chen, @NCL, 2017-05-30
# mainly for ALOS data downloaded from ASF
# can handle data with different master and slave frames
# can handle different fbs/fbd mode for master and slave
# dem is only demfile name
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import isce
from isceobj.XmlUtil import FastXML_Chen as xml
import os, sys, glob
import argparse

#=====================================
###Set global variable, changeble
#=====================================
Data_dir = ''
Frame_list = []
#=====================================

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Create ALOS input xmlfile for insarApp'
    '''

Example: 

insarApp_create_ALOS_mlt.py -d rawdir -m masterID -s slaveID -f framelist -dem demfile -o outdir
            
''')
    parser.add_argument('-d','--rawDir', type=str, default=None, help='raw data folder path', dest='rawdir')
    parser.add_argument('-m','--masterID', type=str, required=True, help='master orbit number', dest='master')
    parser.add_argument('-s','--slaveID',type=str, required=True, help='slave orbit number', dest='slave')
    parser.add_argument('-f','--framelist',type=str, default=None, help='frame list', dest='frame')
    parser.add_argument('-dem','--demfile',type=str, default=None, help='dem file', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
    
   
    inps = parser.parse_args()

    return inps


def ALOS_insarapp_xml_generator(rawdir ,masterID, slaveID, frame_list, demfile=None, outdir='.'):
    '''
    Generation of insarApp.xml for ALOS raw data.

    Inputs:
         masterdir = full path to master folder
         slavedir = full path to slave folder
         demfile = full path to the dem file
         outdir = Directory in which you want insarApp.xml created
    '''
    ###missframe: record missed frame
    missframe = []
    #####Initialize a component named insar
    insar = xml.Component('insar')

    ####Python dictionaries become components
    ####Master info
    master = {} 
    slave = {}
    masterdir_list = []
    slavedir_list = []
    ###make sure master and slave have same frame list
    i = 0
    while i < len(frame_list): 
        if not (glob.glob(rawdir + '/ALP*' + masterID +'*' + frame_list[i] + '*' + 'L1.0')):
            print("no master data for frame: ", frame_list[i])
            del frame_list[i]
        else:
            i += 1     
    i = 0
    while i < len(frame_list):
        if not (glob.glob(rawdir + '/ALP*' + slaveID +'*' + frame_list[i] + '*')):
            print("no slave data for frame: ", frame_list[i])
            del frame_list[i]
        else:
            i +=1
    i = 0
    masterimg_list = []
    masterled_list = []
    slaveimg_list = []
    slaveled_list = []
    masterfbs = False
    slavefbs  = False
    for i, v in enumerate(frame_list):
        masterdir = glob.glob(rawdir + '/ALP*' + masterID +'*' + v + '*' + 'L1.0')[0]
        slavedir = glob.glob(rawdir + '/ALP*' + slaveID +'*' + v + '*' + 'L1.0')[0]

        masterimg = glob.glob(masterdir + '/IMG-HH*')[0]
        masterled = glob.glob(masterdir + '/LED*')[0]
        mastersize = os.path.getsize(masterimg)

        slaveimg = glob.glob(slavedir + '/IMG-HH*')[0]
        slaveled = glob.glob(slavedir + '/LED*')[0]
        slavesize = os.path.getsize(slaveimg)
        if i==0:
            if (round(1.0*mastersize/slavesize, 0)==2.0):
                slavefbs = True
            elif (round(1.0*mastersize/slavesize, 1)==0.5):
                masterfbs = True
        
        masterimg_list.append(os.path.basename(masterdir) + '/' + os.path.basename(masterimg))
        masterled_list.append(os.path.basename(masterdir) + '/' + os.path.basename(masterled))
        slaveimg_list.append(os.path.basename(slavedir) + '/' + os.path.basename(slaveimg))
        slaveled_list.append(os.path.basename(slavedir) + '/' + os.path.basename(slaveled))
    ###make it shorter
    masterimg = list(map(lambda x: '$RawDir$/' + x, masterimg_list))
    masterled = list(map(lambda x: '$RawDir$/' + x, masterled_list))
    master['IMAGEFILE']  =      masterimg      #Can be a string returned by another function
    master['LEADERFILE'] =      masterled      #Can be a string returned by another function
    if masterfbs:
        master['RESAMPLE_FLAG'] = 'dual2single'
    master['output'] = 'master.raw'    #Can parse file names and use date

    slaveimg = list(map(lambda x: '$RawDir$/' + x, slaveimg_list))
    slaveled = list(map(lambda x: '$RawDir$/' + x, slaveled_list))
    slave['IMAGEFILE']  =  slaveimg            #Can be a string returned by another function
    slave['LEADERFILE'] =  slaveled            #Can be a string returned by another function
    if slavefbs:
        slave['RESAMPLE_FLAG'] = 'dual2single'
    slave['output'] = 'slave.raw'     #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components
    insar['RawDir'] = xml.Constant(os.path.abspath(rawdir))
    insar['master'] = master
    insar['slave'] = slave

    ####user can change properties according the need
    ####Set properties###
    ############################
    insar['sensor name'] = 'ALOS'
    insar['range looks'] = 8
    insar['azimuth looks'] = 16
    insar['slc offset method'] = 'ampcor'
    insar['filter strength'] = 0.7
    insar['unwrap'] = 'True'
    insar['do unwrap 2 stage'] = 'True'
    insar['unwrapper name'] = 'snaphu_mcf'
    insar['geocode bounding box'] = [19.79, 23.86, 104.13, 105.66]
#    insar['geocode bounding box'] = S N W E
    insar['geocode list'] = 'filt_topophase.flat filt_topophase.unw filt_topophase_2stage.unw filt_topophase.unw.conncomp phsig.cor'
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
    insarApp_create_ALOS_mlt.py -d rawdir -m masterID -s slaveID -f framelist -dem demfile -o outdir
    '''

    if len(sys.argv) == 1:
        print("insarApp_create_ALOS_mlt.py -d rawdir -m masterID -s slaveID -f framelist -dem demfile -o outdir")
        sys.exit()
#        frame_list = '440, 450, 460, 470,480,490'
    elif len(sys.argv) > 1:
        inps = cmdLineParse()
        if inps.rawdir is None:
            rawdir = Data_dir
        else:
            rawdir = inps.rawdir
        if inps.frame is None:
            frame_list = Frame_list
        else:
            frame_list = inps.frame
        if len(frame_list) < 1:
            print("Error: frame list is required")
            sys.exit()
        master_ID = inps.master
        slave_ID = inps.slave
        frame_list = inps.frame.split(',')
        demfile = inps.dem
        int_dir = inps.out

    ####Example where no DEM is provided in the input file.
        ALOS_insarapp_xml_generator(os.path.abspath(rawdir), master_ID, slave_ID, frame_list, demfile, outdir= os.path.abspath(int_dir))
