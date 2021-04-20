#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# sample_partitions.py: Sample partitons into test and training sets
# ==============================================================
import argparse
import random
import sys

def main():
    args = parseCmd()

    # get seed value
    if args.seed:
        with open(args.seed, 'r') as file:
            seed_value = int(file.read().strip('\n'))
    else:
        seed_value = random.randrange(sys.maxsize)
        with open('{}/seed_value.out'.format(args.partition_dir), 'w+') as file:
            file.write(str(seed_value))
    print(seed_value)
    random.seed(seed_value)

    # sample partitions into 10% train and 90% test sets
    with open(args.partition_dir + '/part.lst', 'r') as file:
        part_lst = file.readlines()
    sample_size = int(0.1 * len(part_lst))
    sample = random.sample(range(0, len(part_lst)), sample_size)
    test_out = ''
    train_out = ''
    for i in range(0, len(part_lst)):
        if i in sample:
            train_out += part_lst[i]
        else:
            test_out += part_lst[i]

    with open(args.partition_dir + '/part_train.lst', 'w+') as file:
        file.write(train_out)
    with open(args.partition_dir + '/part_test.lst', 'w+') as file:
        file.write(test_out)

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--partition_dir', type=str,
        help='')
    parser.add_argument('--seed', type=str,
        help='')
    return parser.parse_args()

if __name__ == '__main__':
    main()
