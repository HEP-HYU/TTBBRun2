import os
import sys
import argparse
from PyQt5 import QtWidgets

sys.path.append(os.getcwd())

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'): return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'): return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Anlyzer')
    parser.add_argument('-b', '--batch', required=False, type=str2bool, default=False, help='batch mode')
    options = parser.parse_args()

    base_path = os.getcwd()
    from ui import ui
    app = QtWidgets.QApplication(sys.argv)
    ex = ui.MyApp(base_path, options.batch)
    sys.exit(app.exec_())
