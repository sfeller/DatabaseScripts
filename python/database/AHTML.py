#!/usr/bin/python
# AHTML.py
#
# Functions to covert a python dictionary to HTML. Useful for :q
#
#
# Developed by: Steve Feller on 11/8/2012
# Release Date:
# versions: 0.1
#
# Functions:
#   genHTML(dbase depth) - function to generate HTML output
#
# Proposed functions:
#   writeDB - exports current dictionary to the the JSON file heirarchy
#
# Notes:
#   - need to add wildcard support to lookup functions (query, findkeys)
############################################################
import os
import argparse
import json
import datetime

#custom files
import AJSON
#import Adict


############################################################
# Global variables
############################################################
VERBOSE = 0                                 #Debug level

############################################################
# genHTML( dbase, depth)
#
# Function to generate a list of strings that show all fields 
# in a database.
#
# Inputs:
#   dbase - dictionary with information
#   depth - tracks recursion depth
############################################################
def genHTML(dbase, depth):
  files=list()
  
  #iterate through all keys
  for k, v in dbase.iteritems():
    
    #iterate query through all keys
    if type(v) is dict:
      for f in genHTML(v, depth-1):
        files.append(k+"/"+f)

    else:
      files.append(str(k)+":"+v)

  return files

#####################################################################
# main - Entry function
#####################################################################

def main(): 
  global VERBOSE
  #parse inputs
  # parse command line arguments
  parser = argparse.ArgumentParser(description='AWARE Database Script')

  parser.add_argument('-v', action='store_const', dest='VERBOSE', const='True', help='VERBOSE output')
  parser.add_argument('-vv', action='store_const', dest='VERBOSE2', const='True', help='VERBOSE output')
  parser.add_argument('-p', action='store_const', dest='printout', const='True', help='print contents in HTML format')
  parser.add_argument('-w', action='store_const', dest='write', const='True', help='write HTML file')
  parser.add_argument('-o', action='store', dest='outfile', help='output file')
  parser.add_argument('filename', nargs='+', help='filename')

  args=parser.parse_args()
 

  #set filename
  if args.VERBOSE:
    VERBOSE=1
  
  if args.VERBOSE2:
    VERBOSE=2

  #Read JSON File
  dbase =AJSON.readJson(filename)

  #Generate table
  htmlBuf=genHTML(dbase, 5)

  #print databse
  if args.printout:
    print htmlBuf



  if VERBOSE > 1:
    print "Complete!"

#Function to validate peformance
if __name__ == '__main__':
  main()

