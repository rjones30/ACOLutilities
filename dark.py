#!/usr/bin/env python

from ROOT import *

gains = range(6,13)
files = ["darkcurrent-8-15-2018/ac_20180815_1e{0}.root".format(g)
         for g in gains]
sectors = ["XP", "XM", "YP", "YM"]
inames = {}
onames = {}
histos = {}
fout = TFile("dark.root", "recreate")
for i in range(0,4):
   sector = sectors[i]
   inames[sector] = "N9:raw_{0}".format(sector)
   onames[sector] = "N10:raw_{0}".format(sector)
   histos["i" + sector] = TProfile("i" + sector, "inner sector " + sector,
                                   7, 5.5, 12.5, -33000, 33000, "s")
   histos["o" + sector] = TProfile("o" + sector, "outer sector " + sector,
                                   7, 5.5, 12.5, -33000, 33000, "s")
   histos["i" + sector].SetMarkerStyle(20 + i)
   histos["o" + sector].SetMarkerStyle(20 + i)
   histos["i" + sector].GetXaxis().SetTitle("log10(gain)")
   histos["o" + sector].GetXaxis().SetTitle("log10(gain)")
   histos["i" + sector].GetYaxis().SetTitle("adc zero")
   histos["o" + sector].GetYaxis().SetTitle("adc zero")
   histos["i" + sector].GetYaxis().SetTitleOffset(1.6)
   histos["o" + sector].GetYaxis().SetTitleOffset(1.6)
   histos["i" + sector].SetStats(0)
   histos["o" + sector].SetStats(0)
   histos["i" + sector].Write()
   histos["o" + sector].Write()

def fillme():
   for i in range(0,7):
      f = TFile(files[i])
      for sector in sectors:
         ti = f.Get(inames[sector])
         to = f.Get(onames[sector])
         fout.cd()
         ti.Draw("data:6+" + str(i) + ">>+i" + sector)
         to.Draw("data:6+" + str(i) + ">>+o" + sector)

def tabulate():
   print "        ",
   for g in range(6,10):
      print "     1e{0} ".format(g),
   for g in range(10,13):
      print "    1e{0} ".format(g),
   print
   print "        ", 
   for g in range(6,13):
      print "---------",
   print
   for sector in sectors:
      print "  i" + sector, "  ",
      pi = fout.Get("i" + sector)
      for b in range(1,8):
         print "  {0:7.1f}".format(pi.GetBinContent(b)),
      print
   for sector in sectors:
      print "  o" + sector, "  ",
      po = fout.Get("o" + sector)
      for b in range(1,8):
         print "  {0:7.1f}".format(po.GetBinContent(b)),
      print

def tabulate_html():
   print "<table>"
   print "<tr><td></td>",
   for g in range(6,13):
      print "<td align=\"right\">1e{0}</td>".format(g),
   print "</tr>"
   print "<tr><td></td>", 
   for g in range(6,13):
      print "<td>---------</td>",
   print "</tr>"
   for sector in sectors:
      print "<tr><td>i" + sector, "</td>",
      pi = fout.Get("i" + sector)
      for b in range(1,8):
         print "<td align=\"right\">{0:7.1f}</td>".format(pi.GetBinContent(b)),
      print "</tr>"
   for sector in sectors:
      print "<tr><td>o" + sector, "</td>",
      po = fout.Get("o" + sector)
      for b in range(1,8):
         print "<td align=\"right\">{0:7.1f}</td>".format(po.GetBinContent(b)),
      print "</tr>"
   print "</table>"

def printme():
   for sector in sectors:
      pi = fout.Get("i" + sector)
      pi.Draw()
      c1.Print("i" + sector + ".png")
      po = fout.Get("o" + sector)
      po.Draw()
      c1.Print("o" + sector + ".png")
