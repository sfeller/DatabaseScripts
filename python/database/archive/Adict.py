#!/usr/bin/python
# Adict.py
# 
# AWARE database class
#
# Functions
#   query - Returns a value for a given key
#   getKey - Returns a keys for a given value.
#
# Created by Steve Feller on 11/8/12
# Released on:
###########################################################

def findKey(dic, val):
  """return the key of dictionary dic given the value"""
  return [k for k, v in symbol_dic.iteritems() if v == val][0]
def findValue(dic, key):
  """return the value of dictionary dic given the key"""
  return dic[key]

class Lookup(dict):
  """
  a dictionary which can lookup value by key, or keys by value
  """
  def __init__(self, items=[]):
    """items can be a list of pair_lists or a dictionary"""
    dict.__init__(self, items)
  def getKey(self, value):
    """find the key(s) as a list given a value"""
    return [item[0] for item in self.items() if item[1] == value]
  def getValue(self, key):
    """find the value given a key"""
    return self[key]


class AJdict(dict):
  #############################################
  # Define intiation with with dict
  #############################################
  def __init__(self, items=[]):
  
    dict.__init__(self, items)

  #############################################
  # getValue 
  #
  # This function returns a value for a given key
  #############################################
  def getValue(self, key):
    return self[key]

  #############################################
  # getKey 
  #
  # This function returns a list of keys for a given value
  #############################################
  def getKey(self, value):
    return [key[0] for key in self.items() if key[1] == value]


# test it out
if __name__ == '__main__':
  # dictionary of chemical symbols
  symbol_dic = {
    'C': 'carbon',
    'H': 'hydrogen',
    'N': 'nitrogen',
    'Li': 'lithium',
    'Be': 'beryllium',
    'B': 'boron'
  }

  print findKey(symbol_dic, 'boron') # B
  print findValue(symbol_dic, 'B') # boron
  print findValue(symbol_dic, 'H') # hydrogen
  name = 'lithium'
  symbol = 'Li'
  
  # use a dictionary
  look = AJdict(symbol_dic)
  print look.getKey(name) # [Li']
  print look.getValue(symbol) # lithium

  print "test2"

  # use a list of pairs instead of a dictionary
  # will be converted to a dictionary by the class internally
  age_list = [['Fred', 23], ['Larry', 28], ['Ene', 23]]
  look2 = AJdict(age_list)
  print look2.getKey(23) # ['Ene', 'Fred']
  print look2.getValue('Fred') # 23

  print look2
