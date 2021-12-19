import math
from ROOT import *
import tdrstyle
                
bRatio = 0.436572

def calculateDiffXsec(lumi, h_in, h_accept):
    h_out = h_in.Clone()

    for ibin in range(1, h_in.GetNbinsX()+1):
        binWidth = h_in.GetXaxis().GetBinWidth(ibin)
        diffXsec = h_in.GetBinContent(ibin)/(h_accept.GetBinContent(ibin)*float(binWidth)*float(lumi)*float(bRatio))
        h_out.SetBinContent(ibin, diffXsec)

    return h_out

def buildGraphFromHist(h_in):
    grp = TGraphErrors()

    for ibin in range(1,h_in.GetNbinsX()+1):
        w = h_in.GetXaxis().GetBinWidth(ibin)
        y = h_in.GetBinContent(ibin)
        err = h_in.GetBinError(ibin)
        if y < 0.0:
            y = 0.0
        grp.SetPoint(ibin-1, h_in.GetBinCenter(ibin), y)
        grp.SetPointError(ibin-1, 0.0, err)

    grp.SetEditable(False)

    return grp

def drawHist(outputDir, lumi, inFile, recoMode='mindR', genMode='mindR'):
    tdrstyle.setTDRStyle()

    gStyle.SetHatchesSpacing(1)
    gStyle.SetHatchesLineWidth(1)

    gStyle.SetPaintTextFormat("4.1f")
    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)

    f_in = TFile.Open(outputDir+'/'+inFile)
    
    hist_list = [x.GetName() for x in f_in.GetListOfKeys()]
    
    canvas = TCanvas('','',800,800)
    color = TColor()
    legend = TLegend(0.6,0.7,0.88,0.88)
    labelCMS = tdrstyle.tdrCMSlabel(float(lumi)) 
    labelSim = tdrstyle.tdrCMSSimlabel()

    for hist in hist_list:
        h_in = f_in.Get(hist)

        canvas.cd()
        if 'Bin' in hist:
            if '__' in hist: continue
            h_in.Scale(100)
            h_err = h_in.Clone()
            if 'Acceptance' in h_in.GetName():
                h_in.GetYaxis().SetTitle('Acceptance(%)')
                h_in.SetMinimum(0.0)
                h_in.SetMaximum(h_in.GetMaximum()*1.3)
            elif 'Purity' in h_in.GetName():
                h_in.GetYaxis().SetTitle('Purity(%)')
                h_in.SetMinimum(0.0)
                h_in.SetMaximum(100.0)
            elif 'Stability' in h_in.GetName():
                h_in.GetYaxis().SetTitle('Stability(%)')
                h_in.SetMinimum(0.0)
                h_in.SetMaximum(100.0)

            h_in.GetYaxis().SetTitleOffset(1.3)
            h_in.GetXaxis().SetTitleOffset(1.2)
            h_in.SetLineWidth(2)
            h_in.SetLineColor(kBlue)
            h_in.Draw('hist')
            if 'Acceptance' in h_in.GetName():
                h_err.SetFillStyle(3154)
                h_err.SetFillColor(color.GetColor('#ee556270'))
                h_err.Draw('e2 same')
            labelSim.Draw('same')
        elif h_in.InheritsFrom(TH2.Class()):
            if 'Emat' in h_in.GetName():
                h_in.Draw('colz text')
            else:
                h_in.Draw('box')
            labelSim.Draw('same')
        elif '__' in h_in.GetName() and h_in.InheritsFrom(TH1.Class()):
            continue
        else:
            if 'Gen' in h_in.GetName() or 'Input' in h_in.GetName():
                continue

            grp = buildGraphFromHist(h_in)
            grp.SetMarkerSize(1.5)
            genName = h_in.GetName()
            genName = genName.replace('Unfolded_', '')
            genName = genName.replace('Reco', 'Gen')
            if 'S3_data_obs' in h_in.GetName():
                genName = genName.replace('S3_data_obs', 'nosel')
            if 'ttbb_closure' in h_in.GetName():
                genName = genName.replace('_ttbb_closure', '')

            h_gen = f_in.Get(genName)
            h_gen.SetLineColor(color.GetColor('#cc0000'))
            h_gen.SetLineWidth(2)

            h_genErr = h_gen.Clone()
            h_genErr.SetFillColor(color.GetColor('#556270'))
            h_genErr.SetFillStyle(3154)
            
            if 'DiffXsec' in h_in.GetName():
                if 'DeltaR' in h_in.GetName():
                    h_gen.GetYaxis().SetTitle('#frac{d#sigma}{d#DeltaR_{b#bar{b}}}[pb]')
                else:
                    h_gen.GetYaxis().SetTitle('#frac{d#sigma}{dm_{b#bar{b}}}[pb/GeV]')
                h_gen.GetYaxis().SetTitleOffset(2.0)
            else:
                h_gen.GetYaxis().SetTitle('Number of events')
            h_gen.SetMaximum(h_in.GetMaximum()*1.8)

            if 'closure' in h_in.GetName():
                legend.AddEntry(grp, 'ttbb Reco MC', 'p')
                label = labelSim
            else:
                legend.AddEntry(grp, 'Data', 'p')
                label = labelCMS

            legend.AddEntry(h_gen, 'ttbb Powheg Pythia', 'l')

            h_gen.Draw('hist')
            grp.Draw('p e same')
            legend.Draw('same')
            label.Draw('same')
        
        canvas.Print(outputDir+'/'+h_in.GetName()+'.pdf','pdf')
        canvas.Clear()
        legend.Clear()

