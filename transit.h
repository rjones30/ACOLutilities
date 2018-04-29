//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Sat Apr 28 13:18:10 2018 by ROOT version 6.06/08
// from TTree act/active collimator stream sequence
// found on file: ac_20180423_213439_serial.root
//////////////////////////////////////////////////////////

#ifndef transit_h
#define transit_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>

// Headers needed by this particular selector


class transit : public TSelector {
public :
   TTreeReader     fReader;  //!the tree reader
   TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain

   // Readers to access the data (delete the ones you do not need).
   TTreeReaderValue<Double_t> trs = {fReader, "stream.trs"};
   TTreeReaderValue<Float_t> ixp = {fReader, "stream.ixp"};
   TTreeReaderValue<Float_t> ixm = {fReader, "stream.ixm"};
   TTreeReaderValue<Float_t> iyp = {fReader, "stream.iyp"};
   TTreeReaderValue<Float_t> iym = {fReader, "stream.iym"};
   TTreeReaderValue<Float_t> oxp = {fReader, "stream.oxp"};
   TTreeReaderValue<Float_t> oxm = {fReader, "stream.oxm"};
   TTreeReaderValue<Float_t> oyp = {fReader, "stream.oyp"};
   TTreeReaderValue<Float_t> oym = {fReader, "stream.oym"};
   TTreeReaderValue<Float_t> cur = {fReader, "stream.cur"};
   TTreeReaderValue<Float_t> gva = {fReader, "stream.gva"};


   transit(TTree * /*tree*/ =0) { }
   virtual ~transit() { }
   virtual Int_t   Version() const { return 2; }
   virtual void    Begin(TTree *tree);
   virtual void    SlaveBegin(TTree *tree);
   virtual void    Init(TTree *tree);
   virtual Bool_t  Notify();
   virtual Bool_t  Process(Long64_t entry);
   virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
   virtual void    SetOption(const char *option) { fOption = option; }
   virtual void    SetObject(TObject *obj) { fObject = obj; }
   virtual void    SetInputList(TList *input) { fInput = input; }
   virtual TList  *GetOutputList() const { return fOutput; }
   virtual void    SlaveTerminate();
   virtual void    Terminate();

   void show_transit(Long64_t entry);

   ClassDef(transit,0);

};

#endif

#ifdef transit_cxx
void transit::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the reader is initialized.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   fReader.SetTree(tree);
}

Bool_t transit::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


#endif // #ifdef transit_cxx
