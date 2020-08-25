#!/usr/bin/env python
#
# calibi.py - calibration of the wedge current vs photon beam
#             intensity from a beam intensity scan over a wide
#             range in photon beam intensities.
#
# author: richard.t.jones at uconn.edu
# version: august 22, 2020

import ROOT
import numpy as np
import statistics as stats

plots = {}
plotranges = {2: {'log10xmin': 1.2,
                  'log10xmax': 3,
                  'log10ymin': -2,
                  'log10ymax': 2,
                  },
              3: {'log10xmin': 0,
                  'log10xmax': 2,
                  'log10ymin': -2,
                  'log10ymax': 2,
                  },
              4: {'log10xmin': -1,
                  'log10xmax': 1,
                  'log10ymin': -2,
                  'log10ymax': 2,
                  },
             }
log10xmin = -1
log10xmax = 3
log10ymin = -2
log10ymax = 2

pedestals = {}
refradlen = 4.5e-4

# This is for the scan taken on August 21, 2020
radiators = {4.5e-4: [1598049000, 1598052120],
             1.7e-5: [1598052120, 1598055300],
            }

gains = {2: 1e-8,
         3: 1e-9,
         4: 1e-10,
#         5: 1e-11,
#         6: 1e-12,
        }

chainvars = {"ixp": "N9:raw_XP",
             "ixm": "N9:raw_XM",
             "iyp": "N9:raw_YP",
             "iym": "N9:raw_YM",
             "oxp": "N10:raw_XP",
             "oxm": "N10:raw_XM",
             "oyp": "N10:raw_YP",
             "oym": "N10:raw_YM",
            }

rootfiles = ["ac_20200821_185034.root",
             "ac_20200821_192323.root",
             "ac_20200821_195048.root",
             "ac_20200802_075342.root",
            ]
chains = {}
for var in sorted(chainvars):
   chains[var] = ROOT.TChain(chainvars[var])
   for rootf in rootfiles:
      chains[var].Add("data/" + rootf)

def load_pedestals(gain, tmin=1598049000, tmax=1600000000):
   current_threshold = 0.3 # nA
   pedestals[gain] = {}
   for var in sorted(chains):
      trips = []
      current = 1
      for i in range(0, chains[var].GetEntries()):
         chains[var].GetEntry(i)
         if chains[var].gain != gain:
            continue
         if chains[var].tsec < tmin or chains[var].tsec > tmax:
            continue
         if chains[var].current <= current_threshold:
            imean = sum(chains[var].data) / 8192.
            if current > 0:
               trips.append([imean])
               current = 0
            else:
               trips[-1].append(imean)
         else:
            current = chains[var].current
      peds = []
      for trip in trips:
        peds += trip[2:-2]
      if len(peds) > 0:
         pedestals[gain][var] = stats.mean(peds)
         print "pedestal at gain", gain, "for", var, \
               "=", stats.mean(peds), "+/-", stats.stdev(peds)
      else:
         print "no pedestal data found at gain", gain, "for", var

def make_plots():
   for gain in gains:
      if not gain in pedestals:
         load_pedestals(gain)
   for var in sorted(chainvars):
      for gain in gains:
         name = "p" + var + "{0}".format(gain)
         title = var + " current vs photon beam intensity"
         log10xmin = plotranges[gain]['log10xmin']
         log10xmax = plotranges[gain]['log10xmax']
         log10ymin = plotranges[gain]['log10ymin']
         log10ymax = plotranges[gain]['log10ymax']
         plots[name] = ROOT.TProfile(name, title, 400, log10xmin, log10xmax,
                                                       log10ymin, log10ymax)
         plots[name].SetDirectory(0)
         plots[name].SetStats(0)
         plots[name].SetLineColor(gain)
         for rad in radiators:
            ped = pedestals[gain][var]
            xvar = "log(current * ({0}))/log(10)".format(rad / refradlen)
            yvar = "log(abs(Sum$(data)/8192-({0})))/log(10)".format(ped)
            yvar += "+log({0})/log(10)".format(10 / 2048.)
            yvar += "+log({0})/log(10)+9".format(gains[gain])
            cond = "(current>3)&&(gain=={0})".format(gain)
            cond += "&&(tsec>{0})".format(radiators[rad][0])
            cond += "&&(tsec<{0})".format(radiators[rad][1])
            hpro = plots[name].Clone("hpro")
            chains[var].Draw(yvar + ":" + xvar + ">>hpro", cond)
            plots[name].Add(hpro)
            plots[name].SetTitle(title)
            plots[name].Draw()
            ROOT.gROOT.FindObject("c1").Update()

