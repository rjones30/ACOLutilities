#!/bin/env python
#
# scans.py - script for viewing and fitting collimator scans
#            with recorded active collimator data.
#
# author: richard.t.jones at uconn.edu
# version: march 31, 2018

from ROOT import *
import numpy
import math

# collimator scans taken 2/16/2018, 8/8/2020
gains = { 82: 1e9,
          86: 1e11,
          87: 1e10, 
         116: 1e8,
         117: 1e8,
        }

rootfile = { 82: "data/collimXY_scan_0082.root",
             86: "data/collimXY_scan_0086.root",
             87: "data/collimXY_scan_0087.root",
            116: "data/collimXY_scan_0116.root",
            117: "data/collimXY_scan_0117.root",
           }

xref = { 82: -114.04,
         86: -114.91,
         87: -114.90,
        116: -115.26,
        117: -115.26,
       }

yref = { 82: 4.79,
         86: 5.32,
         87: 5.30,
        116: 4.67,
        117: 4.67,
       }

xsteps = { 82: [ 9, -116.75, -112.25],
           86: [ 9, -116.75, -112.25],
           87: [ 9, -116.75, -112.25],
          116: [13, -118.25, -111.75],
          117: [13, -118.25, -111.75],
         }

ysteps = { 82: [ 9, 2.75, 7.25],
           86: [ 9, 2.75, 7.25],
           87: [ 9, 2.75, 7.25],
          116: [13, 1.45, 7.95],
          117: [13, 1.45, 7.95],
         }

dead = { 82: [[-116.5, 3.5],[-116.5,6.5],[-116,4]],
         86: [[-116.5, 3.0], [-116.5,5], [-116.5,7]],
         87: [[-116.5, 3.0]],
        116: [[-113.0, 6.2], [-112.5, 6.2], [-115.0, 3.2], [-118.0, 6.7]],
        117: [[-118.0, 5.2], [-118.0, 5.7], [-118.0, 7.2], 
              [-118.0, 3.7], [-116.0, 5.2], [-116.0, 5.7]],
       }

beamcur = { 82: 66.7,
            86: 100.6,
            87: 101.3,
           116: 66.1,
           117: 66.7,
          }

pedestals = { 82: {"ixp":  -45, "ixm":  -44, "iyp":   -9, "iym":    -8,
                   "oxp":  960, "oxm":  -34, "oyp": -720, "oym":  -950},
              87: {"ixp": 1380, "ixm":  503, "iyp":  168, "iym":  -665,
                   "oxp":  -20, "oxm":  -35, "oyp": -520, "oym":  -705},
              86: {"ixp": -230, "ixm": -210, "iyp": -125, "iym": -1140,
                   "oxp":  -24, "oxm":  -35, "oyp":  350, "oym":  1007},
             116: {"ixp": -205, "ixm": -118, "iyp":   10, "iym":    19,
                   "oxp":  -47, "oxm":  -49, "oyp":  -76, "oym":    -1},
             117: {"ixp": -205, "ixm": -118, "iyp":   10, "iym":    19,
                   "oxp":  -47, "oxm":  -49, "oyp":  -76, "oym":    -1},
            }

# original P,Q,R,S calibration performed on 2/21/2018
"""
pedestals = {82: {"ixp":  550, "ixm":  600, "iyp":  700, "iym":   700,
                  "oxp": 1150, "oxm":  -31, "oyp": -700, "oym":  -950},
             87: {"ixp": 1450, "ixm":  550, "iyp":  300, "iym":  -600,
                  "oxp":  -20, "oxm":  -31, "oyp": -480, "oym":  -650},
             86: {"ixp": -220, "ixm": -170, "iyp":  -76, "iym": -1130,
                  "oxp":  -20, "oxm":  -31, "oyp":  375, "oym":   950}}

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
"""

# revised P,Q,R,S calibration performed on 3/31/2018

