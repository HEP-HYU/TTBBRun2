import os
import sys
import time
import argparse
import subprocess

from ROOT import *
import ROOT

import python.unfoldPreProcess as upp
import python.drawUnfoldOutput as duo

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected')

def makeAcceptance(inputDir, outputDir, year, ttbb, genMode):
    cmd = ['root', '-l', '-b', '-q',
            'macro/makeAcceptance.C+("'+inputDir+'", "'+outputDir+'", "'+str(year)+'", "'+ttbb+'", "'+genMode+'")']
    with open('output/unfold'+str(year)+'/acceptance.txt','w') as f_out:
        subprocess.call(cmd, stdout=f_out)

def runUnfold(unfoldDir, year, genMode, recoMode, scanLcurve, fixTau):
    cmd = ['root', '-l', '-b', '-q', 'macro/ttbbDiffXsec.C+("'+unfoldDir+'", "'+str(year)+'", "'+genMode+'", "'+recoMode+'", '+scanLcurve+', '+fixTau+')']
    with open('output/unfold'+str(year)+'/result.txt','w') as f_out:
        subprocess.call(cmd, stdout=f_out)

if __name__ == '__main__':
    start_time = time.time()

    parser = argparse.ArgumentParser(description='Unfolding process')

    parser.add_argument('-d', '--data', required=False, type=str2bool, default=True, help='Input data type')
    parser.add_argument('-a', '--acceptance', required=False, type=str2bool, default=False, help='Run acceptance')
    parser.add_argument('-u', '--unfold', required=False, type=str2bool, default=True, help='Run unfold')
    parser.add_argument('-y', '--year', required=False, type=int, default=9999, help='Run special year')
    parser.add_argument('-f', '--fixtau', required=False, type=str, default='false', help='Fix tau')
    parser.add_argument('-l', '--scanLcurve', required=False, type=str, default='true', help='Fix tau')

    args = parser.parse_args()

    run16 = False
    run17 = False
    run18 = False
    if args.year > 2018:
        run16 = True
        run17 = True
        run18 = True
    elif args.year == 16 or args.year == 2016:
        run16 = True
    elif args.year == 17 or args.year == 2017:
        run17 = True
    elif args.year == 18 or args.year == 2018:
        run18 = True

    for year in range(16,19):
        if year == 16 and run16 == False: continue
        if year == 17 and run17 == False: continue
        if year == 18 and run18 == False: continue


        argDict = {'year':args.year}
        group = []
        with open('./samples/unfold'+str(year)+'.txt','r') as f:
            while True:
                line = f.readline()
                if not line: break
                line = line.replace('\n', '')
                tmp = line.split(' ')
                if len(tmp) < 3:
                    argDict[tmp[0]] = tmp[1]
                else:
                    group = tmp[1:]

        argDict['group'] = group
        fixTau = (args.fixtau).lower()
        scanLcurve = (args.scanLcurve).lower()
        if not os.path.exists(argDict['outputDir']):
            os.makedirs(argDict['outputDir'])
        
        lumi = {16:35922, 17:41529, 18:59693}

        upp.unfoldPreProcess(**argDict)
        makeAcceptance(argDict['prefitDir'], argDict['outputDir'], year, argDict['matrix'], argDict['genMode'])
        runUnfold(argDict['outputDir'], year, argDict['genMode'], argDict['recoMode'], scanLcurve, fixTau)
        duo.drawHist(argDict['outputDir'],  lumi[year], 'hist_accept.root', argDict['recoMode'], argDict['genMode'])
        duo.drawHist(argDict['outputDir'],  lumi[year], 'hist_output.root', argDict['recoMode'], argDict['genMode'])
        duo.drawTable(year, argDict['outputDir'], lumi[year], 'hist_output.root', argDict['recoMode'], argDict['genMode'])
