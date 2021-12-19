#pragma once

#include <iostream>
#include <fstream>

#include <boost/algorithm/string/replace.hpp>

#include <TFile.h>
#include <TGraphErrors.h>
#include <TCanvas.h>
#include <TMath.h>

#include "histBook.h"
#include "tdrstyle.C"

//Unfolding options
const char *genMode = "mindR";
const bool scanLcurve = true;

std::map<std::string, int> m_lumi = {{"16",35922}, {"17",41529}, {"18",59693}};
double BRATIO_ = 0.436572; // 2*3*0.1086*0.67

TH1 *calculateDiffXsec(std::string year, TH1 *h_in, TH1 *h_acceptance, bool gen = false){
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
  tmp_name.replace(tmp_name, "Unfold_", "");
 
  h_out->SetName(Form("DiffXsec_%s",tmp_name.c_str()));
  return h_out;
}
