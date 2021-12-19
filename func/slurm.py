import os
import sys
import textwrap
import subprocess

class MakeSlurmJob:


    def __init__(self, year, input_path, base_path, target):
        self.year = year
        self.input_path = input_path
        self.base_path = base_path
        self.target = target
        self.testset = ['TTLJ_PowhegPythia_ttbb', 'Tree_ttbbLepJets_000.root']
        self.slurm_template = textwrap.dedent("""\
            #! /bin/bash
            
            #SBATCH -J {job_name}
            #SBATCH -p {node} 
            #SBATCH -N 1 
            #SBATCH --open-mode=append
            #SBATCH -o %x.out
            #SBATCH -e %x.error
            #SBATCH --ntasks=1
            #SBATCH --mem=1gb
            #SBATCH --cpus-per-task=1
            #SBATCH --comment python
            #SBATCH --hint=compute_bound

            {opts}
            echo {command}
            {command}
        """)

    from slurm_make import make_slurm_job

