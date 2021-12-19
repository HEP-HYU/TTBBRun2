import os
import sys
import multiprocessing as mp
import subprocess
from array import array

import ROOT

class RunPostProcess:
    def __init__(self, base_path, input_path, year):
        self.base_path = base_path
        self.input_path = input_path
        self.year = year

        self.root_dir = os.path.join(self.input_path, 'root'+str(self.year))
        self.dnn_dir = os.path.join(self.input_path, 'dnn'+str(self.year))
        self.qcd_dir = os.path.join(self.input_path, 'qcd'+str(self.year))
        self.merge_dir = os.path.join(self.input_path, 'merge'+str(self.year))
        
        self.ctl = False
        self.dnn = False
        self.qcd = False

        self._check_directory()
        self._load_samples()

    from postproc_merge import _merge_root
    from postproc_merge import do_merge_root

    from postproc_post import _normalize_by_bSF
    from postproc_post import _rescale_extsample
    from postproc_post import _write_envelope
    from postproc_post import _execute_postprocess

    def _check_directory(self):
        self.ctl = os.path.exists(self.root_dir)
        self.dnn = os.path.exists(self.dnn_dir)
        self.qcd = os.path.exists(self.qcd_dir)

        if self.ctl:
           print("...%s exists" % self.root_dir)
        else:
           print("...%s does not exist" % self.root_dir)
        
        if self.dnn:
           print("...%s exists" % self.dnn_dir)
        else:
           print("...%s does not exist" % self.dnn_dir)

        if self.qcd:
           print("...%s exists" % self.qcd_dir)
        else:
           print("...%s does not exist" % self.qcd_dir)

    def _load_samples(self):
        from func import saveAndLoadSamples as sls
        load = sls.LoadSamples(self.year, self.base_path+'/samples')
        self.data = load.get_data()
        self.samples = load.get_samples()
        extntuple = load.get_extsyst()
        self.extsyst = []

        for sample in self.samples:
            if any(i in sample for i in ['Data','QCD']):
                self.samples.remove(sample)

        for syst in extntuple:
            tmp = syst.split('_')
            if 'Bkg' in syst:
                name = tmp[-1].lower()
            else:
                name = tmp[-2].lower()
            name = name.replace('up', '')
            name = name.replace('down', '')
            if 'tunecuetp8m4' in name:
                name = name.replace('tunecuetp8m4', 'tune')
            if 'tunecp5' in name:
                name = name.replace('tunecp5', 'tune')
            self.extsyst.append(name)
        tmpset = set(self.extsyst)
        self.extsyst = list(tmpset)

    def do_postprocess(self):
        print("...Run post process")
        if not os.path.exists(self.input_path+'/post'):
            try:
                os.makedirs(self.input_path+'/post')
            except OSError:
                print(self.input_path+'/post: already exists')
        
        procs = []
        for item in os.listdir(input_dir):
            if any(i in item for i in ['__','gen','Data']): continue
            if not item.endswith('.root'): continue
            proc = mp.Process(target=self._execute_postprocess, args=(input_dir, item, year))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()
        for file in glob.glob(input_dir+'/hist_QCD*'):
            cmd = ['cp',file,input_dir+'/post']
            subprocess.call(cmd)
