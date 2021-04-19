#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# pasa2hint.py: Creates hints for EVM and TSEBRA from PASA assembly
# ==============================================================
import argparse
import csv
import sys

class Transcript:
    '''Handles the alignment of one transcript from the assembly
    '''
    def __init__(self, id):
        self.id = id
        self.chr = None
        self.coords = []
        self.strand = None
        self.introns = []

    def add_line(self, line):
        # add a gtf line to tx
        if not self.chr:
            self.chr = line[0]
        if not line[0] == self.chr:
            sys.stderr.write('Chr. Error at gene_id: \n' + self.id)
        if not self.strand:
            self.strand = line[6]
        if  not line[6] == self.strand:
            sys.stderr.write('Strand Error at gene_id: \n' + self.id)
        self.coords.append([int(line[3]), int(line[4])])

    def add_introns(self):
        # add intron positions to alingment
        if len(self.coords) > 1:
            self.coords = sorted(self.coords, key=lambda c:c[0])
            for i in range(1, len(self.coords)):
                self.introns.append([self.coords[i-1][1] + 1, self.coords[i][0] - 1])

    def check_coords(self):
        # remove small alignment gaps
        self.coords = sorted(self.coords, key=lambda c:c[0])
        new_coords = [self.coords[0]]
        for c in self.coords[1:]:
            if c[0] - new_coords[-1][1] < 3:
                new_coords[1] = c[1]
            else:
                new_coords.append(c)
        self.coords = new_coords

    def get_gtf(self):
        # returns gtf for tx alignment
        out = []
        for c in self.coords:
            out.append([self.chr, 'PASA', 'cDNA_match', c[0], c[1], '.', \
                self.strand, '.', 'ID={};'.format(self.id)])
        if self.strand == '-':
            out.reverse()
        return out

def main():
    args = parseCmd()
    tx = {}

    introns = {}

    # read PASA assembly
    with open (args.pasa, 'r') as file:
        for line in file.readlines():
            line = line.split('\t')
            if len(line) == 9:
                id = line[8].split('ID=')[1].split(';')[0]
                if id not in tx.keys():
                    tx.update({id : Transcript(id)})
                tx[id].add_line(line)

    # remove small gaps and add introns to all tx alignments
    out_evm = []
    for key in tx.keys():
        tx[key].check_coords()
        tx[key].add_introns()
        out_evm += tx[key].get_gtf()
        for intron in tx[key].introns:
            i_key = '{}_{}_{}_{}'.format(tx[key].chr, intron[0], intron[1], tx[key].strand)
            if not i_key in introns.keys():
                introns.update({i_key : [tx[key].chr, intron[0], intron[1], tx[key].strand, 0]})
            introns[i_key][4] += 1

    # write hints to files
    gtf = ''
    mult = 0
    for i in introns.values():
        gtf += '\t'.join([i[0], 'PASA', 'intron', str(i[1]), str(i[2]), '.' , i[3], '.', \
            'src=E;mult={};pri=4'.format(i[4])])
        mult += i[4]
        gtf += '\n'
    with open(args.braker_out, 'w+') as file:
        file.write(gtf)
    with open(args.evm_out, 'w+') as file:
        outGff = csv.writer(file, delimiter='\t')
        for line in out_evm:
            outGff.writerow(line)

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--pasa', type=str,
        help='PASA assembly')
    parser.add_argument('--braker_out', type=str,
        help='Output of intron position hints')
    parser.add_argument('--evm_out', type=str,
        help='Output hints as alignments')
    return parser.parse_args()

if __name__ == '__main__':
    main()
