#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# runTSEBRA.py: Run TSEBRA for a set of partitions
# ==============================================================
import argparse
import subprocess as sp
import multiprocessing as mp
import os
import csv
import sys

class FileMissing(Exception):
    pass

bin = os.path.dirname(os.path.realpath(__file__))
workdir = ''
partition_list = []
cfg = ''

def main():
    global evm, workdir, partition_list, cfg, bin
    args = parseCmd()
    workdir = os.path.abspath(args.data_dir)
    # read partition lists
    partition_list_path = '{}/partitions/part_test.lst'.format(workdir)
    with open(partition_list_path, 'r') as file:
        part = csv.reader(file, delimiter='\t')
        for p in part:
            partition_list.append(p)

    # Check config file
    cfg = '{}/tsebra.cfg'.format(workdir)
    if not os.path.exists(cfg):
        raise FileMissing('Weight file is missing at: {}'.format(cfg))

    # Run TSEBRA predicitons
    job_results = []
    pool = mp.Pool(args.threads)
    for part in partition_list:
        r = pool.apply_async(prediction, (part[3],))
        job_results.append(r)
    for r in job_results:
        r.wait()
    pool.close()
    pool.join()

def prediction(exec_dir):
    # make a TSEBRA predcition for one partition and evaluate it

    cmd = 'tsebra.py -g {}/braker1.gtf,{}/braker2.gtf '.format(exec_dir, exec_dir) \
        + '-e {}/braker_pasa.gff,{}/braker_protein.gff '.format(exec_dir, exec_dir) \
        + '-c {} -o {}/tsebra_EVM.gtf -q'.format(cfg, exec_dir)

    q = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = q.communicate()
    if stderr.decode():
        error = ''
        for line in stderr.decode().split('\n'):
            if not line[:8] == 'Skipping':
                error += line + '\n'
        if error.strip('\n'):
            sys.stderr.write('Error in {} with: {}'.format(cmd, error))

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_dir', type=str,
        help='')
    parser.add_argument('--threads', type=int,
        help='')
    return parser.parse_args()

if __name__ == '__main__':
    main()
