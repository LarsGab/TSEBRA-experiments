#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# partition.py: Partitons and prepares all data necassary for a comparison of TSEBRA and EVidenceModeler
# ==============================================================

import argparse
import subprocess as sp
import csv
import os
import multiprocessing as mp
import sys

class FileMissing(Exception):
    pass

segmentSize = 400000
overlapSize = 50000
mode = ''
evm = ''
bin_dir = os.path.abspath(os.path.dirname(__file__))
workdir = ''

def main():
    global workdir, mode, evm

    args = parseCmd()

    mode = args.test_level
    workdir = make_abs(args.out)
    evm = make_abs(args.evm_path)
    data_dir = make_abs(args.species_dir)
    braker1 = make_abs('{}/braker1/braker_fixed.gtf'.format(data_dir))
    braker2 = make_abs('{}/braker2/{}/braker_fixed.gtf'.format(data_dir, mode))
    anno = make_abs('{}/annot/annot.gtf'.format(data_dir))
    pseudo = make_abs('{}/annot/pseudo.gff3'.format(data_dir))
    spaln = make_abs('{}/braker2/{}/Spaln/spaln.gff'.format(data_dir, mode))
    pasa = make_abs('{}/pasa/sample_mydb_pasa.sqlite.pasa_assemblies.gff3'.format(data_dir))
    genome = make_abs('{}/data/genome.fasta.masked'.format(data_dir))
    tsebra_default = make_abs('{}/tsebra_default/{}/tsebra_default.gtf'.format(data_dir, mode))

    if not os.path.exists(workdir):
        os.mkdir(workdir)

    gene_set = '{}/gene_set.gff'.format(workdir)
    braker2evm(braker1, braker2, gene_set)

    part_file = partition(gene_set, pasa, spaln, genome)

    part_lst = []
    with open(part_file, 'r') as file:
        tab = csv.reader(file, delimiter='\t')
        for line in tab:
            part_lst.append(line)

    pool = mp.Pool(mp.cpu_count())
    for part in part_lst:
        pool.apply_async(prep_partition, (part[3], anno, pseudo, braker1, braker2, tsebra_default))
    pool.close()
    pool.join()

def braker2evm(braker1, braker2, braker_path):
    # create concatinated set of genes from BRAKER1
    # and BRAKER2 in format that is accepted by EVM
    cmd = 'python3 {}/braker2evm_format.py --braker1 {} --braker2 {} '.format(bin_dir, braker1, braker2) \
        + '--out {} --evm {}'.format(braker_path, evm)
    call_process(cmd)

def prep_partition(partition, anno, pseudo, braker1, braker2, tsebra_default):
    os.chdir(partition)
    dir = partition.strip('/').split('/')[-1]
    chr = dir.split('_')[0]
    start, end = dir.split('_')[1].split('-')

    # create hints for EVM and TSEBRA from pasa assemblies and topProteins
    cmd = 'python3 {}/pasa2hints.py --braker_out braker_pasa.gff '.format(bin_dir) \
        + '--pasa sample_mydb_pasa.sqlite.pasa_assemblies.gff3 --evm_out evm_pasa.gff'
    call_process(cmd)
    cmd = 'python3 {}/topProt2hints.py --topProts topProteins.gff '.format(bin_dir) \
        + '--braker_out braker_protein.gff --evm_out evm_protein.gff'
    call_process(cmd)

    # add files for TSEBRA runs and evaluation to the partitions
    files = [braker1, braker2, anno, pseudo, tsebra_default]
    file_name = ['braker1.gtf', 'braker2.gtf', 'annot.gtf', 'pseudo.gff3', 'tsebra_default.gtf']
    for i in range(0,len(files)):
        cmd = '{}/EvmUtils/gff_range_retriever.pl {} {} {} ADJUST_TO_ONE < '.format(evm, chr, start, end) \
            + '{} > {}/{}'.format(files[i], partition, file_name[i])
        sp.call(cmd, shell=True)
        cmd = 'sort -k1,1 -k4,4n -k5,5n -o {}/{} {}/{}'.format(partition, \
            file_name[i], partition, file_name[i])
        sp.call(cmd, shell=True)

def partition(gene_set, transcript, spaln, genome):
    # get topProteins from Spaln alignment
    protein = '{}/topProteins.gff'.format(workdir)
    cmd = 'grep topProt=TRUE {} > {}'.format(spaln, protein)
    sp.call(cmd, shell=True)

    # partition all data for EVM
    part_dir = '{}/partitions/'.format(workdir)
    if not os.path.exists(part_dir):
        os.mkdir(part_dir)
    os.chdir(part_dir)
    partitions = '{}/partitions/part.lst'.format(workdir)
    cmd = '{}/EvmUtils/partition_EVM_inputs.pl --genome {} '.format(evm, genome) \
        + '--gene_predictions {} --transcript_alignments {} '.format(gene_set, transcript) \
        + '--protein_alignments {} --segmentSize {} '.format(protein, segmentSize) \
        + '--overlapSize {} --partition_listing {}'.format(overlapSize, partitions)
    sp.call(cmd, shell=True)

    return partitions

def call_process(cmd):
    q = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = q.communicate()
    if stderr.decode():
        sys.stderr.write('Error in {} with: {}'.format(cmd, stderr.decode()))

def change_source(file_path, new_source, new_path):
    result = []
    new_path = '{}_{}'.format(file_path, new_source)
    with open(file_path, 'r') as file:
        gff = csv.reader(file, delimiter='\t')
        for line in gff:
            if len(line) == 9:
                line[1] = new_source
                result.append(line)

    with open(new_path, 'w+') as file:
        gff = csv.writer(file, delimiter='\t')
        for line in result:
            gff.writerow(line)
    return new_path

def make_abs(path):
    if not os.path.exists(path):
        raise FileMissing('File {} is missing!'.format(path))
    return os.path.abspath(path)

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--species_dir', type=str,
        help='Path to directory where all necassary files reside.')
    parser.add_argument('--test_level', type=str,
        help='One of "species_excluded", "family_excluded" or "order_excluded"')
    parser.add_argument('--evm_path', type=str,
        help='Path to the directory where EVidenceModeler is installed')
    parser.add_argument('--out', type=str,
        help='Directory where the partition is created')
    return parser.parse_args()

if __name__ == '__main__':
    main()
