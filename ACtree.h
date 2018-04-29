//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Apr 24 15:39:22 2018 by ROOT version 6.06/08
// from TTree N9:raw_XP/AC records
// found on file: data/ac_20180423_213439.root
//////////////////////////////////////////////////////////

#ifndef ACtree_h
#define ACtree_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH1D.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>

// Headers needed by this particular selector


class ACtree : public TSelector {
public :
   TTree *fChain = 0;   //!pointer to the analyzed TTree or TChain
   TTree *fTree[8];

   // Local variables to access the data
   struct record_t {
      Long64_t tsec;
      Long64_t tnsec;
      Float_t data[8192];
      Float_t current;
      Short_t gain;
   } rec[8];

   // Fourier transform histograms of waveforms
   TH1D *FThist[8];
   TH1D *FTwork[8][2];

   // Output tree serializes the parallel data streams
   struct ac_t {
      double trs;
      float ixp;
      float ixm;
      float iyp;
      float iym;
      float oxp;
      float oxm;
      float oyp;
      float oym;
      float cur;
      float gva;
   } ac_serial;
#  define AC_FORM "trs/D:ixp/F:ixm/F:iyp/F:iym/F:oxp/F:oxm/F:oyp/F:oym/F:cur/F:gva/F"
   TTree *actree;
   TFile *acfile;
   Long64_t tbases = -1;

   ACtree(TTree * /*tree*/ =0) { }
   virtual ~ACtree() { }
   virtual Int_t   Version() const { return 2; }
   virtual void    Begin(TTree *tree);
   virtual void    SlaveBegin(TTree *tree);
   virtual void    Init(TTree *tree);
   virtual Bool_t  Notify();
   virtual Bool_t  Process(Long64_t entry);
   virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) {
      return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0;
   }
   virtual void    SetOption(const char *option) { fOption = option; }
   virtual void    SetObject(TObject *obj) { fObject = obj; }
   virtual void    SetInputList(TList *input) { fInput = input; }
   virtual TList  *GetOutputList() const { return fOutput; }
   virtual void    SlaveTerminate();
   virtual void    Terminate();

   ClassDef(ACtree,0);

};

#endif

#ifdef ACtree_cxx
void ACtree::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the reader is initialized.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   fTree[0] = (TTree*)tree->GetDirectory()->Get("N9:raw_XP");
   fTree[1] = (TTree*)tree->GetDirectory()->Get("N9:raw_XM");
   fTree[2] = (TTree*)tree->GetDirectory()->Get("N9:raw_YP");
   fTree[3] = (TTree*)tree->GetDirectory()->Get("N9:raw_YM");
   fTree[4] = (TTree*)tree->GetDirectory()->Get("N10:raw_XP");
   fTree[5] = (TTree*)tree->GetDirectory()->Get("N10:raw_XM");
   fTree[6] = (TTree*)tree->GetDirectory()->Get("N10:raw_YP");
   fTree[7] = (TTree*)tree->GetDirectory()->Get("N10:raw_YM");
   for (int i=0; i < 8; ++i) {
      if (fTree[i] == 0) {
         std::cerr << "Error in ACtree::Init - "
                      "tree " << i << " does not exist in input directory" << std::endl;
         exit(1);
      }
      fTree[i]->SetBranchAddress("record", &rec[i].tsec);
   }
}

Bool_t ACtree::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


#endif // #ifdef ACtree_cxx
