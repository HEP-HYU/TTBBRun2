import os
import sys

import ROOT

import saveAndLoadSamples as sls
import tdrstyle

class DrawSystPlots(sls.LoadSamples):
    luminosity = {16:35922, 17:41529, 18:59741}
    def __init__(self, year, root_path, hist_name, output_path):
        self.year = year
        self.root_path = root_path
        self.hist_name = hist_name
        self.output_path = output_path
        self.samples = {} 
        self.xsecs = {}
        self.genevt = {}
        
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def get_root_files(self):
        self.get_sample_info()
       
        for sample in self.xsecs.values():
            self.samples[sample[0]] = ROOT.TFile(os.path.join(self.root_path, 'hist_'+sample[0]+'.root'))

    def draw_histograms(self):
        ROOT.gStyle.SetOptStat(0)

        for name, file in self.samples.items():
            if not 'ttbb' in name: continue
            temp = [x.GetName() for x in file.GetListOfKeys()]
            break

        syst_name = []
        for item in temp:
            if not self.hist_name in item: continue
            if item[-2:] == 'up':
                name = (item.split('__')[-1]).replace('up','')
                syst_name.append(name)

        xsecs = {}
        for sample in self.xsecs.values():
            xsecs[sample[0]] = sample[1]
        for syst in syst_name:
            i = 0
            for name, file in self.samples.items():
                if 'QCD' in name: continue
                if any(i in syst for i in ['tune','pdf','ps','sw','hdamp','isr','fsr']):
                    if not ('TT' in name and 'Powheg' in name): continue
                if i == 0:
                    TH1Nom = file.Get(self.hist_name).Clone()
                    TH1Up = file.Get(self.hist_name+'__'+syst+'up').Clone()
                    TH1Down = file.Get(self.hist_name+'__'+syst+'down').Clone()

                    TH1Nom.Scale(xsecs[name]*DrawSystPlots.luminosity[self.year]/self.genevt[name])
                    TH1Up.Scale(xsecs[name]*DrawSystPlots.luminosity[self.year]/self.genevt[name])
                    TH1Down.Scale(xsecs[name]*DrawSystPlots.luminosity[self.year]/self.genevt[name])
                    i += 1
                else:
                    tmpNom = file.Get(self.hist_name).Clone()
                    tmpUp = file.Get(self.hist_name+'__'+syst+'up').Clone()
                    tmpDown = file.Get(self.hist_name+'__'+syst+'down').Clone()
                    
                    tmpNom.Scale(xsecs[name]*DrawSystPlots.luminosity[self.year]/self.genevt[name])
                    tmpUp.Scale(xsecs[name]*DrawSystPlots.luminosity[self.year]/self.genevt[name])
                    tmpDown.Scale(xsecs[name]*DrawSystPlots.luminosity[self.year]/self.genevt[name])

                    TH1Nom.Add(tmpNom)
                    TH1Up.Add(tmpUp)
                    TH1Down.Add(tmpDown)
 
            label = ROOT.TPaveText(0.14,0.9549955,0.97,1,"brNDC")
            label.SetBorderSize(0)
            label.SetFillStyle(0)
            label.SetTextAlign(13)
            label.SetTextSize(0.05850585)
            label.AddText("  CMS simulation #font[52]{#scale[0.76]{Work in Progress}}")

            canvas = ROOT.TCanvas("","",1025,568,450,450)
            canvas.Range(0,0,1,1)
            canvas.SetFillColor(0)
            canvas.SetBorderMode(0)
            canvas.SetBorderSize(2)
            canvas.SetTickx(1)
            canvas.SetTicky(1)
            canvas.SetLeftMargin(0.14)
            canvas.SetRightMargin(0.03)
            canvas.SetTopMargin(0.06)
            canvas.SetFrameBorderMode(0)

            pad1 = ROOT.TPad("pad1","pad1",0.0,0.33333,1.0,1.0)
            pad1.Range(-67.46988,-190.601,414.4578,9339.448)
            pad1.SetLeftMargin(0.14)
            pad1.SetRightMargin(0.03)
            pad1.SetBottomMargin(0.02)
            pad1.SetFrameFillColor(0)
            pad1.SetFillColor(0)
            pad1.SetBorderMode(0)
            pad1.SetBorderSize(2)
            pad1.SetTickx(1)
            pad1.SetTicky(1)
            pad1.SetFrameBorderMode(0)

            pad2 = ROOT.TPad("pad2","pad2",0.0,0.0,1.0,0.33333)
            pad2.Range(-67.46988,-0.1539271,414.4578,1.692312)
            pad2.SetTopMargin(0.05)
            pad2.SetBottomMargin(0.30003)
            pad2.SetLeftMargin(0.14)
            pad2.SetRightMargin(0.03)
            pad2.SetGridy()
            pad2.SetFrameFillColor(0)
            pad2.SetTickx(1)
            pad2.SetTicky(1)
            pad2.SetFrameBorderMode(0)

            pad1.Draw()
            pad2.Draw()
            
            pad1.cd()
            TH1Nom.GetXaxis().SetLabelFont(43)
            TH1Nom.GetXaxis().SetTitleFont(43)
            TH1Nom.GetYaxis().SetLabelFont(43)
            TH1Nom.GetYaxis().SetLabelSize(14)
            TH1Nom.GetYaxis().SetTitleSize(15)
            TH1Nom.GetYaxis().SetTitleOffset(2)
            TH1Nom.GetYaxis().SetTitleFont(43)
            TH1Nom.GetXaxis().SetLabelSize(0)
            TH1Nom.GetXaxis().SetTitleSize(0)
            TH1Nom.SetMinimum(0)

            TH1Up.SetLineColor(ROOT.kGreen)
            TH1Down.SetLineColor(ROOT.kRed)

            TH1Nom.Draw("hist")
            TH1Up.Draw("hist same")
            TH1Down.Draw("hist same")
            label.Draw("same")

            pad2.cd()
            TH1RatioUp = TH1Nom.Clone()
            TH1RatioUp.Divide(TH1Up)
            TH1RatioDown = TH1Nom.Clone()
            TH1RatioDown.Divide(TH1Down)
            
            TH1RatioUp.SetMaximum(1.4)
            TH1RatioUp.SetMinimum(0.6)
            TH1RatioUp.GetXaxis().SetLabelOffset(0.021)
            TH1RatioUp.GetXaxis().SetLabelSize(14)
            TH1RatioUp.GetXaxis().SetTitleSize(15)
            TH1RatioUp.GetXaxis().SetTitleOffset(3.3)
            TH1RatioUp.GetYaxis().SetTitle("Nom. / Syst.")
            TH1RatioUp.GetYaxis().SetLabelOffset(0.012)
            TH1RatioUp.GetYaxis().SetLabelSize(14)
            TH1RatioUp.GetYaxis().SetTitleSize(15)
            TH1RatioUp.GetYaxis().SetNdivisions(505)
            
            TH1RatioUp.SetLineColor(ROOT.kGreen)
            TH1RatioDown.SetLineColor(ROOT.kRed)
            
            TH1RatioUp.Draw("p")
            TH1RatioDown.Draw("p same")

            canvas.Print(self.output_path+'/'+syst+".pdf","pdf")
            
            pad1.Clear()
            pad2.Clear()
            canvas.Clear()
