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
from multiprocessing import Process
from time import sleep
from multiprocessing import Process
from time import sleep


flagIn_g        = False
inputfile_g     = "/dev/null"
outputfile_g    = "/dev/null"
stationfile_g   = "/dev/null"
logfile_g       = "/dev/null"
radio_g         = 10.0
logger_g        = logging.getLogger("umacheckcobertura")


def inSide(shape_p,point_p):
  global flagIn_g
  flagIn_g = shape_p.contains(point_p)

def run_with_limited_time(func, args, kwargs, time):
    """Runs a function with time limit

    :param func: The function to run
    :param args: The functions args, given as tuple
    :param kwargs: The functions keywords, given as dict
    :param time: The time limit in seconds
    :return: True if the function ended successfully. False if it was terminated.
    """
    p = Process(target=func, args=args, kwargs=kwargs)
    p.start()
    p.join(time)
    if p.is_alive():
        p.terminate()
        return False
    return True

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

def in_me(self, point):
  print "In Me:"

  result = False
  n = len(self.corners)

  p1x = int(self.corners[0].x)
  p1y = int(self.corners[0].y)
  for i in range(n+1):
    p2x = int(self.corners[i % n].x)
    p2y = int(self.corners[i % n].y)
    if point.y > min(p1y,p2y):
      if point.x <= max(p1x,p2x):
        if p1y != p2y:
          xinters = (point.y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
          print xinters
        if p1x == p2x or point.x <= xinters:
          result = not result
    p1x,p1y = p2x,p2y
  return result

def checkPointInPolygon(argv,puntosIn_p,puntosOut_p):
  global  radio_g;
  global  inputfile_g;
  global  outputfile_g;
  global  stationfile_g;
  global  logfile_g;
  
  contadorPuntos = 0 ;


  with fiona.open(inputfile_g, 'r') as input:
    for pt in input:
      puntosOut_p.append(pt);


  print "Comienza con puntos Out: " + str(len(puntosOut_p));  
  logger_g.info("Comienza con puntos Out: " + str(len(puntosOut_p)));

  contadorArea = 0 ;
  print "File: " + stationfile_g
  logger_g.info("File: " + stationfile_g)


  with fiona.open(stationfile_g,'r') as fiona_collection:
    for pl in fiona_collection:
      shapefile_record = pl
      shape = shapely.geometry.asShape( shapefile_record['geometry'] )
      contadorArea = contadorArea + 1  ;
      index = 0 ;

      if not puntosOut_p:
        break
      else:
        for pt in puntosOut_p:
          point = pt['geometry']['coordinates']
          point = Point(float(point[0]),float(point[1]))
          index = index + 1 
          flagExec = run_with_limited_time(inSide, (shape,point), {}, 1)
          if flagExec == True:
            flagIn = flagIn_g;
          else:
            print "TimeOut"
            flagIn = False

          if flagIn:
            puntosIn_p.append(pt);
            puntosOut_p.remove(pt)

      print "Contador Area: " + str(contadorArea) + " Index " + str(index);  
      print "Puntos Out: " + str(len(puntosOut_p));  
      print "Puntos In: " + str(len(puntosIn_p));  

      logger_g.info("Contador Area: " + str(contadorArea) + " Index " + str(index))
      logger_g.info("Puntos Out: " + str(len(puntosOut_p)))
      logger_g.info("Puntos In: " + str(len(puntosIn_p)))


  print contadorArea;

        
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


  outFileIn  = outputfile_g + "_in.shp";
  outFileOut = outputfile_g + "_out.shp";
          
  
  puntosIn  = []
  puntosOut = []
  
  checkPointInPolygon(argv,puntosIn,puntosOut);


  schema = { 'geometry': 'Point', 'properties': { 'name': 'str' } }
  clusterContador = 1 ;
  with collection(outFileIn, "w", "ESRI Shapefile", schema) as output:
    for row in puntosIn:
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
    for row in puntosOut:
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
        
  #~ w.save('/tmp/test.shp')    
        
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

