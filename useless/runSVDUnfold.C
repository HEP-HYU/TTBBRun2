R__LOAD_LIBRARY(libRooUnfold)

#include <iostream>

#include <TSystem.h>

//Output vector
//[0]: SVDUnfold output
//[1]: Error matrix propagated before unfolding
//[2]: Total error matrix

std::vector<TH1 *> runSVDUnfold(TH1 *h_in_, TH2 *h_resp_,
    std::map<const char *, TH1 *> m_bkg_, std::map<const char *, double> m_scale_,
    std::map<const char *, TH2 *> m_sys_,
    int reg = -1, bool scanReg = false)
{
  gSystem->Load("/home/seohyun/tools/RooUnfold/build/libRooUnfold.so");
   
  auto h_in = h_in_;
  auto h_resp = h_resp_;
  auto h_reco = h_resp->ProjectionX();
  auto h_gen = h_resp->ProjectionY();

  if(!m_bkg_.empty()){
    for(auto m_itr=m_bkg_.begin(); m_itr != m_bkg_.end(); ++m_itr){
      auto h_tmp = m_itr->second;
      h_tmp->Scale(m_scale_[m_itr->first]);
      h_in->Add(h_tmp, -1);
    }
  }

  RooUnfold::ErrorTreatment err = RooUnfold::kCovariance;
  RooUnfoldResponse *roo_resp;
  RooUnfold *roo_unfold;

  roo_resp = new RooUnfoldResponse(h_reco, h_gen, h_resp);
  
  if(reg == -1) roo_unfold = new RooUnfoldSvd(roo_resp, h_in);
  else  roo_unfold = new RooUnfoldSvd(roo_resp, h_in, reg);
  auto h_out = (TH1 *)roo_unfold->Hreco(err);
  h_out->SetName(Form("Unfolded_%s", h_in->GetName()));
  //cout << "Regularization Parameter : " << roo_unfold->GetRegParm() << endl;
  
  //roo_unfold = new RooUnfoldInvert(roo_resp, h_in);
  //auto h_out = (TH1 *)roo_unfold->Hreco(err);

  TH2D *h2_ematrix = new TH2D(roo_unfold->Ereco(err));
  h2_ematrix->SetName(Form("%s_EmatrixTot", h_in->GetName()));
  //h2_ematrix->SetName(Form("Ematrix_%s", h_in->GetName()));
  vector<TH1 *> v_output;
  v_output.push_back(h_out);
  v_output.push_back(h2_ematrix);
  
  if(!m_sys_.empty()){
    vector<TH2 *> v_sys_err;
    for(auto m_itr=m_sys_.begin(); m_itr != m_sys_.end(); ++m_itr){
      RooUnfoldResponse *resp_sys = new RooUnfoldResponse(
        (m_itr->second)->ProjectionX(), (m_itr->second)->ProjectionY(), m_itr->second);
      RooUnfold *unfold_sys = new RooUnfoldSvd(resp_sys, h_in, reg);
      auto h_sysout = (TH1 *)unfold_sys->Hreco(err);
      auto h_deltasys = (TH1 *)h_out->Clone();
      h_deltasys->Add(h_sysout, -1);
      h_deltasys->SetName(Form("%s_DeltaSysSource%s", h_in->GetName(), m_itr->first));
      v_output.push_back(h_deltasys);
      //TH2D *h2_err_sys = new TH2D(unfold_sys->Ereco(err));
      //h2_err_sys->SetName(Form("EmatrixSys_%s%s", (*v_itr)->GetName(), h_in->GetName()));
      //v_sys_err.push_back(h2_err_sys);
    }
    //TH2 *h2_err_total = (TH2 *)v_output[1]->Clone();
    //for(auto v_itr=v_sys_err.begin(); v_itr != v_sys_err.end(); ++v_itr){
    //  TH2 *h2_tmp = (TH2 *)(*v_itr)->Clone();
    //  h2_err_total->Add(h2_tmp);
    //}
    //v_output.push_back(h2_err_total);
  }
  return v_output;
}

