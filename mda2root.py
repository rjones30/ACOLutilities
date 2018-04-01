#!/bin/env python
#
# mda2root.py - script to read an EPICS scan data file in mda format
#               and write out the scan data as a root tree.
#
# author: richard.t.jones at uconn.edu
# version: march 31, 2018 [rtj]
#
# usage:
#          $ mda2root.py <inputfile.mda>
#
# notes:
# 1) Before invoking mda2root.py, make sure that you have the mda2ascii
#    utility in your path. This is part of the mdautils package written
#    by Dohn Arms (Argonne).

from ROOT import *
import numpy
import subprocess
import sys
import os
import re

varname = []

def usage():
   print "Usage: mda2root.py <inputfile.mda>"
   print " You must have mda2ascii in your PATH before invoking this command."
   sys.exit(1)

def declare_theTree():
   global tree
   global varray
   if not tree:
      tree = TTree("theTree", "EPICS scan data")
      varray = numpy.array([0] * len(varname), dtype=float)
      form = "/D:".join(varname) + "/D"
      tree.Branch("scan_data", varray, form)
   return tree
   
def fill_theTree(asc):
   global varray
   if len(varname) == 0:
      varname.append("entry")
   for line in asc:
      if re.match(r"^[1-9]", line):
         tree = declare_theTree()
         f = line.split()
         for i in range(1, len(f)):
            varray[i] = float(f[i])
         varray[0] += 1
         tree.Fill()
      elif line[0] == '#':
         try:
            vnum = int(re.search(r"^#  *([1-9][0-9]*)  *\[1-D (Detector|Positioner)  *([0-9]*)", line).group(1))
            vname = re.search(r"] *([^,]*),", line).group(1)
            vname = re.sub(r":", "_", vname)
            vname = re.sub(r"\.", "_", vname)
         except:
            continue
         if vnum == 1:
            continue
         elif vnum == len(varname) + 1:
            varname.append(vname)
         elif varname[vnum - 1] == vname:
            continue
         else:
            print "Error - variable", vnum, "(", vname, ") delared out of order,"
            print "vnum, len(varname) = ", vnum, len(varname)
            print "cannot continue."
            sys.exit(1)

