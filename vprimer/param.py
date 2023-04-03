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
        hlp = "[required] vcf file (text or gz)"
        metavar = "vcf_file"
        parser.add_argument('--vcf', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # required (2) ------------------------------------
        # --ref
        hlp = "[required] reference fasta (txt or gz)"
        metavar = "ref_fasta"
        parser.add_argument('--ref', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # required (3) ------------------------------------
        # --target
        '''
        Format:
            range_str   ::= stt - end
            scope       ::= chrom_name | chrom_name:range_str
            target      ::= scope | target scope
            region_def  ::= target_name | target_name:scope
            regions     ::= region_def | regions region_def
        '''

        hlp = "scope := chrom_name | chrom_name:range_str"
        metavar = "scope"
        parser.add_argument('--target', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --pick_mode
        hlp = "mode for picking up markers: indel / caps / snp"
        metavar = "mode"
        parser.add_argument('--pick_mode', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # for preparation ---------------------------------
        # --show_samples
        hlp = "show sample names embedded in VCF files"
        parser.add_argument('--show_samples', action='store_true',
            help="{}".format(hlp))

        # --show_fasta
        hlp = "show fasta chromosomal information."
        parser.add_argument('--show_fasta', action='store_true',
            help="{}".format(hlp))


        # selection required ------------------------------
        # --auto_group 
        hlp = "analysis by auto grouping"
        metavar = "sample_name"
        parser.add_argument('--auto_group', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --sample_a
        hlp = "group A sample names"
        metavar = "sample_name"
        parser.add_argument('--a_sample', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --sample_b
        hlp = "group B sample names"
        metavar = "sample_name"
        parser.add_argument('--b_sample', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        #-------------------------------------------------------------

        # --indel_size
        hlp = "target indel size, min-max"
        metavar = 'min-max'
        parser.add_argument('--indel_size', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --product_size
        hlp = "PCR product size, min-max"
        metavar = 'min-max'
        parser.add_argument('--product_size', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        #---------------------------------------------------------
        # --enzyme
        hlp = "enzyme name list"
        metavar = "enzyme_name"
        parser.add_argument('--enzyme', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --enzyme_file
        hlp = "enzyme file list, separate by comma"
        metavar = "file"
        parser.add_argument('--enzyme_file', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --p3_normal
        hlp = "primer3 parameter file"
        metavar = "file"
        parser.add_argument('--p3_normal', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --p3_amplicon
        hlp = "primer3 parameter file for amplicon specific"
        metavar = "file"
        parser.add_argument('--p3_amplicon', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --amplicon_param
        hlp = "parameter for amplicon(SNP). Ftag,Rtag[,HrTM,DyTM]"
        metavar = "parameter"
        parser.add_argument('--amplicon_param', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # --bed_thal
        #parser.add_argument('--bed_thal', action='store',
        #    type=str, metavar='file',
        #    help="bed_thal file")

        # --bam_table
        hlp = "Correspondence table between sample names and bam files"
        metavar = "file"
        parser.add_argument('--bam_table', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --bed_bams
        #parser.add_argument('--bed_bams', action='store',
        #    type=str, metavar='bam',
        #    nargs='*',
        #    help="All specified bam are used for thin align judgment")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # --min_max_depth
        hlp = ""
        metavar = "min-max"
        parser.add_argument('--min_max_depth', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --out_dir
        hlp = "dir name for data output"
        metavar = "dir_name"
        parser.add_argument('--out_dir', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --thread
        hlp = "thread number: default 2"
        metavar = "num"
        parser.add_argument('--thread', action='store',
            type=int, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # ===================================================================
        # debug, etc.
        # --progress
        hlp = "progress start point, prepare/variant/marker/primer/formfail"
        metavar = "start_point"
        parser.add_argument('--progress', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --stop
        hlp = "progress stop point, prepare/variant/marker/primer"
        metavar = "stop_point"
        parser.add_argument('--stop', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --ini_file
        hlp = "ini file"
        metavar = "file"
        parser.add_argument('--ini_file', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        return parser

        # --use_joblib_threading
        hlp="use or not threading yes/no default yes"
        metavar = "yes/no"
        parser.add_argument('--use_joblib_threading', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # ===================================================================
        # in ini_file
        # --fragment_pad_len int
        hlp = ""
        metavar = "num"
        parser.add_argument('--fragment_pad_len', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --blast_distance int
        hlp = ""
        metavar = "num"
        parser.add_argument('--blast_distance', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --blast_word_size int
        hlp = ""
        metavar = "num"
        parser.add_argument('--blast_word_size', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --snp_marker_diff_len int
        hlp = ""
        metavar = "num"
        parser.add_argument('--snp_marker_diff_len', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))


        # --analyse_caps
        hlp = "print caps info"
        parser.add_argument('--analyse_caps', action='store_true',
            help="{}".format(hlp))


        # --ini_version
        hlp = "ini file version"
        metavar = "float"
        parser.add_argument('--ini_version', action='store',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # Full mode ===============================================
        # --regions
        hlp = "region_def ::= target_name | target_name:scope"
        metavar = "region_def"
        parser.add_argument('--regions', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --group_members
        hlp = "group_members full description"
        metavar = "what"
        parser.add_argument('--group_members', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        # --distinguish_groups
        hlp = "distinguish_groups full description"
        metavar = "what"
        parser.add_argument('--distinguish_groups', action='store',
            nargs='*',
            type=str, metavar="{}".format(metavar),
            help="{}".format(hlp))

        return parser

