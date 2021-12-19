import os, sys

from array import array

import ROOT

class RunWithGenTree:
    def __init__(self, ntuple_path, ttbb_name, output_path):
        self.ntuple_path = ntuple_path
        self.ttbb_name = ttbb_name
        self.output_path = output_path

    def run_with_gen_tree(self):
        h_gentop_deltaR = [[0] for i in range(0,3)]
        h_gentop_invMass = [[0] for i in range(0,3)]
        h_mindR_deltaR = [[0] for i in range(0,3)]
        h_mindR_invMass = [[0] for i in range(0,3)]

        nbins_gen_addbjets_dr = 3
        gen_addbjets_dr_min = 0.4
        gen_addbjets_dr_max = 4.0
        gen_addbjets_dr_width = [0.4,1.0,2.0,4.0]

        nbins_gen_addbjets_m = 4
        gen_addbjets_m_min = 0.0
        gen_addbjets_m_max = 400.0
        gen_addbjets_m_width = [0.0,60.0,100.0,170.0,400.0]

        for ich in range(0,3):
            h_gentop_deltaR[ich] = ROOT.TH1D(
                "h_gentop_GenAddbJetDeltaR_Ch%d_nosel" % ich, "",
                nbins_gen_addbjets_dr, array('d', gen_addbjets_dr_width)
                )
            h_gentop_deltaR[ich].SetXTitle(Form("#DeltaR_{b#bar{b}}"));
            h_gentop_deltaR[ich].SetYTitle("Entries");
            h_gentop_deltaR[ich].Sumw2();
              
            h_gentop_invMass[ich] = ROOT.TH1D(
                "h_gentop_GenAddbJetInvMass_Ch%d_nosel" % ich, "",
                nbins_gen_addbjets_m, array('d', gen_addbjets_m_width)
              )
            h_gentop_invMass[ich].SetXTitle(Form("M_{b#bar{b}}"));
            h_gentop_invMass[ich].SetYTitle("Entries");
            h_gentop_invMass[ich].Sumw2();

            h_mindR_deltaR[ich] = ROOT.TH1D(
                "h_mindR_GenAddbJetDeltaR_Ch%d_nosel" % ich, "",
                nbins_gen_addbjets_dr, array('d', gen_addbjets_dr_width)
                )
            h_mindR_deltaR[ich].SetXTitle(Form("#DeltaR_{b#bar{b}}"));
            h_mindR_deltaR[ich].SetYTitle("Entries");
            h_mindR_deltaR[ich].Sumw2();
              
            h_mindR_invMass[ich] = ROOT.TH1D(
                "h_mindR_GenAddbJetInvMass_Ch%d_nosel" % ich, "",
                nbins_gen_addbjets_m, array('d', gen_addbjets_m_width)
              )
            h_mindR_invMass[ich].SetXTitle(Form("M_{b#bar{b}}"));
            h_mindR_invMass[ich].SetYTitle("Entries");
            h_mindR_invMass[ich].Sumw2();

        f_out = ROOT.TFile.Open(os.path.join(self.output_path, 'hist_GenTree.root'), 'RECREATE')

        genchain = ROOT.TChain('ttbbLepJets/gentree')
        genchain.Add(os.path.join(self.ntuple_path, self.ttbb_name))

        import utils as ut
        for i in xrange(genchain.GetEntries()):
            ut.printProgress(i, genchain.GetEntries(), 'Progress:', 'Complete', 1, 50)

            genchain.GetEntry(i)
            gentop_addbjet1 = ROOT.TLorentzVector()
            gentop_addbjet2 = ROOT.TLorentzVector()
            gentop_addbjet1.SetPtEtaPhiE(genchain.addbjet1_pt, genchain.addbjet1_eta, genchain.addbjet1_phi, genchain.addbjet1_e)
            gentop_addbjet2.SetPtEtaPhiE(genchain.addbjet2_pt, genchain.addbjet2_eta, genchain.addbjet2_phi, genchain.addbjet2_e)

            mindR_addbjet1 = ROOT.TLorentzVector()
            mindR_addbjet2 = ROOT.TLorentzVector()
            mindR_addbjet1.SetPtEtaPhiE(genchain.mindRjet1_pt, genchain.mindRjet1_eta, genchain.mindRjet1_phi, genchain.mindRjet1_e)
            mindR_addbjet2.SetPtEtaPhiE(genchain.mindRjet2_pt, genchain.mindRjet2_eta, genchain.mindRjet2_phi, genchain.mindRjet2_e)

            gentop_dR = -999
            gentop_m = -999
            mindR_dR = -999
            mindR_m = -999
 
            gentop_dR = gentop_addbjet1.DeltaR(gentop_addbjet2)
            gentop_m = (gentop_addbjet1 + gentop_addbjet2).M()
           
            mindR_dR   = mindR_addbjet1.DeltaR(mindR_addbjet2)
            mindR_M    = (mindR_addbjet1 + mindR_addbjet2).M()

            channel = genchain.channel
            genweight = genchain.genweight

            h_gentop_deltaR[channel].(gentop_dR, genweight)
            h_gentop_invMass[channel].(gentop_m, genweight)
            h_mindR_deltaR[channel].(mindR_dR, genweight)
            h_mindR_invMass[channel].(mindR_m, genweight)

            if channel == 0 or channel == 1:
                h_gentop_deltaR[2].(gentop_dR, genweight)
                h_gentop_invMass[2].(gentop_m, genweight)
                h_mindR_deltaR[2].(mindR_dR, genweight)
                h_mindR_invMass[2].(mindR_m, genweight)

        f_out.cd()
        for ich in range(0,3):
            h_gentop_deltaR[ich].Write()
            h_gentop_invMass[ich].Write()
            h_mindR_deltaR[ich].Write()
            h_mindR_invMass[ich].Write()
        f_out.Close()

