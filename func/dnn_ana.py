import sys, os

import pandas as pd
import math
import numpy as np
from array import array
import yaml

import ROOT
from ROOT import *

import utils as ut
if not len(sys.argv) == 6:
    print "usage: ana.py year inputDir array outputDir"
    print "\nMake additional b jets histograms"
    print "All arguments are required. Please enter arguments"

year = int(sys.argv[1])
inputDir = sys.argv[2]
outputDir = sys.argv[4]
process = outputDir.split('/')[-1]
print("Process: "+process+"/"+sys.argv[3])

output = sys.argv[3].replace('array','hist').replace('h5','root')
f_out = ROOT.TFile(outputDir+'/'+output, 'recreate')

number_of_jets = 6
number_of_bjets = 2

nChannel = 3

nbins_reco_addbjets_dr = 4
reco_addbjets_dr_min = 0.4
reco_addbjets_dr_max = 4.0
reco_addbjets_dr_width = [0.4,0.6,1.0,2.0,4.0]

nbins_reco_addbjets_m = 4
reco_addbjets_m_min = 0
reco_addbjets_m_max = 400
reco_addbjets_m_width = [0.0,60.0,100.0,170.0,400.0]

nbins_gen_addbjets_dr = 3
gen_addbjets_dr_min = 0.4
gen_addbjets_dr_max = 4.0
gen_addbjets_dr_width = [0.4,1.0,2.0,4.0]

nbins_gen_addbjets_m = 4
gen_addbjets_m_min = 0
gen_addbjets_m_max = 400
gen_addbjets_m_width = [0.0,60.0,100.0,170.0,400.0]

nbins_jet_csv = 10
jet_csv_width = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]

varlist = ut.getVarlist()
xlabel = ut.getHistXlabel()

with open('object_selection_config.yml', 'r') as f:
    if '16' in inputDir:
        era = 2016
    elif '17' in inputDir:
        era = 2017
    elif '18' in inputDir:
        era = 2018
    else:
        print "There is no such era ",inputDir
        exit(0)
    obj_selection = yaml.load(f, Loader=yaml.FullLoader)
    muon_ch = 0
    muon_pt = float(obj_selection[era]['muon']['pt'])
    muon_eta = float(obj_selection[era]['muon']['eta'])
    electron_ch = 1
    electron_pt = float(obj_selection[era]['electron']['pt'])
    electron_eta = float(obj_selection[era]['electron']['eta'])
    jet_pt = float(obj_selection[era]['jet']['pt'])
    jet_eta = float(obj_selection[era]['jet']['eta'])
    jet_csv = float(obj_selection[era]['jet']['csv'][obj_selection['bjet']])

listSyst = []
if any(i in process for i in ['Data', 'QCD', 'Driven', 'Nosys']):
    if 'qcdisoup' in process: listSyst.append("__qcdisoup")
    elif 'qcdisodown' in process: listSyst.append("__qcdisodown")
    else: listSyst.append("")
elif "__" in process:
    if "tuneup"      in process: listSyst.append("__tuneup")
    if "tunedown"    in process: listSyst.append("__tunedown")
    if "tunecp5up"   in process: listSyst.append("__tuneup")
    if "tunecp5down" in process: listSyst.append("__tunedown")
    
    if "hdampup"   in process: listSyst.append("__hdampup")
    if "hdampdown" in process: listSyst.append("__hdampdown")
    
    if "isrup"   in process: listSyst.append("__isrup")
    if "isrdown" in process: listSyst.append("__isrdown")
    if "fsrup"   in process: listSyst.append("__fsrup")
    if "fsrdown" in process: listSyst.append("__fsrdown")
    
    if "jerup"   in process: listSyst.append("__jerup")
    if "jerdown" in process: listSyst.append("__jerdown")
    if "jecup"   in process: listSyst.append("__jecup")
    if "jecdown" in process: listSyst.append("__jecdown")
