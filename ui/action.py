import os
import sys
import textwrap

def _get_config(self):
    import yaml
    try:
        with open(os.path.join(self.base_path, self.cfg), 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        if not self.batch: self.cfg_status_lbl.setText(str("Success"))
    except Exception as e:
        if self.batch:
            print(str(e))
        else:
            self.log_qte.append(str(e))
            self.cfg_status_lbl.setText(str("Fail"))

    if not self.batch: self.log_qte.append("Setup configs: "+str(self.config))

def _run_cmd(self):
    try:
        if 'sample' in self.cmd:
            from func import sampleinfo as si
            c = si.SaveSamples(self.config['year'], self.config['ntuple'], self.sample_path)

            if not self.batch: self.cmd_status_lbl.setText(str("Success"))

        elif 'tselector' in self.cmd:
            from func import slurm as sl
            c = sl.MakeSlurmJob(self.config['year'], self.config['ntuple'], self.base_path, 'tselector.py')
            if 'test' in self.cmd:
                c.make_slurm_job(True, False)
            elif 'qcd' in self.cmd:
                c.make_slurm_job(False, True)
            else:
                c.make_slurm_job()

            if not self.batch: self.cmd_status_lbl.setText(str("Success"))
        
        elif 'DNN' in self.cmd:
            if 'model' in self.cmd:
                from func import dnn_model as mm
                model = mm.MakeModel(self.config)
                model.compile_train()
            
            elif 'n2a' in self.cmd:
                from func import slurm as sl
                c = sl.MakeSlurmJob(self.config['year'], self.config['ntuple'], self.base_path, 'dnn_n2a.py')
                c.make_slurm_job()

            elif 'pred' in self.cmd:
                outputDir = self.base_path+'/output/pred'+str(self.config['year'])
                if not os.path.exists(outputDir):
                    os.makedirs(outputDir)
                from func import dnn_pred as pd
                pd.prediction(self.config['year'], self.config['array'], outputDir)

            elif 'hist' in self.cmd:
                from func import slurm as sl
                c = sl.MakeSlurmJob(self.config['year'], self.base_path+'/output/pred'+str(year), self.base_path, 'dnn_ana.py')
                c.make_slurm_job()

            if not self.batch: self.cmd_status_lbl.setText(str("Success"))
        
        elif 'post' in self.cmd:
            from func import postproc as pp
            post = pp.PostProcess(self.base_path, self.output_path, self.config['year'])
            if 'merge' in self.cmd:
                post.merge_hist()
            else:
                post.do_post_process()
            
            if not self.batch: self.cmd_status_lbl.setText(str("Success"))
       
        elif 'qcd' in self.cmd:
            post_path = self.base_path+'/output/post'+str(self.config['year'])
            from func import qcd
            qcd = qcd.GetQCDshape(self.config['year'], self.config['luminosity'], post_path)
            qcd.get_qcd_shape()

        elif 'gen' in self.cmd:
            post_path = self.base_path+'/output/post'+str(self.config['year'])
            from func import genhist as gh
            gen = gh.RunWithGenTree(self.config['ntuple'], 'TTLJ_PowhegPythia_ttbb', post_path)
            gen.run_with_gen_tree()

        elif 'draw' in self.cmd:
            post_path = self.base_path+'/output/post'+str(self.config['year'])
            if 'table' in self.cmd:
                output_path = self.output_path+'/table'+str(self.config['year'])
                
                from func import drawCutflowTable as cf
                table = cf.DrawYieldsTable(self.config['year'], self.config['luminosity'], post_path, output_path)
                table.draw_yields()
                
                if not self.batch: self.cmd_status_lbl.setText(str("Success"))
            elif 'syst' in self.cmd:
                output_path = self.output_path+'/syst'+str(self.config['year'])
                
                from func import drawSystPlots as sp
                hist = sp.DrawSystPlots(self.config['year'], post_path, self.config['hist'], output_path)
                hist.draw_histograms()
                
                if not self.batch: self.cmd_status_lbl.setText(str("Success"))
            elif 'plotIt' in self.cmd:
                text = textwrap.dedent("""\
                    This command only make plotIt config files.
                    If you want to run plotIt, please activate SL7 environment first.
                    Setup command: source plotIt/setup_sl7_env.sh
                    plotIt command: plotIt plotIt/configs/config[YEAR].yml -o output/pdf/[YEAR]
                    """)
                if not self.batch:
                    self.log_qte.append(text)
                else:
                    print text
                
                from func import makePlotItConfigs as mpc
                
                config_path = os.path.join(self.base_path,'plotIt/configs')
                make = mpc.MakeConfigs(self.config['year'], post_path, config_path)
                make.make_file_configs()
                make.make_histogram_configs()
                
                if not self.batch: self.cmd_status_lbl.setText(str("Success"))
        
        elif 'selection' in self.cmd:
            text = textwrap.dedent("""\
                ...Event selection
                Step 0: one lepton
                Step 1: Step 0 + Njets >= 1
                Step 2: Step 0 + 2 <= Njets < 4
                Step 3: Step 0 + Njets >= 4
                Step 4: Step 3 + Nbjets >= 2
                Step 5: Step 0 + 2 <= Njets < 6
                Step 6: Step 0 + Njets >= 6
                Step 7: Step 6 + Nbjets >= 2
                Step 8: Step 6 + Nbjets >= 3
                Step 9: Step 6 + Nbjets >= 4
            """)

            if self.batch:
                print text
            else:
                self.log_qte.append(text)

        else:
            if not self.batch: self.cmd_status_lbl.setText(str("?"))
    
    except Exception as e:
        if not self.batch:
            self.log_qte.append(str(e))
            self.cmd_status_lbl.setText(str('Fail'))
