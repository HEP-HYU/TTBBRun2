from ROOT import *
import os
import sys

from array import array

def rescale(f_sys, h_eventinfo):
    hist_list = []
    hist_list = [x.GetName() for x in f_sys.GetListOfKeys()]
    h_eventinfo_sys = f_sys.Get("EventInfo")

    bratio = 1.0
    if "TT_" in f_sys.GetName() and not "Bkg" in f_sys.GetName(): bratio = 356.4/831.76

    h_out =[]
    for hist in hist_list:
        if hist == "EventInfo" or "Weights" in hist: continue
        h_tmp = f_sys.Get(hist)
        h_tmp.Scale(h_eventinfo.GetBinContent(2)/(h_eventinfo_sys.GetBinContent(2)*bratio))
        h_out.append(h_tmp)

    return h_out

def write_envelope(sys_name, h_central, h_sys_list, h_eventinfo, h_weights):
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

def bSFnorm(h_bSF, h_tmp):
    hist_name = h_tmp.GetName()
    btag_sys = hist_name.split('__')[-1]
    binnum = 2
    if any(i in hist_name for i in ['__lf', '__hf', '__cferr']):
        binnum = h_bSF.GetXaxis().FindBin(str(btag_sys))

    if h_bSF.GetBinContent(binnum) > 0:
        h_tmp.Scale(h_bSF.GetBinContent(1)/h_bSF.GetBinContent(binnum))

    return h_tmp

def postProcess(input_path, proc, year, isCP5=True):
    if not os.path.exists(input_path+'/post'):
        try:
            os.makedirs(input_path+'/post')
        except OSError:
            print(input_path+'/post: already exists')
    print("Begin Process "+str(os.getpid())+" "+str(proc))
      
    if any(i in proc for i in ['Data', 'QCD']):
        return

    f_sample = TFile.Open(os.path.join(input_path, proc), "READ")
    f_update = TFile.Open(os.path.join(input_path,'post', proc), "RECREATE")
    
    h_eventinfo    = f_sample.Get("EventInfo")
    h_scaleweights = f_sample.Get("ScaleWeights")
    h_pdfweights   = f_sample.Get("PDFWeights")

    print("b-tag SF scaling...")
    hist_list = [x.GetName() for x in f_sample.GetListOfKeys()]

    f_update.cd()
    for hist in hist_list:
        if any(i in hist for i in ['scale','ps','pdf','Info','Weight']): continue
        tmp = hist.split('__')[0]
        tmp = tmp.split('_')[-2]
        if not 'Ch2' in tmp:
            if 'S0' in hist:
                h_bSF = f_sample.Get('h_bSFinfo_'+tmp+'_S0')
            else:
                h_bSF = f_sample.Get('h_bSFinfo_'+tmp+'_S1')
        else:
            if 'S0' in hist:
                h_bSF = f_sample.Get('h_bSFinfo_Ch0_S0')
                h_bSF.Add(f_sample.Get('h_bSFinfo_Ch1_S0'))
            else:
                h_bSF = f_sample.Get('h_bSFinfo_Ch0_S0')
                h_bSF.Add(f_sample.Get('h_bSFinfo_Ch1_S0'))

        h_tmp = f_sample.Get(hist)
        h_tmp = bSFnorm(h_bSF, h_tmp)
        h_tmp.Write()

    print("Merge JER, JEC histograms...")
    syst_jet = ["jerup", "jerdown", "jecup", "jecdown"]
    f_list = []
    for jet in syst_jet:
        f_list.append(TFile.Open(os.path.join(input_path, proc[:-5]+"__"+jet+".root")))

    f_update.cd()
    for hist in hist_list:
        if not any(i in hist for i in ['__', 'Info', 'Weight', 'bSF']):
            for index, value in enumerate(f_list):
                tmp = value.Get(hist+"__"+syst_jet[index])
                tmp.Write()

    if not isCP5:
        syst_external = ['tune', 'hdamp', 'isr', 'fsr']
    else:
        syst_external = ['tune', 'hdamp']

    if 'Filter' in proc: return 

    if 'TT' in proc:
        print("Rescaling external samples...")
        for syst in syst_external:
            for vari in ['up','down']:
                if isCP5:
                    ext_name = proc[:-5]
                else:
                    ext_name = proc.replace('TTLJ','TT')[:-5]
                
                tmp = syst+vari 
                f_ext = TFile.Open(os.path.join(input_path, ext_name+'__'+tmp+'.root'), "READ")
                h_out = []
                h_out = rescale(f_ext, h_eventinfo)

                f_update.cd()
                for hist in h_out:
                    if not any(i in hist.GetName() for i in ['Info', 'Weight']):
                        hist.Write()

        print("Writing envelope...")
        ps_list = ["isrup", "fsrup", "isrdown", "fsrdown"]
        
        if not isCP5:
            if not 'Bkg' in proc:
                ext_name = proc.replace('TTLJ','TT')[:-5]
            else:
                ext_name = proc[:-5]

            f_ps_list = []
            for ps in ps_list:
                f_ps_list.append(TFile.Open(os.path.join(input_path, ext_name+"__"+ps+".root"),"READ"))

            h_psweights = TH1D("PSweights","",4,0,4)
            for index, value in enumerate(ps_list):
                h_psweights.GetXaxis().SetBinLabel(index+1,value)
                tmp = (f_ps_list[index].Get("EventInfo")).GetBinContent(2)
                h_psweights.SetBinContent(index+1,tmp)
                f_ps_list[index].Close()
        else:
            h_psweights = f_sample.Get("PSWeights")

        for hist in hist_list:
            if any(i in hist for i in ['__', 'Info', 'Weight', 'bSF']): continue

            h_central = f_sample.Get(hist)
        
            h_sw_list = []
            for i in range(6):
                h_sw_list.append(f_sample.Get(hist+"__scale"+str(i)))
        
            h_pdf_list = []
            if year == 16 and not 'CP5' in proc: maxpdf = 102
            else: maxpdf = 104
            for i in range(maxpdf):
                h_pdf_list.append(f_sample.Get(hist+"__pdf"+str(i)))
        
            h_ps_list = []
            if year == 16:
                for ps in ps_list:
                    h_ps_list.append(f_update.Get(hist+"__"+ps))
            else:
                for ps in ps_list:
                    h_ps_list.append(f_sample.Get(hist+"__"+ps))
       
            f_update.cd()
            h_sw_new = []
            h_sw_new = write_envelope("sw", h_central, h_sw_list, h_eventinfo, h_scaleweights)
            h_sw_new[0].Write()
            h_sw_new[1].Write()

            h_pdf_new = []
            h_pdf_new = write_envelope("pdf", h_central, h_pdf_list, h_eventinfo, h_pdfweights)
            h_pdf_new[0].Write()
            h_pdf_new[1].Write()    
           
            #h_ps_new = []
            #h_ps_new = write_envelope("ps", h_central, h_ps_list, h_eventinfo, h_psweights)
            #h_ps_new[0].Write()
            #h_ps_new[1].Write()
    
    f_update.cd()
    evtinfo = f_sample.Get("EventInfo")
    evtinfo.Write()
    f_update.Close()
    f_sample.Close()
    print("End Process "+str(os.getpid())+" "+str(proc))
