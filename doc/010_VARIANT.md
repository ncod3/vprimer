[Description](DESCRIPTION.md)

# 010_variant

<dl>
<dt>
chrom, pos
</dt>
<dd>
<p><p>
現在注目している chromosome と position 。
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
ここで比較しているサンプルグループに付けられた名前と、対応するアリルの番号。(カンマ区切り)
</p>


|name| fixed two groups | auto (just two groups) | auto (three groups or more) |
|:---:|:---:|:---:|:---:|
| targ_grp |a,b|a,b|c,e|
| targ_ano |0,1|0,1|0,2|


２グループ固定の場合は、グループ名は 'a,b' が用いられる。genotype で自動的に分けられるオートグループの場合、比較するアリルが２つならば、グループ名は 'a,b' が用いられ、比較するアリルが３つ以上ならば、'c' からグループ名を付け始める ('c', 'd', 'e', ...) 。

</dd>
</dl>










<dl>
<dt>
targ_grp, targ_ano
</dt>
<dd>
<p><p>
比較しているサンプルグループに付けられた名前と、比較しているアリルの番号。(カンマ区切り)
</p>


|name| fixed two groups | auto (just two groups) | auto (three groups or more) |
|:---:|:---:|:---:|:---:|
| targ_grp |a,b|a,b|c,e|
| targ_ano |0,1|0,1|0,2|


２グループ固定の場合は、グループ名は 'a,b' が用いられる。genotype で自動的に分けられるオートグループの場合、比較するアリルが２つならば、グループ名は 'a,b' が用いられ、比較するアリルが３つ以上ならば、'c' からグループ名を付け始める ('c', 'd', 'e', ...) 。

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

var_typeはバリアントの種類。indelはアリル長の差がユーザが指定した範囲内のもの。snpはバリアント長が１でアリル長の差が無いもの。indelとsnpの間すなわち、アリル長の差が、2 以上、最短indel長未満のものを、mind(mini-indel)と名付けている。

mk_typeは var_type が どのマーカーメソッドで取り扱われるかを示す。vprimerでは、mindは CAPSメソッドで扱われている。

ユーザは pick_mode を指定し、対応する mk_type がマーカーメソッドとして用いられる。

|name||||
|:---:|:---:|:---:|:---:|
| var_type |indel|snp / mind |snp|
| mk_type |INDEL|CAPS|SNP|
|(pick_mode)| indel|caps|snp|


</dd>
</dl>


<dl>
<dt>
gts_segr_lens
</dt>
<dd>
<p><p>
比較する２つのバリアントが、どのようなアリルの組み合わせに分解されるかのパターンを示す。

name|value
:---:|:---:
gts_segr_lens|00/01,hohe_s1,1.1/1.1

カンマで区切られた３つのフィールドからなり、

|field|content|
|:---:|:---:|
|genotypes|00/01|
|segregation pattern|hohe_s1|
|lengths|1.1/1.1|

genotypesは、各グループのgenotype。segregation patternは、異なるアリルの組み合わせのパータンと数、lengthsは、各グループのアリルの長さ。

|symbol|gts|num|pattern|
|:---:|:---:|:---:|:---:|
|hoho_1 | 00/11|   1 |  0:1
|hohe_s1 |00/01 |  1 |  0:1
|hohe_n2 |00/12 |  2 |  0:1, 0:2
|hehe_s3 |01/02 |  3 |  0:2, 1:0, 1:2
|hehe_n4 |01/23 |  4 |  0:2, 0:3, 1:2, 1:3


実際にパターンごとにマーカーとしての評価を行い、マーカーとしての資格のあるものがファイルに書き出される。

</p>
</dd>
</dl>


<dl>
<dt>
auto_grp0, auto_grp1
</dt>
<dd>
<p><p>
オートグループの際に、genotypeにより比較グループとして分けられたサンプル群。
</p>
</dd>
</dl>


<dl>
<dt>
vseq_ano_str
</dt>
<dd>
<p><p>
アリル番号順に、アリルの配列をカンマ区切りで接続した文字列
</p>
</dd>
</dl>


<dl>
<dt>
set_n
</dt>
<dd>
<p><p>
segregation patternから、マーカー評価をした際の、自分の順番/全体の順番。マーカー評価で対象とならなかったものは覗かれている（indelが範囲内ではない場合）。
</p>
</dd>
</dl>


<dl>
<dt>
len_g0g1_dif_long
</dt>
<dd>
<p><p>
グループごとに、アリルの長さと、比較対象アリルとの長さの差。


1,1,0,0


</p>
</dd>
</dl>


[Description](DESCRIPTION.md)

