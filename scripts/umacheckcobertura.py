#!/usr/bin/env python3
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
# ~ import md5
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
basedir_g       ="/home/rsotomayor/rsotomayor@savtec.cl/workspace/iotagro/"
logger_g        = logging.getLogger("umacheckcobertura")
banda_g         = "2G"
operador_g      = "entel"


areacobertura_g = [ 
              { 
                "entel":
                { 
                  '2G': 
                  { 
                    '1900': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_XIII_contour_region.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_I_contour_region.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_II_contour_region.shp",
                        "3":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_III_contour_region.shp",
                        "4":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_IV_contour_region.shp",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_V_contour_region.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_VI_contour_region.shp",
                        "7":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_VII_contour_region.shp",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_VIII_contour_region.shp",
                        "9":  basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_IX_contour_region.shp",
                        "10": basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_X_contour_region.shp",
                        "11": basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_XI_contour_region.shp",
                        "12": basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_XII_contour_region.shp",
                        "14": basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_XIV_contour_region.shp",
                        "15": basedir_g+"data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_XV_contour_region.shp"                                        
                      }
                   },
                  '3G': 
                  { 
                    '900': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XIII_contour_region.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_I_contour_region.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_II_contour_region.shp",
                        "3":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_III_contour_region.shp",
                        "4":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_IV_contour_region.shp",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_V_contour_region.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_VI_contour_region.shp",
                        "7":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_VII_contour_region.shp",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_VIII_contour_region.shp",
                        "9":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_IX_contour_region.shp",
                        "10": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_X_contour_region.shp",
                        "11": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XI_contour_region.shp",
                        "12": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XII_contour_region.shp",
                        "14": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XIV_contour_region.shp",
                        "15": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XV_contour_region.shp"                                        
                      },
                    '1900': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XIII_contour_region.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_I_contour_region.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_II_contour_region.shp",
                        "3":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_III_contour_region.shp",
                        "4":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_IV_contour_region.shp",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_V_contour_region.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_VI_contour_region.shp",
                        "7":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_VII_contour_region.shp",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_VIII_contour_region.shp",
                        "9":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_IX_contour_region.shp",
                        "10": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_X_contour_region.shp",
                        "11": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XI_contour_region.shp",
                        "12": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XII_contour_region.shp",
                        "14": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XIV_contour_region.shp",
                        "15": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XV_contour_region.shp"                                        
                      }
                   },
                  '4G': 
                  { 
                    '700': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE700_RM_contour_region.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE700_I_contour_region.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE700_II_contour_region.shp",
                        "3":  "NO FILE",
                        "4":  "NO FILE",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE700_V_contour_region.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE700_VI_contour_region.shp",
                        "7":  "NO FILE",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE700_VIII_contour_region.shp",
                        "9":  "NO FILE",
                        "10":  "NO FILE",
                        "11":  "NO FILE",
                        "12":  "NO FILE",
                        "14":  "NO FILE",
                        "15":  "NO FILE"
                      },
                    '2600': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_RM_contour_region.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_I_contour_region.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_II_contour_region.shp",
                        "3":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_III_contour_region.shp",
                        "4":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_IV_contour_region.shp",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_V_contour_region.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_VI_contour_region.shp",
                        "7":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_VII_contour_region.shp",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_VIII_contour_region.shp",
                        "9":  basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_IX_contour_region.shp",
                        "10": basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_X_contour_region.shp",
                        "11": basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_XI_contour_region.shp",
                        "12": basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_XII_contour_region.shp",
                        "14": basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_XIV_contour_region.shp",
                        "15": basedir_g+"data/comunicaciones/areacobertura/entel/4G/LTE2600_XV_contour_region.shp"
                      }
                   }
                },
                "wom":
                { 
                  '3G': 
                  { 
                    'UMTS': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region XIII.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region I.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region II.shp",
                        "3":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region III.shp",
                        "4":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region IV.shp",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region V.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region VI.shp",
                        "7":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region VII.shp",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region VIII.shp",
                        "9":  basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region IX.shp",
                        "10": basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region X.shp",
                        "11": basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region XI.shp",
                        "12": basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region XII.shp",
                        "14": basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region XIV.shp",
                        "15": basedir_g+"data/comunicaciones/areacobertura/wom/3G/WOM_UMTS_Region XV.shp"
                      }
                   },
                  '4G': 
                  { 
                    'LTE': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XIII_contour_region.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_I_contour_region.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_II_contour_region.shp",
                        "3":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_III_contour_region.shp",
                        "4":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_IV_contour_region.shp",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_V_contour_region.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_VI_contour_region.shp",
                        "7":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_VII_contour_region.shp",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_VIII_contour_region.shp",
                        "9":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_IX_contour_region.shp",
                        "10": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_X_contour_region.shp",
                        "11": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XI_contour_region.shp",
                        "12": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XII_contour_region.shp",
                        "14": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XIV_contour_region.shp",
                        "15": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_900_trim_XV_contour_region.shp"                                        
                      },
                    '1900': 
                      {
                        "0":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XIII_contour_region.shp",
                        "1":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_I_contour_region.shp",
                        "2":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_II_contour_region.shp",
                        "3":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_III_contour_region.shp",
                        "4":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_IV_contour_region.shp",
                        "5":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_V_contour_region.shp",
                        "6":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_VI_contour_region.shp",
                        "7":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_VII_contour_region.shp",
                        "8":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_VIII_contour_region.shp",
                        "9":  basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_IX_contour_region.shp",
                        "10": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_X_contour_region.shp",
                        "11": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XI_contour_region.shp",
                        "12": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XII_contour_region.shp",
                        "14": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XIV_contour_region.shp",
                        "15": basedir_g+"data/comunicaciones/areacobertura/entel/3G/Cob_3G_1900_trim_XV_contour_region.shp"                                        
                      }

                   }
                }
                
              }
                 ];
                  



