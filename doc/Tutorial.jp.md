[../README.md](../README.md) | [Usage.jp.md](Usage.jp.md)

# V-primer チュートリアル (日本語)

## １．デモデータ概説

このチュートリアルでは、デモデータに基づき動作の解説を行う。

デモデータをダウンロードし、test_script の下の７つのスクリプトを順次実行していく。７つのスクリプトは３つの種類に分かれている。スクリプト名の右には、→ の先にそれぞれのスクリプトの結果出力ディレクトリが書かれている。

### 種類１：初期設定

必須項目であるリファレンスFastaとVCFファイルのみを指定し、解析の事前処理を行う。

- 010.show_samples.sh → out_vprimer

結果出力ディレクトリ (--out_dir) を明示的に指定していないことから、結果の出力はデフォルト「out_vprimer」に書き出される。結果出力ディレクトリには、logsと、bakというディレクトリが作成され、logsの下には最新の稼動ログ「vprimer_log.txt」が１つだけ保存される。bakには、何度か解析を実施したとしても、決して既存の情報を上書きしてしまわぬよう、同名のファイルがあったなら必ずbakにコピーを残してある。また、使用する各種データの準備を行うrefsディレクトリが作成される。refsディレクトリの詳細については後述する。

### 種類２：ユーザ指定のグルーピング
サンプルのグルーピングをユーザが指定する。スクリプトでは、a、b、２つのグループにそれぞれ３サンプルがカンマ区切りで指定されている。
>--a_sample MP2_012,MP2_013,MP2_014  
--b_sample MP2_015,MP2_018,MP2_020

解析モードはそれぞれindel、 caps、snpを指定する。

- 020.6samples_indel.sh → out_vprimer_020_indel
- 021.6samples_caps.sh → out_vprimer_021_caps
- 022.6samples_snp.sh → out_vprimer_022_snp

### 種類３：genotypeによる自動グルーピング
サンプルのグルーピングをgenotypeにより自動で行う。スクリプトでは、使用するサンプル群が６サンプル指定されている。

>--auto_group MP2_012,MP2_013,MP2_014,MP2_015,MP2_018,MP2_020

解析モードはそれぞれindel、 caps、snpを指定する。

- 030.auto_group_indel.sh → out_vprimer_030_indel
- 031.auto_group_caps.sh → out_vprimer_031_caps
- 032.auto_group_snp.sh → out_vprimer_032_snp

それぞれのスクリプトにしたがって、動作の内容を説明する。

## ２．デモスクリプト毎の説明

### 010.show_samples.sh

必須項目であるリファレンスFastaとVCFファイルのみを指定し、解析の事前処理として refs ディレクトリを作成する。

### refs ディレクトリ
vprimerを実行したディレクトリの直下に、refs ディレクトリが作成され、解析に必要な環境がこの中に整えられる。

--show_samples オプションを指定した場合には最小限の設定が行われ、以下の３種類のファイル、ディレクトリが準備される。

#### 1) リファレンスfasta
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
  - プログラム内部で用いるfastaの辞書形式をpickleで保存したもの。次回以降早い立ち上げを行う。

#### 2) vcfファイル
- slink_{vcfファイル名}:
  - ユーザが指定したvcfへのシンボリックリンク
- {vcfファイル名}_GTonly.vcf.gz.tbi:
  - ユーザ指定のvcfを、FORMATにGTのみ抽出したvcfファイル。
- {vcfファイル名}_sample_bam_table.txt:
  - vcfの各サンプルと、対応するbamもしくはbedの対応表。
- {vcfファイル名}_sample_name.txt
  - vcf内のサンプル名詳細。５つのフィールドがある。システム内でのサンプル指定は nickname で行うことができる。
    - no: 先頭からの番号(0オリジン)
    - group: ユーザ指定のグループ名を記述することでグループ化できる。初期状態は、'-'(所属なし)。
    - nickname: システムで用いるもっとも一般的なサンプル名。
    - basename: パス表記がされている場合、もっとも下流に書かれた名前。
    - fullname: vcfに書かれた名前そのもの。


#### 3) bedディレクトリ
bamファイルを用いて、プライマー生成の際に有効depthの判断を行う場合に作成される各種ファイルが置かれる。この時点ではディレクトリが作成されるのみ。






[../README.md](../README.md) | [Usage.jp.md](Usage.jp.md)

