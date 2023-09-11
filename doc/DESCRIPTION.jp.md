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
</p>

</dd>
</dl>

<dl>
<dt>
--show_fasta
</dt>
<dd>
<p><p>
解析の事前処理として、fasta内に収められたcontig名とそのサイズを表示して終了する。
</p>

</dd>
</dl>

