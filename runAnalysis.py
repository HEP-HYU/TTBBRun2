#!/usr/bin/python
import os
import sys
import subprocess
import argparse

import python.storeSampleInfo
import python.getQCD
import python.runTSelector

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze ntuples')

    parser.add_argument('-y', '--year', required=False, type=int, default=9999, help='Run special year')
    parser.add_argument('-t', '--test', required=False, type=str2bool, default=False, help='Run test sample')
    parser.add_argument('-q', '--qcd',  required=False, type=str2bool, default=False, help='QCD estimation')

    args = parser.parse_args()

    run16  = False 
    run17  = False 
    run18  = False

    if args.year == 16 or args.year == 2016: run16 = True
    if args.year == 17 or args.year == 2017: run17 = True
    if args.year == 18 or args.year == 2018: run18 = True
    if args.year == 9999:
        run16 = True
        run17 = True
        run18 = True

    #python.storeSampleInfo.storeSampleList(os.getcwd()+'/samples')
    #python.storeSampleInfo.storeNumberOfEvents(os.getcwd()+'/samples')

    for year in range(16,19):
        if year == 16 and run16 == False: continue
        if year == 17 and run17 == False: continue
        if year == 18 and run18 == False: continue

        samples = []
        with open('samples/sample'+str(year)+'.txt','r') as f:
            n = 1
            while True:
                line = f.readline()
                if not line: break
                if n == 1:
                    inputDir = line[:-1]
                else:
                    samples.append(line[:-1])
                n += 1

        data = []
        with open('samples/data'+str(year)+'.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line: break
                data.append(line[:-1])
        
        samples += data
                   
        #Compile TSelector
        python.runTSelector.runAna(year, inputDir+"/TTLJ_PowhegPythia_ttbb", "Tree_ttbbLepJets_000.root", "Nosys_Compile", "False")
        
        if args.test:
            python.runTSelector.runAna(year, inputDir+'/TTLJ_PowhegPythia_ttbb', 'Tree_ttbbLepJets_000.root', 'Test_ttbb', 'False')
            #testDataset = ['TTLJ_PowhegPythia_ttbb', 'TTLJ_PowhegPythiaCP5_ttbb', 'ttWToLNu_aMCatNLOMadspinPythia', 'TTLL_PowhegPythiaTuneCP5_ttbkg', 'TT_PowhegPythiaBkg_SYS_ISRDown']
            #for sample in testDataset:
                #cmd = ['sbatch','job_slurm.sh', str(year), inputDir+'/'+sample, 'Tree_ttbbLepJets_000.root', sample, 'False']
                #subprocess.call(cmd)
                #for item in os.listdir(inputDir+'/'+sample):
                #    cmd = ['sbatch','job_slurm.sh', str(year), inputDir+'/'+sample, item, sample, 'False']
                #    subprocess.call(cmd)
                #jetsyst = ['jerup','jerdown','jecup','jecdown']
                #for syst in jetsyst:
                #    for item in os.listdir(inputDir+'/'+sample):
                #        cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,sample+'__'+syst,'False']
                #        subprocess.call(cmd)

        elif args.qcd:
            for sample in samples:
                for item in os.listdir(inputDir+'/'+sample):
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,'Nosys_'+sample,'False']
                    subprocess.call(cmd)
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,'dataDriven_'+sample,'True']
                    subprocess.call(cmd)
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,'dataDriven_'+sample+'__qcdisoup','True']
                    subprocess.call(cmd)
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,'dataDriven_'+sample+'__qcdisodown','True']
                    subprocess.call(cmd)
            #python.getQCD.getQCDShape(os.getcwd(), year, samples)
        else:
            for sample in samples:
                for item in os.listdir(inputDir+'/'+sample):
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,sample,'False']
                    subprocess.call(cmd)
           
            for sample in samples:
                if "QCD" in sample or "Data" in sample: continue
                jetsyst = ['jerup','jerdown','jecup','jecdown']
                for syst in jetsyst:
                    for item in os.listdir(inputDir+'/'+sample):
                        cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,sample+'__'+syst,'False']
                        subprocess.call(cmd)
 
            extSystematics = [] 
            with open('samples/systematic'+str(year)+'.txt', 'r') as f:
                while True:
                    line = f.readline()
                    if not line: break
                    extSystematics.append(line[:-1])
          
            for syst in extSystematics:
                tmp = syst.split('_')
                if 'Bkg' in syst:
                    outName = tmp[0]+'_'+tmp[1]+'__'+tmp[-1].lower()
                else:
                    outName = tmp[0]+'_'+tmp[1]+'_'+tmp[-1]+'__'+tmp[-2].lower()
                if 'tunecuetp8m4' in outName:
                    outName = outName.replace('tunecuetp8m4','tune')
                if 'tunecp5' in outName:
                    outName = outName.replace('tunecp5', 'tune')
                for item in os.listdir(inputDir+'/'+syst):
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+syst,item,outName,'False']
                    subprocess.call(cmd)
