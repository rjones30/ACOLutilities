#!/bin/env python
#
# scans.py - script for viewing and fitting collimator scans
#            with recorded active collimator data.
#
# author: richard.t.jones at uconn.edu
# version: march 31, 2018

from ROOT import *

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

# original calibration performed on 2/21/2018
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

"""
# revised calibration performed on 3/31/2018
pedestals = {82: {"ixp":  -45, "ixm":  -44, "iyp":   -9, "iym":    -8,
                  "oxp":  960, "oxm":  -34, "oyp": -720, "oym":  -950},
             87: {"ixp": 1380, "ixm":  503, "iyp":  168, "iym":  -665,
                  "oxp":  -20, "oxm":  -35, "oyp": -520, "oym":  -705},
             86: {"ixp": -230, "ixm": -210, "iyp": -125, "iym": -1140,
                  "oxp":  -24, "oxm":  -35, "oyp":  350, "oym":  1007}}
"""

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
             "STsum": "ST_T_1_scaler_r1+ST_T_2_scaler_r1+ST_T_3_scaler_r1+ST_T_4_scaler_r1" +
                      "ST_T_5_scaler_r1+ST_T_6_scaler_r1+ST_T_7_scaler_r1+ST_T_8_scaler_r1" +
                      "ST_T_9_scaler_r1+ST_T_10_scaler_r1+ST_T_11_scaler_r1+ST_T_12_scaler_r1" +
                      "ST_T_13_scaler_r1+ST_T_14_scaler_r1+ST_T_15_scaler_r1+ST_T_16_scaler_r1" +
                      "ST_T_17_scaler_r1+ST_T_18_scaler_r1+ST_T_19_scaler_r1+ST_T_20_scaler_r1" +
                      "ST_T_21_scaler_r1+ST_T_22_scaler_r1+ST_T_23_scaler_r1+ST_T_24_scaler_r1" +
                      "ST_T_25_scaler_r1+ST_T_26_scaler_r1+ST_T_27_scaler_r1+ST_T_28_scaler_r1" +
                      "ST_T_29_scaler_r1+ST_T_30_scaler_r1",
             "atarg": "Active_Target_T_scaler_r1",
             "PSsum": "PSC_T_3_scaler_r1+PSC_T_4_scaler_r1+PSC_T_5_scaler_r1+PSC_T_6_scaler_r1" +
                      "PSC_T_7_scaler_r1+PSC_T_8_scaler_r1+PSC_T_9_scaler_r1+PSC_T_10_scaler_r1" +
                      "PSC_T_11_scaler_r1+PSC_T_12_scaler_r1+PSC_T_13_scaler_r1+PSC_T_14_scaler_r1" +
                      "PSC_T_15_scaler_r1+PSC_T_16_scaler_r1",
             }

def map2d(var, scan):
   global c1
   global tree
   global treefile
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
   varstring = "({0})/({1})".format(epicsvars[var], epicsvars["cur"])
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

def suppress_dead(h, scan):
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
         h.SetBinError(j,0)
   else:
      print "suppress_dead error - Unknown object, ignoring", h.GetName()
