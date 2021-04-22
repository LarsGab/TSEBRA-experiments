#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# eval_exp1.py: Evaluate a set of partitions from a genome for:
#           BRAKER1, BRAKER2, TSEBRA_default
# ==============================================================
import argparse
import subprocess as sp
import os
import csv
import sys

class EvalError(Exception):
    pass

species_dir = ''
modes = ['cds', 'trans', 'gene']
measures = ['F1', 'Sn', 'Sp']
methods = ['BRAKER1', 'BRAKER2', 'TSEBRA_default']
methods_files = ['braker1/braker.gtf', 'braker2/{}/braker.gtf', 'tsebra_default/{}/tsebra_default.gtf']
test_level = ''

def main():
    global species_dir, test_level
    args = parseCmd()

    species_dir = os.path.abspath(args.species_dir)
    test_level = args.test_level
    methods_files[1] = methods_files[1].format(args.test_level)
    methods_files[2] = methods_files[2].format(args.test_level)

    eval = {}
    for method, gene_pred in zip(methods, methods_files):
        eval.update({method : evaluation('{}/{}'.format(species_dir, gene_pred))})

    for mea in measures:
        single_eval(eval, mea)

    sys.stderr.write('### Finished, results are located in ' \
        + '{}/tsebra_default/{}/\n'.format(species_dir, test_level))

def single_eval(eval, mea):
    # prints a table for one measure (row = species, col = mode_method)
    # header
    tab = []
    line = []
    for mo in modes:
        line += [' ', mo, ' ']
    tab.append(line)
    tab.append([] + methods*3)

    # body
    line = []
    for mo in modes:
        for meth in methods:
            line.append(round(eval[meth][mo][mea],2))
    tab.append(line)

    csv_writer(tab, '{}/tsebra_default/{}/{}.eval.tab'.format(species_dir, test_level, mea))

def csv_writer(tab, out_path):
    with open(out_path, 'w+') as file:
        table = csv.writer(file, delimiter='\t')
        for line in tab:
            table.writerow(line)

def evaluation(gene_pred):
    # compute for all measures (F1, Sn, Sp) on all eval_level (gene, transcript and CDS)
    # returns dict eval[eval_level][measure] = value
    eval = {}

    # run evaluation script
    cmd = "compute_accuracies.sh {}/annot/annot.gtf {}/annot/pseudo.gff3 {} gene trans cds".\
        format(species_dir, species_dir, gene_pred)
    p = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    if stderr.decode():
        raise EvalError(stderr.decode())
    stdout = stdout.decode()
    stdout = [s.split('\t') for s in stdout.split('\n') if s]

    # read result into eval
    for line in stdout:
        eval_level, measure = line[0].split('_')
        if eval_level not in eval:
            eval.update({eval_level : {}})
        eval[eval_level].update({measure : float(line[1])})

    # add F1 score
    for key in eval:
        eval[key].update({'F1' : (2 * eval[key]['Sn'] * eval[key]['Sp']) / \
            (eval[key]['Sn'] + eval[key]['Sp'])})
    return eval

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='Evaluate predictions ' \
        + 'from: BRAKER1, BRAKER2, TSEBRA_default ')
    parser.add_argument('--test_level', type=str,
        help='One of "species_excluded", "family_excluded" or "order_excluded"')
    parser.add_argument('--species_dir', type=str,
        help='Directory containing the results of TSEBRA-experiment 1 for one species')
    return parser.parse_args()

if __name__ == '__main__':
    main()
