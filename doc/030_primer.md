[Description](DESCRIPTION.md)

# 030_primer

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

marker_id, set_enz_cnt, marker_info, vseq_lens_ano_str, g0_seq_target_len, g0_seq_target, g1_seq_target_len, g1_seq_target, seq_template_ref_len, seq_template_ref_abs_pos, seq_template_ref_rel_pos, SEQUENCE_TARGET, SEQUENCE_TEMPLATE

</dt>
<dd>
<p><p>
(020_markerより引き継ぎ)
</p>
</dd>
</dl>


<dl>
<dt>
in_target
</dt>
<dd>
<p><p>

プライマー設計の準備段階で、TEMPLATE_SEQUENCE 上にあるグループ内各サンプルのバリアントの領域は、除外エリアとして登録するが、TARGET_SEQUENCE 上のバリアントは設計作業には影響しない。そのため、TARGET_SEQUENCE上のバリアントの情報を、この列に書き入れる。

サンプル名に続けて()の中に、+で繋がれた２つの数値が並ぶ。左側の数値はバリアントのポジションからの相対的位置を示す。マイナスの値であれば、5'側にあり、プラスの値であれば、3'側にある。右の数値はバリアントの長さである。複数ある場合はカンマ区切りで繋がれる。

|name|value|
|:---:|:---:|
|in_target |MP2_012(32+1),MP2_013(38+1)


</p>
</dd>
</dl>


<dl>
<dt>
try_cnt
</dt>
<dd>
<p><p>

ここまでにプライマー設計を繰り返した数。

</p>
</dd>
</dl>


<dl>
<dt>
complete
</dt>
<dd>
<p><p>
Primer3によるプライマー設計が成功した時、すなわち Primer3 から「PRIMER_PAIR_NUM_RETURNED=1」が戻ってきた場合、complete には 1 が入っています。「PRIMER_PAIR_NUM_RETURNED=0」が返って来た場合、-20 が入っています。
</p>
</dd>
</dl>


<dl>
<dt>
blast_check
</dt>
<dd>
<p><p>

作成されたプライマーの blast_check の結果が入ります。blast_check をパスすると blast_check には、"-" が入り、complete に 1 が入り、プライマー作成が成功したことを示します。

blast_check が失敗すると、blast_check には、以下のように他の染色体で見つかった region と他に見つかった回数が()の中に記述されます。complete には、-1 が入り、再度プライマー作成を試みることになります。

|name||
|:---:|:---:|
|blast_check|chrom_02:1831993-1832348(355)|

</p>
</dd>
</dl>


<dl>
<dt>
PRIMER_PAIR_0_PRODUCT_SIZE
</dt>
<dd>
<p><p>

作成されたプライマーペアが reference から切り出すプロダクトのサイズ。

</p>
</dd>
</dl>


<dl>
<dt>
product_gc_contents
</dt>
<dd>
<p><p>
切り出されたプロダクトのGC contents
</p>
</dd>
</dl>


<dl>
<dt>
PRIMER_LEFT_0, left_primer_id, PRIMER_LEFT_0_SEQUENCE, PRIMER_RIGHT_0, right_primer_id, PRIMER_RIGHT_0_SEQUENCE
</dt>
<dd>
<p><p>

作成されたプライマーの情報です。

PRIMER_LEFT_0, PRIMER_RIGHT_0 は、TEMPLATE_SEQUENCE 上におけるプライマー開始点の相対アドレスと長さを示します。


|name|value|
|:---:|:---:|
|PRIMER_LEFT_0|121,25|
|left_primer_id|chrom_01:19263-19287:plus|
|PRIMER_LEFT_0_SEQUENCE|TAAACCCCTAAACCCCTAAACCCTA|
|||
|PRIMER_RIGHT_0| 463,25 |
|right_primer_id| chrom_01:19581-19605:minus |
|PRIMER_RIGHT_0_SEQUENCE|AGGGTTTAGGGTTTAGGGTTTTAGG|

</p>
</dd>
</dl>


<dl>
<dt>
left_primer_id
</dt>
<dd>
<p><p>
左側プライマーのid
</p>
</dd>
</dl>


<dl>
<dt>
PRIMER_LEFT_0_SEQUENCE
</dt>
<dd>
<p><p>
左側のプライマーの配列
</p>
</dd>
</dl>



<dl>
<dt>
right_primer_id
</dt>
<dd>
<p><p>
右側プライマーのid
</p>
</dd>
</dl>


<dl>
<dt>
PRIMER_RIGHT_0_SEQUENCE
</dt>
<dd>
<p><p>
右側プライマーの配列
</p>
</dd>
</dl>


<dl>
<dt>
SEQUENCE_EXCLUDED_REGION
</dt>
<dd>
<p><p>
除外エリア TEMPLATE_SEQUENCE 上の開始相対posと、長さ
（詳細)
</p>
</dd>
</dl>


[Description](DESCRIPTION.md)

