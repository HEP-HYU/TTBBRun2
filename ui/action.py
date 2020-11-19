import os
import sys

def _get_config(self):
    import yaml
    try:
        with open(os.path.join(self._base_path, self.cfg), 'r') as f:
            self._config = yaml.load(f, Loader=yaml.FullLoader)
        if not self.batch: self.cfg_status_lbl.setText(str("Success"))
    except Exception as e:
        if self.batch:
            print(str(e))
        else:
            self.log_qte.append(str(e))
            self.cfg_status_lbl.setText(str("Fail"))

    if not self.batch: self.log_qte.append("Setup configs: "+str(self._config))

def _run_cmd(self):
    try:
        if 'sample' in self.cmd:
            from func import saveAndLoadSamples as sls
            c = sls.SaveSamples(self._config['year'], self._config['ntuple'], self._base_path+'/samples')

            if not self.batch: self.cmd_status_lbl.setText(str("Success"))

        elif 'tselector' in self.cmd:
            from func import makeSlurmJob as sj
            c = sj.MakeSlurmJob(self._config['year'], self._config['ntuple'], self._base_path)
            if 'test' in self.cmd:
                c.make_slurm_job(True, False)
            elif 'qcd' in self.cmd:
                c.make_slurm_job(False, True)
            else:
                c.make_slurm_job()

            if not self.batch: self.cmd_status_lbl.setText(str("Success"))
            
        else:
            print "MELONA"

        """
        elif 'DNN' in cmd.text():
            if 'model' in cmd.text():
                import makeModel as mm
                train_input = ''
                config_file = ''
                model = mm.MakeModel(train_input, config_file)
                model.load_config()
                model.compile_train()
                model.save_config()
            
            elif 'n2a' in cmd.text():
                outputDir = '../output/array'+str(self.config['year'])
                for item in os.listdir(inputDir+'/TTLJ_PowhegPythia_ttbb'):
                    cmd = ['sbatch','slurm_n2a.sh',inputDir+'/TTLJ_PowhegPythia_ttbb',item,outputDir+'/Training','True','']
                    subprocess.call(cmd)
                for sample in os.listdir(inputDir):
                    outputDir = '../output/array'+str(year)+'/'+sample
                    if 'part' in sample: continue
                    for item in os.listdir(inputDir+'/'+sample):
                        cmd = ['sbatch','slurm_n2a.sh',inputDir+'/'+sample,item,outputDir,'False']
                        subprocess.call(cmd)
                    if not any(i in sample for i in ['QCD','Data','SYS']):
                        jetSyst = ['jerup','jerdown','jecup','jecdown']
                        for syst in jetSyst:
                            outputDir = '../output/array'+str(year)+'/'+sample+'__'+syst
                            for item in os.listdir(inputDir+'/'+sample):
                                cmd = ['sbatch','slurm_n2a.sh',inputDir+'/'+sample,item,outputDir,'False',syst]
                                subprocess.call(cmd)
            
            elif 'pred' in cmd.text():
               inputDir = '../output/array'+str(config['year'])
                outputDir = '../output/pred'+str(config['year'])
                if not os.path.exists(outputDir):
                    os.makedirs(outputDir)
                import prediction as pred
                pred.prediction(year, inputDir, outputDir)

            elif 'hist' in cmd.text():
                arrayDir  = '../output/pred'+str(config['year'])
                outputDir = '../output/dnn'+str(config['year'])
                if not os.path.exists(outputDir):
                    os.makedirs(outputDir)
                procs = []
                for sample in os.listdir(arrayDir):
                    #if not 'DataSingleMuB' in sample: continue
                    if 'Training' in sample: continue
                    if 'SYS' in sample:
                        tmp = sample.split('_')
                        if 'Bkg' in sample:
                            outName = tmp[0]+'_'+tmp[1]+'__'+tmp[-1].lower()
                        else:
                            outName = tmp[0]+'_'+tmp[1]+'_'+tmp[-1]+'__'+tmp[-2].lower()
                    else:
                        outName = sample
                    if 'tunecuetp8m4' in outName:
                        outName = outName.replace('tunecuetp8m4','tune')
                    if 'tunecp5' in outName:
                        outName = outName.replace('tunecp5', 'tune')
                    outputDir = '../output/dnn'+str(year)+'/'+outName
                    if not os.path.exists(outputDir):
                        os.makedirs(outputDir)
                    for item in os.listdir(os.path.join(arrayDir,sample)):
                        cmd = ['sbatch', 'slurm_a2h.sh', str(year), arrayDir+'/'+sample, item, outputDir, outName]
                        subprocess.call(cmd)

            else:
                label.setText(str('Not yet'))

        elif 'post' in cmd.text():
            print "melona"
        elif 'draw' in cmd.text():
            if 'table' in cmd.text():
            elif 'syst' in cmd.text():
            elif 'plotIt' in cmd.text():
            else:
            print "melona"
        else:
            label.setText(str("Not yet"))
        """
    except Exception as e:
        if not self.batch:
            self.log_qte.append(str(e))
            self.cmd_status_lbl.setText(str('Fail'))
