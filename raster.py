#!/bin/env python
#
# raster.py - simple script to generate a raster pattern with 
#             and arbitrary frequency ratio on x and y
#
# author: richard.t.jones at uconn.edu
# version: april 26, 2018

import math
import numpy
from ROOT import *

Hz = 1.0
mm = 1.0

freqX = 23*Hz
freqY = 27*Hz
freqDot = 60.11599876*Hz
ampX = 1.2*mm
ampY = 1.2*mm
ampR = 0.2*mm

c1 = TCanvas("c1", "c1", 100, 200, 500, 500)
r1 = TRandom3()

def genpattern():
   xar = []
   yar = []
   for n in range(0, 10000):
      t = n / freqDot
      x = ampX * math.sin(2 * math.pi * freqX * t)
      y = ampY * math.sin(2 * math.pi * freqY * t)
      xar.append(x + r1.Gaus(0, ampR))
      yar.append(y + r1.Gaus(0, ampR))
   g = TGraph(len(xar), numpy.array(xar, dtype=float),
                        numpy.array(yar, dtype=float))
   g.SetTitle("raster pattern")
   g.Draw('ap')
   g.GetHistogram().GetXaxis().SetTitle("x (mm)")
   g.GetHistogram().GetYaxis().SetTitle("y (mm)")
   c1.Update()
   return g
