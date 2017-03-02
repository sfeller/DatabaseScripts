#!/usr/bin/python
import sys
from lxml import etree


xmlns="http://www.opengis.net/kml/2.2"

def getPosition( fileName ):
  inFile = "temp.kml" 
  xmlData = etree.parse(fileName) #etree.parse() opens and parses the data

  print xmlData
 
  # find all "Message" records in the document, regardless of level
  messages = xmlData.findall(".//", namespaces={xmlns})
 
  for msg in messages:
    #first, get the data in the "tags" of the record
    if "coord" in msg.tag:
      location = msg.text.split(',')
#       lon = location[0]
#       lat = location[1]
#       alt = location[2]

      return location


def main ():

  #parse command line options
  if len(sys.argv) != 2:
    print "usage: getPos.py sourceFile\n"
    return;

  filename = sys.argv[1]

  print "fn:"+filename

  location = getPosition(filename)
  
  print "Coordinates: ("+location[0]+","+location[1]+","+location[2]+")\n"


if __name__ == "__main__":
    main()
