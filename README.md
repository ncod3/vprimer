# V-primer

V-primer is a software written in Python3 for the efficient design of genome-wide InDel, CAPS, and SNP markers from multi-sample variant call format (VCF) genotyping data obtained by NGS.

## SYNOPSIS
```
vprimer
	[-h | --help] [--version]
	[--vcf] [--ref]
	[--auto_group] [--a_sample] [--b_sample]
	[--target] [--pick_mode]
	[--indel_size] [--product_size]
	[--enzyme] [--enzyme_file]
	[--p3_normal] [--p3_amplicon] [--amplicon_param]
	[--bam_table] [--min_max_depth]
	[--show_samples] [--show_fasta]
	[--out_dir]
	[--thread]
```

## Description

V-primer designs Indel, CAPS and SNP markers that can distinguish between two sample groups using a VCF file created from multiple sample BAM files. There are two ways to specify the sample groups: 1) by user-specified selection of two groups to be compared, and 2) by automatically generating two groups based on the genotype of the VCF file within the entire user-specified set of samples.

## Installation

Create a working environment using conda and install vprimer from this GitHub site using pip.

First, check the settings for channels to install various conda tools. If the highest priority and lowest priority are set as follows, there is no problem:

```
$ conda config --get channels

--add channels 'conda-forge'   # lowest priority
--add channels 'bioconda'
--add channels 'defaults'   # highest priority
```

If the settings are not as described above, run the following three lines:

```
$ conda config --add channels 'conda-forge'
$ conda config --add channels 'bioconda'
$ conda config --add channels 'defaults'

```

Next, create a virtual environment named "vprimer" using conda.

```
$ conda create -n vprimer python 'biopython==1.76'
```

Activate the created virtual environment.

```
$ conda activate vprimer
```

Prepare the remaining required environments using the conda install command.

```
(vprimer) $ conda install pandas vcfpy pysam joblib samtools bcftools bedtools tabix primer3 primer3-py blast
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

## Usage

### ***<span style="color: #FF4D00; ">required</span>***
<dl>
<dt style="font-style:normal;">--ref <span style="font-weight:normal;">ref_file</span>
</dt>
<dd>
Reference fasta.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--vcf <span style="font-weight:normal;">vcf_file</span>
</dt>
<dd>
VCF file.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--target <span style="font-weight:normal;">all | chr | chr:stt-end | chr:stt-[,…​]
</span>
</dt>
<dd>
Comma- or Space-separated list of regions.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--pick_mode <span style="font-weight:normal;">mode</span>
</dt>
<dd>
Type of marker to pick up. [ indel | caps | snp ]
</dd>
</dl>

### ***<span style="color: #FF4D00; ">for preparation</span>***

<dl>
<dt style="font-style:normal;">--show_fasta</span>
</dt>
<dd>
Prepare fasta, display fasta information and exit.
</dd>
</dl>

<dl>
<dt style="font-style:normal;"> --show_samples</span>
</dt>
<dd>
Prepare VCF, display VCF information and exit.
</dd>
</dl>

### ***<span style="color: #FF4D00; "> selection required </span>***

<dl>
<dt style="font-style:normal;">
--a_sample <span style="font-weight:normal;">[sample [sample ...]]</span><br>
--b_sample <span style="font-weight:normal;">[sample [sample ...]]
<br>
 or <br>
</span>
--auto_group <span style="font-weight:normal;">[sample [sample ...]]
</span>
</dt>
<dd>
If you already have two groups to compare, list the samples in a_sample and b_sample.
When analyzing by genotype-based auto group, list the samples in auto_group.
</dd>
</dl>

### ***<span style="color: #FF4D00; "> optional</span>***

<dl>
<dt style="font-style:normal;">--indel_size <span style="font-weight:normal;"> min-max </span>
</dt>
<dd>
The range of InDel size.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--product_size <span style="font-weight:normal;">min-max</span>
</dt>
<dd>
The range of product size for designing primer.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--enzyme <span style="font-weight:normal;">enzyme_name</span>
</dt>
<dd>
Restriction enzyme names used in CAPS marker.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--enzyme_file <span style="font-weight:normal;"> file </span>
</dt>
<dd>
File that listing restriction enzyme names for use in CAPS marker.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--p3_normal <span style="font-weight:normal;"> file </span>
</dt>
<dd>
File that listing parameters to set Primer3 for InDel or CAPS marker.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--p3_amplicon <span style="font-weight:normal;"> file </span>
</dt>
<dd>
File that listing parameters to set Primer3 for SNP marker.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--amplicon_param <span style="font-weight:normal;"> parameter </span>
</dt>
<dd>
Parameters for designing SNP markers.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--bam_table <span style="font-weight:normal;">file</span>
</dt>
<dd>
File that that associates bam file names with VCF sample names.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--out_dir <span style="font-weight:normal;"> dir_name </span>
</dt>
<dd>
Directory name for outputting results.
</dd>
</dl>

<dl>
<dt style="font-style:normal;">--thread <span style="font-weight:normal;">num</span>
</dt>
<dd>
Number of CPUs used.
</dd>
</dl>
	

## Authors
- Satoshi Natsume s-natsume@ibrc.or.jp

See also the list of contributors who participated in this project.

## Licence

Copyright (c) 2023 Satoshi Natsume
Released under the MIT license
https://github.com/YukinobuKurata/YouTubeMagicBuyButton/blob/master/MIT-LICENSS
E.txt

## Changelog
- 2023-04-03
	- 1.0.1 Modify parameter settings.
- 2023-04-02 
	- vprimer 1.0.0 released.





