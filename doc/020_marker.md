[../README.md](../README.md) | [Usage.jp.md](Usage.jp.md)

# 020_marker

<dl>
<dt>
marker_id
</dt>
<dd>
<p><p>

マーカを特定可能な情報。

| pick_mode |marker_id|
|:---:|:---:|
|indel|chrom_01.62651.0,1.indel.INDEL.00/01.0,32,4|
|caps|chrom_01.19308.0,1.snp.CAPS.00/01.1,21,MseI|
|snp|chrom_01.19308.0,1.snp.SNP.00/01.0,1,1|

indelとsnpの場合、"." で区切られたフィールドの意味は以下の通り。

|name|indel|snp|
|:---:|:---:|:---:|
|chrom|chrom_01|chrom_01|
|pos|62651|19308|
|ano_gno|0,1|0,1|
|var_type|indel|snp|
|mk_type|INDEL|SNP|
|alstr_gno|00/01|00/01|
|detail|0,32,4|0,1,1|

chrom, pos は 染色体とポジション。ano_gnoは、グループ番号ごとのアリル番号カンマ区切り。var_typeは、バリエションタイプ。mk_typeはマーカータイプ。alstr_gnoは、グループごとのアリル連結文字列。"/" 区切り。

detailのフィールドは次の通り。

||name|||
|:---:|:---:|:---:|:---:|
|pick_mode| longer_group | longer_length | shorter_length |
|indel|0|32|4|
|snp|0|1|1|


longer_groupは、長さの長い方のグループ番号。longer_lengthは、長い方の長さ、shorter_length は短い方の長さ。snpだと、常に 0,1,1 となる。

caps の場合、"." で区切られたフィールドの意味は以下の通り。

|name|caps|
|:---:|:---:|
|chrom|chrom_01|
|pos|19308|
|ano_gno|0,1|
|var_type|snp|
|mk_type|CAPS|
|alstr_gno|00/01|
|detail|1,21,MseI|

detailのフィールドは次の通り。

|pick_mode|digested_gno|found_pos|enzyme_name|
|:---:|:---:|:---:|:---:|
|caps|1|21|MseI|

digested_gno は、消化される側のグループ番号、found_pos は、TARGET_SEQUENCE 内で 制限酵素の recognition siteが見つかった相対位置。enzyme_nameは、制限酵素名。

</p>
</dd>
</dl>


<dl>
<dt>

chrom, pos, targ_grp, vseq_gno_str, gts_segr_lens, targ_ano, var_type, mk_type, auto_grp0, auto_grp1

</dt>
<dd>
<p><p>
(010_variantより引き継ぎ)
</p>
</dd>
</dl>


<dl>
<dt>
set_enz_cnt
</dt>
<dd>
<p><p>

010_variantの、"set_n" (異なるアリルの組み合わせの全体数と自分の順番) に加えて、pick_mode が CAPS の場合、有効となったenzymeの全体数と現在解析中の自分の順番(enz_cnt) を、"-" でつないだもの。pick_mode が CAPS 以外であれば、enz_cnt は、"1/1" が入る。

|name|value|
|:---:|:---:|
|set_n| 2/3|
|enz_cnt|1/2|
|set_enz_cnt|2/3-1/2|

set_enz_cntの "-" の左側 "2/3" (set_n) は、現在のバリアントに、異なるアリルの組み合わせが３つ存在しており、現在解析しているものがそのうちの２番目であることを示す。右側 "1/2" は、CAPS解析で 有効な制限酵素が２つあって、現在解析しているものが１番目であることを示す。

</p>
</dd>
</dl>


<dl>
<dt>
marker_info
</dt>
<dd>
<p><p>

indelとsnpの場合

| |indel|snp|
|:---:|:---:|:---:|
|marker_info|0.32.4.28.0|0.1.1.0.0|

"." で区切った各フィールドの意味は次の通り。

| |indel|snp|
|:---:|:---:|:---:|
| longer_group |0|0|
| longer_length|32|1|
| shorter_length|4|1|
| diff_length|28|0|
| digested_pos|0|0|

longer_group は、比較しているアリルの長さが長い方のグループ、longer_length は、長い方のアリルの長さ、shorter_length は、短い方のアリルの長さ、diff_length は長さの差、digested_pos は、常に０。

capsの場合、

| |caps|
|:---:|:---:|
|marker_info|MseI.1.21.T^TA_A.1|


CAPSマーカーの制限酵素の効果は、biopython の Working with restriction enzymes (http://biopython.org/DIST/docs/cookbook/Restriction.html ) を使っている。さらに、biopython <= 1.76 の、IUPACAmbiguousDNA() モジュールを用いることで、Ambiguous なパターンをそのまま効果判定に用いている。


"." で区切った各フィールドの意味は次の通り。

|name|value|
|:---:|:---:|
|enzyme_name|MseI|
|digested_gno|1|
|found_pos|21|
|digest_pattern|T^TA_A|
|digested_pos|1|



</p>
</dd>
</dl>


<dl>
<dt>
vseq_lens_ano_str
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g0_seq_target_len
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g0_seq_target
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g1_seq_target_len
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g1_seq_target
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
seq_template_ref_len
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
seq_template_ref_abs_pos
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
seq_template_ref_rel_pos
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
SEQUENCE_TARGET
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
SEQUENCE_TEMPLATE
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


[../README.md](../README.md) | [Usage.jp.md](Usage.jp.md)

