# TSEBRA-Experiments

This repository contains all data and scripts used for the experinments of the [TSEBRA Paper]. 
Both experiment require that [TSEBRA](https://github.com/LarsGab/TSEBRA) has been downloaded and that its ```bin``` folder is added to ```$PATH```.
Instructions can be found in each species folder. Genome and annotation files have to be prepared as descripted in https://github.com/gatech-genemark/EukSpecies-BRAKER2. Additional dependencies for both experiments are explained below and you need to add all programs to your ```$PATH``` variable. 

## 1. Experiment

The first experiment was carried out with all species listed in ```species.tab```. It demonstrates the increase of accuarcies of TSEBRA compared to BRAKER1 and BRAKER2.

### Dependencies
If you want to do this experiment from scratch, you need:
* BRAKER v2.1.5 from https://github.com/Gaius-Augustus/BRAKER/releases/tag/v2.1.5 
* RNA-seq and protein hints as described in https://github.com/gatech-genemark/BRAKER2-exp.

Alternatively, you can use the BRAKER1 and BRAKER2 results provided at [Link to Webserver], in which case you only need to install TSEBRA. 

## 2. Experiment

The second experiment was carried out with all model species listed in ```model_species.tab```. It compares TSEBRA with EVidenceModeler (EVM) [cite].

### Dependencies

For this experiment you need to install:
* EVidenceModeler from https://github.com/EVidenceModeler/EVidenceModeler

If you want to do this experiment from scratch you need the dependencies from the first experiment and you need to install:
* Trinity v2.12.0 https://github.com/trinityrnaseq/trinityrnaseq/releases/tag/v2.12.0
* PASA v2.4.1 https://github.com/PASApipeline/PASApipeline/releases/tag/pasa-v2.4.1
* ...

### References
