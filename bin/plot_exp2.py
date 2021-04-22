#!/usr/bin/env python3
# ==============================================================
# author: Lars Gabriel
#
# plot_exp2.py: Plot average F1-score on gene, transcript and CDS level for the second experiment.
# ==============================================================
import argparse
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os
import csv
import math
from statistics import mean
import sys

class Axis_range:
    # search for a good axis range and set axis ticks
    def __init__(self):
        self.x_range = [100,0]
        self.y_range = [100,0]
        self.x_ticks = []
        self.y_ticks = []

    def add_coords(self, x, y):
        for value, range in zip([x, y], [self.x_range, self.y_range]):
            range[0] = min(float(value), range[0])
            range[1] = max(float(value), range[1])

    def set_axis(self, pad_fraction):
        axis_range = max(self.x_range[1] - self.x_range[0], \
            self.y_range[1] - self.y_range[0])
        axis_range += pad_fraction * axis_range
        new_range = []
        for range in [self.x_range, self.y_range]:
            difference = axis_range - range[1] + range[0]
            new_range.append([range[0] - 1/2 * difference, range[1] + 1/2 * difference])
        self.x_range, self.y_range = *new_range,

    def set_ticks(self):
        self.x_ticks = list(range(ceil_five(self.x_range[0]), floor_five(self.x_range[1]) + 1, 5))
        self.y_ticks = list(range(ceil_five(self.y_range[0]), floor_five(self.y_range[1]) + 1, 5))

def ceil_five(x):
    return 5 * math.ceil(x/5)

def floor_five(x):
    return 5 * math.floor(x/5)

class Coordinate:
    def __init__(self, line):
        self.values = {}
        for label, i in zip(eval_label, line[1:]):
            self.values.update({label : float(i)})
        self.method = line[0]

eval_label = ['cds_F1', 'cds_Sn', 'cds_Sp', 'trans_F1', 'trans_Sn', 'trans_Sp', 'gene_F1', 'gene_Sn', 'gene_Sp']
def main():
    args = parseCmd()

    species = ['Arabidopsis thaliana', 'Caenorhabditis elegans', 'Drosophila melanogaster']
    eval_level = ['CDS level', 'Transcript level', 'Gene level']
    color = {'BRAKER1' : 'skyblue', 'BRAKER2' : 'blue', 'EVM' : 'green', \
        'TSEBRA_EVM' : 'orange', 'TSEBRA_default' : 'red'}
    test_level = ['species_excluded', 'family_excluded', 'order_excluded']
    data = os.path.abspath(args.parent_dir)

    # create legend
    legend1_elements = []
    for key in color.keys():
        legend1_elements.append(Line2D([0], [0], marker='o', color='none', alpha=0.8,\
            markerfacecolor=color[key], markeredgecolor='none', markersize=15, label=key))

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 6))
    plt.setp(axes.flat, xlabel='Specificity', ylabel='Sensitivity')

    # write text for eval level
    dist = 10
    for ax, col in zip(axes, eval_level):
        ax.annotate(col, xy=(0.5, 1), xytext=(0, dist),
                    xycoords='axes fraction', textcoords='offset points',
                    size='large', ha='center', va='baseline', weight='bold')

    # read eval tables
    coords = {}
    for i in range(0, 3):
        for l in test_level:
            tab = read_eval('{}/{}/EVM/{}/evaluation/full.eval.out'.format(data, species[i].replace(' ', '_'), l))
            for c in tab:
                if not c.method in coords.keys():
                    coords.update({c.method : {}})
                for label in eval_label:
                    if not label in coords[c.method].keys():
                        coords[c.method].update({label : []})
                    coords[c.method][label].append(c.values[label])

    # plot average Sp and Sn
    axis = [Axis_range(), Axis_range(), Axis_range()]
    for method in coords.keys():
        i = 0
        for j, level in zip([0,1,2], ['cds', 'trans', 'gene']):
            sp = '{}_Sp'.format(level)
            sn = '{}_Sn'.format(level)
            axis[j].add_coords(mean(coords[method][sp]), mean(coords[method][sn]))
            axes[j].scatter(mean(coords[method][sp]), mean(coords[method][sn]), color=color[method], linewidths=2, \
                edgecolor='none', marker='o', s=100, alpha=0.8)

    # set axis ranges and ticks
    for j in [0,1,2]:
        axis[j].set_axis(0.3)
        axis[j].set_ticks()
        axes[j].set_xlim(axis[j].x_range[0], axis[j].x_range[1])
        axes[j].set_ylim(axis[j].y_range[0], axis[j].y_range[1])
        axes[j].set_axisbelow(True)
        axes[j].xaxis.set_ticks(axis[j].x_ticks)
        axes[j].yaxis.set_ticks(axis[j].y_ticks)

    fig.legend(bbox_to_anchor=(0.05, 0.03, 0.92, 0), handles=legend1_elements, loc='lower center', \
        borderaxespad=0., ncol=5, mode='expand')
    fig.tight_layout()
    fig.subplots_adjust(left=0.05, right=0.97, top=0.9, bottom=0.175)

    fig.savefig('{}/evaluation/plot_exp2.png'.format(data), dpi=fig.dpi)
    sys.stderr.write('### Finished, plot is located at {}/evaluation/plot_exp2.png\n'.format(data))
def read_eval(eval_file):
    coords = []
    if os.path.exists(eval_file):
        with open(eval_file, 'r') as file:
            table = csv.reader(file, delimiter='\t')
            for line in table:
                if line[0][0] == '#':
                    continue
                coords.append(Coordinate(line))
    return coords

def parseCmd():
    """Parse command line arguments

    Returns:
        dictionary: Dictionary with arguments
    """
    parser = argparse.ArgumentParser(description='Plot average F1-score on gene, ' \
        + 'transcript and CDS level for the second experiment.')
    parser.add_argument('--parent_dir', type=str,
        help='Directory containing results for TSEBRA-experiments for different species')
    return parser.parse_args()

if __name__ == '__main__':
    main()
