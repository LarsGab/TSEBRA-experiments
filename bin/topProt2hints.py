#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# topProt2hints.py: Creates hints for EVM and TSEBRA from ProteinAlignment file in gff format
# ==============================================================
import argparse
import csv
import re

def main():
    args = parseCmd()
    evm_out = []
    braker_out = []
    type_translate = {  'Intron' : 'intron',
                    'start_codon' : 'start',
                    'stop_codon' : 'stop'}
    braker_hints = {}
    evm_hints = {}

    # read protein alignments
    with open(args.topProts, 'r') as file:
        topProtGff = csv.reader(file, delimiter='\t')
        for line in topProtGff:
            if line[2].lower() == 'cds':
                id = get_new_id(line[8])
                line[8] = 'ID={};'.format(id)
                line[2] = 'protein_match'
                line[3] = int(line[3])
                line[4] = int(line[4])
                if not id in evm_hints.keys():
                    evm_hints.update({id : []})
                evm_hints[id].append(line)
            elif line[2].lower() in ['intron', 'start_codon', 'stop_codon']:
                key = '{}_{}_{}_{}'.format(line[0], line[3], line[4], line[6])
                if key not in braker_hints.keys():
                    braker_hints.update({key : [line, 0]})
                braker_hints[key][1] += 1

    # remove small gaps in alignments
    for key in evm_hints.keys():
        tx = sorted(evm_hints[key], key = lambda l:l[3])
        out = [tx[0]]
        for line in tx[1:]:
            if (line[3] - out[-1][4]) < 3:
                out[-1][4] = line[4]
            else:
                out.append(line)
        if out[0][6] == '-':
            out.reverse()
        if len(out) > 1:
            evm_out += out

    # write hints to files
    for value in braker_hints.values():
        value[0][2] = type_translate[value[0][2]]
        value[0][8] = 'mult={};src=P;pri=4'.format(value[1])
        braker_out.append(value[0])

    with open(args.evm_out, 'w+') as file:
        outGff = csv.writer(file, delimiter='\t')
        for line in evm_out:
            outGff.writerow(line)

    with open(args.braker_out, 'w+') as file:
        outGff = csv.writer(file, delimiter='\t')
        for line in braker_out:
            outGff.writerow(line)

def get_attribute(attributes, a_name):
    expression = a_name + '=([^;]+)'
    return re.search(expression, attributes).groups()[0]

def get_new_id(attributes):
    return '{}.{}'.format(get_attribute(attributes, 'prot'), \
        get_attribute(attributes, 'seed_gene_id'))

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='Creates hints for EVM and ' \
        + 'TSEBRA from ProteinAlignment file in gff format')
    parser.add_argument('--topProts', type=str,
        help='Protein alignments')
    parser.add_argument('--evm_out', type=str,
        help='Output of intron position hints')
    parser.add_argument('--braker_out', type=str,
        help='Output hints as alignments')
    return parser.parse_args()

if __name__ == '__main__':
    main()
