import os, sys
import math
from array import array
from ROOT import *

def makeInputHists(*args):
    print 'Make unfold input from postfit ditritubions'
    inputDir = args[0]
    outputDir = args[1]
    discriminant = args[2]
    group = args[3]
    recoMode = args[4]

    nbinsDR = -999
    nbinsM = -999
    widthDR = []
    widthM = []
    with open('macro/histBook.h', 'r') as f:
        getNbinsDR = False
        getNbinsM = False
        getWidthDR = False
        getWidthM = False
        while True:
            line = f.readline()
            if not line: break
            if 'nbins_reco_addbjets_dR' in line and getNbinsDR == False:
                tmp = line.split('=')
                tmp = tmp[-1].replace(';','')
                nbinsDR = int(tmp)
                getNbinsDR = True
            if 'reco_addbjets_dR_width' in line and getWidthDR == False:
                tmp = line.split('=')
                tmp = tmp[-1].replace('{','')
                tmp = tmp.replace('}','')
                tmp = tmp.replace(';','')
                tmp = tmp.replace(' ','')
                tmp = tmp.split(',')
                for value in tmp:
                    widthDR.append(float(value))
                getWidthDR = True
            if 'nbins_reco_addbjets_M' in line and getNbinsM == False:
                tmp = line.split('=')
                tmp = tmp[-1].replace(';','')
                nbinsM = int(tmp)
                getNbinsM = True
            if 'reco_addbjets_M_width' in line and getWidthM == False:
                tmp = line.split('=')
                tmp = tmp[-1].replace('{','')
                tmp = tmp.replace('}','')
                tmp = tmp.replace(';','')
                tmp = tmp.replace(' ','')
                tmp = tmp.split(',')
                for value in tmp:
                    widthM.append(float(value))
                getWidthM = True
            if getNbinsDR and getNbinsM and getWidthDR and getWidthM: break

    f_out = TFile.Open(outputDir+'/hist_input.root','recreate')

    systList = ['','__postfitup','__postfitdown']
    for process in group:
        f_tmp = TFile.Open(inputDir+'/'+process+'_postfit_histos.root')
        for syst in systList:
            if 'data' in process and syst != '': continue
            h_post = f_tmp.Get(discriminant+syst)
            h_dR = TH1D('h_'+recoMode+'_RecoAddbJetDeltaR_Ch2_S3_'+process+syst,'',nbinsDR, array('d', widthDR))
            h_dR.SetXTitle('#DeltaR_{b#bar{b}}')
            h_dR.SetYTitle('Entries')
            h_dR.Sumw2()
            h_M = TH1D('h_'+recoMode+'_RecoAddbJetInvMass_Ch2_S3_'+process+syst,'',nbinsM, array('d', widthM))
            h_M.SetXTitle('M_{b#bar{b}}(GeV)')
            h_M.SetYTitle('Entries')
            h_M.Sumw2()

            for ibin in range(1,nbinsDR+1):
                value = 0.0
                sqrEr = 0.0
                for jbin in range(nbinsM):
                    value += h_post.GetBinContent(1+(ibin-1)*8+jbin)
                    sqrEr += pow(h_post.GetBinError(1+(ibin-1)*8+jbin),2)
                h_dR.SetBinContent(ibin, value)
                h_dR.SetBinError(ibin, math.sqrt(sqrEr))

            for ibin in range(1,nbinsM+1):
                value = 0.0
                sqrEr = 0.0
                for jbin in range(nbinsDR):
                    value += h_post.GetBinContent(ibin+jbin*8)
                    sqrEr += pow(h_post.GetBinError(ibin+jbin*8),2)
                h_M.SetBinContent(ibin, value)
                h_M.SetBinError(ibin, math.sqrt(sqrEr))

            f_out.cd()
            h_dR.Write()
            h_M.Write()
        f_tmp.Close()

    f_out.Close()
    print 'Postfit distributions are saved successfully in '+str(outputDir)

