import os
import sys
import subprocess
import argparse
from argparse import RawTextHelpFormatter
import textwrap

def _write_config(self):
    print textwrap.dedent("""\
        ...Write config file's location and name
        ...Default config file: configs/config16.yml
    """)
    loc = raw_input("...Config file: ")
    self._get_config(loc)

def _select_command(self):
    print textwrap.dedent("""\
        ...Select run option 
        1. sample: save ntuple information 
        2. tselector: run tselector for basic plots
        3. dnn: run dnn analyzer code
        4. qcd: run tselector for qcd estimation
        5. post: run post process
        6. draw: draw cut flow table and histograms\
    """)

    cmd = raw_input("...Choose option: sample/tselector/dnn/qcd/post/draw/exit ")
    if not any(i in cmd for i in ['sample','tselector','dnn','qcd','post','draw','exit']):
        print "...Wrong command"
        exit(0)
    if cmd == "exit":
        exit(0)
   
    sub_cmd = ''
    if cmd == 'dnn':
        print textwrap.dedent("""\
            ====== WARNING: ACTIVATE CONDA ENVIRONMENT FIRST ======"
            cmd in htop: conda activate py27
            ...Select sub-option
            1. model: Make DNN model
            2. n2a: make array from ntuple
            3. pred: predict DNN score
            4. hist: make DNN output histograms\
        """)
        sub_cmd = raw_input("Choose subcommand: model/n2a/pred/hist/exit ")
        if not any(i in sub_cmd for i in ['mode','n2a','pred','hist','exit']):
            print "...Wrong command"
            exit(0)
        if sub_cmd == 'exit': exit(0) 

    elif cmd == 'draw':
        print textwrap.dedent("""\
            ...Select sub-option
            1. table: make cut flow table
            2. syst: draw systematic plot for each source
            3. plotIt: run plotter
            4. exit: Close program\
        """)
        sub_cmd = raw_input("...Choose subcommand: table/syst/plotIt/exit ")
        if not any(i in sub_cmd for i in ['table','syst','plotIt','exit']):
            print "...Wrong command"
            exit(0)
        if sub_cmd == 'exit': exit(0) 
    if not sub_cmd == '': cmd = cmd + '/' + sub_cmd
        
    return cmd

def _run_command(self, cmd):
    print self.cmd 
