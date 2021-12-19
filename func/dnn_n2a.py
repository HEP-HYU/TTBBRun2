#! /usr/bin/env python
import os, sys
import argparse
import multiprocessing as mp
import time

import numpy as np
from numpy.lib.recfunctions import stack_arrays
from ROOT import *
from root_numpy import tree2array
from array import array
import math
import glob
import pandas as pd
from tqdm import tqdm

import yaml

import utils as ut

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'): return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'): return False

def transversemass(vec1, met):
    tmp1 = TLorentzVector(vec1.Px(), vec1.Py(), 0, vec1.E()*math.sin(vec1.Theta()))
    tmp2 = TLorentzVector(met.Px(), met.Py(), 0, met.E());

    return (tmp1+tmp2).M()

def makeCombi(year, inputDir, inputFile, makeTrainingInput, sys=''):
    print("Begin Process "+str(os.getpid())+": "+str(inputFile))
    makeTrainingInput = str2bool(makeTrainingInput)
    
    chain = TChain("ttbbLepJets/tree")
    chain.Add(inputDir+"/"+inputFile)

    outputDir = '/data/users/seohyun/array/Run20'+str(year)
    try:
        os.makedirs(outputDir)
    except OSError:
        print(outputDir+": already exists")

    data = False
    if 'Data' in inputDir: data = True
    ttbb = False
    if 'ttbb' in inputDir: ttbb = True

    with open('object_selection_config.yml', 'r') as f:
        if '2016' in inputDir:
            era = 2016
        elif '2017' in inputDir:
            era = 2017
        elif '2018' in inputDir:
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

    jetCombi = []
    for i in xrange(chain.GetEntries()) :
        chain.GetEntry(i)

        lep = TLorentzVector()
        lep.SetPtEtaPhiE(chain.lepton_pt, chain.lepton_eta, chain.lepton_phi, chain.lepton_e)
        passmuon = False
        passelectron = False
        passmuon = chain.channel == muon_ch and lep.Pt() > muon_pt and abs(lep.Eta()) < muon_eta
        passelectron = chain.channel == electron_ch and lep.Pt() > electron_pt and abs(lep.Eta()) < electron_eta
        if passmuon == False and passelectron == False:
            continue

        addbjet1 = TLorentzVector(0,0,0,0)
        addbjet2 = TLorentzVector(0,0,0,0)
        if ttbb:
            addbjet1.SetPtEtaPhiE(chain.addbjet1_pt,chain.addbjet1_eta,chain.addbjet1_phi,chain.addbjet1_e)
            addbjet2.SetPtEtaPhiE(chain.addbjet2_pt,chain.addbjet2_eta,chain.addbjet2_phi,chain.addbjet2_e)
        njets = 0
        nbjets = 0
        addbjet1_matched = TLorentzVector(0,0,0,0)
        addbjet2_matched = TLorentzVector(0,0,0,0)

        for iJet in range(len(chain.jet_pt)):
            jet = TLorentzVector()
            jet.SetPtEtaPhiE(chain.jet_pt[iJet],chain.jet_eta[iJet],chain.jet_phi[iJet],chain.jet_e[iJet])

            if not data :
                if   'jecup'   in sys:
                    jet *= chain.jet_JER_Nom[iJet] * chain.jet_JES_Up[iJet]
                elif 'jecdown' in sys:
                    jet *= chain.jet_JER_Nom[iJet] * chain.jet_JES_Down[iJet]
                elif 'jerup'   in sys:
                    jet *= chain.jet_JER_Up[iJet]
                elif 'jerdown' in sys:
                    jet *= chain.jet_JER_Down[iJet]
                else:
                    jet *= chain.jet_JER_Nom[iJet]

            if jet.Pt() < jet_pt or abs(jet.Eta()) > jet_eta: continue
            njets += 1
            if chain.jet_deepCSV[iJet] > jet_csv: nbjets += 1

            if addbjet1.DeltaR(jet) < 0.4: addbjet1_matched = jet;
            if addbjet2.DeltaR(jet) < 0.4: addbjet2_matched = jet;

        if njets < 6 or nbjets < 2: continue

        prefireweight = []
        pdfweight = []
        psweight = []
        scaleweight = []
        PUWeight = []
        lepton_SF = []
        jet_SF_CSV_30 = []
        if not data:
            for j in xrange((chain.lepton_SF).size()):
                lepton_SF.append(float(chain.lepton_SF[j]))
            for j in xrange((chain.jet_SF_deepCSV_30).size()):
                jet_SF_CSV_30.append(float(chain.jet_SF_deepCSV_30[j]))
            for j in xrange((chain.PUWeight).size()):
                PUWeight.append(float(chain.PUWeight[j]))
            if chain.GetBranchStatus("prefireweight"):
                for j in xrange((chain.prefireweight).size()):
                    prefireweight.append(float(chain.prefireweight[j]))
        if 'TT' in inputDir:
            for j in xrange((chain.scaleweight).size()):
                scaleweight.append(float(chain.scaleweight[j]))
            for j in xrange((chain.pdfweight).size()):
                pdfweight.append(float(chain.pdfweight[j]))
            if chain.GetBranchStatus("psweight"):
                for j in xrange((chain.psweight).size()):
                    psweight.append(float(chain.psweight[j]))

        MET_px = chain.MET*math.cos(chain.MET_phi)
        MET_py = chain.MET*math.sin(chain.MET_phi)
        nu = TLorentzVector(MET_px, MET_py, 0, chain.MET)

        for j in range(len(chain.jet_pt)-1):
            for k in range(j+1, len(chain.jet_pt)):
                if chain.jet_deepCSV[j] > jet_csv and chain.jet_deepCSV[k] > jet_csv:
                    b1 = TLorentzVector()
                    b2 = TLorentzVector()
                    b1.SetPtEtaPhiE(chain.jet_pt[j], chain.jet_eta[j], chain.jet_phi[j], chain.jet_e[j])
                    b2.SetPtEtaPhiE(chain.jet_pt[k], chain.jet_eta[k], chain.jet_phi[k], chain.jet_e[k])
                    if not data :
                        if   'jecup'   in sys:
                            b1 *= chain.jet_JER_Nom[j] * chain.jet_JES_Up[j]
                            b2 *= chain.jet_JER_Nom[k] * chain.jet_JES_Up[k]
                        elif 'jecdown' in sys:
                            b1 *= chain.jet_JER_Nom[j] * chain.jet_JES_Down[j]
                            b2 *= chain.jet_JER_Nom[k] * chain.jet_JES_Down[k]
                        elif 'jerup'   in sys:
                            b1 *= chain.jet_JER_Up[j]
                            b2 *= chain.jet_JER_Up[k]
                        elif 'jerdown' in sys:
                            b1 *= chain.jet_JER_Down[j]
                            b2 *= chain.jet_JER_Down[k]
                        else                 :
                            b1 *= chain.jet_JER_Nom[j]
                            b2 *= chain.jet_JER_Nom[k]

                    tmp = []
                    if makeTrainingInput:
                        if (addbjet1_matched.DeltaR(b1) == 0 and addbjet2_matched.DeltaR(b2) == 0) or (addbjet2_matched.DeltaR(b1) == 0  and addbjet1_matched.DeltaR(b2) == 0):
                            signal = 1
                        else:
                            signal = 0
                        tmp = [signal]
                    tmp += [i, (b1+b2).M(), b1.DeltaR(b2), b1.DeltaPhi(b2),  abs(b1.Eta()-b2.Eta()),
                            (b1+b2).Phi(), (b1+b2).Eta(), 
                            (b1+b2+nu).M(), (b1+b2).DeltaR(nu), 
                            (b1+nu).M(), b1.DeltaR(nu), (b2+nu).M(), b2.DeltaR(nu),
                            (b1+b2+lep).M(), (b1+b2).DeltaR(lep),
                            (b1+lep).M(), b1.DeltaR(lep), (b2+lep).M(), b2.DeltaR(lep),
                            (b1+b2).DeltaR(lep+nu),
                            b1.Pt(), b1.Eta(), b1.E(), chain.jet_deepCSV[j], b1.M(),
                            b2.Pt(), b2.Eta(), b2.E(), chain.jet_deepCSV[k], b2.M(),
                            lep.Pt(), lep.Eta(), lep.E(),
                            nu.Pt(), nu.Phi(),
                            nbjets]

                    if not makeTrainingInput:
                        tmp += [chain.channel, chain.genweight, PUWeight, scaleweight, pdfweight,
                                prefireweight, psweight, lepton_SF, jet_SF_CSV_30,
                                lep.Pt(), lep.Eta(), lep.Phi(), lep.E(),
                                addbjet1.Pt(), addbjet1.Eta(), addbjet1.Phi(), addbjet1.E(),
                                addbjet2.Pt(), addbjet2.Eta(), addbjet2.Phi(), addbjet2.E(),
                                njets, j, k]
                    jetCombi.append(tmp)

    if makeTrainingInput:
        combi = pd.DataFrame(jetCombi, columns=['signal', 'event']+ut.getVarlist())
    else:
        combi = pd.DataFrame(jetCombi, columns=
            ['event']+ut.getVarlist()+
            ['channel', 'genWeight', 'PUWeight', 'scaleweight', 'pdfweight',
            'prefireweight', 'psweight', 'lepton_SF', 'jet_SF_CSV_30', 
            'leptonPt','leptonEta','leptonPhi','leptonE',
            'addbjet1_pt','addbjet1_eta','addbjet1_phi','addbjet1_e',
            'addbjet2_pt','addbjet2_eta','addbjet2_phi','addbjet2_e',
            'njets','b1','b2'])

    combi.style.format('table')
    combi.to_hdf(outputDir+"/array_"+inputFile.replace("root","h5"),key='combi',mode='w')
    print("End Process "+str(os.getpid())+": "+str(inputFile))

if len(sys.argv) == 5:
    makeCombi(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
elif len(sys.argv) == 6:
    makeCombi(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
