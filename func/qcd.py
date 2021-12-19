import os, sys
import subprocess

import ROOT

import sampleinfo as si

class GetQCDshape(si.LoadSamples):
    def __init__(self, year, lumi, root_path):
        self.year = year
        self.lumi = lumi
        self.root_path = root_path
       
        self.data = {}
        self.samples = {}
        
        self.get_sample_info()
        self._get_root_files()

    def _get_root_files(self):
        self.data['Muon'] = ROOT.TFile(os.path.join(self.root_path, 'hist_dataDriven_DataSingleMu.root'))
        self.data['Electron'] = ROOT.TFile(os.path.join(self.root_path, 'hist_dataDriven_DataSingleEG.root'))
        for sample in self.xsecs.values():
            self.samples[sample[0]] = ROOT.TFile(os.path.join(self.root_path, 'hist_dataDriven_'+sample[0]+'.root'))

    def get_qcd_shape(self):
        qcd_syst = ['','__qcdisoup', '__qcdisodown']
        print "Get QCD shape in the sideband region"
        for syst in qcd_syst:
            f_qcd = ROOT.TFile.Open(os.path.join(self.root_path, 'hist_temp'+str(syst)+'.root'), "RECREATE")
            hist_list = [x.GetName() for x in f_data[0].GetListOfKeys()]
            
            f_qcd.cd()
            for hist in hist_list:
                if any(i in hist.lower() for i in ['info', 'weight']): continue
                if 'Ch0' in hist:
                    h_qcd = self.data['Muon'].Get(hist)
                elif 'Ch1' in hist:
                    h_qcd = self.data['Electron'].Get(hist)
                else:
                    h_qcd = self.data['Muon'].Get(hist)
                    tmp = self.f_data['Electron'].Get(hist)
                    h_qcd.Add(tmp)

                if "TransverseMass" in hist:
                    nevt_data = h_qcd.Integral(0, h_qcd.GetNbinsX()+1)

                for key, value in self.samples.item():
                    if any(i in key for i in ['QCD', 'Filter']): continue
                    scale = self.lumi*self.xsec[key]/self.genevt[key]
                    h_tmp = value.Get(hist)
                    h_tmp.Scale(scale)
                    h_qcd.Add(h_tmp,-1)
                h_qcd.Write()
                    
                if "TransverseMass" in hist:
                    nevt_qcd = h_qcd.Integral(0, h_qcd.GetNbinsX()+1)
                    print("Purity of QCD")
                    print("Hist: "+str(hist))
                    print("nevt_data: "+str(nevt_data))
                    print("nevt_qcd: "+str(nevt_qcd))
                    if nevt_data != 0:
                        purity = float(nevt_qcd)/float(nevt_data)
                    else:
                        purity = 'Nan'
                    print("Puriy: "+str(purity))
            f_qcd.Close()
        cmd = ['hadd', os.path.join(self.root_path, 'hist_dataDriven_QCD.root')]
        for syst in qcd_syst:
            cmd.append(os.path.join(self.root_path, 'hist_temp'+str(syst)+'.root'))
        subprocess.call(cmd)
