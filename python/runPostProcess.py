import os
import sys
import glob
import time

import multiprocessing as mp
import subprocess
import argparse

from ROOT import *

import python.getQCD as gq
import python.postProcess as pp

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected')

def mergeHist(input_dir):
    tmp = input_dir.split('/')
    output_dir = '/'.join(tmp[:-1])
    input_sample = tmp[-1]
    cmd = ['hadd', str(output_dir)+'/hist_'+str(input_sample)+'.root']+glob.glob(input_dir+'/*')
    subprocess.call(cmd)

def runGentree(year):
    f_txt = open('samples/sample'+str(year)+'.txt','r')
    ntuple_loc = f_txt.readline()[:-1]
    f_txt.close()
    cmd = ['root', '-l', '-b', '-q', 
           'macro/runGentree.C("'+str(ntuple_loc)+'", "'+str(os.getcwd())+"/output/root"+str(year)+'/post")']
    subprocess.call(cmd)

if __name__ == '__main__':
    start_time = time.time()

    parser = argparse.ArgumentParser(description='Run post process')

    parser.add_argument('-y', '--year', required=False, type=int, default=9999, help='Run special year')
    parser.add_argument('-m', '--merge', required=False, type=str2bool, default=False, help='Merge histograms')
    parser.add_argument('-q', '--qcd', required=False, type=str2bool, default=False, help='Get QCD shapes')
    parser.add_argument('-d', '--dnn', required=False, type=str2bool, default=False, help='Get QCD shapes')
    
    args = parser.parse_args()
    year = args.year
    input_dir = os.getcwd()+'/output/root'+str(year)
    if args.qcd: input_dir = os.getcwd()+'/output/root'+str(year)+'_qcd'
    if args.dnn: input_dir = os.getcwd()+'/output/dnn'+str(year)

    if args.merge:
        print "Merge histogram root files"
        procs = []
        dir_list = filter(os.path.isdir, glob.glob(input_dir+'/*'))
        for item in dir_list:
            proc = mp.Process(target=mergeHist, args=(item,))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()

        for item in os.listdir(input_dir):
            if os.path.isdir(input_dir+'/'+item):
                os.system('rm -rf '+input_dir+'/'+item)

        if args.qcd:
            listKind = ['Nosys', 'dataDriven']
            for kind in listKind:
                for lep in ['Mu','EG']:
                    name = input_dir+'/hist_'+kind+'_DataSingle'+lep
                    cmd = ['hadd', name+'.root']+glob.glob(name+'?.root')
                    subprocess.call(cmd)
                    if kind != 'dataDriven': continue
                    listSyst = ['__qcdisoup', '__qcdisodown']
                    for syst in listSyst:
                        name = input_dir+'/hist_'+kind+'_DataSingle'+lep
                        cmd = ['hadd', name+syst+'.root']+glob.glob(name+'*'+syst+'*')
                        subprocess.call(cmd)
        else:
            for lep in ['Mu','EG']:
                cmd = ['hadd', input_dir+'/hist_DataSingle'+lep+'.root']+glob.glob(input_dir+'/hist_DataSingle'+lep+'*')
                subprocess.call(cmd)
        
        
        post_path = os.getcwd()+'/output/root'+str(year)
        if args.dnn and os.path.exists(post_path):
            for sample in os.listdir(input_dir):
                tmp_dir = os.getcwd()+'/output/merge'+str(year)
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)
                cmd = ['hadd', tmp_dir+'/'+sample, post_path+'/'+sample, input_dir+'/'+sample]
                subprocess.call(cmd)

        exit(0)

    if args.qcd:
        gq.getQCDShape(os.getcwd(), year)

    else:
        print("Run gentree")
        runGentree(year)

        print("Run post process")
        procs = []
        for item in os.listdir(input_dir):
            if any(i in item for i in ['__','gen','Data']): continue
            if year == 16 and ((not 'CP5' in item) or 'TT_PowhegPythiaBkg' in item):
                isCP5 = False
            else:
                isCP5 = True
            isCP5 = True
            if not item.endswith('.root'):
                continue
            proc = mp.Process(target=pp.postProcess, args=(input_dir, item, year, isCP5))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()           
        for file in glob.glob(input_dir+'/hist_QCD*'):
            cmd = ['cp',file,input_dir+'/post']
            subprocess.call(cmd)

    print("Total running time: %s" %(time.time() - start_time))
