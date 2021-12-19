#!/usr/bin/python
import os
import sys

from ROOT import TChain, TFile, TH1D, TH1F, TCanvas

def runAna(year, dir, file, name, isQCD='False'):   
    # tmp: /data/users/seohyun/ntuple/Run2016/v808/nosplit/Nosys_Compile/TTLJ_PowhegPythia_ttbbFilter_ttbb
    # process: Run2016/TTLJ_PowhegPythia_ttbb__jecup/TTLJ_PowhegPythia_ttbb
    tmp = dir+'/'+str(name)+'/'+file[:-5]
    tmp = tmp.split('/')
    process = str(tmp[5])+'/'+str(tmp[-2])+'/'+str(tmp[-1])

    #print("Begin Process "+str(os.getpid())+": "+str(process))

    outdir = 'output/root'+str(year) 
    if 'Tree' in file:
        outdir += '/'+name
    try:
        os.makedirs(outdir)
    except OSError:
        print(outdir+": already exists")

    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected')
    
    isQCD = str2bool(isQCD)
    if isQCD:
        chain = TChain("ttbbLepJetsQCD/tree", "events")
    else:
        chain = TChain("ttbbLepJets/tree","events")

    chain.Add(dir+"/"+file)
    chain.Process("macro/MyAnalysis.C+", process)

    f = TFile(dir+"/"+file,"read")

    ## save Event Summary histogram ##
    if 'Tree' in process:
        out = TFile(outdir+'/hist_'+file, 'update')
    else:
        out = TFile(outdir+'/hist_'+name+'.root', 'update')

    hevt = f.Get("ttbbLepJets/EventInfo")
    hsw = f.Get("ttbbLepJets/ScaleWeights")
    hpdf = f.Get("ttbbLepJets/PDFWeights")
    hps = f.Get("ttbbLepJets/PSWeights")
    hevt.Write()
    if not hpdf == None: hpdf.Write()
    if not hsw == None: hsw.Write()
    if not hps == None: hps.Write()
    out.Write()
    out.Close()
    
    print("End Process "+str(os.getpid())+": "+str(process))

if len(sys.argv) == 6:
    runAna(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
