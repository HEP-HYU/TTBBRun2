import os, sys

from ROOT import *
import ROOT

print("Start merging 2017 and 2018 dataset")

path_17 = '../output/root17/'
path_18 = '../output/root18/'
path_merged = '../output/root19/'
if not os.path.exists(path_merged): os.mkdir(path_merged)
lumi17 = 41529.0
lumi18 = 59693.0

sample17 = []
with open('../samples/sample17.txt','r') as f:
    while True:
        line = f.readline()
	if not line: break
	if '/' in line: continue
	else: sample17.append(line[:-1])

sample18 = []
with open('../samples/sample18.txt', 'r') as f:
    while True:
        line = f.readline()
	if not line: break
	if '/' in line: continue
	else: sample18.append(line[:-1])

nevt17 = {}
with open('../samples/genevt17.txt', 'r') as f:
    while True:
        line = f.readline()
	if not line: break
	tmp = line.split(' ')
	nevt17[tmp[0]] = float(tmp[1])

nevt18 = {}
with open('../samples/genevt18.txt', 'r') as f:
    while True:
        line = f.readline()
	if not line: break
	tmp = line.split(' ')
	nevt18[tmp[0]] = float(tmp[1])

# Merge Response Matrix
print('Merge Response Matrix')
matrix17 = ROOT.TFile(os.path.join(path_17, 'hist_ResponseMatrix_ttbb.root'))
matrix18 = ROOT.TFile(os.path.join(path_18, 'hist_ResponseMatrix_ttbb.root'))
matrix_merged = ROOT.TFile(os.path.join(path_merged, 'hist_ResponseMatrix_ttbb.root'), 'recreate')

hist_list = [x.GetName() for x in matrix17.GetListOfKeys()]
scale = (lumi17*nevt18['TTLJ_PowhegPythia_ttbb'])/(lumi18*nevt17['TTLJ_PowhegPythia_ttbb'])

matrix_merged.cd()
for hist in hist_list:
    if '__' in hist and (not 'up' in hist and not 'down' in hist): continue
    if 'pref' in hist: continue
    tmp0 = matrix17.Get(hist)
    tmp1 = matrix18.Get(hist)
    tmp0.Scale(scale)
    tmp1.Add(tmp0)
    tmp1.Write()

matrix17.Close()
matrix18.Close()
matrix_merged.Close()
print('Merging matrix is completed')

# Merge Data
print('Merge Data')
data_muon17 = ROOT.TFile(os.path.join(path_17, 'hist_DataSingleMu.root'))
data_muon18 = ROOT.TFile(os.path.join(path_18, 'hist_DataSingleMu.root'))
data_muon_merged = ROOT.TFile(os.path.join(path_merged, 'hist_DataSingleMu.root'), 'recreate')

hist_list = [x.GetName() for x in data_muon17.GetListOfKeys()]
data_muon_merged.cd()
for hist in hist_list:
    tmp0 = data_muon17.Get(hist)
    tmp1 = data_muon18.Get(hist)
    tmp1.Add(tmp0)
    tmp1.Write()

data_muon17.Close()
data_muon18.Close()
data_muon_merged.Close()

data_electron17 = ROOT.TFile(os.path.join(path_17, 'hist_DataSingleEG.root')) 
data_electron18 = ROOT.TFile(os.path.join(path_18, 'hist_DataSingleEG.root'))
data_electron_merged = ROOT.TFile(os.path.join(path_merged, 'hist_DataSingleEG.root'), 'recreate')

data_electron_merged.cd()
for hist in hist_list:
    tmp0 = data_electron17.Get(hist)
    tmp1 = data_electron18.Get(hist)
    tmp1.Add(tmp0)
    tmp1.Write()

data_electron17.Close()
data_electron18.Close()
data_electron_merged.Close()
print('Merging data is completed')

# Merge non-QCD MC
print('Merge non-QCD MC samples')
for sample in sample17:
    if not 'ttbb' in sample: continue
    if 'QCD' in sample: continue
    print(sample)
    mc17 = ROOT.TFile(os.path.join(path_17, 'hist_'+sample+'.root'))
    mc18 = ROOT.TFile(os.path.join(path_18, 'hist_'+sample+'.root'))
    mc_merged = ROOT.TFile(os.path.join(path_merged, 'hist_'+sample+'.root'), 'recreate')
    
    hist_list = [x.GetName() for x in mc17.GetListOfKeys()]
    scale = (lumi17*nevt18[sample])/(lumi18*nevt17[sample])
    
    mc_merged.cd()
    for hist in hist_list:
        if '__' in hist and (not 'up' in hist and not 'down' in hist): continue
        if 'pref' in hist: continue
        tmp0 = mc17.Get(hist)
        tmp1 = mc18.Get(hist)
        tmp0.Scale(scale)
        tmp1.Add(tmp0)
        tmp1.Write()

    mc17.Close()
    mc18.Close()
    mc_merged.Close()
print('Merged non-QCD MC is completed')

"""
# Merge QCD MC
# 17 only QCD samples are not included...
print('Merge QCD MC samples')
for sample in sample17:
    if not 'QCD' in sample: continue
    qcd17 = ROOT.TFile(os.path.join(path_17, 'hist_'+sample+'.root'))
    if os.path.exists(os.path.join(path_18, 'hist_'+sample+'.root')):
        qcd18 = ROOT.TFile(os.path.join(path_18, 'hist_'+sample+'.root'))
    qcd_merged = ROOT.TFile(os.path.join(path_merged, 'hist_'+sample+'.root'), 'recreate')

    hist_list = [x.GetName() for x in qcd17.GetListOfKeys()]
    qcd_merged.cd()
    if os.path.exists(os.path.join(path_18, 'hist_'+sample+'.root')):
        scale = (lumi17*nevt18[sample])/(lumi18*nevt17[sample])
        for hist in hist_list:
	    tmp0 = qcd17.Get(hist)
	    tmp1 = qcd18.Get(hist)
	    tmp0.Scale(scale)
	    tmp1.Add(tmp0)
	    tmp1.Write()
    
    qcd17.Close()
    qcd18.Close()
    qcd_merged.Close()

for sample in sample18:
    if not 'QCD' in sample: continue
    if not os.path.exists(os.path.join(path_17, 'hist_'+sample+'.root')):
        os.system('cp '+path_18+'/hist_'+sample+'.root '+path_merged+'/hist_'+sample+'.root')

print('Merged QCD MC is completed')
"""
print('All processes are finished')
