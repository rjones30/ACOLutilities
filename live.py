#!/bin/env python
#
# live.py - generates a live display of active collimator data
#           from the EPICS archiver.
#
# author: richard.t.jones at uconn.edu
# version: april 3, 2018

from ROOT import *
import numpy

import mysql.connector
import datetime
import time
import sys
import re

gains = [1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12]

pedestals = {1e9: {"ixp":  -45, "ixm":  -44, "iyp":   -9, "iym":    -8,
                   "oxp":  960, "oxm":  -34, "oyp": -720, "oym":  -950},
             1e10: {"ixp": 1380, "ixm":  503, "iyp":  168, "iym":  -665,
                   "oxp":  -20, "oxm":  -35, "oyp": -520, "oym":  -705},
             1e11: {"ixp": -230, "ixm": -210, "iyp": -125, "iym": -1140,
                   "oxp":  -24, "oxm":  -35, "oyp":  350, "oym":  1007}}

gpedestal = {1e9: {"ixp": 3277, "ixm": 3277, "iyp": 3277, "iym": 3277,
                   "oxp": 3277, "oxm": 3277, "oyp": 3277, "oym": 3277},
             1e10:{"ixp": 3277, "ixm": 3277, "iyp": 3277, "iym": 3277,
                   "oxp": 3277, "oxm": 3277, "oyp": 3277, "oym": 3277},
             1e11:{"ixp": 3140, "ixm": 3180, "iyp": 3190, "iym": 2910,
                   "oxp": 2780, "oxm": 3200, "oyp": 3210, "oym": 3200}}

# version 1.0 calibration: P,Q,R,S parameterization (2/21/2018)

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

# version 2.0 calibration: G,F,E parameterization (4/5/2018)

calparamG = {1e9: {"ixp": 1.0000, "ixm": 0.8552, "iyp": 1.0000, "iym": 1.0132,
                   "oxp": 1.0000, "oxm": 1.0000, "oyp": 1.0000, "oym": 0.8029},
             1e10:{"ixp": 1.0000, "ixm": 0.9001, "iyp": 1.0000, "iym": 0.9874,
                   "oxp": 1.0000, "oxm": 1.0000, "oyp": 1.0000, "oym": 0.8642},
             1e11:{"ixp": 1.0000, "ixm": 0.9605, "iyp": 1.0000, "iym": 1.0455,
                   "oxp": 1.0000, "oxm": 1.0000, "oyp": 1.0000, "oym": 0.9213}}
calparamF = {1e9: {"ixp": 0.1415, "ixm": -0.1053, "iyp": 0.1265, "iym": -0.1415,
                   "oxp": 0.0000, "oxm": -0.0000, "oyp": 0.0719, "oym": -0.0493},
             1e10:{"ixp": 0.1730, "ixm": -0.1200, "iyp": 0.1593, "iym": -0.1521,
                   "oxp": 0.0000, "oxm": -0.0000, "oyp": 0.0907, "oym": -0.0639},
             1e11:{"ixp": 0.1891, "ixm": -0.1588, "iyp": 0.1799, "iym": -0.1898,
                   "oxp": 0.0000, "oxm": -0.0000, "oyp": 0.0850, "oym": -0.0809}}
calparamE = {1e9: {"ixp": 0.01019, "ixm": 0.01340, "iyp": 0.01273, "iym": 0.01628,
                   "oxp": 1.00000, "oxm": 1.00000, "oyp": 0.01051, "oym": 0.00794},
             1e10:{"ixp": 0.01203, "ixm": 0.01457, "iyp": 0.02297, "iym": 0.02141,
                   "oxp": 1.00000, "oxm": 1.00000, "oyp": 0.01235, "oym": 0.01054},
             1e11:{"ixp": 0.02288, "ixm": 0.02176, "iyp": 0.02278, "iym": 0.02170,
                   "oxp": 1.00000, "oxm": 1.00000, "oyp": 0.00910, "oym": 0.00998}}