def handler(signum, frame):
  print("Timeout ....")
  logger_g.warning("Timeout ....")

def my_sleep(sleep_p,point_p,poly_p):
  dist=point_p.distance(poly_p)  
  return dist;

def now():
  return time.ctime(time.time())


def usage(var_p):
  print(var_p + " no esta definida");
  print('umacheckcobertura.py --input=<inputfile> --operador=<operador> --banda=<banda> --output=<ouputfile> ')


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
  layer  = reader.GetLayer(0)
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
    print("Area: " + str(j) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))
    logger_g.info("Area: " + str(j) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))
    for i, pt in enumerate(puntosOut_p):
      point = shape(pt['geometry'])
      #~ if ( i%500 == 0 ):
        #~ print ("Cheking points: " + str(i))
        #~ logger_g.info("Cheking points: " + str(i))
      if point.within(shape(multi['geometry'])):
        puntosIn_p.append(pt);
        del puntosOut_p[i]
        contadorIn = contadorIn + 1 
        #~ print ("ContadorIn: " + str(contadorIn))
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
    print("Punto: " + str(i) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))
    logger_g.info("Punto: " + str(i) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))

    multipol = records(stationfile_g)
    for j, pl in enumerate(multipol):
      multi = pl;
      if ( j%25000 == 0 ):
        print("Cheking polygon: " + str(j))
        logger_g.info("Cheking polygon: " + str(j))

      if point.within(shape(multi['geometry'])):
        puntosIn_p.append(pt);
        puntosOut_p.remove(pt);
        send2File(puntosIn_p,puntosOut_p)
        break;
  send2File(puntosIn_p,puntosOut_p)



def checkPointInPolygonv3(puntosIn_p,puntosOut_p):

  print(inputfile_g);
  

  points  = [pt for pt in records(inputfile_g)]
  
  
  return;

  #~ multipol = records(stationfile_g)
  #~ multi = multipol.next() # 1 feature

