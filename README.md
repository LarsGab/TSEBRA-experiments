# TSEBRA-Experiments

This repository contains all data and scripts used for the experiments of the ToDo: [TSEBRA Paper].

Both experiments require that [TSEBRA](https://github.com/LarsGab/TSEBRA) has been downloaded and that its ```bin``` folder is added to ```$PATH```, e.g.:
```console
git clone https://github.com/LarsGab/TSEBRA
export PATH="$(pwd)/TSEBRA/bin:$PATH"
```

<h2 id="1-exp"> Experiment 1 (Comparison to BRAKER1 and BRAKER2)</h2>

The first experiment was carried out with all species listed in ```species.tab```. It demonstrates the increase of accuarcies of TSEBRA compared to BRAKER1 and BRAKER2.

### Before you start
Choose a species and replace "Enter species" with a species name from ```species.tab```, e.g. "Bombus_terrestris".
```console
species="Enter_species"
species_dir=$(pwd)"/$species"
```

You have to choose a level of exclusion for the protein database of the BRAKER2 run.
We used the levels 'species_excluded', 'family_excluded', 'order_excluded' for the species listed in ```model_species.tab```. For all other species we only used 'order_excluded'.
```console
### Choose a test level and remove the '#'
### Only choose species_excluded or family_excluded if your species is listed in model_species.tab
#level="species_excluded"
#level="family_excluded"
#level="order_excluded"

braker1_dir="${species_dir}/braker1/"
braker2_dir="${species_dir}/braker2/${level}"
```

### BRAKER1<sup name="a1">[1](#ref1)</sup> and BRAKER2<sup name="a2">[2](#ref2)</sup>
You can use the BRAKER1 and BRAKER2 results prepared at ToDo: [Link to Webserver]:
```console
wget link/to/webserver/$species.tar.gz
tar -xzvf $species.tar.gz
```

Alternatively, you can create your own BRAKER runs, if you want to do the experiment from scratch.

Then you have to
* install [BRAKER v2.1.5](https://github.com/Gaius-Augustus/BRAKER/releases/tag/v2.1.5),
* prepare genome and annotation as described in [EukSpecies-BRAKER2](https://github.com/gatech-genemark/EukSpecies-BRAKER2),
* prepare RNA-seq hints and protein data as described in [BRAKER2-exp](https://github.com/gatech-genemark/BRAKER2-exp) into ```$species_dir```.

You have to run BRAKER1 only once per species!

Run BRAKER1:

```console
braker.pl --genome=${species_dir}/data/genome.fasta.masked --hints=${species_dir}/varus/varus.gff --softmasking --species=${species}_braker1 --workingdir=$braker1_dir
```

Run BRAKER2:
```console
mkdir -p $braker2_dir
braker.pl --genome=${species_dir}/data/genome.fasta.masked --prot_seq=${species_dir}/data/${level}.fa --softmasking --species=${species}_${level} --epmode --prg=ph --nocleanup --AUGUSTUS_ab_initio --workingdir=$braker2_dir
```

### TSEBRA

Ensure that the transcript and gene IDs of the BRAKER prediction files are in order:
```console
fix_gtf_ids.py --gtf ${braker1_dir}braker.gtf --out ${braker1_dir}/braker_fixed.gtf
fix_gtf_ids.py --gtf ${braker2_dir}/braker.gtf --out ${braker2_dir}/braker_fixed.gtf
```

Run TSEBRA:
```console
tsebra_default=${species_dir}/tsebra_default/${level}/
mkdir -p $tsebra_default
tsebra.py -g ${braker1_dir}/braker_fixed.gtf,${braker2_dir}/braker_fixed.gtf -c ${species_dir}/../config/default.cfg -e ${braker1_dir}/hintsfile.gff,${braker2_dir}/hintsfile.gff -o ${tsebra_default}/tsebra_default.gtf
```

### Evaluation
Compute F1-score, Sensitivity, Specificity:
```console
eval_exp1.py --species_dir $species_dir --test_level $level
```

The TSEBRA and evaluation results are located at ```$species_dir/tsebra_default/$level/```.

## Experiment 2 (Comparison to EVidenceModeler<sup name="a3">[3](#ref3)</sup>)

The second experiment was carried out with all model species listed in ```model_species.tab``` and the following manual only works for these species. In this experiment we compared TSEBRA with EVidenceModeler (EVM) [cite].

### Before you start

For this experiment you need to
* perform [Experiment 1](#1-exp),
* install [EVidenceModeler](https://github.com/EVidenceModeler/EVidenceModeler).

If you haven't done it for the first Experiment:
* prepare genome and annotation as described in [EukSpecies-BRAKER2](https://github.com/gatech-genemark/EukSpecies-BRAKER2)
* install [TSEBRA](https://github.com/LarsGab/TSEBRA)

Choose a species and replace "Enter species" with a species name from ```model_species.tab```, e.g. "Drosophila_melanogaster".
```console
species="Enter_species"
species_dir=$(pwd)"/$species"
```

Choose a level of exclusion for the protein database of the BRAKER2 run and remove the corresponding '#'.
```console
### Choose a test level and remove the '#':
#level="species_excluded"
#level="family_excluded"
#level="order_excluded"
```

Download the prepared files from ToDo[Enter link to webserver], if you didn't download them for the first experiment.
```console
wget link/to/webserver/$species.tar.gz
tar -xzvf $species.tar.gz ${species}/EVM/ -C ${species_dir}
```

### PASA<sup name="a4">[4](#ref4)</sup>
You can use the PASA results we have prepared and copy them to your ```$species_dir```.
They are already in your ```$species_dir``` and you do not need to run following commands, if you used the prepared files in the experiment 1.

Otherwise:
```console
tar -xzvf $species.tar.gz $species/pasa/ -C $species_dir
```

Alternatively, you can create your own PASA run. Then, you have to make your own VARUS run from scratch as decribed in [BRAKER2-exp](https://github.com/gatech-genemark/BRAKER2-exp) into ```$species_dir/varus/``` and you have to install:
* [samtools](https://github.com/samtools/samtools)
* [Trinity v2.12.0](https://github.com/trinityrnaseq/trinityrnaseq/releases/tag/v2.12.0)
* [PASA v2.4.1](https://github.com/PASApipeline/PASApipeline/releases/tag/pasa-v2.4.1)

Add them to your ```$PATH``` variable.

Extract RNA-read sequences from VARUS.bam
```console
samtools fasta ${species_dir}/varus/VARUS.bam > ${species_dir}/varus/VARUS.fasta
```

Run Trinity<sup name="a5">[5](#ref5)</sup> (you can change the max_memory and CPU to suit your system):
```console
Trinity --seqType fa --max_memory 4G --CPU 4 --single ${species_dir}/varus/VARUS.fasta --run_as_paired --output ${species_dir}/trinity/
```

Run PASA:
```console
mkdir ${species_dir}/pasa/
cp ${species_dir}/../config/alignAssembly.config ${species_dir}/pasa/
sed -i "s,pathtoyourpasadir,$species_dir/pasa,g" ${species_dir}/pasa/alignAssembly.config
Launch_PASA_pipeline.pl -c ${species_dir}/pasa/alignAssembly.config -C -R -g ${species_dir}/genome/genome.fasta.masked --ALIGNERS blat,gmap -t ${species_dir}/trinity/Trinity.fasta
```

### Partition
Enter here the absolute path to the directory where EVidenceModeler is installed
```console
evm_path="ENTER EVM PATH"
```

Partiton and prepare all data for EVM, TSEBRA and their evaluation:
```console
partition.py --species_dir $species_dir --test_level $level --evm_path $evm_path --out ${species_dir}/EVM/${level}/
```

If you want to reconstruct the results from ToDo: [PAPER] then use the provided partition test set:
```console
sed -i "s,pathtoyoutpartitions,$species_dir/EVM/$level/partitions/,g" ${species_dir}/EVM/${level}/partitions/part_test.lst
sed -i "s,pathtoyoutpartitions,$species_dir/EVM/$level/partitions/,g" ${species_dir}/EVM/${level}/partitions/part_train.lst
```
Or you can sample 90% of the partions as the test set:
```console
sample_partitions.py --partition_dir ${species_dir}/EVM/${level}/partitions/ --seed ${species_dir}/EVM/${level}/seed_value.out
```

### EVM
Run EVM for all test partitions. (adjust the number of threads to fit your system)
```console
runEVM.py --species_dir $species_dir --test_level $level --evm_path $evm_path --threads 4
```
### TSEBRA
Run TSEBRA for all test partitions. (adjust the number of threads to fit your system)
```console
runTSEBRA.py --species_dir $species_dir --test_level $level --threads 4
```

### Evaluation
Evaluate the test partitions. (adjust the number of threads to fit your system)
```console
eval_exp2.py --species_dir $species_dir --test_level $level --threads 4
```
The results are located at ```$species_dir/EVM/$level/evaluation/```.

## Summary of all Results
Enter here the path to the directory containing the folders for the species for which you have performed the experiments.

```console
parent_dir="Enter path to parent dir"
```

Create table with all available results.
```console
eval_summary.py --parent_dir $parent_dir
```
Each row contains the result for a species and test level. A row contains the result for the second experiment if results for both experiments are present.
You can find the table in ```$parent_dir/evaluation/```.


You can plot the average Sensitivity and Specificity for all species in ```$parent_dir``` for gene, transcript and CDS level from the second experiment. This requires that ```matplotlib``` is installed, e.g. with :
```console
pip install matplotlib
```
Create plot:
```console
eval_summary.py --parent_dir $parent_dir
```
You can find the plot at ```$parent_dir/evaluation/plot_exp2.png```.

## Licence
All source code, i.e. `bin/*.py` and `bin/*.pl` are under the Artistic License (see <https://opensource.org/licenses/Artistic-2.0>).

### References
<b id="ref1">[1]</b> Hoff, Katharina J, Simone Lange, Alexandre Lomsadze, Mark Borodovsky, and Mario Stanke. 2015. “BRAKER1: Unsupervised Rna-Seq-Based Genome Annotation with Genemark-et and Augustus.” *Bioinformatics* 32 (5). Oxford University Press: 767--69.[↑](#a1)

<b id="ref2">[2]</b> Tomas Bruna, Katharina J. Hoff, Alexandre Lomsadze, Mario Stanke and Mark Borodvsky. 2021. “BRAKER2: automatic eukaryotic genome annotation with GeneMark-EP+ and AUGUSTUS supported by a protein database." *NAR Genomics and Bioinformatics* 3(1):lqaa108.[↑](#a2)

<b id="ref3">[3]</b> Haas, B. J., Salzberg, S. L., Zhu, W., Pertea, M., Allen, J. E., Orvis, J., ... & Wortman, J. R. 2008. Automated eukaryotic gene structure annotation using EVidenceModeler and the Program to Assemble Spliced Alignments. Genome biology, 9(1), 1-22.[↑](#a3)

<b id="ref4">[4]</b> Haas, B.J., Delcher, A.L., Mount, S.M., Wortman, J.R., Smith Jr, R.K., Jr., Hannick, L.I., Maiti, R., Ronning, C.M., Rusch, D.B., Town, C.D. et al. 2003 Improving the Arabidopsis genome annotation using maximal transcript alignment assemblies. Nucleic Acids Res, 31, 5654-5666.[↑](#a4)

<b id="ref5">[5]</b> Grabherr, M. G., Haas, B. J., Yassour, M., Levin, J. Z., Thompson, D. A., Amit, I., ... & Regev, A. 2011. Trinity: reconstructing a full-length transcriptome without a genome from RNA-Seq data. Nature biotechnology, 29(7), 644.[↑](#a5)
