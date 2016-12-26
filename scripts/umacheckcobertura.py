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


def prediceCobertura():
  global basedir_g
  global inputfile_g
  global stationfile_g
  global fbudget_g
  
  global fcubiertos_g
  global fnocubiertos_g
  global stationfile_g

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


def usage(var_p):
  print var_p + " no esta definida";
  print 'umacheckcobertura.py --input=<inputfile> --output=<ouputfile> --station=<stationlist> --radio=<radio>'
 

def in_me(self, point):
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

def work(argv,puntosIn_p,puntosOut_p):
  radio_g        = 10.0 ;

  try:
    opts, args = getopt.getopt(argv,"h:i:b:s:r",["input=","output=","basedir=","station=","radio="])
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
    elif opt in ("-r", "--radio"):
      radio_g = float(arg);

  contadorPuntos = 0 ;


  try:
    inputfile_g
  except NameError:
    usage("inputfile_g");
    sys.exit(1);

  try:
    outputfile_g
  except NameError:
    usage("outputfile_g");
    sys.exit(1);

  try:
    stationfile_g
  except NameError:
    usage("stationfile_g");
    sys.exit(1);
    
  try:
    radio_g
  except NameError:
    usage("radio_g");
    sys.exit(1);
    

  with fiona.open(inputfile_g, 'r') as input:
    for pt in input:
      contadorPuntos = contadorPuntos + 1
      point = pt['geometry']['coordinates']
      point = Point(point[0],point[1])
      
      #~ point = shapely.geometry.Point(-71.6272500, -33.039320 )
      print point
      with fiona.open(stationfile_g,'r') as fiona_collection:
        contador = 0 ;
        flagContains = False
        for pl in fiona_collection:
          contador = contador + 1
          if contador % 10000 == 0:
            print contador;
          shapefile_record = pl
          shape = shapely.geometry.asShape( shapefile_record['geometry'] )
          if shape.contains(point):
            flagContains = True
            break

      if contadorPuntos > 10:
        break;


      if flagContains == True:
        #~ print pt
        print "Punto Encontrado" + str(contador)
        puntosIn_p.append(pt);
      else:
        print "Punto No Encontrado " + str(contador)
        puntosOut_p.append(pt);
        
      print "Contador Puntos= " + str(contadorPuntos)

        
def main(argv):

  puntosIn  = []
  puntosOut = []

  try:
    opts, args = getopt.getopt(argv,"h:i:b:s:r",["input=","output=","basedir=","station=","radio="])
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
    elif opt in ("-r", "--radio"):
      radio_g = float(arg);


  try:
    outputfile_g
  except NameError:
    usage("outputfile_g");
    sys.exit(1);

  work(argv,puntosIn,puntosOut);


  outFileIn  = outputfile_g + "_in.shp";
  outFileOut = outputfile_g + "_out.shp";
        
  for row in puntosIn:
    print "IN =>";
    print row;
    print "<=";
    
  for row in puntosOut:
    print "OUT =>";
    print row;
    print "<=";
              

        
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

