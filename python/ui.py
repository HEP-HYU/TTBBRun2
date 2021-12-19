import sys
from PyQt5 import QtCore, QtWidgets
#from PyQt5.QtWidgets import  QApplication, QWidget, QDesktopWidget, QPushButton, QLabel
#from PyQt5.QtCore import QCoreApplication, QRect

import button
import var

class MyApp(QtWidgets.QWidget):
    _base_path = '/home/seohyun/work/ttbb/ttbbRun2/'
    _config = []
    def __init__(self, batch):
        if batch:
            self.initUI()
        else:
            super(QtWidgets.QWidget,self).__init__()
            self.initGUI()

    from batch import _select_command
    from batch import _run_command
    from gui import _make_layout
    from gui import _make_cfg_btn
    
    def initGUI(self):
        self.make_layout()
        self.setWindowTitle('ttbb lep+jet analyzer')
        
        self.resize(1200,900)
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        self.show()

    def initUI(self):
        self._set_config()
        cmd = self._select_command()
        self._run_command(cmd)
