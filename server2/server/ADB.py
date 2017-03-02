#!/usr/bin/python
"""
# ADB.py
#
# Functions to manage the Aqeuti database interface
#
# This file is used to merge a heirarchy of json files used to track AWARE 
# Imaging System.
#
# Created by: Steve Feller on 11/8/2012
# Release Date:
#
# Modified:
#    1/22/2014 - Steve Feller - Added file system interface support
#    2/9/2014  - Steve Feller - Added support for AWS
# versions: 0.2
#
# Functions:
#    generate(path)  - function to generate a dictionary of 
#                      the json data using the given path as
#                      the root.
#    writeDict(dest) - function to write the current dictionary
#                      to the specified file
#    query(key)      - function to get a list of all values for the given key
#    findKeys(value) - function to find a key that matches a given value
#
#    genDict(path)   - recursive function that step through
#                      subdirectories of the given path and 
#                      aggregates data into a single dictionary
#                      that is returned. 
#
#                       Any data that needs to be adjusted in handled within
#                     this function.
#
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
"""
import os
import argparse
import json
import datetime

#custom files
import AJSON                                #JSON file interface functions
import MDB                                  #mongodb database interface class
import AWS                                  #amazon web services interface

from bson.objectid import ObjectId

############################################################
# Global variables
############################################################
VERBOSE = 0                                 #Debug level

"""
############################################################
# stringList( dbase)
#
# Function to generate a list of strings that show all fields 
# in a database. 
############################################################
"""
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

"""
############################################################
# findKeys
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
#
# sdf - I'm sure there's a better way
############################################################
"""
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

"""
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
"""
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

"""
############################################################
# insert 
#
# Function that inserts the contents of a dictionary into the specified
# database. The collection type must be specified in the dictionary 
# and must be one listed below. The collection name is a the plural
# fo the type (i.e. component => components). This function assumes
# all json files have an unique id.
#
# Supported types:
#   dataset - dataset of raw images saved from camera
#   composite - stitched image for display
#   part      - part for component assembly
#   component - specific components in the system
#   model     - image formation model used
#   
# Inputs:
#   record - dictionary to add to the database
#  
# Returns (dictionary):
#   "rc" - return code
#           1 = success
#          -1 = No type field found
#          -2 = Unknown type
#          -3 = Record exists
#
# Comments:
#   
############################################################
"""
def insert(mdb, node ):
   global VERBOSE

   #add node to database
   if VERBOSE > 0:
      print "Inserting:"+str(node)

   collection = getType( node )
   if isinstance( collection, int):
      if VERBOSE > 1:
         print "Type not defined or present in "+obj
      return -1

   #make sure record does not currently exist in dictionary
   q={"id":node["id"]}
   if mdb.query(collection, q):
      if VERBOSE > 0:
         print "Record Exists in "+collection+":"+str(node["id"])
      return -3

   #############################################
   #Correct any node parameters based on verions
   #############################################
   if node["version"] == "1.1":
      if VERBOSE > 0:
         print "Correcting version 1.1"

      node["version"]=1.1
      if VERBOSE > 0:
         print "Version:"+str(node["version"])

      try:
         node["width"]=int(node[width])
      except:
         node["width"] = 0 
      if VERBOSE > 0:
         print "Width:"+str(node["width"])

      try:
         node["height"]=int(node[height])
      except:
         node["height"] = 0 
      if VERBOSE > 0:
         print "Height:"+str(node["height"])



   #Record found. Let's insert
   if VERBOSE > 1:
         print "Record "+str(node["id"])+": is ready to insert in "+collection

   #remove type key from dictionary
   del node["type"]

   #insert new data and return
   mdb.insert(collection, node)

   return 1