def extractMatrix(*args):
    print 'Merge response matrix and MC input'
    inputDir = args[0]
    outputDir = args[1]
    year = int(args[2])
    ttbb = args[3]
    matrix = args[4]
    recoMode = args[5]
    genMode = args[6]

    if year == 16 or year == 2016: lumi = 35922
    if year == 17 or year == 2017: lumi = 41529
    if year == 18 or year == 2018: lumi = 59693
    with open('samples/xsec'+str(year)+'.txt', 'r') as f:
        while True:
            line = f.readline()
            if not line: break
            tmp = line.split(' ')
            if ttbb in line:
                ttbbXsec = float(tmp[1])
            if matrix in line:
                preXsec = float(tmp[1])
    with open('samples/genevt'+str(year)+'.txt', 'r') as f:
        while True:
            line = f.readline()
            if not line: break
            tmp = line.split(' ')
            if ttbb in line:
                ttbbGenEvts = float(tmp[1])
            if matrix in line:
                preGenEvts = float(tmp[1])

    f_gen = TFile.Open(inputDir+'/hist_gen.root')
    f_ttbb = TFile.Open(inputDir+'/hist_'+ttbb+'.root')
    print inputDir+'/hist_'+ttbb+'.root'
    f_postfit = TFile.Open(outputDir+'/hist_input.root')
    f_matrix = TFile.Open(inputDir+'/hist_'+matrix+'.root')

    f_out = TFile.Open(outputDir+'/hist_matrix.root', 'recreate')
    f_out.cd()
    
    variables = ['DeltaR', 'InvMass']
    systList = ['',
        '__swup', '__swdown', '__psup', '__psdown',
        '__tuneup', '__tunedown', '__hdampup', '__hdampdown',
        '__pdfup', '__pdfdown',
        '__jerup', '__jerdown', '__jecup', '__jecdown',
        '__mutrgup', '__mutrgdown',
        '__eltrgup', '__eltrgdown',
        '__lfup', '__lfdown', '__hfup', '__hfdown',
        '__hfstat1up','__hfstat1down', '__hfstat2up', '__hfstat2down',
        '__lfstat1up','__lfstat1down', '__lfstat2up', '__lfstat2down',
        '__cferr1up', '__cferr1down',  '__cferr2up',  '__cferr2down',
        '__puup', '__pudown'
        ]
    if year == 16 or year == 2016:
        systList.extend(['__musfup','__musfdown','__elsfup','__elsfdown'])
    else:
        systList.extend(['__muidup','__muiddown','__muisoup','__muisodown',
            '__elidup','__eliddown','__elrecoup','__elrecodown',
            '__elzvtxup','__elzvtxdown'])
    if year == 17 or year == 2017:
        systList.extend(['__prefireup','__prefiredown'])

    for vari in variables: 
        h_prefit = f_matrix.Get('h_'+recoMode+'_RecoAddbJet'+vari+'_Ch2_S3')
        h_prefit.Scale(lumi*preXsec/preGenEvts)
        
        h_postfit = f_postfit.Get('h_'+recoMode+'_RecoAddbJet'+vari+'_Ch2_S3_ttbb')
        
        h_full = f_gen.Get('h_'+genMode+'_GenAddbJet'+vari+'_Ch2_nosel')
        h_full.Scale(lumi*preXsec/preGenEvts)
        if ttbb != matrix:
            h_mc = f_ttbb.Get('h_'+recoMode+'_RecoAddbJet'+vari+'_Ch2_S3')
            h_mc.Scale(lumi*ttbbXsec/ttbbGenEvts)
            h_gen = f_ttbb.Get('h_'+genMode+'_GenAddbJet'+vari+'_Ch2_S3')
            h_gen.Scale(lumi*ttbbXsec/ttbbGenEvts)
        else:
            h_mc = f_ttbb.Get('h_'+recoMode+'_RecoAddbJet'+vari+'2_Ch2_S3')
            h_mc.Scale(lumi*ttbbXsec/ttbbGenEvts)
            h_gen = f_ttbb.Get('h_'+genMode+'_GenAddbJet'+vari+'2_Ch2_S3')
            h_gen.Scale(lumi*ttbbXsec/ttbbGenEvts)
        h_gen.SetName('h_'+genMode+'_GenAddbJet'+vari+'_Ch2_S3')
        
        h_ratio = h_postfit.Clone()
        h_ratio.Divide(h_prefit)

        h_mc.SetName(h_postfit.GetName()+'_closure')
        h_prefit.SetName(h_prefit.GetName()+'_prefit')
        h_postfit.SetName(h_postfit.GetName()+'_postfit')
        h_ratio.SetName(h_ratio.GetName()+'_fitRatio')

        for syst in systList:
            if ttbb != matrix:
                h2_mat_prefit = f_matrix.Get('h_'+genMode+'_ResponseMatrix'+vari+'_Ch2_S3'+syst)
            else:
                h2_mat_prefit = f_matrix.Get('h_'+genMode+'_ResponseMatrix'+vari+'2_Ch2_S3'+syst)

            h2_mat_postfit = h2_mat_prefit.Clone()
            for iybin in range(1,h2_mat_prefit.GetNbinsY()+1):
                for ixbin in range(1,h2_mat_prefit.GetNbinsX()+1):
                    value = h2_mat_prefit.GetBinContent(ixbin, iybin)*h_ratio.GetBinContent(ixbin) 
                    error = h2_mat_prefit.GetBinError(ixbin, iybin)*h_ratio.GetBinContent(ixbin)
                    h2_mat_postfit.SetBinContent(ixbin, iybin, value)
                    h2_mat_postfit.SetBinError(ixbin, iybin, error)

            h2_mat_prefit.SetName('h_'+genMode+'_ResponseMatrix'+vari+'_Ch2_S3_prefit'+syst)
            h2_mat_postfit.SetName('h_'+genMode+'_ResponseMatrix'+vari+'_Ch2_S3_postfit'+syst)

            h2_mat_prefit.Write()
            h2_mat_postfit.Write()

        h_gen.Write()
        h_full.Write()
        h_ratio.Write()
        h_mc.Write()
        h_prefit.Write()
        h_postfit.Write()       

    f_gen.Close()
    f_ttbb.Close()
    f_postfit.Close()
    f_matrix.Close()
    f_out.Close()

    print 'Response matrix and MC input are saved successfully in '+str(outputDir)

def unfoldPreProcess(**kwargs):
    prefitDir = kwargs['prefitDir']
    postfitDir = kwargs['postfitDir']
    outputDir = kwargs['outputDir']
    discriminant = kwargs['discriminant']
    group = kwargs['group']
    year = float(kwargs['year'])
    ttbb = kwargs['ttbb']
    matrix = kwargs['matrix']
    recoMode = kwargs['recoMode']
    genMode = kwargs['genMode']
    
    makeInputHists(postfitDir, outputDir, discriminant, group, recoMode)
    extractMatrix(prefitDir, outputDir, year, ttbb, matrix, recoMode, genMode)
