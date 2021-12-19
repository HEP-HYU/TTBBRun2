import os
import sys
import ROOT

class SaveSamples:
    def __init__(self, year, ntuple_path, output_path):
        self.year = year
        self.ntuple_path = ntuple_path
        self.output_path = output_path
        
        self._store_sample_list()
        self._store_nevents()
    
    def _store_sample_list(self):
        f_data = open(self.output_path+'/data'+str(self.year)+'.txt','w')
        f_mc   = open(self.output_path+'/sample'+str(self.year)+'.txt', 'w')
        f_syst = open(self.output_path+'/systematic'+str(self.year)+'.txt','w')

        f_mc.write(self.output_path+'\n')

        for item in os.listdir(self.ntuple_path):
            if not os.path.isdir(self.ntuple_path+'/'+item): continue
            if 'part' in item: continue
            print item
            if 'Data' in item:
                f_data.write(item+'\n')
            elif any(i in item for i in ['Herwig','Evtgen','TT_aMC','SYS']):
                f_syst.write(item+'\n')
            else:
                f_mc.write(item+'\n')

        f_data.close()
        f_mc.close()
        f_syst.close()

    def _store_nevents(self):
        f_out = open(self.output_path+'/genevt'+str(self.year)+'.txt','w')
        
        for item in os.listdir(self.ntuple_path):
            if not os.path.isdir(self.ntuple_path+'/'+item): continue
            if any(i in item for i in ['Data','part']): continue
            nevts = 0.0
            for file in os.listdir(os.path.join(self.ntuple_path,item)):
                TFile = ROOT.TFile.Open(os.path.join(self.ntuple_path,item,file))
                EventInfo = TFile.Get('ttbbLepJets/EventInfo')
                nevts += EventInfo.GetBinContent(2)
                TFile.Close()
            f_out.write("%s: %f\n" % (item, nevts))
            print "%s: %f" % (item, nevts)
        f_out.close()

class LoadSamples:
    def __init__(self, year, text_path):
        self.year = year
        self.text_path = text_path
        self.data = []
        self.samples = []
        self.extsyst = []
        self.xsecs = {}
        self.genevt = {}
        
        self._get_sample_info()

    def get_data(self):
        return self.data

    def get_samples(self):
        return self.samples

    def get_extsyst(self):
        return self.extsyst

    def get_xsecs(self):
        return self.xsecs

    def get_genevt(self):
        return self.genevt
    
    def _get_sample_info(self):
        with open(self.text_path+'/data'+str(self.year)+'.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line: break
                self.data.append(line[:-1])

        with open(self.text_path+'/sample'+str(self.year)+'.txt', 'r') as f:
            while True:
                line = f.readline()
                if '/data/' in line: continue
                if not line: break
                self.samples.append(line[:-1])

        with open(self.text_path+'/systematic'+str(self.year)+'.txt', 'r') as f:
            while True:
                line = f.readline()
                if '/data/' in line: continue
                if not line: break
                self.extsyst.append(line[:-1])
        
        with open(self.text_path+'/xsec'+str(self.year)+'.txt','r') as f:
            while True:
                line = f.readline()
                if 'Xsec' in line: continue
                if not line: break
                tmp = line.split(' ')
                if int(tmp[2]) < 0: continue
                if not tmp[0] in self.samples: continue
                self.xsecs[int(tmp[2])] = [tmp[0], float(tmp[1])]

        with open(self.text_path+'/genevt'+str(self.year)+'.txt','r') as f:
            while True:
                line = f.readline()
                if not line: break
                tmp = line.split(' ')
                self.genevt[tmp[0]] = float(tmp[1])
