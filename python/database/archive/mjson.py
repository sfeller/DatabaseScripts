#!/usr/bin/python
# file.py
# 
# AWARE database file interface function
#
# Based on code developed by Sally Gewalt
# Modified by Steve Feller on 11/8/12
# Released on:
import os
import argparse
import json

############################################################
# mosaic_json_file()
#
# Class for json file related i/o
############################################################
class mosaic_json_file():
  path = None                               #path to file
  name = None                               #file name
  data = None                               #data list

  #Create new json file
  def writeFile( self, destDir, destName):
    print "destDir:"+destDir+" destName:"+destName

#Read

#Write

#Validate
############################################################
# main
# 
# Command line function for interfacing with python data 
############################################################
def main():
  # parse command line arguments
  parser = argparse.ArgumentParser(description='AWARE json file parser')

  parser.add_argument('-v', action='store_const', dest='verbose', const='True', help='verbose output')
  parser.add_argument('-c', action='store_const', dest='create', const='True', help='create new JSON file')
  parser.add_argument('-p', action='store_const', dest='printDict', const='True', help='print contents of JSON file')
  parser.add_argument('--verify', action='store_const', dest='verify', const='True', help='print contents of JSON file')
  parser.add_argument('filename', nargs='+', help='filename')

  args.parser.parse_args()

  #Create class to represent file
  mjf = mosaic_json_file()

  #open specified file
  if args.create:
    print "Creating new file:",args.filename[0],"\n"
    if not mjf.name_new_mjfile(args.filename[0],True):
      print "Unable to create file ",args.filename[0],"\n"
      sys.exit(-1)
  else:
    if not mjf.open_existing_mjfile(args.filename[0]):
      print "Unable to open file ",args.filename[0],"\n"
      sys.exit(-1)


  
  jfile.createFile('Path','File')

  

############################################################
# Namespace validation
############################################################
if __name__ == "__main__":
  main()

