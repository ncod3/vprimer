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
--a_sample {サンプル名 {サンプル名 ...}}<br>
--b_sample {サンプル名 {サンプル名 ...}}
</dt>
<dd>
<p><p>
ユーザが解析したいグループを２つに分ける時の、各グループのサンプル群。片側に「ref」を指定すると、リファレンスFastaを単一のサンプルとして扱うことができる。
</p></p>
</dd>
</dl>



<dl>
<dt>
--auto_group {サンプル名 {サンプル名 ...}}
</dt>
<dd>
<p><p>
解析グループを固定で分けず、genotypeで自動的に分ける時の、使用するサンプル群。vcf内のすべてのサンプルを示す、「all」を使用可能。最終的なプライマー情報には、サンプル群がどのように分けられたかが記述される。
</p></p>
</dd>
</dl>


<!-- ここからしたがまだ -->

<dl>
<dt>
--pick_mode { indel | caps | snp }
</dt>
<dd>
<p><p>
マーカーを取得する際の３種類のモードを指定する。indelとcapsは並列して指定可能だが、snpは単独でしか指定できない。デフォルトは、「indel」。
</p></p>
</dd>
</dl>



<dl>
<dt>
--target { scope := chrom_name | chrom_name:range_str }
</dt>
<dd>
<p><p>
マーカーを取得するリファレンスfasta上の範囲を指定する。「all」と指定すると全染色体が対象となる。個別の範囲指定は、染色体名、または染色体上の範囲 (chrom_name:from-to) を列挙する。
</p></p>
</dd>
</dl>



<dl>
<dt>
--indel_size 最小サイズ-最大サイズ
</dt>
<dd>
<p><p>
indelを対象とする場合、２つのバリアントの長さの差の範囲を指定する。最大サイズを越える差は解析対象外となる。最小サイズ未満の差は indel では対象外となるが、caps では解析対象となる。したがって caps をSNPのみを対象にしたい場合は、最小サイズを１として設定することにより、長さの差が０のバリアントのみを解析対象とすることができる。デフォルトは、「20-200」。
</p></p>
</dd>
</dl>



<dl>
<dt>
--product_size 最小サイズ-最大サイズ
</dt>
<dd>
<p><p>
primer3でプライマー設計をする際に用いるプロダクトサイズの範囲を指定する。複数の範囲を一度に指定することはできない。デフォルトは、「200-500」。
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



