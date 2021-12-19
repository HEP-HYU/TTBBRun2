#!/usr/bin/python
import os
import sys
import subprocess

from ROOT import TChain, TFile, TH1D, TH1F, TCanvas

import var

class RunTSelector:
    def __init__(self, year, ntuple_path):
        self.year = year
        self.ntuple_path = ntuple_path

    def make_slurm_job(self, is_test=False, is_qcd=False):
        import templateBook as tb
        job_name = str(self.year)+'_plots'
        node = 'gpu'
        opts = 'opt1\nopt2\nopt3\nopt4\nopt5\n\n'
        command = 'python python/runTSelector.py $opt1 $opt2 $opt3 $opt4 $opt5'
        script = tb.strSlurmTemplate.format(job_name=job_name, node=node, opts=opts, command=command)
        
        import runTSelector
        #Compile TSelector
        runTSelector.runAna(self.year, self.ntuple_path+"/TTLJ_PowhegPythia_ttbb", "Tree_ttbbLepJets_000.root", "Nosys_Compile", "False")
        
        if is_test:
            runTSelector.runAna(self.year, self.ntuple_path+'/TTLJ_PowhegPythia_ttbb', 'Tree_ttbbLepJets_000.root', 'Test_ttbb', 'False')
        elif is_qcd:
            for sample in samples:
                for item in os.listdir(inputDir+'/'+sample):
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,'dataDriven_'+sample,'True']
                    subprocess.call(cmd)
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,'dataDriven_'+sample+'__qcdisoup','True']
                    subprocess.call(cmd)
                    cmd = ['sbatch','job_slurm.sh',str(year),inputDir+'/'+sample,item,'dataDriven_'+sample+'__qcdisodown','True']
                    subprocess.call(cmd)
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
            with open(var.BASE_PATH_+'/samples/systematic'+str(year)+'.txt', 'r') as f:
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
