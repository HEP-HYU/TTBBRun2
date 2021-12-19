#pragma once

#include <vector>
#include <map>
#include <iostream>
#include <string>
#include <algorithm>
#include <fstream>
#include <sstream>

#include <boost/algorithm/string/replace.hpp>

#include <TFile.h>
#include <TCanvas.h>
#include <TMath.h>
#include <TLegend.h>
#include <TAttFill.h>
#include <TPaveText.h>
#include <TROOT.h>
#include <TSystem.h>

#include "histBook.h"
#include "tdrstyle.C"
#include "runTUnfold.C"

TH1 *calculateDiffXsec(std::string year, TH1 *h_in, TH1 *h_acceptance, bool gen = false);

void ttbbDiffXsec(std::string unfoldDir, std::string year, const char *genMode, const char *recoMode, 
    bool scanLcurve, bool fixtau){
  //gErrorIgnoreLevel = kFatal; // kWarning
  gROOT->ProcessLine("setTDRStyle();");
  
  std::string tmp_str;
  std::string tmp_name; double tmp_value;
  
  ifstream tau(Form("samples/tau%s.txt", year.c_str()));
  std::map<std::string, double> m_tau;
  while(getline(tau, tmp_str)){
    std::stringstream ss;
    ss.str(tmp_str);
    ss >> tmp_name;
    ss >> tmp_value;
    m_tau.insert(pair<std::string, double>(tmp_name, tmp_value));
  }
  tau.close();

  double fixedtau_dR = m_tau["fixedtau_dR"];
  double taumin_dR = m_tau["taumin_dR"];
  double taumax_dR = m_tau["taumax_dR"];

  double fixedtau_M = m_tau["fixedtau_M"];
  double taumin_M = m_tau["taumin_M"];
  double taumax_M = m_tau["taumax_M"];

  ifstream unfold(Form("samples/unfold%s.txt", year.c_str()));
  std::vector<std::string> group;
  while(getline(unfold, tmp_str)){
    size_t pos;
    if( (pos = tmp_str.find("group",0)) == std::string::npos ) continue;
    std::stringstream ss;
    ss.str(tmp_str);
    while(ss >> tmp_name){
      if(tmp_name == "group") continue;
      group.push_back(tmp_name);
    }
  }
  unfold.close();

  std::cout << "Load Files..." << std::endl;
  
  TFile *f_out    = TFile::Open(Form("%s/hist_output.root", unfoldDir.c_str()),"recreate");
  TFile *f_input  = TFile::Open(Form("%s/hist_input.root", unfoldDir.c_str()));
  TFile *f_matrix = TFile::Open(Form("%s/hist_matrix.root", unfoldDir.c_str()));
  TFile *f_accept = TFile::Open(Form("%s/hist_accept.root", unfoldDir.c_str()));

  std::cout << "Unfolding directory: " << unfoldDir << std::endl;
  std::cout << "Input file: " << f_input << " " << f_input->GetName() << std::endl;
  std::cout << "Acceptance file: " << f_accept << " " << f_accept->GetName() << std::endl;
  std::cout << "Matrix file: " << f_matrix << " " << f_matrix->GetName() << std::endl;
  std::cout << "Load histograms..." << std::endl;

  std::vector<std::string> syst_list = syst_basic;
  syst_list.insert(syst_list.end(), syst_jet.begin(), syst_jet.end());
  if( year == "16" || year == "2016" )
    syst_list.insert(syst_list.end(), syst_lep16.begin(), syst_lep16.end());
  else
    syst_list.insert(syst_list.end(), syst_lep1718.begin(), syst_lep1718.end());
  syst_list.insert(syst_list.end(), syst_ttbar.begin(), syst_ttbar.end());

  f_out->cd();
  std::vector<std::string> variables = {"DeltaR", "InvMass"};
  for( auto vari : variables ){
    std::vector<TH1 *> v_unfold_out;
    // Closure Test
    // Calculate Matrix Systematic Uncertainties
    TH2 *h_resp_pref = (TH2 *)f_matrix->Get(Form("h_%s_ResponseMatrix%s_Ch2_S3_prefit", genMode, vari.c_str()));
    TH1 *h_reco_clos = (TH1 *)f_matrix->Get(Form("h_%s_RecoAddbJet%s_Ch2_S3_ttbb_closure", recoMode, vari.c_str()));
    TH1 *h_gen_clos  = (TH1 *)f_matrix->Get(Form("h_%s_GenAddbJet%s_Ch2_S3", genMode, vari.c_str()));

    //  std::vector<TH1 *> runTUnfold(
    //    std::string outdir_, TH1 *h_in_, TH2 *h_resp_,
    //    std::map<const char *, TH1 *> m_bkgs_, std::map<const char *, double> m_scale_,
    //    std::map<const char *, TH2 *> m_sys_,
    //    bool scanLcurve_ = false, double tauMin_ = 0., double tauMax_ = 0.,
    //    bool fixTau_ = false, double fixedTau_ = 0.)
    v_unfold_out = runTUnfold(
      unfoldDir.c_str(), h_reco_clos, h_resp_pref,
      std::map<const char *, TH1 *>(), std::map<const char *, double>(), std::map<const char *, TH2 *>(), 
      scanLcurve, taumin_dR, taumax_dR, fixtau, fixedtau_dR);
    for ( auto out : v_unfold_out ){
      if( out != NULL ) out->Write();
    }
    h_gen_clos->Write();
    
    // Unfold data
    std::cout << "Unfold data..." << std::endl;
    TH2 *h_resp_post = (TH2 *)f_matrix->Get(Form("h_%s_ResponseMatrix%s_Ch2_S3_postfit", genMode, vari.c_str()));
    TH1 *h_data = (TH1 *)f_input->Get(Form("h_%s_RecoAddbJet%s_Ch2_S3_data_obs", recoMode, vari.c_str()));
    std::map<const char *, TH1 *> m_bkg, m_bkgup, m_bkgdown;
    std::map<const char *, double> m_scale;

    for(auto bkg : group){
      size_t pos;
      if( (pos = bkg.find("data",0)) != std::string::npos ) continue;
      if( (pos = bkg.find("ttbb",0)) != std::string::npos ) continue;
      m_scale.insert(pair<const char *, double>(bkg.c_str(), 1));
      auto tmp = (TH1 *)f_input->Get(Form("h_%s_RecoAddbJet%s_Ch2_S3_%s", recoMode, vari.c_str(), bkg.c_str()));
      auto tmpup = (TH1 *)f_input->Get(Form("h_%s_RecoAddbJet%s_Ch2_S3_%s__postfitup", recoMode, vari.c_str(), bkg.c_str()));
      auto tmpdown = (TH1 *)f_input->Get(Form("h_%s_RecoAddbJet%s_Ch2_S3_%s__postfitdown", recoMode, vari.c_str(), bkg.c_str()));
      m_bkg.insert(pair<const char *, TH1 *>(bkg.c_str(), tmp));
      m_bkgup.insert(pair<const char *, TH1 *>(bkg.c_str(), tmpup));
      m_bkgdown.insert(pair<const char *, TH1 *>(bkg.c_str(), tmpdown));
    }

    std::map<const char *, TH2 *> m_sysInput;
    for( std::string syst : syst_list ){
      TH2 *tmp = (TH2 *)f_matrix->Get(Form("h_%s_ResponseMatrix%s_Ch2_S3_postfit%s", genMode, vari.c_str(), syst.c_str()));
      m_sysInput.insert(pair<const char *, TH2 *>(syst.c_str(), tmp));
    }
  
    v_unfold_out = runTUnfold(
      unfoldDir.c_str(), h_data, h_resp_post,
      m_bkg, m_scale, m_sysInput,
      scanLcurve, taumin_dR, taumax_dR, fixtau, fixedtau_dR);
    for ( auto out : v_unfold_out ){
      if( out != NULL ) out->Write();
    }
    auto v_up = runTUnfold(
      unfoldDir.c_str(), h_data, h_resp_post,
      m_bkgup, m_scale, std::map<const char*, TH2 *>(),
      scanLcurve, taumin_dR, taumax_dR, fixtau, fixedtau_dR, "__postup");
    auto v_down = runTUnfold(
      unfoldDir.c_str(), h_data, h_resp_post,
      m_bkgdown, m_scale, std::map<const char*, TH2 *>(),
      scanLcurve, taumin_dR, taumax_dR, fixtau, fixedtau_dR, "__postdown");
    v_up[0]->SetName(Form("Background_%s", v_up[0]->GetName())); v_up[0]->Write();
    v_down[0]->SetName(Form("Background_%s", v_down[0]->GetName())); v_down[0]->Write();

    // Calculate differential cross section
    std::cout << "Calculate Differential cross section" << std::endl;
    TH1 *h_gen_nosel = (TH1 *)f_matrix->Get(Form("h_%s_GenAddbJet%s_Ch2_nosel", genMode, vari.c_str()));
    TH1 *h_accept = (TH1 *)f_accept->Get(Form("h_BinAcceptance%s_Ch2", vari.c_str()));

    auto h_diffXsec_MC = calculateDiffXsec(year, h_gen_nosel, NULL, true);
    auto h_diffXsec = calculateDiffXsec(year, v_unfold_out[0], h_accept);

    h_diffXsec_MC->Write();
    h_diffXsec->Write();
    h_gen_nosel->Write();

    for( auto syst : syst_list ){
      if(syst == "") continue;
      TH1 *h_sys = (TH1 *)f_accept->Get(Form("h_BinAcceptance%s_Ch2%s", vari.c_str(), syst.c_str()));
      TH1 *h_diffSys = calculateDiffXsec(year, v_unfold_out[0], h_sys);
      h_diffSys->SetName(Form("Acceptance_%s%s", h_data->GetName(), syst.c_str()));
      h_diffSys->Write();
    }

  }
  std::cout << "Finish unfolding" << std::endl;
  f_out->Close();
}