epicsvars = {"ixp": "IOCHDCOL:VMICADC1_1",
             "ixm": "IOCHDCOL:VMICADC2_1",
             "iyp": "IOCHDCOL:VMICADC3_1",
             "iym": "IOCHDCOL:VMICADC4_1",
             "oxp": "IOCHDCOL:VMICADC1_2",
             "oxm": "IOCHDCOL:VMICADC2_2",
             "oyp": "IOCHDCOL:VMICADC3_2",
             "oym": "IOCHDCOL:VMICADC4_2",
             "gain": "IAC5H01I_GAINXM",
             #"ixp_ped": "AC:inner:ped:x_plus",
             #"ixm_ped": "AC:inner:ped:x_minus",
             #"iym_ped": "AC:inner:ped:y_plus",
             #"iyp_ped": "AC:inner:ped:y_minus",
             #"oxp_ped": "AC:outer:ped:x_plus",
             #"oxm_ped": "AC:outer:ped:x_minus",
             #"oym_ped": "AC:outer:ped:y_plus",
             #"oyp_ped": "AC:outer:ped:y_minus",
             "cur": "IBCAD00CRCUR6",
             "xmo": "hd:collimator:x:motor.RBV",
             "ymo": "hd:collimator:y:motor.RBV",
             "xbp": "bpu_mean_x",
             "ybp": "bpu_mean_y",
             "bpu": "hd:bpu_at_a"}

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

   epicstime = stime * (1 << 28)
   mya1 = mysql_connection(nmya)
   cursor = mya1.cursor()
   if stime > 0:
      query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
               " WHERE time < {0:f}".format(epicstime) +
               " ORDER BY time DESC LIMIT {0}".format(nmax/2))
   else:
      query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
               " ORDER BY time DESC LIMIT {0}".format(nmax/2))
   cursor.execute(query)
   row = cursor.fetchall()
   if len(row) > 0:
      epicstime = row[-1][0]
      query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
               " WHERE time >= {0:f}".format(epicstime) +
               " ORDER BY time ASC LIMIT {0}".format(nmax))
      cursor.execute(query)
      rows = cursor.fetchall()
      epicsrecord[var] = rows[::-1]
      print var, "updated from", 
      print datetime.datetime.fromtimestamp(epicsrecord[var][-1][0]/(1 << 28)).strftime('%d.%m.%Y %H:%M:%S'),
      print "to",
      print datetime.datetime.fromtimestamp(epicsrecord[var][0][0]/(1 << 28)).strftime('%d.%m.%Y %H:%M:%S'),
      print ",", len(epicsrecord[var]), "elements"
   else:
      epicsrecord[var] = []
   cursor.close()

def get_epics_record(var, stime):
   epicstime = stime * (1 << 28)
   try:
      if epicsrecord[var][0][0] < epicstime:
         print "fast-forward", var
         update_epics_record(var, 1000, stime)
      elif epicsrecord[var][-1][0] > epicstime:
         print "rewind", var
         update_epics_record(var, 1000, stime)
   except:
      update_epics_record(var, 1000, stime)
   for row in epicsrecord[var]:
      if epicstime > row[0]:
         return row
   print "lookup of", var, "failed"
   return []