else:
    listSyst += [
        "", "__puup", "__pudown",
        "__muidup", "__muiddown", "__muisoup", "__muisodown", "__mutrgup", "__mutrgdown",
        "__elidup", "__eliddown", "__elrecoup", "__elrecodown", "__elzvtxup", "__elzvtxdown",
        "__eltrgup", "__eltrgdown",
        "__lfup", "__lfdown", "__hfup", "__hfdown",
        "__hfstat1up", "__hfstat1down", "__hfstat2up", "__hfstat2down",
        "__lfstat1up", "__lfstat1down", "__lfstat2up", "__lfstat2down",
        "__cferr1up", "__cferr1down", "__cferr2up", "__cferr2down"]
    if year == 16 or year == 17:
        listSyst += ["__prefireup", "__prefiredown"]
    if any(i in process for i in ["TTLJ", "Bkg"]):
        listSyst += ["__scale0", "__scale1", "__scale2", "__scale3", "__scale4", "__scale5", "__scale6"]
        listSyst += ["__pdf"+str(pdf) for pdf in range(104)]
        
        #if (year == 16) and (not "CP5" in process):
        #    listSyst += ["__pdf"+str(pdf) for pdf in range(102)]
        #else:
        #    listSyst += ["__pdf"+str(pdf) for pdf in range(104)]

