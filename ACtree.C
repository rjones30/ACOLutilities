#define ACtree_cxx
// The class definition in ACtree.h has been generated automatically
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
// root> T->Process("ACtree.C")
// root> T->Process("ACtree.C","some options")
// root> T->Process("ACtree.C+")
//

#include "ACtree.h"
#include <TH2.h>
#include <TStyle.h>
#include <sstream>
#include <vector>
#include <math.h>

const double twopi = 2 * M_PI;

// Set sync_delta_s to less than the time between sampling intervals,
// used to align the rows from the individual trees for each wedge.
double sync_delta_s = 0.8;

// Set fadc_delta_s to the sampling period of the fadc,
// sampling_average_count / fadc_clock_frequency_Hz
double fadc_delta_s = 32. / 500000.;

// Set fmaxHz to the highest frequency you want to see in the 
// Fourier spectra that are recorded during output tree generation.
double fmaxHz = 500;

// Set dfHz to the reciprocal of the fadc sampling interval,
// needed to avoid aliasing effects from sampling gaps.
double dfHz = 1 / (8192 * fadc_delta_s);

// Set ncoherent to the number of sequential sampling intervals
// to use n computing the during Fourier spectra. Spectra are
// accummulated over ncoherent seconds, and the results summed
// over the complete run period.
int ncoherent = 10;

// Ignore any sampling intervals where the record beam current in
// the input trees is less than this threshold (nA).
double current_threshold = 10;


void ACtree::Begin(TTree * /*tree*/)
{
   // The Begin() function is called at the start of the query.
   // When running with PROOF Begin() is only called on the client.
   // The tree argument is deprecated (on PROOF 0 is passed).

   TString option = GetOption();
}

void ACtree::SlaveBegin(TTree * /*tree*/)
{
   // The SlaveBegin() function is called after the Begin() function.
   // When running with PROOF SlaveBegin() is called on each slave server.
   // The tree argument is deprecated (on PROOF 0 is passed).

   TString option = GetOption();
   acfile = new TFile("ac_serial.root", "recreate");
   actree = new TTree("act", "active collimator stream sequence");
   actree->Branch("stream", &ac_serial, AC_FORM);

   int nft = ceil(fmaxHz / dfHz);
   double fmax = nft * dfHz;
   FThist[0] = new TH1D("ixpft", "ix+ fourier transform", nft, 0, fmax);
   FThist[1] = new TH1D("ixmft", "ix- fourier transform", nft, 0, fmax);
   FThist[2] = new TH1D("iypft", "iy+ fourier transform", nft, 0, fmax);
   FThist[3] = new TH1D("iymft", "iy- fourier transform", nft, 0, fmax);
   FThist[4] = new TH1D("oxpft", "ox+ fourier transform", nft, 0, fmax);
   FThist[5] = new TH1D("oxmft", "ox- fourier transform", nft, 0, fmax);
   FThist[6] = new TH1D("oypft", "oy+ fourier transform", nft, 0, fmax);
   FThist[7] = new TH1D("oymft", "oy- fourier transform", nft, 0, fmax);

   for (int i=0; i < 8; ++i) {
      FThist[i]->GetYaxis()->SetTitle("fourier amplitude (arb. units)");
      FThist[i]->GetYaxis()->SetTitleOffset(1.5);
      FThist[i]->GetXaxis()->SetTitle("f (Hz)");
      FThist[i]->GetXaxis()->SetRange(2, nft);
      FThist[i]->SetStats(0);
      TString name(FThist[i]->GetName());
      FTwork[i][0] = (TH1D*)FThist[i]->Clone(name + "_cm");
      FTwork[i][1] = (TH1D*)FThist[i]->Clone(name + "_sm");
   }
}

