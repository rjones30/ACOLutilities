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
double sync_delta_s = 2.5;

// Set fadc_delta_s to the sampling period of the fadc,
// sampling_average_count / fadc_clock_frequency_Hz
//double fadc_delta_s = 512. / 500000.;
double fadc_delta_s = 32. / 500000.;

// Set fmaxHz to the highest frequency you want to see in the 
// Fourier spectra that are recorded during output tree generation.
//double fmaxHz = 500;
double fmaxHz = 8192;

// Set dfHz to the reciprocal of the fadc sampling interval,
// needed to avoid aliasing effects from sampling gaps.
double dfHz = 1 / (8192 * fadc_delta_s);

// Set ncoherent to the number of sequential sampling intervals
// to use n computing the during Fourier spectra. Spectra are
// accummulated over ncoherent seconds, and the results summed
// over the complete run period.
int ncoherent = 1;

// Ignore any sampling intervals where the record beam current in
// the input trees is less than this threshold (nA).
//double current_threshold = 10;
double current_threshold = 300;

// Accummulate Fourier transforms only within this time interval
double trs_ft_start = 0;
double trs_ft_end = 99999;

// Stored updating baseline currents for each wedge
double baselines[8] = {0,0,0,0,0,0,0,0};
double baseline_memory = 3;  // samples
double baseline_current = 3;  // nA

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
   FIhist[0] = new TH1I("ixpno", "ix+ samples", nft, 0, fmax);
   FThist[1] = new TH1D("ixmft", "ix- fourier transform", nft, 0, fmax);
   FIhist[1] = new TH1I("ixmno", "ix- samples", nft, 0, fmax);
   FThist[2] = new TH1D("iypft", "iy+ fourier transform", nft, 0, fmax);
   FIhist[2] = new TH1I("iypno", "iy+ samples", nft, 0, fmax);
   FThist[3] = new TH1D("iymft", "iy- fourier transform", nft, 0, fmax);
   FIhist[3] = new TH1I("iymno", "iy- samples", nft, 0, fmax);
   FThist[4] = new TH1D("oxpft", "ox+ fourier transform", nft, 0, fmax);
   FIhist[4] = new TH1I("oxpno", "ox+ samples", nft, 0, fmax);
   FThist[5] = new TH1D("oxmft", "ox- fourier transform", nft, 0, fmax);
   FIhist[5] = new TH1I("oxmno", "ox- samples", nft, 0, fmax);
   FThist[6] = new TH1D("oypft", "oy+ fourier transform", nft, 0, fmax);
   FIhist[6] = new TH1I("oypno", "oy+ samples", nft, 0, fmax);
   FThist[7] = new TH1D("oymft", "oy- fourier transform", nft, 0, fmax);
   FIhist[7] = new TH1I("oymno", "oy- samples", nft, 0, fmax);

   for (int i=0; i < 8; ++i) {
      FThist[i]->GetYaxis()->SetTitle("fourier amplitude (arb. units)");
      FThist[i]->GetYaxis()->SetTitleOffset(1.5);
      FThist[i]->GetXaxis()->SetTitle("f (Hz)");
      FThist[i]->GetXaxis()->SetRange(2, nft);
      FThist[i]->SetStats(0);
      FIhist[i]->GetYaxis()->SetTitle("sample count");
      FIhist[i]->GetYaxis()->SetTitleOffset(1.5);
      FIhist[i]->GetXaxis()->SetTitle("f (Hz)");
      FIhist[i]->SetStats(0);
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
   if (tbases < 0)
      tbases = rec[0].tsec;
   double t0 = rec[0].tsec - tbases + rec[0].tnsec * 1.0e-9;
   int joffset[8] = {0,0,0,0,0,0,0,0};
   std::stringstream rep;
   rep << "entry " << entry << ": ";
   for (int i=1; i < 8; ++i) {
      Long64_t entries = fTree[i]->GetEntries();
      fTree[i]->GetEntry(entry);
      double t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
      int search = 0;
      double best_deltas = fabs(t1 - t0);
      std::vector<double> tsearch;
      while (t1 - t0 > sync_delta_s) {
         if (++search > 999 or entry == 0) {
            std::cerr << "Error in ACtree::Process - "
                      << "tree reverse search failed for wedge " << i
                      << ", " << rep.str() << std::endl;
            return false;
         }
         fTree[i]->GetEntry(--entry);
         t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
         if (fabs(t1 - t0) < best_deltas)
            best_deltas = fabs(t1 - t0);
         tsearch.push_back(t1);
      }
      while (t1 - t0 < -sync_delta_s) {
         if (++search > 999 or entry == entries - 1) {
            std::cerr << "Error in ACtree::Process - "
                      << "tree forward search failed for wedge " << i
                      << ", " << rep.str() << std::endl;
            return false;
         }
         fTree[i]->GetEntry(++entry);
         t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
         if (fabs(t1 - t0) < best_deltas)
            best_deltas = fabs(t1 - t0);
         tsearch.push_back(t1);
      }
      if (fabs(t1 - t0) > best_deltas) {
         fTree[i]->GetEntry(--entry);
         t1 = rec[i].tsec - tbases + rec[i].tnsec * 1.0e-9;
         tsearch.push_back(t1);
      }
      if (best_deltas > 2*sync_delta_s) {
         std::cerr << "Warning in ACtree::Process - "
                   << "no sync for wedge " << i 
                   << ": best delta t = " << rational(t1 - t0) << " seconds, "
                   << rep.str() << std::endl;
         std::cerr << "search failed for " << t0 << " among";
         for (int j=0; j < (int)tsearch.size(); ++j)
            std::cerr << " " << tsearch[j];
         std::cerr << std::endl;
         return false;
      }
      else {
         //joffset[i] = round((t1 - t0) / fadc_delta_s);
      }
      rep << rational(t1 - t0) << " ";
   }
   std::cout << rep.str() << std::endl;

   if (rec[0].current < baseline_current) {
      std::cerr << "baselines:";
      for (int i=0; i < 8; ++i) {
         double sum = 0;
         for (int j=0; j < 8192; ++j) {
            sum += rec[i].data[j];
         }
         baselines[i] *= (baseline_memory - 1) / baseline_memory;
         baselines[i] += sum / (8192 * baseline_memory);
         std::cerr << " " << baselines[i];
      }
      std::cerr << std::endl;
   }
   else if (rec[0].current > current_threshold) {
      ac_serial.trs = t0;
      ac_serial.cur = rec[0].current;
      ac_serial.gva = pow(10, 6 + rec[0].gain);
      for (int j=0; j < 8192; ++j) {
         float *currents = &ac_serial.ixp;
         int i;
         for (i=0; i < 8; ++i) {
            int jj = j - joffset[i];
            if (jj >= 0 && jj < 8192)
               currents[i] = rec[i].data[jj] - baselines[i];
            else
               break;
         }
         if (i == 8)
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
               if (ac_serial.trs > trs_ft_start && ac_serial.trs < trs_ft_end) {
                  FThist[j]->SetBinContent(i, a + sqrt(c*c + s*s));
                  FIhist[j]->Fill(fHz);
               }
               FTwork[j][0]->SetBinContent(i, 0);
               FTwork[j][1]->SetBinContent(i, 0);
            }
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
   for (int j=0; j < 8; ++j) {
      FThist[j]->Divide(FIhist[j]);
      FThist[j]->Write();
   }
   acfile->Close();
}

void ACtree::Terminate()
{
   // The Terminate() function is the last function to be called during
   // a query. It always runs on the client, it can be used to present
   // the results graphically or save the results to file.

}

std::string ACtree::rational(double ratio, int *numer, int *denom, double prec)
{
   // Try to find a ratio of small integers that approximates ratio

   int mindenom = 60;

   std::stringstream out;
   if (fabs(ratio) < prec) {
      if (numer)
         *numer = 0;
      if (denom)
         *denom = 1;
      out << 0;
      return out.str();
   }
   for (int d=mindenom; d < 1/prec; d++) {
      int n = round(ratio * d);
      if (fabs(ratio * d - n) < prec) {
         if (numer)
            *numer = n;
         if (denom)
            *denom = d;
         out << n << "/" << d;
         return out.str();
      }
      else {
         std::cerr << "bad rational " << ratio << "=" << n << "/" << d << " misses by " << ratio * d - n << std::endl;
         break;
      }
   }
   if (numer)
      *numer = 0;
   if (denom)
      *denom = 0;
   out << ratio;
   return out.str();
}
