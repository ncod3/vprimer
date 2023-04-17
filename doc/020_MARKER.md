[Description](DESCRIPTION.md)

# 020_marker

<dl>
<dt>
marker_id
</dt>
<dd>
<p><p>
word
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
word
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


[Description](DESCRIPTION.md)