def drawTable(year, outputDir, lumi, inFile, recoMode='mindR', genMode='mindR'):
    f_in = TFile.Open(outputDir+'/'+inFile)
    f_accept = TFile.Open(outputDir+'/hist_accept.root')
    histList = ['h_'+recoMode+'_RecoAddbJetDeltaR_Ch2_S3','h_'+recoMode+'_RecoAddbJetInvMass_Ch2_S3']
    niceSystName = {
            'pu':'PileUp','lf':'Light flavour','hf':'Heavy flavour',
            'sw':'Matrix Element','ps':'Parton Shower','hdamp':'ME & PS Matching','tune':'Pythia Tune',
            'pdf':'PDF'
            }
    systCategories = {
            'Muon':[],'Electron':[],
            'bTag':['lf','hf','hfstat1','hfstat2','lfstat1','lfstat2','cferr1','cferr2'],
            'Experiment':['pu','jer','jec'],
            'Theory':['sw','ps','tune','hdamp','pdf'],
            }
    
    lumiUnc = '      & Luminosity & \\multicolumn{4}{|c|}{0.0}'
    if year == 16:
        systCategories['Muon'].extend(['musf','mutrg'])
        systCategories['Electron'].extend(['elsf','eltrg'])
    elif year == 17 or year == 18:
        systCategories['Muon'].extend(['muid','muiso','mutrg'])
        systCategories['Electron'].extend(['elid','elreco','elzvtx','eltrg'])
    else:
        print "Wrong year"
        exit()

    for hist in histList:
        strTemplate = """
\\begin{table}[htb]
  \\begin{center}
    \\begin{tabular}{%(nRow)s}
      \\hline
      & Variable & %(vari)s \\\\
      & Source %(binRange)s \\\\
      \\hline
      \\multicolumn{5}{|c|}{MC Uncertainties} \\\\
%(mcUnc)s 
      \\hline
      \\multicolumn{5}{|c|}{Experiment Uncertainties} \\\\
%(lumiUnc)s
%(muonUnc)s
%(elecUnc)s
%(btagUnc)s
%(otherExpUnc)s
      \\hline
      \\multicolumn{5}{|c|}{Theory Uncertainties} \\\\
%(theoryUnc)s 
      \\hline
    \\end{tabular}
  \\end{center}
\\end{table}
        """
        h_nominal = f_in.Get('DiffXsec_Unfolded_'+hist+'_data_obs')
        binNum = h_nominal.GetNbinsX()
        binRange = []
        for ibin in range(1,binNum+2):
            binLowEdge = h_nominal.GetBinLowEdge(ibin)
            binRange.append(binLowEdge)

        strBinRange = ''
        for idx in range(len(binRange)):
            if idx+1 == len(binRange):
                continue
            strBinRange += '& '+str(binRange[idx])+' -- '+str(binRange[idx+1])+' '
        strMatrixStatUnc = '      & ttbb MC stat '
        strMCbkgUnc = '      & Background MC scale '
        strUnc = {'Muon':[],'Electron':[],'bTag':[],'Experiment':[],'Theory':[]}

        if 'DeltaR' in hist:
            h_accept = f_accept.Get('h_BinAcceptanceDeltaR_Ch2')
            vari = '\\multicolumn{%d}{|c|}{$\DeltaR_{b\\bar{b}}$}' % (binNum-1)
        else:
            h_accept = f_accept.Get('h_BinAcceptanceInvMass_Ch2')
            vari = '\\multicolumn{%d}{|c|}{$m_{b\\bar{b}}$}' % (binNum-1)

        h2_EmatMatrixStat = f_in.Get('EmatrixInput_'+hist+'_data_obs')
        for ibin in range(1, h2_EmatMatrixStat.GetNbinsX()+1):
            value = math.sqrt(h2_EmatMatrixStat.GetBinContent(ibin,ibin))/\
                    (h_accept.GetBinContent(ibin)*h_nominal.GetXaxis().GetBinWidth(ibin)*lumi*bRatio)
            if value < 0.0:
                value = 0.0
            strMatrixStatUnc += '& %.7f ' % value
        
        h_postUp = calculateDiffXsec(lumi, f_in.Get('Background_Unfolded_'+hist+'_data_obs__postup'), h_accept)
        h_postDown = calculateDiffXsec(lumi, f_in.Get('Background_Unfolded_'+hist+'_data_obs__postdown'), h_accept)
        for ibin in range(1, h_postUp.GetNbinsX()+1):
            nominal = h_nominal.GetBinContent(ibin)
            up   = h_postUp.GetBinContent(ibin)
            down = h_postDown.GetBinContent(ibin)

            deltaUp = up - nominal
            deltaDown = down - nominal
            value = max(abs(deltaUp), abs(deltaDown))
            strMCbkgUnc += '& %.7f ' % value

        for categories, systList in systCategories.items():
            for syst in systList:
                h_systUp = f_in.Get('DeltaSysSource_'+hist+'_data_obs__'+syst+'up')
                h_systDown = f_in.Get('DeltaSysSource_'+hist+'_data_obs__'+syst+'down') 
                if h_systUp == None:
                    print '%s up does not exist, %s up systematic uncertainties set zero' % (syst, syst)
                    h_systUp = h_nominal.Clone()
                    for ibin in range(1,h_nominal.GetNbinsX()+1):
                        h_systUp.SetBinContent(ibin, 0)
                else:
                    h_systUp = calculateDiffXsec(lumi, f_in.Get('DeltaSysSource_'+hist+'_data_obs__'+syst+'up'), h_accept)
                if h_systDown == None:
                    print '%s down does not exist, %s down systematic uncertainties set zero' % (syst, syst)
                    h_systDown = h_nominal.Clone()
                    for ibin in range(1,h_nominal.GetNbinsX()+1):
                        h_systDown.SetBinContent(ibin, 0)
                else:
                    h_systDown = calculateDiffXsec(lumi, f_in.Get('DeltaSysSource_'+hist+'_data_obs__'+syst+'down'), h_accept)
                tmpStr = '      & '+syst+' '
                for ibin in range(1, h_nominal.GetNbinsX()+1):
                    deltaUp = h_systUp.GetBinContent(ibin)
                    deltaDown = h_systDown.GetBinContent(ibin)
                    value = max(abs(deltaUp), abs(deltaDown))

                    tmpStr += '& %.7f ' % value
                tmpStr += '\\\\\n'
                strUnc[categories].append(tmpStr)
        
        dictIn = {}
        dictIn['vari'] = vari
        dictIn['nRow'] = '|c'*binNum + '|c|'
        dictIn['binRange'] = strBinRange
        dictIn['mcUnc'] = strMatrixStatUnc +'\\\\\n' + strMCbkgUnc+'\\\\\n' 
        dictIn['lumiUnc'] = str(lumiUnc)
        dictIn['muonUnc'] = ''.join(strUnc['Muon'])
        dictIn['elecUnc'] = ''.join(strUnc['Electron'])
        dictIn['btagUnc'] = ''.join(strUnc['bTag'])
        dictIn['otherExpUnc'] = ''.join(strUnc['Experiment'])
        dictIn['theoryUnc'] = ''.join(strUnc['Theory'])

        strOut = strTemplate % dictIn

        with open(outputDir+'/SystUnc_'+hist+'.tex','w') as f: f.write(strOut)
