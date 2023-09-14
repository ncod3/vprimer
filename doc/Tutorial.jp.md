[../README.md](../README.md) | [Usage.jp.md](Usage.jp.md)

# V-primer チュートリアル (日本語)

>１．デモデータ概説  
>２．refs ディレクトリ  
>３．解析の基本３フェーズ、variant、marker、primer  
>４．出力取りまとめ、formpass  
>５，SNP解析モードの snpfilter、chkhdimer

## １．デモデータ概説

このチュートリアルでは、デモデータに基づき動作の解説を行う。

デモデータをダウンロードし、test_script の下の７つのスクリプトを順次実行していく。７つのスクリプトは３つの種類に分かれている。スクリプト名の右には、→ の先にそれぞれのスクリプトの結果出力ディレクトリが書かれている。

### 種類１：初期設定

必須項目であるリファレンスFastaとVCFファイルのみを指定し、解析の事前処理を行う。

- 010.show_samples.sh → out_vprimer

結果出力ディレクトリ (--out_dir) を明示的に指定していないことから、結果の出力はデフォルト「out_vprimer」に書き出される。結果出力ディレクトリには、logsと、bakというディレクトリが作成され、logsの下には最新の稼動ログ「vprimer_log.txt」が１つだけ保存される。bakには、何度か解析を実施したとしても、決して既存の情報を上書きしてしまわぬよう、同名のファイルがあったなら必ずbakにコピーを残してある。また、使用する各種データの準備を行うrefsディレクトリが作成される。refsディレクトリの詳細については後述する。

### 種類２：ユーザ指定の２グループ分割
サンプル群の２グループ分割をユーザが指定する。スクリプトでは、a、b、２つのグループにそれぞれ３サンプルがカンマ区切りで指定されている。
>--a_sample MP2_012,MP2_013,MP2_014  
--b_sample MP2_015,MP2_018,MP2_020

解析モードはそれぞれindel、 caps、snpを指定し、出力ディレクトリは次の通り。

- 020.6samples_indel.sh → out_vprimer_020_indel
- 021.6samples_caps.sh → out_vprimer_021_caps
- 022.6samples_snp.sh → out_vprimer_022_snp

### 種類３：genotypeによる自動２グループ分割
サンプル群の２グループ分割をgenotypeにより自動で行う。スクリプトでは、使用するサンプル群が６サンプル指定されている。

>--auto_group MP2_012,MP2_013,MP2_014,MP2_015,MP2_018,MP2_020

解析モードはそれぞれindel、 caps、snpを指定し、出力ディレクトリは次の通り。

- 030.auto_group_indel.sh → out_vprimer_030_indel
- 031.auto_group_caps.sh → out_vprimer_031_caps
- 032.auto_group_snp.sh → out_vprimer_032_snp

## ２．refs ディレクトリ

V-primer は、最初に実行された場所の直下に refs というディレクトリを作成し、そこに、解析に必要な情報をまとめて作成する。--show_samples オプションを指定した場合には最小限の 1) 〜 3) が準備され、実際の解析においては、1) 〜 6) が準備される。順に説明する。

### 1) リファレンスfasta
- slink_{fasta名}:
  - ユーザが指定したfastaへのシンボリックリンク。
- {fasta名}_BGZIP.gz:
  - ユーザ指定のfastaを、bgzipで再度圧縮し直したファイル。
- {fasta名}_BGZIP.gz.chrom.txt:
  - 染色体名と、長さを記述したファイル
- {fasta名}_BGZIP.gz.fai:
  - fastaのindexテキストファイル
- {fasta名}_BGZIP.gz.gzi:
  - fastaのindexファイル、bgzip用。
- {fasta名}_BGZIP.gz.pickle:
  - fastaを、プログラム内部で用いる辞書形式に変換しpickleで保存したもの。次回以降早い立ち上げを行うため。

### 2) vcfファイル
- slink_{vcfファイル名}:
  - ユーザが指定したvcfへのシンボリックリンク
- {vcfファイル名}_GTonly.vcf.gz.tbi:
  - ユーザ指定のvcfを、FORMATにGTのみ抽出したvcfファイル。
- {vcfファイル名}_sample_bam_table.txt:
  - vcfの各サンプルと、対応するbamもしくはbedの対応表のテンプレート。２つのフィールド、vcf_sampleとbam_or_bedがあり、vcf_sampleにはあらかじめサンプル名が記述されている。bam_or_bedに、指定したいbamファイルもしくはbedファイルを記述する。
- {vcfファイル名}_sample_name.txt
  - vcf内のサンプル名詳細。５つのフィールドがある。システム内でのサンプル指定は nickname で行うことができる。
    - no: 先頭からの番号(0オリジン)
    - group: ユーザ指定のグループ名を記述することでグループ化できる。初期状態は、'-'(所属なし)。
    - nickname: システムで用いるもっとも一般的なサンプル名。
    - basename: パス表記がされている場合、もっとも下流に書かれた名前。
    - fullname: vcfに書かれた名前そのもの。

