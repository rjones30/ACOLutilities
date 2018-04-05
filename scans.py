#!/bin/env python
#
# scans.py - script for viewing and fitting collimator scans
#            with recorded active collimator data.
#
# author: richard.t.jones at uconn.edu
# version: march 31, 2018

from ROOT import *
import numpy

# collimator scans taken 2/16/2018
gains = {82: 1e9, 86: 1e11, 87: 1e10}
rootfile = {82: "data/collimXY_scan_0082.root",
            86: "data/collimXY_scan_0086.root",
            87: "data/collimXY_scan_0087.root"}
xref = {82: -114.04, 86: -114.91, 87: -114.90}
yref = {82:    4.79, 86:    5.32, 87:    5.30}
xsteps = [9, -116.75, -112.25]
ysteps = [9, 2.75, 7.25]
dead = {82: [[-116.5, 3.5],[-116.5,6.5],[-116,4]],
        86: [[-116.5, 3], [-116.5,5], [-116.5,7]],
        87: [[-116.5, 3]]}
beamcur = {82: 66.7, 86: 100.6, 87: 101.3}

# original calibration performed on 2/21/2018
"""
pedestals = {82: {"ixp":  550, "ixm":  600, "iyp":  700, "iym":   700,
                  "oxp": 1150, "oxm":  -31, "oyp": -700, "oym":  -950},
             87: {"ixp": 1450, "ixm":  550, "iyp":  300, "iym":  -600,
                  "oxp":  -20, "oxm":  -31, "oyp": -480, "oym":  -650},
             86: {"ixp": -220, "ixm": -170, "iyp":  -76, "iym": -1130,
                  "oxp":  -20, "oxm":  -31, "oyp":  375, "oym":   950}}
"""

calparamP = {82: {"ix": 1026, "iy": -311, "ox": 0, "oy": -76},
             87: {"ix": 1512, "iy":  732, "ox": 0, "oy": 470},
             86: {"ix": 1175, "iy": 1134, "ox": 0, "oy": 657}}
calparamQ = {82: {"ix": -438, "iy":  273, "ox": 0, "oy": -729},
             87: {"ix": -472, "iy": -573, "ox": 0, "oy": -551},
             86: {"ix": 2051, "iy": 1646, "ox": 0, "oy": -540}}
calparamR = {82: {"ix": 1.604, "iy": 0.909, "ox": 0, "oy": 1.178},
             87: {"ix": 1.347, "iy": 1.112, "ox": 0, "oy": 1.392},
             86: {"ix": 1.184, "iy": 1.077, "ox": 0, "oy": 1.307}}
