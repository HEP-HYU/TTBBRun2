import os

import var

class test:
    def __init__(self, text):
        self.text = text

    def load_yaml(self):
        var.CONFIGS_ = {}
        import yaml
        try:
            with open('/home/seohyun/work/ttbb/ttbbRun2/'+self.text, 'r') as f:
                var.CONFIGS_ = yaml.load(f, Loader=yaml.FullLoader)
            return True
        except Exception as e:
            return False


