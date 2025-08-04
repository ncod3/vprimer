# V-primer

V-primer is a software written in Python3 for the efficient design of genome-wide InDel, CAPS, and SNP markers from multi-sample variant call format (VCF) genotyping data obtained by NGS. 

## SYNOPSIS
```
vprimer
	[-h | --help] [--version]
	[--vcf] [--ref] [--out_dir]
	[--show_samples] [--show_fasta]
	[--auto_group] [--a_sample] [--b_sample] 
	[--pick_mode] [--target] [--indel_size] [--product_size]
	[--homo_only] [--enzyme] [--enzyme_file] 
	[--p3_normal] [--p3_amplicon]
	[--amplicon_param] [--snp_filter] 
	[--bam_table] [--min_max_depth]
	[--progress] [--stop] [--ini_file]
	[--thread]
```

## Description

V-primer designs Indel, CAPS and SNP markers that can distinguish between two sample groups using a VCF file created from multiple sample BAM files. There are two ways to specify the sample groups: 1) by user-specified selection of two groups to be compared, and 2) by automatically generating two groups based on the genotype of the VCF file within the entire user-specified set of samples.

The specification of the restriction enzyme used in CAPS marker mode can be done by specifying the enzyme name as an option or by specifying some files containing the enzyme names. The list of available restriction enzyme names can be found on this website under the name 'caps_enzyme_name_list.whole_enzyme.txt.' It includes 745 restriction enzymes derived from the 'REBASE imprint files version 908 (2019),' which is used in the BioPython 1.76 library. If no option is specified, the default set of 72 restriction enzymes, listed on our website as 'caps_enzyme_name_list.txt.original,' will be used.

In SNP marker mode, we conduct checks for homodimer, heterodimer, and hairpin structures on each pair of designed primers, which are sequences with amplicon tags added as specified by the user. Additionally, we also perform heterodimer confirmation on all primers that pass these checks. However, due to the need for confirmation with all possible combinations of primers, the number of confirmations becomes very large. Therefore, by default, we extract primers at a rate of one per 1Mbps, with a GC content range of 50-55%, to reduce the number of primers and perform the confirmation.

[Usage (Japanese doc)](doc/Usage.jp.md)

[Tutorial (Japanese doc)](doc/Tutorial.jp.md)


## Installation

Create a working environment using conda and install vprimer from this GitHub site using pip.

First, check the settings for channels to install various conda tools. If the highest priority and lowest priority are set as follows, there is no problem:

```
$ conda config --get channels

--add channels 'defaults'   # lowest priority
--add channels 'bioconda'
--add channels 'conda-forge'   # highest priority
```

If the settings are not as described above, run the following three lines:

```
$ conda config --add channels 'defaults'
$ conda config --add channels 'bioconda'
$ conda config --add channels 'conda-forge'

```

Next, create a virtual environment named "vprimer" using conda.

```
$ conda create -n vprimer python=3.8
```

Activate the created virtual environment.

```
$ conda activate vprimer
```

Prepare the remaining required environments using the conda install command.

```
(vprimer) $ conda install pandas vcfpy pysam samtools bcftools bedtools tabix primer3 primer3-py blast
```

Install vprimer. First, try uninstalling.

```
(vprimer) $ pip uninstall vprimer
WARNING: Skipping vprimer as it is not installed.
```

If it is not installed, the message above will appear, so continue the installation.


```
(vprimer) $ pip install git+https://github.com/ncod3/vprimer
Collecting git+https://github.com/ncod3/vprimer
  Cloning https://github.com/ncod3/vprimer to /tmp/pip-req-build-sljhy9du
...
Successfully installed vprimer-1.0.1
```

If the message "Successfully" appears, the installation is complete.


## Demo

Create a demo working directory anywhere you like and download the demonstration data. The data can be found at the following URL: ( https://github.com/ncod3/data_vprimer ).

Create a working directory with any name and move to it.

```
(vprimer) $ mkdir test_vprimer
(vprimer) $ cd test_vprimer
```

Download the demonstration data to this working directory.

```
(vprimer) $ git clone https://github.com/ncod3/data_vprimer
```

The "data_vprimer" directory will be created and the data will be downloaded.

Create a symbolic link to the demo shell script prepared in the test_script directory under data_vprimer in the current directory.

```
(vprimer) $ ln -s data_vprimer/test_script/*.sh .
```

Run the shell script named 010.show_samples.sh as follows.

```
(vprimer) $ sh ./010.show_samples.sh
```

The "refs" directory will be created and the vprimer analysis will be prepared.

To measure areas with low coverage of sequences using the sample bam files used to create the VCF, edit the file named "refs/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt" and describe the path to the corresponding bam file for each sample.

In this demo, the cat command is used to overwrite the files under refs with files that have already been prepared.

```
(vprimer) $ cat data_vprimer/bams/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt_filled > refs/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt
```

Execute the demo shell script in order.

```
(vprimer) $ sh ./020.6samples_indel.sh
(vprimer) $ sh ./021.6samples_caps.sh
(vprimer) $ sh ./022.6samples_snp.sh
(vprimer) $ sh ./030.auto_group_indel.sh
(vprimer) $ sh ./031.auto_group_caps.sh
(vprimer) $ sh ./032.auto_group_snp.sh
```

## Authors
- Satoshi Natsume s-natsume@ibrc.or.jp

See also the list of contributors who participated in this project.

## Licence

Copyright (c) 2023 Satoshi Natsume
Released under the MIT license

https://github.com/YukinobuKurata/YouTubeMagicBuyButton/blob/master/MIT-LICENSSE.txt

## Changelog
- 2023-09-26:
	- 1.0.8 Fixed a bug that did not work when bam file was not specified. And it is now possible to specify --amplicon_param separated by spaces.
- 2023-07-01
	- 1.0.7 Improved the behavior of heterodimer checks in SNP mode.
- 2023-06-07
	- 1.0.6 Fixed a bug related to incorporating the allele string information(00 01).
- 2023-06-06
	- 1.0.5 Includes Hetero Dimer check in SNP mode.
- 2023-04-10
	- 1.0.3 add 'in_target' and 'dup_pos' field in result output.
- 2023-04-09
	- 1.0.2 Fixed a bug that stopped at auto_group.
- 2023-04-03
	- 1.0.1 Modify parameter settings.
- 2023-04-02 
	- vprimer 1.0.0 released.





