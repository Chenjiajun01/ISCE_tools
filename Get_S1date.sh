#!/bin/bash
##unzip Sentinel zip and generate conversion between filename ID and date
#Created by J. Chen @NCL on 2017-04-27
#
##
if [ $# -lt 1 ]; then
    echo "Usage: Get_S1date.sh <zipdir> [dateID.info]"
    exit 1
fi
zipdir=$1
if [ $# -eq 2 ]; then
    dateIdFile=$2
else
    dateIdFile=dateID.info
fi

if [ ! -d ${zipdir} ]; then
    echo "Cannot find ${zipdir}"
    exit 1
fi


# get date from workreport file
cd ${zipdir}
if [ -f $dateIdFile ]; then
    rm -f $dateIdFile
fi
touch $dateIdFile
for folder in ./S1*.zip; do
    if [ -f $folder ]; then
        folder_base=`basename $folder`
        date=`echo | awk '{print substr("'${folder_base}'",18,8)}'`
        # print file orbit ID and date to file
        echo "${date}" >> temp.info
    fi
done
# remove the same lines
#sort -n $dateIdFile | uniq
sort -n temp.info | awk '{if($0!=line)print; line=$0}' > $dateIdFile
rm -f temp.info
echo "create datelist file in ${zipdir}"
echo "Finished!"
