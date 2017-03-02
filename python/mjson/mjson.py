#!/usr/bin/python
import sys
import argparse
import os
import re
import string
#from configobj import ConfigObj, flatten_errors
#from validate import Validator
import json
import pprint
import collections


VERSION=0.1
VERBOSE=False

# 120202 slg DISP - introduced mjson to edi

SPECFILE = "mosaicspec.ini" 

# see: http://www.doughellmann.com/PyMOTW/json/
# see: http://secretgeek.net/json_3mins.asp
# see: http://simplejson.googlecode.com/svn/tags/simplejson-2.1.1/docs/index.html
DEBUG = 0

class mosaic_json_file() :
  json_mfile = None             # the path to the json file we are talking to
  json_fp = None              # file pointer to the reference json file
  current_dict = None           # the current data
   
  # --------------------------------------------
  def open_existing_mjfile(self, json_filepath):
    if not os.path.isfile(json_filepath):
      print "mjson: Can't open existing file because can\'t find original", json_filepath
      print "mjson cwd:",os.getcwd()
      return -1 
    else: 
      self.json_mfile = json_filepath 
      try:
        json_fp = open(json_filepath)
      except(Exception, IOError), e:
#        print 'mjson: Simply could not open %s: %s'%(json_filepath,e)
        self.clear_mjdata() # make an empty jason file that can be added to 
        return -2 
      try:
        #self.current_dict = json.loads(json_filepath) # loads not liked at all
        self.current_dict = json.load(json_fp)
        print "Current:",self.current_dict
        DEBUG=1
        json_fp.close()
        if DEBUG: print "read:"
        if DEBUG: print json.dumps(self.current_dict, sort_keys=True, indent=2)
      except(Exception, IOError), e:
