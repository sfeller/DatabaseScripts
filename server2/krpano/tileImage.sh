#!/bin/bash
if [ "$#" -ne 1 ];
   then echo "Enter filename" 
   exit
fi

echo processing file $1
./krpanotools makepano -config=./templates/flat.config $1
echo $1
