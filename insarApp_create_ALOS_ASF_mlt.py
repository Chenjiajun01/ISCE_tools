#!/usr/bin/env python3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# last modified by J. Chen, @NCL, 2017-05-30
# mainly for ALOS data downloaded from ASF
# can handle data with different main and subordinate frames
# can handle different fbs/fbd mode for main and subordinate
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

insarApp_create_ALOS_mlt.py -d rawdir -m mainID -s subordinateID -f framelist -dem demfile -o outdir
            
''')
    parser.add_argument('-d','--rawDir', type=str, default=None, help='raw data folder path', dest='rawdir')
    parser.add_argument('-m','--mainID', type=str, required=True, help='main orbit number', dest='main')
    parser.add_argument('-s','--subordinateID',type=str, required=True, help='subordinate orbit number', dest='subordinate')
    parser.add_argument('-f','--framelist',type=str, default=None, help='frame list', dest='frame')
    parser.add_argument('-dem','--demfile',type=str, default=None, help='dem file', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
    
   
    inps = parser.parse_args()

    return inps


def ALOS_insarapp_xml_generator(rawdir ,mainID, subordinateID, frame_list, demfile=None, outdir='.'):
    '''
    Generation of insarApp.xml for ALOS raw data.

    Inputs:
         maindir = full path to main folder
         subordinatedir = full path to subordinate folder
         demfile = full path to the dem file
         outdir = Directory in which you want insarApp.xml created
    '''
    ###missframe: record missed frame
    missframe = []
    #####Initialize a component named insar
    insar = xml.Component('insar')

    ####Python dictionaries become components
    ####Main info
    main = {} 
    subordinate = {}
    maindir_list = []
    subordinatedir_list = []
    ###make sure main and subordinate have same frame list
    i = 0
    while i < len(frame_list): 
        if not (glob.glob(rawdir + '/ALP*' + mainID +'*' + frame_list[i] + '*' + 'L1.0')):
            print("no main data for frame: ", frame_list[i])
            del frame_list[i]
        else:
            i += 1     
    i = 0
    while i < len(frame_list):
        if not (glob.glob(rawdir + '/ALP*' + subordinateID +'*' + frame_list[i] + '*')):
            print("no subordinate data for frame: ", frame_list[i])
            del frame_list[i]
        else:
            i +=1
    i = 0
    mainimg_list = []
    mainled_list = []
    subordinateimg_list = []
    subordinateled_list = []
    mainfbs = False
    subordinatefbs  = False
    for i, v in enumerate(frame_list):
        maindir = glob.glob(rawdir + '/ALP*' + mainID +'*' + v + '*' + 'L1.0')[0]
        subordinatedir = glob.glob(rawdir + '/ALP*' + subordinateID +'*' + v + '*' + 'L1.0')[0]

        mainimg = glob.glob(maindir + '/IMG-HH*')[0]
        mainled = glob.glob(maindir + '/LED*')[0]
        mainsize = os.path.getsize(mainimg)

        subordinateimg = glob.glob(subordinatedir + '/IMG-HH*')[0]
        subordinateled = glob.glob(subordinatedir + '/LED*')[0]
        subordinatesize = os.path.getsize(subordinateimg)
        if i==0:
            if (round(1.0*mainsize/subordinatesize, 0)==2.0):
                subordinatefbs = True
            elif (round(1.0*mainsize/subordinatesize, 1)==0.5):
                mainfbs = True
        
        mainimg_list.append(os.path.basename(maindir) + '/' + os.path.basename(mainimg))
        mainled_list.append(os.path.basename(maindir) + '/' + os.path.basename(mainled))
        subordinateimg_list.append(os.path.basename(subordinatedir) + '/' + os.path.basename(subordinateimg))
        subordinateled_list.append(os.path.basename(subordinatedir) + '/' + os.path.basename(subordinateled))
    ###make it shorter
    mainimg = list(map(lambda x: '$RawDir$/' + x, mainimg_list))
    mainled = list(map(lambda x: '$RawDir$/' + x, mainled_list))
    main['IMAGEFILE']  =      mainimg      #Can be a string returned by another function
    main['LEADERFILE'] =      mainled      #Can be a string returned by another function
    if mainfbs:
        main['RESAMPLE_FLAG'] = 'dual2single'
    main['output'] = 'main.raw'    #Can parse file names and use date

    subordinateimg = list(map(lambda x: '$RawDir$/' + x, subordinateimg_list))
    subordinateled = list(map(lambda x: '$RawDir$/' + x, subordinateled_list))
    subordinate['IMAGEFILE']  =  subordinateimg            #Can be a string returned by another function
    subordinate['LEADERFILE'] =  subordinateled            #Can be a string returned by another function
    if subordinatefbs:
        subordinate['RESAMPLE_FLAG'] = 'dual2single'
    subordinate['output'] = 'subordinate.raw'     #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components
    insar['RawDir'] = xml.Constant(os.path.abspath(rawdir))
    insar['main'] = main
    insar['subordinate'] = subordinate

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
    insarApp_create_ALOS_mlt.py -d rawdir -m mainID -s subordinateID -f framelist -dem demfile -o outdir
    '''

    if len(sys.argv) == 1:
        print("insarApp_create_ALOS_mlt.py -d rawdir -m mainID -s subordinateID -f framelist -dem demfile -o outdir")
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
        main_ID = inps.main
        subordinate_ID = inps.subordinate
        frame_list = inps.frame.split(',')
        demfile = inps.dem
        int_dir = inps.out

    ####Example where no DEM is provided in the input file.
        ALOS_insarapp_xml_generator(os.path.abspath(rawdir), main_ID, subordinate_ID, frame_list, demfile, outdir= os.path.abspath(int_dir))
