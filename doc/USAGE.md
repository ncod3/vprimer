[Description](DESCRIPTION.md)

## Usage

### ** required
<dl>
<dt>
--ref ref_file
</dt>
<dd>
<p><p>
Reference fasta.
</p>

</dd>
</dl>

<dl>
<dt>
--vcf vcf_file
</dt>
<dd>
<p><p>
VCF file.
</p>

</dd>
</dl>

<dl>
<dt>
--target all | chr | chr:stt-end | chr:stt-[,…​]
</dt>
<dd>
<p><p>
Comma- or Space-separated list of regions.
</p>
</dd>
</dl>

<dl>
<dt>
--pick_mode mode
</dt>
<dd>
<p><p>
Type of marker to pick up. [ indel | caps | snp ]
</p>

</dd>
</dl>

### ** for preparation

<dl>
<dt>
--show_fasta
</dt>
<dd>
<p><p>
Prepare fasta, display fasta information and exit.
</p>

</dd>
</dl>

<dl>
<dt>
--show_samples
</dt>
<dd>
<p><p>
Prepare VCF, display VCF information and exit.
</p>

</dd>
</dl>

### ** selection required

<dl>
<dt>
--a_sample [sample [sample ...]]<br>
--b_sample [sample [sample ...]]<br>
 or <br>
--auto_group [sample [sample ...]]
</dt>
<dd>
<p><p>
If you already have two groups to compare, list the samples in a_sample and b_sample.
When analyzing by genotype-based auto group, list the samples in auto_group.
</p>

</dd>
</dl>

### ** optional

<dl>
<dt>
--indel_size min-max
</dt>
<dd>
<p><p>
The range of InDel size.
</p>

</dd>
</dl>

<dl>
<dt>
--product_size min-max
</dt>
<dd>
<p><p>
The range of product size for designing primer.
</p>

</dd>
</dl>

<dl>
<dt>
--enzyme enzyme_name
</dt>
<dd>
<p><p>
Restriction enzyme names used in CAPS marker.
</p>

</dd>
</dl>

<dl>
<dt>
--enzyme_file file
</dt>
<dd>
<p><p>
File that listing restriction enzyme names for use in CAPS marker.
</p>

</dd>
</dl>

<dl>
<dt>
--p3_normal file
</dt>
<dd>
<p><p>
File that listing parameters to set Primer3 for InDel or CAPS marker.
</p>

</dd>
</dl>

<dl>
<dt>
--p3_amplicon file
</dt>
<dd>
<p><p>
File that listing parameters to set Primer3 for SNP marker.
</p>

</dd>
</dl>

<dl>
<dt>
--amplicon_param parameter
</dt>
<dd>
<p><p>
Parameters for designing SNP markers.
</p>

</dd>
</dl>

<dl>
<dt>
--bam_table file
</dt>
<dd>
<p><p>
File that that associates bam file names with VCF sample names.
</p>

</dd>
</dl>

<dl>
<dt>
--out_dir dir_name
</dt>
<dd>
<p><p>
Directory name for outputting results.
</p>

</dd>
</dl>

<dl>
<dt>
--thread num
</dt>
<dd>
<p><p>
Number of CPUs to use.
</p>

</dd>
</dl>
	