TH1 *calculateDiffXsec(std::string year, TH1 *h_in, TH1 *h_acceptance, bool gen){
  TH1 *h_out = (TH1 *)h_in->Clone(); 
  double incXsec = 0.0; double incXsec_err = 0.0;
  
  std::cout << "--------------------------------------------------------"<< std::endl;
  std::cout << h_in->GetName() << endl;
  std::string name = h_in->GetName();
  ssize_t pos;
  
  for(int ibin=1; ibin <= h_in->GetNbinsX(); ++ibin){
    double bin_width, diffXsec, diffXsec_err;
    // diffXsec = (1/bin width)*(nevt/accp*lumi)
    bin_width = h_in->GetXaxis()->GetBinWidth(ibin);
    if(gen){
      diffXsec     = h_in->GetBinContent(ibin)/(bin_width*m_lumi[year]*BRATIO_);
      diffXsec_err = h_in->GetBinError(ibin)/(bin_width*m_lumi[year]*BRATIO_); 
    }
    else{
      diffXsec     = h_in->GetBinContent(ibin)
                   / (h_acceptance->GetBinContent(ibin)*bin_width*m_lumi[year]*BRATIO_);
      diffXsec_err = h_in->GetBinError(ibin) 
                   / (h_acceptance->GetBinContent(ibin)*bin_width*m_lumi[year]*BRATIO_);
      if(h_acceptance->GetBinContent(ibin) == 0.0){
        diffXsec = 0.0;
        diffXsec_err = 0.0;
      }
    }

    h_out->SetBinContent(ibin, diffXsec);
    h_out->SetBinError(ibin, diffXsec_err);

    incXsec += diffXsec*bin_width;
    incXsec_err += pow(diffXsec_err*bin_width,2);
    
    std::cout << ibin << "th diffXsec: " << diffXsec << " || err: " << diffXsec_err << " || bin width: " << bin_width << std::endl;
  }
  
  std::cout << "inclusive Xsection : " << incXsec << " || error : " << sqrt(incXsec_err) << std::endl; 
  std::cout << "--------------------------------------------------------"<< std::endl;

  std::string tmp_name = h_out->GetName();
  boost::replace_all(tmp_name, "_Unfolded_", "_");
 
  h_out->SetName(Form("DiffXsec_%s",tmp_name.c_str()));
  return h_out;
}