Bool_t ACtree::Process(Long64_t entry)
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

   fTree[0]->GetEntry(entry);
   if (rec[0].current < current_threshold)
      return false;
   if (tbases < 0)
      tbases = rec[0].tsec;
   double t0 = rec[0].tsec - tbases + rec[0].tnsec * 1.0e-9;
   std::stringstream rep;
   rep << "entry " << entry << ": ";
   for (int i=1; i < 8; ++i) {
      Long64_t entries = fTree[i]->GetEntries();
      fTree[i]->GetEntry(entry);
      double t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
      int search = 0;
      double best_deltas = fabs(t1 - t0);
      while (t1 - t0 > sync_delta_s) {
         if (++search > 99 or entry == 0) {
            std::cerr << "Error in ACtree::Process - "
                      << "tree sync failed for wedge " << i
                      << ", " << rep.str() << std::endl;
            return false;
         }
         fTree[i]->GetEntry(--entry);
         t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
         if (fabs(t1 - t0) < best_deltas)
            best_deltas = fabs(t1 - t0);
      }
      while (t1 - t0 < -sync_delta_s) {
         if (++search > 99 or entry == entries - 1) {
            std::cerr << "Error in ACtree::Process - "
                      << "tree sync failed for wedge " << i
                      << ", " << rep.str() << std::endl;
            return false;
         }
         fTree[i]->GetEntry(++entry);
         t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
         if (fabs(t1 - t0) < best_deltas)
            best_deltas = fabs(t1 - t0);
      }
      if (fabs(t1 - t0) > best_deltas) {
         fTree[i]->GetEntry(--entry);
         t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
      }
      if (best_deltas > sync_delta_s) {
         std::cerr << "Error in ACtree::Process - "
                   << "tree sync failed for wedge " << i 
                   << ": best delta t = " << t1 - t0 << " seconds, "
                   << rep.str() << std::endl;
         return false;
      }
      rep << t1 - t0 << " ";
   }
   std::cout << rep.str() << std::endl;
   ac_serial.trs = t0;
   ac_serial.cur = rec[0].current;
   ac_serial.gva = pow(10, 6 + rec[0].gain);
   for (int i=0; i < 8192; ++i) {
      ac_serial.ixp = rec[0].data[i];
      ac_serial.ixm = rec[1].data[i];
      ac_serial.iyp = rec[2].data[i];
      ac_serial.iym = rec[3].data[i];
      ac_serial.oxp = rec[4].data[i];
      ac_serial.oxm = rec[5].data[i];
      ac_serial.oyp = rec[6].data[i];
      ac_serial.oym = rec[7].data[i];
      actree->Fill();
      ac_serial.trs += fadc_delta_s;
   }
   int nbins = FThist[0]->GetNbinsX();
   for (int i=1; i <= nbins; ++i) {
      double si[8] = {0};
      double ci[8] = {0};
      double fHz = FThist[0]->GetXaxis()->GetBinLowEdge(i);
      double sm = sin(twopi * fHz * ac_serial.trs) / 8192;
      double cm = cos(twopi * fHz * ac_serial.trs) / 8192;
      double sfdt = sin(twopi * fHz * fadc_delta_s);
      double cfdt = cos(twopi * fHz * fadc_delta_s);
      for (int it=0; it < 8192; ++it) {
         for (int j=0; j < 8; ++j) {
            si[j] += sm * rec[j].data[it];
            ci[j] += cm * rec[j].data[it];
         }
         double ss = sm;
         double cc = cm;
         sm = ss * cfdt + cc * sfdt;
         cm = cc * cfdt - ss * sfdt;
      }
      for (int j=0; j < 8; ++j) {
         double c = FTwork[j][0]->GetBinContent(i);
         double s = FTwork[j][1]->GetBinContent(i);
         FTwork[j][0]->SetBinContent(i, c + ci[j]);
         FTwork[j][1]->SetBinContent(i, s + si[j]);
      }
      if (entry % ncoherent == 0) {
         for (int j=0; j < 8; ++j) {
            double a = FThist[j]->GetBinContent(i);
            double c = FTwork[j][0]->GetBinContent(i);
            double s = FTwork[j][1]->GetBinContent(i);
            FThist[j]->SetBinContent(i, a + sqrt(c*c + s*s));
            FTwork[j][0]->SetBinContent(i, 0);
            FTwork[j][1]->SetBinContent(i, 0);
         }
      }
   }
   return kTRUE;
}

void ACtree::SlaveTerminate()
{
   // The SlaveTerminate() function is called after all entries or objects
   // have been processed. When running with PROOF SlaveTerminate() is called
   // on each slave server.

   actree->Write();
   for (int j=0; j < 8; ++j)
      FThist[j]->Write();
   acfile->Close();
}

void ACtree::Terminate()
{
   // The Terminate() function is the last function to be called during
   // a query. It always runs on the client, it can be used to present
   // the results graphically or save the results to file.

}
