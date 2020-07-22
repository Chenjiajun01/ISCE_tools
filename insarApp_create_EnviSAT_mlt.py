#!/usr/bin/env python3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# created by J.Chen @NCL 07/05/2017
# last update: 08/05/2017
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from datetime import date,timedelta
import isce
from isceobj.XmlUtil import FastXML_Chen as xml
import os, sys, glob
import argparse

#=====================================
###Set global variable, changeble
#=====================================
Data_dir = ''
## necessary varibale=================
Orb_dir = '/mnt/hpc/storage/ESASAR/ENVISAT_DORISOrbits/ENVORB'
Ins_dir = '/mnt/hpc/storage/ESASAR/ASARAux'
#=====================================

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Create ESA EnviSAT input xmlfile for insarApp'
    '''

Example: 

insarApp_create_EnviSAT_mlt.py -d rawdir -m maindate maintime -s subordinatedate subordinatetime -dem demfile -o outdir
insarApp_create_EnviSAT_mlt.py -d rawdir -m YYYYMMDD 'hhmmss,hhmmss, ...' -s YYYYMMDD 'hhmmss, hhmmss, ...' -dem demfile -o outdir
            
''')
    parser.add_argument('-d','--rawDir', type=str, default=None, help='raw data folder path', dest='rawdir')
    parser.add_argument('-m','--main', type=str, nargs='+', required=True, help='main date and timelist', dest='main')
    parser.add_argument('-s','--subordinate',type=str, nargs='+', required=True, help='subordinate orbit number', dest='subordinate')
    parser.add_argument('-dem','--demfile',type=str, default=None, help='dem file', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
   
    inps = parser.parse_args()
    if len(inps.main) > 2:
        raise Exception('main should be at most two parameters. Undefined input for -m : '+str(inps.main))
    if len(inps.subordinate) > 2:
        raise Exception('subordinate should be at most two parameters. Undefined input for -m : '+str(inps.subordinate))

    return inps


def EnviSat_insarapp_xml_generator(rawdir, maindate, subordinatedate, maintime=None, subordinatetime=None, demfile=None, outdir='.'):
    '''
    Generation of insarApp.xml for EnviSAT raw data.

    Inputs:
         maintime = list of main time
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
    mainimg = []
    mainimg_list = []
    mainins = ''
    #all files in main date
    if maintime is None:
        mainfiles = glob.glob(rawdir + '/ASA_IM*' + maindate + '*.N1')
        mainimg_list = list(map(lambda x: os.path.basename(x), mainfiles))
    #defined time list
    else:
        for i, v in enumerate(maintime):
            tempfile = glob.glob(rawdir + '/ASA_IM*' + maindate +'*' + v + '*' + '.N1')[0]
            if not os.path.exists(tempfile):
                print(tempfile, " cannot be found")
                sys.exit()
            mainimg_list.append(os.path.basename(tempfile))
    ###make it shorter
    mainimg = list(map(lambda x: '$RawDir$/' + x, mainimg_list))
    #orbit file(only check date)
    date_main = date(int(maindate[0:4]), int(maindate[4:6]), int(maindate[6:8]))
    dt = timedelta(days=1)
    mdate_orbd1 = date_main - dt
    mdate_orbd2 = date_main + dt
    str_morbd1 = mdate_orbd1.strftime("%Y%m%d")
    str_morbd2 = mdate_orbd2.strftime("%Y%m%d")
    mainorb = glob.glob(Orb_dir + '/DOR_*' + str_morbd1 + '*' + str_morbd2 + '*')[0]
    if not os.path.exists(mainorb):
        sys.exit()
    #instrument file
    ins_all = glob.glob(Ins_dir + '/ASA_INS_AX*') 
    insname_all = list(map(lambda x: os.path.basename(x), ins_all))
    for i, v in enumerate(insname_all):
        str_d1 = v[30:38]
        str_d2 = v[46:54]
        date_d1 = date(int(str_d1[0:4]), int(str_d1[4:6]), int(str_d1[6:8]))
        date_d2 = date(int(str_d2[0:4]), int(str_d2[4:6]), int(str_d2[6:8]))
        #check if image date is between them
        if date_d1 > date_main or date_d2 < date_main:
            continue
        elif date_d1 <= date_main and date_d2 >= date_main:
            mainins = Ins_dir + '/' + v
        else:
            print("error to search main instrument file")
            sys.exit()
     #in case no instrument file found

    main['IMAGEFILE']  =           mainimg      #Can be a string returned by another function
    main['ORBITFILE']  =           mainorb     #Can be a string returned by another function
    main['INSTRUMENTFILE'] =       mainins     #Can be a string returned by another function
    main['output'] = 'main.raw'    #Can parse file names and use date

    ####Subordinate info
    subordinate = {}
    subordinateimg = []
    subordinateimg_list = []
    subordinateins = ''
     #all files in subordinate date
    if subordinatetime is None:
        subordinatefiles = glob.glob(rawdir + '/ASA_IM*' + subordinatedate + '*.N1')
        subordinateimg_list = list(map(lambda x: os.path.basename(x), subordinatefiles))
    #defined time list
    else:
        for i, v in enumerate(subordinatetime):
            tempfile = glob.glob(rawdir + '/ASA_IM*' + subordinatedate +'*' + v + '*' + '.N1')[0]
            if not os.path.exists(tempfile):
                print(tempfile, " cannot be found")
                sys.exit()
            subordinateimg_list.append(os.path.basename(tempfile))
    ###make it shorter
    subordinateimg = list(map(lambda x: '$RawDir$/' + x, subordinateimg_list))
    #orbit file(only check date)
    date_subordinate = date(int(subordinatedate[0:4]), int(subordinatedate[4:6]), int(subordinatedate[6:8]))
    ##dt = timedelta(days=1)
    subordinate_orbd1 = date_subordinate - dt
    subordinate_orbd2 = date_subordinate + dt
    str_sorbd1 = subordinate_orbd1.strftime("%Y%m%d")
    str_sorbd2 = subordinate_orbd2.strftime("%Y%m%d")
    subordinateorb = glob.glob(Orb_dir + '/DOR_*' + str_sorbd1 + '*' + str_sorbd2 + '*')[0]
    if not os.path.exists(subordinateorb):
        print(subordinateorb, " cannot be found")
        sys.exit()
    #instrument file
    #ins_all = glob.glob(Ins_dir + '/ASA_INS_AX*') 
    #insnameall = list(map(lambda x: os.path.basename(x), ins_all))
    for i, v in enumerate(insname_all):
        str_d1 = v[30:38]
        str_d2 = v[46:54]
        date_d1 = date(int(str_d1[0:4]), int(str_d1[4:6]), int(str_d1[6:8]))
        date_d2 = date(int(str_d2[0:4]), int(str_d2[4:6]), int(str_d2[6:8]))
        #check if image date is between them
        if date_d1 > date_subordinate or date_d2 < date_subordinate:
            continue
        elif date_d1 <= date_subordinate and date_d2 >= date_subordinate:
            subordinateins = Ins_dir + '/' + v
        else:
            print("error to search subordinate instrument file")
            sys.exit()
     #in case no instrument file found

    subordinate['IMAGEFILE']      =       subordinateimg      #Can be a string returned by another function
    subordinate['ORBITFILE']      =       subordinateorb      #Can be a string returned by another function
    subordinate['INSTRUMENTFILE'] =       subordinateins      #Can be a string returned by another function
    subordinate['output']         =      'subordinate.raw'    #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components
    insar['RawDir'] = xml.Constant(os.path.abspath(rawdir))
    insar['main'] = main
    insar['subordinate'] = subordinate

    ####user can change properties according the need
    ####Set properties###
    ############################
    insar['sensor name'] = 'Envisat'
    insar['doppler method'] = 'useDOPIQ'

#    insar['range looks'] = 4
#    insar['azimuth looks'] = 8
    insar['slc offset method'] = 'ampcor'
    insar['filter strength'] = 0.7
    insar['unwrap'] = 'False'
    insar['unwrapper name'] = 'snaphu_mcf'
#    insar['geocode bounding box'] = [25.33, 25.75, 97.39, 98.46]
#    insar['geocode bounding box'] = S N W E
    insar['geocode list'] = 'topophase.flat filt_topophase.flat filt_topophase.unw phsig.cor'
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
    insarApp_create_EnviSAT.py -d rawdir -m maindate maintimelist -s subordinatedate subordinatetimelist -dem demfile -o outdir
    '''

#    if len(sys.argv) == 1:
#        print("insarApp_create_EnviSAT_mlt.py -d rawdir -m maindate maintimelist -s subordinatedate subordinatetimelist -dem demfile -o outdir")
#        sys.exit()
#    if len(sys.argv) > 1:
    inps = cmdLineParse()
    if inps.rawdir is None:
        rawdir = Data_dir
    else:
        rawdir = inps.rawdir

    main_date = inps.main[0]
    if len(inps.main) == 1:
        main_timelist = None
    elif len(inps.main) == 2:
        main_timelist_str = inps.main[1]
        main_timelist = main_timelist_str.split(',')

    subordinate_date = inps.subordinate[0]
    if len(inps.subordinate) == 1:
        subordinate_timelist = None
    elif len(inps.subordinate) == 2:
        subordinate_timelist_str = inps.subordinate[1]
        subordinate_timelist = subordinate_timelist_str.split(',')

    demfile = inps.dem
    int_dir = inps.out

    ####Example where no DEM is provided in the input file.
    EnviSat_insarapp_xml_generator(os.path.abspath(rawdir), main_date, subordinate_date, main_timelist, subordinate_timelist, demfile, outdir= os.path.abspath(int_dir))