def follow():
   epoch = time.time()
   lastime = ""
   while True:
      pattern = '%d.%m.%Y %H:%M:%S'
      newtime = raw_input("Enter a date and time [dd.mm.yyyy hh:mm:ss]: ")
      if newtime:
         lastime = newtime
      else:
         newtime = lastime
      if len(newtime) == 0:
         pass
      elif newtime[0] == 'f': # fast-forward to the next FSD 
         while True:
            cur = get_epics_record("cur", epoch)
            if cur[1] > 0:
               epoch += 1
            else:
               break
      elif newtime[0] == 'r': # fast-forward to the next beam-on period
         while True:
            cur = get_epics_record("cur", epoch)
            if cur[1] < 10:
               epoch += 1
            else:
               break
      elif newtime[0] == '+':
         epoch += float(newtime)
      elif len(newtime) > 0 and newtime[0] == '-':
         epoch += float(newtime)
      else:
         try:
            epoch = int(time.mktime(time.strptime(newtime, pattern)))
         except:
            return
      record = {}
      for var in epicsvars:
         record[var] = get_epics_record(var, epoch)
      g = gains[record['gain'][1]]
      for var in ("ixp", "ixm", "iyp", "iym", "oxp", "oxm", "oyp", "oym"):
         if var + "_ped" in record and len(record[var + '_ped']) > 0:
            ped = record[var + '_ped'][1] * gpedestal[g][var]
         else:
            ped = pedestals[g][var]
         if len(record[var]) < 2:
            print "bad bad leroy brown...", var
            continue
         print var, ":", record[var][1], "-", ped,
         print "=", record[var][1] - ped
      current = record['cur'][1]
      print "current:", current
      repoch = record['ixp'][0] / (1 << 28)
      timestring = datetime.datetime.fromtimestamp(repoch).strftime('%d.%m.%Y %H:%M:%S')
      print timestring,
      print "gain: {0:.0e}".format(g),
      for var in ("ix", "iy", "ox", "oy"):
         if var + 'p_ped' in record and len(record[var + 'p_ped']) > 0:
            Ip_ped = record[var + 'p_ped'][1] * gpedestal[g][var + 'p']
            Im_ped = record[var + 'm_ped'][1] * gpedestal[g][var + 'm']
         else:
            Ip_ped = pedestals[g][var + 'p']
            Im_ped = pedestals[g][var + 'm']
         Ip = record[var + 'p'][1] - Ip_ped
         Im = record[var + 'm'][1] - Im_ped
         """ Old calibration, disabled
         P = calparamP[g][var]
         Q = calparamQ[g][var]
         R = calparamR[g][var]
         S = calparamS[g][var]
         x = S * (Ip - R * Im + P) / (Ip + R * Im + Q + 1e-99)
         """
         A = Ip * calparamE[g][var + 'm'] - Im * calparamE[g][var + 'p']
         B = Ip * calparamF[g][var + 'm'] - Im * calparamF[g][var + 'p']
         C = Ip * calparamG[g][var + 'm'] - Im * calparamG[g][var + 'p']
         D = B**2 - 4 * A * C
         if D > 0 and Ip + Im > 100:
            x = (-B - D**0.5) / (2 * A) 
         else:
            x = "***"
         print var, ":", x, "   ",
      print "xmo:", record['xmo'][1], "ymo:", record['ymo'][1]
   
      # keep track of my own pedestals, the EPICS values are not consistent
      if current == 0:
         f = 0.5
         for var in ("ixp", "ixm", "iyp", "iym", "oxp", "oxm", "oyp", "oym"):
            pedestals[g][var] = pedestals[g][var] * (1-f) + record[var][1] * f

   #close_mysql_connections()

def plot(vars=["ixp", "iyp", "oxp", "oyp", "cur", "bpu"], start=0, duration=0):
   pattern = '%d.%m.%Y %H:%M:%S'
   if start == 0:
      start = raw_input("Enter the start date and time [dd.mm.yyyy hh:mm:ss]: ")
   epoch = int(time.mktime(time.strptime(start, pattern)))
   if duration == 0:
      duration = raw_input("Enter the length of the period to plot [seconds]: ")
      duration = int(duration)
   global graphs
   graphs = {}
   vlimits = [0] * 2
   for var in vars:
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

      epicstime = [epoch * (1 << 28), (epoch + duration) * (1 << 28)]
      mya1 = mysql_connection(nmya)
      cursor = mya1.cursor()
      query = ("SELECT time, val1 FROM table_{0}".format(chan_id) +
               " WHERE time >= {0:f}".format(epicstime[0]) +
               " AND time <= {0:f}".format(epicstime[1]) +
               " ORDER BY time ASC LIMIT {0}".format(1000000))
      print "nmya is", nmya
      print "epoch of start:", epoch
      print "epoch of stop:", epoch + duration
      print "query is SELECT time, val1 FROM table_{0}".format(chan_id) +\
               " WHERE time >= {0:f}".format(epicstime[0]) +\
               " AND time <= {0:f}".format(epicstime[1]) +\
               " ORDER BY time ASC LIMIT {0}".format(1000000)
      cursor.execute(query)
      rows = cursor.fetchall()
      print var, "has", len(rows), "rows"
      ti = []
      va = []
      for (t, v) in rows:
         vlimits[0] = v if v < vlimits[0] else vlimits[0]
         vlimits[1] = v if v > vlimits[1] else vlimits[1]
         ti.append(t / (1 << 28) - epoch)
         va.append(v)
      if len(ti) > 0:
         graphs[var] = TGraph(len(ti), numpy.array(ti, dtype=float), 
                                       numpy.array(va, dtype=float))
   global hframe
   hframe = TH1D("hframe", "time chart", 1, 0, duration)
   hframe.GetXaxis().SetTitle("time (s) starting {0}".format(start))
   hframe.SetMinimum(vlimits[0])
   hframe.SetMaximum(vlimits[1])
   hframe.SetStats(0)
   hframe.Draw()
   color = 1
   for var in graphs:
      print "graphing", var
      graphs[var].SetLineColor(color)
      graphs[var].Draw("l")
      color += 1
