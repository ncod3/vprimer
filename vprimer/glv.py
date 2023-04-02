# -*- coding: utf-8 -*-

import sys
#import os
import errno
import time
import datetime
import string
from pathlib import Path
import re

# using class
from vprimer.param import Param
from vprimer.ini_file import IniFile
from vprimer.conf import Conf
from vprimer.outlist import OutList

##########################################
easy_region =           'e_reg'
# log file name
refs_dir_name =         'refs'
bed_dir_name =          'bed'
log_dir_name =          'logs'
bak_dir_name =          'bak'
log_file_name =         'vprimer_log.txt'

BGZIP_fasta_gz =        '_BGZIP.gz'
GTonly_vcf_ext =        '_GTonly.vcf.gz'

bak_timestamp =         'bak_timestamp.txt'
ini_vprimer_file =      'ini_vprimer.txt'
p3_normal_file =        'p3_normal.txt'
p3_amplicon_file =      'p3_amplicon.txt'
caps_enzyme_name_file = 'caps_enzyme_name_list.txt'
current_setting_ini =   'current_setting_ini.txt'

slink_prefix =          'slink_'
cp_prefix =             'cp.'

fai_ext =               '.fai'
chrom_txt_ext =         '.chrom.txt'
blastdb_ext =           '.blastdb'
pickle_ext =            '.pickle'

need_update =           'need'
noneed_update =         'no_need'

vcf_sample_name_ext =   '_sample_name.txt'
vcf_sample_bam_ext =    '_sample_bam_table.txt'

original_file_ext =     '.original'

bed_dict_common =       'common'

bam_slink_ext =         '_slink.bam'
bed_mid_txt =           '_depth_'

#####

#bed_thal_prefix =       'bed_thal_'
#bed_tmp_ext =           '.bed_tmp'

#bed_thal_tmp_ext =      '.bed_thal_sort'
#bed_thal_merge_ext =    '.bed_thal_merge'

#-----------------------------------------
# glv.conf.p3_mode
p3_normal =             'p3_normal'
p3_amplicon =           'p3_amplicon'

#-----------------------------------------
# amplicon_param default value
amplicon_forward_tag =  'ACACTGACGACATGGTTCTACA'
amplicon_reverse_tag =  'TACGGTAGCAGAGACTTGGTCT'
hairpin_tm =            '45'
dimer_tm =              '40'

#-----------------------------------------
# depth_check_mode
depth_no_check =        'depth_no_check'

depth_bam_table =       'depth_bam_table'
depth_bed_thal =        'depth_bed_thal'
depth_bed_bams =        'depth_bed_bams'

##########################################
# NonePath for pathlib resolve()
# if ga.resolve() == None:
NonePath = type('NonePath', (), {'resolve': lambda: None})

# for ref_fasta_chrom_dict_list
genome_total_len   = "genome_total_len"

##########################################
# bed_thal
##########################################

# now_stat
bed_now_nop        = "now_nop"

bed_now_zero       = "Z"
bed_now_thin       = "thin"
bed_now_valid      = "valid"
bed_now_thick      = "THICK"

# stat_changed
bed_stat_nop       = "bed_stat_nop"

bed_stat_init      = "bed_stat_init"
bed_stat_continue  = "bed_stat_continue"
bed_stat_changed   = "bed_stat_changed"

# bam_bed
min_max_ext        = ".mMin_xMax"
bam_bed_ext        = ".bb.bed"
bam_bed_tmp_ext    = ".bed_tmp"

# bed_thal
bed_thal_prefix    = "bed_thal_"
bed_thal_ext       = ".bta.bed"
bed_thal_tmp_ext   = ".bed_thal_sort"
bed_thal_merge_ext = ".bed_thal_merge"

na_group_names     = "GRP_NA"


##########################################
AUTO_GROUP  = "auto_group"  # group name for "auto_group"
ALL_MEMBER  = "all"         # indicate all vcf sample member

# group name list ["a", "b", ... "z"]
GROUP_NAME = list(string.ascii_lowercase)

EASY_MODE   = "<EASY_MODE>" # a word used for replacement in easy mode

##########################################
# pick_mode
MODE_INDEL  = 'indel'   # indel
MODE_CAPS   = 'caps'    # for caps
MODE_SNP    = 'snp'     # snp for amplicon
MODE_OOR    = 'oor'     # Out of Range

# check at conf_disting.py:_rectify_distinguish_groups_str
pick_mode_list = [
    MODE_INDEL,
    MODE_CAPS,
    MODE_SNP,
    MODE_OOR
]

##########################################
# var_type (variation type)
# set in allele_select.py:_get_variant_type
OutOfRange  = "oor"
# Code for indel allele, includes substitutions of unequal length
INDEL       = MODE_INDEL
# Code for single nucleotide variant allele
SNP         = MODE_SNP
# Code for a multi nucleotide variant allele
MNV         = "mnv"
# mini_indel 1 =< diff_len min_indel_len
MIND        = "mind"

