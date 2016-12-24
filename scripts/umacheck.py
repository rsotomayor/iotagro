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
  fbudget       = 10.0 ;
  fcubiertos_g   = "fcubiertos.csv";
  fnocubiertos_g = "fnocubiertos.csv";
  stationfile_g  = "estaciones.csv";
  inputfile_g    = "fruticulturatodas.csv"
  try:
    opts, args = getopt.getopt(argv,"h:i:b:s:f",["input=","basedir=","station=","fbudget="])
  except getopt.GetoptError:
    print 'umacheck.py --input=<inputfile> --station=<stationlist> --basedir=<basedir> --fbudget=<fbudget>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umacheck.py --input=<inputfile> --station=<stationlist> --basedir=<basedir> --fbudget=<fbudget>'
      sys.exit()
    elif opt in ("-b", "--basedir"):
      basedir_g = arg
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-s", "--station"):
      stationfile_g = arg
    elif opt in ("-f", "--fbudget"):
      fbudget = float(arg);


  print stationfile_g
  print inputfile_g
  print basedir_g
  contadorPuntos = 0 ;

  contadoresPuntoCubierto   = 0 ;
  contadoresPuntoNoCubierto = 0 ;


  f = open(inputfile_g, 'rt')

  try:
      contadorPuntos = 0 ;
      reader = csv.reader(f)
      firstline = True
      for row in reader:
        if firstline:    #skip first line
          firstline = False
          fcubiertos = open(fcubiertos_g, 'w')
          fcubiertos.write(" ".join((str(elem)+",") for elem in row) + "\n")
          fnocubiertos = open(fnocubiertos_g, 'w')
          fnocubiertos.write(" ".join((str(elem)+",") for elem in row) + "\n")
          continue
        longitudePunto=float(row[0])
        latitudePunto=float(row[1])

        contadorEstaciones = 0 
        f2 = open(stationfile_g, 'rt')
        flagCubierto = False
        try:
            reader2 = csv.reader(f2)
            firstline = True
            for row2 in reader2:
              if firstline:    #skip first line
                firstline = False
                continue
              longitudeEstacion=float(row2[18].replace(",","."))
              latitudeEstacion=float(row2[17].replace(",","."))

               
              distance = haversine(longitudePunto,latitudePunto,longitudeEstacion,latitudeEstacion);
              if ( distance < fbudget ):
                #~ print "Distancia :" + str(distance)
                flagCubierto = True
                break;
              contadorEstaciones = contadorEstaciones + 1
        finally:
            f2.close()

        if flagCubierto == True:
          contadoresPuntoCubierto   = contadoresPuntoCubierto + 1 ;
          fcubiertos.write(" ".join((str(elem)+",") for elem in row) + "\n")          
        else:
          contadoresPuntoNoCubierto = contadoresPuntoNoCubierto + 1 ;
          fnocubiertos.write(" ".join((str(elem)+",") for elem in row) + "\n")
          

        print "Puntos Cobertura: " + str(contadoresPuntoCubierto) + " NO Cobertura: " + str(contadoresPuntoNoCubierto)
        contadorPuntos = contadorPuntos + 1
  finally:
      f.close()
      fcubiertos.close();
      fnocubiertos.close();
      
  print "Puntos "+ str(contadorPuntos)
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

