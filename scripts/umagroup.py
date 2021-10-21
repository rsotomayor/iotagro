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
    opts, args = getopt.getopt(argv,"h:i:b:o:l",["input=","basedir=","output=","linkbudget="])
  except getopt.GetoptError:
    print 'umagroup.py --input=<inputfile> --output=<stationlist> --basedir=<basedir> --linkbudget=<fbudget>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umagroup.py --input=<inputfile> --output=<stationlist> --basedir=<basedir> --linkbudget=<fbudget>'
      sys.exit()
    elif opt in ("-b", "--basedir"):
      basedir_g = arg
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-s", "--output"):
      outputfile_g = arg
    elif opt in ("-f", "--linkbudget"):
      radio_g = float(arg);


  print "INPUT FILE:  " + inputfile_g
  print "OUTPUT FILE: " + outputfile_g
  print "BASEDIR:     " + basedir_g
  print "RADIO :      " + str(radio_g)
  contadorPuntos = 0 ;

  inputfilenew_g = 'new_' + inputfile_g ;

  f = open(inputfile_g, 'rt')
  cluster_r = []
  
  longitudePuntoAnterior = 0 
  latitudePuntoAnterior  = 0
  fcluster  = open(outputfile_g, 'w')
  uma = 0 ;

  try:
      contadorPuntos = 0 ;
      reader = csv.reader(f)
      firstline = True
      for row in reader:
        if firstline:    #skip first line
          firstline = False
          strLine="";
          cntElem=0;
          row[3] = "UMA"
          for elem in row:
            if cntElem < (len(row)-1):
              strLine = strLine + str(elem) + ","  
            else:
              strLine = strLine + str(elem) + "\n" 
            cntElem = cntElem + 1 ;
          strLine.replace("\"","")
          fcluster.write(strLine);
          continue

        longitudePunto=float(row[0])
        latitudePunto=float(row[1])
        
        distance = haversine(longitudePunto,latitudePunto,longitudePuntoAnterior,latitudePuntoAnterior)
        #~ print "DISTANTCE: "+str(distance)

        
        if ( distance < radio_g ):
          pass;
        else:
          flagIn = False
          for cluster in cluster_r:
            lon = float(cluster[0]);
            lat = float(cluster[1]);
            distance = haversine(longitudePunto,latitudePunto,lon,lat)
            if ( distance < radio_g ):
              flagIn = True
              break

          if flagIn == False:
            uma = uma + 1 ;
            row[3] = uma
            cluster_r.append(row);
            longitudePuntoAnterior = longitudePunto
            latitudePuntoAnterior  = latitudePunto
            print "UMA :" + str(uma)
            #~ print row

        contadorPuntos = contadorPuntos + 1
  finally:
    f.close()

  print "Puntos "+ str(contadorPuntos)

  contadorCluster = 0 

  for cluster in cluster_r:
    contadorCluster = contadorCluster + 1 ;
    strLine="";
    cntElem=0;
    for elem in cluster:
      if cntElem < (len(cluster)-1):
        strLine = strLine + str(elem) + ","  
      else:
        strLine = strLine + str(elem) + "\n" 
      cntElem = cntElem + 1 ;
    strLine.replace('"','')
    fcluster.write(strLine);
  
  fcluster.close()


  print "Cluster Puntos "+ str(contadorCluster)


  f = open(inputfile_g, 'rt')
  finputnew = open(inputfilenew_g, 'w')


  try:
      contadorPuntos = 0 ;
      reader = csv.reader(f)
      for row in reader:
        if ( contadorPuntos == 0 ):
          strLine="UMA,";
          cntElem=0;
          for elem in row:
            if cntElem < (len(row)-1):
              strLine = strLine + str(elem) + ","  
            else:
              strLine = strLine + str(elem)  + "," 
              strLine = strLine + "DISTANCE" + "\n" 
            cntElem = cntElem + 1 ;
          strLine.replace("\"","")
          finputnew.write(strLine);
        else:
          longitudePunto=float(row[0])
          latitudePunto=float(row[1])
          contadorCluster = 0 
          distanceMin     = 10000;
          for cluster in cluster_r:
            lon = float(cluster[0]);
            lat = float(cluster[1]);
            distance = haversine(longitudePunto,latitudePunto,lon,lat)
            if ( distance < distanceMin):
              distanceMin   = distance ;
              umaEncontrada = cluster[3];
            contadorCluster = contadorCluster + 1 

          print "UMA ENCONTRADA " + str(umaEncontrada)  + "DISTANCE " + str(distanceMin)

          strLine=str(umaEncontrada) + ",";
          cntElem=0;
          for elem in row:
            if cntElem < (len(row)-1):
              strLine = strLine + str(elem) + ","  
            else:
              strLine = strLine + str(elem) + ","  
              strLine = strLine + str(distanceMin) + "\n" 


            cntElem = cntElem + 1 ;
          strLine.replace("\"","")
          finputnew.write(strLine);
                      
            
        contadorPuntos = contadorPuntos + 1
        print "Punto "+ str(contadorPuntos)

  finally:
    f.close()
        
  finputnew.close();
  

    
  
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

