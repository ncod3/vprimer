[../README.md](../README.md)

# コマンド詳細 (日本語)

## 利用方法

vprimer [options]

### 必須項目（２つ）

<dl>
<dt>
--ref リファレンスFasta
</dt>
<dd>
<p><p>
VCFファイル作成時に用いたbamファイルのリファレンスFastaを指定する。プレーンテキストでもgzip圧縮形式でも可。
</p></p>
</dd>
</dl>



<dl>
<dt>
--vcf VCFファイル
</dt>
<dd>
<p><p>
各サンプルのバリアントが収納されたVCFファイルを指定する。
</p></p>
</dd>
</dl>


### 選択項目

<dl>
<dt>
--out_dir 結果出力ディレクトリ名
</dt>
<dd>
<p><p>
結果を出力するディレクトリ名を指定する。デフォルトは「out_vprimer」。
</p></p>
</dd>
</dl>



<dl>
<dt>
--show_samples
</dt>
<dd>
<p><p>
解析の事前処理として、VCF内に収められたサンプル名を表示して終了する。システム内ではサンプル名を３種類で指定可能である。VCFファイルに書かれたサンプル名そのもの(fullname)、'/' で区切られたPATHを取り除いた名前(basename)、basenameから拡張子.bamを取り除いた名前(nickname)である。この情報は、refsの中の _sample_name.txt という拡張子の付いたファイルに保存されており、このファイルの nickname をユーザが編集することで、システム内で利用可能となる。
</p></p>
</dd>
</dl>



<dl>
<dt>
--show_fasta
</dt>
<dd>
<p><p>
解析の事前処理として、fasta内に収められたcontig名とそのサイズを表示して終了する。
</p></p>
</dd>
</dl>



<dl>
<dt>
--a_sample [サンプル名 [サンプル名 ...]]<br>
--b_sample [サンプル名 [サンプル名 ...]]
</dt>
<dd>
<p><p>
ユーザが解析したいグループを２つに分ける時の、各グループのサンプル群。
</p></p>
</dd>
</dl>



<dl>
<dt>
--auto_group [サンプル名 [サンプル名 ...]]
</dt>
<dd>
<p><p>
解析グループを固定で分けず、genotypeで自動的に分ける時の、使用するサンプル群。最終的なプライマー情報には、サンプル群がどのように分けられたかが記述される。
</p></p>
</dd>
</dl>


<!-- ここからしたがまだ -->

<dl>
<dt>
--pick_mode
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--target
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--indel_size
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--product_size 最小サイズ-最大サイズ
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--homo_only
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--enzyme
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--enzyme_file
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--p3_normal
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--p3_amplicon
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--amplicon_param
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--snp_filter
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--bam_table
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--min_max_depth
</dt>
<dd>
<p><p>
解析グループを固定で分けず、genotypeで自動的に分ける時の、使用するサンプル群。最終的なプライマー情報には、サンプル群がどのように分けられたかが記述される。
</p></p>

</dd>
</dl>



<dl>
<dt>
--progress
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--stop
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--ini_file
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>



<dl>
<dt>
--thread
</dt>
<dd>
<p><p>

</p></p>
</dd>
</dl>


