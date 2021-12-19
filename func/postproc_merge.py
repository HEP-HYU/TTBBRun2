import os
import subprocess
import glob

def _merge_root(self, input_dir):
    tmp = input_dir.split('/')
    output_dir = '/'.join(tmp[:-1])
    input_root = tmp[-1]
    cmd = ['hadd', str(out_path)+'/hist_'+str(input_root)+'.root']+glob.glob(self.input_path+'/*')
    subprocess.call(cmd)

def do_merge_root(self):
    print("...Merge root files")
    dirs = []
    if self.ctl: dirs += filter(os.path.isdir, glob.glob(self.root_dir+'/*'))
    if self.dnn: dirs += filter(os.path.isdir, glob.glob(self.dnn_dir+'/*'))
    
    proc = []
    for item in dirs:
        proc = mp.Process(target=self._merge_root, args=(item,))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()

    for item in dirs:
        os.system('rm -rf '+item)

    for directory in [self.root_dir, self.dnn_dir, self.qcd_dir]
        files = filter(os.path.isfile, glob.glob(directory+'/*'))
        data = {'Mu':[],'EG':[]}
        for item in files:
            result = item.find('Data')
            if not result < 0:
                if 'Mu' in item:
                    data['Mu'].append(item)
                else:
                    data['EG'].append(item)

        for lep in ['Mu','EG']:
            loc = data[lep].find(lep)
            name = data[lep][:result+2]+'.root'
            cmd = ['hadd', name]+data[lep]
            subprocess.call(cmd)

    if self.ctl and self.dnn:
        if not os.path.exists(self.merge_dir):
            os.makedirs(tmp_dir)
        for sample in os.listdir(self.root_dir):
            cmd = ['hadd', self.merge_dir+'/'+sample, self.root_dir+'/'+sample, self.dnn_dir+'/'+sample]
            subprocess.call(cmd)
