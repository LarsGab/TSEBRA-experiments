#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# gff32gtf.py: Convert gff3 to gtf
# ==============================================================
import argparse

def main():
    result = []
    args = parseCmd()
    with open(args.gff, 'r') as file:
        for line in file.readlines():
            line = line.split('\t')
            if len(line) == 9:
                if line[2] not in ['CDS', 'exon']:
                    continue
                id = line[8].split('Parent=')[1].strip('\n')
                line[8] = 'transcript_id "{}"; gene_id "{}_g";\n'.format(id, id)
                result.append('\t'.join(line))
    with open(args.out, 'w+') as file:
        file.write(''.join(result))

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--gff', type=str,
        help='File in gff3 format')
    parser.add_argument('--out', type=str,
        help='Output in gtf format')
    return parser.parse_args()

if __name__ == '__main__':
    main()
