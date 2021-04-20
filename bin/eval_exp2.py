#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# eval_exp2.py: Evaluate a set of partitions from a genome for:
#           BRAKER1, BRAKER2, EVM, TSEBRA_EVM, TESEBRA_default
# ==============================================================
import argparse
import subprocess as sp
import multiprocessing as mp
import os
import itertools
import csv
import re
import sys

class EvalError(Exception):
    pass

class Score:
    def __init__(self, tp, fn, fp):
        self.tp = int(tp)
        self.fn = int(fn)
        self.fp = int(fp)

    def sens(self):
        if self.fn + self.tp > 0:
            return self.tp / (self.fn + self.tp)
        return 0

    def spec(self):
        if self.fp + self.tp > 0:
            return self.tp / (self.fp + self.tp)
        return 0

    def f1(self):
        if self.fn + self.tp + self.fp > 0:
            return self.tp / (1/2 * (self.fn + self.fp) + self.tp)
        return 0

evm_bin = os.path.dirname(os.path.realpath(__file__))
workdir = ''
partition_list = []
modes = ['cds', 'trans', 'gene']
measures = ['F1', 'Sn', 'Sp']
methods = ['BRAKER1', 'BRAKER2', 'EVM', 'TSEBRA_EVM', 'TESEBRA_default']
methods_files = ['braker1.gtf', 'braker2.gtf', 'evm.gtf', 'tsebra_EVM.gtf', \
    'tsebra_default.gtf']
part_eval_result = []
threads = 1

def main():
    global workdir, partition_list, threads
    args = parseCmd()

    workdir = os.path.abspath('{}/EVM/{}/'.format(args.species_dir, args.test_level))
    threads = args.threads
    if not os.path.exists('{}/evaluation/'.format(workdir)):
        os.makedirs('{}/evaluation/'.format(workdir))

    # read partition lists
    partition_list_path = '{}/partitions/part_test.lst'.format(workdir)
    with open(partition_list_path, 'r') as file:
        part = csv.reader(file, delimiter='\t')
        for p in part:
            partition_list.append(p)

    eval = {}
    for method, gene_pred in zip(methods, methods_files):
        eval.update({method : job(gene_pred)})

    full_eval(eval)

    for mea in measures:
        single_eval(eval, mea)

    sys.stderr.write('### Finished, results are located at {}/evaluation/\n'.format(workdir))

def single_eval(eval, mea):
    # prints a line for the evaluation one measure (col = mode_method)
    # header
    tab = []
    for mo in modes:
        line += [' ', ' ', mo, ' ', ' ']
    tab.append(line)
    tab.append(methods*3)

    # body
    line = []
    for mo in modes:
        for meth in methods:
            line.append(round(100 * eval[meth][mo][mea],2))
    tab.append(line)

    csv_writer(tab, '{}/evaluation/{}.eval.tab'.format(workdir, mea))

def full_eval(eval):
    # write complete eval (rows = methods, col = mode_measure)
    tab = []
    # header
    line = ['# method']
    for mo in modes:
        for mea in measures:
            line.append('{}_{}'.format(mo, mea))
    tab.append(line)

    # body
    for meth in methods:
        line = [meth]
        for mo in modes:
            for mea in measures:
                line.append(round(100 * eval[meth][mo][mea],2))
        tab.append(line)

    csv_writer(tab, '{}/evaluation/full.eval.out'.format(workdir))

def csv_writer(tab, out_path):
    with open(out_path, 'w+') as file:
        table = csv.writer(file, delimiter='\t')
        for line in tab:
            table.writerow(line)

def collector(r):
    global part_eval_result
    part_eval_result.append(r)

def job(gene_pred):
    global part_eval_result
    part_eval_result = []
    job_results = []

    #for part in partition_list:
        #collector(eval_part(part[3], gene_pred))

    pool = mp.Pool(threads)
    for part in partition_list:
        r = pool.apply_async(eval_part, (part[3], gene_pred), callback=collector)
        job_results.append(r)
    for r in job_results:
        r.wait()
    pool.close()
    pool.join()
    results = part_eval_result
    test_result = {}
    for m in modes:
        list = []
        for r in part_eval_result:
            list.append(r[m])
        score = sum_score_lst(list)
        test_result.update({m : {}})
        test_result[m].update({'F1' : score.f1()})
        test_result[m].update({'Sn' : score.sens()})
        test_result[m].update({'Sp' : score.spec()})
    return test_result


def eval_part(exec_dir, gene_pred):
    part_name = exec_dir.split('/')[-1]
    score = {}
    gene_pred = '{}/{}'.format(exec_dir, gene_pred)

    if os.stat(gene_pred).st_size == 0:
        count = count_trans_cds('{}/annot.gtf'.format(exec_dir))
        for m in modes:
            score.update({m : Score(0,count[m],0)})
        return score

    if os.stat('{}/annot.gtf'.format(exec_dir)).st_size == 0:
        count = count_trans_cds(gene_pred)
        for m in modes:
            score.update({m : Score(0,0,count[m])})
        return score

    cmd = 'sort -k1,1 -k4,4n -k5,5n -o {} {}'.format(gene_pred, gene_pred)
    sp.call(cmd, shell=True)
    for m in modes:
        cmd = 'compare_intervals_exact.pl --f1 {}/annot.gtf --f2 {} --pseudo {}/pseudo.gff3 --{}'.format( \
            exec_dir, gene_pred, exec_dir, m)
        q = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        stdout, stderr = q.communicate()
        if stderr.decode():
            raise EvalError(stderr.decode())
        out = [o.split('\t') for o in stdout.decode().split('\n') if o]
        score.update({m : Score(out[0][1], out[0][2], out[1][2])})

    return score

def sum_score_lst(list):
    score = Score(0,0,0)
    for l in list:
        score.tp += l.tp
        score.fn += l.fn
        score.fp += l.fp
    return score

def count_trans_cds(file_path):
    cds = 0
    tx = []
    gene = []
    with open(file_path, 'r') as file:
        gtf = csv.reader(file, delimiter='\t')
        for line in gtf:
            if not line[2] in ['CDS', 'exon']:
                continue
            id = get_attribute(line[8], 'transcript_id')
            if id not in tx:
                tx.append(id)
            id = get_attribute(line[8], 'gene_id')
            if id not in gene:
                gene.append(id)
            if line[2].lower() == 'cds':
                cds += 1
    return {'gene' : len(gene), 'trans' : len(tx), 'cds' : cds}

def get_attribute(attributes, a_name):
    expression = a_name + '\s"([^";]+)'
    return re.search(expression, attributes).groups()[0]

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--test_level', type=str,
        help='')
    parser.add_argument('--species_dir', type=str,
        help='')
    parser.add_argument('--threads', type=str,
        help='')
    return parser.parse_args()

if __name__ == '__main__':
    main()
