#!/usr/bin/env python

#fuction:     download S1A data from cart
#author:	  J. Chen
#created:	  10/09/2016
#updated:         11/10/2017, for new product.meta4 file which add size

import os,sys
import argparse
import xml.etree.ElementTree as ET

#global variable
USERNAME = '' 
PASSWORD = ''

def cmdLineParse():
    '''
    Command Line Parser.
    '''
    parser = argparse.ArgumentParser(description='Download S1A data from cart file'
    '''

Example:

download_S1.py -i input.xml 

''')
    parser.add_argument('-i','--input', type=str, required=True, help='Input cart metadata file', dest='infile')
    parser.add_argument('-u','--username', type=str, help='user name in ESAR Hub Website', dest='user')
    parser.add_argument('-p','--password', type=str, help='password in ESAR Hub Website', dest='password')
    parser.add_argument('-d','--outdir',type=str, default=None, help='Download data folder', dest='outdir')

    inps = parser.parse_args()
    if (not inps.infile):
        print('User did not provide input file')
        sys.exit(0)

    return inps
def XmlRender(metafile, user, passw, outdir=None):

#	metaTree = ET.iterparse(sys.argv[1])
    metaTree = ET.iterparse(metafile)
    count = 0
    for event, files in metaTree:
        if event =='end':
            if files.tag == 'file':
                file_name = os.path.join(outdir,files.attrib['name'])
                file_url0 = files[2].text
                file_url = file_url0[0:-7]
                wget_str1 = 'wget --no-check-certificate --user=' + user + ' --password=' + passw + ' \"'
                wget_str = wget_str1 + file_url + "/\$value\" -O " + file_name
                print(wget_str)
                os.system(wget_str)
            #	print(file_name)
            #	print(elem[1].text)
                count += 1
                print(count, " files downloaded!")

if __name__ == '__main__':
    '''
    Makes the script executable
    '''
    inps = cmdLineParse()
    if inps.infile.endswith('.meta4'):
        inXmlFile = inps.infile
    else:
        exec("No metadata file input")
    if inps.outdir is None:
        outFolder = './'
    else:
        outFolder = inps.outdir
    if inps.user is None:
        if USERNAME == "":
            print("User name required")
        else:
            user = USERNAME
    else:
        user = inps.user
    if inps.password is None:
        if PASSWORD == "":
            print("password required")
        else:
            password = PASSWORD
    else:
        password = inps.password


    print('Output folder : {0}'.format(outFolder))
    XmlRender(inXmlFile, user, password, outFolder)
