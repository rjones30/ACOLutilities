#!/bin/env python
#
# live.py - generates a live display of active collimator data
#           from the EPICS archiver.
#
# author: richard.t.jones at uconn.edu
# version: april 3, 2018

import mysql.connector
import datetime
import time
import sys
import re

gains = [1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12]
calparamR = {1e9: {"ix": 1.340, "iy": 0.893, "ox": 0, "oy": 1.460},
             1e11:{"ix": 1.195, "iy": 0.953, "ox": 0, "oy": 1.050},
             1e10:{"ix": 1.444, "iy": 1.045, "ox": 0, "oy": 1.418}}
calparamP = {1e9: {"ix": 568, "iy": -430, "ox": 0, "oy": 314},
             1e11:{"ix": 1343, "iy": -47, "ox": 0, "oy": -94},
             1e10:{"ix": 2141, "iy": 233, "ox": 0, "oy": 564}}
calparamQ = {1e9: {"ix":-1440, "iy":-1377, "ox": 0, "oy": -1027},
             1e11:{"ix": 2198, "iy": 2563, "ox": 0, "oy": -208},
             1e10:{"ix": -776, "iy": -196, "ox": 0, "oy": -487}}
calparamS = {1e9: {"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2},
             1e11:{"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2},
             1e10:{"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2}}

# extracted values for use prior to addition of pedestals to EPICS archive
pedestals = {1e9: {"ixp":  -45, "ixm":  -44, "iyp":   -9, "iym":    -8,
                   "oxp":  960, "oxm":  -34, "oyp": -720, "oym":  -950},
             1e10: {"ixp": 1380, "ixm":  503, "iyp":  168, "iym":  -665,
                   "oxp":  -20, "oxm":  -35, "oyp": -520, "oym":  -705},
             1e11: {"ixp": -230, "ixm": -210, "iyp": -125, "iym": -1140,
                   "oxp":  -24, "oxm":  -35, "oyp":  350, "oym":  1007}}

epicsvars = {"ixp": "IOCHDCOL:VMICADC1_1",
             "ixm": "IOCHDCOL:VMICADC2_1",
             "iyp": "IOCHDCOL:VMICADC3_1",
             "iym": "IOCHDCOL:VMICADC4_1",
             "oxp": "IOCHDCOL:VMICADC1_2",
             "oxm": "IOCHDCOL:VMICADC2_2",
             "oyp": "IOCHDCOL:VMICADC3_2",
             "oym": "IOCHDCOL:VMICADC4_2",
             "gain": "IAC5H01I_GAINXM",
             "ixp_ped": "AC:inner:ped:x_plus",
             "ixm_ped": "AC:inner:ped:x_minus",
             "iym_ped": "AC:inner:ped:y_plus",
             "iyp_ped": "AC:inner:ped:y_minus",
             "oxp_ped": "AC:outer:ped:x_plus",
             "oxm_ped": "AC:outer:ped:x_minus",
             "oym_ped": "AC:outer:ped:y_plus",
             "oyp_ped": "AC:outer:ped:y_minus",
             "cur": "IBCAD00CRCUR6",
             "xmo": "hd:collimator:x:motor.RBV",
             "ymo": "hd:collimator:y:motor.RBV",
             "xbp": "bpu_mean_x",
             "ybp": "bpu_mean_y"}

myahost = [{"name":"opsmya0.acc.jlab.org", 
            "proxy":"gluey.phys.uconn.edu", "port": 63306},
           {"name":"opsmya1.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63307},
           {"name":"opsmya2.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63308},
           {"name":"opsmya3.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63309},
           {"name":"opsmya4.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63310},
           {"name":"opsmya5.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63311},
           {"name":"opsmya6.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63312},
           {"name":"opsmya7.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63313},
           {"name":"opsmya8.acc.jlab.org",
            "proxy":"gluey.phys.uconn.edu", "port": 63314}]

# global variables

epicsrecord = {}
cnx = [0] * 9

def mysql_connection(n):
   if cnx[n] == 0:
      cnx[n] = mysql.connector.connect(user='myapi', password='MYA',
                                       host=myahost[n]["proxy"],
                                       port=myahost[n]["port"],
                                       database='archive')
   return cnx[n]

def close_mysql_connections():
   for c in cnx:
      if c:
         c.close()

def update_epics_record(var, nmax=1000, stime=0):
   mya0 = mysql_connection(0)
   cursor = mya0.cursor()
   query = "SELECT chan_id, host FROM channels WHERE name = %s"
   cursor.execute(query, (epicsvars[var],))
   chan_id = -1
   for (c, h) in cursor:
      chan_id = c
      host = h
   if chan_id == -1:
      print "update_epics_record error -",
      print "epics variable", epicsvars[var], 
      print "is not in the archive, cannot continue!"
      print cursor._executed
      sys.exit(1)
   cursor.close()

   nmya = -1
   for h in myahost:
      if h["name"] == host + ".acc.jlab.org":
         nmya = int(host[6])
   if nmya < 0:
      print "update_epics_record error -",
      print "mya host", host, 
      print "is not in my archive server list, cannot continue!"
      sys.exit(1)

   epicstime = stime * 65536**2
   mya1 = mysql_connection(nmya)
   cursor = mya1.cursor()
   if stime > 0:
      query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
               " WHERE time < {0:f}".format(epicstime) +
               " ORDER BY time DESC LIMIT {0}".format(nmax))
   else:
      query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
               " ORDER BY time DESC LIMIT {0}".format(nmax))
   cursor.execute(query)
   epicsrecord[var] = []
   for (t, v) in cursor:
      epicsrecord[var].append([t, v])
   if len(epicsrecord[var]) == 0 or epicsrecord[var][0][0] < epicstime and stime < time.time() - 500:
      query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
               " WHERE time > {0:f}".format(epicstime) +
               " ORDER BY time ASC LIMIT {0}".format(nmax / 2))
      cursor.execute(query)
      row = cursor.fetchall()
      if len(row) > 0:
         epicstime = row[-1][0]
         query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
                  " WHERE time < {0:f}".format(epicstime) +
                  " ORDER BY time DESC LIMIT {0}".format(nmax))
         cursor.execute(query)
         epicsrecord[var] = []
         for (t, v) in cursor:
            epicsrecord[var].append([t, v])
   print var, "updated from", 
   print datetime.datetime.fromtimestamp(epicsrecord[var][-1][0]/65536**2).strftime('%m.%d.%Y %H:%M:%S'),
   print "to",
   print datetime.datetime.fromtimestamp(epicsrecord[var][0][0]/65536**2).strftime('%m.%d.%Y %H:%M:%S'),
   print ",", len(epicsrecord[var]), "elements"
   cursor.close()

def get_epics_record(var, stime):
   epicstime = stime * 65536**2
   precount = 500
   while precount > 0:
      try:
         if epicsrecord[var][0][0] < epicstime:
            print "fast-forward", var
            update_epics_record(var, 1000, stime + 5)
      except:
         update_epics_record(var, 1000, stime + precount)
      for row in epicsrecord[var]:
         if epicstime > row[0]:
            return row
      if len(epicsrecord[var]) == 1000:
         del epicsrecord[var]
         precount /= 10
      else:
         break
   #print "lookup of", var, "failed"
   return []

epoch = time.time()
date_time = 0
while True:
   if date_time > -2:
      pattern = '%d.%m.%Y %H:%M:%S'
      date_time = raw_input("Enter a date and time [dd.mm.yyyy hh:mm:ss]: ")
   else:
      date_time = "+2"
   if date_time:
      if date_time[0] == '+':
         epoch += float(date_time)
      elif date_time[0] == '-':
         epoch += float(date_time)
      else:
         epoch = int(time.mktime(time.strptime(date_time, pattern)))
   else:
      epoch = time.time()
   record = {}
   for var in epicsvars:
      record[var] = get_epics_record(var, epoch)
   g = gains[record['gain'][1]]
   for var in ("ixp", "ixm", "iyp", "iym", "oxp", "oxm", "oyp", "oym"):
      if len(record[var + '_ped']) > 0:
         ped = record[var + '_ped'][1] * 3276.8
      else:
         ped = pedestals[g][var]
      print var, ":", record[var][1], "-", ped,
      print "=", record[var][1] - ped
   repoch = record['ixp'][0] / 65536**2
   timestring = datetime.datetime.fromtimestamp(repoch).strftime('%m.%d.%Y %H:%M:%S')
   print timestring,
   print "gain: {0:.0e}".format(g),
   for var in ("ix", "iy", "ox", "oy"):
      P = calparamP[g][var]
      Q = calparamQ[g][var]
      R = calparamR[g][var]
      S = calparamS[g][var]
      if len(record[var + 'p_ped']) > 0:
         Ip_ped = record[var + 'p_ped'][1] * 3276.8
         Im_ped = record[var + 'm_ped'][1] * 3276.8
      else:
         Ip_ped = pedestals[g][var + 'p']
         Im_ped = pedestals[g][var + 'm']
      Ip = record[var + 'p'][1] - Ip_ped
      Im = record[var + 'm'][1] - Im_ped
      x = S * (Ip - R * Im + P) / (Ip + R * Im + Q + 1e-99)
      print var, ":", x, "   ",
   print "xmo:", record['xmo'][1], "ymo:", record['ymo'][1]

close_mysql_connections()