"""
############################################################
# recurse
#
# Function that recursively adds JSON files from 
# a given root-level path.
#
# Inputs
#   - dbase   - name of database to reference
#   - path    - initial path to start processing
#   - command - what function to perform (currently only insert is implemented)
############################################################
"""
def recurse(mdb, path, command):
   #count number of valid records added
   count = 0

   #check if valid path (need more debugging)
   if path[-1] == '/':
      dirname=os.path.basename(path[:-1])
   else:
      dirname=os.path.basename(path)
      path=path+'/'

   #######################################
   # Check if JSON file exists. If it exists
   # insert into the database
   #######################################
   for files in os.listdir(path):
      if files.endswith(".json"):
         jname=path+files

         if VERBOSE > 1:
            print "JSON Filename:",jname

         if command == "insert":
            node = AJSON.readJson( jname )
            if isinstance( node, int ):
               if VERBOSE > 0:
                  print "Unable to read record"
               return -1;
   
            rc = insert(mdb, jname) 
        
            if rc > 1:
               count = count + 1

   #######################################
   # Walk through subdirectories to ensure we get all files
   #######################################
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

      #recursively call this function. zoom and tiles indicate zoomify and
      #krpano heirarchical images.
      if not "zoom" in path and not "tiles" in path:
         rc = recurse(mdb, cpath, command)

   return count


"""
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
#
# Notes:
#   sdf - need to improve argument parsing (no inputs variable)
#   sdf - need to add support for server/port
#   sdf - need to add error checking
############################################################
"""
def writeDict(dbase, dest):
  rc = AJSON.writeJson(dest, dbase, True)
  return rc

"""
############################################################
# updateAWS( dbase, bucket)
#
# Function that get list of AWS objects in a given bucket and
# adds JSON files to library
#
# Inputs: 
#    mdb    - database class
#    aws    - Amazon web services class
#    bucket - name of bucket to write to 
############################################################
"""
def updateAWS( mdb, aws, bucket ):
   global VERBOSE 

   count=0

   #Get list of buckets from AWS
   objList = aws.getObjectList( bucket )
   
   if isinstance( objList, int):
      if VERBOSE  > 0:
         print "ADB::upateAWS: Failed on getObjectList with code: "+str(objList)+". Please verify bucket name"
      return -1

   #Loop through list and process all JSON files
   for obj in objList:
      if VERBOSE > 1:
         print "Updating Object: "+str(obj)

      #If Jsonfile, process
      if "json" in str(obj): 
         if VERBOSE > 1:
            print "Getting JSON object from bucket"
         node = aws.getJson( obj )

         try:
            #convert file received from AWS into a python dictionary
            node = eval(node)

            #Map output file to the given directory
            path=node["outputFiles"]
            for key in path:
#               name="https://s3.amazonaws.com/"+obj.name+"/"+node["outputFiles"][key]
	
               name = os.path.dirname(obj.name);
               name="https://s3.amazonaws.com/"+bucket+"/"+name
#               name=name.replace('.json','')

               #strip JSON
               node["outputFiles"][key]=name

            #Insert record into database
            if VERBOSE > 1:
               print "Inserting node into database"
            rc = insert( mdb, node)
            if rc > 0:
               count = count +1
      
         except:
            print "Error in JSON file: "+str(obj)

   return count
   
"""
############################################################
# getType (node)
#
# Function that reads the type field in a node and determines if 
# it is valid
#
# Inputs: 
#    dbase - 
############################################################
"""
def getType( node ):
   global VERBOSE 

   #Check if type is known
   if node["type"]=="dataset":
      return "datasets"
   elif node["type"]=="composite":
       return "composites"
   elif node["type"]=="model":
       return "models"
   elif node["type"]=="part":
       return "parts"
   elif node["type"]=="component":
       return "components"
   else:
      if VERBOSE > 0:
         print "Type not currently supported"
         return -2



