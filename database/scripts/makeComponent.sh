#!/bin/bash
#
# Dumb interface to generate json files for a part from the component level
# created by: Steve Feller
if [ $# -lt 3 ]
then 
   echo "Must add components in this order"
   echo "./makeComponents type PN ver Name OriginalName Description"
   exit 0
fi

filepath="$1/$2/$3"
filename="$1$2$3.json"

#create directory
mkdir -p $filepath

echo "{" >> $filepath/$filename
echo "   \"id\":\"$1$2$3\"," >> $filepath/$filename
echo "   \"Name\":\"$4\"," >> $filepath/$filename
echo "   \"Original Name\":\"$5\"," >> $filepath/$filename
echo "   \"Description\":\"$6\"" >> $filepath/$filename
echo "}" >> $filepath/$filename