#        print 'mjson: Could not load json format data from %s: %s'%(json_filepath,e)
        self.clear_mjdata() # make an empty jason file that can be added to 
        return --33 
      return 1

  # ---------------------------------------------
  def name_new_mjfile(self, new_json_filepath, overwrite_ok) :
    # check if filename already exists
    if os.path.isfile(new_json_filepath) and not overwrite_ok:
      print "mjson: Can\'t use filepath name", new_json_filepath, "because it already exists and you did not allow overwrite"
      return 0 
    else:
      self.json_mfile = new_json_filepath
      self.current_dict = {'in':'out'};
      print "current_dict['in']: ", self.current_dict['in']
    return 1 

  # ---------------------------------------------
  def write_mjfile(self, overwrite_ok) :
    if DEBUG: print "wrote:"
    if DEBUG: print json.dumps(self.current_dict, sort_keys=True, indent=2)
    if os.path.isfile(self.json_mfile) and not overwrite_ok:
      print "mjson: overwrite not selected, so cannot write existing", self.json_mfile
      return 0 
    else:
      try:
        json_destfp = open(self.json_mfile, "w")
        json_destfp.write(json.dumps(self.current_dict, indent=2, sort_keys=True)) # sort or arb order
      except(IOError), e:
        print 'mjson: Could not write destination %s: %s'%(self.json_mfile,e)
        return 0 
      return 1

  # ---------------------------------------------
  def json_stringify(self) :
    return(json.dumps(self.current_dict, separators=(',',':'))) # compact encoding

  # ---------------------------------------------
  def json_stringify_pretty(self) :
    return(json.dumps(self.current_dict, indent=4)) # compact encoding

  # ---------------------------------------------
  def filter_strings(self, obj):
    if isinstance(obj, str):
      #print "found a string:",obj
      obj = obj.replace("'","*")  # remove pesky apostrophe
    elif isinstance(obj, unicode):
      # this seems to be found far more than str
      obj = obj.replace("'","*")  # replace pesky apostrophe
    elif isinstance(obj, (list, tuple, set)):
      obj = list(obj)
      for i,v in enumerate(obj):
        obj[i] = self.filter_strings(v)
    elif isinstance(obj, dict):
      for i,v in obj.iteritems():
        obj[i]=self.filter_strings(v)
    else:
      pass
    return obj

  # ---------------------------------------------
  def json_replace_apost(self):
  # call this prior to regular stringify to straighten out problems with apostrophes making whole list disappear
    #print "replacing"
    self.current_dict = self.filter_strings(self.current_dict)

  # ---------------------------------------------
  def json_cleanse_apos_stringify(self):
     s = json.dumps(self.current_dict, separators=(',',':')) # compact encoding
     s = s.replace("'","XXXXXXXXXXX")  # remove pesky apostrophe
     return s

  # ---------------------------------------------
  def clear_mjdata(self) :
    self.current_dict={}
      
  # ---------------------------------------------
  def getKeys(formatString):
    '''formatString is a format string with embedded dictionary keys.
    Return a list containing all the keys from the format string.'''
    print "getting keys"
    keyList = list()
    end = 0
    repetitions = formatString.count('{')
    for i in range(repetitions):
        start = formatString.find('{', end) + 1
        end = formatString.find('}', start)
        key = formatString[start : end]
        keyList.append(key)
    return keyList
  # ---------------------------------------------
  def get(self, *keys) :
  # returns (key_found, value)
    d = self.current_dict
    print "Dict:",d

    for key in keys:
      print "Key: ",key
      if key in d :
        print "Working:"
        d = d[key]
      else: 
        return (0, d)
    return (1, d)

  # ---------------------------------------------
  def set(self, value, *keys) :
    d = self.current_dict
    depth = len(keys)
    dictpath = ""
    print "---final value:",value
    for key in keys:
      
      dictpath = dictpath + str(key) + ":"
      print "depth=",depth, "key=",key

      if key not in d: 
        if depth != 1 :  # we need to be able to traverse whole keys list
          print "key", key, "not in d"
          return 0
        else:
          print "Setting new value for key \'"+dictpath+"\' to "+str(value)
          d[key] = value   
          return 1
      else:
        if depth > 1:
          d = d[key]   
          print "  got next:",d
          depth -= 1
        else:
          if DEBUG: print "Re-setting existing value for key \'"+dictpath+"\' from "+str(d[key])+" to "+str(value)
          d[key] = value   
          return 1
    return 0

  # ---------------------------------------------
  def update(self, update_str):
    u = json.loads(update_str)
    self.current_dict = self.go_update(self.current_dict, u)

  # ---------------------------------------------
  def replace_check(self, update_str):
    try:
      u = json.loads(update_str)
      #self.current_dict = self.go_update(self.current_dict, u)
      start_dict = {}
      test_dict = self.go_update(start_dict, u)
    except(Exception, IOError), e:
      print 'mjson: Could not update json format data'
      return 0 
    self.current_dict = test_dict
    return 1
  
  
  # ---------------------------------------------
  def go_update(self, d, u):
    #http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    # amazing, Alex Martelli
    for k, v in u.iteritems():
       if isinstance(v, collections.Mapping):
         r = self.go_update(d.get(k, {}), v)
         d[k] = r
       else:
         d[k] = u[k]
    return d
   
   # dict1={'level1':{'level2':{'levelA':0,'levelB':1}}}
   # update1={'level1':{'level2':{'levelB':10}}}
   # go_update(dict1, update1)
   # {'level1': {'level2': {'levelB': 10}}}

  # ---------------------------------------------
  def arrayIndexGet(self, keyword, index) :
    # if value is an array
    if keyword in self.current_dict :
      key_available = 1 
      value = self.current_dict[keyword][index]
      #print "value=",value
    else: 
      key_available = 0
      value = None
    return(key_available, value)

  # ---------------------------------------------
  #def plainDump(self, infile) :
  def plainDump(self) :
    for majorkey, subdict in self.current_dict.iteritems():
      print majorkey,":"
      for subkey, value in subdict.iteritems():
        print "  ", subkey, ":", value
    
  # ---------------------------------------------
  def fixKeysWithSpaces(self) :
    # this is tailored to fix the first gen of disp template.
    # So untested on deeper than 1 layer keys and it does not fix the major elements (access,photographer...)
    for majorkey, subdict in self.current_dict.iteritems():
      #print majorkey   # known to be spaceless
      for subkey, value in subdict.iteritems():
        #print "   ", subkey, ":", value
        # if subkey has a spaces, remove, capitialize words (but not 1st), recombine
        if re.search(" ",subkey) :
           s = string.find(subkey, " ")  # first space
           start = subkey[:s]
           rest = string.capwords(subkey[s:])
           l = string.split(rest)
           rest = string.join(l,'')
           subkey2 = start + rest
           # replace subkey with spaceless version 
           del self.current_dict[majorkey][subkey]
           self.current_dict[majorkey][subkey2] = value
    #print "Fix Keys With Spaces: json dict becomes:"
    #self.plainDump()

  # ---------------------------------------------
  def check_mjson_web_content(self):
    # Call to grossly verify mjson provided is useful for web annotations

    #self.current_dict = json.loads(mjson)

    sec = "access"
    item= "json_avail"
    ok, val = self.get(sec,item)
    # was a real json file available or is this a faked up template placeholder
    if not ok:
      return (False, "missing "+ sec +": "+ item +" setting")
    if val != "yes": 
      return (False, "No json chronicle file available")
  
    sec = "access"
    item= "webInclude"
    ok, val = self.get(sec,item)
    if not ok:
      return (False, "missing "+ sec +": "+ item +" setting")
    if val != "yes": 
      return (False, sec +": "+ item +"="+val)
  
    sec = "photographer"
    item = "sectionReady"
    ok, val = self.get(sec,item)
    if not ok:
      return (False, "missing "+ sec +": "+ item +" setting")
    if val != "yes": 
      return (False, sec +": "+ item +"="+val)

    return (ok, "ok")

  # ---------------------------------------------
  def jsonUpdaterReplacer(self, file):
    # routine to fix old json
    if mjf.open_existing_mjfile(file) < 0:
       print "unable to load test.json"
       sys.exit(1)
    mjf.fixKeysWithSpaces() 
    # rename current file
    old = file + ".oldkeys"
    os.rename(file, old) 
    # write out new json with to current name
    if not mjf.write_mjfile(1) :
       print "unable to write fixed json to:",file

    print "Saved old format as:", old,
    print "  Wrote fixed format to original file:",file


  ############################################################
  # sdf generated code
  ############################################################
  ############################################################
  # Code to insert an key/value pair at a given location
  ############################################################
  def insert(self, key, value):
    #split key into a list of keys
    keys = string.split(key,"/")
    print keys

    front=""
    back=""

    #generate dictionary
    for k in keys:
      front=front+"{'"+k+"':"
      print "Front"+front
      back = back+'}'

    newDict = front+"'"+value+"'"+back
 
    print "NewDict: "+newDict
    self.set(newDict)

    


