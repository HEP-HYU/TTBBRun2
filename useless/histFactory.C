#include <vector>
#include <iostream>
#include <string>
#include <algorithm>
#include <fstream>
#include <sstream>

#include "TFile.h"
#include "TROOT.h"
#include "TSystem.h"
#include "RooWorkspace.h"
#include "RooAbsData.h"
#include "RooRealVar.h"
#include "RooStats/HistFactory/Measurement.h"
#include "RooStats/HistFactory/MakeModelAndMeasurementsFast.h"

void histFactory(int year){
  ssize_t pos;

  double lumi = 1.0;
  if     (year == 16) lumi = 35922;
  else if(year == 17) lumi = 41529;
  else if(year == 18) lumi = 59693;
  else {
    std::cout << "Wrong year" << std::endl;
    return;
  }

  ifstream sample(Form("../samples/sample%d.txt", year));  
  std::vector<std::string> v_sample;
  std::string tmp_str;
  int i = 1;
  while(getline(sample, tmp_str)){
    if(i != 1) v_sample.push_back(tmp_str);
    ++i;
  }

  i = 1;
  std::stringstream ss;
  ifstream xsec(Form("../samples/xsec%d.txt", year));
  std::map<std::string, double> m_xsec;
  std::string tmp_name; double tmp_value;
  while(getline(xsec, tmp_str)){
    if( i != 1){
      ss.str(tmp_str);
      ss >> tmp_name;
      ss >> tmp_value;
      m_xsec.insert(std::pair<std::string, double>(tmp_name, tmp_value));
    }
    ++i;
  }
  xsec.close();

  ifstream genevt(Form("../samples/genevt%d.txt", year));
  std::map<std::string, double> m_genevt;
  while(getline(genevt, tmp_str)){
    ss.str(tmp_str);
    ss >> tmp_name;
    ss >> tmp_value;
    m_genevt.insert(std::pair<std::string, double>(tmp_name, tmp_value));
  }
  genevt.close();
  
  TFile *f_data[2];
  f_data[0] = TFile::Open(Form("../output/root%d/hist_DataSingleMu.root",year));
  f_data[1] = TFile::Open(Form("../output/root%d/hist_DataSingleEG.root",year));

  std::map<std::string, TFile *> m_fsample;
  for(auto v_itr = v_sample.begin(); v_itr != v_sample.end(); ++v_itr){
    m_fsample.insert(std::pair<std::string, TFile *>(
        *v_itr ,TFile::Open(Form("../output/root%d/hist_%s.root",year, (*v_itr).c_str()))));
  }

  for(int ich=0; ich < 1; ++ich){
    std::string hist_name = Form("h_nbJets_Ch%d_S1",ich);
    auto h_data = (TH1 *)f_data[ich]->Get(hist_name.c_str());

    std::map<std::string, TH1 *> m_hsim;
    for(auto v_itr = v_sample.begin(); v_itr != v_sample.end(); ++v_itr){
      auto h_tmp = (TH1 *)m_fsample[*v_itr]->Get(hist_name.c_str());
      // Normaize without luminosity
      h_tmp->Scale(lumi*m_xsec[*v_itr]/m_genevt[*v_itr]);
      if((pos = (*v_itr).find("Bkg",0)) != std::string::npos 
          || (pos = (*v_itr).find("ttother",0)) != std::string::npos) continue;
      m_hsim.insert(std::pair<std::string, TH1 *>(*v_itr, h_tmp));
    }
    // Merge ttbar background histograms
    if( year == 2016 ){
      std::string ttbkg = "TT_PowhegPythiaBkg";
      std::string ttother = "TTLJ_PowhegPythia_ttother";
      auto h_bkg = (TH1 *)m_fsample[ttbkg]->Get(hist_name.c_str());
      auto h_ttother = (TH1 *)m_fsample[ttother]->Get(hist_name.c_str());
      h_bkg->Scale(lumi*m_xsec[ttbkg]/m_genevt[ttbkg]);
      h_ttother->Scale(lumi*m_xsec[ttother]/m_genevt[ttother]);
      h_bkg->Add(h_ttother);
      m_hsim.insert(std::pair<std::string, TH1 *>("ttbkg", h_bkg));
    }
    else{
      std::string ttjjbkg = "TTJJ_PowhegPythiaBkg";
      std::string ttljbkg = "TTLJ_PowhegPythiaBkg";
      std::string ttllbkg = "TTLL_PowhegPythiaBkg";
      std::string ttother = "TTLJ_PowhegPythia_ttother";
      auto h_ttjj = (TH1 *)m_fsample[ttjjbkg]->Get(hist_name.c_str());
      auto h_ttlj = (TH1 *)m_fsample[ttljbkg]->Get(hist_name.c_str());
      auto h_ttll = (TH1 *)m_fsample[ttllbkg]->Get(hist_name.c_str());
      auto h_ttother = (TH1 *)m_fsample[ttother]->Get(hist_name.c_str());
      h_ttjj->Scale(lumi*m_xsec[ttjjbkg]/m_genevt[ttjjbkg]);
      h_ttlj->Scale(lumi*m_xsec[ttljbkg]/m_genevt[ttljbkg]);
      h_ttll->Scale(lumi*m_xsec[ttllbkg]/m_genevt[ttllbkg]);
      h_ttother->Scale(lumi*m_xsec[ttother]/m_genevt[ttother]);
      h_ttjj->Add(h_ttlj);
      h_ttjj->Add(h_ttll);
      h_ttjj->Add(h_ttother);
      m_hsim.insert(std::pair<std::string, TH1 *>("ttbkg", h_ttjj));
    }

    std::cout << "Start Fitting" << std::endl;
    RooStats::HistFactory::Measurement meas("meas", "meas");
    meas.SetOutputFilePrefix(Form("../output/workspace/%d/",year));
    meas.SetPOI("ttbb");
    //meas.SetPOI("ttbj");
    //meas.SetPOI("ttcc");
    //meas.SetPOI("ttLF");
    //meas.SetPOI("ttbkg");
    meas.SetLumi(1.0);
    meas.AddConstantParam("Lumi");

    std::cout << "Set channel" << std::endl;
    RooStats::HistFactory::Channel channel("bJet");
    channel.SetData(h_data);

    std::cout << "Set signal" << std::endl;
    RooStats::HistFactory::Sample signal("signal");
    signal.SetHisto(m_hsim["TTLJ_PowhegPythia_ttbb"]);
    signal.AddNormFactor("ttbb",1,0.5,1.5);
    channel.AddSample(signal);

    std::cout << "Set background" << std::endl;
    RooStats::HistFactory::Sample sample[v_sample.size()-1];
    int i = 0;
    for(auto m_itr = m_hsim.begin(); m_itr != m_hsim.end(); ++m_itr){
      std::cout << "Sample: " << m_itr->first << std::endl;
      if( m_itr->first == "TTLJ_PowhegPythia_ttbb" ) continue;
      bool flag = false;
      if     ( m_itr->first == "TTLJ_PowhegPythia_ttbj" ) flag = true;
      else if( m_itr->first == "TTLJ_PowhegPythia_ttcc" ) flag = true;
      else if( m_itr->first == "TTLJ_PowhegPythia_ttLF" ) flag = true;
      else if( m_itr->first == "ttbkg" )                  flag = true;
      sample[i].SetName(m_itr->first);
      sample[i].SetHisto(m_itr->second);
      if(flag) sample[i].AddNormFactor(m_itr->first, 1, 0.5, 1.5);
      channel.AddSample(sample[i]);
      ++i;
    }
    std::cout << "Add channel" << std::endl;
    meas.AddChannel(channel);
    //std::cout << "CollectHistograms" << std::endl;
    ///meas.CollectHistograms();

    RooWorkspace *w = RooStats::HistFactory::MakeModelAndMeasurementFast(meas);
  }
}
