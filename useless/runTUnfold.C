#include <iostream>

#include "TGraph.h"
#include "TSpline.h"
#include "TUnfold.h"
#include "TUnfoldDensity.h"

void drawRegHist(std::string outdir_, const char *h_name_,
    TSpline *spl_logTauscanX_, TGraph *grp_BestLcurveX_, TGraph *grp_BestTau_, TGraph *grp_Lcurve_,
    bool scanLcurve_=true, TSpline *spl_Tauscan_=NULL){

  std::cout << "Draw Regularization Histograms" << std::endl;

  auto grp_Lcurve = grp_Lcurve_;
  auto spl_logTauscanX = spl_logTauscanX_;
  auto grp_BestTau = grp_BestTau_;
  auto grp_BestLcurveX = grp_BestLcurveX_;
  auto spl_Tauscan = spl_Tauscan_;

  gROOT->ProcessLine("setTDRStyle();");

  TCanvas *c = new TCanvas("","",800,800);
  c->cd();

  spl_logTauscanX->SetTitle(/*log(chi^2)log(tau)*/"; log_{10}(#tau); log_{10}(#chi^{2})");
  spl_logTauscanX->Draw();
  //spl_logTauscanX->GetXaxis()->SetLabelSize(0.1);
  //spl_logTauscanX->GetYaxis()->SetLabelSize(0.1);
  grp_BestLcurveX->SetMarkerSize(2.3);
  grp_BestLcurveX->SetMarkerColor(kBlue);
  grp_BestLcurveX->SetMarkerStyle(kFullStar);
  grp_BestLcurveX->Draw("p");
  //grp_BestLcurveX->SetEditable(false);
  c->Print(Form("%s/TUnfold_regular_logTaulogChi2_%s.pdf", outdir_.c_str(), h_name_),"pdf");
  c->Clear();
  
  c->cd();
  if( scanLcurve_ ){
    grp_Lcurve->SetTitle("; L^{curve}_{x}; L^{curve}_{y}");
    //grp_Lcurve->GetXaxis()->SetTitle("log(#tau)");
    grp_Lcurve->GetXaxis()->SetLabelSize(0.025);
    grp_Lcurve->GetYaxis()->SetLabelSize(0.03);
    grp_BestTau->SetMarkerSize(2.3);
    grp_BestTau->SetMarkerColor(kBlue);
    grp_BestTau->SetMarkerStyle(kFullStar);
    grp_Lcurve->Draw();
    grp_BestTau->Draw("p");
    //grp_BestTau->SetEditable(false);
    c->Print(Form("%s/TUnfold_regular_Lcurve_%s.pdf", outdir_.c_str(), h_name_), "pdf");
  }
  else{
    spl_Tauscan->SetTitle(/*Tau scan*/"; log_{10}(#tau); avg #rho");
    spl_Tauscan->SetMarkerSize(0.7);
    grp_BestTau->SetMarkerSize(2.3);
    grp_BestTau->SetMarkerColor(kBlue);
    grp_BestTau->SetMarkerStyle(kFullStar);
    spl_Tauscan->Draw("lp");
    grp_BestTau->Draw("p");
    //grp_BestTau->SetEditable(false);
    c->Print(Form("%s/TUnfold_regular_minRho_%s.pdf", outdir_.c_str(), h_name_), "pdf");
  } 
}

