import math
import os

from ROOT import *
import ROOT

def calError(h_nom, h_sys, delta=True):
    error = []
    h_delta = h_sys.Clone()
    if not delta:
        for ibin in range(1, h_nom.GetNbinsX()+1):
            value = h_sys.GetBinContent(ibin) - h_nom.GetBinContent(ibin)
            h_delta.SetBinContent(ibin, value)

    for ibin in range(1,h_nom.GetNbinsX()+1):
        err = 0.0
        if h_nom.GetBinContent(ibin) > 0.0:
            err = (h_delta.GetBinContent(ibin)/h_nom.GetBinContent(ibin))*100
	error.append(err)

    return error

def drawHist(h_nom, h_sys_up, h_sys_down):
    style = TStyle("","")
    style.SetOptStat(0)

    sysname = (h_sys_up.GetName()).split('__')[1]
    outname = h_nom.GetName()+'__'+sysname[:-2]
    if 'Background' in h_sys_up.GetName(): outname = 'Background'+outname
    if 'DeltaSysSource' in h_sys_up.GetName(): outname = 'Matrix'+outname
    if 'Acceptance' in h_sys_up.GetName(): outname = 'Acceptance'+outname

    if 'DeltaR' in h_nom.GetName():
        h_nom.SetXTitle("#DeltaR_{b#bar{b}}")
        h_nom.SetYTitle("#frac{d#sigma^{full}}{d#DeltaR}[pb]")
    if 'InvMass' in h_nom.GetName():
        h_nom.SetXTitle("M_{b#bar{b}}(GeV)")
        h_nom.SetYTitle("#frac{d#sigma^{full}}{dM}[pb/GeV]")
        #h_nom.GetXaxis().SetTitleOffset(0.2)
        h_nom.GetYaxis().SetLabelSize(0.03)

    h_nom.GetYaxis().SetTitleSize(0.045)
    h_nom.GetYaxis().SetTitleOffset(1.6)


    c = TCanvas("","",800,800)
    leg = TLegend(0.40,0.70,0.89,0.87)
    leg.SetHeader(sysname[:-2])
    leg.AddEntry(h_nom, "Central", "p")
    leg.AddEntry(h_sys_up, "Sys up", "l")
    leg.AddEntry(h_sys_down, "Sys down", "l")

    style.cd()
    h_sys_up.SetLineColor(kRed)
    h_sys_down.SetLineColor(kBlue)
    h_nom.SetMinimum(0)
    h_nom.SetMaximum(h_sys_up.GetMaximum()*2.0)
    h_nom.Draw("axis")
    h_sys_up.Draw("hist same")
    h_sys_down.Draw("hist same")
    h_nom.Draw("p same")
    leg.Draw("same")

    if not os.path.exists('../output/unfold/syst/'):
        os.mkdir('../output/unfold/syst')
    c.Print('../output/unfold/syst/'+outname+'.pdf', "pdf")

f_err = open('../output/unfold/syst_errors.tex', 'w')
f_list = []
f_list.append(TFile.Open("../output/unfold/hist_unfolded_hist_DataSingleMu.root"))
f_list.append(TFile.Open("../output/unfold/hist_unfolded_hist_DataSingleEl.root"))
syst_list = [
    "__jer", "__jec",
    "__musf", "__mutrg",
    "__elsf", "__eltrg",
    "__lf", "__hf",
    "__hfstat1", "__hfstat2",
    "__lfstat1", "__lfstat2",
    "__cferr1",  "__cferr2",
    "__pu",
    "__ps", "__sw",
    "__hdamp", "__tune"
]
syst_lep  = ["__musf", "__mutrg", "__elsf", "__eltrg"]
syst_btag = [
    "__lf", "__hf", "__hfstat1", "__hfstat2",
    "__lfstat1", "__lfstat2", "__cferr1", "__cferr2"
]
genmode = "mindR"
histlist = ["RecoAddbJetDeltaR", "RecoAddbJetInvMass", "RecoAddbJetDeltaPhi", "RecoAddbJetDeltaEta"] 
f_err.write('\\documentclass[a4paper]{report}\n')
f_err.write('\\begin{document}\n')