# Column Descriptions:
#    1  [     Index      ]
#    2  [1-D Positioner 1]  hd:collimator:x:motor.VAL, CollimatorX, LINEAR, mm, hd:collimator:x:motor.RBV, CollimatorX, mm
#    3  [1-D Detector   1]  hd:collimator:x:motor.RBV, CollimatorX, mm
#    4  [1-D Detector   2]  hd:collimator:y:motor.RBV, CollimatorY, mm
#    5  [1-D Detector   3]  IBCAD00CRCUR6, analog input record, nA
#    6  [1-D Detector   4]  bpu_mean_x, , mm
#    7  [1-D Detector   5]  bpu_mean_y, , mm
#    8  [1-D Detector   6]  PSC:T:3:scaler_r1, , 
#    9  [1-D Detector   7]  PSC:T:4:scaler_r1, , 
#   10  [1-D Detector   8]  PSC:T:5:scaler_r1, , 
#   11  [1-D Detector   9]  PSC:T:6:scaler_r1, , 
#   12  [1-D Detector  10]  PSC:T:7:scaler_r1, , 
#   13  [1-D Detector  11]  PSC:T:8:scaler_r1, , 
#   14  [1-D Detector  12]  PSC:T:9:scaler_r1, , 
#   15  [1-D Detector  13]  PSC:T:10:scaler_r1, , 
#   16  [1-D Detector  14]  PSC:T:11:scaler_r1, , 
#   17  [1-D Detector  15]  PSC:T:12:scaler_r1, , 
#   18  [1-D Detector  16]  PSC:T:13:scaler_r1, , 
#   19  [1-D Detector  17]  PSC:T:14:scaler_r1, , 
#   20  [1-D Detector  18]  PSC:T:15:scaler_r1, , 
#   21  [1-D Detector  19]  PSC:T:16:scaler_r1, , 
#   22  [1-D Detector  20]  HALO:T:gamma:col:left:scaler_r1, , 
#   23  [1-D Detector  21]  HALO:T:gamma:col:top:scaler_r1, , 
#   24  [1-D Detector  22]  HALO:T:gamma:col:right:scaler_r1, , 
#   25  [1-D Detector  23]  HALO:T:gamma:col:bottom:scaler_r1, , 
#   26  [1-D Detector  24]  HALO:T:gamma:tgt:left:scaler_r1, , 
#   27  [1-D Detector  25]  HALO:T:gamma:tgt:top:scaler_r1, , 
#   28  [1-D Detector  26]  HALO:T:gamma:tgt:right:scaler_r1, , 
#   29  [1-D Detector  27]  HALO:T:gamma:tgt:bottom:scaler_r1, , 
#   30  [1-D Detector  28]  IOCHDCOL:VMICADC1_1, analog input record, counts
#   31  [1-D Detector  29]  IOCHDCOL:VMICADC2_1, analog input record, counts
#   32  [1-D Detector  30]  IOCHDCOL:VMICADC3_1, analog input record, counts
#   33  [1-D Detector  31]  IOCHDCOL:VMICADC4_1, analog input record, counts
#   34  [1-D Detector  32]  IOCHDCOL:VMICADC1_2, analog input record, counts
#   35  [1-D Detector  33]  IOCHDCOL:VMICADC2_2, analog input record, counts
#   36  [1-D Detector  34]  IOCHDCOL:VMICADC3_2, analog input record, counts
#   37  [1-D Detector  35]  IOCHDCOL:VMICADC4_2, analog input record, counts
#   38  [1-D Detector  36]  ST:T:1:scaler_r1, , 
#   39  [1-D Detector  37]  ST:T:2:scaler_r1, , 
#   40  [1-D Detector  38]  ST:T:3:scaler_r1, , 
#   41  [1-D Detector  39]  ST:T:4:scaler_r1, , 
#   42  [1-D Detector  40]  ST:T:5:scaler_r1, , 
#   43  [1-D Detector  41]  ST:T:6:scaler_r1, , 
#   44  [1-D Detector  42]  ST:T:7:scaler_r1, , 
#   45  [1-D Detector  43]  ST:T:8:scaler_r1, , 
#   46  [1-D Detector  44]  ST:T:9:scaler_r1, , 
#   47  [1-D Detector  45]  ST:T:10:scaler_r1, , 
#   48  [1-D Detector  46]  ST:T:11:scaler_r1, , 
#   49  [1-D Detector  47]  ST:T:12:scaler_r1, , 
#   50  [1-D Detector  48]  ST:T:13:scaler_r1, , 
#   51  [1-D Detector  49]  ST:T:14:scaler_r1, , 
#   52  [1-D Detector  50]  ST:T:15:scaler_r1, , 
#   53  [1-D Detector  51]  ST:T:16:scaler_r1, , 
#   54  [1-D Detector  52]  ST:T:17:scaler_r1, , 
#   55  [1-D Detector  53]  ST:T:18:scaler_r1, , 
#   56  [1-D Detector  54]  ST:T:19:scaler_r1, , 
#   57  [1-D Detector  55]  ST:T:20:scaler_r1, , 
#   58  [1-D Detector  56]  ST:T:21:scaler_r1, , 
#   59  [1-D Detector  57]  ST:T:22:scaler_r1, , 
#   60  [1-D Detector  58]  ST:T:23:scaler_r1, , 
#   61  [1-D Detector  59]  ST:T:24:scaler_r1, , 
#   62  [1-D Detector  60]  ST:T:25:scaler_r1, , 
#   63  [1-D Detector  61]  ST:T:26:scaler_r1, , 
#   64  [1-D Detector  62]  ST:T:27:scaler_r1, , 
#   65  [1-D Detector  63]  ST:T:28:scaler_r1, , 
#   66  [1-D Detector  64]  ST:T:29:scaler_r1, , 
#   67  [1-D Detector  65]  ST:T:30:scaler_r1, , 
#   68  [1-D Detector  66]  Active_Target:T:scaler_r1, , 
#   69  [1-D Detector  67]  PSC:coinc:scaler:rate, , 
#   70  [1-D Detector  68]  TAC:T:scaler_r1, , 
#   71  [1-D Detector  69]  AC:inner:position:x, AC inner x-position, mm
#   72  [1-D Detector  70]  AC:inner:position:y, AC inner y-position, mm

