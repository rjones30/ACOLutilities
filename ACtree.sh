#!/bin/bash
#
# ACtree.sh - shell script to run ACtree TSelector over one
#             raw active collimator tree file.
#
# author: richard.t.jones at uconn.edu
# version: april 28, 2018

if [[ $# != 1 || ! -r $1 ]]; then
    echo "Usage: ./ACtree.sh <ac_YYYYMMDD_hhmmss.root>"
    exit 1
fi

root -l $1 <<EOI
TTree *t = (TTree*)gROOT->FindObject("N9:raw_XP");
t->Process("ACtree.C+O")
.q
EOI

mv ac_serial.root `basename $1 | sed 's/.root$/_serial.root/'`
