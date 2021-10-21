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
    opts, args = getopt.getopt(argv,"h:i:b:o:l",["input=","output="])
  except getopt.GetoptError:
    print 'umagroup.py --input=<inputfile> --output=<stationlist> --basedir=<basedir> --linkbudget=<fbudget>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'umagroup.py --input=<inputfile> --output=<stationlist> --basedir=<basedir> --linkbudget=<fbudget>'
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile_g = arg
    elif opt in ("-s", "--output"):
      outputfile_g = arg


  print "INPUT FILE:  " + inputfile_g
  print "OUTPUT FILE: " + outputfile_g
  contadorPuntos = 0 ;

  inputfilenew_g = 'new_' + inputfile_g ;

  f = open(inputfile_g, 'rt')
  fcluster  = open(outputfile_g, 'w')
    
  umaanterior = 99 ;

  try:
      contadorPuntos = 0 ;
      reader = csv.reader(f)
      
      
      for row in reader:
        uma = row[0]
        if len(uma) == 0 :
          uma = umaanterior;
        print "UMA: "+ str(uma);

        strLine="";
        cntElem=0;
        row[0] = uma 
        for elem in row:
          if cntElem < (len(row)-1):
            strLine = strLine + str(elem) + ","  
          else:
            strLine = strLine + str(elem) + "\n" 
          cntElem = cntElem + 1 ;
        strLine.replace("\"","")
        fcluster.write(strLine);
        umaanterior = uma ;
  finally:
    f.close()
    fcluster.close;

    
  
  print "QUIT"


if __name__ == "__main__":
   main(sys.argv[1:])

