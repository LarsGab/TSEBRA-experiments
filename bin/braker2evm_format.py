#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# braker2evm_format.py: Concatinate BRAKER1 and BRAKER2 prediction
# into a file in gff format that is compatible with EVM
# ==============================================================
import argparse
import subprocess as sp
import os

path_bin = os.path.dirname(os.path.realpath(__file__))
path_evm = ''
path_out = ''

def main():
    global path_evm, path_out
    args = parseCmd()
    path_out = args.out
    if args.evm:
        path_evm = args.evm

    i = 1
    for path in [args.braker1, args.braker2]:
        prefix = 'braker{}'.format(i)
        gtf = read_braker(path, prefix)
        i += 1

        out = os.path.dirname(os.path.realpath(path_out)) + '/{}.gtf'.format(prefix)
        with open(out, 'w+') as file:
            file.write(gtf)
        gtf2evm(prefix, out)

def change_src(string, src):
    # change the second cell in each row of a gtf file to src
    result = []
    string = string.split('\n')
    for line in string:
        line = line.split('\t')
        if len(line) == 9:
            line[1] = src
            result.append('\t'.join(line))
    return '\n'.join(result)

def read_braker(path, prefix):
    # read braker.gtf file and get all CDS and exon lines
    result = ''
    with open(path, 'r') as file:
        for line in file.readlines():
            line = line.split('\t')
            if len(line) == 9:
                if not line[2] in ['CDS', 'exon']:
                    continue
                tx_id = prefix + '.' + line[8].split('transcript_id "')[1].split('"')[0]
                gene_id = prefix + '.' + line[8].split('gene_id "')[1].split('"')[0]
                line[8] = 'transcript_id "{}"; gene_id "{}";\n'.format(tx_id, gene_id)
                result += '\t'.join(line)
    return result

def gtf2evm(prefix, gtf):
    # transform gtf file to gff format accepted by EVM
    cmd = '{}/EvmUtils/misc/augustus_GTF_to_EVM_GFF3.pl {}'.format(path_evm, gtf)
    with sp.Popen(cmd, shell=True, stdout=sp.PIPE,  stderr=sp.PIPE) as p:
        stdout, stderr = p.communicate()
        evm = change_src(stdout.decode(), prefix)
    with open(path_out, 'a+') as file:
        file.write(evm)

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='Concatinate BRAKER1 and BRAKER2 prediction ' \
        'into a file in gff format that is compatible with EVM')
    parser.add_argument('--braker1', type=str,
        help='BRAKER1 prediciton')
    parser.add_argument('--braker2', type=str,
        help='BRAKER2 prediciton')
    parser.add_argument('--evm', type=str,
        help='Path where EVM is installed')
    parser.add_argument('--out', type=str,
        help='Output file')
    return parser.parse_args()

if __name__ == '__main__':
    main()