# 1-D Scan Values
"""
1 -116.506331 -116.506332 3 67.5 -3.10873151 -2.6929388 7002.06592 6738.59033 6542.97949 6569.92578 6250.56152 6166.72803 7973.1333 7539.99561 7459.15625 7127.81543 6892.28418 6670.7251 6224.61279 6136.7876 554
93.2852 20840.9238 33248.0625 34279.082 1259.57788 1557.00586 861.343628 1081.91943 2995 4445 3517 5906 2502 -14 954 714 84465.9141 123091.047 149831.828 136302.75 108920.25 135075.203 118758.672 153987.562 122
705.812 144492.453 145589.281 141415.578 119536.125 131420.469 147872.734 113569.992 126841.461 152719.938 123135.836 198855.078 122948.211 102408.102 133661.875 125155.812 125833.469 104634.672 96540.7891 9481
9.2188 100728.453 113178.664 230.757935 14427.2627 0 1.15346956 -1.87083423

******************************************************************************
*Tree    :theTree   : The Tree                                               *
*Entries :       90 : Total =          118355 bytes  File  Size =      87834 *
*        :          : Tree compression factor =   1.00                       *
******************************************************************************
*Br    0 :Entry     : Float_t F                                              *
*Entries :       90 : Total  Size=       1495 bytes  File Size  =       1035 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br    1 :hd_collimator_x_motor.VAL : Float_t F                              *
*Entries :       90 : Total  Size=       1695 bytes  File Size  =       1215 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br    2 :hd_collimator_x_motor.RBV : Float_t F                              *
*Entries :       90 : Total  Size=       1695 bytes  File Size  =       1215 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br    3 :hd_collimator_y_motor.RBV : Float_t F                              *
*Entries :       90 : Total  Size=       1695 bytes  File Size  =       1077 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.13     *
*............................................................................*
*Br    4 :IBCAD00CRCUR6 : Float_t F                                          *
*Entries :       90 : Total  Size=       1575 bytes  File Size  =       1060 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.04     *
*............................................................................*
*Br    5 :bpu_mean_x : Float_t F                                             *
*Entries :       90 : Total  Size=       1545 bytes  File Size  =       1080 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br    6 :bpu_mean_y : Float_t F                                             *
*Entries :       90 : Total  Size=       1545 bytes  File Size  =       1080 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br    7 :PSC_T_3_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br    8 :PSC_T_4_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br    9 :PSC_T_5_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   10 :PSC_T_6_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   11 :PSC_T_7_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   12 :PSC_T_8_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   13 :PSC_T_9_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   14 :PSC_T_10_scaler_r1 : Float_t F                                     *
*Entries :       90 : Total  Size=       1625 bytes  File Size  =       1152 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   15 :PSC_T_11_scaler_r1 : Float_t F                                     *
*Entries :       90 : Total  Size=       1625 bytes  File Size  =       1152 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   16 :PSC_T_12_scaler_r1 : Float_t F                                     *
*Entries :       90 : Total  Size=       1625 bytes  File Size  =       1152 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   17 :PSC_T_13_scaler_r1 : Float_t F                                     *
*Entries :       90 : Total  Size=       1625 bytes  File Size  =       1152 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   18 :PSC_T_14_scaler_r1 : Float_t F                                     *
*Entries :       90 : Total  Size=       1625 bytes  File Size  =       1152 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   19 :PSC_T_15_scaler_r1 : Float_t F                                     *
*Entries :       90 : Total  Size=       1625 bytes  File Size  =       1152 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   20 :PSC_T_16_scaler_r1 : Float_t F                                     *
*Entries :       90 : Total  Size=       1625 bytes  File Size  =       1152 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   21 :HALO_T_gamma_col_left_scaler_r1 : Float_t F                        *
*Entries :       90 : Total  Size=       1755 bytes  File Size  =       1269 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   22 :HALO_T_gamma_col_top_scaler_r1 : Float_t F                         *
*Entries :       90 : Total  Size=       1745 bytes  File Size  =       1260 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   23 :HALO_T_gamma_col_right_scaler_r1 : Float_t F                       *
*Entries :       90 : Total  Size=       1765 bytes  File Size  =       1278 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   24 :HALO_T_gamma_col_bottom_scaler_r1 : Float_t F                      *
*Entries :       90 : Total  Size=       1775 bytes  File Size  =       1287 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   25 :HALO_T_gamma_tgt_left_scaler_r1 : Float_t F                        *
*Entries :       90 : Total  Size=       1755 bytes  File Size  =       1269 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   26 :HALO_T_gamma_tgt_top_scaler_r1 : Float_t F                         *
*Entries :       90 : Total  Size=       1745 bytes  File Size  =       1260 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   27 :HALO_T_gamma_tgt_right_scaler_r1 : Float_t F                       *
*Entries :       90 : Total  Size=       1765 bytes  File Size  =       1278 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   28 :HALO_T_gamma_tgt_bottom_scaler_r1 : Float_t F                      *
*Entries :       90 : Total  Size=       1775 bytes  File Size  =       1287 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   29 :IOCHDCOL_VMICADC1_1 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   30 :IOCHDCOL_VMICADC2_1 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   31 :IOCHDCOL_VMICADC3_1 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   32 :IOCHDCOL_VMICADC4_1 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   33 :IOCHDCOL_VMICADC1_2 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   34 :IOCHDCOL_VMICADC2_2 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1140 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.02     *
*............................................................................*
*Br   35 :IOCHDCOL_VMICADC3_2 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   36 :IOCHDCOL_VMICADC4_2 : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   37 :ST_T_1_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   38 :ST_T_2_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   39 :ST_T_3_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   40 :ST_T_4_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   41 :ST_T_5_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   42 :ST_T_6_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   43 :ST_T_7_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   44 :ST_T_8_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   45 :ST_T_9_scaler_r1 : Float_t F                                       *
*Entries :       90 : Total  Size=       1605 bytes  File Size  =       1134 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   46 :ST_T_10_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   47 :ST_T_11_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   48 :ST_T_12_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   49 :ST_T_13_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   50 :ST_T_14_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   51 :ST_T_15_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   52 :ST_T_16_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   53 :ST_T_17_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   54 :ST_T_18_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   55 :ST_T_19_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   56 :ST_T_20_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   57 :ST_T_21_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   58 :ST_T_22_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   59 :ST_T_23_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   60 :ST_T_24_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   61 :ST_T_25_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   62 :ST_T_26_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   63 :ST_T_27_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   64 :ST_T_28_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   65 :ST_T_29_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   66 :ST_T_30_scaler_r1 : Float_t F                                      *
*Entries :       90 : Total  Size=       1615 bytes  File Size  =       1143 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   67 :Active_Target_T_scaler_r1 : Float_t F                              *
*Entries :       90 : Total  Size=       1695 bytes  File Size  =       1215 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   68 :PSC_coinc_scaler_rate : Float_t F                                  *
*Entries :       90 : Total  Size=       1655 bytes  File Size  =       1179 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   69 :TAC_T_scaler_r1 : Float_t F                                        *
*Entries :       90 : Total  Size=       1595 bytes  File Size  =        981 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.15     *
*............................................................................*
*Br   70 :AC_inner_position_x : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
*Br   71 :AC_inner_position_y : Float_t F                                    *
*Entries :       90 : Total  Size=       1635 bytes  File Size  =       1161 *
*Baskets :        9 : Basket Size=      32000 bytes  Compression=   1.00     *
*............................................................................*
"""

if len(sys.argv) != 2:
   usage()

try:
   res = subprocess.call(["mda2ascii", sys.argv[1]])
   if res != 0:
      usage()
except:
   usage()

basename = re.search(r"([^/][^/]*).mda", sys.argv[1]).group(1)
if len(basename) == 0:
   usage()
fout = TFile(basename + ".root", "recreate")

tree = 0
entry = numpy.array([0], dtype=float)
for scan in range(0, 9999999):
   try:
      asc = open("{0}_{1}.asc".format(basename, scan + 1))
   except:
      nscans = scan
      break
   fill_theTree(asc)
tree.Write()

# clean up and exit
for scan in range(0, nscans):
   os.remove("{0}_{1}.asc".format(basename, scan + 1))
sys.exit(0)
