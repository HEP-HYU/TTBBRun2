import os
import sys
from array import array

from ROOT import *

def _normalize_by_bSF(self, f_sample):
    print f_sample # debugging
    hist_list = [x.GetName() for x in f_sample.GetListOfKeys()]
    
    bSF_book = {'S0':[], 'S1':[], 'S2':[], 'S3':[], 'S5':[], 'S6':[]}
    for key in bSF_book.keys():
        for ich in range(0,3):
            bSF_book[key].append(f_sample.Get('h_bSFinfo_Ch'+str(ich)+'_'+str(key)))

    h_out = []
    for hist in hist_list:
        if any(i in hist.lower() for i in ['info','weight']): continue
        name = hist.split('__')[0]
        name = name.split('_')
        ch = name[-2]
        step = name[-1]
        if step == 'S4': step = 'S3'
        if any(i == step for i in ['S7','S8','S9']): step = 'S6'

        h_bSF = bSF_book[step]('h_bSFinfo_'+str(ch)+'_'+str(step))
        h_tmp = f_sample.Get(hist)
    
        btag_sys = hist.split('__')[-1]
        binnum = 2
        if any(i in hist_name for i in ['__lf', '__hf', '__cferr']):
            binnum = h_bSF.GetXaxis().FindBin(str(btag_sys))

        if h_bSF.GetBinContent(binnum) > 0:
            h_tmp.Scale(h_bSF.GetBinContent(1)/h_bSF.GetBinContent(binnum))

        h_out.append(h_tmp)

    return h_out

def _rescale_extsample(self, f_sys, h_eventinfo):
    print f_tmp # debugging
    hist_list = []
    hist_list = [x.GetName() for x in f_sys.GetListOfKeys()]
    h_eventinfo_sys = f_sys.Get("EventInfo")

    bratio = 1.0
    if "TT_" in f_sys.GetName() and not "Bkg" in f_sys.GetName(): bratio = 356.4/831.76

    h_out =[]
    for hist in hist_list:
        if any(i in hist.lower() for i in ['info', 'weight']): continue
        h_tmp = f_sys.Get(hist)
        h_tmp.Scale(h_eventinfo.GetBinContent(2)/(h_eventinfo_sys.GetBinContent(2)*bratio))
        h_out.append(h_tmp)

    return h_out

def _write_envelope(self, sys_name, h_central, h_sys_list, h_eventinfo, h_weights):
    #Find maximum, minimum bin errors
    h_sys_weighted_list = []
    for index, hist in enumerate(h_sys_list):
        #hist.Scale(h_eventinfo.GetBinContent(2)/(h_weights.GetBinContent(index+1)*bratio))
        h_sys_weighted_list.append(hist)

    h_up = h_central.Clone()
    h_down = h_central.Clone()
    
    if h_central.GetDimension() == 1:
        for ibin in range(h_central.GetNbinsX()+2):
            minimum = float("inf")
            maximum = float("-inf")

            for hist in h_sys_weighted_list:
                minimum = min(minimum, hist.GetBinContent(ibin))
                maximum = max(maximum, hist.GetBinContent(ibin))

            h_up.SetBinContent(ibin, maximum)
            h_down.SetBinContent(ibin, minimum)
    elif h_central.GetDimension() == 2:
        for ixbin in range(h_central.GetNbinsX()+2):
            for iybin in range(h_central.GetNbinsY()+2):
                minimum = float("inf")
                maximum = float("-inf")

                for hist in h_sys_weighted_list:
                    minimum = min(minimum, hist.GetBinContent(ixbin, iybin))
                    maximum = max(maximum, hist.GetBinContent(ixbin, iybin))

                h_up.SetBinContent(ixbin, iybin, maximum)
                h_down.SetBinContent(ixbin, iybin, minimum)

    upname = "__"+sys_name+"up"
    downname= "__"+sys_name+"down"
    
    h_up.SetName(h_central.GetName()+upname)
    h_down.SetName(h_central.GetName()+downname)

    return [h_up, h_down]

