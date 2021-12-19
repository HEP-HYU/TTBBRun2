strSlurmTemplate="""
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
"""
