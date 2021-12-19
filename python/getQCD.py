from ROOT import *
import ROOT
import os
import sys

import postProcess as pp

def getQCDShape(base_path, year):
    lumi = {16:35922, 17:41529, 18:59741}

    genevt = {}
    with open(base_path+'/samples/genevt'+str(year)+'.txt','r') as f:
        while True:
            line = f.readline()
            if not line: break
            tmp = line.split(' ')
            genevt[tmp[0]] = float(tmp[1])

    sample_list = [] 
    xsec = {}
    with open(base_path+'/samples/xsec'+str(year)+'.txt','r') as f:
        while True:
            line = f.readline()
            if not line: break
            if 'Sample Xsec' in line: continue
            tmp = line.split(' ')
            if float(tmp[2]) < 0: continue
            xsec[tmp[0]] = float(tmp[1])
            sample_list.append(tmp[0])
 
    input_path = base_path+'/output/root'+str(year)+'_qcd/'
    if not os.path.exists(input_path+'/post'):
        os.mkdir(input_path+'/post')   
   
    f_out = open("../qcd"+str(year)+'.txt','w')
    print "YEAR: "+str(year)
    print "Start post process for data driven QCD"

    qcd_list = ['Nosys','dataDriven']
    qcd_syst = ['qcdisoup', 'qcdisodown']
    for qitem in qcd_list:
        print "Merge root files and rescale histograms to b-tag SF"
        data = ['Mu', 'EG']
        for value in data:
            f_data = TFile.Open(os.path.join(input_path, 'hist_'+qitem+'_DataSingle'+value+'.root'))
            print "File: "+ str(f_data.GetName())
            f_update = TFile.Open(os.path.join(input_path+'/post', 'hist_'+qitem+'_DataSingle'+value+'.root'), "RECREATE")
            f_syst = []
            if not 'Nosys' in qitem:
                for syst in qcd_syst:
                    f_syst.append(TFile.Open(os.path.join(input_path, 'hist_'+qitem+'_DataSingle'+value+'__'+syst+'.root')))

            hist_list = [x.GetName() for x in f_data.GetListOfKeys()]
            f_update.cd()
            for hist in hist_list:
                h_tmp = f_data.Get(hist)
                h_tmp.Write()
                if not any(i in hist for i in ['__', 'Info', 'Weight', 'bSF']) and not 'Nosys' in qitem:
                    for index, value in enumerate(f_syst):
                        tmp = value.Get(hist+'__'+qcd_syst[index])
                        tmp.Write()
            f_update.Close() 

        for proc in sample_list:
            if 'Data' in proc: continue
            f_sample = TFile.Open(os.path.join(input_path, 'hist_'+qitem+'_'+proc+'.root'), "READ")
            print "File: " +str(f_sample.GetName())
            f_update = TFile.Open(os.path.join(input_path+'/post', 'hist_'+qitem+'_'+proc+'.root'), "RECREATE")

            f_syst = []
            if not 'Nosys' in qitem:
                for syst in qcd_syst:
                    f_syst.append(TFile.Open(os.path.join(input_path, 'hist_'+qitem+'_'+proc+'__'+syst+'.root')))

            hist_list = [x.GetName() for x in f_sample.GetListOfKeys()]
            
            f_update.cd()
            for hist in hist_list:
                if any(i in hist for i in ['info', 'Info', 'Weight']): continue
                tmp = hist.split('__')[0]
                ch   = tmp.split('_')[-2]
                step = tmp.split('_')[-1]
                if qitem == 'QCDshape':
                    if 'S0' in hist:
                        h_bSF = f_sample.Get('h_bSFinfo_'+ch+'_S0')
                    else:
                        h_bSF = f_sample.Get('h_bSFinfo_'+ch+'_S1')
                else:
                    h_bSF = f_sample.Get('h_bSFinfo_'+ch+'_'+step)
                h_tmp = f_sample.Get(hist)
                h_tmp = pp.bSFnorm(h_bSF, h_tmp)
                h_tmp.Write()
                if not 'Nosys' in qitem:
                    for index, syst in enumerate(qcd_syst):
                        h_tmp = f_syst[index].Get(hist+'__'+syst)
                        h_tmp = pp.bSFnorm(h_bSF, h_tmp)
                        h_tmp.Write()
            f_update.Close()

        if 'Nosys' in qitem: continue
        print "Get QCD shape in the sideband region"
        f_qcd = TFile.Open(os.path.join(input_path+'/post', 'hist_'+qitem+'_QCD.root'), "RECREATE")
        f_data = []
        for value in data:
            f_data.append(TFile.Open(os.path.join(input_path+'/post', 'hist_'+qitem+'_DataSingle'+value+'.root')))

        hist_list = [x.GetName() for x in f_data[0].GetListOfKeys()]
        samples = {}
        for proc in sample_list:
            f_tmp = TFile.Open(os.path.join(input_path+'/post', "hist_"+qitem+"_"+proc+".root"))
            samples[proc] = f_tmp

        f_qcd.cd()
        for hist in hist_list:
            if any(i in hist for i in ['info', 'Info', 'Weight']): continue
            if 'Ch0' in hist:
                h_qcd = f_data[0].Get(hist)
            elif 'Ch1' in hist:
                h_qcd = f_data[1].Get(hist)
            else:
                h_qcd = f_data[0].Get(hist)
                tmp = f_data[1].Get(hist)
                h_qcd.Add(tmp)

            if "TransverseMass" in hist:
                nevt_data = h_qcd.Integral(0, h_qcd.GetNbinsX()+1)

            for proc in sample_list:
                if any(i in proc for i in ['QCD', 'Filter', 'Data']): continue
                scale = lumi[year]*xsec[proc]/genevt[proc]
                
                h_tmp = samples[proc].Get(hist)
                h_tmp.Scale(scale)
                h_qcd.Add(h_tmp,-1)
                
            if "TransverseMass" in hist:
                nevt_qcd = h_qcd.Integral(0, h_qcd.GetNbinsX()+1)
                print("Purity of QCD")
                print("Hist: "+str(hist))
                print("nevt_data: "+str(nevt_data))
                print("nevt_qcd: "+str(nevt_qcd))
                f_out.write("Hist: "+str(hist))
                f_out.write("nevt_data: "+str(nevt_data))
                f_out.write("nevt_qcd: "+str(nevt_qcd))
                #purity = float(nevt_qcd)/float(nevt_data)
                #print("Puriy: "+str(purity))

            h_qcd.Write()
        f_qcd.Close()
    f_out.close()