def _execute_postprocess(self, proc):
    f_sample = TFile.Open(os.path.join(self.merge_dir, proc), "READ")
    f_update = TFile.Open(os.path.join(self.merge_dir,'post', proc), "RECREATE")
    
    h_eventinfo    = f_sample.Get("EventInfo")
    hist_list = [x.GetName() for x in f_sample.GetListOfKeys()]

    print("%s: b-tag SF scaling..." % proc)
    h_out = self._normalize_by_bSF(f_sample) 
    f_update.cd()
    for hist in h_out:
        if not any(i in hist.GetName() for i in ['info', 'Weight']):
            hist.Write()
   
    print("%s: Merge JER, JEC histograms..." % proc)
    syst_jet = ["__jerup", "__jerdown", "__jecup", "__jecdown"]
    for syst in jet_syst:
        f = TFile.Open(os.path.join(self.merge_dir, proc[:-5]+syst+'.root'))
        h_out = self._normalize_by_bSF(f)
        f_update.cd()
        for hist in h_out:
            if not any(i in hist.GetName() for i in ['info', 'Weight']):
                hist.Write()

    if 'TT' in proc and not 'Filter' in proc:
        print("%s: Rescaling external samples..." % proc)
        for syst in self.extsyst:
            for vari in ['up','down']:
                ext_name = proc[:-5]
                
                tmp = syst+vari 
                f_ext = TFile.Open(os.path.join(self.merge_dir, ext_name+'__'+tmp+'.root'), "READ")
                f_tmp = TFile.Open(os.path.join(self.merge_dir, "tmp.root"), "RECREATE")
                
                h_out = self._normalize_by_bSF(f_ext)
                f_tmp.cd()
                for hist in h_out:
                    if not any(i in hist.GetName() for i in ['info', 'Weight']):
                        hist.Write()
                
                h_out = self._rescale_extsample(f_tmp, h_eventinfo)
                f_update.cd()
                for hist in h_out:
                    if not any(i in hist.GetName() for i in ['Info', 'Weight']):
                        hist.Write()

        print("%s: Writing envelope..." % proc)
        h_scaleweights = f_sample.Get("ScaleWeights")
        h_pdfweights   = f_sample.Get("PDFWeights")
        h_psweights = f_sample.Get("PSWeights")

        for hist in hist_list:
            if any(i in hist.lower() for i in ['__', 'info', 'weight']): continue

            h_central = f_sample.Get(hist)
        
            h_sw_list = []
            for i in range(6):
                h_sw_list.append(f_sample.Get(hist+"__scale"+str(i)))
        
            h_pdf_list = []
            maxpdf = 104
            for i in range(maxpdf):
                h_pdf_list.append(f_sample.Get(hist+"__pdf"+str(i)))
        
            h_ps_list = []
            for ps in ps_list:
                h_ps_list.append(f_sample.Get(hist+"__"+ps))
       
            f_update.cd()
            h_sw_new = []
            h_sw_new = self._write_envelope("sw", h_central, h_sw_list, h_eventinfo, h_scaleweights)
            h_sw_new[0].Write()
            h_sw_new[1].Write()

            h_pdf_new = []
            h_pdf_new = self._write_envelope("pdf", h_central, h_pdf_list, h_eventinfo, h_pdfweights)
            h_pdf_new[0].Write()
            h_pdf_new[1].Write()    
           
            h_ps_new = []
            h_ps_new = self._write_envelope("ps", h_central, h_ps_list, h_eventinfo, h_psweights)
            h_ps_new[0].Write()
            h_ps_new[1].Write()
    
    f_update.cd()
    evtinfo = f_sample.Get("EventInfo")
    evtinfo.Write()
    f_update.Close()
    f_sample.Close()
    
    print("End Process "+str(os.getpid())+" "+str(proc))       
