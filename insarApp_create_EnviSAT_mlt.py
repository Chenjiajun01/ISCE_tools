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

insarApp_create_EnviSAT_mlt.py -d rawdir -m masterdate mastertime -s slavedate slavetime -dem demfile -o outdir
insarApp_create_EnviSAT_mlt.py -d rawdir -m YYYYMMDD 'hhmmss,hhmmss, ...' -s YYYYMMDD 'hhmmss, hhmmss, ...' -dem demfile -o outdir
            
''')
    parser.add_argument('-d','--rawDir', type=str, default=None, help='raw data folder path', dest='rawdir')
    parser.add_argument('-m','--master', type=str, nargs='+', required=True, help='master date and timelist', dest='master')
    parser.add_argument('-s','--slave',type=str, nargs='+', required=True, help='slave orbit number', dest='slave')
    parser.add_argument('-dem','--demfile',type=str, default=None, help='dem file', dest='dem')
    parser.add_argument('-o','--outdir',type=str, default='./', help='output xml file path', dest='out')
   
    inps = parser.parse_args()
    if len(inps.master) > 2:
        raise Exception('master should be at most two parameters. Undefined input for -m : '+str(inps.master))
    if len(inps.slave) > 2:
        raise Exception('slave should be at most two parameters. Undefined input for -m : '+str(inps.slave))

    return inps


def EnviSat_insarapp_xml_generator(rawdir, masterdate, slavedate, mastertime=None, slavetime=None, demfile=None, outdir='.'):
    '''
    Generation of insarApp.xml for EnviSAT raw data.

    Inputs:
         mastertime = list of master time
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
    masterimg = []
    masterimg_list = []
    masterins = ''
    #all files in master date
    if mastertime is None:
        masterfiles = glob.glob(rawdir + '/ASA_IM*' + masterdate + '*.N1')
        masterimg_list = list(map(lambda x: os.path.basename(x), masterfiles))
    #defined time list
    else:
        for i, v in enumerate(mastertime):
            tempfile = glob.glob(rawdir + '/ASA_IM*' + masterdate +'*' + v + '*' + '.N1')[0]
            if not os.path.exists(tempfile):
                print(tempfile, " cannot be found")
                sys.exit()
            masterimg_list.append(os.path.basename(tempfile))
    ###make it shorter
    masterimg = list(map(lambda x: '$RawDir$/' + x, masterimg_list))
    #orbit file(only check date)
    date_master = date(int(masterdate[0:4]), int(masterdate[4:6]), int(masterdate[6:8]))
    dt = timedelta(days=1)
    mdate_orbd1 = date_master - dt
    mdate_orbd2 = date_master + dt
    str_morbd1 = mdate_orbd1.strftime("%Y%m%d")
    str_morbd2 = mdate_orbd2.strftime("%Y%m%d")
    masterorb = glob.glob(Orb_dir + '/DOR_*' + str_morbd1 + '*' + str_morbd2 + '*')[0]
    if not os.path.exists(masterorb):
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
        if date_d1 > date_master or date_d2 < date_master:
            continue
        elif date_d1 <= date_master and date_d2 >= date_master:
            masterins = Ins_dir + '/' + v
        else:
            print("error to search master instrument file")
            sys.exit()
     #in case no instrument file found

    master['IMAGEFILE']  =           masterimg      #Can be a string returned by another function
    master['ORBITFILE']  =           masterorb     #Can be a string returned by another function
    master['INSTRUMENTFILE'] =       masterins     #Can be a string returned by another function
    master['output'] = 'master.raw'    #Can parse file names and use date

    ####Slave info
    slave = {}
    slaveimg = []
    slaveimg_list = []
    slaveins = ''
     #all files in slave date
    if slavetime is None:
        slavefiles = glob.glob(rawdir + '/ASA_IM*' + slavedate + '*.N1')
        slaveimg_list = list(map(lambda x: os.path.basename(x), slavefiles))
    #defined time list
    else:
        for i, v in enumerate(slavetime):
            tempfile = glob.glob(rawdir + '/ASA_IM*' + slavedate +'*' + v + '*' + '.N1')[0]
            if not os.path.exists(tempfile):
                print(tempfile, " cannot be found")
                sys.exit()
            slaveimg_list.append(os.path.basename(tempfile))
    ###make it shorter
    slaveimg = list(map(lambda x: '$RawDir$/' + x, slaveimg_list))
    #orbit file(only check date)
    date_slave = date(int(slavedate[0:4]), int(slavedate[4:6]), int(slavedate[6:8]))
    ##dt = timedelta(days=1)
    slave_orbd1 = date_slave - dt
    slave_orbd2 = date_slave + dt
    str_sorbd1 = slave_orbd1.strftime("%Y%m%d")
    str_sorbd2 = slave_orbd2.strftime("%Y%m%d")
    slaveorb = glob.glob(Orb_dir + '/DOR_*' + str_sorbd1 + '*' + str_sorbd2 + '*')[0]
    if not os.path.exists(slaveorb):
        print(slaveorb, " cannot be found")
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
        if date_d1 > date_slave or date_d2 < date_slave:
            continue
        elif date_d1 <= date_slave and date_d2 >= date_slave:
            slaveins = Ins_dir + '/' + v
        else:
            print("error to search slave instrument file")
            sys.exit()
     #in case no instrument file found

    slave['IMAGEFILE']      =       slaveimg      #Can be a string returned by another function
    slave['ORBITFILE']      =       slaveorb      #Can be a string returned by another function
    slave['INSTRUMENTFILE'] =       slaveins      #Can be a string returned by another function
    slave['output']         =      'slave.raw'    #Can parse file names and use date

    #####Set sub-component
    ####Nested dictionaries become nested components
    insar['RawDir'] = xml.Constant(os.path.abspath(rawdir))
    insar['master'] = master
    insar['slave'] = slave

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
    insarApp_create_EnviSAT.py -d rawdir -m masterdate mastertimelist -s slavedate slavetimelist -dem demfile -o outdir
    '''

#    if len(sys.argv) == 1:
#        print("insarApp_create_EnviSAT_mlt.py -d rawdir -m masterdate mastertimelist -s slavedate slavetimelist -dem demfile -o outdir")
#        sys.exit()
#    if len(sys.argv) > 1:
    inps = cmdLineParse()
    if inps.rawdir is None:
        rawdir = Data_dir
    else:
        rawdir = inps.rawdir

    master_date = inps.master[0]
    if len(inps.master) == 1:
        master_timelist = None
    elif len(inps.master) == 2:
        master_timelist_str = inps.master[1]
        master_timelist = master_timelist_str.split(',')

    slave_date = inps.slave[0]
    if len(inps.slave) == 1:
        slave_timelist = None
    elif len(inps.slave) == 2:
        slave_timelist_str = inps.slave[1]
        slave_timelist = slave_timelist_str.split(',')

    demfile = inps.dem
    int_dir = inps.out

    ####Example where no DEM is provided in the input file.
    EnviSat_insarapp_xml_generator(os.path.abspath(rawdir), master_date, slave_date, master_timelist, slave_timelist, demfile, outdir= os.path.abspath(int_dir))
