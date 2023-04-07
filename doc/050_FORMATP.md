[Description](DESCRIPTION.md)

# 050_formatP

<dl>
<dt>
chrom, pos, var_type, mk_type, gts_segr_lens , auto_grp0, auto_grp1
</dt>
<dd>
<p><p>
(010_variantより引き継ぎ)
</p>
</dd>
</dl>


<dl>
<dt>
marker_id
</dt>
<dd>
<p><p>
(020_markerより引き継ぎ)
</p>
</dd>
</dl>


<dl>
<dt>
try_cnt, complete
</dt>
<dd>
<p><p>
(030_markerより引き継ぎ)
</p>
</dd>
</dl>


<dl>
<dt>
g0_name, g1_name, g0_gt, g1_gt, targ_ano, g0_vseq, g1_vseq
</dt>
<dd>
<p><p>
グループ０とグループ１で対比されている情報。テーブルは、グループの番号をnumで行に分けた。また、カラムのXは、グループの番号が入る。
</p>
<p>
gX_nameはグループ名、gX_gtはgenotype、targ_anoはカンマで区切られたアリル番号で、グループがどのアリル番号と対応しているかを示す。
</p>

|num|gX_name|gX_gt|targ_ano|
|:---:|:---:|:---:|:---:|
| 0 |a|0 / 0|0|
| 1 |b|0 / 1| 1|

<p>
gX_vseqは、バリアントの配列。ここでは indel, caps, snp の時の具体例を示す。
</p>

|num|gX_vseq (indel)|gX_vseq (caps)|gX_vseq (snp)|
|:---:|:---:|:---:|:---:|
| 0 |GACCATTACTCGCTTACTCGCTTGTATGCTCCA |G|G
| 1 |ACCA|A|T

</dd>
</dl>


<dl>
<dt>
comment
</dt>
<dd>
<p><p>
１つのpositionで複数のマーカーが設計された場合や、template sequence内にバリアントが確認される場合、注意をうながすためにnoteが書かれる。
</p>
</dd>
</dl>


<dl>
<dt>
enzyme
</dt>
<dd>
<p>
<p>
CAPSマーカーで使用される制限酵素。
</p>
</dd>
</dl>


<dl>
<dt>
g0_product_size, g1_product_size
</dt>
<dd>
<p><p>
グループ０側とグループ１側の、プロダクトサイズ。
</p>

name|indel|caps|snp
---|---|---|---
g0_product_size |389|334|365
g1_product_size |361|334|365

</dd>
</dl>


<dl>
<dt>
product_gc_contents
</dt>
<dd>
<p><p>
REFから切り出してきた配列における両プライマー間のProductにおけるGC contents (%).
</p>
</dd>
</dl>


<dl>
<dt>
diff_length
</dt>
<dd>
<p><p>
バリアントの長さの差。SNPの場合、通常、アリル長の差は0である。
</p>

name|indel|caps|snp
---|:---:|:---:|:---:|
diff_length|28|0|0

</dd>
</dl>


<dl>
<dt>
g0_digested_size, g1_digested_size

</dt>
<dd>
<p><p>
CAPSマーカーの場合、グループ０側のバリアントにより制限酵素でdigestされる長さ。
</p>

name|value|
---|---|
g0_product_size |334
g1_product_size |334/267/67

<p>
g0側はdigestされないためPCRの結果、334bpの長さが１本になる。一方、g1側は、一方のアリルは切断されず、もう一方のアリルだけが切断されるため 334/267/67 の３本のバンドがあらわれる。
</p>
</dd>
</dl>


<dl>
<dt>
digested_gno, digested_ano
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
left_primer_id, PRIMER_LEFT_0_SEQUENCE, right_primer_id, PRIMER_RIGHT_0_SEQUENCE
</dt>
<dd>
<p><p>
word
</p>

name|value
:---:|:---:
left_primer_id |chrom_01:62446-62470:plus
PRIMER_LEFT_0_SEQUENCE|TTCTCCAAGATCGATTCACTCTGTT
right_primer_id |chrom_01:62810-62834:minus
PRIMER_RIGHT_0_SEQUENCE |TACCTGCTAGTCCAAGCTAATTTGT

</dd>
</dl>

[Description](DESCRIPTION.md)

