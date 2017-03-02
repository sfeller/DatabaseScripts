#!/usr/bin/python
# ADB.py
#
# Functions to manage an AWARE database dictionary
#
# This file is used to merge a heirarchy of json files used to track AWARE 
# Imaging System.
#
# Developed by: Steve Feller on 11/8/2012
# Release Date:
# versions: 0.1
#
# Functions:
#    generate(path) - function to generate a dictionary of 
#                     the json data using the given path as
#                     the root.
#    writeDict(dest) - function to write the current dictionary
#                     to the specified file
#    query(key) - function to get a list of all values for the given key
#    findKeys(value) - function to find a key that matches a given value
#
#    genDict(path)  - recursive function that step through
#                     subdirectories of the given path and 
#                     aggregates data into a single dictionary
#                     that is returned.
#    findKeys - recursive function to find keys for a given value
#    stringList(dbase) - iterative generate a list of strings for each value
#                     for each value in a dictionary. 
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
# stringList( dbase)
#
# Function to generate a list of strings that show all fields 
# in a database. 
############################################################
def stringList(dbase):
  files=list()
  
  #iterate through all keys
  for k, v in dbase.iteritems():
    
    #iterate query through all keys
    if type(v) is dict:
      for f in stringList(v):
        files.append(k+"/"+f)

    else:
      files.append(str(k)+":"+v)

  return files

############################################################
# genKeys
#
# Function that recursively walks through dictionary and
# returns keys the given value
#
# Inputs:
#   dbase - database to query (local to function to be iterative)
#   val - value to query on
#
# Returns:
#   result - dictionary of all subsequent instances of value
############################################################
def findKeys(dbase, val):
  global VERBOSE
  result={}
  
  #For each dictionary element, see if it has children
  for k, v in dbase.iteritems():
    if VERBOSE > 1:
      print "ADB.findKeys: Key: ",k," Value:",v
    
    #iterate query through all keys
    if type(v) is dict:
      value=findKeys(v, val)
      
      if len(value) > 0:
        #print "Result1:",k," value:",v
        result[k]=value
    
    if v == val:
      #print "Result:",k," value:",v
      result[k]=v
    
    if VERBOSE > 1:
      print "ADB.findKeys:result: ",result ," found", v," key:",k
  
  return result

############################################################
# query
#
# Function that recursively walks through dictionary and
# returns sub values that contain the given key
#
# Inputs:
#   ldbase - database to query (local to function to be iterative)
#   key - key to query on
#
# Returns:
#   result - dictionary of all subsequent instances of value
#
# Notes: Eventually should include wildcards lookup options
#
############################################################
def query(dbase, key):
  global VERBOSE
  result={}
  
  #For each dictionary element, see if it has children
  for k, v in dbase.iteritems():
    if VERBOSE > 1:
      print "ADB.query: key: ",k," Value:",v

    #iterate query through all keys
    if type(v) is dict:
      value=query(v, key)

      if len(value) > 0:
        #print "Result1:",k," value:",v
        result[k]=value

    if k == key:
      #print "Result:",k," value:",v
      result[k]=v
    
    if VERBOSE > 1:
      print "ADB.query:result: ",result ," found", k," Value:",v
  
  return result

############################################################
# generate
#
# External call to generate a dictionary from the specified
# root level path. Adds date/time header information to 
# toplevel of dictionary
#
# Inputs:
#   path - base directory to generate database from
# 
# Returns:
#   dbase - resulting database
############################################################
def generate(path):
  dbase = {}
  global VERBOSE

  #get current time
  dt = datetime.datetime.now()

  #generate unique ID from timestamp (onl
  dbase["id"] = dt.strftime("%Y%m%d%H%m%S")+str(dt.microsecond)
  
  #set date and time par
  dbase["date"]=dt.strftime("%Y-%m-%d")
  dbase["time"]=dt.strftime("%H:%m.%S")

  #check if valid path (need more debugging)
  if path[-1] == '/':
    dirname=os.path.basename(path[:-1])
  else:
    dirname=os.path.basename(path)

  ret = genDict(dbase, path)
  
  if ret["rc"] == 1:
    dbase[dirname]=ret["data"]

  if VERBOSE > 1:
    print "ADB.generate dbase:",dbase

  return dbase

