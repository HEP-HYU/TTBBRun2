import os, sys
from PyQt5 import QtCore, QtWidgets

class MyApp(QtWidgets.QWidget):
    def __init__(self, base_path, batch):
        super(QtWidgets.QWidget,self).__init__()
        
        self.base_path = base_path 
        self.ui_path = os.path.join(self.base_path, 'ui')
        self.func_path = os.path.join(self.base_path, 'func')
        self.macro_path = os.path.join(self.base_path, 'macro')
        self.sample_path = os.path.join(self.base_path, 'samples')
        self.output_path = os.path.join(self.base_path, 'output')
        self.config = []
        self.batch = batch
        self.cfg = ''
        self.cmd = ''
       
        if self.batch:
            self.initUI()
        else:
            self.initGUI()

    from batch import _write_config
    from batch import _select_command

    from gui import _make_layout
    from gui import _make_qle_with_lbl
    from gui import _make_cfg_btn
    from gui import _make_cmd_btn
    from gui import _make_cfg_combo
    from gui import _make_cmd_combo

    from action import _get_config
    from action import _run_cmd
    
    def initGUI(self):
        self._make_layout()
        self.setWindowTitle('ttbb lep+jet analyzer')
        
        self.resize(1200,900)
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        self.show()

    def initUI(self):
        self._write_config()
        while True:
            self.cmd = self._select_command()
            self._run_cmd()
