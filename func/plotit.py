import os
import sys

import ROOT

strHistConfigTemplate = """\
'{name}':
  y-axis: "Events"
  y-axis-format: "%1%"
  save-extensions: ['pdf']
  show-ratio: true
  {options}
"""

strFileConfigTemplate = """\
'{name}':
  type: {type}
  pretty-name: '{prettyname}'
{options}
"""

strMCOptionsTemplate = """\
  cross-section: {xsec}
  generated-events: {genevt}
  fill-color: '{color}'
  group: {group}
  order: {order}
""" 

class MakeConfigs:
    def __init__(self, year, root_path, output_path):
        self.year = year
        self.root_path = root_path
        self.output_path = output_path

    def make_histogram_configs(self):
        f_tmp = ROOT.TFile(os.path.join(self.root_path, 'hist_DataSingleMu.root'))
        hist_list = [x.GetName() for x in f_tmp.GetListOfKeys()]

        str_bank = []
        for hist in hist_list:
            if any(i in hist for i in ['Resp', 'Info', 'Weights', 'bSF']): continue
            TH1 = f_tmp.Get(hist)
            if TH1.InheritsFrom('TH2') or TH1.InheritsFrom('TH3'): continue
            str_config = strHistConfigTemplate.format(name=hist, options='#log-y: true')
            str_bank.append(str_config)

        config = open(os.path.join(self.output_path, 'histos.yml'), 'w')
        str_out = '\n'.join(item for item in str_bank)
        config.write(str_out)
        config.close()

    def make_file_configs(self):
        str_bank = []
        
        data_options = "  legend: 'Data'\n  marker-size: 0.6\n  group: GData"
        
        temp = strFileConfigTemplate.format(name='hist_DataSingleMu.root', type='data', legend='data',
            prettyname='DataSingleMu', options=data_options)
        str_bank.append(temp)

        temp = strFileConfigTemplate.format(name='hist_DataSingleEG.root', type='data', legend='data',
            prettyname='DataSingleEG', options=data_options)
        str_bank.append(temp)

        genevt = {}
        with open('./samples/genevt'+str(self.year)+'.txt','r') as f:
            while True:
                line = f.readline()
                if not line: break
                tmp = line.split(' ')
                genevt[tmp[0]] = float(tmp[1])

        with open('./samples/xsec'+str(self.year)+'.txt','r') as f:
            while True:
                line = f.readline()
                if not line: break
                if 'Sample' in line: continue
                tmp = line.split(' ')
                sample = tmp[0]
                xsec = float(tmp[1])
                order = int(tmp[2])
                color = tmp[3]
                legend = tmp[4][:-1]
                if order < 0: continue

                group = 'G'+legend
                
                mc_options = strMCOptionsTemplate.format(xsec=str(xsec), genevt=str(genevt[sample]),
                        color=str(color), group=str(group), order=str(order))
                temp = strFileConfigTemplate.format(name='hist_'+sample+'.root', type='mc', legend=legend,
                        prettyname=sample, options=mc_options)
                str_bank.append(temp)

        config = open(os.path.join(self.output_path, 'files'+str(self.year)+'.yml'), 'w')
        str_out = '\n'.join(item for item in str_bank)
        config.write(str_out)
        config.close()
