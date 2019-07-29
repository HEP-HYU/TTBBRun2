//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Jan 31 23:15:22 2017 by ROOT version 6.06/01
// from TTree tree/TopTree
//
// Updated : 2017-07-25
// Developer : Seohyun
//
//////////////////////////////////////////////////////////

#ifndef MyAnalysis_h
#define MyAnalysis_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TH1D.h>
#include <TH2F.h>
// Headers needed by this particular selector
#include <vector>
#include <TLorentzVector.h>
#include <fstream>
#include <iostream>

#include "/home/seohyun/work/ttbb/heptool_Run2017/include/histBook.h"

class MyAnalysis : public TSelector {
public :
   TTreeReader     fReader;  //!the tree reader
   TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain

   // Readers to access the data (delete the ones you do not need).
   TTreeReaderValue<Int_t>   event             = {fReader, "event"};
   TTreeReaderValue<Int_t>   run               = {fReader, "run"};
   TTreeReaderValue<Int_t>   luminumber        = {fReader, "luminumber"};
   TTreeReaderValue<Float_t> genWeight         = {fReader, "genweight"};
   TTreeReaderValue<Int_t>   GoodPV            = {fReader, "GoodPV"};
   TTreeReaderValue<Int_t>   channel           = {fReader, "channel"};
   TTreeReaderArray<float>   PUWeight          = {fReader, "PUWeight"};
   TTreeReaderArray<float>   pdfweight         = {fReader, "lepton_SF"};
   TTreeReaderArray<float>   scaleweight       = {fReader, "lepton_SF"};
   TTreeReaderValue<Float_t> MET               = {fReader, "MET"};
   TTreeReaderValue<Float_t> MET_phi           = {fReader, "MET_phi"};
   TTreeReaderValue<Float_t> lepton_pT         = {fReader, "lepton_pt"};
   TTreeReaderValue<Float_t> lepton_eta        = {fReader, "lepton_eta"};
   TTreeReaderValue<Float_t> lepton_phi        = {fReader, "lepton_phi"};
   TTreeReaderValue<Float_t> lepton_E          = {fReader, "lepton_e"};
   TTreeReaderValue<Float_t> lepton_relIso     = {fReader, "lepton_relIso"};
   TTreeReaderValue<bool>    lepton_isIso      = {fReader, "lepton_isIso"};
   TTreeReaderArray<float>   lepton_SF         = {fReader, "lepton_SF"};
   TTreeReaderArray<float>   jet_pT            = {fReader, "jet_pt"};
   TTreeReaderArray<float>   jet_eta           = {fReader, "jet_eta"};
   TTreeReaderArray<float>   jet_phi           = {fReader, "jet_phi"};
   TTreeReaderArray<float>   jet_E             = {fReader, "jet_e"};
   TTreeReaderArray<int>     jet_index         = {fReader, "jet_index"};
   TTreeReaderArray<float>   jet_CSV           = {fReader, "jet_deepCSV"};
   //TTreeReaderArray<float>   jet_SF_CSV_25     = {fReader, "jet_SF_CSV_25"};
   TTreeReaderArray<float>   jet_SF_CSV_30     = {fReader, "jet_SF_deepCSV_30"};
   //TTreeReaderArray<float>   jet_SF_CSV_35     = {fReader, "jet_SF_CSV_35"};
   //TTreeReaderArray<float>   jet_SF_CSV_40     = {fReader, "jet_SF_CSV_40"};
   //TTreeReaderArray<float>   jet_SF_CSV        = {fReader, "jet_SF_deepCSV_30"};
   //TTreeReaderArray<float>   jet_CvsL          = {fReader, "jet_CvsL"};
   //TTreeReaderArray<float>   jet_CvsB          = {fReader, "jet_CvsB"};
   //TTreeReaderValue<Int_t>   jet_number        = {fReader, "jet_number"};
   //TTreeReaderArray<int>     jet_partonFlavour = {fReader, "jet_partonFlavour"};
   //TTreeReaderArray<int>     jet_hadronFlavour = {fReader, "jet_hadronFlavour"};
   TTreeReaderArray<float>   jet_JES_Up        = {fReader, "jet_JES_Up"};
   TTreeReaderArray<float>   jet_JES_Down      = {fReader, "jet_JES_Down"};
   TTreeReaderArray<float>   jet_JER_Up        = {fReader, "jet_JER_Up"};
   TTreeReaderArray<float>   jet_JER_Nom       = {fReader, "jet_JER_Nom"};
   TTreeReaderArray<float>   jet_JER_Down      = {fReader, "jet_JER_Down"};
   TTreeReaderValue<float>   addbjet1_pt       = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   addbjet1_eta      = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   addbjet1_phi      = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   addbjet1_e        = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   addbjet2_pt       = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   addbjet2_eta      = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   addbjet2_phi      = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   addbjet2_e        = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet1_pt     = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet1_eta    = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet1_phi    = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet1_e      = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet2_pt     = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet2_eta    = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet2_phi    = {fReader, "lepton_pt"};
   TTreeReaderValue<float>   mindRbjet2_e      = {fReader, "lepton_pt"};


   MyAnalysis(TTree * /*tree*/ =0) { }
   virtual        ~MyAnalysis() { }
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
   double          transverseMass(const TLorentzVector & l, const TLorentzVector & nu); 
   //double leptonSF(const TLorentzVector & lep);

   ClassDef(MyAnalysis,0);
   TString option;
   TString process;

   HistoBook *h_control;
   HistoBook *h_matrix;

   bool dosyst = false;
   string syst_ext = "";
};

#endif

#ifdef MyAnalysis_cxx
void MyAnalysis::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the reader is initialized.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).
  
   fReader.SetTree(tree);
}

Bool_t MyAnalysis::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


#endif // #ifdef MyAnalysis_cxx
