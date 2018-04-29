#define transit_cxx
// The class definition in transit.h has been generated automatically
// by the ROOT utility TTree::MakeSelector(). This class is derived
// from the ROOT class TSelector. For more information on the TSelector
// framework see $ROOTSYS/README/README.SELECTOR or the ROOT User Manual.


// The following methods are defined in this file:
//    Begin():        called every time a loop on the tree starts,
//                    a convenient place to create your histograms.
//    SlaveBegin():   called after Begin(), when on PROOF called only on the
//                    slave servers.
//    Process():      called for each event, in this function you decide what
//                    to read and fill your histograms.
//    SlaveTerminate: called at the end of the loop on the tree, when on PROOF
//                    called only on the slave servers.
//    Terminate():    called at the end of the loop on the tree,
//                    a convenient place to draw/fit your histograms.
//
// To use this file, try the following session on your Tree T:
//
// root> T->Process("transit.C")
// root> T->Process("transit.C","some options")
// root> T->Process("transit.C+")
//


#include "transit.h"
#include <TH2.h>
#include <TStyle.h>
#include <TGraph.h>
#include <TCanvas.h>
#include <list>
#include <string>

// This class is used to generate views of the active collimator wedge
// currents during instances where the beam trips off or comes back on.
// When this happens during a smapling interval, one gets a chance to
// check the time alignment between the streams from different wedges.

// Define a "transit" as a point in time where the ixp wedge current
// crosses through ixp_threshold in either direction.
double ixp_threshold = 200;
double lookback_time = 0.3;

// To capture a transit, keep this many samples in a rotating memory buffer
unsigned int ixp_record_len = 500;
std::list<float> ixp_record;
std::list<double> trs_record;

// Record of times (s) at which transits were detected.
std::list<double> transit_times;


void transit::Begin(TTree * /*tree*/)
{
   // The Begin() function is called at the start of the query.
   // When running with PROOF Begin() is only called on the client.
   // The tree argument is deprecated (on PROOF 0 is passed).

   TString option = GetOption();
}

void transit::SlaveBegin(TTree * /*tree*/)
{
   // The SlaveBegin() function is called after the Begin() function.
   // When running with PROOF SlaveBegin() is called on each slave server.
   // The tree argument is deprecated (on PROOF 0 is passed).

   TString option = GetOption();

}

Bool_t transit::Process(Long64_t entry)
{
   // The Process() function is called for each entry in the tree (or possibly
   // keyed object in the case of PROOF) to be processed. The entry argument
   // specifies which entry in the currently loaded tree is to be processed.
   // When processing keyed objects with PROOF, the object is already loaded
   // and is available via the fObject pointer.
   //
   // This function should contain the \"body\" of the analysis. It can contain
   // simple or elaborate selection criteria, run algorithms on the data
   // of the event and typically fill histograms.
   //
   // The processing can be stopped by calling Abort().
   //
   // Use fStatus to set the return value of TTree::Process().
   //
   // The return value is currently not used.

   fReader.SetEntry(entry);
   trs_record.push_back(*trs);
   ixp_record.push_back(*ixp);
   if (ixp_record.size() > ixp_record_len) {
      float ixp_front = ixp_record.front();
      double trs_front = trs_record.front();
      ixp_record.pop_front();
      trs_record.pop_front();
      if (*trs - trs_front < lookback_time) {
         if (ixp_front - *ixp > ixp_threshold) {
            transit_times.push_back(*trs);
            printf("falling edge at t=%lf\n", *trs);
            ixp_record.clear();
            trs_record.clear();
            show_transit(entry);
         }
         else if (ixp_front - *ixp < -ixp_threshold) {
            transit_times.push_back(*trs);
            printf("rising edge at t=%lf\n", *trs);
            ixp_record.clear();
            trs_record.clear();
            show_transit(entry + 200);
         }
      }
   }
   return kTRUE;
}

void transit::SlaveTerminate()
{
   // The SlaveTerminate() function is called after all entries or objects
   // have been processed. When running with PROOF SlaveTerminate() is called
   // on each slave server.

}

void transit::Terminate()
{
   // The Terminate() function is the last function to be called during
   // a query. It always runs on the client, it can be used to present
   // the results graphically or save the results to file.

}

void transit::show_transit(Long64_t entry)
{
   double t[ixp_record_len];
   double w[8][ixp_record_len];
   for (Long64_t i=0; i < ixp_record_len; ++i) {
      fReader.SetEntry(entry - ixp_record_len + i);
      t[i] = *trs;
      w[0][i] = *ixp;
      w[1][i] = *ixm;
      w[2][i] = *iyp;
      w[3][i] = *iym;
      w[4][i] = *oxp;
      w[5][i] = *oxm;
      w[6][i] = *oyp;
      w[7][i] = *oym;
   }
   TGraph *gr[8];
   for (int i=0; i < 8; ++i)
      gr[i] = new TGraph(ixp_record_len, t, w[i]);
   gr[0]->Draw("ap");
   gr[0]->GetHistogram()->SetMaximum(500);
   gr[0]->GetHistogram()->SetMinimum(-200);
   gr[0]->GetHistogram()->Draw();
   for (int i=1; i < 8; ++i)
      gr[i]->Draw("p");
   TCanvas *c1 = (TCanvas*)gROOT->FindObject("c1");
   c1->Update();
   printf("Enter c to continue: ");
   std::string resp;
   std::cin >> resp;
}
