#include "histBook.h"

void runGentree(std::string input_path, std::string output_path){
  TFile *f_in = TFile::Open(Form("%s/TTLJ_PowhegPythia_ttbb.root", input_path.c_str()));
  TFile *f_out = TFile::Open(Form("%s/hist_gen.root", output_path.c_str()), "recreate");

  TTreeReader gentree("ttbbLepJets/gentree", f_in);
  //TTreeReaderValue<Int_t>   event          = {gentree, "event"};
  TTreeReaderValue<Float_t> genweight      = {gentree, "genweight"};
  TTreeReaderValue<Int_t>   channel        = {gentree, "genchannel"};
  TTreeReaderValue<float>   mindRbjet1_pt  = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   mindRbjet1_eta = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   mindRbjet1_phi = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   mindRbjet1_e   = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   mindRbjet2_pt  = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   mindRbjet2_eta = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   mindRbjet2_phi = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   mindRbjet2_e   = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   addbjet1_pt    = {gentree, "addbjet1_pt"};
  TTreeReaderValue<float>   addbjet1_eta   = {gentree, "addbjet1_eta"};
  TTreeReaderValue<float>   addbjet1_phi   = {gentree, "addbjet1_phi"};
  TTreeReaderValue<float>   addbjet1_e     = {gentree, "addbjet1_e"};
  TTreeReaderValue<float>   addbjet2_pt    = {gentree, "addbjet2_pt"};
  TTreeReaderValue<float>   addbjet2_eta   = {gentree, "addbjet2_eta"};
  TTreeReaderValue<float>   addbjet2_phi   = {gentree, "addbjet2_phi"};
  TTreeReaderValue<float>   addbjet2_e     = {gentree, "addbjet2_e"};

  ssize_t pos;
  if((pos = input_path.find("2016")) != std::string::npos ){
    mindRbjet1_pt  = {gentree, "mindRbjet1_pt"};
    mindRbjet1_eta = {gentree, "mindRbjet1_eta"};
    mindRbjet1_phi = {gentree, "mindRbjet1_phi"};
    mindRbjet1_e   = {gentree, "mindRbjet1_e"};
    mindRbjet2_pt  = {gentree, "mindRbjet2_pt"};
    mindRbjet2_eta = {gentree, "mindRbjet2_eta"};
    mindRbjet2_phi = {gentree, "mindRbjet2_phi"};
    mindRbjet2_e   = {gentree, "mindRbjet2_e"};
  }
  else{
    mindRbjet1_pt  = {gentree, "mindRjet1_pt"};
    mindRbjet1_eta = {gentree, "mindRjet1_eta"};
    mindRbjet1_phi = {gentree, "mindRjet1_phi"};
    mindRbjet1_e   = {gentree, "mindRjet1_e"};
    mindRbjet2_pt  = {gentree, "mindRjet2_pt"};
    mindRbjet2_eta = {gentree, "mindRjet2_eta"};
    mindRbjet2_phi = {gentree, "mindRjet2_phi"};
    mindRbjet2_e   = {gentree, "mindRjet2_e"};
  }

  TH1D *h_gen_gentop_deltaR_nosel[nChannel];
  TH1D *h_gen_gentop_invMass_nosel[nChannel];
  TH1D *h_gen_gentop_deltaEta_nosel[nChannel];
  TH1D *h_gen_gentop_deltaPhi_nosel[nChannel];
  TH1D *h_gen_mindR_deltaR_nosel[nChannel];
  TH1D *h_gen_mindR_invMass_nosel[nChannel];
  TH1D *h_gen_mindR_deltaEta_nosel[nChannel];
  TH1D *h_gen_mindR_deltaPhi_nosel[nChannel];
 
  for(int ich=0; ich < nChannel; ++ich){
    h_gen_gentop_deltaR_nosel[ich] = new TH1D(
      Form("h_gentop_%s_Ch%d_nosel",GEN_ADD_DR_,ich),"",
      nbins_gen_addbjets_dR,
      //gen_addbjets_dR_min, gen_addbjets_dR_max,
      gen_addbjets_dR_width
      );
    h_gen_gentop_deltaR_nosel[ich]->SetXTitle(Form("#DeltaR_{b#bar{b}}"));
    h_gen_gentop_deltaR_nosel[ich]->SetYTitle("Entries");
    h_gen_gentop_deltaR_nosel[ich]->Sumw2();
      
    h_gen_gentop_invMass_nosel[ich] = new TH1D(
      Form("h_gentop_%s_Ch%d_nosel",GEN_ADD_M_,ich),"",
      nbins_gen_addbjets_M,
      //gen_addbjets_M_min, gen_addbjets_M_max,
      gen_addbjets_M_width
      );
    h_gen_gentop_invMass_nosel[ich]->SetXTitle(Form("M_{b#bar{b}}"));
    h_gen_gentop_invMass_nosel[ich]->SetYTitle("Entries");
    h_gen_gentop_invMass_nosel[ich]->Sumw2();

    h_gen_gentop_deltaEta_nosel[ich] = new TH1D(
      Form("h_gentop_%s_Ch%d_nosel",GEN_ADD_DETA_,ich),"",
      nbins_gen_addbjets_dEta,
      gen_addbjets_dEta_min, gen_addbjets_dEta_max
      //gen_addbjets_dEta_width
      );
    h_gen_gentop_deltaEta_nosel[ich]->SetXTitle(Form("#Delta#eta_{b#bar{b}}"));
    h_gen_gentop_deltaEta_nosel[ich]->SetYTitle("Entries");
    h_gen_gentop_deltaEta_nosel[ich]->Sumw2();

    h_gen_gentop_deltaPhi_nosel[ich] = new TH1D(
      Form("h_gentop_%s_Ch%d_nosel",GEN_ADD_DPHI_,ich),"",
      nbins_gen_addbjets_dPhi,
      gen_addbjets_dPhi_min, gen_addbjets_dPhi_max
      //gen_addbjets_dPhi_width
      );
    h_gen_gentop_deltaPhi_nosel[ich]->SetXTitle(Form("#Delta#phi_{b#bar{b}}"));
    h_gen_gentop_deltaPhi_nosel[ich]->SetYTitle("Entries");
    h_gen_gentop_deltaPhi_nosel[ich]->Sumw2();
    
    h_gen_mindR_deltaR_nosel[ich] = new TH1D(
      Form("h_mindR_%s_Ch%d_nosel",GEN_ADD_DR_,ich),"",
      nbins_gen_addbjets_dR,
      //gen_addbjets_dR_min, gen_addbjets_dR_max,
      gen_addbjets_dR_width
      );
    h_gen_mindR_deltaR_nosel[ich]->SetXTitle(Form("#DeltaR_{b#bar{b}}"));
    h_gen_mindR_deltaR_nosel[ich]->SetYTitle("Entries");
    h_gen_mindR_deltaR_nosel[ich]->Sumw2();
      
    h_gen_mindR_invMass_nosel[ich] = new TH1D(
      Form("h_mindR_%s_Ch%d_nosel",GEN_ADD_M_,ich),"",
      nbins_gen_addbjets_M,
      //gen_addbjets_M_min, gen_addbjets_M_max,
      gen_addbjets_M_width
      );
    h_gen_mindR_invMass_nosel[ich]->SetXTitle(Form("M_{b#bar{b}}"));
    h_gen_mindR_invMass_nosel[ich]->SetYTitle("Entries");
    h_gen_mindR_invMass_nosel[ich]->Sumw2();

    h_gen_mindR_deltaEta_nosel[ich] = new TH1D(
      Form("h_mindR_%s_Ch%d_nosel",GEN_ADD_DETA_,ich),"",
      nbins_gen_addbjets_dEta,
      gen_addbjets_dEta_min, gen_addbjets_dEta_max
      //gen_addbjets_dEta_width
      );
    h_gen_mindR_deltaEta_nosel[ich]->SetXTitle(Form("#Delta#eta_{b#bar{b}}"));
    h_gen_mindR_deltaEta_nosel[ich]->SetYTitle("Entries");
    h_gen_mindR_deltaEta_nosel[ich]->Sumw2();

    h_gen_mindR_deltaPhi_nosel[ich] = new TH1D(
      Form("h_mindR_%s_Ch%d_nosel",GEN_ADD_DPHI_,ich),"",
      nbins_gen_addbjets_dPhi,
      gen_addbjets_dPhi_min, gen_addbjets_dPhi_max
      //gen_addbjets_dPhi_width
      );
    h_gen_mindR_deltaPhi_nosel[ich]->SetXTitle(Form("#Delta#phi_{b#bar{b}}"));
    h_gen_mindR_deltaPhi_nosel[ich]->SetYTitle("Entries");
    h_gen_mindR_deltaPhi_nosel[ich]->Sumw2();
  }

  std::cout << "Start" << std::endl;
  while(gentree.Next()){
    TLorentzVector mindRbjet1, mindRbjet2;
    mindRbjet1.SetPtEtaPhiE(*mindRbjet1_pt, *mindRbjet1_eta, *mindRbjet1_phi, *mindRbjet1_e);
    mindRbjet2.SetPtEtaPhiE(*mindRbjet2_pt, *mindRbjet2_eta, *mindRbjet2_phi, *mindRbjet2_e);
  
    TLorentzVector addbjet1, addbjet2;
    addbjet1.SetPtEtaPhiE(*addbjet1_pt, *addbjet1_eta, *addbjet1_phi, *addbjet1_e);
    addbjet2.SetPtEtaPhiE(*addbjet2_pt, *addbjet2_eta, *addbjet2_phi, *addbjet2_e);

    double mindR_dR = -999, mindR_M = -999, mindR_dEta = -999, mindR_dPhi = -999; 
    double addbjet_dR = -999, addbjet_M = -999, addbjet_dEta = -999, addbjet_dPhi = -999;

    mindR_dR   = mindRbjet1.DeltaR(mindRbjet2);
    mindR_M    = (mindRbjet1 + mindRbjet2).M();
    mindR_dEta = abs(mindRbjet1.Eta() - mindRbjet2.Eta());
    mindR_dPhi = mindRbjet1.DeltaPhi(mindRbjet2);

    addbjet_dR   = addbjet1.DeltaR(addbjet2);
    addbjet_M    = (addbjet1 + addbjet2).M();
    addbjet_dEta = abs(addbjet1.Eta() - addbjet2.Eta());
    addbjet_dPhi = addbjet1.DeltaPhi(addbjet2);

    h_gen_gentop_deltaR_nosel[*channel]  ->Fill(addbjet_dR,   *genweight);
    h_gen_gentop_invMass_nosel[*channel] ->Fill(addbjet_M,    *genweight);
    h_gen_gentop_deltaEta_nosel[*channel]->Fill(addbjet_dEta, *genweight);
    h_gen_gentop_deltaPhi_nosel[*channel]->Fill(addbjet_dPhi, *genweight);
    
    h_gen_mindR_deltaR_nosel[*channel]  ->Fill(mindR_dR,   *genweight);
    h_gen_mindR_invMass_nosel[*channel] ->Fill(mindR_M,    *genweight);
    h_gen_mindR_deltaEta_nosel[*channel]->Fill(mindR_dEta, *genweight);
    h_gen_mindR_deltaPhi_nosel[*channel]->Fill(mindR_dPhi, *genweight);

    if(*channel == 0 or *channel == 1){
      h_gen_gentop_deltaR_nosel[2]  ->Fill(addbjet_dR,   *genweight);
      h_gen_gentop_invMass_nosel[2] ->Fill(addbjet_M,    *genweight);
      h_gen_gentop_deltaEta_nosel[2]->Fill(addbjet_dEta, *genweight);
      h_gen_gentop_deltaPhi_nosel[2]->Fill(addbjet_dPhi, *genweight);
      
      h_gen_mindR_deltaR_nosel[2]  ->Fill(mindR_dR,   *genweight);
      h_gen_mindR_invMass_nosel[2] ->Fill(mindR_M,    *genweight);
      h_gen_mindR_deltaEta_nosel[2]->Fill(mindR_dEta, *genweight);
      h_gen_mindR_deltaPhi_nosel[2]->Fill(mindR_dPhi, *genweight);
    }
  }

  f_out->cd(); 
  for(int ich=0; ich<nChannel; ++ich){
    h_gen_gentop_deltaR_nosel[ich]->Write();
    h_gen_gentop_invMass_nosel[ich]->Write();
    h_gen_gentop_deltaEta_nosel[ich]->Write();
    h_gen_gentop_deltaPhi_nosel[ich]->Write();
    h_gen_mindR_deltaR_nosel[ich]->Write();
    h_gen_mindR_invMass_nosel[ich]->Write();
    h_gen_mindR_deltaEta_nosel[ich]->Write();
    h_gen_mindR_deltaPhi_nosel[ich]->Write();
  }
  f_out->Close();
}
