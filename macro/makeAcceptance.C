#include <iostream>
#include <fstream>
#include <vector>
#include <map>

#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TCanvas.h"

#include "histBook.h"

HistoBook *MakeHist(std::string outputDir, const char *genMode, TFile *f_in, TFile *f_gen, std::string syst);

void makeAcceptance(std::string inputDir, std::string outputDir, std::string year, std::string ttbb, const char *genMode){

  std::cout << "Calculate Acceptance for each bin..." << std::endl;
  std::cout << "ttbb file: " << ttbb << std::endl;

  TFile *f_in = TFile::Open(Form("%s/hist_%s.root", inputDir.c_str(), ttbb.c_str()));
  TFile *f_gen = TFile::Open(Form("%s/hist_gen.root", inputDir.c_str()));
  TFile *f_out = TFile::Open(Form("%s/hist_accept.root", outputDir.c_str()),"recreate");

  std::vector<std::string> v_syst_list = syst_basic;
  v_syst_list.insert(v_syst_list.end(), syst_jet.begin(), syst_jet.end());
  if( year == "16" || year == "2016" )
    v_syst_list.insert(v_syst_list.end(), syst_lep16.begin(), syst_lep16.end());
  else
    v_syst_list.insert(v_syst_list.end(), syst_lep1718.begin(), syst_lep1718.end());
  v_syst_list.insert(v_syst_list.end(), syst_ttbar.begin(), syst_ttbar.end());
  
  auto h_tmp = MakeHist(outputDir, genMode, f_in, f_gen, "");
  
  f_out->cd();
  for(int ich=0; ich<nChannel; ++ich){
    h_tmp->h_stability_deltaR[ich]->Write();
    h_tmp->h_stability_invMass[ich]->Write();
    h_tmp->h_purity_deltaR[ich]->Write();
    h_tmp->h_purity_invMass[ich]->Write();
    h_tmp->h_acceptance_deltaR[ich]->Write();
    h_tmp->h_acceptance_invMass[ich]->Write();
  }
  h_tmp->~HistoBook();

  for( auto v_itr : v_syst_list ){
    std::cout << "systematics:" << v_itr.c_str() << std::endl;
    h_tmp = MakeHist(outputDir, genMode, f_in, f_gen, v_itr.c_str());
    
    for(int ich=0; ich<nChannel; ++ich){
      h_tmp->h_stability_deltaR[ich]->Write();
      h_tmp->h_stability_invMass[ich]->Write();
      h_tmp->h_purity_deltaR[ich]->Write();
      h_tmp->h_purity_invMass[ich]->Write();
      h_tmp->h_acceptance_deltaR[ich]->Write();
      h_tmp->h_acceptance_invMass[ich]->Write();
    }
    h_tmp->~HistoBook();
  }

  //f_out->Write();
  f_out->Close();
}

