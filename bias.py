#/usr/bin/env python
#
# bias.py - utility functions for analysis of active collimator
#           data saved in root trees by the AC recorder.
#
# author: richard.t.jones at uconn.edu
# version: august 18, 2020

import ROOT

vars = {"ixp": "N9:raw_XP",
        "ixm": "N9:raw_XM",
        "iyp": "N9:raw_YP",
        "iym": "N9:raw_YM",
        "oxp": "N10:raw_XP",
        "oxm": "N10:raw_XM",
        "oyp": "N10:raw_YP",
        "oym": "N10:raw_YM",
       }

rootfiles = ["ac_20200808_170304.root",
             "ac_20200808_174218.root",
             "ac_20200808_182407.root",
             "ac_20200808_191051.root",
             "ac_20200808_194804.root",
            ]

chains = {}
for var in vars:
   chains[var] = ROOT.TChain(vars[var])
   for rfile in rootfiles:
      chains[var].Add(rfile)

colors = {"ixp": ROOT.kBlue,
          "ixm": ROOT.kRed,
          "iyp": ROOT.kBlack,
          "iym": ROOT.kGreen,
          "oxp": ROOT.kBlue,
          "oxm": ROOT.kRed,
          "oyp": ROOT.kBlack,
          "oym": ROOT.kGreen,
         }

pedestals = {"ixp": -6,
             "ixm": 3,
             "iyp": 10,
             "iym": 12,
             "oxp": 6,
             "oxm": 8,
             "oyp": 4,
             "oym": 8,
            }

tstart_up_sec = 1596921720 # 17:22 on August 8, 2020, epoch seconds
tstart_down_sec = 1596923640 # 17:54 on August 8, 2020, epoch seconds
tstart_up2_sec = 1596925620 # 18:27 on August 8, 2020, epoch seconds
tstart_60nA_sec = 1596928500 # 19:15 on August 8, 2020, epoch seconds

RC = 470 # seconds

def draw_raw16(test=0):
   if test == 0:
      tstart = tstart_up_sec
      tend = tstart_down_sec
   elif test == 1:
      tstart = tstart_down_sec
      tend = tstart_up2_sec
   else:
      tstart = tstart_60nA_sec
      tend = 1e99
   cond = "(tsec > {0}) && (tsec < {1})".format(tstart - 100, tend)
   cond += " && (current > 20)"
   opt = ""
   for var in sorted(vars):
      ped = pedestals[var]
      chains[var].SetMarkerColor(colors[var])
      chains[var].Draw("(Sum$(data)/8192-({0}))*100/current:tsec-({1})".format(ped, tstart),
                       cond, opt)
      htemp = ROOT.gPad.GetPrimitive("htemp")
      htemp.SetTitle("active collimator raw currents vs time")
      htemp.GetXaxis().SetTitle("time after bias change (s)")
      htemp.GetYaxis().SetTitle("raw ADC - pedestal")
      opt = "same"

def bias_raw16(test=0):
   if test == 0:
      tstart = tstart_up_sec
      tend = tstart_down_sec
      Vbias = "50*(1-exp(-(tsec-{0})/{1}))".format(tstart, RC)
   elif test == 1:
      tstart = tstart_down_sec
      tend = tstart_up2_sec
      Vbias = "50*exp(-(tsec-{0})/{1})".format(tstart, RC)
   else:
      tstart = tstart_60nA_sec
      tend = 1e99
      Vbias = "50"
   cond = "(tsec > {0}) && (tsec < {1})".format(tstart, tend)
   cond += " && (current > 20)"
   opt = ""
   for var in sorted(vars):
      ped = pedestals[var]
      chains[var].SetMarkerColor(colors[var])
      chains[var].Draw("(Sum$(data)/8192-({0}))*100/current".format(ped) +
                       ":" + Vbias, cond, opt)
      htemp = ROOT.gPad.GetPrimitive("htemp")
      htemp.SetTitle("active collimator raw currents vs bias")
      htemp.GetXaxis().SetTitle("device forward bias (V)")
      htemp.GetYaxis().SetTitle("raw ADC - pedestal")
      opt = "same"