void findBestk(const char *data_name_, vector<TH1 *>h_in_, TH1 *h_truth_){
  gROOT->ProcessLine("setTDRStyle();"); 
  
  vector<int> markerStyle = { kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown,
  kFullStar, kFullDiamond, kFullCross, kFullCrossX, kFullFourTrianglesPlus, kOpenStar};
  vector<int> colorStyle = { kGreen, kYellow, kOrange, kRed, kPink, kViolet, kBlue, kTeal,
    kSpring+4, kPink-5};

  auto h_in = h_in_;
  auto h_truth = h_truth_;
  auto data_name = data_name_;

  TPaveText *label_sim = tdrCMSSimlabel();
  TCanvas *c = new TCanvas("","",800,800);
  TLegend *leg = new TLegend(0.75,0.7,0.88,0.88);

  vector<TGraph *> v_grp;
  vector<TGraph *> v_grp2;
  for(auto v_itr = h_in.begin(); v_itr != h_in.end(); ++v_itr){
    TH1 *h_tmp = *v_itr;
    TGraph *grp = new TGraph();
    TGraph *grp2 = new TGraph();

    for(int j=1; j<=h_tmp->GetNbinsX(); ++j){
      const double y = (h_tmp->GetBinError(j)/h_tmp->GetBinContent(j))*100;
      grp->SetPoint(j-1, h_tmp->GetBinCenter(j), y);

      const double yy = (h_truth->GetBinContent(j)-h_tmp->GetBinContent(j))/h_truth->GetBinContent(j);
      grp2->SetPoint(j-1, h_tmp->GetBinCenter(j), yy);
    }
    v_grp.push_back(grp);
    v_grp2.push_back(grp2);
  }

  TGraph *grp_truth = new TGraph();
  for(int i=1; i<=h_truth->GetNbinsX(); ++i){
    const double y = (sqrt(h_truth->GetBinContent(i))/h_truth->GetBinContent(i))*100;
    grp_truth->SetPoint(i-1, h_truth->GetBinCenter(i), y);
  }
  grp_truth->SetLineStyle(8);
  grp_truth->SetLineColor(kSpring+4);
  grp_truth->SetMarkerColor(kSpring+4);
  grp_truth->SetMarkerStyle(kOpenStar);

  c->cd();
  TH1 *h_tmp = (TH1 *)(h_in.at(0))->Clone();
  h_tmp->SetMaximum(100);
  h_tmp->SetMinimum(0);
  h_tmp->GetYaxis()->SetTitleOffset(1.6);
  h_tmp->GetYaxis()->SetTitleSize(0.04);
  h_tmp->GetYaxis()->SetTitle("Statistical Uncertainty(%)");
  h_tmp->GetXaxis()->SetTitleOffset(1.2);
  h_tmp->Draw("axis");
  for(int i=0; i<v_grp.size(); ++i){
    v_grp.at(i)->SetMarkerSize(1.5);
    v_grp.at(i)->SetMarkerColor(colorStyle.at(i));
    v_grp.at(i)->SetMarkerStyle(markerStyle.at(i));
    leg->AddEntry(v_grp.at(i), Form("k = %d",i+2), "p");
    
    v_grp.at(i)->Draw("C p same");
  }
  leg->AddEntry(grp_truth, "MC input", "lp");
  grp_truth->Draw("C p same");
  
  leg->Draw("same");
  c->Print(Form("../output/unfold/%s_SVD_statErr_%s.pdf", data_name, h_tmp->GetName()), "pdf"); 
  leg->Clear();
  c->Clear();

  c->cd();
  TH1 *h_tmp2 = (TH1 *)(h_in.at(0))->Clone();
  h_tmp2->SetMaximum(0.3);
  h_tmp2->SetMinimum(-0.5);
  h_tmp2->GetYaxis()->SetTitleOffset(1.6);
  h_tmp2->GetYaxis()->SetTitleSize(0.04);
  h_tmp2->GetYaxis()->SetTitle("(N_{truth}-N_{unfolded})/N_{truth}");
  h_tmp2->GetXaxis()->SetTitleOffset(1.2);
  h_tmp2->Draw("axis");
  for(int i=0; i<v_grp2.size(); ++i){
    v_grp2.at(i)->SetMarkerSize(1.5);
    v_grp2.at(i)->SetMarkerColor(colorStyle.at(i));
    v_grp2.at(i)->SetMarkerStyle(markerStyle.at(i));
    leg->AddEntry(v_grp2.at(i), Form("k = %d", i+2), "p");

    v_grp2.at(i)->Draw("C p same");
  }
  leg->Draw("same");
  c->Print(Form("../output/unfold/%s_SVD_gap_%s.pdf", data_name, h_tmp->GetName()), "pdf");
  leg->~TLegend();
  c->~TCanvas();
}
