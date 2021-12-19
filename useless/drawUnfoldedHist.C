#include <unistd.h>

#include "ttbbDiffXsec.h"

TGraphErrors *buildGraphFromHist(TH1* h){
  std::cout << "hist: " << h->GetName() << std::endl;
  TGraphErrors *grp = new TGraphErrors();

  for( int i=1; i<=h->GetNbinsX(); ++i ) {
    const double w = h->GetXaxis()->GetBinWidth(i);
    double y = h->GetBinContent(i);
    const double err = h->GetBinError(i);
    if( y < 0.0 ) y = 0.0;
    grp->SetPoint(i-1, h->GetBinCenter(i), y);
    //grp->SetPointError(i-1, w/2, err);
    grp->SetPointError(i-1, 0, err);
  }
  grp->SetEditable(false);

  return grp;
}
void drawUnfoldedHist(std::string year, bool isData){
  gROOT->ProcessLine("setTDRStyle();");
  gStyle->SetPaintTextFormat("4.1f");
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  TGaxis::SetMaxDigits(3);
  std::string input_dir = "../output/unfold/" + year;

  TPaveText *label_cms;
  if( year == "16" ) label_cms = tdrCMSlabel16();
  else if( year == "17" ) label_cms = tdrCMSlabel17();
  else if( year == "18" ) label_cms = tdrCMSlabel18();
  else label_cms = tdrCMSlabel1718();

  TPaveText *label_sim = tdrCMSSimlabel();
  TCanvas *c = new TCanvas("c","c",400,400);
  TLegend *leg = new TLegend(0.6, 0.7, 0.88, 0.88);
  TColor *color = new TColor();

  TFile *f_hist;
  const char * input_name;
  const char * data_name;

  if( isData ){
    input_name = "data";
    data_name = "_data_obs";
    f_hist = TFile::Open(Form("%s/hist_unfolded_data.root",input_dir.c_str()));
  }
  else{
    input_name = "ttbb";
    data_name = "";
    f_hist = TFile::Open(Form("%s/hist_unfolded_ttbb.root",input_dir.c_str()));
  }
  //access(Form("%s/hist_unfolded_data.root",input_dir.c_str()), exidata);
  //if( exidata == -1 ){
  //  std::cout << "There is no unfolded data root file" << std::endl;
  //}

  const char *name_reco_dR = "h_mindR_RecoAddbJetDeltaR";
  const char *name_reco_M = "h_mindR_RecoAddbJetInvMass";

  for(int ich = 0; ich < 3; ++ich){
    if ( isData and ich < 2 ) continue;
    // Get histograms and set drawing option
    //1. Response Matrix
    auto h2_matrix_dR = (TH2 *)f_hist->Get(Form("h_mindR_ResponseMatrixDeltaR_Ch%d_S3",ich));
    auto h2_matrix_M  = (TH2 *)f_hist->Get(Form("h_mindR_ResponseMatrixInvMass_Ch%d_S3",ich));
    
    //2. Unfolded Reco 
    auto grp_unfolded_dR = buildGraphFromHist((TH1 *)f_hist->Get(Form("Unfolded_%s_Ch%d_S3%s",name_reco_dR, ich, data_name)));
    auto grp_unfolded_M = buildGraphFromHist((TH1 *)f_hist->Get(Form("Unfolded_%s_Ch%d_S3%s",name_reco_M, ich, data_name)));
    
    grp_unfolded_dR->SetMarkerSize(0.8);
    grp_unfolded_M->SetMarkerSize(0.8);
    
    //3. DiffXsec Reco
    auto grp_diff_dR = buildGraphFromHist((TH1 *)f_hist->Get(Form("diffXsec_Unfolded_%s_Ch%d_S3%s",name_reco_dR, ich, data_name)));
    auto grp_diff_M = buildGraphFromHist((TH1 *)f_hist->Get(Form("diffXsec_Unfolded_%s_Ch%d_S3%s",name_reco_M, ich, data_name)));

    grp_diff_dR->SetMarkerSize(0.8);
    grp_diff_M->SetMarkerSize(0.8);
    
    //4. Step 3 Gen.
    auto h_gen_dR = (TH1 *)f_hist->Get(Form("h_mindR_GenAddbJetDeltaR_Ch%d_S3",ich));
    auto h_gen_M  = (TH1 *)f_hist->Get(Form("h_mindR_GenAddbJetInvMass_Ch%d_S3",ich));
    auto h_gen_dR_e = (TH1 *)h_gen_dR->Clone();
    auto h_gen_M_e  = (TH1 *)h_gen_M->Clone();
    
    h_gen_dR->SetLineColor(color->GetColor("#cc0000"));
    h_gen_dR->SetLineWidth(2);
    h_gen_dR->GetYaxis()->SetTitle("Number of events");
    h_gen_dR->SetMaximum(h_gen_dR->GetMaximum()*2.5);
    h_gen_M->SetLineColor(color->GetColor("#cc0000"));
    h_gen_M->SetLineWidth(2);
    h_gen_M->GetYaxis()->SetTitle("Number of events");
    h_gen_M->SetMaximum(h_gen_M->GetMaximum()*2.5);

    h_gen_dR_e->SetFillColor(color->GetColor("#556270"));
    h_gen_dR_e->SetFillStyle(3154);//3154
    h_gen_M_e->SetFillColor(color->GetColor("#556270"));
    h_gen_M_e->SetFillStyle(3154);

    //5. Gen. distribution applied accptance correction
    auto h_diff_nosel_dR = (TH1 *)f_hist->Get(Form("diffXsec_h_mindR_GenAddbJetDeltaR_Ch2_nosel"));
    auto h_diff_nosel_M  = (TH1 *)f_hist->Get(Form("diffXsec_h_mindR_GenAddbJetInvMass_Ch2_nosel"));
    
    h_diff_nosel_dR->SetLineColor(color->GetColor("#cc0000"));
    h_diff_nosel_dR->SetFillColor(color->GetColor("#cc0000"));
    h_diff_nosel_dR->GetYaxis()->SetTitle("#frac{d#sigma}{d#DeltaR_{b#bar{b}}}[pb]");
    h_diff_nosel_dR->GetYaxis()->SetTitleOffset(2.0);
    if( isData ) h_diff_nosel_dR->SetMaximum(h_diff_nosel_dR->GetMaximum()*2.0);
    if( ich == 0 )h_diff_nosel_dR->SetMaximum(h_diff_nosel_dR->GetMaximum()*2.0);
    h_diff_nosel_M->SetLineColor(color->GetColor("#cc0000"));
    h_diff_nosel_M->SetFillColor(color->GetColor("#cc0000"));
    h_diff_nosel_M->GetYaxis()->SetTitle("#frac{d#sigma}{dm_{b#bar{b}}}[pb/GeV]");
    h_diff_nosel_M->GetYaxis()->SetTitleOffset(2.0);
    if( isData ) h_diff_nosel_M->SetMaximum(h_diff_nosel_M->GetMaximum()*2.0);
    if( ich == 0 )h_diff_nosel_M->SetMaximum(h_diff_nosel_M->GetMaximum()*2.0);
    
    //6. Half of gen. distribution for closure test
    auto h_diff_gen_dR = (TH1 *)f_hist->Get(Form("diffXsec_h_mindR_GenAddbJetDeltaR_Ch%d_S3",ich));
    auto h_diff_gen_M  = (TH1 *)f_hist->Get(Form("diffXsec_h_mindR_GenAddbJetInvMass_Ch%d_S3",ich));
    
    h_diff_gen_dR->SetLineColor(color->GetColor("#cc0000"));
    h_diff_gen_dR->SetFillColor(color->GetColor("#cc0000"));
    h_diff_gen_dR->GetYaxis()->SetTitle("#frac{d#sigma}{d#DeltaR_{b#bar{b}}}[pb]");
    h_diff_gen_dR->SetMaximum(h_diff_gen_dR->GetMaximum()*1.5);
    h_diff_gen_M->SetLineColor(color->GetColor("#cc0000"));
    h_diff_gen_M->SetFillColor(color->GetColor("#cc0000"));
    h_diff_gen_M->GetYaxis()->SetTitle("#frac{d#sigma}{dm_{b#bar{b}}}[pb/GeV]");
    h_diff_gen_M->SetMaximum(h_diff_gen_M->GetMaximum()*1.5);

    //7. Reco distribution for comparison between data and MC
    auto h_reco_dR = (TH1 *)f_hist->Get(Form("%s_Ch%d_S3", name_reco_dR, ich));
    auto h_reco_M  = (TH1 *)f_hist->Get(Form("%s_Ch%d_S3", name_reco_M, ich));
    h_reco_dR->SetLineWidth(2);
    h_reco_dR->SetMaximum(h_reco_dR->GetMaximum()*2);
    h_reco_M->SetLineWidth(2);
    h_reco_M->SetMaximum(h_reco_M->GetMaximum()*2);

    //8. Unfolding input
    auto grp_input_dR = buildGraphFromHist((TH1 *)f_hist->Get(Form("Input_%s_Ch%d_S3%s",name_reco_dR, ich, data_name)));
    auto grp_input_M  = buildGraphFromHist((TH1 *)f_hist->Get(Form("Input_%s_Ch%d_S3%s",name_reco_M, ich, data_name)));
    grp_input_dR->SetMarkerSize(0.8);
    grp_input_M->SetMarkerSize(0.8);
    
    // Draw and save histograms
    //1. Response Matrix
    c->cd();
    h2_matrix_dR->Draw("box");
    label_sim->Draw("same");
    c->Print(Form("%s/%s/h2_ResponseMatrixDeltaR_Ch%d_S3.pdf", input_dir.c_str(), input_name, ich),"pdf");
    c->Clear();

    c->cd();
    h2_matrix_M->Draw("box");
    label_sim->Draw("same");
    c->Print(Form("%s/%s/h2_ResponseMatrixInvMass_Ch%d_S3.pdf", input_dir.c_str(), input_name, ich),"pdf");
    c->Clear();

    //2. Unfolded Reco vs. Step 3 Gen
    c->cd();
    //leg->SetHeader("# of jets >= 6, # of b jets >= 3");
    leg->AddEntry(grp_unfolded_dR, Form("Unfolded %s", input_name), "p");
    leg->AddEntry(h_gen_dR, "Gen. distribution", "l");
    h_gen_dR->Draw("hist");
    h_gen_dR_e->Draw("e2 same");
    grp_unfolded_dR->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_DeltaR_Unfolded%s_vs_Gen_Ch%d_S3.pdf", input_dir.c_str(), input_name, input_name, ich), "pdf");
    leg->Clear();
    c->Clear();

    c->cd();
    //leg->SetHeader("# of jets >= 6, # of b jets >= 3");
    leg->AddEntry(grp_unfolded_M, Form("Unfolded %s", input_name), "p");
    leg->AddEntry(h_gen_M, "Gen. distribution", "l");
    h_gen_M->Draw("hist");
    h_gen_M_e->Draw("e2 same");
    grp_unfolded_M->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_InvMass_Unfolded%s_vs_Gen_Ch%d_S3.pdf", input_dir.c_str(), input_name, input_name, ich), "pdf");   
    leg->Clear();
    c->Clear();

    //3. DiffXsec Reco vs. DiffXsec Step 3 Gen: Closure Test Only
    c->cd();
    //leg->SetHeader("Closure Test");
    leg->AddEntry(grp_diff_dR, Form("%s", input_name), "p");
    leg->AddEntry(h_diff_gen_dR, "Powheg+Pythia", "l");
    h_diff_gen_dR->Draw("hist");
    grp_diff_dR->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_DeltaR_DiffXsec%s_vs_Gen_Ch%d_S3.pdf", input_dir.c_str(),input_name, input_name, ich), "pdf");
    leg->Clear();
    c->Clear();

    c->cd();
    //leg->SetHeader("Closure Test");
    leg->AddEntry(grp_diff_M, Form("%s", input_name), "p");
    leg->AddEntry(h_diff_gen_M, "Powheg+Pythia", "l");
    h_diff_gen_M->Draw("hist");
    grp_diff_M->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_InvMass_DiffXsec%s_vs_Gen_Ch%d_S3.pdf", input_dir.c_str(), input_name,input_name, ich), "pdf");
    leg->Clear();
    c->Clear();

    //4. DiffXsec Reco vs. Nosel Geni
    c->cd();
    //leg->SetHeader("Differential Cross Section");
    leg->AddEntry(grp_diff_dR, Form("%s", input_name), "p");
    leg->AddEntry(h_diff_nosel_dR, "Powheg+Pythia", "F");
    h_diff_nosel_dR->Draw("hist");
    grp_diff_dR->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_DeltaR_DiffXsec%s_vs_NoselGen_Ch%d_S3.pdf", input_dir.c_str(), input_name,input_name, ich), "pdf");
    leg->Clear();
    c->Clear();

    c->cd();
    //leg->SetHeader("Closure Test");
    leg->AddEntry(grp_diff_M, Form("%s", input_name), "p");
    leg->AddEntry(h_diff_nosel_M, "Powheg+Pythia", "F");
    h_diff_nosel_M->Draw("hist");
    grp_diff_M->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_InvMass_DiffXsec%s_vs_NoselGen_Ch%d_S3.pdf", input_dir.c_str(), input_name,input_name, ich), "pdf");
    leg->Clear();
    c->Clear();

    //6. Data - bkg vs. reco
    c->cd();
    leg->SetHeader("Data - bkg vs. Reco distribution");
    leg->AddEntry(grp_input_dR, Form("%s", input_name), "p");
    leg->AddEntry(h_reco_dR, "ttbb", "l");
    h_reco_dR->Draw("hist");
    grp_input_dR->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_Input_dR_vs_ttbb_Ch%d_S3.pdf", input_dir.c_str(), input_name, ich),"pdf");
    leg->Clear();
    c->Clear();
 
    c->cd();
    leg->SetHeader("Data - bkg vs. Reco distribution");
    leg->AddEntry(grp_input_M, Form("%s", input_name), "p");
    leg->AddEntry(h_reco_M, "ttbb", "l");
    h_reco_M->Draw("hist");
    grp_input_M->Draw("p e same");
    leg->Draw("same");
    if( isData ) label_cms->Draw("same");
    else label_sim->Draw("same");
    c->Print(Form("%s/%s/h_Input_M_vs_ttbb_Ch%d_S3.pdf", input_dir.c_str(), input_name, ich),"pdf");
    leg->Clear();
    c->Clear(); 
  }
}
