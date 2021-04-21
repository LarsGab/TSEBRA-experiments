# TSEBRA-Experiments

This repository contains all data and scripts used for the experiments of the [TSEBRA Paper].
Both experiments require that [TSEBRA](https://github.com/LarsGab/TSEBRA) has been downloaded and that its ```bin``` folder is added to ```$PATH```, e.g.:
```console
git clone https://github.com/LarsGab/TSEBRA
export PATH="$(pwd)/TSEBRA/bin:$PATH"
```

<h2 id="1-exp"> 1. Experiment (Comparison to BRAKER1 and BRAKER2)</h2>

The first experiment was carried out with all species listed in ```species.tab```. It demonstrates the increase of accuarcies of TSEBRA compared to BRAKER1 and BRAKER2.

### Before you start
Choose a species and replace "Enter species" with a species name from ```species.tab```, e.g. "Drosophila_melanogaster".
```console
species="Enter_species"
species_dir=$(pwd)"/$species"
```

You have to choose a level of exclusion for the protein database of the BRAKER2 run.
We used for the species listed in ```model_species.tab``` the levels 'species_excluded', 'family_excluded', 'order_excluded' for all other species we used only 'order_excluded'.
```console
### Choose a test level and remove the '#':
#level="species_excluded"
#level="family_excluded"
#level="order_excluded"

braker1_dir="${species_dir}/braker1/"
braker2_dir="${species_dir}/braker2/${level}"
```

### BRAKER1 and BRAKER2
You can use the BRAKER1 and BRAKER2 results prepared at [Link to Webserver]:
```console
wget link/to/webserver/$species.tar.gz
tar -xzvf $species.tar.gz
```

Alternatively, you can create your own BRAKER runs, if you want to do the experiment from scratch.

Then you have to
* install [BRAKER v2.1.5](https://github.com/Gaius-Augustus/BRAKER/releases/tag/v2.1.5),
* prepare genome and annotation as described in [EukSpecies-BRAKER2](https://github.com/gatech-genemark/EukSpecies-BRAKER2),
* prepare RNA-seq hints and protein data as described in [BRAKER2-exp](https://github.com/gatech-genemark/BRAKER2-exp) into ```$species_dir```.

make sure the files are at the correct positions (script)

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
```console
eval_exp1.py --species_dir $species_dir --test_level $level
```

## 2. Experiment (Comparison to EVidenceModeler)

The second experiment was carried out with all model species listed in ```model_species.tab``` and the following manual only works for these species. In this experiment we compared TSEBRA with EVidenceModeler (EVM) [cite].

### Before you start

For this experiment you need to
* perform the [1. Experiment](#1-exp),
* install [EVidenceModeler](https://github.com/EVidenceModeler/EVidenceModeler).

If you haven't done it for the 1. Experiment:
* prepare genome and annotation as described in [EukSpecies-BRAKER2](https://github.com/gatech-genemark/EukSpecies-BRAKER2)

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

Please download the prepared file from [Enter link to webserver], if you do not already work with the prepared files:
```console
wget link/to/webserver/$species.tar.gz
tar -xzvf $species.tar.gz ${species}/EVM/ -C ${species_dir}
```

### PASA
You can use the PASA results we have prepared and copy them to your ```$species_dir```.
They are already in your ```$species_dir``` and you do not need to run following commands, if you used the prepared files in the 1. Experiment. Otherwise:
```console
tar -xzvf $species.tar.gz $species/pasa/ -C $species_dir
```

Alternatively, you can create your own PASA[cite] run. Then, you have to make your own VARUS run from scratch as decribed in [BRAKER2-exp](https://github.com/gatech-genemark/BRAKER2-exp) into ```$species_dir/varus/``` and you have to install:
* [samtools](https://github.com/samtools/samtools)
* [Trinity v2.12.0](https://github.com/trinityrnaseq/trinityrnaseq/releases/tag/v2.12.0)
* [PASA v2.4.1](https://github.com/PASApipeline/PASApipeline/releases/tag/pasa-v2.4.1)

Add them to your ```$PATH``` variable.

Extract RNA-read sequences from VARUS.bam
```console
samtools fasta ${species_dir}/varus/VARUS.bam > ${species_dir}/varus/VARUS.fasta
```

Run Trinity (you can change the max_memory and CPU to suit your system):
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

If you want to reconstruct the results from [PAPER] then use the provided partition test set:
```console
sed -i "s,pathtoyoutpartitions,$species_dir/EVM/$level/partitions/,g" ${species_dir}/EVM/${level}/partitions/part_test.lst
sed -i "s,pathtoyoutpartitions,$species_dir/EVM/$level/partitions/,g" ${species_dir}/EVM/${level}/partitions/part_train.lst
```
Or you can sample 90% of the partions as test set:
```console
sample_partitions.py --partition_dir ${species_dir}/EVM/${level}/partitions/ --seed ${species_dir}/EVM/${level}/seed_value.out
```

### EVM

```console
runEVM.py --species_dir $species_dir --test_level $level --evm_path $evm_path --threads 4
```
### TSEBRA
```console
runTSEBRA.py --species_dir $species_dir --test_level $level --threads 4
```

### Evaluation
```console
eval_exp2.py --species_dir $species_dir --test_level $level --threads 4
```

### References
