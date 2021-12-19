import os
import sys

import ROOT

import saveAndLoadSamples as sls

strTableTemplate = """
\\begin{table}[htb]
  \\rotatebox{90}{
  \\footnotesize
  \\begin{center}
	\\caption{%(year)s yields table}
	\\begin{tabular}{%(nRows)s}
      \\hline\\hline
      Sample & Ch0S0 & Ch0S1 & Ch0S2 & Ch1S0 & Ch1S1 & Ch1S2 & Ch2S0 & Ch2S1 & Ch2S2 \\\\
      \\hline
%(mcNevts)s
      \\hline
%(dataNevts)s
%(totalMC)s
%(ratio)s
      \\hline\\hline
    \\end{tabular}
  \\end{center}
  }
\\end{table}
"""

class DrawYieldsTable(sls.LoadSamples):
    def __init__(self, year, lumi, root_path, output_path, hist_name='h_nJets'):
        self.year = year
        self.lumi = float(lumi)
        self.root_path = root_path
        self.output_path = output_path
        self.hist_name = hist_name

        self.data = {}
        self.samples = {}
        self.xsecs = {}
        self.genevt = {}

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        self._get_root_files()
        
    def _get_root_files(self):
        self.get_sample_info()

        self.data['Muon'] = ROOT.TFile(os.path.join(self.root_path, 'hist_DataSingleMu.root'))
        self.data['Electron'] = ROOT.TFile(os.path.join(self.root_path, 'hist_DataSingleEG.root'))
        for sample in self.xsecs.values():
            self.samples[sample[0]] = ROOT.TFile(os.path.join(self.root_path, 'hist_'+sample[0]+'.root'))

    def draw_yields(self):
        for ich in range(0,3):
            steps = [1,3,4,6,7,8,9]
            
            data_nevts = []
            data_str = '     Data ' 
            for istep in steps:
                if ich == 0:
                    TH1 = self.data['Muon'].Get(self.hist_name+'_Ch0_S'+str(istep))
                elif ich == 1:
                    TH1 = self.data['Electron'].Get(self.hist_name+'_Ch1_S'+str(istep))
                else:
                    TH1 = self.data['Muon'].Get(self.hist_name+'_Ch0_S'+str(istep))
                    TH1temp = self.data['Electron'].Get(self.hist_name+'_Ch1_S'+str(istep))
                    TH1.Add(TH1temp)

                error = ROOT.Double()
                nevts = TH1.IntegralAndError(1, TH1.GetNbinsX()+1, error)
                data_str += '& $%.1f $ ' % (nevts)
                data_nevts.append(nevts)
            data_str += '\\\\\n'
           
            mc_nevts = [0.0 for i in range(len(steps))]
            mc_error = [0.0 for i in range(len(steps))]
            mc_dicts = {}
            for item in self.xsecs.items():
                sample_name = item[1][0]
                xsec = item[1][1]
                sample = self.samples[sample_name]
                scale = (self.lumi*xsec/self.genevt[sample_name])

                temp = '      %s ' % (sample_name)
                for idx, istep in enumerate(steps):
                    TH1 = sample.Get(self.hist_name+'_Ch'+str(ich)+'_S'+str(istep))
                    TH1.Scale(scale)
                    
                    #nevts = hist_tmp.Integral(0, hist_tmp.GetNbinsX()+1)
                    error = ROOT.Double()
                    nevts = TH1.IntegralAndError(1, TH1.GetNbinsX()+1, error)
                    
                    temp += '& $%.1f {\scriptstyle\ \pm\ %.1f}$ ' % (nevts, error)
                    mc_nevts[idx] += nevts
                    import math
                    mc_error[idx] = math.sqrt(pow(mc_error[idx],2) + pow(error,2))
                temp += '\\\\\n'
                mc_dicts[item[0]] = temp
    
            totalMC = '      TotalMC '
            ratio = '      Ratio '
            for idx, value in enumerate(mc_nevts):
                temp = float(data_nevts[idx])/float(value)
                totalMC += '& $%.1f {\scriptstyle\ \pm\ %.1f}$ ' % (value, mc_error[idx])
                ratio += ' & $%.2f$ ' % temp
            totalMC += '\\\\'
            ratio += '\\\\'
        
            str_dict = {}
            str_dict['year'] = str(self.year)
            str_dict['nRows'] = '|'+'c|'*len(steps)
            str_dict['mcNevts'] = '\n'.join(value for value in mc_dicts.values())
            str_dict['dataNevts'] = data_str
            str_dict['totalMC'] = totalMC
            str_dict['ratio'] = ratio

            strOut = strTableTemplate % str_dict
            with open(self.output_path+"/yields"+str(self.year)+'_ch'+str(ich)+".tex", 'w') as f: f.write(strOut)