calparamS = {82: {"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2},
             87: {"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2},
             86: {"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2}}

# revised calibration performed on 3/31/2018
pedestals = {82: {"ixp":  -45, "ixm":  -44, "iyp":   -9, "iym":    -8,
                  "oxp":  960, "oxm":  -34, "oyp": -720, "oym":  -950},
             87: {"ixp": 1380, "ixm":  503, "iyp":  168, "iym":  -665,
                  "oxp":  -20, "oxm":  -35, "oyp": -520, "oym":  -705},
             86: {"ixp": -230, "ixm": -210, "iyp": -125, "iym": -1140,
                  "oxp":  -24, "oxm":  -35, "oyp":  350, "oym":  1007}}

epicsvars = {"ixp": "IOCHDCOL_VMICADC1_1",
             "ixm": "IOCHDCOL_VMICADC2_1",
             "iyp": "IOCHDCOL_VMICADC3_1",
             "iym": "IOCHDCOL_VMICADC4_1",
             "oxp": "IOCHDCOL_VMICADC1_2",
             "oxm": "IOCHDCOL_VMICADC2_2",
             "oyp": "IOCHDCOL_VMICADC3_2",
             "oym": "IOCHDCOL_VMICADC4_2",
             "cur": "IBCAD00CRCUR6",
             "xmo": "hd_collimator_x_motor_RBV",
             "ymo": "hd_collimator_y_motor_RBV",
             "xbp": "bpu_mean_x",
             "ybp": "bpu_mean_y",
             "psc": "PSC_coinc_scaler_rate",
             "STsum": "ST_T_1_scaler_r1+ST_T_2_scaler_r1+ST_T_3_scaler_r1+ST_T_4_scaler_r1+" +
                      "ST_T_5_scaler_r1+ST_T_6_scaler_r1+ST_T_7_scaler_r1+ST_T_8_scaler_r1+" +
                      "ST_T_9_scaler_r1+ST_T_10_scaler_r1+ST_T_11_scaler_r1+ST_T_12_scaler_r1+" +
                      "ST_T_13_scaler_r1+ST_T_14_scaler_r1+ST_T_15_scaler_r1+ST_T_16_scaler_r1+" +
                      "ST_T_17_scaler_r1+ST_T_18_scaler_r1+ST_T_19_scaler_r1+ST_T_20_scaler_r1+" +
                      "ST_T_21_scaler_r1+ST_T_22_scaler_r1+ST_T_23_scaler_r1+ST_T_24_scaler_r1+" +
                      "ST_T_25_scaler_r1+ST_T_26_scaler_r1+ST_T_27_scaler_r1+ST_T_28_scaler_r1+" +
                      "ST_T_29_scaler_r1+ST_T_30_scaler_r1",
             "atarg": "Active_Target_T_scaler_r1",
             "PSsum": "PSC_T_3_scaler_r1+PSC_T_4_scaler_r1+PSC_T_5_scaler_r1+PSC_T_6_scaler_r1+" +
                      "PSC_T_7_scaler_r1+PSC_T_8_scaler_r1+PSC_T_9_scaler_r1+PSC_T_10_scaler_r1+" +
                      "PSC_T_11_scaler_r1+PSC_T_12_scaler_r1+PSC_T_13_scaler_r1+PSC_T_14_scaler_r1+" +
                      "PSC_T_15_scaler_r1+PSC_T_16_scaler_r1",
             }

lastscan = 0

def map2d(var, scan):
   global c1
   global tree
   global treefile
   global lastscan
   lastscan = scan
   treefile = TFile(rootfile[scan])
   tree = treefile.Get("theTree")
   h = gROOT.FindObject("h2d")
   if h:
      h.Delete()
   c1 = gROOT.FindObject("c1")
   if not c1:
      c1 = TCanvas("c1", "c1", 50, 50, 500, 500)
   h = TH2D("h2d", "{0} scan {1}".format(var, scan),
            xsteps[0], xsteps[1], xsteps[2], ysteps[0], ysteps[1], ysteps[2])
   xystring = "{1}:{0}".format(epicsvars['xmo'], epicsvars['ymo'])
   varstring = "({0})*({1})/({2})".format(epicsvars[var], 
                                          beamcur[scan],
                                          epicsvars["cur"])
   tree.Draw(xystring + ">>h2d", varstring)
   h.GetXaxis().SetTitle("x motor (mm)")
   h.GetYaxis().SetTitle("y motor (mm)")
   h.GetYaxis().SetTitleOffset(1.4)
   h.SetDirectory(0)
   h.SetStats(0)
   suppress_dead(h, scan)
   h.Draw("colz")
   c1.Update()
   return h

def suppress_dead(h, scan=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   if h.Class().GetName() == "TH2D":
      for p in dead[scan]:
         i = h.GetXaxis().FindBin(p[0])
         j = h.GetYaxis().FindBin(p[1])
         h.SetBinContent(i,j,0)
         h.SetBinError(i,j,0)
   elif h.GetXaxis().GetTitle()[0] == 'x':
      for p in dead[scan]:
         i = h.GetXaxis().FindBin(p[0])
         h.SetBinContent(i,0)
         h.SetBinError(i,0)
   elif h.GetXaxis().GetTitle()[0] == 'y':
      for p in dead[scan]:
         j = h.GetXaxis().FindBin(p[1])
         h.SetBinContent(j,0)
         h.SetBinError(j,0)
   else:
      print "suppress_dead error - Unknown object, ignoring", h.GetName()
   return h

def prox(h2d, row1=0, row2=0, scan=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   if row1 == 0:
      row1 = 1
   if row2 == 0:
      row2 = h2d.GetNbinsX()
   mapx = gROOT.FindObject("mapx")
   if mapx:
      mapx.Delete()
   mapx = h2d.ProjectionX("mapx", row1, row2)
   mapx.Scale(1.0 / (row2 - row1 + 1))
   for i in range(row1, row2 + 1):
      mapx.SetBinError(i, 0.01 * mapx.GetBinContent(i))
   mapx.SetStats(0)
   mapx.SetDirectory(0)
   return suppress_dead(mapx)

def proy(h2d, row1=0, row2=0, scan=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   if row1 == 0:
      row1 = 1
   if row2 == 0:
      row2 = h2d.GetNbinsX()
   mapy = gROOT.FindObject("mapy")
   if mapy:
      mapy.Delete()
   mapy = h2d.ProjectionY("mapy", row1, row2)
   mapy.Scale(1.0 / (row2 - row1 + 1))
   for i in range(row1, row2 + 1):
      mapy.SetBinError(i, 0.01 * mapy.GetBinContent(i))
   mapy.SetStats(0)
   mapy.SetDirectory(0)
   return suppress_dead(mapy)

def calibrate_ix(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('ixp', scan)
   hpx = prox(hp, row1, row2, scan)
   hm = map2d('ixm', scan)
   hmx = prox(hm, row1, row2, scan)
   fitp = hpx.Fit("pol2", "s")
   fitm = hmx.Fit("pol2", "s")
   hpx.Draw("same")
   ap = [fitp.Parameter(i) for i in range(0,3)]
   am = [fitm.Parameter(i) for i in range(0,3)]
   pslope = 2 * ap[2] * xref[scan] + ap[1]
   mslope = 2 * am[2] * xref[scan] + am[1]
   pcross = ap[2] * xref[scan]**2 + ap[1] * xref[scan] + ap[0]
   mcross = am[2] * xref[scan]**2 + am[1] * xref[scan] + am[0]
   pcross -= pedestals[scan]['ixp']
   mcross -= pedestals[scan]['ixm']
   print "inner x+ fit parameters:", pcross, pslope/pcross, ap[2]/pcross
   print "inner x- fit parameters:", mcross, mslope/mcross, am[2]/mcross
   S = calparamS[scan]['ix']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['ix'] = P
   calparamQ[scan]['ix'] = Q
   calparamR[scan]['ix'] = R

def calibrate_iy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('iyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('iym', scan)
   hmy = proy(hm, row1, row2, scan)
   fitp = hpy.Fit("pol2", "s")
   fitm = hmy.Fit("pol2", "s")
   ap = [fitp.Parameter(i) for i in range(0,3)]
   am = [fitm.Parameter(i) for i in range(0,3)]
   pslope = 2 * ap[2] * yref[scan] + ap[1]
   mslope = 2 * am[2] * yref[scan] + am[1]
   pcross = ap[2] * yref[scan]**2 + ap[1] * yref[scan] + ap[0]
   mcross = am[2] * yref[scan]**2 + am[1] * yref[scan] + am[0]
   pcross -= pedestals[scan]['iyp']
   mcross -= pedestals[scan]['iym']
   print "inner y+ fit parameters:", pcross, pslope/pcross, ap[2]/pcross
   print "inner y- fit parameters:", mcross, mslope/mcross, am[2]/mcross
   S = calparamS[scan]['iy']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['iy'] = P
   calparamQ[scan]['iy'] = Q
   calparamR[scan]['iy'] = R

def calibrate_ox(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oxp', scan)
   hpx = prox(hp, row1, row2, scan)
   hm = map2d('oxm', scan)
   hmx = prox(hm, row1, row2, scan)
   fitp = hpx.Fit("pol2", "s")
   fitm = hmx.Fit("pol2", "s")
   ap = [fitp.Parameter(i) for i in range(0,3)]
   am = [fitm.Parameter(i) for i in range(0,3)]
   pslope = 2 * ap[2] * xref[scan] + ap[1]
   mslope = 2 * am[2] * xref[scan] + am[1]
   pcross = ap[2] * xref[scan]**2 + ap[1] * xref[scan] + ap[0]
   mcross = am[2] * xref[scan]**2 + am[1] * xref[scan] + am[0]
   pcross -= pedestals[scan]['oxp']
   mcross -= pedestals[scan]['oxm']
   print "outer x+ fit parameters:", pcross, pslope/pcross, ap[2]/pcross
   print "outer x- fit parameters:", mcross, mslope/mcross, am[2]/mcross
   S = calparamS[scan]['ox']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['ox'] = P
   calparamQ[scan]['ox'] = Q
   calparamR[scan]['ox'] = R

def calibrate_oy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('oym', scan)
   hmy = proy(hm, row1, row2, scan)
   fitp = hpy.Fit("pol2", "s")
   fitm = hmy.Fit("pol2", "s")
   ap = [fitp.Parameter(i) for i in range(0,3)]
   am = [fitm.Parameter(i) for i in range(0,3)]
   pslope = 2 * ap[2] * yref[scan] + ap[1]
   mslope = 2 * am[2] * yref[scan] + am[1]
   pcross = ap[2] * yref[scan]**2 + ap[1] * yref[scan] + ap[0]
   mcross = am[2] * yref[scan]**2 + am[1] * yref[scan] + am[0]
   pcross -= pedestals[scan]['oyp']
   mcross -= pedestals[scan]['oym']
   print "outer y+ fit parameters:", pcross, pslope/pcross, ap[2]/pcross
   print "outer y- fit parameters:", mcross, mslope/mcross, am[2]/mcross
   S = calparamS[scan]['oy']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['oy'] = P
   calparamQ[scan]['oy'] = Q
   calparamR[scan]['oy'] = R

def check_ix(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('ixp', scan)
   hpx = prox(hp, row1, row2, scan)
   hm = map2d('ixm', scan)
   hmx = prox(hm, row1, row2, scan)
   P = calparamP[scan]['ix']
   Q = calparamQ[scan]['ix']
   R = calparamR[scan]['ix']
   S = calparamS[scan]['ix']
   hix = hpx.Clone("hix")
   hix.SetTitle("inner x calibration check, scan {0}".format(scan))
   for i in range(1, xsteps[0] + 1):
      Ip = hpx.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['ixp']
      Im = hmx.GetBinContent(i)
      Im -= pedestals[scan]['ixm']
      xin = (Ip - R * Im + P) / (Ip + R * Im + Q) * S
      hix.SetBinContent(i, xin)
      hix.SetBinError(i, 0.05)
   res = hix.Fit("pol1","s")
   x = numpy.array([xref[scan], xref[scan]], dtype=float)
   y = numpy.array([-5, 5], dtype=float)
   global g
   g = TGraph(2, x, y)
   g.SetLineColor(kBlue)
   g.Draw("l")
   print "zero crossing is", -res.Parameter(0) / res.Parameter(1)
   return hix

def check_iy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('iyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('iym', scan)
   hmy = proy(hm, row1, row2, scan)
   P = calparamP[scan]['iy']
   Q = calparamQ[scan]['iy']
   R = calparamR[scan]['iy']
   S = calparamS[scan]['iy']
   hiy = hpy.Clone("hiy")
   hiy.SetTitle("inner y calibration check, scan {0}".format(scan))
   for i in range(1, ysteps[0] + 1):
      Ip = hpy.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['iyp']
      Im = hmy.GetBinContent(i)
      Im -= pedestals[scan]['iym']
      yin = (Ip - R * Im + P) / (Ip + R * Im + Q) * S
      hiy.SetBinContent(i, yin)
      hiy.SetBinError(i, 0.05)
   res = hiy.Fit("pol1","s")
   x = numpy.array([yref[scan], yref[scan]], dtype=float)
   y = numpy.array([-5, 5], dtype=float)
   global g
   g = TGraph(2, x, y)
   g.SetLineColor(kBlue)
   g.Draw("l")
   print "zero crossing is", -res.Parameter(0) / res.Parameter(1)
   return hiy

def check_ox(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oxp', scan)
   hpx = prox(hp, row1, row2, scan)
   hm = map2d('oxm', scan)
   hmx = prox(hm, row1, row2, scan)
   P = calparamP[scan]['ox']
   Q = calparamQ[scan]['ox']
   R = calparamR[scan]['ox']
   S = calparamS[scan]['ox']
   hox = hpx.Clone("hox")
   hox.SetTitle("inner x calibration check, scan {0}".format(scan))
   for i in range(1, xsteps[0] + 1):
      Ip = hpx.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['oxp']
      Im = hmx.GetBinContent(i)
      Im -= pedestals[scan]['oxm']
      xin = (Ip - R * Im + P) / (Ip + R * Im + Q) * S
      hox.SetBinContent(i, xin)
      hox.SetBinError(i, 0.05)
   res = hox.Fit("pol1","s")
   x = numpy.array([xref[scan], xref[scan]], dtype=float)
   y = numpy.array([-5, 5], dtype=float)
   global g
   g = TGraph(2, x, y)
   g.SetLineColor(kBlue)
   g.Draw("l")
   print "zero crossing is", -res.Parameter(0) / res.Parameter(1)
   return hox

def check_oy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('oym', scan)
   hmy = proy(hm, row1, row2, scan)
   P = calparamP[scan]['oy']
   Q = calparamQ[scan]['oy']
   R = calparamR[scan]['oy']
   S = calparamS[scan]['oy']
   hoy = hpy.Clone("hoy")
   hoy.SetTitle("inner y calibration check, scan {0}".format(scan))
   for i in range(1, ysteps[0] + 1):
      Ip = hpy.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['oyp']
      Im = hmy.GetBinContent(i)
      Im -= pedestals[scan]['oym']
      yin = (Ip - R * Im + P) / (Ip + R * Im + Q) * S
      hoy.SetBinContent(i, yin)
      hoy.SetBinError(i, 0.05)
   res = hoy.Fit("pol1","s")
   x = numpy.array([yref[scan], yref[scan]], dtype=float)
   y = numpy.array([-5, 5], dtype=float)
   global g
   g = TGraph(2, x, y)
   g.SetLineColor(kBlue)
   g.Draw("l")
   print "zero crossing is", -res.Parameter(0) / res.Parameter(1)
   return hoy

def docal():
   for scan in gains:
      calibrate_ix(scan)
      calibrate_iy(scan)
      calibrate_ox(scan)
      calibrate_oy(scan)
   print "R values: "
   for scan in gains:
      print " ", scan, ":",
      print "{0:.3f}".format(calparamR[scan]['ix']),
      print "{0:.3f}".format(calparamR[scan]['iy']),
      print "{0:.3f}".format(calparamR[scan]['ox']),
      print "{0:.3f}".format(calparamR[scan]['oy'])
   print "P values: "
   for scan in gains:
      print " ", scan, ":",
      print "{0:.0f}".format(calparamP[scan]['ix']),
      print "{0:.0f}".format(calparamP[scan]['iy']),
      print "{0:.0f}".format(calparamP[scan]['ox']),
      print "{0:.0f}".format(calparamP[scan]['oy'])
   print "Q values: "
   for scan in gains:
      print " ", scan, ":",
      print "{0:.0f}".format(calparamQ[scan]['ix']),
      print "{0:.0f}".format(calparamQ[scan]['iy']),
      print "{0:.0f}".format(calparamQ[scan]['ox']),
      print "{0:.0f}".format(calparamQ[scan]['oy'])
   print "S values: "
   for scan in gains:
      print " ", scan, ":",
      print "{0:6}".format(calparamS[scan]['ix']),
      print "{0:6}".format(calparamS[scan]['iy']),
      print "{0:6}".format(calparamS[scan]['ox']),
      print "{0:6}".format(calparamS[scan]['oy'])
