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
サンプルのグルーピングをユーザが指定する。解析モードはそれぞれindel、 caps、snpを指定する。

- 020.6samples_indel.sh → out_vprimer_020_indel
- 021.6samples_caps.sh → out_vprimer_021_caps
- 022.6samples_snp.sh → out_vprimer_022_snp

### 種類３：genotypeによる自動グルーピング
サンプルのグルーピングをgenotypeにより自動で行う。解析モードはそれぞれindel、 caps、snpを指定する。

- 030.auto_group_indel.sh → out_vprimer_030_indel
- 031.auto_group_caps.sh → out_vprimer_031_caps
- 032.auto_group_snp.sh → out_vprimer_032_snp

それぞれのスクリプトにしたがって、動作の内容を説明する。

## ２．デモスクリプト毎の説明

### 010.show_samples.sh

必須項目であるリファレンスFastaとVCFファイルのみを指定し、解析の事前処理として refs ディレクトリを作成する。






[../README.md](../README.md) | [Usage.jp.md](Usage.jp.md)

