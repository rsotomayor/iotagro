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
    opts, args = getopt.getopt(argv,"h:i:c:o",["input=","cobertura=","output="])
  except getopt.GetoptError:
    print 'umacheckmycob.py --input=<inputfile> --cobertura=<cobfile> --output=<outputfile>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umacheckmycob.py --input=<inputfile> --cobertura=<cobfile> --output=<outputfile>'
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-o", "--output"):
      outputfile_g = arg
    elif opt in ("-c", "--cobertura"):
      coberturafile_g = arg      


  print "INPUT FILE:  " + inputfile_g
  print "COBERTURAFILE FILE: " + coberturafile_g  
  print "OUTPUT FILE: " + outputfile_g
  contadorPuntos = 0 ;

  fi    = open(inputfile_g, 'rt')


  #~ f = open(inputfile_g, 'rt')
  fo   = open(outputfile_g, 'w')
    
  #~ umaanterior = 99 ;

  try:
      contadorPuntos = 0 ;
      reader    = csv.reader(fi)

          
      for row in reader:
        if contadorPuntos==0:
          strLine="";
          cntElem=0;
          for elem in row:
            if cntElem < (len(row)-1):
              strLine = strLine + str(elem) + ","  
            else:
              strLine = strLine + str(elem) + "," 
              strLine = strLine + "B2G,"                
              strLine = strLine + "B3G,"                
              strLine = strLine + "B4G\n"                
            cntElem = cntElem + 1 ;
          strLine.replace("\"","")
          fo.write(strLine);
        else:
          longitudePunto = float(row[2]);
          latitudePunto  = float(row[3]);
          

          contadorCobertura = 0 ;
          distanceMin = 9999.0;
          fcob  = open(coberturafile_g, 'rt')          
          cobertura = csv.reader(fcob)          
          for record in cobertura:
            #~ print record;
            if ( contadorCobertura == 0 ):
              pass;
            else:
              lon  = float(record[1]);
              lat  = float(record[2]);
              distance = haversine(longitudePunto,latitudePunto,lon,lat)
              #~ print "lon1 " + str(longitudePunto) + " lat1" + str(latitudePunto) + " lon2 " + str(lon) + " lat2" + str(lat) + " distance " + str(distance);
              if ( distance < distanceMin ):
                distanceMin = distance;
                b2g  = int(record[3]);
                b3g  = int(record[4]);
                b4g  = int(record[5]);
            contadorCobertura = contadorCobertura + 1 ;
          fcob.close();
          if ( distanceMin > 5 ):
            b2g  = 0;
            b3g  = 0;
            b4g  = 0;

          strLine="";
          cntElem=0;
          for elem in row:
            if cntElem < (len(row)-1):
              strLine = strLine + str(elem) + ","  
            else:
              strLine = strLine + str(elem) + ","
              strLine = strLine + str(b2g)  + "," 
              strLine = strLine + str(b3g)  + ","            
              strLine = strLine + str(b4g)  + "\n"          
            cntElem = cntElem + 1 ;
          strLine.replace("\"","")
          fo.write(strLine);

          print "contadorPuntos: " + str(contadorPuntos) + " distanceMin " + str(distanceMin)
          
        contadorPuntos = contadorPuntos + 1 ;

  finally:
    fi.close()
    fo.close()

  print "contadorPuntos: " + str(contadorPuntos)
    
  
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