HistoBook *MakeHist(std::string outputDir, const char *genMode, TFile *f_in, TFile *f_gen, std::string syst){
  std::ofstream fout(Form("%s/BinCriteria%s.txt", outputDir.c_str(), syst.c_str()));
  fout << "Systematic sample: " << syst << std::endl;
  //NORMALIZATION
  //double xsec = 0.0;
  //if( syst.find("sw",0,2) != std::string::npos ) xsec = 831.76;
  //else if( syst.find("tune",0,4) != std::string::npos ) xsec = 831.76;
  //else xsec = XSEC_[TTBB_];
  //TH1 *EventInfo = (TH1 *)f_in->Get("EventInfo");
  //const double scale = SF_ttbb*LUMINOSITY_*xsec/EventInfo->GetBinContent(2);

  //HISTOGRAMS
  HistoBook *h_stb = new HistoBook(3,syst.c_str());

  TH2D *h_matrix_deltaR[nChannel];
  TH2D *h_matrix_invMass[nChannel];

  TH1D *h_gen_deltaR[nChannel];
  TH1D *h_gen_invMass[nChannel];

  TH1D *h_reco_deltaR[nChannel];
  TH1D *h_reco_invMass[nChannel];

  TH1D *h_gen_deltaR_nosel[nChannel];
  TH1D *h_gen_invMass_nosel[nChannel];

  for(int ich=0; ich < nChannel; ++ich){    
    h_gen_deltaR_nosel[ich]    = (TH1D *)f_gen->Get(Form("h_%s_%s_Ch%d_nosel", genMode, GEN_ADD_DR_,   ich));
    h_gen_invMass_nosel[ich]   = (TH1D *)f_gen->Get(Form("h_%s_%s_Ch%d_nosel", genMode, GEN_ADD_M_,    ich));
    
    h_matrix_deltaR[ich]   = (TH2D *)f_in->Get(Form("h_%s_%s_Ch%d_S3%s", genMode, MATRIX_DR_,   ich, syst.c_str()));
    h_matrix_invMass[ich]  = (TH2D *)f_in->Get(Form("h_%s_%s_Ch%d_S3%s", genMode, MATRIX_M_,    ich, syst.c_str()));

    h_gen_deltaR[ich]   = (TH1D *)f_in->Get(Form("h_%s_%s_Ch%d_S3%s", genMode, GEN_ADD_DR_,   ich, syst.c_str()));
    h_gen_invMass[ich]  = (TH1D *)f_in->Get(Form("h_%s_%s_Ch%d_S3%s", genMode, GEN_ADD_M_,    ich, syst.c_str()));

    h_reco_deltaR[ich]   = (TH1D *)f_in->Get(Form("h_%s_%s_Ch%d_S3%s", genMode, RECO_ADD_DR_,   ich, syst.c_str())); 
    h_reco_invMass[ich]  = (TH1D *)f_in->Get(Form("h_%s_%s_Ch%d_S3%s", genMode, RECO_ADD_M_,   ich, syst.c_str())); 
  }

  for(int ich=0; ich<nChannel; ++ich){
    fout << "=======================================" << std::endl;
    fout << "Channel: " << ich << std::endl;
    
    fout << "----------------------------------------" << std::endl;
    fout << "----------------------------------------" << std::endl;
    fout << "**************** Purity ****************" << std::endl;
    fout << "Variable: delta R" << endl;

    for(int ibin=1; ibin < nbins_reco_addbjets_dR+1; ++ibin){
      fout << "------" << ibin << "th Bin ------" << std::endl;
      double purity_dR = 0.0;
      if(h_reco_deltaR[ich]->GetBinContent(ibin) != 0.0){
        auto xlow = h_matrix_deltaR[ich]->GetXaxis()->GetBinLowEdge(ibin);
        auto ybin = h_matrix_deltaR[ich]->GetYaxis()->FindBin(xlow);
        purity_dR = h_matrix_deltaR[ich]->GetBinContent(ibin,ybin)/h_reco_deltaR[ich]->GetBinContent(ibin);
         
        fout << "x low : " << xlow << std::endl;
        fout << "y bin number : " << ybin << std::endl;
        fout << "xBinContent : " << h_reco_deltaR[ich]->GetBinContent(ibin) << std::endl;
        fout << "yBinContent : " << h_matrix_deltaR[ich]->GetBinContent(ibin,ybin) << std::endl;
        fout << "value : " << purity_dR << std::endl;
      }
      h_stb->h_purity_deltaR[ich]->SetBinContent(ibin, purity_dR);
      fout << "----------------------------------------" << std::endl;
    }
    
    fout << "----------------------------------------" << std::endl;
    fout << "Variable: inv Mass" << endl;

    for(int ibin=1; ibin < nbins_reco_addbjets_M+1; ++ibin){
      fout << "------" << ibin << "th Bin ------" << std::endl;
      double purity_M = 0.0;
      if(h_reco_invMass[ich]->GetBinContent(ibin) != 0.0){
        auto xlow = h_matrix_invMass[ich]->GetXaxis()->GetBinLowEdge(ibin);
        auto ybin = h_matrix_invMass[ich]->GetYaxis()->FindBin(xlow);
        purity_M = h_matrix_invMass[ich]->GetBinContent(ibin,ybin)/h_reco_invMass[ich]->GetBinContent(ibin);
         
        fout << "x low : " << xlow << std::endl;
        fout << "y bin number : " << ybin << std::endl;
        fout << "xBinContent : " << h_reco_invMass[ich]->GetBinContent(ibin) << std::endl;
        fout << "yBinContent : " << h_matrix_invMass[ich]->GetBinContent(ibin,ybin) << std::endl;
        fout << "value : " << purity_M << std::endl;
      }
      h_stb->h_purity_invMass[ich]->SetBinContent(ibin, purity_M);
      fout << "----------------------------------------" << std::endl;
    }

    fout << "----------------------------------------" << std::endl;
    fout << "************** Stability  **************" << std::endl;
    fout << "Variable: delta R" << endl;
    for(int ibin=1; ibin<nbins_gen_addbjets_dR+1; ++ibin){
      fout << "------" << ibin << "th Bin ------" << std::endl;
      double stability_dR = 0.0;
      if(h_gen_deltaR[ich]->GetBinContent(ibin) != 0.0){
        auto ylow = h_matrix_deltaR[ich]->GetYaxis()->GetBinLowEdge(ibin);
        auto ymax = h_matrix_deltaR[ich]->GetYaxis()->GetBinLowEdge(ibin+1);
        auto xlow = h_matrix_deltaR[ich]->GetXaxis()->FindBin(ylow);
        auto xmax = h_matrix_deltaR[ich]->GetXaxis()->FindBin(ymax);
        if(xlow == xmax && xmax == h_matrix_deltaR[ich]->GetNbinsX()) ++xmax;
        double xbincontent = 0.;
        for(int ixbin = xlow; ixbin < xmax; ++ixbin)
          xbincontent += h_matrix_deltaR[ich]->GetBinContent(ixbin,ibin);
        stability_dR = xbincontent/h_gen_deltaR[ich]->GetBinContent(ibin);
        fout << "y low : " << ylow << ", max : " << ymax << std::endl;
        fout << "x low : " << xlow << ", max : " << xmax << std::endl;
        fout << "xBinContent : " << xbincontent << std::endl;
        fout << "yBinContent : " << h_gen_deltaR[ich]->GetBinContent(ibin) << std::endl;
        fout << "value :" << stability_dR << std::endl;
      }
      h_stb->h_stability_deltaR[ich]->SetBinContent(ibin, stability_dR);
      fout << "----------------------------------------" << std::endl;
    }

    fout << "----------------------------------------" << std::endl;
    fout << "Variable: inv Mass" << endl;
    for(int ibin=1; ibin<nbins_gen_addbjets_M+1; ++ibin){
      fout << "------" << ibin << "th Bin ------" << std::endl;
      double stability_M = 0.0;
      if(h_gen_invMass[ich]->GetBinContent(ibin) != 0.0){
        auto ylow = h_matrix_invMass[ich]->GetYaxis()->GetBinLowEdge(ibin);
        auto ymax = h_matrix_invMass[ich]->GetYaxis()->GetBinLowEdge(ibin+1);
        auto xlow = h_matrix_invMass[ich]->GetXaxis()->FindBin(ylow);
        auto xmax = h_matrix_invMass[ich]->GetXaxis()->FindBin(ymax);
        if(xlow == xmax && xmax == h_matrix_invMass[ich]->GetNbinsX()) ++xmax;
        double xbincontent = 0.;
        for(int ixbin = xlow; ixbin < xmax; ++ixbin)
          xbincontent += h_matrix_invMass[ich]->GetBinContent(ixbin,ibin);
        stability_M = xbincontent/h_gen_invMass[ich]->GetBinContent(ibin);
        fout << "y low : " << ylow << ", max : " << ymax << std::endl;
        fout << "x low : " << xlow << ", max : " << xmax << std::endl;
        fout << "xBinContent : " << xbincontent << std::endl;
        fout << "yBinContent : " << h_gen_invMass[ich]->GetBinContent(ibin) << std::endl;
        fout << "value :" << stability_M << std::endl;
      }
      h_stb->h_stability_invMass[ich]->SetBinContent(ibin, stability_M);
      fout << "----------------------------------------" << std::endl;
    }

    fout << "----------------------------------------" << std::endl;
    fout << "************** Acceptance  *************" << std::endl;
    fout << "Variable : delta R" << std::endl;
    for(int ibin=1; ibin<nbins_gen_addbjets_dR+1;++ibin){
      fout << "------" << ibin << "th Bin ------" << std::endl;
      double acceptance_dR = 0.0;
      double dR_err = 0.0;
      if( h_gen_deltaR_nosel[0]->GetBinContent(ibin) > 0.0 && h_gen_deltaR_nosel[1]->GetBinContent(ibin) > 0.0 ){
        acceptance_dR = h_gen_deltaR[ich]->GetBinContent(ibin)
          / (h_gen_deltaR_nosel[0]->GetBinContent(ibin) + h_gen_deltaR_nosel[1]->GetBinContent(ibin));
        if( h_gen_deltaR[ich]->GetBinContent(ibin) > 0.0 ){
          dR_err = abs(acceptance_dR)
             * sqrt(pow(h_gen_deltaR[ich]->GetBinError(ibin)/h_gen_deltaR[ich]->GetBinContent(ibin),2) 
             + pow(h_gen_deltaR_nosel[0]->GetBinError(ibin)/h_gen_deltaR_nosel[0]->GetBinContent(ibin),2)
             + pow(h_gen_deltaR_nosel[1]->GetBinError(ibin)/h_gen_deltaR_nosel[1]->GetBinContent(ibin),2));
        }
      }
      h_stb->h_acceptance_deltaR[ich]->SetBinContent(ibin, acceptance_dR);
      h_stb->h_acceptance_deltaR[ich]->SetBinError(ibin, dR_err);
      fout << "value :" << acceptance_dR << std::endl;
      fout << "err :" << dR_err << std::endl;
      fout << "----------------------------------------" << std::endl;
    }
    
    fout << "----------------------------------------" << std::endl;
    fout << "Variable : inv Mass" << std::endl;
    for(int ibin=1; ibin<nbins_gen_addbjets_M+1;++ibin){
      fout << "------" << ibin << "th Bin ------" << std::endl;
      double acceptance_M = 0.0;
      double M_err = 0.0;
      if( h_gen_invMass_nosel[0]->GetBinContent(ibin) > 0.0 && h_gen_invMass_nosel[1]->GetBinContent(ibin) > 0.0 ){
	      acceptance_M = h_gen_invMass[ich]->GetBinContent(ibin)
	        / (h_gen_invMass_nosel[0]->GetBinContent(ibin) + h_gen_invMass_nosel[1]->GetBinContent(ibin));
	      if( h_gen_invMass[ich]->GetBinContent(ibin) > 0.0 ){
	        M_err = abs(acceptance_M)
	          * sqrt(pow(h_gen_invMass[ich]->GetBinError(ibin)/h_gen_invMass[ich]->GetBinContent(ibin),2) 
	          + pow(h_gen_invMass_nosel[0]->GetBinError(ibin)/h_gen_invMass_nosel[0]->GetBinContent(ibin),2)
		        + pow(h_gen_invMass_nosel[1]->GetBinError(ibin)/h_gen_invMass_nosel[1]->GetBinContent(ibin),2));
        }
      }
      h_stb->h_acceptance_invMass[ich]->SetBinContent(ibin, acceptance_M);
      h_stb->h_acceptance_invMass[ich]->SetBinError(ibin, M_err);
      fout << "value :" << acceptance_M << std::endl;
      fout << "err :" << M_err << std::endl;
      fout << "----------------------------------------" << std::endl;
    }
  }//Channel

  return h_stb;
}