"""
############################################################
# Main function
############################################################
"""
def main(): 
   global VERBOSE
   global collection

   #default access info
   awsAccessKey = 'AKIAJICPBE3SSHW5SR7A'
   awsSecretKey = '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'
   awsBucket    = 'aqueti.data'
  
   #parse inputs
   # parse command line arguments
   parser = argparse.ArgumentParser(description='AWARE Database Script')

   parser.add_argument('-v', action='store_const', dest='VERBOSE', const='True', help='VERBOSE output')
   parser.add_argument('-vv', action='store_const', dest='VERBOSE2', const='True', help='VERBOSE output')
   parser.add_argument('-p', action='store_const', dest='printout', const='True', help='print contents of JSON file')
   parser.add_argument('-d', action='store', dest='path', help='path to data')
   parser.add_argument('-b', action='store', dest='bucket', help='S3 Bucket with data')
   parser.add_argument('-a', action='store', dest='aws_access', help='AWS access code')
   parser.add_argument('-s', action='store', dest='aws_secret', help='path to data')
   parser.add_argument('-f', action='store', dest='fname', help='filename to insert')
   parser.add_argument('-i', action='store_const', dest='insert', const='True', help='Add records to the given dictionary.')
   parser.add_argument('-r', action='store_const', dest='recurse', const='True', help='recursively add JSON files to the dictionary')
   parser.add_argument('-u', action='store_const', dest='update', const='True', help='update records')
   parser.add_argument('-c', action='store', dest='collection', help='collection (table) to use')
   parser.add_argument('dbase', help='database name')

   args=parser.parse_args()

   #set VERBOSE flag as requested
   if args.VERBOSE:
      VERBOSE=1
  
   if args.VERBOSE2:
      VERBOSE=2
      print "VERBOSE=2"

   #extract relevant parameters
   if VERBOSE > 1:
      print "Using database "+args.dbase


   ##################################################
   # connect to database and AWS server (if needed)
   ##################################################
   #connect to database
   mdb=MDB.MDB()
   if VERBOSE > 1:
      print "Connecting to mongodb: "+args.dbase
   try:
      rc = mdb.connect(args.dbase)
   except:
      print "MDB: Unable to connect to database: "+args.dbase
      return -1

   if args.aws_access:
      awsAccessKey = args.aws_access

   if args.aws_secret:
      awsSecretKey = arts.aws_secret

   if args.bucket:
      awsBucket = args.bucket

   # Connect to AWS class
   #sdf - need to make this optional
   aws=AWS.AWS()
   aws.setVerbose( VERBOSE );

   if VERBOSE > 1:
      print "Connecting to AWS: "+awsAccessKey+"/"+awsSecretKey
   try:
      aws.connect( awsAccessKey, awsSecretKey )
   except:
      print "Unable to connect to AWS. Please check inputs"
      return -1

   #Update specified database with the appropriate bucket
   if args.update:
      #ensure bucket and dbase are defined
      if awsBucket:
         if VERBOSE > 1:
            print "Updating database with bucket "+awsBucket
         rc = updateAWS(mdb, aws, awsBucket )

         print str(rc)+" records added to the database"

         if VERBOSE > 0:
            if rc > 0:
               print "ADB::main: Database updated successfully"
               return 1;
            else:
               print "ADB: Unable to update database. Return code:"+rc
               return -1;
      else:
         print "Unable to update. The database bucket name is not defined"
         return -2
 
      return 1


   #sdf - needs to be checked
   #if args.host != "" and args.port != -1:
   #   mdb = MDB(args.dbase, args.host, args.port)
   #else:
   #   mdb = MDB(args.dbase)
   if args.list_objects:
      if args.bucket == "ALL":
         aws.listBuckets()
      else:
         aws.listObjects( args.bucket )
#      bucket = conn.get_bucket('aqueti.data')
#      for key in bucket.list():
#         print key.name.encode('utf-8')

   #We are inserting records. Check if recursing directories or not
   if args.insert:
      if args.fname:
         node = AJSON.readJson( args.fname)
         if isinstance( node, int ):
            if VERBOSE > 0:
               print "Unable to read record"
            return -1;
   

         rc = insert(str(args.dbase), str(args.fname))
     
      elif args.path:
         if args.recurse:
            recurse(args.dbase, str(args.path), "insert")
   else:
      print "Currently only insert capability is supported"   

"""
############################################################
#Function to validate peformance
############################################################
"""
if __name__ == '__main__':
  main()