def color_plot(*wedges):
   if len(plots) == 0:
      make_plots()
   hlinlin = ROOT.TH2D("hlinlin", "", 10, log10xmin, log10xmax,
                                      10, log10ymin, log10ymax)
   c1 = ROOT.gROOT.FindObject("c1")
   c1.cd()
   c1.SetLogx(0)
   c1.SetLogy(0)
   hlinlin.SetStats(0)
   title = ",".join(wedges)
   hlinlin.SetTitle(title + " current vs beam intensity")
   hlinlin.Draw("a")
   dapad = ROOT.gPad
   for wedge in wedges:
      for gain in sorted(gains):
         name = "p{0}{1}".format(wedge, gain)
         plots[name].Draw("same")
   axpad = ROOT.TPad("axpad", "", 0, 0, 1, 1)
   axpad.SetFillStyle(4000)
   axpad.SetFillColor(0)
   axpad.SetFrameFillStyle(4000)
   axpad.Draw()
   axpad.cd()
   axpad.SetLogx()
   axpad.SetLogy()
   hloglog = ROOT.TH2D("hloglog", "", 10, 10**log10xmin, 10**log10xmax,
                                      10, 10**log10ymin, 10**log10ymax)
   hloglog.GetXaxis().SetTitle("photon beam intensity (nA equiv)")
   hloglog.GetYaxis().SetTitle("wedge current (nA)")
   hloglog.GetXaxis().SetTitleOffset(1.2)
   hloglog.SetStats(0)
   hloglog.Draw();
   plots["hloglog"] = hloglog
   plots["hlinlin"] = hlinlin

def fit_plot(*wedges):
   if len(plots) == 0:
      make_plots()
   hlogfit = ROOT.TH1D("hlinfit", "", 1000, log10xmin, log10xmax)
   for wedge in wedges:
      for gain in gains:
         name = "p{0}{1}".format(wedge, gain)
         for i in range(0, plots[name].GetNbinsX()):
            yerr = plots[name].GetBinError(i+1)
            if yerr == 0:
               continue
            yval = plots[name].GetBinContent(i+1)
            x = plots[name].GetXaxis().GetBinCenter(i+1)
            ibin = hlogfit.FindBin(x)
            hval = hlogfit.GetBinContent(ibin)
            herr = hlogfit.GetBinError(ibin)
            if herr > 0:
               ysum = hval / herr**2 + yval / yerr**2
               yvar = 1 / (1 / herr**2 + 1 / yerr**2)
               hlogfit.SetBinContent(ibin, ysum * yvar)
               yerr = (yvar + 0.02**2)**0.5
               hlogfit.SetBinError(ibin, yerr)
            else:
               hlogfit.SetBinContent(ibin, yval)
               yerr = (yerr**2 + 0.02**2)**0.5
               hlogfit.SetBinError(ibin, yerr)
   c1 = ROOT.gROOT.FindObject("c1")
   c1.cd()
   c1.SetLogx(0)
   c1.SetLogy(0)
   ROOT.gStyle.SetOptStat(0)
   ROOT.gStyle.SetOptFit(1)
   title = ",".join(wedges)
   hlogfit.SetTitle(title + " current vs beam intensity")
   hlogfit.GetXaxis().SetTitle("log_{10}(photon beam intensity / nA)")
   hlogfit.GetYaxis().SetTitle("log_{10}(wedge current / nA)")
   hlogfit.GetXaxis().SetTitleOffset(1.2)
   ROOT.gStyle.SetStatX(0.5)
   ROOT.gStyle.SetStatY(0.85)
   plots["hlogfit"] = hlogfit
   hlogfit.Fit("pol1")
   return hlogfit

def do_fits():
   for wedge in ('ixp','ixm','iyp','iym',
                 'oxp','oxm','oyp','oym'):
      fit_plot(wedge)
      c1 = ROOT.gROOT.FindObject("c1")
      c1.Update()
      c1.Print("ac_fit_{0}.png".format(wedge))
