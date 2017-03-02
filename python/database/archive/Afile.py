#!/usr/bin/python
# file.py
# 
# AWARE json file interface code
#
# This file supports JSON file I/O. The output is assumed to
# be a dictionary. It is a base class for the ADBASE application
#
# Functions:
#   Read - read JSON file into a dictionary
#   Write - write dictionary to a JSON file
#
# Based on code developed by Sally Gewalt
# Modified by Steve Feller on 11/8/12
# Released on:
###########################################################
import os
import argparse
import json

VERBOSE=0



#############################################
# readJson
#
# This function reads a json file into the global data dictionary
#
# Inputs: None
# Return Codes:
#    1 Normal exit
#    0 File does not exist
#   -1 Name is not defined
#   -2 File could not be opened
#############################################
def readJson(name):
  #verify that the filename has been set
  if name is None:
    if VERBOSE > 0:
      print "Name not defined"
    return {"rc":-1}

  #if file does not exist, use current database (empty)
  if not os.path.isfile(name):
    if VERBOSE > 1:
      print "readFile: ",name," does not exist, creating empty dictionary"
    return {"rc":0}
  else:
    #open specified filename
    try:
      fptr = open(name)
    except(Exception, IOError), e:
      if VERBOSE > 0:
        print 'readFile: Could not open %s: %s'%(name,e)
      return {"rc":-2} 

    #read data from json file
    data = json.load(fptr)
    
    #close file pointer
    fptr.close();

  return {"rc":1,"data":data}


#############################################
# writeJson
#
# This function reads a json file into the global data dictionary
#
# Inputs: None
# Return Codes:
#    1 Normal exit
#   -1 Name is not defined
#   -2 File exists, no force
#   -3 File could not be opened
#############################################
def writeJson(name, data):
  #verify that the filename has been set
  if name is None:
    if VERBOSE > 0:
      print "write: Name not defined"
    return -1

  if os.path.isfile(name):
    if VERBOSE > 0:
      print "cannot overwrite existing", name
    return -2 
  else:
    try:
      fptr = open(name, "w")
      fptr.write(json.dumps(data, indent=2, sort_keys=True)) # sort or arb order
    except(IOError), e:
      if VERBOSE > 0:
        print 'write: Could not write destination %s: %s'%(json_mfile,e)
      return -3
  return 1




############################################################
# AJfile()
#
# Class for json file related I/O
#
# Functions:
#    Read
#    Write
#
# Debug levels (VERBOSE)
#    0 - no console output
#    1 - major error codes
#    2 - All comments
############################################################
class AJfile:
  #function assumes you pass in a filename
  def __init__(self, filename):
    self.name=filename

  #flags
  VERBOSE=0                                 #debug level
  force = True

  name = None                               #file name
  data = {}                                 #data dictionary



  #############################################
  # read
  #
  # This function reads a json file into the global data dictionary
  #
  # Inputs: None
  # Return Codes:
  #    1 Normal exit
  #    0 File does not exist
  #   -1 Name is not defined
  #   -2 File could not be opened
  #############################################
  def read(self):
    #verify that the filename has been set
    if self.name is None:
      if self.VERBOSE > 0:
        print "Name not defined"
      return -1

    #if file does not exist, use current database (empty)
    if not os.path.isfile(self.name):
      if self.VERBOSE > 1:
        print "readFile: ",self.name," does not exist, creating empty dictionary"
      return 0
    else:
      #open specified filename
      try:
        fptr = open(self.name)
      except(Exception, IOError), e:
        if selfVERBOSE > 0:
          print 'readFile: Could not open %s: %s'%(self.name,e)
        return -2 

      #read data from json file
      self.data = json.load(fptr)
      
      #close file pointer
      fptr.close();

    return 1
    
  #############################################
  # write
  #
  # This function reads a json file into the global data dictionary
  #
  # Inputs: None
  # Return Codes:
  #    1 Normal exit
  #   -1 Name is not defined
  #   -2 File exists, no force
  #   -3 File could not be opened
  #############################################
  def write(self):
    #verify that the filename has been set
    if self.name is None:
      if self.VERBOSE > 0:
        print "write: Name not defined"
      return -1

    if os.path.isfile(self.name) and not self.force:
      if self.VERBOSE > 0:
        print "cannot overwrite existing", self.name
      return -2 
    else:
      try:
        fptr = open(self.name, "w")
        fptr.write(json.dumps(self.data, indent=2, sort_keys=True)) # sort or arb order
      except(IOError), e:
        if self.VERBOSE > 0:
          print 'write: Could not write destination %s: %s'%(self.json_mfile,e)
        return -3
    return 1


############################################################
# main
# 
# Command line function for interfacing with python data 
############################################################
def main():

  # parse command line arguments
  parser = argparse.ArgumentParser(description='AWARE json file parser')

  parser.add_argument('-v', action='store_const', dest='VERBOSE', const='True', help='VERBOSE output')
  parser.add_argument('-vv', action='store_const', dest='VERBOSE2', const='True', help='VERBOSE output')
  parser.add_argument('-p', action='store_const', dest='printout', const='True', help='print contents of JSON file')
  parser.add_argument('-no-force', action='store_const', dest='noforce', const='True', help='force write JSON file')
  parser.add_argument('-w', action='store_const', dest='write', const='True', help='write JSON file')
  parser.add_argument('-o', action='store', dest='outfile', help='output file')
  parser.add_argument('filename', nargs='+', help='filename')

  args=parser.parse_args()

  #Create class to represent file
  mjf = AJfile(args.filename[0])

  #set debug level
  if args.VERBOSE:
    mjf.VERBOSE=1
  if args.VERBOSE2:
    mjf.VERBOSE=2

  #read in file (if it exists)
  iRC = mjf.read()

  #if printout
  if args.printout:
    print json.dumps(mjf.data, indent=4)

  #write file
  if args.write:
    if args.noforce:
      mjf.force = False

    #if outfile set, change name
    if args.outfile:
      mjf.name=args.outfile

    #write file
    mjf.write()


  

############################################################
# Namespace validation
############################################################
if __name__ == "__main__":
  main()

