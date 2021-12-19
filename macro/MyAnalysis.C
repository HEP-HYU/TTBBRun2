#define MyAnalysis_cxx
#include <TH2.h>
#include <TStyle.h>

#include <boost/algorithm/string/replace.hpp>

#include "MyAnalysis.h"

using namespace TMath;
using namespace std;

void MyAnalysis::Begin(TTree * /*tree*/){
}

void MyAnalysis::SlaveBegin(TTree * /*tree*/){
  option = GetOption();
  process = option.Data();

  /*
   * Systematics 
   * PileUp
   *  __puup, __pudown
   * Muon
   *   __muidup, __muiddown, __muisoup, __muisodown, __mutrgup, __mutrgdown
   * Electron
   *   __elidup, __eliddown, __elrecoup, __elrecodown, __elzvtxup, __elzvtxdown
   *   __eltrgup, __eltrgdown
   * CSV shape
   *   __lfup, __lfdown, __hfup, __hfdown
   *   __hfstat1up, __hfstat1down, __hfstat2up, __hfstat2down
   *   __lfstat1up, __lfstat1down, __lfstat2up, __lfstat2down
   *   __cferr1up, __cferr1down, __cferr2up, __cferr2down
   * Scale Weight(ME)
   *   __scale0, __scale1, __scale2, __scale3, __scale4, __scale5
   * Parton Shower(PS)
   *   __isrup, __isrdown, __fsrup, __fsrdown
   * ME & PS
   *   __hdampup, __hdampdown
   *  Pythia Tune
   *   __tuneup, __tunedown
   */

  if( process.Contains("Data") || process.Contains("QCD") || process.Contains("Driven") || process.Contains("Nosys") ){
    if     ( process.Contains("qcdisoup")   ) v_syst.push_back("__qcdisoup");
    else if( process.Contains("qcdisodown") ) v_syst.push_back("__qcdisodown");
    else                                      v_syst.push_back("");
  }
  else if( process.Contains("__") ){
    //Pythia Tune, ME & PS Matching
    if( process.Contains("tuneup")    ) v_syst.push_back("__tuneup");
    if( process.Contains("tunedown")  ) v_syst.push_back("__tunedown");

    if( process.Contains("hdampup")   ) v_syst.push_back("__hdampup");
    if( process.Contains("hdampdown") ) v_syst.push_back("__hdampdown");

    if( process.Contains("isrup")   ) v_syst.push_back("__isrup");
    if( process.Contains("isrdown") ) v_syst.push_back("__isrdown");
    if( process.Contains("fsrup")   ) v_syst.push_back("__fsrup");
    if( process.Contains("fsrdown") ) v_syst.push_back("__fsrdown");

    if( process.Contains("jerup") )   v_syst.push_back("__jerup");
    if( process.Contains("jerdown") ) v_syst.push_back("__jerdown");
    if( process.Contains("jecup") )   v_syst.push_back("__jecup");
    if( process.Contains("jecdown") ) v_syst.push_back("__jecdown");
  }
  else{
    v_syst.push_back("");
    v_syst.insert(v_syst.end(), syst_basic.begin(), syst_basic.end());
    if( !process.Contains("2018") ){
      v_syst.push_back("__prefireup"); v_syst.push_back("__prefiredown");
    }
    if( process.Contains("TT") ){
      v_syst.push_back("__scale0"); v_syst.push_back("__scale1"); v_syst.push_back("__scale2");
	    v_syst.push_back("__scale3"); v_syst.push_back("__scale4"); v_syst.push_back("__scale5");
      if( process.Contains("2016") && !process.Contains("CP5") ){
 	      int maxpdf = 102;
	      std::string str_tmp;
        for( int i = 0; i < maxpdf; ++i){
          str_tmp = "__pdf" + to_string(i);
	        v_syst.push_back(str_tmp);
        }
      }
      else{
        v_syst.push_back("__isrup");  v_syst.push_back("__isrdown");
        v_syst.push_back("__fsrup");  v_syst.push_back("__fsrdown");
        int maxpdf = 104;
        std::string str_tmp;
        for( int i = 0; i < maxpdf; ++i){
          str_tmp = "__pdf" + to_string(i);
          v_syst.push_back(str_tmp);
        }
      }
    }
  }
  
  if( process.Contains("TT") ){
    pdfweight   = {fReader, "pdfweight"};
    scaleweight = {fReader, "scaleweight"};
    //if( !process.Contains("2016") || process.Contains("CP5") ) 
    psweight = {fReader, "psweight"};
  }
  if( process.Contains("TTLJ") && !process.Contains("Bkg") && !process.Contains("SYS") ){
    addbjet1_pt    = {fReader, "addbjet1_pt"};
    addbjet1_eta   = {fReader, "addbjet1_eta"};
    addbjet1_phi   = {fReader, "addbjet1_phi"};
    addbjet1_e     = {fReader, "addbjet1_e"};
    addbjet2_pt    = {fReader, "addbjet2_pt"};
    addbjet2_eta   = {fReader, "addbjet2_eta"};
    addbjet2_phi   = {fReader, "addbjet2_phi"};
    addbjet2_e     = {fReader, "addbjet2_e"};

    mindRbjet1_pt  = {fReader, "mindRjet1_pt"};
    mindRbjet1_eta = {fReader, "mindRjet1_eta"};
    mindRbjet1_phi = {fReader, "mindRjet1_phi"};
    mindRbjet1_e   = {fReader, "mindRjet1_e"};
    mindRbjet2_pt  = {fReader, "mindRjet2_pt"};
    mindRbjet2_eta = {fReader, "mindRjet2_eta"};
    mindRbjet2_phi = {fReader, "mindRjet2_phi"};
    mindRbjet2_e   = {fReader, "mindRjet2_e"};
  }
  if( process.Contains("2017") ){
    MUON_ETA_       = 2.4;
    ELECTRON_PT_    = 30.0;
    ELECTRON_ETA_   = 2.4;
    JET_CSV_TIGHT_  = 0.8001;
    JET_CSV_MEDIUM_ = 0.4941;
    JET_CSV_LOOSE_  = 0.1522;
  }
  if( process.Contains("2018") ){
    MUON_ETA_       = 2.4;
    ELECTRON_PT_    = 30.0;
    ELECTRON_ETA_   = 2.4;
    JET_CSV_TIGHT_  = 0.7527;
    JET_CSV_MEDIUM_ = 0.4184;
    JET_CSV_LOOSE_  = 0.1241;
  }

  for(unsigned int i = 0; i < v_syst.size(); i++){
    HistoBook *h_tmp1 = new HistoBook(1, v_syst[i].c_str());
    histBook.push_back(h_tmp1);
  }
   
  for(unsigned int i = 0; i < v_syst.size(); i++){
    for(int iChannel=0; iChannel<nChannel; ++iChannel){
      for(int iStep=0; iStep<nStep; ++iStep){
        if( i == 0 ){
          h_bSF[iChannel][iStep] = new TH1D(Form("h_bSFinfo_Ch%d_S%d", iChannel, iStep), "", 18, 0, 18);
          h_bSF[iChannel][iStep]->SetXTitle("bSF Sum of weight");
          h_bSF[iChannel][iStep]->Sumw2();
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(1, "Raw(without bSF)");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(2, "Nominal");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(3, "lfup");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(4, "lfdown");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(5, "hfup");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(6, "hfdown");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(7, "hfstat1up");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(8, "hfstat1down");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(9, "hfstat2up");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(10, "hfstat2down");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(11, "lfstat1up");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(12, "lfstat1down");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(13, "lfstat2up");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(14, "lfstat2down");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(15, "cferr1up");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(16, "cferr1down");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(17, "cferr2up");
          h_bSF[iChannel][iStep]->GetXaxis()->SetBinLabel(18, "cferr2down");
          fOutput->Add(h_bSF[iChannel][iStep]);
        }
        
        fOutput->Add(histBook[i]->h_lepton_pt[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_lepton_eta[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_lepton_relIso[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_njets[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_nbjets[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_trans_mass[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_pv[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_pv_nosf[iChannel][iStep]);
        
        for(int iJet=0; iJet<nJet; ++iJet){
          fOutput->Add(histBook[i]->h_jet_pt[iChannel][iStep][iJet]);
          fOutput->Add(histBook[i]->h_jet_eta[iChannel][iStep][iJet]);
          fOutput->Add(histBook[i]->h_csv[iChannel][iStep][iJet]);
        }

        fOutput->Add(histBook[i]->h_reco_addbjet1_pt[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_reco_addbjet1_csv[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_reco_addbjet2_pt[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_reco_addbjet2_csv[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_reco_addbjets_deltaR[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_reco_addbjets_invMass[iChannel][iStep]);

        fOutput->Add(histBook[i]->h_gen_mindR_addbjet1_pt[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_gen_mindR_addbjet2_pt[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_gen_mindR_deltaR[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_gen_mindR_invMass[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_respMatrix_mindR_deltaR[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_respMatrix_mindR_invMass[iChannel][iStep]);

        fOutput->Add(histBook[i]->h_gen_gentop_addbjet1_pt[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_gen_gentop_addbjet2_pt[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_gen_gentop_deltaR[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_gen_gentop_invMass[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_respMatrix_gentop_deltaR[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_respMatrix_gentop_invMass[iChannel][iStep]);

        for(int iBin=0; iBin < nbins_reco_addbjets_dR; iBin++)
          fOutput->Add(histBook[i]->h_reco_deltaRvsCSV_bin[iChannel][iStep][iBin]);
        for(int iBin=0; iBin < nbins_reco_addbjets_M; iBin++)
          fOutput->Add(histBook[i]->h_reco_invMassvsCSV_bin[iChannel][iStep][iBin]);
        fOutput->Add(histBook[i]->h_3Dmatrix_mindR_deltaR[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_3Dmatrix_mindR_invMass[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_3Dmatrix_gentop_deltaR[iChannel][iStep]);
        fOutput->Add(histBook[i]->h_3Dmatrix_gentop_invMass[iChannel][iStep]);
      }//step
    }//channel
  }//syst
}

Bool_t MyAnalysis::Process(Long64_t entry){
  fReader.SetEntry(entry);
  
  process = option.Data();
  const int mode = *channel;
  if(mode>2) return kTRUE;

  //Object selection
  TLorentzVector p4met;
  const double met = *MET;
  const double met_phi = *MET_phi;
  const double apt = TMath::Abs(met);
  const double met_x = apt*TMath::Cos(met_phi);
  const double met_y = apt*TMath::Sin(met_phi);
  p4met.SetPxPyPzE(met_x, met_y, 0, met);

  TLorentzVector lepton;
  lepton.SetPtEtaPhiE(*lepton_pT, *lepton_eta, *lepton_phi, *lepton_E);

  //const bool isQCD = transverseM < 20;
  //const bool doQCDestimation = false; // change this flags if you want to do the QCD estimation
  const double relIso = *lepton_relIso;
  //const bool isIso = doQCDestimation ? *lepton_isIso  : false ;

  //Object selection
  const bool passmuon = (mode == MUON_) && (lepton.Pt() > MUON_PT_) && (abs(lepton.Eta()) < MUON_ETA_);
  const bool passelectron = (mode == ELECTRON_) && (lepton.Pt() > ELECTRON_PT_) && (abs(lepton.Eta()) < ELECTRON_ETA_);
  if ( !passmuon and !passelectron ) return kTRUE;
  std::string syst_ext = v_syst[0];

  bool invertIso = false;
  if( passmuon ){
    if     ( syst_ext == "__qcdisoup"   ) invertIso = relIso > 0.4 ? true : false;
    else if( syst_ext == "__qcdisodown" ) invertIso = (relIso > 0.2 and relIso <= 0.4) ? true : false;
    else                                  invertIso = relIso > 0.2 ? true : false;
  }
  if( passelectron ){
    // 2016 electron
    // Isolation: <= 0.0588 in barrel region
    // Cut-based veto working point: I_rel > 0.175
    if     ( syst_ext == "__qcdisoup"   ) invertIso = relIso > 0.3 and relIso <= 0.85 ? true : false;
    else if( syst_ext == "__qcdisodown" ) invertIso = relIso > 0.06 and relIso <= 0.3 ? true : false; 
    else                                  invertIso = relIso > 0.06 and relIso < 0.85 ? true : false;
  }
  
  int njets = 0;
  int nbjets = 0;
  multimap<float /*jet_Pt*/,   TLorentzVector /*jet_4-momentum*/, greater<float>> m_jets;
  multimap<float /*jet_CSV*/,  TLorentzVector /*jet_4-momentum*/, greater<float>> m_jets_csv;
  multimap<float /*jet_CSV*/, TLorentzVector /*jet_4-momentum*/, greater<float>> m_bjets;
  for (unsigned int iJet = 0; iJet < jet_pT.GetSize() ; ++iJet) {
    float jetSystVar = 1.0;
    if( !process.Contains("Data") ){
      // Jet Energy Correction, Jet Energy Resolution
      if     ( syst_ext == "__jecup"   ) jetSystVar = jet_JER_Nom[iJet] * jet_JES_Up[iJet];
      else if( syst_ext == "__jecdown" ) jetSystVar = jet_JER_Nom[iJet] * jet_JES_Down[iJet];
      else if( syst_ext == "__jerup"   ) jetSystVar = jet_JER_Up[iJet];
      else if( syst_ext == "__jerdown" ) jetSystVar = jet_JER_Down[iJet];
      else                               jetSystVar = jet_JER_Nom[iJet];
    }

    TLorentzVector jet;
    jet.SetPtEtaPhiE(jet_pT[iJet], jet_eta[iJet], jet_phi[iJet], jet_E[iJet]);
    jet *= jetSystVar;

    if ( jet.Pt() <= JET_PT_ || abs(jet.Eta()) >= JET_ETA_ ) continue;

    //m_jets.insert(pair<float,TLorentzVector>(jet_CSV[iJet],jet));
    m_jets.insert(pair<float,TLorentzVector>(jet.Pt(),jet));
    m_jets_csv.insert(pair<float,TLorentzVector>(jet_CSV[iJet],jet));
    ++njets;
    if( jet_CSV[iJet] > JET_CSV_MEDIUM_ ){
      ++nbjets;
      m_bjets.insert(pair<float, TLorentzVector>(jet_CSV[iJet], jet));
    }
  }

  double a_jetPt[6]  = {-999,-999,-999,-999,-999,-999};
  double a_jetEta[6] = {-999,-999,-999,-999,-999,-999};
  int tmp_idx = 0;
  for(auto m_itr = m_jets.begin(); m_itr != m_jets.end(); ++m_itr){
    if(tmp_idx >= 6) continue;
    a_jetPt[tmp_idx] = m_itr->first;
    a_jetEta[tmp_idx] = (m_itr->second).Eta();
    ++tmp_idx;
  }
  tmp_idx = 0;
  double a_jetCSV[6] = {-999,-999,-999,-999,-999,-999};
  for(auto m_itr = m_jets_csv.begin(); m_itr != m_jets_csv.end(); ++m_itr){
    if(tmp_idx >= 6) continue;
    a_jetCSV[tmp_idx] = m_itr->first;
    ++tmp_idx;
  }

  TLorentzVector reco_addbjet1, reco_addbjet2;
  double reco_addbjet1_pt = -999, reco_addbjet2_pt = -999;
  double reco_addbjet1_csv = -999, reco_addbjet2_csv = -999;
  double reco_addbjets_deltaR = -999, reco_addbjets_invMass = -999;
  if (m_bjets.size() >= 2){
    for(auto m_itr = m_bjets.begin(); m_itr != m_bjets.end(); m_itr++){
      for(auto m_itr2 = m_itr; m_itr2 != m_bjets.end(); m_itr2++){
        if( m_itr->first == m_itr2->first ) continue;
        double tmp_dR = (m_itr->second).DeltaR(m_itr2->second);
        
        if(tmp_dR < abs(reco_addbjets_deltaR)){
          reco_addbjet1 = m_itr->second;
          reco_addbjet2 = m_itr2->second;
          reco_addbjet1_pt = reco_addbjet1.Pt();
          reco_addbjet2_pt = reco_addbjet2.Pt();
          reco_addbjet1_csv = m_itr->first;
          reco_addbjet2_csv = m_itr2->first;

          reco_addbjets_deltaR   = tmp_dR;
          reco_addbjets_invMass  = (reco_addbjet1 + reco_addbjet2).M();
        }
      }
    }
  }

  int dRregion = 999, Mregion = 999;
  int len_dR = sizeof(reco_addbjets_dR_width)/sizeof(*reco_addbjets_dR_width);
  int len_M = sizeof(reco_addbjets_M_width)/sizeof(*reco_addbjets_M_width);
  for(int i=0; i < len_dR-1; i++)
    if( reco_addbjets_deltaR >= reco_addbjets_dR_width[i] and reco_addbjets_deltaR < reco_addbjets_dR_width[i+1] ) dRregion = i;
  for(int i=0; i < len_M-1; i++)
    if( reco_addbjets_invMass >= reco_addbjets_M_width[i] and reco_addbjets_invMass < reco_addbjets_M_width[i+1] ) Mregion = i;

  double gen_gentop_addbjet1_pt = -999, gen_gentop_addbjet2_pt = -999;
  double gen_gentop_addbjets_deltaR = -999, gen_gentop_addbjets_invMass = -999;
  double gen_mindR_addbjet1_pt = -999, gen_mindR_addbjet2_pt = -999;
  double gen_mindR_addbjets_deltaR = -999, gen_mindR_addbjets_invMass = -999; 

  TLorentzVector gen_gentop_addbjet1, gen_gentop_addbjet2;
  TLorentzVector gen_mindR_addbjet1, gen_mindR_addbjet2;
  if( process.Contains("PowhegPythia_ttbb") ){
    gen_gentop_addbjet1.SetPtEtaPhiE(*addbjet1_pt, *addbjet1_eta, *addbjet1_phi, *addbjet1_e);
    gen_gentop_addbjet2.SetPtEtaPhiE(*addbjet2_pt, *addbjet2_eta, *addbjet2_phi, *addbjet2_e);

    gen_mindR_addbjet1.SetPtEtaPhiE(*mindRbjet1_pt, *mindRbjet1_eta, *mindRbjet1_phi, *mindRbjet1_e);
    gen_mindR_addbjet2.SetPtEtaPhiE(*mindRbjet2_pt, *mindRbjet2_eta, *mindRbjet2_phi, *mindRbjet2_e);
    
    gen_gentop_addbjet1_pt        = gen_gentop_addbjet1.Pt();
    gen_gentop_addbjet2_pt        = gen_gentop_addbjet2.Pt();
    gen_gentop_addbjets_deltaR    = gen_gentop_addbjet1.DeltaR(gen_gentop_addbjet2);
    gen_gentop_addbjets_invMass   = (gen_gentop_addbjet1+gen_gentop_addbjet2).M(); 
   
    gen_mindR_addbjet1_pt       = gen_mindR_addbjet1.Pt();
    gen_mindR_addbjet2_pt       = gen_mindR_addbjet2.Pt();
    gen_mindR_addbjets_deltaR   = gen_mindR_addbjet1.DeltaR(gen_mindR_addbjet2); 
    gen_mindR_addbjets_invMass  = (gen_mindR_addbjet1+gen_mindR_addbjet2).M(); 
  }

  int passchannel = -999;
  bool passlepton = false;
  if(  passmuon and !passelectron ){
     passchannel = MUON_;
     passlepton = true;
  }
  else if( !passmuon and  passelectron ){
    passchannel = ELECTRON_;
    passlepton = true;
  }
  
  bool eventSelection[nStep];
  for(int iStep = 0; iStep < nStep; iStep++) eventSelection[iStep] = false;

  if( process.Contains("dataDriven") ){
    eventSelection[0] = passlepton and invertIso;
    //Should change condition: invertIso and (passmuon or passelectron and abs(lepton.Eta()) <= 1.4445));
  }
  else{
    eventSelection[0] = passlepton;
  }
  eventSelection[1] = eventSelection[0] and njets >= 1;
  eventSelection[2] = eventSelection[0] and njets >= 2 and njets < 4;
  eventSelection[3] = eventSelection[0] and njets >= 4;
  eventSelection[4] = eventSelection[3] and nbjets >= 2;
  eventSelection[5] = eventSelection[0] and njets >= 2 and njets < 6;
  eventSelection[6] = eventSelection[0] and njets >= 6;
  eventSelection[7] = eventSelection[6] and nbjets >= 2;
  eventSelection[8] = eventSelection[6] and nbjets >= 3;
  eventSelection[9] = eventSelection[6] and nbjets >= 4;

  if( !eventSelection[0] ) return kTRUE;

  for(unsigned int iSys = 0; iSys < v_syst.size(); ++iSys){
    syst_ext = v_syst[iSys];
    //Event Weight
    double EventWeight = 1.0;
    double bSF = 1.0;
    if( !option.Contains("Data") ){
      EventWeight *= *genWeight;
      
      //Pile Up weight
      if     ( syst_ext == "__puup"   ) EventWeight *= PUWeight[1];
      else if( syst_ext == "__pudown" ) EventWeight *= PUWeight[2];
      else                              EventWeight *= PUWeight[0];
   
      //Prefire weight, 2016,17 only
      if     ( syst_ext == "__prefireup"   ) EventWeight *= prefireweight[1];
      else if( syst_ext == "__prefiredown" ) EventWeight *= prefireweight[2];
      else                                   EventWeight *= prefireweight[0];
      
      //Lepton Scale Factor
      if( passchannel == 0 ){
        //Muon
        //[0]~[2]:ID, [3]~[5]:Iso, [6]~[8]:Trigger
        if     ( syst_ext == "__muidup"    ) EventWeight *= lepton_SF[1];
        else if( syst_ext == "__muiddown"  ) EventWeight *= lepton_SF[2];
        else                                 EventWeight *= lepton_SF[0];

        if     ( syst_ext == "__muisoup"   ) EventWeight *= lepton_SF[4];
        else if( syst_ext == "__muisodown" ) EventWeight *= lepton_SF[5];
        else        	                       EventWeight *= lepton_SF[3];

        if     ( syst_ext == "__mutrgup"   ) EventWeight *= lepton_SF[7];
        else if( syst_ext == "__mutrgdown" ) EventWeight *= lepton_SF[8];
        else                                 EventWeight *= lepton_SF[6];
      }
      else if( passchannel == 1 ){
        //Electron
        //[0]~[2]: ID, [3]~[5]:Reco, [6]~[8]:Zvtx, [9]~[11]: Trigger
        if     ( syst_ext == "__elidup"     ) EventWeight *= lepton_SF[1];
        else if( syst_ext == "__eliddown"   ) EventWeight *= lepton_SF[2];
        else                                  EventWeight *= lepton_SF[0];

        if     ( syst_ext == "__elrecoup"   ) EventWeight *= lepton_SF[4];
        else if( syst_ext == "__elrecodown" ) EventWeight *= lepton_SF[5];
        else	                                EventWeight *= lepton_SF[3];

        if     ( syst_ext == "__elzvtxup"   ) EventWeight *= lepton_SF[7];
        else if( syst_ext == "__elzvtxdown" )	EventWeight *= lepton_SF[8];
        else	                                EventWeight *= lepton_SF[6];

        if     ( syst_ext == "__eltrgup"   )	EventWeight *= lepton_SF[10];
        else if( syst_ext == "__eltrgdown" )  EventWeight *= lepton_SF[11];
        else	                                EventWeight *= lepton_SF[9];
      }

      //Scale Weight(ME)
      //[0] = muF up , [1] = muF down, [2] = muR up, [3] = muR up && muF up
      //[4] = muR down, [5] = muF down && muF down
      if     ( syst_ext == "__scale0" ) EventWeight *= scaleweight[0];
      else if( syst_ext == "__scale1" ) EventWeight *= scaleweight[1];
      else if( syst_ext == "__scale2" )	EventWeight *= scaleweight[2];
      else if( syst_ext == "__scale3" )	EventWeight *= scaleweight[3];
      else if( syst_ext == "__scale4" )	EventWeight *= scaleweight[4];
      else if( syst_ext == "__scale5" )	EventWeight *= scaleweight[5];
      else                              EventWeight *= 1.0;
      
      //CSV Shape
      // Systematics for bottom flavor jets:
      //   Light flavor contamination: lf
      //   Linear and quadratic statistical fluctuations: hfstats1 and hfstats2
      // Systematics for light flavor jets:
      //   Heavy flavor contamination: hf
      //   Linear and quadratic statistical fluctuations: lfstats1 and lfstats2
      // Systematics for charm flavor jets:
      //   Linear and quadratic uncertainties: cferr1 and cferr2
      if     ( syst_ext == "__lfup"        ) bSF *= jet_SF_CSV_30[3];
      else if( syst_ext == "__lfdown"      ) bSF *= jet_SF_CSV_30[4];
      else if( syst_ext == "__hfup"        ) bSF *= jet_SF_CSV_30[5];
      else if( syst_ext == "__hfdown"      ) bSF *= jet_SF_CSV_30[6];
      else if( syst_ext == "__hfstat1up"   ) bSF *= jet_SF_CSV_30[7];
      else if( syst_ext == "__hfstat1down" ) bSF *= jet_SF_CSV_30[8];
      else if( syst_ext == "__hfstat2up"   ) bSF *= jet_SF_CSV_30[9];
      else if( syst_ext == "__hfstat2down" ) bSF *= jet_SF_CSV_30[10];
      else if( syst_ext == "__lfstat1up"   ) bSF *= jet_SF_CSV_30[11];
      else if( syst_ext == "__lfstat1down" ) bSF *= jet_SF_CSV_30[12];
      else if( syst_ext == "__lfstat2up"   ) bSF *= jet_SF_CSV_30[13];
      else if( syst_ext == "__lfstat2down" ) bSF *= jet_SF_CSV_30[14];
      else if( syst_ext == "__cferr1up"    ) bSF *= jet_SF_CSV_30[15];
      else if( syst_ext == "__cferr1down"  ) bSF *= jet_SF_CSV_30[16];
      else if( syst_ext == "__cferr2up"    ) bSF *= jet_SF_CSV_30[17];
      else if( syst_ext == "__cferr2down"  ) bSF *= jet_SF_CSV_30[18];
      else	                                 bSF *= jet_SF_CSV_30[0];
      
      for(int iStep=0; iStep < nStep; ++iStep){
        if( !eventSelection[iStep] ) continue;
        if( syst_ext == ""){
          h_bSF[passchannel][iStep]->Fill(0.5, EventWeight);
          h_bSF[passchannel][iStep]->Fill(1.5, bSF*EventWeight);
        }
        else if( syst_ext == "__lfup"        ) h_bSF[passchannel][iStep]->Fill(2.5,  bSF*EventWeight);
        else if( syst_ext == "__lfdown"      ) h_bSF[passchannel][iStep]->Fill(3.5,  bSF*EventWeight);
        else if( syst_ext == "__hfup"        ) h_bSF[passchannel][iStep]->Fill(4.5,  bSF*EventWeight);
        else if( syst_ext == "__hfdown"      ) h_bSF[passchannel][iStep]->Fill(5.5,  bSF*EventWeight);
        else if( syst_ext == "__hfstat1up"   ) h_bSF[passchannel][iStep]->Fill(6.5,  bSF*EventWeight);
        else if( syst_ext == "__hfstat1down" ) h_bSF[passchannel][iStep]->Fill(7.5,  bSF*EventWeight);
        else if( syst_ext == "__hfstat2up"   ) h_bSF[passchannel][iStep]->Fill(8.5,  bSF*EventWeight);
        else if( syst_ext == "__hfstat2down" ) h_bSF[passchannel][iStep]->Fill(9.5,  bSF*EventWeight);
        else if( syst_ext == "__lfstat1up"   ) h_bSF[passchannel][iStep]->Fill(10.5, bSF*EventWeight); 
        else if( syst_ext == "__lfstat1down" ) h_bSF[passchannel][iStep]->Fill(11.5, bSF*EventWeight); 
        else if( syst_ext == "__lfstat2up"   ) h_bSF[passchannel][iStep]->Fill(12.5, bSF*EventWeight); 
        else if( syst_ext == "__lfstat2down" ) h_bSF[passchannel][iStep]->Fill(13.5, bSF*EventWeight);
        else if( syst_ext == "__cferr1up"    ) h_bSF[passchannel][iStep]->Fill(14.5, bSF*EventWeight);
        else if( syst_ext == "__cferr1down"  ) h_bSF[passchannel][iStep]->Fill(15.5, bSF*EventWeight);
        else if( syst_ext == "__cferr2up"    ) h_bSF[passchannel][iStep]->Fill(16.5, bSF*EventWeight);
        else if( syst_ext == "__cferr2down"  ) h_bSF[passchannel][iStep]->Fill(17.5, bSF*EventWeight);
      }

      //Parton Shower
      //if( !process.Contains("2016") || process.Contains("CP5") ){
      if      ( syst_ext == "__isrup"   ) EventWeight *= psweight[0];
      else if ( syst_ext == "__isrdown" ) EventWeight *= psweight[2];
      else if ( syst_ext == "__fsrup"   ) EventWeight *= psweight[1];
      else if ( syst_ext == "__fsrdown" ) EventWeight *= psweight[3];
      else                                EventWeight *= 1.0;
      //}

      //PDF Uncertainties
      size_t pos;
      if( (pos = syst_ext.find("pdf",0)) != std::string::npos ){
        int maxpdf = 104;
        //if( process.Contains("2016") && !process.Contains("CP5") ) maxpdf = 102;
        for( int i = 0; i < maxpdf; ++i){
          std::string str_tmp = "pdf" + to_string(i);
          if( (pos = syst_ext.find(str_tmp)) != std::string::npos ){
            EventWeight *= pdfweight[i];
            break;
          }
        }
      }
    }// EventWeight

    for(int iStep=0; iStep < nStep; iStep++){
      if( !eventSelection[iStep] ) continue;
      histBook[iSys]->h_pv[passchannel][iStep]     ->Fill(*GoodPV, bSF*EventWeight);
      histBook[iSys]->h_pv_nosf[passchannel][iStep]->Fill(*GoodPV, bSF*EventWeight/PUWeight[0]);
      
      histBook[iSys]->h_lepton_pt[passchannel][iStep]    ->Fill(lepton.Pt(), bSF*EventWeight);
      histBook[iSys]->h_lepton_eta[passchannel][iStep]   ->Fill(abs(lepton.Eta()), bSF*EventWeight);
      histBook[iSys]->h_lepton_relIso[passchannel][iStep]->Fill(relIso, bSF*EventWeight);
      
      histBook[iSys]->h_trans_mass[passchannel][iStep]->Fill(transverseMass(lepton,p4met), bSF*EventWeight);
      
      histBook[iSys]->h_njets[passchannel][iStep] ->Fill(njets, bSF*EventWeight);
      histBook[iSys]->h_nbjets[passchannel][iStep]->Fill(nbjets, bSF*EventWeight);

      for(int iJet=0; iJet<nJet; iJet++){
        histBook[iSys]->h_jet_pt[passchannel][iStep][iJet] ->Fill(a_jetPt[iJet],  bSF*EventWeight);
        histBook[iSys]->h_jet_eta[passchannel][iStep][iJet]->Fill(a_jetEta[iJet], bSF*EventWeight);
        histBook[iSys]->h_csv[passchannel][iStep][iJet]    ->Fill(a_jetCSV[iJet], bSF*EventWeight);
      }
     
      histBook[iSys]->h_reco_addbjet1_pt[passchannel][iStep]     ->Fill(reco_addbjet1_pt, bSF*EventWeight); 
      histBook[iSys]->h_reco_addbjet1_csv[passchannel][iStep]    ->Fill(reco_addbjet1_csv, bSF*EventWeight); 
      histBook[iSys]->h_reco_addbjet2_pt[passchannel][iStep]     ->Fill(reco_addbjet2_pt, bSF*EventWeight); 
      histBook[iSys]->h_reco_addbjet2_csv[passchannel][iStep]    ->Fill(reco_addbjet2_csv, bSF*EventWeight); 
      histBook[iSys]->h_reco_addbjets_deltaR[passchannel][iStep] ->Fill(reco_addbjets_deltaR, bSF*EventWeight);
      histBook[iSys]->h_reco_addbjets_invMass[passchannel][iStep]->Fill(reco_addbjets_invMass, bSF*EventWeight);
      
      histBook[iSys]->h_gen_mindR_addbjet1_pt[passchannel][iStep]   ->Fill(gen_mindR_addbjet1_pt, bSF*EventWeight);
      histBook[iSys]->h_gen_mindR_addbjet2_pt[passchannel][iStep]   ->Fill(gen_mindR_addbjet2_pt, bSF*EventWeight);
      histBook[iSys]->h_gen_mindR_deltaR[passchannel][iStep]        ->Fill(gen_mindR_addbjets_deltaR, bSF*EventWeight);
      histBook[iSys]->h_gen_mindR_invMass[passchannel][iStep]       ->Fill(gen_mindR_addbjets_invMass, bSF*EventWeight);
      histBook[iSys]->h_respMatrix_mindR_deltaR[passchannel][iStep] ->Fill(reco_addbjets_deltaR,  gen_mindR_addbjets_deltaR, bSF*EventWeight);
      histBook[iSys]->h_respMatrix_mindR_invMass[passchannel][iStep]->Fill(reco_addbjets_invMass, gen_mindR_addbjets_invMass, bSF*EventWeight);

      histBook[iSys]->h_gen_gentop_addbjet1_pt[passchannel][iStep]   ->Fill(gen_gentop_addbjet1_pt, bSF*EventWeight);
      histBook[iSys]->h_gen_gentop_addbjet2_pt[passchannel][iStep]   ->Fill(gen_gentop_addbjet2_pt, bSF*EventWeight);
      histBook[iSys]->h_gen_gentop_deltaR[passchannel][iStep]        ->Fill(gen_gentop_addbjets_deltaR, bSF*EventWeight);
      histBook[iSys]->h_gen_gentop_invMass[passchannel][iStep]       ->Fill(gen_gentop_addbjets_invMass, bSF*EventWeight);
      histBook[iSys]->h_respMatrix_gentop_deltaR[passchannel][iStep] ->Fill(reco_addbjets_deltaR, gen_gentop_addbjets_deltaR, bSF*EventWeight);
      histBook[iSys]->h_respMatrix_gentop_invMass[passchannel][iStep]->Fill(reco_addbjets_invMass, gen_gentop_addbjets_invMass, bSF*EventWeight);

      if( dRregion != 999 ) histBook[iSys]->h_reco_deltaRvsCSV_bin[passchannel][iStep][dRregion]->Fill(reco_addbjet1_csv, bSF*EventWeight);
      histBook[iSys]->h_3Dmatrix_mindR_deltaR[passchannel][iStep]->Fill(reco_addbjets_deltaR, gen_mindR_addbjets_deltaR, reco_addbjet1_csv, bSF*EventWeight);
      histBook[iSys]->h_3Dmatrix_gentop_deltaR[passchannel][iStep]->Fill(reco_addbjets_deltaR, gen_gentop_addbjets_deltaR, reco_addbjet1_csv, bSF*EventWeight);

      if( Mregion != 999 ) histBook[iSys]->h_reco_invMassvsCSV_bin[passchannel][iStep][Mregion]->Fill(reco_addbjet1_csv, bSF*EventWeight);
      histBook[iSys]->h_3Dmatrix_mindR_invMass[passchannel][iStep]->Fill(reco_addbjets_invMass, gen_mindR_addbjets_invMass, reco_addbjet1_csv, bSF*EventWeight);
      histBook[iSys]->h_3Dmatrix_gentop_invMass[passchannel][iStep]->Fill(reco_addbjets_invMass, gen_gentop_addbjets_invMass, reco_addbjet1_csv, bSF*EventWeight);
    }//iStep
  }
  return kTRUE;
}

void MyAnalysis::SlaveTerminate(){
  option = GetOption();
}

void MyAnalysis::Terminate(){
  option = GetOption();
  process = option.Data();
  string str_opt = option.Data();

  size_t first_idx = str_opt.find_first_of("/");
  size_t last_idx  = str_opt.find_last_of("/");

  string outname = str_opt.substr(last_idx+1,string::npos);
  string sample  = str_opt.substr(first_idx+1, last_idx-first_idx-1);

  int year = 999;
  if( process.Contains("2016") ) year = 16;
  if( process.Contains("2017") ) year = 17;
  if( process.Contains("2018") ) year = 18;

  TFile *out;
  if( process.Contains("Tree") ) 
    out = TFile::Open(Form("output/root%d/%s/hist_%s.root", year, sample.c_str(), outname.c_str()), "RECREATE");
  else 
    out = TFile::Open(Form("output/root%d/hist_%s.root", year, sample.c_str()), "RECREATE");
  
  TIter next(GetOutputList());
  TObject *obj = 0;
  while( (obj = next()) ){
    const char *name = obj->GetName();
    std::string str(name);
    if(str.find("Ch2") != std::string::npos ){
      std::string strMuon = boost::replace_all_copy(str, "Ch2", "Ch0");
      std::string strElec = boost::replace_all_copy(str, "Ch2", "Ch1");
      TList *tmp = new TList;
      if( obj->InheritsFrom(TH1D::Class()) ){
        auto htmp = dynamic_cast<TH1D *>(obj);
        tmp->Add((TH1D *)fOutput->FindObject(strMuon.c_str()));
        tmp->Add((TH1D *)fOutput->FindObject(strElec.c_str()));
        htmp->Merge(tmp);
      }
      else if( obj->InheritsFrom(TH2D::Class()) ){
        auto htmp = dynamic_cast<TH2D *>(obj);
        tmp->Add((TH2D *)fOutput->FindObject(strMuon.c_str()));
        tmp->Add((TH2D *)fOutput->FindObject(strElec.c_str()));
        htmp->Merge(tmp);     
      }
      else if( obj->InheritsFrom(TH3D::Class()) ){
        auto htmp = dynamic_cast<TH3D *>(obj);
        tmp->Add((TH3D *)fOutput->FindObject(strMuon.c_str()));
        tmp->Add((TH3D *)fOutput->FindObject(strElec.c_str()));
        htmp->Merge(tmp);          
      }
    }
    if(str.find("h_") != std::string::npos ) obj->Write();
  }
  
  out->Write();
  out->Close();
}

double MyAnalysis::transverseMass(const TLorentzVector & lepton, const TLorentzVector & met){

  TLorentzVector leptonT(lepton.Px(),lepton.Py(),0.,lepton.E()*TMath::Sin(lepton.Theta()));
  TLorentzVector metT(met.Px(), met.Py(), 0, met.E());

  return (leptonT+metT).M();
}
