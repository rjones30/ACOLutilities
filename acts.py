#!/usr/bin/env python
#
# acts.py - utility functions for analysis of the ACtree data
#           from the active collimator.
#
# author: richard.t.jones at uconn.edu
# version: february 18, 2020

import numpy as np
import ROOT as R

def fitsin4(var, par):
   return par[0] + par[1] * np.sin((var[0] * 2*np.pi * par[2]) + par[3]) 

def fsin(fHz):
   f4 = R.TF1("fsin", fitsin4, 0, 1e8, 4)
   f4.SetParameter(0, 1)
   f4.SetParameter(1, 1)
   f4.SetParameter(2, fHz)
   f4.SetParameter(3, 1)
   return f4
