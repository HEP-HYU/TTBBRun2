import sys
from PyQt5 import QtCore, QtWidgets
#from PyQt5.QtWidgets import  QApplication, QWidget, QDesktopWidget, QPushButton, QLabel
#from PyQt5.QtCore import QCoreApplication, QRect

import button
import var

def _make_layout(self):
    grid = QtWidgets.QGridLayout()
    self.setLayout(grid)

    self.log_qte = QtWidgets.QTextEdit(self)
    
    # Config
    cfg_qle, self.cfg_status_lbl = self._make_qle_with_lbl()
    cfg_btn, self.cfg_name_lbl = self._make_cfg_btn()
    cfg_combo = self.make_cfg_combo()
    
    grid.addWidget(QtWidgets.QLabel("Config:"), 0, 0, 2, 1)
    grid.addWidget(cfg_combo, 0, 1, 1, 1)
    grid.addWidget(cfg_qle, 0, 2, 1, 3)
    grid.addWidget(cfg_btn, 1, 1, 1, 1)
    grid.addWidget(self.cfg_name_lbl, 1, 2, 1, 2)
    grid.addWidget(self.cfg_status_lbl, 1, 4, 1, 1)

    # Command
    cmd_qle, self.cmd_status_lbl = self._make_qle_with_lbl()
    cmd_btn, self.cmd_name_lbl = self._make_cmd_btn()
    cmd_cmb, cmd_sub_cmb = self._make_cmd_combo()

    grid.addWidget(QtWidgets.QLabel("Command:"), 2, 0, 2, 1)
    grid.addWidget(cmd_cmb, 2, 1, 1, 1)
    grid.addWidget(cmd_sub_cmb, 2, 2, 1, 1)
    grid.addWidget(cmd_qle, 2, 3, 1, 2)
    grid.addWidget(cmd_btn, 3, 1, 1, 1)
    grid.addWidget(self.cmd_status_lbl, 3, 2, 1, 2)
    grid.addWidget(self.cmd_name_lbl, 3, 4, 1, 1)

    # Log
    grid.addWidget(QtWidgets.QLabel("Log:"), 4, 0)
    grid.addWidget(self.log_qte, 4, 1, 1, 4)

def _make_qle_with_lbl(self):
    def change_label(qle, label):
        label.setText(qle.text())

    label = QtWidgets.QLabel(self) 
    qle = QtWidgets.QLineEdit(self)
    qle.textChanged.connect(lambda: change_label(qle, label))
    qle.returnPressed.connect(lambda: change_label(qle, label))

    return qle, label

def _make_cfg_btn(self):
    label = QtWidgets.QLabel("Status")
    btn = QtWidgets.QPushButton('Setup', self)
    btn.clicked.connect(lambda: self._get_config(label))
    
    return btn, label

def _make_cmd_btn(self):
    label = QtWidgets.QLabel("Status")
    btn = QtWidgets.QPushButton('Run', self)
    btn.clicked.connect(lambda: self._run_cmd(label, self.label_run_stat, self.qte))

    return btn, label

def _make_cfg_combo(self):
    def select_combo(label):
        label.setText(cb.currentText())

    cb = QtWidgets.QComboBox(self)
    cb.addItem('')
    cb.addItem('configs/config16.yml')
    cb.addItem('configs/config17.yml')
    cb.addItem('configs/config18.yml')
    cb.currentTextChanged.connect(lambda: select_combo(self.label_cfg_stat))

    return cb

def _make_cmd_combo(self):
    def select_combo(label):
        if not cb2.currentText() == '':
            label.setText(cb.currentText()+'/'+cb2.currentText())
        else:
            label.setText(cb.currentText())
    
    def make_subcombo(cb):
        cb2.clear()
        if cb.currentText() == 'DNN':
            cb2.addItem('')
            cb2.addItem('model')
            cb2.addItem('n2a')
            cb2.addItem('pred')
            cb2.addItem('hist')
        elif cb.currentText() == 'draw':
            cb2.addItem('')
            cb2.addItem('table')
            cb2.addItem('syst')
            cb2.addItem('plotIt')
        else:
            cb2.addItem('')

    cb = QtWidgets.QComboBox(self)
    cb2 = QtWidgets.QComboBox(self)
    
    cb.addItem('')
    cb.addItem('sample')
    cb.addItem('tselector')
    cb.addItem('DNN')
    cb.addItem('qcd')
    cb.addItem('post')
    cb.addItem('draw')
    
    cb.currentTextChanged.connect(lambda: select_combo(self.label_run_stat))
    cb.currentTextChanged.connect(lambda: make_subcombo(cb))
    cb2.currentTextChanged.connect(lambda: select_combo(self.label_run_stat))

    return cb, cb2
