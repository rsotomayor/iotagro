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
  print 'umacheckcobertura.py --input=<inputfile> --output=<ouputfile> --station=<stationlist> --radio=<radio>'

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


def checkPointInPolygon(puntosIn_p,puntosOut_p):
  points  = [pt for pt in records(inputfile_g)]
  multipol = records(stationfile_g)
  #~ multi = multipol.next() # 1 feature

  for i, pt in enumerate(points):
    puntosOut_p.append(pt);

  contadorIn = 0 ;
  contadorInAnterior = 0; 
  send2File(puntosIn_p,puntosOut_p)
  for j, pl in enumerate(multipol):
    multi = pl;
    print "Area: " + str(j) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p))
    logger_g.info("Area: " + str(j) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))
    for i, pt in enumerate(puntosOut_p):
      point = shape(pt['geometry'])
      #~ if ( i%500 == 0 ):
        #~ print "Cheking points: " + str(i)
        #~ logger_g.info("Cheking points: " + str(i))
      if point.within(shape(multi['geometry'])):
        puntosIn_p.append(pt);
        del puntosOut_p[i]
        contadorIn = contadorIn + 1 
        #~ print "ContadorIn: " + str(contadorIn)
        if ( contadorIn != contadorInAnterior ):
          send2File(puntosIn_p,puntosOut_p)
        contadorAnterior = contadorIn;
  send2File(puntosIn_p,puntosOut_p)


def checkPointInPolygonv2(puntosIn_p,puntosOut_p):
  points  = [pt for pt in records(inputfile_g)]
  multipol = records(stationfile_g)
  #~ multi = multipol.next() # 1 feature

  for i, pt in enumerate(points):
    puntosOut_p.append(pt);

  send2File(puntosIn_p,puntosOut_p)
  for i, pt in enumerate(points):
  #~ for i, pt in enumerate(puntosOut_p):
    point = shape(pt['geometry'])
    print "Punto: " + str(i) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p))
    logger_g.info("Punto: " + str(i) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))

    multipol = records(stationfile_g)
    for j, pl in enumerate(multipol):
      multi = pl;
      if ( j%10000 == 0 ):
        print "Cheking polygon: " + str(j)
        logger_g.info("Cheking polygon: " + str(j))

      if point.within(shape(multi['geometry'])):
        puntosIn_p.append(pt);
        puntosOut_p.remove(pt);
        send2File(puntosIn_p,puntosOut_p)
        break;
  send2File(puntosIn_p,puntosOut_p)

          
def send2File(puntosIn_p,puntosOut_p):
  outFileIn  = outputfile_g + "_in.shp";
  outFileOut = outputfile_g + "_out.shp";

  schema = { 'geometry': 'Point', 'properties': { 'name': 'str' } }
  clusterContador = 1 ;
  with collection(outFileIn, "w", "ESRI Shapefile", schema) as output:
    for row in puntosIn_p:
      point = row['geometry']['coordinates']
      point = Point(point[0],point[1])  
      name = "Cluster In " + str(clusterContador)
      output.write({
          'properties': {
              'name': name
          },
          'geometry': mapping(point)
          })
      clusterContador = clusterContador +1 ;


  schema = { 'geometry': 'Point', 'properties': { 'name': 'str' } }
  clusterContador = 1 ;
  with collection(outFileOut, "w", "ESRI Shapefile", schema) as output:
    for row in puntosOut_p:
      point = row['geometry']['coordinates']
      point = Point(point[0],point[1])      
      name = "Cluster Out " + str(clusterContador)
      output.write({
          'properties': {
              'name': name
          },
          'geometry': mapping(point)
          })
      clusterContador = clusterContador +1 ;


        
  print "Saving ...."
  
  
        
def main(argv):
  global  radio_g;
  global  inputfile_g;
  global  outputfile_g;
  global  stationfile_g;
  global  logfile_g;

  try:
    opts, args = getopt.getopt(argv,"h:i:b:s:l:r",["input=","output=","basedir=","station=","logfile=","radio="])
  except getopt.GetoptError:
    print 'umacheckcobertura.py --input=<inputfile> --station=<stationlist> --output=<ouputfile>  --radio=<radio> '
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umacheckcobertura.py --input=<inputfile> -station=<stationlist> --output=<ouputfile> ---radio=<radio>'
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-o", "--output"):
      outputfile_g = arg
    elif opt in ("-s", "--station"):
      stationfile_g = arg
    elif opt in ("-l", "--logfile"):
      logfile_g = arg
    elif opt in ("-r", "--radio"):
      radio_g = float(arg);

  if not os.path.exists(inputfile_g):
    usage("inputfile_g");
    sys.exit(1);
  
  if not os.path.exists(stationfile_g):
    usage("stationfile_g");
    sys.exit(1);

  try:
    outputfile_g
  except NameError:
    usage("outputfile_g");
    sys.exit(1);


  try:
    radio_g
  except NameError:
    usage("radio_g");
    sys.exit(1);



  hdlr      = logging.FileHandler(logfile_g)  
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  hdlr.setFormatter(formatter)
  logger_g.addHandler(hdlr) 
  logger_g.setLevel(logging.INFO)


          
  
  puntosIn  = []
  puntosOut = []
  
  checkPointInPolygonv2(puntosIn,puntosOut);
          
  #~ w.save('/tmp/test.shp')    
        
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

