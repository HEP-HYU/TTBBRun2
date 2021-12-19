import sys
from PyQt5 import QtCore, QtWidgets

def _make_layout(self):
    grid = QtWidgets.QGridLayout()
    self.setLayout(grid)

    self.log_qte = QtWidgets.QTextEdit(self)
    
    # Config
    cfg_qle, self.cfg_name_lbl = self._make_qle_with_lbl()
    cfg_btn, self.cfg_status_lbl = self._make_cfg_btn()
    cfg_combo = self._make_cfg_combo()
    
    grid.addWidget(QtWidgets.QLabel("Config:"), 0, 0, 2, 1)
    grid.addWidget(cfg_combo, 0, 1, 1, 1)
    grid.addWidget(cfg_qle, 0, 2, 1, 3)
    grid.addWidget(cfg_btn, 1, 1, 1, 1)
    grid.addWidget(self.cfg_name_lbl, 1, 2, 1, 2)
    grid.addWidget(self.cfg_status_lbl, 1, 4, 1, 1)

    # Command
    cmd_qle, self.cmd_name_lbl = self._make_qle_with_lbl()
    cmd_btn, self.cmd_status_lbl = self._make_cmd_btn()
    cmd_cmb, cmd_sub_cmb = self._make_cmd_combo()

    grid.addWidget(QtWidgets.QLabel("Command:"), 2, 0, 2, 1)
    grid.addWidget(cmd_cmb, 2, 1, 1, 1)
    grid.addWidget(cmd_sub_cmb, 2, 2, 1, 1)
    grid.addWidget(cmd_qle, 2, 3, 1, 2)
    grid.addWidget(cmd_btn, 3, 1, 1, 1)
    grid.addWidget(self.cmd_name_lbl, 3, 2, 1, 2)
    grid.addWidget(self.cmd_status_lbl, 3, 4, 1, 1)

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
    def set_cfg(label):
        self.cfg = label.text()

    label = QtWidgets.QLabel("Status")
    btn = QtWidgets.QPushButton('Setup', self)
    btn.clicked.connect(lambda: set_cfg(self.cfg_name_lbl))
    btn.clicked.connect(lambda: self._get_config())
    
    return btn, label

def _make_cmd_btn(self):
    def set_cmd(label):
        self.cmd = label.text()

    label = QtWidgets.QLabel("Status")
    btn = QtWidgets.QPushButton('Run', self)
    btn.clicked.connect(lambda: set_cmd(self.cmd_name_lbl))
    btn.clicked.connect(lambda: self._run_cmd())

    return btn, label

def _make_cfg_combo(self):
    def select_combo(label):
        label.setText(cb.currentText())

    cb = QtWidgets.QComboBox(self)
    cb.addItem('')
    cb.addItem('configs/config16.yml')
    cb.addItem('configs/config17.yml')
    cb.addItem('configs/config18.yml')
    cb.currentTextChanged.connect(lambda: select_combo(self.cfg_name_lbl))

    return cb

def _make_cmd_combo(self):
    def select_combo(cb, cb2, label):
        if not cb2.currentText() == '':
            label.setText(cb.currentText()+'/'+cb2.currentText())
        else:
            label.setText(cb.currentText())
    
    def make_subcombo(cb):
        cb2.clear()
        if cb.currentText() == 'tselector':
            cb2.addItem('')
            cb2.addItem('test')
            cb2.addItem('qcd')
            cb2.addItem('common')
        elif cb.currentText() == 'DNN':
            cb2.addItem('')
            cb2.addItem('model')
            cb2.addItem('n2a')
            cb2.addItem('pred')
            cb2.addItem('hist')
        elif cb.currentText() == 'post':
            cb2.addItem('')
            cb2.addItem('merge')
            cb2.addItem('scale')
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
    cb.addItem('selection')
    cb.addItem('sample')
    cb.addItem('tselector')
    cb.addItem('DNN')
    cb.addItem('qcd')
    cb.addItem('post')
    cb.addItem('draw')
    
    cb.currentTextChanged.connect(lambda: select_combo(cb, cb2, self.cmd_name_lbl))
    cb.currentTextChanged.connect(lambda: make_subcombo(cb))
    cb2.currentTextChanged.connect(lambda: select_combo(cb, cb2, self.cmd_name_lbl))

    return cb, cb2
