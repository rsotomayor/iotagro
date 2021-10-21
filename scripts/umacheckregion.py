#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mawsserver.py
#
#  Copyright 2012 Rafael Sotomayor Brule <rsotomayor@ub-rsotomayor>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import fiona
import shapefile
import shapely
from shapely.geometry import Polygon, Point, MultiPolygon, shape, mapping
import numpy as np
import csv
import os, sys
import getopt
import time
import datetime
import md5
from hashlib import sha1
from random import random
from math import radians,sin, cos, asin, sqrt, atan2
from fiona import collection
import logging
from os.path import expanduser
from os.path import basename
import signal
from osgeo import ogr
import json



flagIn_g        = False
inputfile_g     = "/dev/null"
outputfile_g    = "/dev/null"
stationfile_g   = "/dev/null"
logfile_g       = "/dev/null"
radio_g         = 10.0
logger_g        = logging.getLogger("umacheckcobertura")



def handler(signum, frame):
  print "Timeout ...."
  logger_g.warning("Timeout ....")

def my_sleep(sleep_p,point_p,poly_p):
  dist=point_p.distance(poly_p)  
  return dist;

def now():
  return time.ctime(time.time())


def usage(var_p):
  print var_p + " no esta definida";
  print 'umacheckregion.py --input=<inputfile> --region=<region> --output=<ouputfile>'

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """

    #~ Viña del Mar
    #~ longitudeEstacion = -71.55183
    #~ latitudeEstacion  = -33.02457

    #~ Puerto Montt
    #~ longitudeEstacion = -72.94289
    #~ latitudeEstacion  = -41.46574    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

def records(file):  
  # generator 
  reader = ogr.Open(file)
  layer = reader.GetLayer(0)
  for i in range(layer.GetFeatureCount()):
      feature = layer.GetFeature(i)
      yield json.loads(feature.ExportToJson())

          
def send2File(puntos_p):
  outFile  = outputfile_g
  clusterContador = 0


  schema = { 'geometry': 'Point', 'properties': { 'name': 'str','Region':'str' } }

  with collection(outFile, "w", "ESRI Shapefile", schema) as output:
    index = 0 ;
    for row in puntos_p:
      output.write(row[0])
      #~ print "INDEX: " + str(index) 
      #~ print row[0];
      #~ print row[1];

      index = index + 1 
      #~ output.write({
          #~ 'properties': {
              #~ 'name': row[0]['properties']['name'],
              #~ 'Region': row[0]['properties']['Region']
          #~ },
          #~ 'geometry': row[0]['geometry']
          #~ })
      
      clusterContador = clusterContador +1 ;
        
  print "Saving ...." + str(clusterContador);


def checkPointInRegion():
  points  = [pt for pt in records(inputfile_g)]
  multipol = records(regionfile_g)
  #~ multi = multipol.next() # 1 feature

  puntos = []

  for i, pt in enumerate(points):
    #~ print pt;
    point = shape(pt['geometry'])
    multipol = records(regionfile_g)
    now = datetime.datetime.now()
    print now.strftime("%Y-%m-%d %H:%M:%S")
    print " I: " + str(i)
    name  = str(pt['properties']['name'])

    
    schema = { 'geometry': 'Point', 'properties': { 'name': 'str','Region': 'str' } }    
    
    for j, pl in enumerate(multipol):
      #~ print j
      if point.within(shape(pl['geometry'])):
        region = str(pl['properties']['Region']) 
        mypoint = [ 
                    { "properties": 
                          {"name": name,"Region":region}, 
                      "geometry": mapping(point) 
                    }
                  ]
                            
        
      #~ output.write({
          #~ 'properties': {
              #~ 'name': name
          #~ },
          #~ 'geometry': mapping(point)
          #~ })
        
        
        #~ print "Region :" + region
        puntos.append(mypoint);
        #~ print puntos;
        send2File(puntos);
        break;
    
    #~ puntosOut_p.append(pt);

  #~ for i, pt in enumerate(points):
    #~ point = shape(pt['geometry'])
    #~ print "Punto: " + str(i) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p))
    #~ logger_g.info("Punto: " + str(i) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))

    #~ multipol = records(stationfile_g)
    #~ for j, pl in enumerate(multipol):
      #~ multi = pl;
      #~ if ( j%25000 == 0 ):
        #~ print "Cheking polygon: " + str(j)
        #~ logger_g.info("Cheking polygon: " + str(j))

      #~ if point.within(shape(multi['geometry'])):
        #~ puntosIn_p.append(pt);
        #~ puntosOut_p.remove(pt);
        #~ send2File(puntosIn_p,puntosOut_p)
        #~ break;
  #~ send2File(puntosIn_p,puntosOut_p)


  
        
def main(argv):
  global  inputfile_g;
  global  outputfile_g;
  global  regionfile_g;
  global  logfile_g;

  inputfile_g  = "" ;
  regionfile_g = "" ;
  outputfile_g = "umaregion.data"; 
  logfile_g    = "umaregion.log";
  
  try:
    opts, args = getopt.getopt(argv,"h:i:o:r:l",["input=","output=","region=","logfile="])
  except getopt.GetoptError:
    print 'umacheckregion.py --input=<inputfile> --region=<region> --output=<ouputfile>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umacheckregion.py --input=<inputfile> --region=<region> --output=<ouputfile>'
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-o", "--output"):
      outputfile_g = arg
    elif opt in ("-l", "--logfile"):
      logfile_g = arg
    elif opt in ("-r", "--region"):
      regionfile_g = arg

  if not os.path.exists(inputfile_g):
    usage("inputfile_g");
    sys.exit(1);

  if not os.path.exists(regionfile_g):
    usage("regionfile_g");
    sys.exit(1);

  try:
    outputfile_g
  except NameError:
    usage("outputfile_g");
    sys.exit(1);


  checkPointInRegion();


  #~ hdlr      = logging.FileHandler(logfile_g)  
  #~ formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  #~ hdlr.setFormatter(formatter)
  #~ logger_g.addHandler(hdlr) 
  #~ logger_g.setLevel(logging.INFO)


          
  
  #~ puntosIn  = []
  #~ puntosOut = []
  
  #~ checkPointInPolygonv2(puntosIn,puntosOut);
          
  #~ w.save('/tmp/test.shp')    
        
  print "QUIT APP"


if __name__ == "__main__":
   main(sys.argv[1:])

