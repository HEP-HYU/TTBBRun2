import os
import sys
from ROOT import *
import ROOT

import argparse
import subprocess

parser = argparse.ArgumentParser(description='Unfolding process')

parser.add_argument('-d', '--data', required=True, help='Input data type')
parser.add_argument('-a', '--acceptance', required=False, default="False", help='Run acceptance')
parser.add_argument('-u', '--unfold', required=False, default="True", help='Run unfold')
parser.add_argument('-y', '--year', required=False, type=int, default=9999, help='Run special year')
parser.add_argument('-s', '--sys', required=False, default="False", help='Run systematics')
parser.add_argument('-t', '--tunfold', required=False, default="True", help='Unfold by TUnfold')
parser.add_argument('-m', '--matrix', required=False, default="", help='Set input matrix')
parser.add_argument('-f', '--fixtau', required=False, default="False", help='Fix tau')

args = parser.parse_args()

def runAcceptance(year, ttbb, runSys):
    cmd = ['root', '-l', '-b', '-q', 'makeAcceptance.C("'+str(year)+'", "'+ttbb+'", '+runSys+')']
    with open('../output/unfold/'+str(year)+'/acceptance.txt','w') as f_out:
        subprocess.call(cmd, stdout=f_out)

def runUnfold(year, matrix_name, isData, runSys, useTUnfold, fixtau):
    out = "mc"
    if isData == 'true': out = "data" 
    cmd = ['root', '-l', '-b', '-q', 'ttbbDiffXsec.C+("'+str(year)+'", "'+matrix_name+'", '+isData+', '+runSys+', '+useTUnfold+', '+fixtau+')']
    cmd2 = ['root', '-l', '-b', '-q', 'drawUnfoldedHist.C("'+str(year)+'",'+isData+')']
    with open('../output/unfold/'+str(year)+'/result_'+out+'.txt','w') as f_out:
        subprocess.call(cmd, stdout=f_out)
	subprocess.call(cmd2)

for year in range(16,20):
    # Arguments
    # year
    if args.year == 16 or args.year == 2016:
        if year != 16: continue
    if args.year == 17 or args.year == 2017:
        if year != 17: continue
    if args.year == 18 or args.year == 2018:
        if year != 18: continue
    if args.year == 19 or args.year == 2019:
        if year != 19: continue

    # sys
    runSys = 'false'
    args.sys = (args.sys).lower()
    if args.sys == 'true': runSys = 'true'
    # acceptance
    runAcc = False
    args.acceptance = (args.acceptance).lower()
    if args.acceptance == "true": runAcc = True
    if runAcc: runAcceptance(year, "TTLJ_PowhegPythia_ttbb", runSys)
    # data
    isData = 'false'
    args.data = (args.data).lower()
    if args.data == 'true': isData = 'true'
    # tunfold
    useTUnfold = 'false'
    args.tunfold = (args.tunfold).lower()
    if args.tunfold == 'true': useTUnfold = 'true'
    # matrix
    if args.matrix == "":
        matrix_name = "ResponseMatrix_ttbb"
    else:
        matrix_name = args.matrix
    
    fixtau= 'false'
    args.fixtau = (args.fixtau).lower()
    if args.fixtau == 'true': fixtau= 'true'

    if not os.path.exists('../output/unfold'):
        os.mkdir('../output/unfold')

    if not os.path.exists('../output/unfold/'+str(year)):
        os.mkdir('../output/unfold/'+str(year))

    print("Year: "+str(year))
    print("Matrix: "+matrix_name)
    runUnf = False
    args.unfold = (args.unfold).lower()
    if args.unfold == "true": runUnf = True
    if runUnf: runUnfold(year, matrix_name, isData, runSys, useTUnfold, fixtau)