#~ data/comunicaciones/areacobertura/entel/2G/Cob_2G_1900_trim_XV_contour_region.shp


  for i, pt in enumerate(points):
    puntosOut_p.append(pt);


  send2File(puntosIn_p,puntosOut_p)
  for i, pt in enumerate(points):
    point  = shape(pt['geometry'])
    region = str(pt['properties']['Region'])
    print("Region :" +  region)
    
    print("Punto: " + str(i+1) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))
    logger_g.info("Punto: " + str(i+1) + " Puntos Out: " + str(len(puntosOut_p)) + " Puntos In: " + str(len(puntosIn_p)))

    #~ print areacobertura_g[0]['entel']['2G'];

    for k,station in enumerate(areacobertura_g[0][operador_g][banda_g]):
      #~ print station
      stationfile_g = areacobertura_g[0][operador_g][banda_g][station][region]
      if os.path.exists(stationfile_g):
        multipol = records(stationfile_g)
        for j, pl in enumerate(multipol):
          multi = pl;
          if ( j%25000 == 0 ):
            print("Cheking polygon: " + str(j))
            logger_g.info("Cheking polygon: " + str(j))
          flagin = False;

          try:
            flagin = point.within(shape(multi['geometry']))
          except(Exception, err):
            print("myerror")

          if flagin:
            try:
              puntosIn_p.append(pt);
            except(Exception, err):
              print("Error Punto IN")

            try:
              puntosOut_p.remove(pt);
            except(Exception, err):
              print("Error Punto Out")
            
            send2File(puntosIn_p,puntosOut_p)
            break;

        if flagin:
          flagin = False
          break;
      else:
        print("File " + stationfile_g + " no existe !!!")

  send2File(puntosIn_p,puntosOut_p)


          
def send2File(puntosIn_p,puntosOut_p):
  outFileIn  = outputfile_g + "_in.shp";
  outFileOut = outputfile_g + "_out.shp";

  schema = { 'geometry': 'Point', 'properties': { 'name': 'str','Region': 'str' } }
  clusterContador = 1 ;
  with collection(outFileIn, "w", "ESRI Shapefile", schema) as output:
    for row in puntosIn_p:
      point = row['geometry']['coordinates']
      region = row['properties']['Region']
      point = Point(point[0],point[1])  
      name = "Cluster In " + str(clusterContador)
      output.write({
          'properties': {
              'name': name,
              'Region': region
              
          },
          'geometry': mapping(point)
          })
      clusterContador = clusterContador +1 ;


  schema = { 'geometry': 'Point', 'properties': { 'name': 'str','Region': 'str' } }
  clusterContador = 1 ;
  with collection(outFileOut, "w", "ESRI Shapefile", schema) as output:
    for row in puntosOut_p:
      point = row['geometry']['coordinates']
      region = row['properties']['Region']

      point = Point(point[0],point[1])      
      name = "Cluster Out " + str(clusterContador)
      output.write({
          'properties': {
              'name': name,
              'Region': region
          },
          'geometry': mapping(point)
          })
      clusterContador = clusterContador +1 ;


        
  print("Saving ....")
  
  
        
def main(argv):
  global  radio_g;
  global  inputfile_g;
  global  outputfile_g;
  global  operador_g;
  global  banda_g;
  global  logfile_g;

  try:
    opts, args = getopt.getopt(argv,"h:i:o:b:p:l:b",["input=","output=","basedir=","operador=","logfile=","banda="])
  except getopt.GetoptError:
    print('umacheckcobertura.py --input=<inputfile> --operador=<operador> --banda=<banda> --output=<ouputfile> ');
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('umacheckcobertura.py --input=<inputfile> --operador=<operador> --banda=<banda> --output=<ouputfile> ')
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-o", "--output"):
      outputfile_g = arg
    elif opt in ("-p", "--operador"):
      operador_g = arg
    elif opt in ("-l", "--logfile"):
      logfile_g = arg
    elif opt in ("-r", "--banda"):
      banda_g = arg;


  if not os.path.exists(inputfile_g):
    usage("inputfile_g");
    sys.exit(1);
  
  try:
    outputfile_g
  except NameError:
    usage("outputfile_g");
    sys.exit(1);


  print("Operador: " + operador_g);
  print("Banda: " + banda_g);


  hdlr      = logging.FileHandler(logfile_g)  
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  hdlr.setFormatter(formatter)
  logger_g.addHandler(hdlr) 
  logger_g.setLevel(logging.INFO)


          
  
  puntosIn  = []
  puntosOut = []
  
  checkPointInPolygonv3(puntosIn,puntosOut);
          
  #~ w.save('/tmp/test.shp')    
        
  print("QUIT")


if __name__ == "__main__":
   main(sys.argv[1:])

