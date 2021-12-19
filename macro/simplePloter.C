#include <TFile.h>
#include <TObject.h>
#include <TKey.h>
#include <TH1.h>
#include <TH2.h>
#include <TH3.h>
#include <TCanvas.h>

#include "tdrstyle.C"

void simplePloter(string inputFile, string outputLocation = "../output/pdf/"){
  gROOT->ProcessLine("setTDRStyle();");
  
  gStyle->SetPaintTextFormat("4.1f");
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  gStyle->SetPadRightMargin(0.05);
  //gStyle->SetErrorX(00);
  TGaxis::SetMaxDigits(3);
  
  size_t pos;
  
  TPaveText *label_cms = tdrCMSlabel();
  TPaveText *label_sim = tdrCMSSimlabel();

  TFile *file = TFile::Open(inputFile.c_str());

  TCanvas *c = new TCanvas("c","c",800,800);

  TIter next(file->GetListOfKeys());
  TKey *key;
  TObject *obj;
  while((key = (TKey*)next())){
    obj = key->ReadObj();
    if(obj->InheritsFrom(TH1D::Class())){
      auto h = (TH1D *)obj;
      auto e = (TH1D *)h->Clone();
      string histname = h->GetName();
      if((pos = histname.find("__")) != std::string::npos) continue;
      h->SetLineWidth(2);
      h->SetLineColor(kBlue);
      e->SetFillStyle(3013);
      e->SetFillColor(kBlue);
      h->Draw("hist");
      e->Draw("e2 same");
      h->GetYaxis()->SetTitleOffset(1.5);
      h->GetXaxis()->SetTitleOffset(1.2);
      if((pos = histname.find("Data")) != std::string::npos)
	label_cms->Draw("same");
      else 
	label_sim->Draw("same");
      c->Print(Form("%s/%s.pdf",outputLocation.c_str(), obj->GetName()),"pdf");
    }
    else if(obj->InheritsFrom(TH2D::Class())){
      auto h = (TH2D *) obj;
      string histname = h->GetName();
      if((pos = histname.find("__")) != std::string::npos) continue;
      //h->Draw("col text");
      h->Draw("box");
      if((pos = histname.find("Data")) != std::string::npos)
        label_cms->Draw("same");
      else
        label_sim->Draw("same");
      c->Print(Form("%s/%s.pdf",outputLocation.c_str(), obj->GetName()),"pdf");
    }
    else{
      auto h = (TH3D *) obj;
      h->Draw();
    }
  }
}
