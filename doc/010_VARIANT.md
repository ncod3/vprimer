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


<dl>
<dt>
targ_grp
</dt>
<dd>
<p><p>
ここで比較しているサンプルグループに付けられた名前(カンマ区切り)
</p>


|name| fixed two groups | auto (just two groups) | auto (three groups or more) |
|:---:|:---:|:---:|:---:|
| targ_grp |a,b|a,b|c,e|


２グループ固定の場合は、グループ名は 'a,b' が用いられる。genotype で自動的に分けられるオートグループの場合、比較するアリルが２つならば、グループ名は 'a,b' が用いられ、比較するアリルが３つ以上ならば、'c' からグループ名を付け始める ('c', 'd', 'e', ...) 。

</dd>
</dl>


<dl>
<dt>
vseq_gno_str
</dt>
<dd>
<p><p>
グループ順にカンマで区切った、アリルの配列。

name|indel|caps|snp|
:---:|:---:|:---:|:---:|
vseq_gno_str|ACCATTACTCGCTTACTCGCTTGTATGCTCCA,ACCA|A,T|G,C|

</p>
</dd>
</dl>



<dl>
<dt>
gts_segr_lens
</dt>
<dd>
<p><p>
比較する２種類の genotype が、どのようなアリルの組み合わせに分解されるかのパターンを表す。

|name|example|
|:---:|:---:|
|gts_segr_lens|00/01,hohe_s1,1.1/1.1|

カンマで区切られた３つのフィールドからなり、それぞれ以下の意味がある。

|field|content|
|:---:|:---:|
|genotypes|00/01|
|segregation pattern|hohe_s1|
|lengths|1.1/1.1|

genotypesは、グループ順のgenotype。segregation patternは、グループ間で比較する異なるアリル組み合わせのパターンとその数。lengthsは、各グループのアリルの長さ。

segregation pattern の symbplの詳細は以下の通り。

|symbol|discription|example genotype|num|diff allele compare pattern|
|:---:|:---:|:---:|:---:|:---:|
|hoho_1 |homo & homo | 00/11|   1 |  0/1
|hohe_s1 |homo & hetero share|00/01 |  1 |  0/1
|hohe_n2 |homo & hetero not share|00/12 |  2 |  0/1, 0/2
|hehe_s3 |hetero & hetero share|01/02 |  3 |  0/2, 1/0, 1/2
|hehe_n4 |hetero & hetero not share|01/23 |  4 |  0/2, 0/3, 1/2, 1/3


このように全ての異なるアリルの組み合わせごとにマーカーとしての評価を行い、Pass したものがファイルに書き出される。

</p>
</dd>
</dl>



<dl>
<dt>
targ_ano
</dt>
<dd>
<p><p>
現在比較しているアリル番号の組み合わせをグループ順にカンマ区切り。
</p>


|name| fixed two groups | auto (just two groups) | auto (three groups or more) |
|:---:|:---:|:---:|:---:|
| targ_ano |0,1|0,1|0,2|


</dd>
</dl>


<dl>
<dt>
set_n
</dt>
<dd>
<p><p>


異なるアリルの組み合わせの全体数と、自分の順番。

|name| value |
|:---:|:---:|
| set_n |1/3|


indelが範囲内ではない場合など、マーカー評価で対象とならなかったものは飛ばされている。

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
auto_grp0, auto_grp1
</dt>
<dd>
<p><p>
オートグループの際に、genotypeにより比較グループとして分けられたサンプル群。固定グループの場合は "-" が入る。
</p>

|name| value |
|:---:|:---:|
| auto_grop0 |MP2_013,MP2_015,MP2_018|
| auto_grop1 |MP2_012,MP2_014,MP2_020|

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


|name| indel |caps|snp|
|:---:|:---:|:---:|:---:|
| vseq_ano_str |CAAAA,CAAAAAAAAAAAAAAAAAAAAAAAAAA,CAAAAAAAAAAAAAAAAAA|A,T|G,A|

</dd>
</dl>


<dl>
<dt>
len_g0g1_dif_long
</dt>
<dd>
<p><p>
グループ順に、アリルの長さと、比較対象アリルとの長さの差。

|name| indel |CAPS|
|:---:|:---:|:---:|
| len_g0g1_dif_long |32,4,28,0|1,1,0,0|

カンマ区切りの各フィールドの意味は、以下である。

|32,4,28,0|1,1,0,0|
|:---:|:---:|
|グループ０のアリル長=32|グループ０のアリル長=1|
|グループ１のアリル長=4|グループ１のアリル長=1|
|アリル長差=28|アリル長差=0|
|長い方のグループ=0|長い方のグループ=0 (同じ時は0)|

</p>
</dd>
</dl>


[Description](DESCRIPTION.md)

