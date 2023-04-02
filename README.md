# V-primer

vprimer 1.00

## Features

## Contents

## Requirement

## Installation

~~~
$ conda config --add channels 'defaults'
$ conda config --add channels 'bioconda'
$ conda config --add channels 'conda-forge'
$ conda config --get channels
--add channels 'defaults'   # lowest priority
--add channels 'bioconda'
--add channels 'conda-forge'   # highest priority
~~~

~~~
$ conda create -n vprimer python 'biopython==1.76'
$ conda activate vprimer
$ conda install pandas vcfpy pysam joblib samtools bcftools tabix primer3 primer3-py blast
~~~

~~~
$ pip uninstall vprimer
~~~

~~~
$ pip install git+https://github.com/ncod3/vprimer
~~~

## Getting Started

~~~
$ git clone https://github.com/ncod3/data_vprimer
~~~

~~~
$ ln -s data_vprimer/test_script/*.sh .
$ sh ./010.show_samples.sh

overwrite

$ cat data_vprimer/bams/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt_filled > refs/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt

$ sh ./020.6samples_indel.sh

~~~

## Usage

## Note

## Authors
- Satoshi Natsume s-natsume@ibrc.or.jp

See also the list of contributors who participated in this project.

## Licence

Copyright (c) 2023 Satoshi Natsume
Released under the MIT license
https://github.com/YukinobuKurata/YouTubeMagicBuyButton/blob/master/MIT-LICENSE.txt

## Acknowledgements

