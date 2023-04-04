# V-primer

V-primerは、VCF(variant call format)形式の genotyping データから、全ゲノム規模のInDelマーカーとSNPマーカーを効率的に設計するためのソフトウェアです。

## SYNOPSIS (書式)
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

## Description (概要)

複数のサンプルbamから作成されたVCFファイルを用いて、２つのサンプル群を識別可能なIndelマーカーもしくはSNPマーカーを設計します。サンプル群の指定方法は次の２種類があります。１）比較したい２種類のサンプル群をユーザ指定する方法、２）指定されたサンプル群範囲の中でVCFのgenotypeにより自動的に２グループが生成される方法、です。

## Installation (インストール)

conda を用いて動作環境を作成し、pipを用いてこの githubサイトから vprimer をインストールします。

まず、各種condaのツールをインストールするための channel の設定を確認します。highest priority と、lowest priority が、以下のように設定されているならば問題はありません。

```
$ conda config --get channels

--add channels 'conda-forge'   # lowest priority
--add channels 'bioconda'
--add channels 'defaults'   # highest priority
```

もし、上記の設定となっていない場合は、以下の３行を実行してください。

```
$ conda config --add channels 'conda-forge'
$ conda config --add channels 'bioconda'
$ conda config --add channels 'defaults'

```

最初に、conda を用いて、"vprimer" と名付けた仮想環境を作成します。

```
$ conda create -n vprimer python 'biopython==1.76'
```

作成した仮想環境を activate します。

```
$ conda activate vprimer
```

残りの必要環境を conda install コマンドで準備します。

```
(vprimer) $ conda install pandas vcfpy pysam joblib samtools bcftools bedtools tabix primer3 primer3-py blast
```

vprimerをインストールします。まず最初に、uninstall をしてみます。

```
(vprimer) $ pip uninstall vprimer
WARNING: Skipping vprimer as it is not installed.
```

インストールされていない場合、上記のメッセージが出ますので、インストールを続けます。

```
(vprimer) $ pip install git+https://github.com/ncod3/vprimer
Collecting git+https://github.com/ncod3/vprimer
  Cloning https://github.com/ncod3/vprimer to /tmp/pip-req-build-sljhy9du
...
Successfully installed vprimer-1.0.1
```

"Successfully" のメッセージが出たならば、インストール完了です。


## Demo (動作デモ)

任意の場所に、デモ作業用ディレクトリを作成し、動作デモ用データをダウンロードします。次のURLにデータが置いてあります。( https://github.com/ncod3/data_vprimer )。

任意のディレクトリ名で、作業ディレクトリを作成し、移動します。

```
(vprimer) $ mkdir test_vprimer
(vprimer) $ cd test_vprimer
```

この作業ディレクトリに、動作デモ用データをダウンロードします。

```
(vprimer) $ git clone https://github.com/ncod3/data_vprimer
```
data_vprimer というディレクトリが作成され、データがダウンロードされています。

data_vprimer の下の、test_script というディレクトリに準備された、デモ用シェルスクリプトを、カレントディレクトリにシンボリックリンクします。

```
(vprimer) $ ln -s data_vprimer/test_script/*.sh .
```

以下のように、010.show_samples.sh というシェルスクリプトを実行します。

```
(vprimer) $ sh ./010.show_samples.sh
```

refs というディレクトリが作成され、vprimerの解析の準備ができました。

VCFを作成した際のサンプルbamファイルを利用して、sequenceの張り付きの薄い箇所を計測するため、refs/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt というフィアルに、サンプルに対応するbamファイルのパスを記述します。

この動作デモでは、すでに準備してあるファイルを、refsの下のファイルに、overwriteします。

```
(vprimer) $ cat data_vprimer/bams/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt_filled > refs/MP2_6_TDr96_F1.vcf.gz_GTonly.vcf.gz_sample_bam_table.txt
```

順次、デモ用シェルスクリプトを実行します。

```
(vprimer) $ sh ./020.6samples_indel.sh
(vprimer) $ sh ./010.show_samples.sh
(vprimer) $ sh ./020.6samples_indel.sh
(vprimer) $ sh ./021.6samples_caps.sh
(vprimer) $ sh ./022.6samples_snp.sh
(vprimer) $ sh ./030.nogroup_indel.sh
(vprimer) $ sh ./031.nogroup_caps.sh
(vprimer) $ sh ./032.nogroup_snp.sh

```

## Usage (使用法)
### required（必須項目）
<dl>
<dt>--ref ref_file</dt>
<dd>
reference fastaを指定する。
</dd>
</dl>

<dl>
<dt>--vcf vcf_file</dt>
<dd>
vcfファイルを指定する。
</dd>
</dl>

<dl>
--target [scope [scope ...]]

解析するfastaの範囲を指定する。
</dl>

<dl>
--pick_mode mode

ピックアップするマーカーの種類を指定する。
</dl>

### for preparation（準備）

<dl>
<dt>
--show_fasta
</dt>
<dd>
fastaの情報を表示する。
</dd>
</dl>

<dl>
<dt>
--show_samples
</dt>
<dd>
VCFファイルの内容を表示する。
</dd>
</dl>

### selection required（必須選択項目）

<dl>
<dt>
--auto_group [sample [sample ...]]<br>
もしくは <br>
--a_sample [sample [sample ...]]<br>
--b-sample [sample [sample ...]]
</dt>
<dd>
サンプル群の指定方法と使用するサンプル群範囲を指定する。
</dd>
</dl>

### optional（任意項目）

<dl>
<dt>
--indel_size min-max
</dt>
<dd>
InDelのサイズを指定する。
</dd>
</dl>

<dl>
<dt>
--product_size min-max
</dt>
<dd>
プロダクトサイズを指定する。
</dd>
</dl>

<dl>
<dt>
--enzyme enzyme_name
</dt>
<dd>
CAPSマーカーで使用する制限酵素名を指定する。
</dd>
</dl>

<dl>
<dt>
--enzyme_file file
</dt>
<dd>
CAPSマーカーで使用する制限酵素名が書かれたファイルを指定する。
</dd>
</dl>

<dl>
<dt>
--p3_normal file
</dt>
<dd>
Primer3に設定するパラメータが書かれたファイルの指定。InDelもしくはCAPS用。
</dd>
</dl>

<dl>
<dt>
--p3_amplicon file
</dt>
<dd>
Primer3に設定するパラメータが書かれたファイルの指定。SNP用。
</dd>
</dl>

<dl>
<dt>
--amplicon_param parameter
</dt>
<dd>
SNPマーカー構築の際のパラメータを指定する。
</dd>
</dl>

<dl>
<dt>
--bam_table file
</dt>
<dd>
シーケンスが薄い張り付きの部分を避けてプライマー設計を行うために、VCF内サンプル名に対応するbamファイルのパスが書かれたファイルを指定する。
</dd>
</dl>

<dl>
<dt>
--out_dir dir_name
</dt>
<dd>
結果が出力されるディレクトリを指定する。
</dd>
</dl>

<dl>
<dt>
--thread num
</dt>
<dd>
使用するCPU数を指定する。
</dd>
</dl>
	


## Authors (著者)
- Satoshi Natsume s-natsume@ibrc.or.jp

See also the list of contributors who participated in this project.

## Licence (ライセンス)

Copyright (c) 2023 Satoshi Natsume
Released under the MIT license
https://github.com/YukinobuKurata/YouTubeMagicBuyButton/blob/master/MIT-LICENSS
E.txt

## Changelog (更新履歴)
- 2023-04-03
	- 1.0.1 パラメータ指定修正
- 2023-04-02 
	- 1.0.0 公開