calparamP = {82: {"ix":  595, "iy": -418, "ox": 0, "oy": 314},
             87: {"ix": 2138, "iy":  258, "ox": 0, "oy": 574},
             86: {"ix": 1314, "iy":  -82, "ox": 0, "oy": -88}}
calparamQ = {82: {"ix":-1457, "iy":-1380, "ox": 0, "oy":-1026},
             87: {"ix": -846, "iy": -207, "ox": 0, "oy": -493},
             86: {"ix": 2181, "iy": 2595, "ox": 0, "oy": -179}}
calparamR = {82: {"ix": 1.344, "iy": 0.894, "ox": 0, "oy": 1.460},
             87: {"ix": 1.442, "iy": 1.047, "ox": 0, "oy": 1.421},
             86: {"ix": 1.191, "iy": 0.948, "ox": 0, "oy": 1.051}}
calparamS = {82: {"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2},
             87: {"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2},
             86: {"ix": 6.3, "iy": 6.3, "ox": 11.2, "oy": 11.2}}

# version 2.0 calibration: G,F,E parameterization (4/5/2018)

calparamG = {82: {"ixp": 1.0000, "ixm": 0.8552, "iyp": 1.0000, "iym": 1.0132,
                  "oxp": 1.0000, "oxm": 1.0000, "oyp": 1.0000, "oym": 0.8029},
             87: {"ixp": 1.0000, "ixm": 0.9001, "iyp": 1.0000, "iym": 0.9874,
                  "oxp": 1.0000, "oxm": 1.0000, "oyp": 1.0000, "oym": 0.8642},
             86: {"ixp": 1.0000, "ixm": 0.9605, "iyp": 1.0000, "iym": 1.0455,
                  "oxp": 1.0000, "oxm": 1.0000, "oyp": 1.0000, "oym": 0.9213}}
calparamF = {82: {"ixp": 0.1415, "ixm": -0.1053, "iyp": 0.1265, "iym": -0.1415,
                  "oxp": 0.0000, "oxm": -0.0000, "oyp": 0.0719, "oym": -0.0493},
             87: {"ixp": 0.1730, "ixm": -0.1200, "iyp": 0.1593, "iym": -0.1521,
                  "oxp": 0.0000, "oxm": -0.0000, "oyp": 0.0907, "oym": -0.0639},
             86: {"ixp": 0.1891, "ixm": -0.1588, "iyp": 0.1799, "iym": -0.1898,
                  "oxp": 0.0000, "oxm": -0.0000, "oyp": 0.0850, "oym": -0.0809}}
calparamE = {82: {"ixp": 0.01019, "ixm": 0.01340, "iyp": 0.01273, "iym": 0.01628,
                  "oxp": 1.00000, "oxm": 1.00000, "oyp": 0.01051, "oym": 0.00794},
             87: {"ixp": 0.01203, "ixm": 0.01457, "iyp": 0.02297, "iym": 0.02141,
                  "oxp": 1.00000, "oxm": 1.00000, "oyp": 0.01235, "oym": 0.01054},
             86: {"ixp": 0.02288, "ixm": 0.02176, "iyp": 0.02278, "iym": 0.02170,
                  "oxp": 1.00000, "oxm": 1.00000, "oyp": 0.00910, "oym": 0.00998}}

# constants, not changed by the calibration

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
   """
   special value scan=116.5 returns the average value for scans 116 and 117
   with the dead channels suppressed to fill in the holes in each
   """
   global c1
   if scan == 116.5:
      h = map2d(var, 116)
      h116 = h.Clone("h116")
      h116.SetDirectory(0)
      h = map2d(var, 117)
      h117 = h.Clone("h117")
      h117.SetDirectory(0)
      h.SetTitle("{0} scan {1}".format(var, scan))
      for i in range(0, h.GetNbinsX()):
         for j in range(0, h.GetNbinsY()):
            z116 = h116.GetBinContent(i,j)
            z117 = h117.GetBinContent(i,j)
            if z116 > 0 and z117 > 0:
               h.SetBinContent(i,j, (z116 + z117)/2)
            elif z116 > 0:
               h.SetBinContent(i,j, z116)
            else:
               h.SetBinContent(i,j, z117)
      h.Draw("colz")
      c1.Update()
      return h
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
      c1 = TCanvas("c1", "c1", 50, 50, 540, 500)
      gPad.SetRightMargin(0.15)
   h = TH2D("h2d", "{0} scan {1}".format(var, scan),
            xsteps[scan][0], xsteps[scan][1], xsteps[scan][2],
            ysteps[scan][0], ysteps[scan][1], ysteps[scan][2])
   xystring = "{1}:{0}".format(epicsvars['xmo'], epicsvars['ymo'])
   varstring = "({0})*({1})/({2})".format(epicsvars[var], 
                                          beamcur[scan],
                                          epicsvars["cur"])
   tree.Draw(xystring + ">>h2d", varstring)
   h.GetXaxis().SetTitle("x motor (mm)")
   h.GetYaxis().SetTitle("y motor (mm)")
   h.GetYaxis().SetTitleOffset(1.4)
   h.SetContour(100)
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
   S = calparamS[scan]['ix']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['ix'] = P
   calparamQ[scan]['ix'] = Q
   calparamR[scan]['ix'] = R
   print "inner x+ fit parameters:", pcross, pslope / pcross, ap[2] / pcross
   print "inner x- fit parameters:", mcross, mslope / mcross, am[2] / mcross
   calparamG[scan]['ixp'] = 1
   calparamG[scan]['ixm'] = mcross / pcross
   calparamF[scan]['ixp'] = pslope / pcross
   calparamF[scan]['ixm'] = mslope / pcross
   calparamE[scan]['ixp'] = ap[2] / pcross
   calparamE[scan]['ixm'] = am[2] / pcross

def calibrate_iy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('iyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('iym', scan)
   hmy = proy(hm, row1, row2, scan)
   fitp = hpy.Fit("pol2", "s")
   fitm = hmy.Fit("pol2", "s")
   hpy.Draw("same")
   ap = [fitp.Parameter(i) for i in range(0,3)]
   am = [fitm.Parameter(i) for i in range(0,3)]
   pslope = 2 * ap[2] * yref[scan] + ap[1]
   mslope = 2 * am[2] * yref[scan] + am[1]
   pcross = ap[2] * yref[scan]**2 + ap[1] * yref[scan] + ap[0]
   mcross = am[2] * yref[scan]**2 + am[1] * yref[scan] + am[0]
   pcross -= pedestals[scan]['iyp']
   mcross -= pedestals[scan]['iym']
   S = calparamS[scan]['iy']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['iy'] = P
   calparamQ[scan]['iy'] = Q
   calparamR[scan]['iy'] = R
   print "inner y+ fit parameters:", pcross, pslope/pcross, ap[2]/pcross
   print "inner y- fit parameters:", mcross, mslope/mcross, am[2]/mcross
   calparamG[scan]['iyp'] = 1
   calparamG[scan]['iym'] = mcross / pcross
   calparamF[scan]['iyp'] = pslope / pcross
   calparamF[scan]['iym'] = mslope / pcross
   calparamE[scan]['iyp'] = ap[2] / pcross
   calparamE[scan]['iym'] = am[2] / pcross

def calibrate_ox(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oxp', scan)
   hpx = prox(hp, row1, row2, scan)
   hm = map2d('oxm', scan)
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
   pcross -= pedestals[scan]['oxp']
   mcross -= pedestals[scan]['oxm']
   S = calparamS[scan]['ox']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['ox'] = P
   calparamQ[scan]['ox'] = Q
   calparamR[scan]['ox'] = R
   print "outer x+ fit parameters:", pcross, pslope/pcross, ap[2]/pcross
   print "outer x- fit parameters:", mcross, mslope/mcross, am[2]/mcross
   calparamG[scan]['oxp'] = 1
   calparamG[scan]['oxm'] = mcross / pcross
   calparamF[scan]['oxp'] = pslope / pcross
   calparamF[scan]['oxm'] = mslope / pcross
   calparamE[scan]['oxp'] = ap[2] / pcross
   calparamE[scan]['oxm'] = am[2] / pcross

def calibrate_oy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('oym', scan)
   hmy = proy(hm, row1, row2, scan)
   fitp = hpy.Fit("pol2", "s")
   fitm = hmy.Fit("pol2", "s")
   hpy.Draw("same")
   ap = [fitp.Parameter(i) for i in range(0,3)]
   am = [fitm.Parameter(i) for i in range(0,3)]
   pslope = 2 * ap[2] * yref[scan] + ap[1]
   mslope = 2 * am[2] * yref[scan] + am[1]
   pcross = ap[2] * yref[scan]**2 + ap[1] * yref[scan] + ap[0]
   mcross = am[2] * yref[scan]**2 + am[1] * yref[scan] + am[0]
   pcross -= pedestals[scan]['oyp']
   mcross -= pedestals[scan]['oym']
   S = calparamS[scan]['oy']
   R = -pslope / mslope
   P = R * mcross - pcross
   Q = 2 * S * pslope - pcross - R * mcross
   calparamP[scan]['oy'] = P
   calparamQ[scan]['oy'] = Q
   calparamR[scan]['oy'] = R
   print "outer y+ fit parameters:", pcross, pslope/pcross, ap[2]/pcross
   print "outer y- fit parameters:", mcross, mslope/mcross, am[2]/mcross
   calparamG[scan]['oyp'] = 1
   calparamG[scan]['oym'] = mcross / pcross
   calparamF[scan]['oyp'] = pslope / pcross
   calparamF[scan]['oym'] = mslope / pcross
   calparamE[scan]['oyp'] = ap[2] / pcross
   calparamE[scan]['oym'] = am[2] / pcross

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
   for i in range(1, xsteps[scan][0] + 1):
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

def check2_ix(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('ixp', scan)
   hpx = prox(hp, row1, row2, scan)
   hm = map2d('ixm', scan)
   hmx = prox(hm, row1, row2, scan)
   hix = hpx.Clone("hix")
   hix.SetTitle("inner x calibration check, scan {0}".format(scan))
   for i in range(1, xsteps[scan][0] + 1):
      Ip = hpx.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['ixp']
      Im = hmx.GetBinContent(i)
      Im -= pedestals[scan]['ixm']
      A = Ip * calparamE[scan]['ixm'] - Im * calparamE[scan]['ixp']
      B = Ip * calparamF[scan]['ixm'] - Im * calparamF[scan]['ixp']
      C = Ip * calparamG[scan]['ixm'] - Im * calparamG[scan]['ixp']
      D = B**2 - 4 * A * C
      xin = (-B - D**0.5) / (2 * A) 
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
   for i in range(1, ysteps[scan][0] + 1):
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

def check2_iy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('iyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('iym', scan)
   hmy = proy(hm, row1, row2, scan)
   hiy = hpy.Clone("hiy")
   hiy.SetTitle("inner y calibration check, scan {0}".format(scan))
   for i in range(1, ysteps[scan][0] + 1):
      Ip = hpy.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['iyp']
      Im = hmy.GetBinContent(i)
      Im -= pedestals[scan]['iym']
      A = Ip * calparamE[scan]['iym'] - Im * calparamE[scan]['iyp']
      B = Ip * calparamF[scan]['iym'] - Im * calparamF[scan]['iyp']
      C = Ip * calparamG[scan]['iym'] - Im * calparamG[scan]['iyp']
      D = B**2 - 4 * A * C
      yin = (-B - D**0.5) / (2 * A) 
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
   for i in range(1, xsteps[scan][0] + 1):
      Ip = hpx.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['oxp']
      Im = hmx.GetBinContent(i)
      Im -= pedestals[scan]['oxm']
      xout = (Ip - R * Im + P) / (Ip + R * Im + Q) * S
      hox.SetBinContent(i, xout)
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

def check2_ox(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oxp', scan)
   hpx = prox(hp, row1, row2, scan)
   hm = map2d('oxm', scan)
   hmx = prox(hm, row1, row2, scan)
   hox = hpx.Clone("hox")
   hox.SetTitle("inner x calibration check, scan {0}".format(scan))
   for i in range(1, xsteps[scan][0] + 1):
      Ip = hpx.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['oxp']
      Im = hmx.GetBinContent(i)
      Im -= pedestals[scan]['oxm']
      A = Ip * calparamE[scan]['oxm'] - Im * calparamE[scan]['oxp']
      B = Ip * calparamF[scan]['oxm'] - Im * calparamF[scan]['oxp']
      C = Ip * calparamG[scan]['oxm'] - Im * calparamG[scan]['oxp']
      D = B**2 - 4 * A * C
      xout = (-B - D**0.5) / (2 * A) 
      hox.SetBinContent(i, xout)
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
   for i in range(1, ysteps[scan][0] + 1):
      Ip = hpy.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['oyp']
      Im = hmy.GetBinContent(i)
      Im -= pedestals[scan]['oym']
      yout = (Ip - R * Im + P) / (Ip + R * Im + Q) * S
      hoy.SetBinContent(i, yout)
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

def check2_oy(scan, row1=0, row2=0):
   if scan == 0 and lastscan > 0:
      scan = lastscan
   hp = map2d('oyp', scan)
   hpy = proy(hp, row1, row2, scan)
   hm = map2d('oym', scan)
   hmy = proy(hm, row1, row2, scan)
   hoy = hpy.Clone("hoy")
   hoy.SetTitle("inner y calibration check, scan {0}".format(scan))
   for i in range(1, ysteps[scan][0] + 1):
      Ip = hpy.GetBinContent(i)
      if Ip == 0:
         continue
      Ip -= pedestals[scan]['oyp']
      Im = hmy.GetBinContent(i)
      Im -= pedestals[scan]['oym']
      A = Ip * calparamE[scan]['oym'] - Im * calparamE[scan]['oyp']
      B = Ip * calparamF[scan]['oym'] - Im * calparamF[scan]['oyp']
      C = Ip * calparamG[scan]['oym'] - Im * calparamG[scan]['oyp']
      D = B**2 - 4 * A * C
      yout = (-B - D**0.5) / (2 * A) 
      hoy.SetBinContent(i, yout)
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
   """
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
   """
   print "G values: "
   for scan in gains:
      print " ", scan, ":",
      print "{0:6.4f}".format(calparamG[scan]['ixp']),
      print "{0:6.4f}".format(calparamG[scan]['ixm']),
      print "   ",
      print "{0:6.4f}".format(calparamG[scan]['iyp']),
      print "{0:6.4f}".format(calparamG[scan]['iym']),
      print "   ",
      print "{0:6.4f}".format(calparamG[scan]['oxp']),
      print "{0:6.4f}".format(calparamG[scan]['oxm']),
      print "   ",
      print "{0:6.4f}".format(calparamG[scan]['oyp']),
      print "{0:6.4f}".format(calparamG[scan]['oym'])
   print "F values: "
   for scan in gains:
      print " ", scan, ":",
      print "{0:6.4f}".format(calparamF[scan]['ixp']),
      print "{0:6.4f}".format(calparamF[scan]['ixm']),
      print "   ",
      print "{0:6.4f}".format(calparamF[scan]['iyp']),
      print "{0:6.4f}".format(calparamF[scan]['iym']),
      print "   ",
      print "{0:6.4f}".format(calparamF[scan]['oxp']),
      print "{0:6.4f}".format(calparamF[scan]['oxm']),
      print "   ",
      print "{0:6.4f}".format(calparamF[scan]['oyp']),
      print "{0:6.4f}".format(calparamF[scan]['oym'])
   print "E values: "
   for scan in gains:
      print " ", scan, ":",
      print "{0:6.5f}".format(calparamE[scan]['ixp']),
      print "{0:6.5f}".format(calparamE[scan]['ixm']),
      print "  ",
      print "{0:6.5f}".format(calparamE[scan]['iyp']),
      print "{0:6.5f}".format(calparamE[scan]['iym']),
      print "   ",
      print "{0:6.5f}".format(calparamE[scan]['oxp']),
      print "{0:6.4f}".format(calparamE[scan]['oxm']),
      print "  ",
      print "{0:6.5f}".format(calparamE[scan]['oyp']),
      print "{0:6.5f}".format(calparamE[scan]['oym'])

##################################################################
# Below are the functions that I added to do the calibration
# of the active collimator response with bias voltage applied,
# without the more complicated scheme that was developed for
# dealing with the squirrelly behavior of the unbiased device.
##################################################################

def map_asym(var1, var2, scan):
   h = map2d(var1, scan)
   hplus = h.Clone("hplus")
   hplus.SetDirectory(0)
   h = map2d(var2, scan)
   hminus = h.Clone("hminus")
   hminus.SetDirectory(0)
   hsum = hplus.Clone("hsum")
   hsum.Add(hminus)
   hasym = hplus.Clone("hasym")
   hasym.Add(hminus, -1)
   hasym.Divide(hsum)
   hasym.SetTitle("{0}-{1} asymmetry from scan {2}".format(var1, var2, scan))
   hasym.SetContour(100)
   hasym.Draw("colz")
   c1.Update()
   return hasym

def poly3(var, par):
   return sum([par[i] * (var[0] - par[0])**i for i in range(1,4)])

def fit_pol3(h1d):
   nx = h1d.GetNbinsX()
   x0 = h1d.GetXaxis().GetBinLowEdge(1)
   x1 = h1d.GetXaxis().GetBinUpEdge(nx)
   foly3 = TF1("foly3", poly3, x0, x1, 4)
   foly3.SetParameter(0, (x0 + x1)/2)
   foly3.SetParameter(1, 1)
   foly3.SetParameter(2, 1e-3)
   foly3.SetParameter(3, 1e-3)
   fres = h1d.Fit(foly3, "s")
   redchi2 = h1d.Chisquare(foly3) / (nx - 4)
   for i in range(0, nx):
      sigma = h1d.GetBinError(i+1)
      h1d.SetBinError(i+1, sigma * redchi2**0.5)
   return h1d.Fit(foly3, "s")

def do_cal_fits(scan=116.5):
   hix = map_asym('ixp', 'ixm', scan)
   hix.SetDirectory(0)
   hiy = map_asym('iyp', 'iym', scan)
   hiy.SetDirectory(0)
   hox = map_asym('oxp', 'oxm', scan)
   hox.SetDirectory(0)
   hoy = map_asym('oyp', 'oym', scan)
   hoy.SetDirectory(0)
   c1 = gROOT.FindObject("c1")
   for h in (hix, hiy, hox, hoy):
      h.Smooth()
      h.Draw("colz")
      c1.Update()
      c1.Print("ac_" + h.GetName() + ".png")
   hixp = hix.ProjectionX("hixp", 7, 7)
   hiyp = hiy.ProjectionY("hiyp", 7, 7)
   hoxp = hox.ProjectionX("hoxp", 7, 7)
   hoyp = hoy.ProjectionY("hoyp", 7, 7)
   gStyle.SetOptFit()
   gStyle.SetOptStat(0)
   gStyle.SetStatX(0.5)
   gStyle.SetStatY(0.85)
   for h in (hixp, hiyp, hoxp, hoyp):
      fit_pol3(h)
      c1.Update()
      c1.Print("ac_" + h.GetName() + ".png")