for f_in in f_list:
    ich = 999
    if   "Mu" in f_in.GetName(): ich = 0
    elif "El" in f_in.GetName(): ich = 1
    f_err.write('%'+f_in.GetName()+'\n')
    f_err.write('% Channel: '+str(ich)+'\n')
    for hist in histlist:
        # Calculate Matrix Uncertainties
        histname = "diffXsec_Unfolded_h_"+genmode+"_"+hist+"_Ch"+str(ich)+"_S3"
	print(histname)
        h_nom = f_in.Get(histname)
        binnum = h_nom.GetNbinsX()
	sys_tot_sqaure = [0 for i in range(binnum)]
	row = 'c'
	for i in range(binnum): row += 'c'
	tmpname = hist.replace('_',' ')
	f_err.write('\\begin{table}\n')
	f_err.write('    \\caption{'+tmpname+'}\n')
	f_err.write('    \\begin{flushleft}\n')
	f_err.write('        \\begin{tabular}{'+row+'}\n')
	f_err.write('            \\hline\\hline\n')
	col = ''
	for i in range(binnum): col += ' & '+str(i+1)+' bin'
	f_err.write('            Source '+col+'\\\\\n')
	f_err.write('            \\hline\n')
	f_err.write('            \multicolumn{'+str(binnum+1)+'}{l}{Matrix uncertainties}\\\\\n')
        syst_errors = {}
        for sys in syst_list:
            if "ps" in sys or "sw" in sys or "hdamp" in sys or "tune" in sys: continue
            histname = "diffXsec_h_"+genmode+"_"+hist+"_Ch"+str(ich)+"_S3_DeltaSysSource"+sys
            if 'Ch0' in hist and 'el' in sys: continue
            elif 'Ch1' in hist and 'mu' in sys: continue
            
	    errors = []
            drawHist(h_nom, f_in.Get(histname+'up'), f_in.Get(histname+'down'))
            err_up = calError(h_nom,f_in.Get(histname+'up'))
            err_down = calError(h_nom, f_in.Get(histname+'down'))
            for index2, up in enumerate(err_up):
                tmp_e = max(abs(up), abs(err_down[index2]))
                errors.append(tmp_e)
                sys_tot_sqaure[index2] = pow(tmp_e,2)
            syst_errors[sys] = errors
        
	err_btag = []
        str_btag = ''
	for idx, value in enumerate(syst_errors[syst_btag[0]]):
            tmp_esquare = pow(value, 2)
	    for idx2, value in enumerate(syst_btag):
	        if idx2 == 0: continue
		tmp_esquare += pow(syst_errors[value][idx], 2)
	    err_btag.append(math.sqrt(tmp_esquare))
        for i in err_btag: str_btag += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
        f_err.write('            bTag'+str_btag+'\\\\\n')

	err_lep = []
        str_lep = ''
	for idx, value in enumerate(syst_errors[syst_lep[0]]):
            tmp_esquare = pow(value, 2)
	    for idx2, value in enumerate(syst_lep):
	        if idx2 == 0: continue
		tmp_esquare += pow(syst_errors[value][idx], 2)
	    err_lep.append(math.sqrt(tmp_esquare))
        for i in err_lep: str_lep += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
        f_err.write('            lepton'+str_lep+'\\\\\n')

        for key, value in syst_errors.items():
            tmp = ''
            for i in value: tmp += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
            tmpkey = key.replace('__','')
            if not key in syst_btag: continue
            #if key in syst_lep: continue
            f_err.write('            '+tmpkey+tmp+'\\\\\n')
        
	# Calculate Acceptance Uncertainties
	f_err.write('            \\hline\n')
	f_err.write('            \multicolumn{'+str(binnum+1)+'}{l}{Acceptance uncertainties}\\\\\n')
        syst_errors = {}
        for sys in syst_list:
            histname = "diffXsec_Unfolded_h_"+genmode+"_"+hist+"_Ch"+str(ich)+"_S3_Acceptance"+sys
            if 'Ch0' in hist and 'el' in sys: continue
            elif 'Ch1' in hist and 'mu' in sys: continue
            errors = []
            drawHist(h_nom, f_in.Get(histname+'up'), f_in.Get(histname+'down'))
            err_up = calError(h_nom,f_in.Get(histname+'up'), False)
            err_down = calError(h_nom, f_in.Get(histname+'down'), False)
            for index2, up in enumerate(err_up):
                tmp_e = max(abs(up), abs(err_down[index2]))
                errors.append(tmp_e)
                sys_tot_sqaure[index2] += pow(tmp_e,2)
            syst_errors[sys] = errors
        
	err_btag = []
        str_btag = ''
	for idx, value in enumerate(syst_errors[syst_btag[0]]):
            tmp_esquare = pow(value, 2)
	    for idx2, value in enumerate(syst_btag):
	        if idx2 == 0: continue
		tmp_esquare += pow(syst_errors[value][idx], 2)
	    err_btag.append(math.sqrt(tmp_esquare))
        for i in err_btag: str_btag += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
        f_err.write('            bTag'+str_btag+'\\\\\n')

	err_lep = []
        str_lep = ''
	for idx, value in enumerate(syst_errors[syst_lep[0]]):
            tmp_esquare = pow(value, 2)
	    for idx2, value in enumerate(syst_lep):
	        if idx2 == 0: continue
		tmp_esquare += pow(syst_errors[value][idx], 2)
	    err_lep.append(math.sqrt(tmp_esquare))
        for i in err_lep: str_lep += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
        f_err.write('            lepton'+str_lep+'\\\\\n')

        for key, value in syst_errors.items():
            tmp = ''
            for i in value: tmp += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
            tmpkey = key.replace('__','')
            if not key in syst_btag: continue
            #if key in syst_lep: continue
            f_err.write('            '+tmpkey+tmp+'\\\\\n')

        # Calculate Background Uncertainties
	f_err.write('            \\hline\n')
	f_err.write('            \multicolumn{'+str(binnum+1)+'}{l}{Background uncertainties}\\\\\n')
        syst_errors = {}
        for sys in syst_list:
            histname = "diffXsec_Unfolded_h_"+genmode+"_"+hist+"_Ch"+str(ich)+"_S3_Background"+sys
            if 'Ch0' in hist and 'el' in sys: continue
            elif 'Ch1' in hist and 'mu' in sys: continue
            errors = []
            drawHist(h_nom, f_in.Get(histname+'up'), f_in.Get(histname+'down'))
            err_up = calError(h_nom,f_in.Get(histname+'up'), False)
            err_down = calError(h_nom, f_in.Get(histname+'down'), False)
            for index2, up in enumerate(err_up):
                tmp_e = max(abs(up), abs(err_down[index2]))
                errors.append(tmp_e)
                sys_tot_sqaure[index2] += pow(tmp_e,2)
            syst_errors[sys] = errors
        
	err_btag = []
        str_btag = ''
	for idx, value in enumerate(syst_errors[syst_btag[0]]):
            tmp_esquare = pow(value, 2)
	    for idx2, value in enumerate(syst_btag):
	        if idx2 == 0: continue
		tmp_esquare += pow(syst_errors[value][idx], 2)
	    err_btag.append(math.sqrt(tmp_esquare))
        for i in err_btag: str_btag += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
        f_err.write('            bTag'+str_btag+'\\\\\n')

	err_lep = []
        str_lep = ''
	for idx, value in enumerate(syst_errors[syst_lep[0]]):
            tmp_esquare = pow(value, 2)
	    for idx2, value in enumerate(syst_lep):
	        if idx2 == 0: continue
		tmp_esquare += pow(syst_errors[value][idx], 2)
	    err_lep.append(math.sqrt(tmp_esquare))
        for i in err_lep: str_lep += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
        f_err.write('            lepton'+str_lep+'\\\\\n')

        for key, value in syst_errors.items():
            tmp = ''
            for i in value: tmp += ' & $\\pm$'+str(format(i,'.3f')) + '\\%'
            tmpkey = key.replace('__','')
            if not key in syst_btag: continue
            #if key in syst_lep: continue
            f_err.write('            '+tmpkey+tmp+'\\\\\n')

        # Write total systematic uncertainties
        tmp2 = ''
	for value in sys_tot_sqaure:
            tmp2 += ' & $\\pm$' + str(format(math.sqrt(value),'.3f')) + '\\%'
	f_err.write('            \\hline\n')
	f_err.write('            Total sys. unc.'+tmp2+'\\\\\n')
        f_err.write('            \\hline\\hline\n')
	f_err.write('        \\end{tabular}\n')
	f_err.write('    \\end{flushleft}\n')
	f_err.write('\\end{table}\n')
f_err.write('\\end{document}\n')
f_err.close()


