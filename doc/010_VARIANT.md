[Description](DESCRIPTION.md)

# 010_variant

<dl>
<dt>
chrom, pos
</dt>
<dd>
<p><p>
chromosomeと、position。
</p>

chrom | pos
:---:|:---:
chrom_01 | 62651

</dd>
</dl>

-----------------------------------

<dl>
<dt>
targ_grp, targ_ano
</dt>
<dd>
<p><p>
現在比較しているサンプルグループの名前と、使われているアリルの番号。(カンマ区切り)
</p>


|name| fixed two groups | auto (just two groups) | auto (three groups or more) |
|:---:|:---:|:---:|:---:|
| targ_grp |a,b|a,b|c,e|
| targ_ano |0,1|0,1|0,2|


２グループ固定の場合は、グループ名は 'a,b' が用いられる。オートグループの場合、比較するアリルが２つならば、グループ名は、'a,b' が用いられ、比較するアリルが３つ以上ならば、'c' からグループ名を付け始める ('c', 'd', 'e', ...) 。

</dd>
</dl>


<dl>
<dt>
vseq_gno_str
</dt>
<dd>
<p><p>
グループ順にカンマで区切られた、バリアントの配列。

name|indel|caps|snp|
:---:|:---:|:---:|:---:|
vseq_gno_str|ACCATTACTCGCTTACTCGCTTGTATGCTCCA,ACCA|A,T|G,C|

</p>
</dd>
</dl>


<dl>
<dt>
var_type, mk_type
</dt>
<dd>
<p><p>

var_typeはバリアントの種類。indelはアリル長の差がユーザが指定した範囲内のもの。snpはバリアント長が１でアリル長の差が無いもの。この間に属している、アリル長の差が、2 以上、最短indel長未満のものを、mind(mini-indel)と名付けている。

mk_typeは var_type が どのマーカーメソッドで取り扱われるかを示す。vprimerでは、mindは CAPSメソッドで扱われている。

ユーザは、pick_modeを指定し、対応する mk_type がメソッドとして用いられる。

|name||||
|:---:|:---:|:---:|:---:|
| var_type |indel|snp / mind |snp|
| mk_type |INDEL|CAPS|SNP|
|pick_mode| indel|caps|snp|


</dd>
</dl>


<dl>
<dt>
gts_segr_lens
</dt>
<dd>
<p><p>


|name|indel|caps|snp|
:---:|:---:|:---:|:---:|
gts_segr_lens |00/01,hohe_s1,32.32/32.4|00/01,hohe_s1,1.1/1.1|00/01,hohe_s1,1.1/1.1

</p>
</dd>
</dl>


<dl>
<dt>
auto_grp0, auto_grp1
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
vseq_ano_str
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
set_n
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


<dl>
<dt>
len_g0g1_dif_long
</dt>
<dd>
<p><p>
word
</p>
</dd>
</dl>


[Description](DESCRIPTION.md)