### 3) bedディレクトリ
bamファイルを用いて、プライマー生成の際に有効depthの判断を行う場合に作成される各種ファイルが置かれる。この時点ではディレクトリが作成されるのみ。

### 4) bed ディレクトリ

__BB.BEDファイル__

サンプル名に対応するbamファイルが {vcfファイル名}_sample_bam_table.txt の中で指定されており、そのサンプルが解析で用いられたならば、bamファイルのデプス評価が実施される。--min_max_depth 最低デプス-最高デプス で指定されたデプス範囲により、bamファイルごとに拡張子、.m{最低デプス}_x{最高デプス}.bb.bed のbedファイルが作成される。

bedファイルの先頭には、# で始まるいくつかのコメントが書かれている。ここには bedファイルが作成された時の情報が残されている。特に bamファイルのmd5値が計算されており(bam_md5)、指し示すbamが変更されたことが判明した時点で、bedファイルを作成し直す。

最初の # 行の固まりが終わると、bed行となる。

リファレンスFastaの全領域において、デプスが指定された範囲内の領域は、(valid_11) (11は11bpを示す、以下同様) 、デプスが０の領域を Z_94、デプスがしきい値より薄い領域を thin_147、デプスがしきい値より厚い領域を THICK_627 と、bedファイルの４カラム目に表示している。

bed行がすべて終わると、# で始まる以下の統計情報が付加されている。

>\# genome_total_len      4,000,000  
>\# width_coverage_nozero 3,540,700  
>\# width_coverage_nozero_rate    88.52%  
>\# width_coverage_valid  2,165,200  
>\# width_coverage_valid_rate     54.13%  
>\# width_coverage_thin   1,373,936  
>\# width_coverage_thin_rate      34.35%  
>\# width_coverage_zero   459,300  
>\# width_coverage_thick  1,564  
>\#  
>\# depth_valid_average   14.60  
>\# depth_thin_average    2.66  
>\#  
>\# depth_total   38,146,632  
>\# depth_valid   31,602,544  
>\# depth_thin    5,753,082  
>\# depth_thick   791,006  
>\# depth_zero    0  

__BTA.BEDファイル__

指定されたサンプル群ごとに、bb.bedファイルの正常範囲外の領域をまとめたbedファイル(bed_thin_alignファイル)が作成される。ファイル名は、bed_thal_{年_月日_時分_秒}.m{最小デプス}_x{最大デプス}.bta.bed である。bedファイルの先頭には、# で始まる、集められた bb.bed ファイルの情報が書かれている。最初の # 行の固まりが終わると、bed行となる。この領域はデプスが正常範囲外であることを示す。ファイルの最後には、次のような統計情報が書かれている。

>\#  
>\# genome_total_len      373,245,519  
>\# bed_thal_valid_length 326,230,263  
>\# bed_thal_valid_rate   87.40%  
>\#

### 5) caps用 enzyme name list

解析が始まると、解析モードに関わらず、caps用制限酵素名一覧表が作成される。

- caps_enzyme_name_list.whole_enzyme.txt
  - V-primerのシステムで利用可能な制限酵素名の一覧(965)である。
- caps_enzyme_name_list.txt.original
  - よく使いそうな制限酵素を選択した(71)一覧である。
- caps_enzyme_name_list.txt
  - システムのデフォルトファイル。当初は上記の71が記述されている。
- slink_caps_enzyme_name_list.txt
  - ユーザが指定したファイルへのシンボリックリンク

### 6) Primer3用パラメータ指定ファイル (normal / amplicon)

解析が始まると、解析モードに関わらず、Primer3用パラメータ指定ファイルが作成される。

- p3_normal.txt.original
  - 解析モードが indel、caps の時のパラメータ指定ファイルのオリジナル。
- p3_normal.txt
  - 解析モードが indel、caps の時のデフォルトファイル。
- p3_amplicon.txt.original
  - 解析モードが snp の時のパラメータ指定ファイルのオリジナル。
- p3_amplicon.txt
  - 解析モードが snp の時のデフォルトファイル。

## ３．解析の基本３フェーズ、variant、marker、primer

V-primerの解析は３つのフェーズで行われる。それぞれの結果がファイルに書き出される。次に行われるフェーズは、直前のフェーズに書き出されたファイルを読み込んで解析を行う。

### 1) variant フェーズ

[010_VARIANTのファイル項目](010_VARIANT.md)

### 2) marker フェーズ


### 3) primer フェーズ



## ４．出力取りまとめ、formpass

## ５，SNP解析モードの snpfilter、chkhdimer


[../README.md](../README.md) | [Usage.jp.md](Usage.jp.md)

