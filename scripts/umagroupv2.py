#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  umagroupv2.py
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
import matplotlib.path as mplPath
import csv
import os, sys
import getopt
import time
import datetime
import md5
from hashlib import sha1
from random import random
from math import radians,sin, cos, asin, sqrt, atan2
from pyproj import Proj
from pyproj import Proj, transform
import shapely.geometry
from shapely.geometry import Polygon, Point, MultiPolygon, shape, mapping
from fiona import collection
import fiona
from fiona.crs import from_epsg

def usage(var_p):
  print var_p + " no esta definida";
  print 'umagroup.py --input=<inputfile> --output=<outputfile> --radio=<radio>'

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
    

def now():
  return time.ctime(time.time())



def main(argv):
  global basedir_g
  try:
    opts, args = getopt.getopt(argv,"h:i:o:r",["input=","output=","radio="])
  except getopt.GetoptError:
    print 'umagroup.py --input=<inputfile> --output=<outputfile> --radio=<radio>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umagroup.py --input=<inputfile> --output=<outputfile> --radio=<radio>'
      sys.exit()
    elif opt in ("-b", "--basedir"):
      basedir_g = arg
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-s", "--output"):
      outputfile_g = arg
    elif opt in ("-r", "--radio"):
      radio_g = float(arg);


  print "INPUT FILE:  " + inputfile_g
  print "OUTPUT FILE: " + outputfile_g
  print "RADIO :      " + str(radio_g)
  contadorPuntos = 0 ;

  if not os.path.exists(inputfile_g):
    usage("inputfile_g");
    sys.exit(1);

  firstline = True
  cluster_r = []
      
  with fiona.open(inputfile_g) as umasrc:
    schema = umasrc.schema.copy()
    for uma in umasrc:
      contadorPuntos = contadorPuntos + 1 ;
      umageom = shapely.geometry.shape(uma["geometry"])
      longitudePunto = uma['geometry']['coordinates'][0]; 
      latitudePunto  = uma['geometry']['coordinates'][1]; 
      #~ print uma
      indexuma  = uma['properties']['UMA'] 
      regionuma = str(uma['properties']['REGION']) 
      if firstline:    #skip first line
        firstline = False
        cluster_r.append(uma)
      else:
        distance = haversine(longitudePunto,latitudePunto,longitudePuntoAnterior,latitudePuntoAnterior)
        print str(contadorPuntos) + " DISTANCE: " +str(distance)     
        if ( distance < radio_g ):
          pass;
        else:
          flagIn = False
          for cluster in cluster_r:
            #~ print cluster
            lon  = float(cluster['geometry']['coordinates'][0]); 
            lat  = float(cluster['geometry']['coordinates'][1]); 
            distance = haversine(longitudePunto,latitudePunto,lon,lat)
            if ( distance < radio_g ):
              flagIn = True            
          if flagIn == False:
            cluster_r.append(uma)
                    
      longitudePuntoAnterior = longitudePunto 
      latitudePuntoAnterior  = latitudePunto
      
  
  #~ schema = { 'geometry': 'Point', 'properties': { 'name': 'str','Region': 'str' } }    
  clusterContador = 0 ;  
  with collection(outputfile_g, "w", "ESRI Shapefile", schema) as output:  
    for cluster in cluster_r:
      clusterContador = clusterContador + 1 
      point  = cluster['geometry']['coordinates']
      region = cluster['properties']['REGION']
      point  = Point(point[0],point[1])  
      name   = "Cluster In " + str(clusterContador)
      output.write(cluster);
      
      #~ output.write({
          #~ 'properties': {
              #~ 'name': name,
              #~ 'Region': region
              
          #~ },
          #~ 'geometry': mapping(point)
          #~ })
  
  print "QUIT " + str(contadorPuntos);


if __name__ == "__main__":
   main(sys.argv[1:])