#    print "Key:",key," Value:",value,"\n",
#    self.current_dict[key]=value

  ############################################################
  # Code to request an key/value pair at a given location
  ############################################################
  def query (self, key):
    print "Key:",key,"\n"
    value = self.current_dict[key]
    print "Value: ",value,"\n"
    return value

############################################################
# Command line interface to this class
############################################################
############################################################
# Code to print usage info (help)
############################################################
def usage():
  print "\n"
  print "mjson.py version ",VERSION,", developed by DISP group at Duke Unversity"
  print "mjson <opts> filename\n"
  print "Supported Options:\n\n"
  print "-h, --help	display this screen\n"
  print "-v 		verbose output\n"
  print "-a, --add     add key\n"
  print "-s, --set     set value, default is for query (returns value)\n"
  print "-q, --query   query value"
  print "\n"
  print "filename is the name of the json file to edit / query\n\n"

############################################################
# main 
#
# Command line interface to this class
############################################################
def main():
  parser = argparse.ArgumentParser(description='AWARE json file parser')
  parser.add_argument('-vv', action='store_const', dest='verbose', const='True', help='verbose output')
  parser.add_argument('-c', action='store_const', dest='create', const='True', help='create new JSON file')
  parser.add_argument('-s', action='store_true', dest='setval', default=False, help='set key value')
  parser.add_argument('-p', action='store_const', dest='printDict', const='True', help='print contents of JSON file')
  parser.add_argument('filename', nargs='+', help='filename')
  parser.add_argument('-k', action='store', dest='key', help='key')
  parser.add_argument('-v', action='store', dest='value', help='value')

  args=parser.parse_args()

  #instantiate class
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

  print "Open!"
 

  #if keys defined
  if args.key:
    print args.key
    keys = string.split(args.key,"/")
    print "len:",len(keys)

    #print list of keys
    print "Keys: " 
    for i in range(len(keys)):
      print i,"-",keys[i],"\n"

  if args.setval:
    print "Set: ",args.setval
    if not mjf.insert(args.key, args.value):
      print "Unable to set\n"
    
  else:
    print "Query:", args.setval
    (value) = mjf.getKeys(keys)
    print "value: ",value,"\n"

  if args.printDict:
    print mjf.json_stringify_pretty() 

  mjf.write_mjfile(1);

#    bar = """
    #if not mjf.open_existing_mjfile('mjson_eCam_template.json'):
#    if not mjf.open_existing_mjfile('test.json'):
#        sys.exit(1)

    
    
    #print "open new=",mjf.name_new_mjfile('mosdict.json')
    #print "keyset=",mjf.keySet('breed','poodle', 1)
    #(avail, val) = mjf.arrayIndexGet("favorite_image_regions", 0) 
    #if avail: print "found array item=",repr(val)
    #print "description=",val["description"]

 #   (ok, val) = mjf.get_nested("photographer","title")
 #   (ok, val) = mjf.get_nested("access","web display")
#    """

#    bar =    """if not mjf.set_nested("web_display2", "access2"):
    #These routines only work if element exists in file
    # unable to create deep element now:
#       print "unable to load access2"
#    if not mjf.set_nested("ready", "web_display2", "access2"):
#       print "unable to load web_display2"
#    """

#    update1 = '{"access":{"web display":"ready yippee"}}'
#    mjf.update(update1)
##    update2 = '{"photographer":{"photographer":"El Magnifico"}}' 
#    mjf.update(update2)
    
#    bar = """
#    # Do not write to template example
    #print "write=", mjf.write_mjfile(1)
#    overwrite_ok = 1
#    mjf.name_new_mjfile('test2.json', overwrite_ok)
#    print "write=", mjf.write_mjfile(1)
#    mjf.clear_mjdata() 

    #mjf.plainDump('test.json') 
#    if not mjf.open_existing_mjfile('test.json'):
#       print "unable to load test.json"
#       sys.exit(1)
#    """
    #mjf.fixKeysWithSpaces() 
#    print "fixing file: ",sys.argv[1]
#    mjf.jsonUpdaterReplacer(sys.argv[1])


if __name__ == "__main__":
  main()
 
#    main()


