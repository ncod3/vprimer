[Description](DESCRIPTION.md)

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
g0_vseq
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g1_vseq
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g0_gt
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g1_gt
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
dup_pos
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
enzyme
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g0_name
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g1_name
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g0_product_size
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g1_product_size
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
diff_length
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g0_digested_size
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
g1_digested_size
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
digested_gno
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
digested_ano
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>

[Description](DESCRIPTION.md)

