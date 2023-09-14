[README](../README.md) | [Tutorial (Japanese doc)](doc/Tutorial.jp.md) | [Usage (Japanese doc)](doc/Usage.jp.md)

# 040_FormatF, 050_FormatP

040_FormatF と、050_FormatP は、030_primer に記録された、プライマー作成完了(complete == 1) と、プライマー作成失敗（complete != 1) の情報をもとに、失敗したプライマー情報を 040_FormatFに、成功したプライマー情報を 050_FormatP に振り分けたものです。

成功したプライマー情報を集めた 050_FormatP には、さらにPCR長の情報等を付加して、利用しやすい情報としてまとめています。


<dl>
<dt>

chrom, pos, targ_ano, var_type, mk_type, auto_grp0, auto_grp1, gts_segr_lens


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

in_target, product_gc_contents, try_cnt, complete,  left_primer_id, PRIMER_LEFT_0_SEQUENCE, right_primer_id, PRIMER_RIGHT_0_SEQUENCE


</dt>
<dd>
<p><p>
(030_primerより引き継ぎ)
</p>
</dd>
</dl>


<dl>
<dt>
g0_vseq, g1_vseq, g0_gt, g1_gt
</dt>
<dd>
<p><p>

グループ同士で、比較対象となっているsequence。そして、それぞれのグループのgenotype。

|name|indel|caps|snp|
|:---:|:---:|:---:|:---:|
| g0_vseq|ACCATTACTCGCTTACTCGCTTGTATGCTCCA|A|G|
| g1_vseq|ACCA|T|T|
| g0_gt|0/0|0/0|0/0|
| g1_gt|0/1|0/1|0/1|
| targ_ano|0,1|0,1|0,1|

g0_gtと、g1_gtは、どのpick_modeでも、0/0 と 0/1 になっている。グループ０は、0/0のホモ、グループ１は、0/1 のヘテロである。

targ_anoにより、0と1のアリルが比較対象になっていることがわかる。

</p>
</dd>
</dl>


<dl>
<dt>
dup_pos
</dt>
<dd>
<p><p>

CAPSマーカーの際、同じポジションに他の制限酵素による有効なマーカーが完成している場合があることから、その場合に値が入る。同じポジションに、自分以外ない場合は、"-" が入る。

値は、prefixとして付けられた "dup," に続いて、020_marker から引き継がれた set_enz_cnt が入る。

|name|value|
|:---:|:---:|
| set_enz_cnt|1/3-1/1|
|dup_pos|dup,1/3-1/1|


</p>
</dd>
</dl>


<dl>
<dt>
enzyme
</dt>
<dd>
<p><p>
CAPSマーカーの場合、解析された制限酵素名が入る。それ以外は "-" が入る。
</p>
</dd>
</dl>


<dl>
<dt>
g0_name, g1_name
</dt>
<dd>
<p><p>
現在比較しているグループ０とグループ１の名前。
</p>
</dd>
</dl>

<dl>
<dt>
g0_product_size, g1_product_size, diff_length, g0_digested_size, g1_digested_size, digested_gno, digested_ano
</dt>
<dd>
<p><p>

グループごとのプロダクトサイズとその差、capsマーカーの際は、制限酵素により消化された長さを "/" で区切って示す。digested_gno, digested_anoは、それぞれ消化される側のグループ番号、アリル番号を示すが、indelやsnpの場合どちらも0が入る。

|name|indel|caps|snp|
|:---:|:---:|:---:|:---:|
|g0_product_size|389|343|338|
|g1_product_size|361|343|338|
|diff_length|28|0|0|
|g0_digested_size|-|343|-|
|g1_digested_size|-|343/296/47|-|
|digested_gno|0|1|0|
|digested_ano|0|1|0|


</p>
</dd>
</dl>

[README](../README.md) | [Tutorial (Japanese doc)](doc/Tutorial.jp.md) | [Usage (Japanese doc)](doc/Usage.jp.md)