std::vector<TH1 *> runTUnfold(std::string outdir_, TH1 *h_in_, TH2 *h_resp_,
    std::map<const char *, TH1 *> m_bkgs_, std::map<const char *, double> m_scale_,
    std::map<const char *, TH2 *> m_sys_,
    bool scanLcurve_ = false, double tauMin_ = 0., double tauMax_ = 0.,
    bool fixTau_ = false, double fixedTau_ = 0., const char * specialName = ""){

  TH1 * h_in = (TH1 *)h_in_->Clone();
  TH2 * h_resp = (TH2 *)h_resp_->Clone();
  
  string regMethod;
  if( scanLcurve_ ) regMethod = "Scan L-Curve";
  else regMethod = "Find minimum global correlation coefficient";

  std::cout << "========================================" << std::endl;
  std::cout << "TUnfold version: " << TUnfold::GetTUnfoldVersion() << std::endl;
  std::cout << "----------------------------------------" << std::endl;
  std::cout << "Reg. Parameter optimization: " << regMethod << std::endl;
  
  auto regMode = TUnfold::kRegModeCurvature;
  TUnfoldDensity *unfold = new TUnfoldDensity(h_resp, TUnfold::kHistMapOutputVert,
    regMode, TUnfold::kEConstraintArea, TUnfoldDensity::kDensityModeBinWidth,
    0, 0, 0, "*[UOB]");//"*[UO]");

  unfold->SetInput(h_in);
  if( !m_bkgs_.empty() ){
    std::cout << "Number of bkgs: " << m_bkgs_.size() << std::endl;
    for( auto m_itr = m_bkgs_.begin(); m_itr != m_bkgs_.end(); ++m_itr ){
      unfold->SubtractBackground(m_itr->second, m_itr->first, m_scale_[m_itr->first]);
    }
  }
  if( !m_sys_.empty() ){
    std::cout << "Number of sys sources: " << m_sys_.size() << std::endl;
    for( auto m_itr = m_sys_.begin(); m_itr != m_sys_.end(); ++m_itr ){
      std::cout << "Source: " << m_itr->first << std::endl;
      unfold->AddSysError(m_itr->second, m_itr->first, TUnfold::kHistMapOutputVert, TUnfoldSys::kSysErrModeMatrix);
    }
  }

  std::cout << "----------------------------------------" << std::endl;
  std::cout << "Start Tau Scanning" << std::endl;
  
  double bestTau = fixedTau_;
  if( regMode == TUnfold::kRegModeNone ) bestTau = 0.0;
  else{
    if( !fixTau_ ){
      const int nScan = 50;
      int iBest = 0;
      double tauMax = tauMax_, tauMin = tauMin_;
      double bestRho, bestTauX, bestTauY;

      TSpline *spl_Tauscan, *spl_logTauscanX, *spl_logTauscanY;
      TGraph *grp_Lcurve;
      TGraph *grp_BestTau, *grp_BestRho;

      if( scanLcurve_ ){
        //ScanLcurve (Int_t nPoint, Double_t tauMin, Double_t tauMax, TGraph **lCurve, TSpline **logTauX=0, TSpline **logTauY=0, TSpline **logTauCurvature=0)
        iBest = unfold->ScanLcurve(nScan, tauMin, tauMax, &grp_Lcurve, &spl_logTauscanX, &spl_logTauscanY); 
        spl_logTauscanX->GetKnot(iBest, bestTau, bestTauX);
        spl_logTauscanY->GetKnot(iBest, bestTau, bestTauY);
        grp_BestTau = new TGraph(1, &bestTauX, &bestTauY);
      }
      else{
        //ScanTau (Int_t nPoint, Double_t tauMin, Double_t tauMax,
        //	TSpline **scanResult, Int_t mode=kEScanTauRhoAvg, const char *distribution=0, const char *projectionMode=0,
        //	TGraph **lCurvePlot=0, TSpline **logTauXPlot=0, TSpline **logTauYPlot=0)
        iBest = unfold->ScanTau(nScan, tauMin, tauMax,
            &spl_Tauscan, TUnfoldDensity::kEScanTauRhoAvg, 0, "*[UO]",
            &grp_Lcurve, &spl_logTauscanX, &spl_logTauscanY);
        spl_logTauscanX->GetKnot(iBest, bestTau, bestTauX);
        spl_logTauscanY->GetKnot(iBest, bestTau, bestTauY);
        spl_Tauscan->GetKnot(iBest, bestTau, bestRho);
        grp_BestTau = new TGraph(1, &bestTau, &bestRho);
      }
      //drawRegHist(const char *h_name_,
      //TSpline *spl_logTauscanX_, TGraph *grp_BestLcurveX_, TGraph *grp_BestTau_, TGraph *grp_Lcurve_,
      //bool scanLcurve_=false, TSpline *spl_Tauscan_=NULL
      TGraph *grp_BestLcurveX = new TGraph(1, &bestTau, &bestTauX);
      if( scanLcurve_ )
        drawRegHist(outdir_, h_in->GetName(), spl_logTauscanX, grp_BestLcurveX, grp_BestTau, grp_Lcurve);
      else
        drawRegHist(outdir_, h_in->GetName(), spl_logTauscanX, grp_BestLcurveX, grp_BestTau, grp_Lcurve, false, spl_Tauscan);
    }
  }
  if( fixTau_ ) std::cout << "Fixed Tau : " << bestTau << std::endl;
  else          std::cout << "Best log_{10}(#tau) : " << bestTau << std::endl;
  
  
  std::cout << "----------------------------------------" << std::endl;
  std::cout << "Save Unfolding output distribution" << std::endl;
  std::cout << "----------------------------------------" << std::endl;
  
  const double unfoldResult = unfold->DoUnfold(bestTau, h_in);
  auto h_output = unfold->GetOutput(Form("Unfolded_%s%s",h_in->GetName(), specialName),"",0,"*[UO]",true);
  auto h_input = unfold->GetInput(Form("Input_%s%s", h_in->GetName(), specialName),"",0,"*[UO]",true);
  //auto h2_emat = unfold->GetEmatrixInput(Form("EmatrixInput_%s",h_in->GetName()));
  auto h2_emat = unfold->GetEmatrixInput(Form("TempMatrix_%s%s",h_in->GetName(), specialName));
  //for( int ibin = 1; ibin <= h_output->GetNbinsX(); ibin++ ){
  //  auto error = sqrt(h2_emat->GetBinContent(ibin, ibin));
  //  h_output->SetBinError(ibin, error);
  //}
  //Output vector
  //[0]: TUnfold output
  //[1]: TUnfold input
  //[2]: Covariance matrix including all contributions
  //[3]: Covariance contribution from the input statistical uncertainties
  //[4]: Covariance contribution from uncorrelated (statistical) uncertainties of the response matrix
  //[5]: 1-sigma shift from tau
  //[6]: Covariance matrix from tau
  //[7]~[7+nsys*2]:
  //     1. Covariance matrix from the systematics of the input matrix
  //     2. Correlated systematic 1-sigma shift of the input matrix
  //[6+nsys*2+1]~[6+nsys*2+1+nbkg*3]
  //     1. Covraiance matrix from the uncorrelated background unceratinties
  //     2. 1-sigma shift corresponding to a background scale uncertainty
  vector<TH1 *> v_output;
  v_output.push_back(h_output); //[0]
  v_output.push_back(h_input); //[1]
  v_output.push_back(unfold->GetEmatrixTotal(Form("EmatrixTotal_%s%s",h_in->GetName(), specialName))); //[2]
  v_output.push_back(unfold->GetEmatrixInput(Form("EmatrixInput_%s%s",h_in->GetName(), specialName))); //[3]
  v_output.push_back(unfold->GetEmatrixSysUncorr(Form("EmatrixSysUncorr_%s%s", h_in->GetName(), specialName))); //[4]
  //v_output.push_back(unfold->GetBias(Form("%s_Bias", h_in->GetName())));
  v_output.push_back(unfold->GetDeltaSysTau(Form("DeltaSysTau_%s%s", h_in->GetName(), specialName))); //[4]
  TH2D *h2_emat_tau = (TH2D *)h2_emat->Clone();
  unfold->GetEmatrixSysTau(h2_emat_tau);
  h2_emat_tau->SetName(Form("EmatrixSysTau_%s%s", h_in->GetName(), specialName));
  v_output.push_back(h2_emat_tau);
  
  for(auto m_itr=m_sys_.begin(); m_itr != m_sys_.end(); ++m_itr){
    TH2D *h2_emat_source = (TH2D *)h2_emat->Clone();
    unfold->GetEmatrixSysSource(h2_emat_source, m_itr->first);
    h2_emat_source->SetName(Form("EmatrixSysSource_%s%s%s", h_in->GetName(), m_itr->first, specialName));
    v_output.push_back(h2_emat_source);
    v_output.push_back(unfold->GetDeltaSysSource(m_itr->first,
          Form("DeltaSysSource_%s%s%s", h_in->GetName(), m_itr->first, specialName)));
  }
  /*
  for(auto m_itr=m_bkgs_.begin(); m_itr != m_bkgs_.end(); ++m_itr){
    v_output.push_back(unfold->GetEmatrixSysBackgroundUncorr(m_itr->first,
          Form("%s_EmatrixSysBkgUncorr%s", h_in->GetName(), m_itr->first)));
    TH2 *h2_emat_bkgscale;
    unfold->GetEmatrixSysBackgroundScale(h2_emat_bkgscale, m_itr->first);
    h2_emat_bkgscale->SetTitle(Form("%s_EmatrixSysBkgScale%s", h_in->GetName(), m_itr->first));
    v_output.push_back(h2_emat_bkgscale);
    v_output.push_back(unfold->GetDeltaSysBackgroundScale(m_itr->first,
          Form("%s_DeltaBkgScale%s", h_in->GetName(),  m_itr->first)));
  }
  */
  std::cout << "Return TUnfold output vector, size: " << v_output.size() <<endl;
  std::cout << "========================================" << std::endl;
  return v_output;
}

