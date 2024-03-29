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
    opts, args = getopt.getopt(argv,"h:i:o:u:r",["input=","output=","unidades=","radio="])
  except getopt.GetoptError:
    print 'umagroup.py --input=<inputfile> --output=<outputfile> --unidades=<unidadesfile> --radio=<fbudget>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umagroup.py --input=<inputfile> --output=<outputfile> --unidades=<unidadesfile> --radio=<fbudget>'
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-u", "--unidades"):
      unidadesfile_g = arg
    elif opt in ("-o", "--output"):
      outputfile_g = arg
    elif opt in ("-r", "--radio"):
      radio_g = float(arg);


  print "INPUT FILE:  " + inputfile_g
  print "OUTPUT FILE: " + outputfile_g
  print "UNIDADES FILE: " + unidadesfile_g
  print "RADIO :      " + str(radio_g)
  contadorPuntos = 0 ;


  f = open(inputfile_g, 'rt')
  uma_r = []
  unidades_r = []
  
  longitudePuntoAnterior = 0 
  latitudePuntoAnterior  = 0
  fuma = open(outputfile_g, 'w')

  try:
      contadorPuntos = 0 ;
      reader = csv.reader(f)
      firstline = True
      
      index_uma = 0 ;
      
      for row in reader:
        if firstline:    #skip first line
          unidades_r.append(row);
          firstline = False
          strLine="";
          cntElem=0;
          for elem in row:
            field = str(elem)
            field=field.replace(",","")
            field=field.replace("\"","")
            if cntElem < (len(row)-1):
              strLine = strLine + field + ","  
            else:
              strLine = strLine + field + "\n" 
            cntElem = cntElem + 1 ;
          strLine=strLine.replace("\"","")
          fuma.write(strLine);
          continue
        longitudePunto=float(row[0])
        latitudePunto=float(row[1])
        
        distance = haversine(longitudePunto,latitudePunto,longitudePuntoAnterior,latitudePuntoAnterior)
        print str(contadorPuntos) + " DISTANTCE: "+str(distance)

        #~ print "LEN " + str(len(row));


        if ( index_uma == 0 ):
          row[len(row)-1] = 1;
        else:
          row[len(row)-1] = index_uma;
        
        if ( distance < radio_g ):
          pass;
        else:
          flagIn = False
          for uma in uma_r:
            lon = float(uma[0]);
            lat = float(uma[1]);
            distance = haversine(longitudePunto,latitudePunto,lon,lat)
            if ( distance < radio_g ):
              flagIn = True
            
              
          if flagIn == False:
            index_uma = index_uma + 1 ;
            uma_r.append(row);

        unidades_r.append(row);
          
        longitudePuntoAnterior = longitudePunto 
        latitudePuntoAnterior  = latitudePunto
        

        contadorPuntos = contadorPuntos + 1
  finally:
      f.close()

  print "Puntos "+ str(contadorPuntos)

  contadorUma = 0 

  firstline = True
  for uma in uma_r:
    if firstline:    #skip first line
      firstline = False
      continue
    contadorUma = contadorUma + 1 ;
    strLine="";
    cntElem=0;
    for elem in uma:
      field = str(elem)
      field=field.replace(",","")
      field=field.replace("\"","")
      if cntElem < (len(uma)-1):
        strLine = strLine + field + ","  
      else:
        strLine = strLine + field + "\n" 
      cntElem = cntElem + 1 ;
    strLine=strLine.replace("\"","")
    fuma.write(strLine);
  
  fuma.close()

  print "Puntos "+ str(contadorUma)


  contadorUnidades = 0 
  funidades = open(unidadesfile_g, 'w')


  for row in unidades_r:
    contadorUnidades = contadorUnidades + 1 ;
    strLine="";
    cntElem=0;
    for elem in row:
      field = str(elem)
      field=field.replace(",","")
      field=field.replace("\"","")
      if cntElem < (len(row)-1):
        strLine = strLine + field + ","  
      else:
        strLine = strLine + field + "\n" 
      cntElem = cntElem + 1 ;
    strLine = strLine.replace("\"","")
    funidades.write(strLine);
  
  funidades.close()

  print "Unidades "+ str(contadorUnidades)      
      
      
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

