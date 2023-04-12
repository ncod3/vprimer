[../README.md](../README.md)

# Usage

[Usage](USAGE.md)

# Detail description

This document explains how to design markers from a specified VCF file and Fasta file using vprimer.

First, specify the VCF file and Fasta file, and instruct vprimer on the analysis range of the Fasta and the type of marker to design. When vprimer is launched, it creates a refs directory under the current directory and prepares the necessary files for analysis.

The refs directory has the following structure:

[Description of the refs directory structure](REFSDIRECTORY.md)

The results will be written to the specified output directory (out_dir). The analysis proceeds in the following five steps, and the name of each step corresponds to the prefix of the file name that will be output in that step.

## 010_variant

[Detail output for 010_variant](010_VARIANT.md)

## 020_marker

[Detail output for 020_marker](020_MARKER.md)

## 030_primer

[Detail output for 030_primer](030_PRIMER.md)

## 040_formatF and 050_formatP

[Detail output for 040_formatF](040_050_FORMATF_P.md)