# AlleleSelect.is_var_type_in_pick_mode

##########################################
# mk_type marker type
MK_NOTYPE = "NOTYPE"

MK_INDEL = "INDEL"
MK_CAPS = "CAPS"
MK_SNP = "SNP"

# long_smpl_side
SAME_LENGTH = -1

ini_section = "[vprimer]"
ini_version = "20210201"

##########################################
# for region
GENOME_ALL = 'all'

##########################################
# allele status
AL_HOMO     = 'homo'
AL_HETERO   = 'hetero'

# analysis SKIP as variant
SKIP_DONT_SKIP      = -1
SKIP_SAME_HOMO      = 1
SKIP_SAME_HETERO    = 2
SKIP_EXIST_None     = 3
SKIP_DIFF_INGROUP   = 10

# formtxt COMMENT
COMMENT_nop = '-'
COMMENT_dup = 'dup'

# segregation_pattern
segr_ptn_NOP                        = 'nop'
# ./.
segr_ptn_NOT_EXIST_ALLELE           = 'not_exist_allele'
# AA,AA BB,BB CC,CC DD,DD
segr_ptn_SAME_HOMO                  = 'same_homo'
# AB,AB AC,AC AD,AD BC,BC BD,BD CD,CD
segr_ptn_SAME_HETERO                = 'same_hetero'
# AA,BB AA,CC AA,DD BB,CC BB,DD CC,DD
# BB,AA CC,AA DD,AA CC,BB DD,BB DD,CC
segr_ptn_HOMO_HOMO                  = 'hoho_1'
# AA,AB AA,AC AA,AD BB,AB BB,BC BB,BD CC,AC CC,BC CC,CD DD,AD
# DD,BD DD,CD
# AB,AA AC,AA AD,AA AB,BB BC,BB BD,BB AC,CC BC,CC CD,CC AD,DD
# BD,DD CD,DD
segr_ptn_HOMO_HETERO_SHARE          = 'hohe_s1'
# AA,BC AA,BD AA,CD BB,AC BB,AD BB,CD CC,AB CC,AD CC,BD DD,AB
# DD,AC DD,BC
# BC,AA BD,AA CD,AA AC,BB AD,BB CD,BB AB,CC AD,CC BD,CC AB,DD
# AC,DD BC,DD
segr_ptn_HOMO_HETERO_NOT_SHARE      = 'hohe_n2'
# AB,AC AB,AD AB,BC AB,BD AC,AD AC,BC AC,CD AD,BD AD,CD BC,BD
# BC,CD BD,CD
segr_ptn_HETERO_HETERO_SHARE        = 'hehe_s3'
# AB,CD AC,BD AD,BC
segr_ptn_HETERO_HETERO_NOT_SHARE    = 'hehe_n4'

# 使用する制限酵素の最長のrecognition site length
AROUND_SEQ_LEN = 20


def init(prog_name):

    global program_name
    program_name = prog_name

    global now_epochtime, now_datetime_str, now_datetime_form
    now_epochtime, now_datetime_str, now_datetime_form = get_now_time()

    # pathlib object
    global cwd
    cwd = Path.cwd()

    # local variable
    param = Param()
    ini = IniFile()

    global conf
    conf = Conf()

    global outlist
    outlist = OutList()

    #--------------------------------
    # get command line parameter
    param = param.get_args()
    # set user ini file to conf
    conf.user_ini_file = param.p['ini_file']

    # if specified, read ini file
    if conf.user_ini_file is not None:
        ini.read_ini_file(conf.user_ini_file)

    # collect variables from param, ini, default
    conf.collect_param_ini(param, ini)

    # start logging
    conf.out_dir_logging_start()

    param.open_log()

    conf.open_log_reffasta()
    conf.open_log_vcffile()
    conf.open_log_distin()
    conf.open_log_p3_params()
    conf.open_log_enzyme()
    conf.open_log_bedfile()
    conf.open_log_currset()

    outlist.open_log()


def get_now_time():

    now_datetime = datetime.datetime.now()      # 2021-02-09 10:56:57.209040
    # glv.now_epochtime
    now_epochtime = now_datetime.timestamp()    # 1612835817.20904

    now_dt_ms = now_datetime.strftime("%f")     # 209040
    now_dt_ms2 = now_dt_ms[0:2]                 # 20
    now_dt_hr = now_datetime.strftime("%Y%m%d%H%M%S")   # 20210209102610

    # glv.now_datetime_str
    now_datetime_str = "{}{}".format(
        now_dt_hr, now_dt_ms2)                          # 2021020910261020
    # glv.now_datetime_form
    now_datetime_form = now_datetime.strftime("%Y-%m-%d %H:%M:%S")

    now_datetime_form = re.sub(
        r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\..*$',
        r'\1_\2\3_\4\5_\6',
        str(now_datetime))

    #1612835817.20904       for elapsed timestamp 
    #2023012716574459       for file timestamp
    #2023_0120_1256_50      for start timestamp

    return now_epochtime, now_datetime_str, now_datetime_form