dictHist = {}
for syst in listSyst:
    for iChannel in range(nChannel):
        for iStep in range(7,10):
            for i in range(len(varlist)):
                histRange = []
                histRange = ut.getHistRange(varlist[i])
                TH1 = ROOT.TH1D(
                        'h_keras_%s_Ch%d_S%d%s' % (varlist[i], iChannel, iStep, syst), '',
                        int(histRange[0]), float(histRange[1]), float(histRange[2])
                        )
                TH1.GetXaxis().SetTitle(xlabel[varlist[i]])
                TH1.GetYaxis().SetTitle("Entries")
                TH1.Sumw2()
                dictHist[TH1.GetName()] = TH1
            
            TH1 = ROOT.TH1D(
                    'h_keras_nJets_Ch%d_S%d%s' %(iChannel, iStep, syst), '', 4, 6, 10
                    )
            TH1.GetXaxis().SetBinLabel(1,"6")
            TH1.GetXaxis().SetBinLabel(2,"7")
            TH1.GetXaxis().SetBinLabel(3,"8")
            TH1.GetXaxis().SetBinLabel(4,"#geq 9")
            TH1.GetXaxis().SetTitle("Jet multiplicity")
            TH1.GetYaxis().SetTitle("Entries")
            TH1.Sumw2()
            dictHist[TH1.GetName()] = TH1

            if iStep == 7:
                TH1 = ROOT.TH1D(
                    'h_keras_nbJets_Ch%d_S%d%s' % (iChannel, iStep, syst), '', 5, 2, 7
                    )
                TH1.GetXaxis().SetBinLabel(1,"2")
                TH1.GetXaxis().SetBinLabel(2,"3")
                TH1.GetXaxis().SetBinLabel(3,"4")
                TH1.GetXaxis().SetBinLabel(4,"5")
                TH1.GetXaxis().SetBinLabel(5,"#geq 6")
            elif iStep == 8:
                TH1 = ROOT.TH1D(
                    'h_keras_nbJets_Ch%d_S%d%s' % (iChannel, iStep, syst), '', 4, 3, 7
                    )
                TH1.GetXaxis().SetBinLabel(1,"3")
                TH1.GetXaxis().SetBinLabel(2,"4")
                TH1.GetXaxis().SetBinLabel(3,"5")
                TH1.GetXaxis().SetBinLabel(4,"#geq 6")
            elif iStep == 9:
                TH1 = ROOT.TH1D(
                    'h_keras_nbJets_Ch%d_S%d%s' % (iChannel, iStep, syst), '', 3, 4, 7
                    )
                TH1.GetXaxis().SetBinLabel(1,"4")
                TH1.GetXaxis().SetBinLabel(2,"5")
                TH1.GetXaxis().SetBinLabel(3,"#geq 6")
            else:
                print "There is no such step", iStep
                exit(0)
            TH1.GetXaxis().SetTitle("bJet multiplicity")
            TH1.GetYaxis().SetTitle("Entries")
            TH1.Sumw2()
            dictHist[TH1.GetName()] = TH1

            TH1 = ROOT.TH1D(
                    'h_keras_RecoAddbJetDeltaR_Ch%d_S%d%s' % (iChannel, iStep, syst), '',
                    nbins_reco_addbjets_dr, array('d', reco_addbjets_dr_width)
                    )
            TH1.GetXaxis().SetTitle("#DeltaR_{b#bar{b}}")
            TH1.GetYaxis().SetTitle("Entries")
            TH1.Sumw2()
            dictHist[TH1.GetName()] = TH1

            TH1 = ROOT.TH1D(
                    'h_keras_RecoAddbJetInvMass_Ch%d_S%d%s' % (iChannel, iStep, syst), '',
                    nbins_reco_addbjets_m, array('d', reco_addbjets_m_width)
                    )
            TH1.GetXaxis().SetTitle("m_{b#bar{b}}(GeV)")
            TH1.GetYaxis().SetTitle("Entries")
            TH1.Sumw2()
            dictHist[TH1.GetName()] = TH1

            TH1 = ROOT.TH2D(
                    'h_keras_ResponseMatrixDeltaR_Ch%d_S%d%s' % (iChannel, iStep, syst), '',
                    nbins_reco_addbjets_dr, array('d', reco_addbjets_dr_width),
                    nbins_gen_addbjets_dr, array('d', gen_addbjets_dr_width)
                    )
            TH1.GetXaxis().SetTitle("Reco. #DeltaR_{b#bar{b}}")
            TH1.GetYaxis().SetTitle("Gen. #DeltaR_{b#bar{b}}")
            TH1.Sumw2()
            dictHist[TH1.GetName()] = TH1

            TH1 = ROOT.TH2D(
                    'h_keras_ResponseMatrixInvMass_Ch%d_S%d%s' % (iChannel, iStep, syst), '',
                    nbins_reco_addbjets_m, array('d', reco_addbjets_m_width),
                    nbins_gen_addbjets_m, array('d', gen_addbjets_m_width)
                    )
            TH1.GetXaxis().SetTitle("Reco. m_{b#bar{b}}(GeV)")
            TH1.GetYaxis().SetTitle("Gen. m_{b#bar{b}}(GeV)")
            TH1.Sumw2()
            dictHist[TH1.GetName()] = TH1

            TH1 = ROOT.TH3D(
                    'h_keras_3DmatrixDeltaR_Ch%d_S%d%s' % (iChannel, iStep, syst), '',
                    nbins_reco_addbjets_dr, array('d', reco_addbjets_dr_width),
                    nbins_gen_addbjets_dr, array('d', gen_addbjets_dr_width),
                    nbins_jet_csv, array('d', jet_csv_width) 
                    )
            TH1.SetXTitle("Reco. M_{b#bar{b}}")
            TH1.SetYTitle("Gen. M_{b#bar{b}}")
            TH1.SetZTitle("deep CSV")
            TH1.Sumw2();
            dictHist[TH1.GetName()] = TH1

            for i in range(nbins_reco_addbjets_dr):
                TH1 = ROOT.TH1D(
                        "h_keras_RecoDeltaRvsJetCSV_bin%d_Ch%d_S%d%s" % (i, iChannel, iStep, syst),"",
                        nbins_jet_csv, array('d', jet_csv_width) 
                        )
                TH1.SetXTitle("deep CSV")
                TH1.SetYTitle("Entries")
                TH1.Sumw2()
                dictHist[TH1.GetName()] = TH1

            TH1 = ROOT.TH3D(
                    'h_keras_3DmatrixInvMass_Ch%d_S%d%s' % (iChannel, iStep, syst), '',
                    nbins_reco_addbjets_m, array('d', reco_addbjets_m_width),
                    nbins_gen_addbjets_m, array('d', gen_addbjets_m_width),
                    nbins_jet_csv, array('d', jet_csv_width) 
                    )
            TH1.SetXTitle("Reco. M_{b#bar{b}}")
            TH1.SetYTitle("Gen. M_{b#bar{b}}")
            TH1.SetZTitle("deep CSV")
            TH1.Sumw2()
            dictHist[TH1.GetName()] = TH1

            for i in range(nbins_reco_addbjets_m):
                TH1 = ROOT.TH1D(
                        "h_keras_RecoInvMassvsJetCSV_bin%d_Ch%d_S%d%s" % (i, iChannel, iStep, syst),"",
                        nbins_jet_csv, array('d', jet_csv_width) 
                        )
                TH1.SetXTitle("deep CSV")
                TH1.SetYTitle("Entries")
                TH1.Sumw2()
                dictHist[TH1.GetName()] = TH1

