#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# runEVM.py: Run EVM for a set of partitions
# ==============================================================
import argparse
import subprocess as sp
import multiprocessing as mp
import os
import csv
import sys

class FileMissing(Exception):
    pass

evm = ''
bin = os.path.dirname(os.path.realpath(__file__))
workdir = ''
partition_list = []
weights = ''
threads = 1
def main():
    global evm, workdir, partition_list, weights, bin, threads
    args = parseCmd()
    workdir = os.path.abspath('{}/EVM/{}/'.format(args.species_dir, args.test_level))
    evm = os.path.abspath(args.evm_path)
    threads = args.threads
    # read partition lists
    partition_list_path = '{}/partitions/part_test.lst'.format(workdir)
    with open(partition_list_path, 'r') as file:
        part = csv.reader(file, delimiter='\t')
        for p in part:
            partition_list.append(p)

    # Check if weight file exists
    weights = '{}/EVM.weights.tab'.format(workdir)
    if not os.path.exists(weights):
        raise FileMissing('Weight file is missing at: {}'.format(weights))

    '''
    for part in partition_list:
        prediction(part[3], part[0])
    '''
    # Run evm predicitons
    job_results = []
    pool = mp.Pool(threads)
    for part in partition_list:
        r = pool.apply_async(prediction, (part[3], part[0]))
        job_results.append(r)
    for r in job_results:
        r.wait()
    pool.close()
    pool.join()
def prediction(exec_dir, contig):
    # make a EVM predcition for one partition
    part_name = exec_dir.split('/')[-1]
    start = int(part_name.split('_')[1].split('-')[0])
    chr = part_name.split('_')[0]

    # Run EVM
    evm_out = '{}/evm.out'.format(exec_dir)
    evm_cmd = '{}/evidence_modeler.pl -G genome.fasta.masked -g gene_set.gff'.format(evm) \
        + ' -w {} -e evm_pasa.gff -p evm_protein.gff --exec_dir {} > {} 2> {}.log'.format(\
        weights, exec_dir, evm_out, evm_out)

    q = sp.Popen(evm_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = q.communicate()
    if stderr.decode():
        sys.stderr.write('Error in {} with: {}'.format(evm_cmd, stderr.decode()))

    # check if EVM predicted at least one gene and convert evm.out to gff and gtf format
    if not os.stat(evm_out).st_size == 0:
        gff_out = '{}/evm.gff'.format(exec_dir, part_name)
        cmd = '{}/EvmUtils/EVM_to_GFF3.pl {} {} > {}'.format(evm, evm_out, contig, gff_out)
        sp.call(cmd, shell=True)

        gtf_out = '{}/evm.gtf'.format(exec_dir, part_name)
        cmd = '{}/gff32gtf.py --gff {} --out {}'.format(bin, gff_out, gtf_out)
        sp.call(cmd, shell=True)

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--species_dir', type=str,
        help='')
    parser.add_argument('--test_level', type=str,
        help='')
    parser.add_argument('--evm_path', type=str,
        help='')
    parser.add_argument('--threads', type=int,
        help='')
    return parser.parse_args()

if __name__ == '__main__':
    main()