############################################################
# genDict
#
# Function that recursively generates a single dictionary from 
# JSON files starting at the specified root level. This allows 
# the creation of dictionaries that reference a subset of the
# database
#
# Inputs:
#   path - directory path to start generating data
#  
# Returns (dictionary):
#   "rc" - return code
#          1 = success
#          0 = directoy does not have json file 
#   "data" - dictionary of data from current and sub directories
############################################################
def genDict(dbase, path):
  
  #check if valid path (need more debugging)
  if path[-1] == '/':
    dirname=os.path.basename(path[:-1])
  else:
    dirname=os.path.basename(path)
    path=path+'/'

  #generate name of local json file
  jname=path+dirname+'.json'

  if VERBOSE > 1:
    print "Jname:",jname

  #Create dictionary with local data
  #if reads correctly (rc=1) add json info to current dictionary. If not,
  #stop iterative process
  retval = AJSON.readJson(jname)
  if VERBOSE > 1:
    print "Name:",jname," =>",retval
  if retval["rc"] == 1:
    node = retval["data"]
  else:
    return {"rc":"0","data":{}}

  #Walk through subdirectories and recursively pull dictionaries from their content
  #get list of subdirs
  pathList = os.walk(path).next()[1]
 
  if VERBOSE > 1:
    print "Pathlist: ",pathList

  #recurse through each to get a list of children
  for child in pathList:
    #generate pathname for child and do recursive call
    cpath = path+child
    cpath.strip()
    if VERBOSE > 1:
      print  "ChildPath: ",cpath

    #recursively call this function
    db = genDict(dbase, cpath)

    node[child]=db["data"]
 
  return {"rc":1,"data":node}

############################################################
# writeDict
#
# Function to write out the dictionary to a specified file. 
#
# Inputs:
#   path - directory path to start generating data
#  
# Returns (dictionary):
#   "rc" - return code matches AJSON.writeJson
############################################################
def writeDict(dbase, dest):
  rc = AJSON.writeJson(dest, dbase, True)
  return rc


def main(): 
  global VERBOSE
  #parse inputs
  # parse command line arguments
  parser = argparse.ArgumentParser(description='AWARE Database Script')

  parser.add_argument('-v', action='store_const', dest='VERBOSE', const='True', help='VERBOSE output')
  parser.add_argument('-vv', action='store_const', dest='VERBOSE2', const='True', help='VERBOSE output')
  parser.add_argument('-q', action='store', dest='query', help='find values for specified key')
  parser.add_argument('-k', action='store', dest='qval', help='find keys for specified value')
  parser.add_argument('-p', action='store_const', dest='printout', const='True', help='print contents of JSON file')
#  parser.add_argument('-no-force', action='store_const', dest='noforce', const='True', help='force write JSON file')
  parser.add_argument('-w', action='store_const', dest='write', const='True', help='write JSON file')
  parser.add_argument('-o', action='store', dest='outfile', help='output file')
  parser.add_argument('filename', nargs='+', help='filename')

  args=parser.parse_args()
 

  #set filename
  if args.VERBOSE:
    VERBOSE=1
  
  if args.VERBOSE2:
    VERBOSE=2

  dbase = generate(args.filename[0])
 
  if args.printout:
    print json.dumps(dbase, indent=4, sort_keys=True)

  #If query, let's look
  if args.query:
    print "Query: ",args.query
    res = query(dbase, args.query)
    AJSON.printJson(res)

  #If value query, let's look
  if args.qval:
    print "findKeys: ",args.qval
    res = findKeys(dbase, args.qval)
#    printJson(res)
    fileList=stringList(res)
 
    print "Itemlist:"
    for item in fileList:
     print item

  #write output if requested
  if args.outfile:
    writeDict(dbase, args.outfile)
 
  if VERBOSE > 1:
    print "Complete!"

#Function to validate peformance
if __name__ == '__main__':
  main()

