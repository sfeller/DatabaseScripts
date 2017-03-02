#!/bin/bash
############################################################
# Genrate KRPano tiles
############################################################
home=`pwd`
cd /home/ubuntu/krpano
./tileImage.sh $home/$1
cd $home

############################################################
# Add to s3 server
############################################################
#remove non krpano data
fileList=`ls composites |grep jpg`
for f in $fileList; 
do
   rm composites/$f
done

fileList=`ls composites |grep tif`
for f in $fileList; 
do
   rm composites/$f
done

#find all index.html files. These get replaced with the template
indexList=`find composites |grep index`
for f in $indexList;
do
   path=$(dirname ${f})
   cp ~/template/* $path
done

#upload to the amazon server
echo copying data to S3
sudo s3cmd --acl-public --recursive put composites/* s3://aqueti.data/composites/ 

############################################################
# Delete data on success
############################################################
sudo rm -Rf /home/ubuntu/server/composites
mkdir /home/ubuntu/server/composites
chmod a+rw /home/ubuntu/server/composites
