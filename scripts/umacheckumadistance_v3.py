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
  distance_g     =3;

  try:
    opts, args = getopt.getopt(argv,"h:i:s:d",["input=","station=","distance="])
  except getopt.GetoptError:
    print 'umacheckdistance.py --input=<inputfile> --station=<stationlist> --distance=<distance>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umacheckdistance.py --input=<inputfile> --station=<stationlist> --distance=<distance>'
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-s", "--station"):
      stationfile_g = arg
    elif opt in ("-d", "--distance"):
      distance_g = float(arg)


  print "Input file:"    + inputfile_g
  print "Station file: " + stationfile_g
  print "Distance: " + str(distance_g);

  contadorPuntos  = 0 ;
  contadorStation = 0 ;
  
  
  if not os.path.exists(inputfile_g):
    usage("inputfile_g");
    sys.exit(1);

  if not os.path.exists(stationfile_g):
    usage("stationfile_g");
    sys.exit(1);

  outputfile_g = "output.csv"
  foutput = open(outputfile_g, 'w')



  foutput.write("UMA,")
  foutput.write("REGION,")
  foutput.write("NCOLINDANTE,")
  
  foutput.write("\n")
  
  cluster_r = []  
  with fiona.open(inputfile_g) as umasrc:
    for uma in umasrc:
      contadorPuntos = contadorPuntos + 1 ;
      long_uma = uma['geometry']['coordinates'][0]; 
      lat_uma  = uma['geometry']['coordinates'][1]; 
      indexuma   = str(uma['properties']['UMA']) 
      regionuma  = str(uma['properties']['REGION']) 

      #~ print indexuma
            
      #~ print "Contador Puntos: " + str(contadorPuntos)
      ncolindante = 0 ;
      with fiona.open(stationfile_g) as stsrc:
        for station in stsrc:
          long_uma_st = station['geometry']['coordinates'][0]; 
          lat_uma_st  = station['geometry']['coordinates'][1]; 
          uma_st      = str(station['properties']['UMA']) 
          region_st   = str(station['properties']['REGION']) 

          #~ print str(lat_uma_st) + "," + str(long_uma_st);
          contadorStation = contadorStation + 1 ;
          distance_between_pts = abs(haversine(long_uma,lat_uma,long_uma_st,lat_uma_st))
          if ( distance_between_pts < distance_g and (uma_st != indexuma) and ( regionuma == region_st) ):
            #~ print "Distancia : " + str(distance_between_pts) + " UMA " + indexuma + " UMA_ST " + uma_st
            cluster_r.append(station);
            ncolindante = ncolindante + 1 

      print indexuma + "," + regionuma + "," + str(ncolindante)
      foutput.write(str(indexuma)+",")
      foutput.write(regionuma+",")
      foutput.write(str(ncolindante)+",")
      foutput.write("\n")
      #~ print "NCOLINDANTE " + str(ncolindante) ;
          

  foutput.close();
 
  print "Puntos "  + str(contadorPuntos)
  print "Station " + str(contadorStation)
  
  print "QUIT"


  print "QUIT"
  return ;


if __name__ == "__main__":
   main(sys.argv[1:])

