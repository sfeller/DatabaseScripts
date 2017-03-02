#!/usr/bin/python
# genDBase.py
#
# AWARE Parts Database Generator.
#
# This file is used to merge a heirarchy of json files used to track AWARE 
# Imaging System.
#
# Functions:
#
# Developed by: Steve Feller on 11/8/2012
# Release Date:
# versions: 0.1
#############################################################
import os
import argparse
import json
import datetime

#custom files
import Afile
#import Adict

############################################################
# Generally useful functions
############################################################
# jsonPrint
#
# Function to print a dictionary in a pretty JSON format
############################################################
def jsonPrint(dbase):
  print json.dumps(dbase, indent=4, sort_keys=False)



############################################################
# Class Definitions
############################################################
# AWAREDbase
# 
# Class to manage an AWARE database dictionary
#
# Functions:
#  "Public"
#    generate(path) - function to generate a dictionary of 
#                     the json data using the given path as
#                     the root.
#    writeDict(dest) - function to write the current dictionary
#                     to the specified file
#    query(key) - function to get a list of all values for the given key
#    findKeys(value) - function to find a key that matches a given value
#
#  "Internal"
#    genDict(path)  - recursive function that step through
#                     subdirectories of the given path and 
#                     aggregates data into a single dictionary
#                     that is returned.
#    genQuery - recursive function that peforms query for a given key value.
#    genKeys - recursive function to find keys for a given value
#
# Proposed functions:
#   writeDBase - exports current dictionary to the the JSON file heirarchy
#   query
############################################################
class AWAREDBase:
  #global class variables
  VERBOSE = 0                     #DEBUG level
  root=None                       #root directory of tree
  dbase={}                        #database

  def stringList(self, ldbase):
    files=list()
    
    #iterate through all keys
    for k, v in ldbase.iteritems():
      
      #iterate query through all keys
      if type(v) is dict:
        for file in self.stringList(v):
          files.append(k+"/"+file)

      else:
        files.append(str(k)+"/"+v)

    return files




  ############################################################
  # findKeys(value)
  #
  # External call to query find all keys that match a given value
  #
  # Inputs:
  #   value - value to find a key for
  #
  # Returns:
  #   result - list of keys
  #
  # Notes: Eventually should include wildcards lookup options
  ############################################################
  def findKeys( self, value):
    #call recursive iterator
    result = self.genKeys(self.dbase,value)
   
    if self.VERBOSE > 1:
      jsonPrint(result)
    
    return result
  
  ############################################################
  # genKeys
  #
  # Function that recursively walks through dictionary and
  # returns keys the given value
  #
  # Inputs:
  #   ldbase - database to query (local to function to be iterative)
  #   val - value to query on
  #
  # Returns:
  #   result - dictionary of all subsequent instances of value
  ############################################################
  def genKeys(self, ldbase, val):
    result={}
    
    #For each dictionary element, see if it has children
    for k, v in ldbase.iteritems():
      #   if self.VERBOSE > 1:
      #print "genQuery: key: ",k," Value:",v
      
      #iterate query through all keys
      if type(v) is dict:
        value=self.genKeys(v, val)
        
        if len(value) > 0:
          #print "Result1:",k," value:",v
          result[k]=value
      
      if v == val:
        #print "Result:",k," value:",v
        result[k]=v
      
      if self.VERBOSE > 1:
        print "genKey:result: ",result ," found", v," key:",k
      
      if self.VERBOSE > 1:
        print "genKey: Result: ",result
    
    return result

  
  ############################################################
  # query(key)
  #
  # External call to query a value for a given key.
  #
  # Inputs:
  #   key - key value to search for
  #
  # Returns:
  #   result - list of values.
  #
  # Notes: Eventually should include wildcards lookup options
  #
  ############################################################
  def query( self, key):
  
    #call recursive iterator
    result = self.genQuery(self.dbase,key)
  
    if self.VERBOSE > 0:
      jsonPrint(result)

    return result
  
  ############################################################
  # genQuery
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
  def genQuery(self, ldbase, key):
    result={}
    
    #For each dictionary element, see if it has children
    for k, v in ldbase.iteritems():
      #   if self.VERBOSE > 1:
      #print "genQuery: key: ",k," Value:",v

      #iterate query through all keys
      if type(v) is dict:
        value=self.genQuery(v, key)

        if len(value) > 0:
          #print "Result1:",k," value:",v
          result[k]=value

      if k == key:
        #print "Result:",k," value:",v
        result[k]=v
      
      if self.VERBOSE > 1:
        print "genQuery:result: ",result ," found", k," Value:",v
    
      if self.VERBOSE > 1:
        print "genQuery: Result: ",result
    
    return result

  ############################################################
  # generate
  #
  # External call to generate a dictionary from the specified
  # root level path
  #
  # Inputs:
  #   root - base directory to generate database from
  ############################################################
  def generate(self,path):
    #get current time
    dt = datetime.datetime.now()

    #generate unique ID from timestamp (onl
    self.dbase["id"] = dt.strftime("%Y%m%d%H%m%S")+str(dt.microsecond)
    
    #set date and time par
    self.dbase["date"]=dt.strftime("%Y-%m-%d")
    self.dbase["time"]=dt.strftime("%H:%m.%S")

    if self.VERBOSE > 1:
      print "Date: ",str(dt)
   
    #check if valid path (need more debugging)
    if path[-1] == '/':
      dirname=os.path.basename(path[:-1])
    else:
      dirname=os.path.basename(path)
  
    self.root = path
    ret = self.genDict(path)
    
    if ret["rc"] == 1:
      self.dbase[dirname]=ret["data"]


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
  def genDict(self,path):
    
    #check if valid path (need more debugging)
    if path[-1] == '/':
      dirname=os.path.basename(path[:-1])
    else:
      dirname=os.path.basename(path)
      path=path+'/'

    #generate name of local json file
    jname=path+dirname+'.json'

    if self.VERBOSE > 1:
      print "Jname:",jname

    #Create dictionary with local data
    #if reads correctly (rc=1) add json info to current dictionary. If not,
    #stop iterative process
    retval = Afile.readJson(jname)
    if self.VERBOSE > 1:
      print "Name:",jname," =>",retval
    if retval["rc"] == 1:
      node = retval["data"]
    else:
      return {"rc":"0","data":{}}

    #Walk through subdirectories and recursively pull dictionaries from their content
    #get list of subdirs
    pathList = os.walk(path).next()[1]
   
    if self.VERBOSE > 1:
      print "Pathlist: ",pathList

    #recurse through each to get a list of children
    for child in pathList:
      #generate pathname for child and do recursive call
      cpath = path+child
      cpath.strip()
      if self.VERBOSE > 1:
        print  "ChildPath: ",cpath

      #recursively call this function
      db = self.genDict(cpath)

      node[child]=db["data"]
 
    return {"rc":1,"data":node}

  ############################################################
  # getValues
  #
  # Recursive function to generate a list of values for a given
  # key. Returns a list of keys and values. (Eventually may 
  # extend to include wildcards and range parameters)
  #
  # Inputs:
  #   Key  - Key to query
  # Returns:
  #   Solution - list of values
  ############################################################
  def getValue(self,key):
    if self.VERBOSE > 1:
      print "getValue: key: ", key
      
      re
    return self.dbase[key]

  ############################################################
  # writeDict
  #
  # Function to write out the dictionary to a specified file. 
  #
  # Inputs:
  #   path - directory path to start generating data
  #  
  # Returns (dictionary):
  #   "rc" - return code matches Afile.writeJson
  ############################################################
  def writeDict(self, dest):
    rc = Afile.writeJson(dest, self.dbase)
    return rc

def main(): 
  #parse inputs
  # parse command line arguments
  parser = argparse.ArgumentParser(description='AWARE json file parser')

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
  ADB = AWAREDBase()

  if args.VERBOSE:
    ADB.VERBOSE=1
  
  if args.VERBOSE2:
    ADB.VERBOSE=2

  ADB.generate(args.filename[0])
 
  if args.printout:
    print json.dumps(ADB.dbase, indent=4, sort_keys=True)

  #If query, let's look
  if args.query:
    print "Query: ",args.query
    res = ADB.query(args.query)
    jsonPrint(res)

  #If value query, let's look
  if args.qval:
    print "findKeys: ",args.qval
    res = ADB.findKeys(args.qval)
    jsonPrint(res)
    fileList=ADB.stringList(res)

    print "Itemlist:"
    for item in fileList:
     print item

  #write output if requested
  if args.outfile:
    ADB.writeDict(args.outfile)
 
  if ADB.VERBOSE > 1:
    print "Complete!"

#Function to validate peformance
if __name__ == '__main__':
  main()