selEvent = pd.read_hdf(os.path.join(inputDir,sys.argv[3]))
for index, event in selEvent.iterrows():
    channel = event['channel']
    njets = event['njets']
    nbjets = event['nbjets']
    event_selection = [False, False, False]
    if njets >= 6 and nbjets >= 2: event_selection[0] = True
    if njets >= 6 and nbjets >= 3: event_selection[1] = True
    if njets >= 6 and nbjets >= 4: event_selection[2] = True

    gen_addbjet1 = TLorentzVector()
    gen_addbjet2 = TLorentzVector()
    gen_addbjet1.SetPtEtaPhiE(event['addbjet1_pt'],event['addbjet1_eta'],event['addbjet1_phi'],event['addbjet1_e'])
    gen_addbjet2.SetPtEtaPhiE(event['addbjet2_pt'],event['addbjet2_eta'],event['addbjet2_phi'],event['addbjet2_e'])

    gen_dR = gen_addbjet1.DeltaR(gen_addbjet2)
    gen_M = (gen_addbjet1+gen_addbjet2).M()

    reco_dR = event['bbdR']
    reco_M = event['bbM']

    for sys in listSyst:
        eventweight = 1.0
        bSF = 1.0
        if not 'Data' in process:
            eventweight *= event['genWeight']

            if   'puup'   in sys: eventweight *= event['PUWeight'][1]
            elif 'pudown' in sys: eventweight *= event['PUWeight'][2]
            else                : eventweight *= event['PUWeight'][0]

            if not year == 18:
                if   'prefireup'   in sys: eventweight *= event['prefireweight'][1]
                elif 'prefiredown' in sys: eventweight *= event['prefireweight'][2]
                else                     : eventweight *= event['prefireweight'][0]

            if event['channel'] == 0:
                #[0]~[2]: ID, [3]~[5]: Iso, [6]~[8]: Trigger 
                if   'muidup'    in sys: eventweight *= event['lepton_SF'][1]
                elif 'muisodown' in sys: eventweight *= event['lepton_SF'][2]
                else                   : eventweight *= event['lepton_SF'][0]

                if   'muisoup'   in sys: eventweight *= event['lepton_SF'][4]
                elif 'muisodown' in sys: eventweight *= event['lepton_SF'][5]
                else                   : eventweight *= event['lepton_SF'][3]

                if   'mutrgup'   in sys: eventweight *= event['lepton_SF'][7]
                elif 'mutrgdown' in sys: eventweight *= event['lepton_SF'][8]
                else                   : eventweight *= event['lepton_SF'][6]

            elif event['channel'] == 1:
                #[0]~[2]: ID, [3]~[5]: Reco, [6]~[8]: Zvtx, [9]~[11]: Trigger
                if   'elidup'   in sys: eventweight *= event['lepton_SF'][1]
                elif 'eliddown' in sys: eventweight *= event['lepton_SF'][2]
                else                  : eventweight *= event['lepton_SF'][0]

                if   'elrecoup'   in sys: eventweight *= event['lepton_SF'][4]
                elif 'elrecodown' in sys: eventweight *= event['lepton_SF'][5]
                else                    : eventweight *= event['lepton_SF'][3]

                if   'elzvtxup'   in sys: eventweight *= event['lepton_SF'][7]
                elif 'elzvtxdown' in sys: eventweight *= event['lepton_SF'][8]
                else                    : eventweight *= event['lepton_SF'][6]

                if   'eltrgup'   in sys: eventweight *= event['lepton_SF'][10]
                elif 'eltrgdown' in sys: eventweight *= event['lepton_SF'][11]
                else                   : eventweight *= event['lepton_SF'][9]

            #Scale Weight(ME)
            # [0] = muF up, [1] = muF down, [2] = muR up, [3] = muR up && muF up
            # [4] = muR down, [5] = muF down && muF down
            if   'scale0' in sys: eventweight *= event['scaleweight'][0]
            elif 'scale1' in sys: eventweight *= event['scaleweight'][1]
            elif 'scale2' in sys: eventweight *= event['scaleweight'][2]
            elif 'scale3' in sys: eventweight *= event['scaleweight'][3]
            elif 'scale4' in sys: eventweight *= event['scaleweight'][4]
            elif 'scale5' in sys: eventweight *= event['scaleweight'][5]
            else                : eventweight *= 1.0

            #CSV Shape
            # Systematics for bottom flavor jets:
            #  Light flavor contamination: lf
            #  Linear and quadratic statistical fluctuations: hfstats1 and hfstats2
            # Systematics for light flavor jets:
            #  Heavy flavor contamimation: hf
            #  Linear and quadratic statistical fluctuations: lfstats1 and lfstats2
            # Systematics for charm flavor jets:
            #  Linear and quadratic uncertainties: cferr1 and cferr2
            if   'lfup'        in sys: bSF *= event['jet_SF_CSV_30'][3]
            elif 'lfdown'      in sys: bSF *= event['jet_SF_CSV_30'][4]
            elif 'hfup'        in sys: bSF *= event['jet_SF_CSV_30'][5]
            elif 'hfdown'      in sys: bSF *= event['jet_SF_CSV_30'][6]
            elif 'hfstat1up'   in sys: bSF *= event['jet_SF_CSV_30'][7]
            elif 'hfstat1down' in sys: bSF *= event['jet_SF_CSV_30'][8]
            elif 'hfstat2up'   in sys: bSF *= event['jet_SF_CSV_30'][9]
            elif 'hfstat2down' in sys: bSF *= event['jet_SF_CSV_30'][10]
            elif 'lfstat1up'   in sys: bSF *= event['jet_SF_CSV_30'][11]
            elif 'lfstat1down' in sys: bSF *= event['jet_SF_CSV_30'][12]
            elif 'lfstat2up'   in sys: bSF *= event['jet_SF_CSV_30'][13]
            elif 'lfstat2down' in sys: bSF *= event['jet_SF_CSV_30'][14]
            elif 'cferr1up'    in sys: bSF *= event['jet_SF_CSV_30'][15]
            elif 'cferr1down'  in sys: bSF *= event['jet_SF_CSV_30'][16]
            elif 'cferr2up'    in sys: bSF *= event['jet_SF_CSV_30'][17]
            elif 'cferr2down'  in sys: bSF *= event['jet_SF_CSV_30'][18]
            else                     : bSF *= event['jet_SF_CSV_30'][0]

            #Parton Shower
            if (not year == 16) or ("CP5" in process):
                if   'isrup'   in sys: eventweight *= event['psweight'][0]
                elif 'isrdown' in sys: eventweight *= event['psweight'][2]
                elif 'fsrup'   in sys: eventweight *= event['psweight'][1]
                elif 'fsrdown' in sys: eventweight *= event['psweight'][3]
                else                 : eventweight *= 1.0

            #PDF Uncertainties
            if 'pdf' in sys:
                pdfnum = int(sys.replace('__pdf',''))
                eventweight *= event['pdfweight'][pdfnum]

        dRregion = 999
        Mregion = 999
        reco_addbjets_dr_width = [0.4,0.6,1.0,2.0,4.0]
        reco_addbjets_m_width = [0.0,60.0,100.0,170.0,400.0]
        for i in range(0, len(reco_addbjets_dr_width)-1):
            if reco_dR >= reco_addbjets_dr_width[i] and reco_dR < reco_addbjets_dr_width[i+1]: dRregion = i
            if reco_dR > reco_addbjets_dr_width[len(reco_addbjets_dr_width)-1]: dRregion = len(reco_addbjets_dr_width)-2
        for i in range(0, len(reco_addbjets_m_width)-1):
            if reco_M >= reco_addbjets_m_width[i] and reco_M < reco_addbjets_m_width[i+1]: Mregion = i
            if reco_M > reco_addbjets_m_width[len(reco_addbjets_m_width)-1]: Mregion = len(reco_addbjets_m_width)-2
        
        for istep in range(7,10):
            if not event_selection[istep-7]: continue
            for item in varlist:
                dictHist['h_keras_%s_Ch%d_S%d%s'%(item, channel, istep, sys)].Fill(event[item], bSF*eventweight)
            dictHist['h_keras_nJets_Ch%d_S%d%s'%(channel, istep, sys)].Fill(njets, bSF*eventweight)
            dictHist['h_keras_nbJets_Ch%d_S%d%s'%(channel, istep, sys)].Fill(nbjets, bSF*eventweight)
            dictHist['h_keras_RecoAddbJetDeltaR_Ch%d_S%d%s'%(channel, istep, sys)].Fill(reco_dR, bSF*eventweight)
            dictHist['h_keras_RecoAddbJetInvMass_Ch%d_S%d%s'%(channel, istep, sys)].Fill(reco_M, bSF*eventweight)
            dictHist['h_keras_ResponseMatrixDeltaR_Ch%d_S%d%s'%(channel, istep, sys)].Fill(reco_dR, gen_dR, bSF*eventweight)
            dictHist['h_keras_ResponseMatrixInvMass_Ch%d_S%d%s'%(channel, istep, sys)].Fill(reco_M, gen_M, bSF*eventweight)
            dictHist['h_keras_3DmatrixDeltaR_Ch%d_S%d%s'%(channel, istep, sys)].Fill(reco_dR, gen_dR, event['b1CSV'], bSF*eventweight)
            dictHist['h_keras_3DmatrixInvMass_Ch%d_S%d%s'%(channel, istep, sys)].Fill(reco_M, gen_M, event['b1CSV'], bSF*eventweight)
            if dRregion is not 999: dictHist['h_keras_RecoDeltaRvsJetCSV_bin%d_Ch%d_S%d%s'%(dRregion, channel, istep, sys)].Fill(event['b1CSV'], bSF*eventweight)
            if Mregion is not 999: dictHist['h_keras_RecoInvMassvsJetCSV_bin%d_Ch%d_S%d%s'%(Mregion, channel, istep, sys)].Fill(event['b1CSV'], bSF*eventweight)
            if channel == 0 or channel == 1:
                for item in varlist:
                    dictHist['h_keras_%s_Ch2_S%d%s'%(item, istep, sys)].Fill(event[item], bSF*eventweight)
                dictHist['h_keras_nJets_Ch2_S%d%s'%(istep, sys)].Fill(njets, bSF*eventweight)
                dictHist['h_keras_nbJets_Ch2_S%d%s'%(istep, sys)].Fill(nbjets, bSF*eventweight)
                dictHist['h_keras_RecoAddbJetDeltaR_Ch2_S%d%s'%(istep, sys)].Fill(reco_dR, bSF*eventweight)
                dictHist['h_keras_RecoAddbJetInvMass_Ch2_S%d%s'%(istep, sys)].Fill(reco_M, bSF*eventweight)
                dictHist['h_keras_ResponseMatrixDeltaR_Ch2_S%d%s'%(istep, sys)].Fill(reco_dR, gen_dR, bSF*eventweight)
                dictHist['h_keras_ResponseMatrixInvMass_Ch2_S%d%s'%(istep, sys)].Fill(reco_M, gen_M, bSF*eventweight)
                dictHist['h_keras_3DmatrixDeltaR_Ch2_S%d%s'%(istep, sys)].Fill(reco_dR, gen_dR, event['b1CSV'], bSF*eventweight)
                dictHist['h_keras_3DmatrixInvMass_Ch2_S%d%s'%(istep, sys)].Fill(reco_M, gen_M, event['b1CSV'], bSF*eventweight)
                if dRregion is not 999: dictHist['h_keras_RecoDeltaRvsJetCSV_bin%d_Ch2_S%d%s'%(dRregion, istep, sys)].Fill(event['b1CSV'], bSF*eventweight)
                if Mregion is not 999: dictHist['h_keras_RecoInvMassvsJetCSV_bin%d_Ch2_S%d%s'%(Mregion, istep, sys)].Fill(event['b1CSV'], bSF*eventweight)

f_out.Write()
f_out.Close()
