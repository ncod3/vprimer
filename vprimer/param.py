# -*- coding: utf-8 -*-
# https://qiita.com/podhmo/items/1eb7e72a47b713c9cda2
# https://qiita.com/kzkadc/items/e4fc7bc9c003de1eb6d0
# description
# https://qiita.com/mimitaro/items/a845b45df35b39a59c95

# we don't use short option for one character
# [For short options (options only one character long),
#  the option and its value can be concatenated:]

import sys
#import os
import errno
import time

# global configuration
import vprimer.glv as glv

import argparse

from vprimer.__init__ import __version__
from vprimer.logging_config import LogConf


class Param(object):

    def __init__(self):

        pass

    def open_log(self):

        global log
        log = LogConf.open_log(__name__)


    def get_args(self):

        parser = self.get_options()

        # self.p is dict
        if len(sys.argv) == 1:
            self.p = vars(parser.parse_args(['-h']))
        else:
            # to dict
            self.p = vars(parser.parse_args())

        return self


    def get_options(self):

        parser = argparse.ArgumentParser(
            description='vprimer version {}'.format(__version__),
            formatter_class=argparse.RawTextHelpFormatter)
        parser.usage = ('vprimer ...\n')

        parser.add_argument('--version', action='version',
            version='$(prog)s {}'.format(__version__))


        # required (1) ------------------------------------
        # --vcf
        parser.add_argument('--vcf', action='store',
            type=str, metavar='vcf_file',
            help="[required] vcf file (text or gz)")

        # required (2) ------------------------------------
        # --ref
        parser.add_argument('--ref', action='store',
            type=str, metavar='ref_fasta',
            help="[required] reference fasta (txt or gz)")

        # required (3) group definition -------------------
        # --no_group 
        parser.add_argument('--no_group', action='store',
            type=str, metavar='sample',   # default="",
            nargs='*',
            help="analysis by no grouping")

        # --sample_a
        parser.add_argument('--a_sample', action='store',
            type=str, metavar='sample',   # default="",
            nargs='*',
            help="group A sample names")

        # --sample_b
        parser.add_argument('--b_sample', action='store',
            type=str, metavar='sample',   # default="",
            nargs='*',
            help="group B sample names")
        # -------------------------------------------------

        # --target
        '''
        Format:
            range_str   ::= stt - end
            scope       ::= chrom_name | chrom_name:range_str
            target      ::= scope | target scope
            region_def  ::= target_name | target_name:scope
            regions     ::= region_def | regions region_def
        '''
        parser.add_argument('--target', action='store',
            type=str, metavar='scope',
            nargs='*',
            help="scope := chrom_name | chrom_name:range_str")

        #-------------------------------------------------------------
        # --pick_mode
        parser.add_argument('--pick_mode', action='store',
            type=str, metavar='mode',
            nargs='*',
            # indel, caps, snp
            help="mode for picking up markers: indel / caps / snp")

        # --indel_size
        parser.add_argument('--indel_size', action='store',
            type=str, metavar='min-max',
            help="target indel size, min-max")

        # --product_size
        parser.add_argument('--product_size', action='store',
            type=str, metavar='min-max',
            help="PCR product size, min-max")

        #---------------------------------------------------------
        # --out_dir
        parser.add_argument('--out_dir', action='store',
            type=str, metavar='dir',
            help="dir name for data output")

        # --thread
        parser.add_argument('--thread', action='store',
            type=int, metavar='int',
            help="thread number: default 2")

        # --ini_file
        parser.add_argument('--ini_file', action='store',
            type=str, metavar='file',
            help="ini file [optional]")

        # --enzyme
        parser.add_argument('--enzyme', action='store',
            type=str, metavar='enzyme_name',
            nargs='*',
            help="enzyme name list")

        # --enzyme_file
        parser.add_argument('--enzyme_file', action='store',
            type=str, metavar='file',
            nargs='*',
            help="enzyme file list, separate by comma")

        # --p3_normal
        parser.add_argument('--p3_normal', action='store',
            type=str, metavar='file',
            help="primer3 parameter file")

        # --p3_amplicon
        parser.add_argument('--p3_amplicon', action='store',
            type=str, metavar='file',
            help="primer3 parameter file for amplicon specific")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # --bed_thal
        parser.add_argument('--bed_thal', action='store',
            type=str, metavar='file',
            help="bed_thal file")

        # --bam_table
        parser.add_argument('--bam_table', action='store',
            type=str, metavar='file',
            help="Correspondence table between sample names and bam files")

        # --bed_bams
        parser.add_argument('--bed_bams', action='store',
            type=str, metavar='bam',
            nargs='*',
            help="All specified bam are used for thin align judgment")
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


        # --min_max_depth
        parser.add_argument('--min_max_depth', action='store',
            type=str, metavar='min-max',
            help="")

        # --show_samples
        parser.add_argument('--show_samples', action='store_true',
            #type=str, metavar='',
            help="show sample names embedded in VCF files")

        # --show_fasta
        parser.add_argument('--show_fasta', action='store_true',
            #type=str, metavar='',
            help="show fasta chromosomal information.")

        # ===================================================================
        # debug, etc.
        # --progress
        parser.add_argument('--progress', action='store',
            type=str, metavar='',
            help="progress start point, prepare/variant/marker/primer/formfail")

        # --stop
        parser.add_argument('--stop', action='store',
            type=str, metavar='',
            help="progress stop point, prepare/variant/marker/primer")

        # --use_joblib_threading
        parser.add_argument('--use_joblib_threading', action='store',
            type=str, metavar='yes/no',
            help="use or not threading yes/no default yes")

        return parser

        # ===================================================================
        # in ini_file
        # --fragment_pad_len int
        parser.add_argument('--fragment_pad_len', action='store',
            type=int, metavar='int',
            help="")

        # --blast_distance int
        parser.add_argument('--blast_distance', action='store',
            type=str, metavar='int',
            help="")

        # --blast_word_size int
        parser.add_argument('--blast_word_size', action='store',
            type=str, metavar='int',
            help="")

        # --snp_marker_diff_len int
        parser.add_argument('--snp_marker_diff_len', action='store',
            type=str, metavar='int',
            help="")


        # --analyse_caps
        parser.add_argument('--analyse_caps', action='store_true',
            help="print caps info")


        # --ini_version
        parser.add_argument('--ini_version', action='store',
            type=str, metavar='float',
            help="ini file version")

        # Full mode ===============================================
        # --regions
        parser.add_argument('--regions', action='store',
            type=str, metavar='region_def',
            nargs='*',
            help="region_def ::= target_name | target_name:scope")

        # --group_members
        parser.add_argument('--group_members', action='store',
            type=str, metavar='what',
            nargs='*',
            help="group_members full description")

        # --distinguish_groups
        parser.add_argument('--distinguish_groups', action='store',
            type=str, metavar='what',
            nargs='*',
            help="distinguish_groups full description")


        return parser

