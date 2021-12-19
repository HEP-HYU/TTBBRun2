import os
import sys
import textwrap
import subprocess

def make_slurm_job(self, is_test=False, is_qcd=False):
    job_name = str(self.year)+'_plots'
    node = 'gpu'
    opts = 'opt1=$1\nopt2=$2\nopt3=$3\nopt4=$4\nopt5=$5\n\n'
    command = 'python func/%s $opt1 $opt2 $opt3 $opt4 $opt5' % self.target
    script = self.slurm_template.format(job_name=job_name, node=node, opts=opts, command=command)
    script_file = os.path.join(self.base_path, '%s_job_slurm_%d.sh' % (self.target, self.year))
    with open(script_file, 'w') as f:
        f.write(script)

    def make_cmd(input_path, item, output_name, flag, syst=''):
        #input_path, file, outname, flag, syst
        if 'tselector' in self.target.lower():
            #[year, input_path, file, outname, flag]
            options = [str(self.year), input_path, item, output_name+syst, flag]

        if 'array' in self.target.lower():
            #[year, input_path, file, flag, syst]
            options = [str(self.year), input_path, item, flag, syst]

        if 'dnn' in self.target.lower():
            #[year, input_path, file, output_path, outname]
            options = [str(self.year), input_path, item, output_name+syst]

        return ['sbatch',script_file] + options
    
    from func import saveAndLoadSamples as sls
    load = sls.LoadSamples(self.year, self.base_path+'/samples')
    data = load.get_data()
    samples = load.get_samples()
    extsyst = load.get_extsyst()
    
    samples = data + samples
    
    from func import runTSelector as ts
    from func import ntuple2array as ar
    from func import runDNNAnalyzer as da

    #Compile TSelector
    if 'tselector' in self.target.lower():
        ts.runAna(self.year, self.input_path+'/'+self.testset[0], self.testset[1], 'Nosys_Compile', 'False')
    
    if is_test:
        cmd = make_cmd(os.path.join(self.input_path, self.testset[0]), self.testset[1], 'test_ttbb', 'False'))
        subprocess.call(cmd)
    elif is_qcd:
        for sample in samples:
            for item in os.listdir(self.input_path+'/'+sample):
                systlist = ['', '__qcdisoup', '__qcdisodown']
                for syst in systlist:
                    cmd = make_cmd(os.path.join(self.input_path, sample), item, 'dataDriven_'+sample, 'True', syst)
                    subprocess.call(cmd)
    else:
        if 'array' in self.target.lower():
            for item in os.listdir(self.input_path+'/TTLJ_PowhegPythia_ttbb'):
                cmd = make_cmd(os.path.join(self.input_path, 'TTLJ_PowhegPythia_ttbb', item, 'Training', 'True'))
                subprocess.call(cmd)

        for sample in samples:
            for item in os.listdir(self.input_path+'/'+sample):
                cmd = make_cmd(os.path.join(self.input_path, sample), item, sample, 'False')
                subprocess.call(cmd)
       
        for sample in samples:
            if "QCD" in sample or "Data" in sample: continue
            jetsyst = ['jerup','jerdown','jecup','jecdown']
            for syst in jetsyst:
                for item in os.listdir(self.input_path+'/'+sample):
                    cmd = make_cmd(os.path.join(self.input_path, sample), item, sample, 'False', syst)
                    subprocess.call(cmd)

        for syst in extsyst:
            tmp = syst.split('_')
            if 'Bkg' in syst:
                outName = tmp[0]+'_'+tmp[1]+'__'+tmp[-1].lower()
            else:
                outName = tmp[0]+'_'+tmp[1]+'_'+tmp[-1]+'__'+tmp[-2].lower()
            if 'tunecuetp8m4' in outName:
                outName = outName.replace('tunecuetp8m4','tune')
            if 'tunecp5' in outName:
                outName = outName.replace('tunecp5', 'tune')
            for item in os.listdir(self.input_path+'/'+syst):
                cmd = make_cmd(os.path.join(self.input_path, syst), item, outName, 'False']
                subprocess.call(cmd)
