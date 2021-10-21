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
import csv
import os, sys
import getopt
import time
import datetime
import md5
import fiona
import shapely.geometry
from hashlib import sha1
from random import random
from math import radians,sin, cos, asin, sqrt, atan2
from pyproj import Proj
from pyproj import Proj, transform
import fiona
from fiona.crs import from_epsg


def usage(var_p):
  print var_p + " no esta definida";
  print 'umachecksitiotnt.py --input=<inputfile> --station=<stationlist> --output=<output>'

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


  inputfile_g    = "" ;
  stationfile_g  = "" ;
  outputfile_g   = "output.data" ;

  try:
    opts, args = getopt.getopt(argv,"h:i:b:s:f",["input=","station=","output="])
  except getopt.GetoptError:
    print 'umachecksitiotnt.py --input=<inputfile> --station=<stationlist> --output=<output>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umachecksitiotnt.py --input=<inputfile> --station=<stationlist> --output=<output>'
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-s", "--station"):
      stationfile_g = arg
    elif opt in ("-o", "--output"):
      outputfile_g = arg


  print "Input file:"    + inputfile_g
  print "Station file: " + stationfile_g
  print "Output File: "  + outputfile_g

  contadorPuntos  = 0 ;
  contadorStation = 0 ;
  
  
  if not os.path.exists(inputfile_g):
    usage("inputfile_g");
    sys.exit(1);
  
  if not os.path.exists(stationfile_g):
    usage("stationfile_g");
    sys.exit(1);

  foutput = open(outputfile_g, 'w')

  foutput.write("UMA,")
  foutput.write("REGION,")
  foutput.write("LONG_UMA,")
  foutput.write("LAT_UMA,")
  foutput.write("\n")


  with fiona.open(inputfile_g) as umasrc:
    for uma in umasrc:
      contadorPuntos = contadorPuntos + 1 ;
      contadorStation = 0 ;
      umageom = shapely.geometry.shape(uma["geometry"])
      distancia_minima = float("inf")
      distancia_maxima = 0

      long_uma = uma['geometry']['coordinates'][0]; 
      lat_uma  = uma['geometry']['coordinates'][1]; 
      #~ print uma

      with fiona.open(stationfile_g) as stationsrc:
        for station in stationsrc:
          stationgeom = shapely.geometry.shape(station["geometry"])
          station_pt  = stationgeom.coords;

          long_station = station['geometry']['coordinates'][0]; 
          lat_station  = station['geometry']['coordinates'][1]; 
  
          distance_between_pts = haversine(long_uma,lat_uma,long_station,lat_station);  
          
          if ( distance_between_pts < distancia_minima):
            indexuma     = str(station['properties']['indexuma'])
            regionuma    = str(station['properties']['REGION'])
            distancia_minima = distance_between_pts;

          if ( distance_between_pts > distancia_maxima):
            station_max      = str(station['properties']['indexuma'])
            distancia_maxima = distance_between_pts;


          #~ print station_name


          #~ lon, lat = pnyc(long_station, lat_station, inverse=True)
          #~ print uma['geometry']['coordinates'];
          #~ print station['geometry']['coordinates']
          contadorStation = contadorStation + 1 ;
          
          #~ print "Coord UMA (" + str(long_uma) + "," + str(lat_uma) +")" + "  Coord Station (" + str(long_station) + "," + str(lat_station) +")"
          #~ print "Coord UMA (" + str(lon) + "," + str(lat) +")" + "  Coord Station (" + str(lon) + "," + str(lat) +")"

      print "Punto: " + str(contadorPuntos) + " Index UMA: " + str(indexuma) + " Regiom: " + regionuma + " Distancia Minima: " + str(distancia_minima) + " Distancia Maxima: " + str(distancia_maxima);
      
      
          
      foutput.write(str(indexuma)+",")
      foutput.write(str(regionuma)+",")
      foutput.write(str(long_uma)+",")
      foutput.write(str(lat_uma)+",")
      foutput.write("\n")
      
      
  foutput.close();

 
  print "Puntos "  + str(contadorPuntos)
  print "Station " + str(contadorStation)
  
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

