import sys, os
import google.protobuf

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

import pandas as pd
import csv
import math
import numpy as np
from array import array

from ROOT import *
import ROOT

import tensorflow as tf
import csv
from sklearn.utils import shuffle
import re
import string
import math

import printProgress as pp

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def ana(inputDir, process, fileNum) :
    timer = ROOT.TStopwatch()
    timer.Start()

    df = pd.read_hdf("output_ttbb.h5")
    df = df.filter(['signal',
        'dR','dEta','dPhi',
        'nuPt','nuEta','nuPhi','nuMass',
        'lbPt','lbEta','lbPhi','lbMass',
        'lb1Pt','lb1Eta','lb1Phi','lb1Mass',
        'lb2Pt','lb2Eta','lb2Phi','lb2Mass',
        'diPt','diEta','diPhi','diMass',
        'csv1','csv2','pt1','pt2','eta1','eta2','phi1','phi2','e1','e2'])
    train_input = df.values
    #np.load(df.values).astyle(np.float32)
    train_out = train_input[:,0]
    train_data = train_input[:,1:]

    numbertr=len(train_out)

    order=shuffle(range(numbertr),random_state=100)
    train_out = train_out[order]
    train_data = train_data[order,0::]
    train_out = train_out.reshape((numbertr,1))
    trainnb = 0.9

    valid_data = train_data[int(trainnb*numbertr):numbertr,0::]
    valid_data_out = train_out[int(trainnb*numbertr):numbertr]

    train_data_out = train_out[0:int(trainnb*numbertr)]
    train_data = train_data[0:int(trainnb*numbertr),0::]

    model = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(200, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.1),
      tf.keras.layers.Dense(1, activation=tf.nn.sigmoid)
    ])

    model_output_name = "keras"

    if os.path.exists('models/'+model_output_name+'/model.h5'):
        print "Model file exists already!"
        from tensorflow import keras
        model = keras.models.load_model('models/'+model_output_name+'/model.h5')
    else:
        model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy', 'binary_crossentropy'])
        history = model.fit(train_data, train_data_out, batch_size=1024, epochs=200, validation_data=(valid_data,valid_data_out))

        model.save('models/'+model_output_name+'/model.h5')

        evaluate = model.predict( valid_data ) 
        with open('models/'+model_output_name+'/output.csv', 'wb') as f:
          writer = csv.writer(f, delimiter=" ")
          for i in range(len(valid_data)):
            val_x = valid_data_out[i] 
            val_y = evaluate[i]
            writer.writerows( zip(val_y,val_x) )

    data = False
    if 'Data' in process : data = True
    ttbb = False
    if 'ttbb' in process : ttbb = True
    closureTest = False

    muon_ch = 0
    muon_pt = 30.0
    muon_eta = 2.1
    electron_ch = 1
    electron_pt = 35.0
    electron_eta = 2.1
    jet_pt = 30.0
    jet_eta = 2.4
    jet_CSV = 0.9535
    jet_CSV_medium = 0.8484
    number_of_jets = 6
    number_of_bjets = 3
    nChannel = 2
    nStep = 4

    if closureTest :
        f_out = ROOT.TFile("output/hist_closure.root", "recreate")
    else :
        f_out = ROOT.TFile('output/hist_'+str(process)+'.root', "recreate")

    RECO_NUMBER_OF_JETS_ = "nJets"
    RECO_NUMBER_OF_BJETS_ = "nBjets"
    RECO_ADDJETS_DELTAR_ = "RecoJetDeltaR"
    RECO_ADDJETS_INVARIANT_MASS_ = "RecoJetInvMass"
    GEN_ADDBJETS_DELTAR_ = "GenbJetDeltaR"
    GEN_ADDBJETS_INVARIANT_MASS_ = "GenbJetInvMass"
    RESPONSE_MATRIX_DELTAR_ = "ResponseMatrixDeltaR"
    RESPONSE_MATRIX_INVARIANT_MASS_ = "ResponseMatrixInvMass"

    xNbins_reco_addjets_dR = 4
    reco_addjets_dR_width = [0.4,0.6,1.0,2.0,4.0]

    xNbins_reco_addjets_M = 4
    reco_addjets_M_width = [0.0,60.0,100.0,170.0,400.0]

    xNbins_gen_addbjets_dR = 4
    gen_addbjets_dR_width = [0.4,0.6,1.0,2.0,4.0]

    xNbins_gen_addbjets_M = 4
    gen_addbjets_M_width = [0.0,60.0,100.0,170.0,400.0]

    h_gen_addbjets_deltaR_nosel = []
    h_gen_addbjets_invMass_nosel = []
    h_njets = [[0]*nStep for i in range(nChannel)]
    h_nbjets = [[0]*nStep for i in range(nChannel)]
    h_reco_addjets_deltaR = [[0]*nStep for i in range(nChannel)]
    h_reco_addjets_invMass = [[0]*nStep for i in range(nChannel)]
    h_gen_addbjets_deltaR = [[0]*nStep for i in range(nChannel)]
    h_gen_addbjets_invMass = [[0]*nStep for i in range(nChannel)]
    h_respMatrix_deltaR = [[0]*nStep for i in range(nChannel)]
    h_respMatrix_invMass = [[0]*nStep for i in range(nChannel)]

    for iChannel in range(0,nChannel) :
        h_gen_addbjets_deltaR_nosel.append(
            ROOT.TH1D("h_" + GEN_ADDBJETS_DELTAR_ + "_Ch" + str(iChannel) + "_nosel_" + process, "",
                xNbins_gen_addbjets_dR, array('d', gen_addbjets_dR_width)))
        h_gen_addbjets_invMass_nosel.append(
            ROOT.TH1D("h_" + GEN_ADDBJETS_INVARIANT_MASS_ + "_Ch" + str(iChannel) + "_nosel_" + process, "",
                xNbins_gen_addbjets_M, array('d', gen_addbjets_M_width)))
        for iStep in range(0,nStep) :
            h_njets[iChannel][iStep] = ROOT.TH1D("h_" + RECO_NUMBER_OF_JETS_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",10, 0, 10)
            h_njets[iChannel][iStep].GetXaxis().SetTitle("Jet multiplicity")
            h_njets[iChannel][iStep].GetYaxis().SetTitle("Entries")
            h_njets[iChannel][iStep].Sumw2()

            h_nbjets[iChannel][iStep] = ROOT.TH1D("h_" + RECO_NUMBER_OF_BJETS_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",10, 0, 10)
            h_nbjets[iChannel][iStep].GetXaxis().SetTitle("bJet multiplicity")
            h_nbjets[iChannel][iStep].GetYaxis().SetTitle("Entries")
            h_nbjets[iChannel][iStep].Sumw2()

            h_reco_addjets_deltaR[iChannel][iStep] = ROOT.TH1D("h_" + RECO_ADDJETS_DELTAR_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",
                xNbins_reco_addjets_dR, array('d', reco_addjets_dR_width))
            h_reco_addjets_deltaR[iChannel][iStep].GetXaxis().SetTitle("#DeltaR_{b#bar{b}}")
            h_reco_addjets_deltaR[iChannel][iStep].GetYaxis().SetTitle("Entries")
            h_reco_addjets_deltaR[iChannel][iStep].Sumw2()

            h_reco_addjets_invMass[iChannel][iStep] = ROOT.TH1D("h_" + RECO_ADDJETS_INVARIANT_MASS_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",
                xNbins_reco_addjets_M, array('d', reco_addjets_M_width))
            h_reco_addjets_invMass[iChannel][iStep].GetXaxis().SetTitle("M_{b#bar{b}}(GeV)")
            h_reco_addjets_invMass[iChannel][iStep].GetYaxis().SetTitle("Entries")
            h_reco_addjets_invMass[iChannel][iStep].Sumw2()

            h_gen_addbjets_deltaR[iChannel][iStep] = ROOT.TH1D("h_" + GEN_ADDBJETS_DELTAR_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",
                xNbins_gen_addbjets_dR, array('d', gen_addbjets_dR_width))
            h_gen_addbjets_deltaR[iChannel][iStep].GetXaxis().SetTitle("#DeltaR_{b#bar{b}}")
            h_gen_addbjets_deltaR[iChannel][iStep].GetYaxis().SetTitle("Entries")
            h_gen_addbjets_deltaR[iChannel][iStep].Sumw2()

            h_gen_addbjets_invMass[iChannel][iStep] = ROOT.TH1D("h_" + GEN_ADDBJETS_INVARIANT_MASS_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",
                xNbins_gen_addbjets_M, array('d', gen_addbjets_M_width))
            h_gen_addbjets_invMass[iChannel][iStep].GetXaxis().SetTitle("M_{b#bar{b}}(GeV)")
            h_gen_addbjets_invMass[iChannel][iStep].GetYaxis().SetTitle("Entries")
            h_gen_addbjets_invMass[iChannel][iStep].Sumw2()

            h_respMatrix_deltaR[iChannel][iStep] = ROOT.TH2D("h_" + RESPONSE_MATRIX_DELTAR_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",
                xNbins_reco_addjets_dR, array('d', reco_addjets_dR_width),
                xNbins_gen_addbjets_dR, array('d', gen_addbjets_dR_width))
            h_respMatrix_deltaR[iChannel][iStep].GetXaxis().SetTitle("Reco. #DeltaR_{b#bar{b}}")
            h_respMatrix_deltaR[iChannel][iStep].GetYaxis().SetTitle("Gen. #DeltaR_{b#bar{b}}")
            h_respMatrix_deltaR[iChannel][iStep].Sumw2()

            h_respMatrix_invMass[iChannel][iStep] = ROOT.TH2D("h_" + RESPONSE_MATRIX_INVARIANT_MASS_ + "_Ch" + str(iChannel) + "_S" + str(iStep) + "_" + process, "",
                xNbins_reco_addjets_M, array('d', reco_addjets_M_width),
                xNbins_gen_addbjets_M, array('d', gen_addbjets_M_width))
            h_respMatrix_invMass[iChannel][iStep].GetXaxis().SetTitle("Reco. M_{b#bar{b}}(GeV)")
            h_respMatrix_invMass[iChannel][iStep].GetYaxis().SetTitle("Gen. M_{b#bar{b}}(GeV)")
            h_respMatrix_invMass[iChannel][iStep].Sumw2()

    if ttbb == True :
        genchain = TChain("ttbbLepJets/gentree")
        genchain.Add("/data/users/seohyun/ntuple/hep2017/v808/nosplit/TTLJ_PowhegPythia_ttbb.root")

        print "GENTREE RUN"
        for i in xrange(genchain.GetEntries()) :
            pp.printProgress(i, genchain.GetEntries(), 'Progress:', 'Complete', 1, 50)
            genchain.GetEntry(i)
            addbjet1 = TLorentzVector()
            addbjet2 = TLorentzVector()
            addbjet1.SetPtEtaPhiE(genchain.addbjet1_pt, genchain.addbjet1_eta, genchain.addbjet1_phi, genchain.addbjet1_e)
            addbjet2.SetPtEtaPhiE(genchain.addbjet2_pt, genchain.addbjet2_eta, genchain.addbjet2_phi, genchain.addbjet2_e)

            gendR = addbjet1.DeltaR(addbjet2)
            genM = (addbjet1+addbjet2).M()

            if genchain.genchannel == muon_ch:
                h_gen_addbjets_deltaR_nosel[muon_ch].Fill(gendR,genchain.genweight)
                h_gen_addbjets_invMass_nosel[muon_ch].Fill(genM,genchain.genweight)
            elif genchain.genchannel == electron_ch:
                h_gen_addbjets_deltaR_nosel[electron_ch].Fill(gendR,genchain.genweight)
                h_gen_addbjets_invMass_nosel[electron_ch].Fill(genM,genchain.genweight)
            else : print("Error")

    print "\nTREE RUN"
    nEvents = 0
    nEvt_isMatch_DNN = 0
    nEvt_isMatch_mindR = 0
    f_pred = open('pred.txt','w')

    for item in os.listdir(inputDir) :
        print str(item)
        df = pd.read_hdf(inputDir+'/'+item)
        str_query = 'csv1 > '+str(jet_CSV)+' and csv2 > '+str(jet_CSV)+' and njets >= 6 and nbjets >= 3'
        selEvent = df.query(str_query)
        nTotal = selEvent['event'].iloc[-1]
        selEvent.reset_index(drop=True, inplace=True)
        jetCombi = selEvent.filter([
            'dR','dEta','dPhi',
            'nuPt','nuEta','nuPhi','nuMass',
            'lbPt','lbEta','lbPhi','lbMass',
            'lb1Pt','lb1Eta','lb1Phi','lb1Mass',
            'lb2Pt','lb2Eta','lb2Phi','lb2Mass',
            'diPt','diEta','diPhi','diMass',
            'csv1','csv2','pt1','pt2','eta1','eta2','phi1','phi2','e1','e2'
        ])
        if len(jetCombi) is not 0 :
            inputset = np.array(jetCombi)
            pred = model.predict(inputset)

        pred = pd.DataFrame(pred, columns=['signal'])
        f_pred.write('Pred\n'+str(pred)+'\n'+str(type(pred)))
        #f_pred.write('SelEvent\n'+str(selEvent))
        selEvent = pd.concat([selEvent,pred], axis=1)
        #f_pred.write('SelEvent+Pred\n'+str(selEvent))
        idx = selEvent.groupby(['event'])['signal'].transform(max) == selEvent['signal']
        #f_pred.write('\n'+str(idx)+'\n'+str(selEvent[idx])+'\n')
        selEvent[idx].reset_index(drop=True, inplace=True)

        #selEvent.groupby('event').max('signal').reset_index(drop=True, inplace=True)
        f_pred.write("Groupby\n"+str(selEvent[idx]))
        #groups = selEvent.groupby('event')
        for idx, event in selEvent[idx].iterrows() :
            #maxval = event[1][event[1]['signal'] == event[1]['signal'].max()]
            pp.printProgress(event['event'], nTotal, 'Progress:','Complete',1,50)

            eventweight = event['PUWeight']*event['genWeight']
            if not data :  eventweight *= event['lepton_SF']*event['jet_SF_CSV']

            passmuon = False
            passelectron = False
            if event['channel'] == 0 : passmuon = True
            if event['channel'] == 1 : passelectron = True

            njets = event['njets']
            nbjets = event['nbjets']

            gen_addbjet1 = TLorentzVector()
            gen_addbjet2 = TLorentzVector()
            gen_addbjet1.SetPtEtaPhiE(event['addbjet1_pt'],event['addbjet1_eta'],event['addbjet1_phi'],event['addbjet1_e'])
            gen_addbjet2.SetPtEtaPhiE(event['addbjet2_pt'],event['addbjet2_eta'],event['addbjet2_phi'],event['addbjet2_e'])

            gen_dR = gen_addbjet1.DeltaR(gen_addbjet2)
            gen_M = (gen_addbjet1+gen_addbjet2).M()

            reco_dR = 9999
            reco_M = 9999
            reco_addbjet1 = TLorentzVector(0,0,0,0)
            reco_addbjet2 = TLorentzVector(0,0,0,0)
            #additional bjets from DNN

            reco_addbjet1.SetPtEtaPhiE(event['pt1'],event['eta1'],event['phi1'],event['e1'])
            reco_addbjet2.SetPtEtaPhiE(event['pt2'],event['eta2'],event['phi2'],event['e2'])

            reco_dR = reco_addbjet1.DeltaR(reco_addbjet2)
            reco_M = (reco_addbjet1+reco_addbjet2).M()

            #f_pred.write('Pred : '+str(maxval)+'\n')
            #f_pred.write('Score\n'+str(event[1])+'\n')
            #f_pred.write('jet 1 : '+str(reco_addbjet1.Pt())+' jet 2 : '+str(reco_addbjet2.Pt())+'\n')
            #f_pred.write('genjet 1 : '+str(gen_addbjet1.Pt())+' genjet2 : '+str(gen_addbjet2.Pt())+'\n')
            #f_pred.write('reco dR : '+str(reco_addbjet1.DeltaR(reco_addbjet2))+'gen dR : '+str(gen_addbjet1.DeltaR(gen_addbjet2))+'\n')

            passchannel = -999
            passcut = 0

            #matching ratio
            isMatch_DNN = False
            isMatch_DNN = (reco_addbjet1.DeltaR(gen_addbjet1) < 0.5 and reco_addbjet2.DeltaR(gen_addbjet2) < 0.5) or (reco_addbjet1.DeltaR(gen_addbjet2) < 0.5 and reco_addbjet2.DeltaR(gen_addbjet1) < 0.5)
            if passmuon == True and passelectron == False : passchannel = muon_ch
            elif passmuon == False and passelectron == True : passchannel = electron_ch
            else : print "Error!"

            if njets >= number_of_jets :
                passcut += 1
                if nbjets >= number_of_bjets-1 :
                    passcut += 1
                    if nbjets >= number_of_bjets :
                        passcut += 1
                        nEvents += 1
                        if isMatch_DNN : nEvt_isMatch_DNN += 1

            if closureTest :
                for iStep in range(0,passcut+1) :
                    if i%2 == 1 :
                        h_reco_addjets_deltaR[passchannel][iStep].Fill(reco_dR, eventweight)
                        h_reco_addjets_invMass[passchannel][iStep].Fill(reco_M, eventweight)
                        h_gen_addbjets_deltaR[passchannel][iStep].Fill(gen_dR, eventweight)
                        h_gen_addbjets_invMass[passchannel][iStep].Fill(gen_M, eventweight)
                    else :
                        h_respMatrix_deltaR[passchannel][iStep].Fill(reco_dR, gen_dR, eventweight)
                        h_respMatrix_invMass[passchannel][iStep].Fill(reco_M, gen_M, eventweight)
            else :
                for iStep in range(0,passcut+1) :
                    h_njets[passchannel][iStep].Fill(njets, eventweight)
                    h_nbjets[passchannel][iStep].Fill(nbjets, eventweight)
                    h_reco_addjets_deltaR[passchannel][iStep].Fill(reco_dR, eventweight)
                    h_reco_addjets_invMass[passchannel][iStep].Fill(reco_M, eventweight)
                    if ttbb :
                        h_gen_addbjets_deltaR[passchannel][iStep].Fill(gen_dR, eventweight)
                        h_gen_addbjets_invMass[passchannel][iStep].Fill(gen_M, eventweight)
                        h_respMatrix_deltaR[passchannel][iStep].Fill(reco_dR, gen_dR, eventweight)
                        h_respMatrix_invMass[passchannel][iStep].Fill(reco_M, gen_M, eventweight)

    matching_DNN = 0.0
    matching_mindR = 0.0
    if nEvents is not 0 :
        matching_DNN = float(nEvt_isMatch_DNN) / float(nEvents)
        matching_mindR = float(nEvt_isMatch_mindR) / float(nEvents)
    #print "\nSelected Events / Total Events : "+str(nEvents)+"/"+str(nTotal)
    print "Matching Ratio from DNN : "+str(matching_DNN)+"("+str(nEvt_isMatch_DNN)+"/"+str(nEvents)+")"
    #print "Matching Ratio from minimun dR : "+str(matching_mindR)+"("+str(nEvt_isMatch_mindR)+"/"+str(nEvents)+")"

    for iChannel in range(0,2) :
        for iStep in range(0,4) :
            h_njets[iChannel][iStep].AddBinContent(10,h_njets[iChannel][iStep].GetBinContent(11))
            h_nbjets[iChannel][iStep].AddBinContent(10,h_nbjets[iChannel][iStep].GetBinContent(11))
            h_reco_addjets_deltaR[iChannel][iStep].AddBinContent(xNbins_reco_addjets_dR, h_reco_addjets_deltaR[iChannel][iStep].GetBinContent(xNbins_reco_addjets_dR+1))
            h_reco_addjets_invMass[iChannel][iStep].AddBinContent(xNbins_reco_addjets_M, h_reco_addjets_invMass[iChannel][iStep].GetBinContent(xNbins_reco_addjets_M+1))
            h_gen_addbjets_deltaR[iChannel][iStep].AddBinContent(xNbins_gen_addbjets_dR, h_gen_addbjets_deltaR[iChannel][iStep].GetBinContent(xNbins_gen_addbjets_dR+1))
            h_gen_addbjets_invMass[iChannel][iStep].AddBinContent(xNbins_gen_addbjets_M, h_gen_addbjets_invMass[iChannel][iStep].GetBinContent(xNbins_gen_addbjets_M+1))

            for iXaxis in range(1, xNbins_reco_addjets_dR+1) :
                tmp = h_respMatrix_deltaR[iChannel][iStep].GetBinContent(iXaxis, xNbins_gen_addbjets_dR)+h_respMatrix_deltaR[iChannel][iStep].GetBinContent(iXaxis, xNbins_gen_addbjets_dR+1)
                h_respMatrix_deltaR[iChannel][iStep].SetBinContent(iXaxis, xNbins_gen_addbjets_dR, tmp)
            for iYaxis in range(1, xNbins_gen_addbjets_dR+1) :
                tmp = h_respMatrix_deltaR[iChannel][iStep].GetBinContent(xNbins_reco_addjets_dR, iYaxis)+h_respMatrix_deltaR[iChannel][iStep].GetBinContent(xNbins_reco_addjets_dR+1, iYaxis)
                h_respMatrix_deltaR[iChannel][iStep].SetBinContent(xNbins_reco_addjets_dR, iYaxis, tmp)

            for iXaxis in range(1, xNbins_reco_addjets_M+1) :
                tmp = h_respMatrix_invMass[iChannel][iStep].GetBinContent(iXaxis, xNbins_gen_addbjets_M)+h_respMatrix_invMass[iChannel][iStep].GetBinContent(iXaxis, xNbins_gen_addbjets_M+1)
                h_respMatrix_invMass[iChannel][iStep].SetBinContent(iXaxis, xNbins_gen_addbjets_M, tmp)
            for iYaxis in range(1, xNbins_gen_addbjets_M+1) :
                tmp = h_respMatrix_invMass[iChannel][iStep].GetBinContent(xNbins_reco_addjets_M, iYaxis)+h_respMatrix_invMass[iChannel][iStep].GetBinContent(xNbins_reco_addjets_M+1, iYaxis)
                h_respMatrix_invMass[iChannel][iStep].SetBinContent(xNbins_reco_addjets_M, iYaxis,tmp)

            h_njets[iChannel][iStep].ClearUnderflowAndOverflow()
            h_nbjets[iChannel][iStep].ClearUnderflowAndOverflow()
            h_reco_addjets_deltaR[iChannel][iStep].ClearUnderflowAndOverflow()
            h_reco_addjets_invMass[iChannel][iStep].ClearUnderflowAndOverflow()
            h_gen_addbjets_deltaR[iChannel][iStep].ClearUnderflowAndOverflow()
            h_gen_addbjets_invMass[iChannel][iStep].ClearUnderflowAndOverflow()
            h_respMatrix_deltaR[iChannel][iStep].ClearUnderflowAndOverflow()
            h_respMatrix_invMass[iChannel][iStep].ClearUnderflowAndOverflow()

    f_out.Write()
    f_out.Close()
    f_pred.close()

    timer.Stop()
    realtime = timer.RealTime()
    cputime = timer.CpuTime()
    print("Real Time : {0:6.2f} seconds, CPU Time : {1:6.2f} seconds").format(realtime,cputime)
