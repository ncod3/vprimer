# -*- coding: utf-8 -*-

import sys
#import os
import errno
import re
import time
import numpy as np
from pathlib import Path

import pprint

# global variants
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
from vprimer.conf_distin import ConfDistinG
from vprimer.conf_ref_fasta import ConfRefFasta
from vprimer.conf_vcf_file import ConfVcfFile
from vprimer.conf_curr_setting import ConfCurrSet
from vprimer.conf_enzyme import ConfEnzyme
from vprimer.conf_bed_file import ConfBedFile
from vprimer.conf_p3_params import ConfP3Params
from vprimer.conf_amplicon import ConfAmplicon

# class Conf(ConfBase, ConfDistinG, ConfBedFile, 
#     ConfCurrSet, ConfEnzyme):
#     ''' Split class and join with multiple inheritance
#     '''
#     pass

class ConfBase(object):

    def __init__(self):

        # ----------------------------------------------------------
        # A dictionary that associates a value with a variable name 
        # for all parameters
        # param.py _get_options()
        self.conf_dict = {
            # from param.py _get_options()

            # required (1), (2)
            'vcf':          {'dtype': 'str',    'default': ''},
            'ref':          {'dtype': 'str',    'default': ''},

            # required (3) group definition
            'auto_group':     {'dtype': 'str',    'default': ''},
            'a_sample':     {'dtype': 'str',    'default': ''},
            'b_sample':     {'dtype': 'str',    'default': ''},

            # Easy mode
            'target':       {'dtype': 'str',    'default': ''},

            # Full mode
            'regions':      {'dtype': 'str',    'default': ''},
            # The default for group_member is group_members_vcf_str
            # read from vcf.
            # Do not initialize the key for safety as we will update it later.
            #                {'dtype': 'str',    'default': ''},
            'group_members':
                            {'dtype': 'str',},
            'distinguish_groups':
                            {'dtype': 'str',    'default': ''},

            #
            'indel_size':   {'dtype': 'str',    'default': '20-200'},
            'product_size': {'dtype': 'str',    'default': '200-500'},
            'pick_mode':    {'dtype': 'str',    'default': glv.MODE_INDEL},

            #
            'out_dir':      {'dtype': 'str',    'default': 'out_vprimer'},
            'ini_file':     {'dtype': 'str',    'default': ''},
            'ini_version':  {'dtype': 'str',    'default': ''},
            'thread':       {'dtype': 'int',    'default': '2'},

            # 2023.03.31 force no
            # 2023.05.01 returned to yes
            #'use_joblib_threading': # param
            #                {'dtype': 'str',    'default': 'yes'},
            #                {'dtype': 'str',    'default': 'no'},

            # list enzyme_file refs/enzyme_names.txt
            'enzyme_file':  {'dtype': 'str',    'default': ''},

            # list enzyme
            'enzyme':       {'dtype': 'str',    'default': ''},

            # normal        refs/p3_params.txt
            'p3_normal':    {'dtype': 'str',    'default': ''},

            # for amplicon  refs/p3_amplicon.txt
            'p3_amplicon':  {'dtype': 'str',    'default': ''},

            # for amplicon Ftag,Rtag[,HrTM,DyTM]")
            'amplicon_param':  {'dtype': 'str',    'default': ''},

            # filter for snp marker
            'snp_filter':   {'dtype': 'str',   'default':
                                        'gcrange:50-55,interval:1M'},

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # bed_thal
            'bam_table':
                            {'dtype': 'str',    'default': ''},
            'bed_thal':
                            {'dtype': 'str',    'default': ''},
            # 不要
            #'bed_bams':
            #                {'dtype': 'str',    'default': ''},
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            # min_max_depth
            'min_max_depth':
                            {'dtype': 'str',    'default': "8-300"},

            # ---------------------------------------------------------------
            'fragment_pad_len':
                            {'dtype': 'int',    'default': '500'},

            'blast_distance':
                            {'dtype': 'int',    'default': '10000'},
            # blast_word_size will be set later after p3 PRIMER_MIN_SIZE
            # is set.
            'blast_word_size': # PRIMER_MIN_SIZE
                            {'dtype': 'int',    'default': '23'},

            # for amplicon, when you want to widen the size difference
            'snp_marker_diff_len':
                            {'dtype': 'int',    'default': '0'},

            #
            'show_samples': {'dtype': 'bool',   'default': 'False'},
            'show_fasta':   {'dtype': 'bool',   'default': 'False'},
            'progress':     {'dtype': 'str',    'default': 'all'},
            'stop':         {'dtype': 'str',    'default': 'no'},

            # for all variant
            'homo_only':    {'dtype': 'bool',   'default': 'False'},

            # debug
            'analyse_caps': {'dtype': 'bool',   'default': 'False'},
        }

        # cwd, log --------------------------------------------
        self.cwd = glv.cwd
        self.log = LogConf()

        # refseq: reference on memory
        self.refseq = dict()

        # fasta: It will be set in main later
        self.ref_fasta_chrom_dict_list = list()
        self.ref_fasta_chrom_list = list()
        self.ref_fasta_chrom_region_list = list()

        # vcf: sample_nickname -------------------------------------
        self.vcf_sample_nickname_list = list()
        self.vcf_sample_basename_list = list()
        self.vcf_sample_fullname_list = list()

        self.vcf_sample_nickname_dict = dict()
        self.vcf_sample_basename_dict = dict()
        self.vcf_sample_fullname_dict = dict()

        self.group_members_vcf_str = ""

        # sample cnt for ndarray
        self.vcf_sample_cnt = 0

        # enzyme ----------------------------------------------
        # list of enzymes used throughout the system
        self.enzyme_name_list = list()
        # list of enzyme files used throughout the system
        self.enzyme_files_list = list()
        # If you specify the enzyme name directly, it will take precedence 
        self.user_enzyme_list = list()
        self.user_enzyme_files_list = list()

        # region group member string --------------------------
        # select string by priority, next make dict or list variables
        self.region_name_list = list()
        self.group_name_list = list()

        self.regions_dict = dict()
        self.group_members_dict = dict()
        self.distinguish_groups_list = list()
        # for each reg
        self.all_proc_cnt = 0
        # for iterate group_dict and region
        self.gdct_reg_list = list()

        # key : bed_thal_path
        self.bed_thal_dict = dict()

        # primer3 params --------------------------------------
        self.p3_key_normal = { \
            'p3_key': glv.p3_normal,
            'PRIMER_MIN_SIZE': 23,
            'PRIMER_OPT_SIZE': 25,
            'PRIMER_MAX_SIZE': 27,
            'PRIMER_MIN_GC': 40,
            'PRIMER_OPT_GC': 50,
            'PRIMER_MAX_GC': 60,
            'PRIMER_MIN_TM': 57.0,
            'PRIMER_OPT_TM': 60.0,
            'PRIMER_MAX_TM': 63.0,
            'PRIMER_MAX_POLY_X': 4,
            'PRIMER_PAIR_MAX_DIFF_TM': 4,
        }

        # primer3 params for amplicon
        self.p3_key_amplicon = {
            'p3_key': glv.p3_amplicon,
            'PRIMER_MIN_SIZE': 20,
            'PRIMER_OPT_SIZE': 23,
            'PRIMER_MAX_SIZE': 26,
            'PRIMER_MIN_GC': 40,
            'PRIMER_OPT_GC': 50,
            'PRIMER_MAX_GC': 60,
            'PRIMER_MIN_TM': 58.0,
            'PRIMER_MAX_TM': 60.0,
            'PRIMER_MAX_POLY_X': 3,
            'PRIMER_PAIR_MAX_DIFF_TM': 0.5,
            'PRIMER_MAX_SELF_ANY': 8,
            'PRIMER_MAX_SELF_END': 3,
            'PRIMER_GC_CLAMP': 1,
        }


    # --- before log file open, from glv.init
    def collect_param_ini(self, param, ini):
        ''' aggregate all parameters into one dictionary
        '''

        self.param = param
        self.ini = ini

        for vname in self.conf_dict:

            param_value = self.get_param_value(vname, param)

            ini_value = None

            if param.p['ini_file'] is not None:
                 # ini
                ini_value = self.get_ini_value(vname, ini)

            # If no ini file is specified, 
            # self.conf_dict[vname]['ini'] is None
            self.conf_dict[vname]['param'] = param_value
            self.conf_dict[vname]['ini'] = ini_value


    def get_param_value(self, vname, param):
        ''' get data from parameter
        param handles values with the correct data type
        '''

        ret = None

        # a_sample="DRS_013.all.rd DRS_084.all.rd,DRS_099.all.rd ref"
        # b_sample="DRS_025.all.rd, DRS_061.all.rd DRS_101.all.rd"

        # {'a_sample': ['DRS_013.all.rd',
        #   'DRS_084.all.rd,DRS_099.all.rd', 'ref'],
        # 'b_sample': ['DRS_025.all.rd,', 'DRS_061.all.rd',
        #   'DRS_101.all.rd'],

        if vname in param.p:

            val = param.p[vname]

            if type(val) == list:
                # 'DRS_084.all.rd,DRS_099.all.rd'
                # 'DRS_025.all.rd,'
                #print("{}={}".format(vname, val))

                mod_list = list()
                for item in val:
                    sep_list = item.split(",")
                    for sep in sep_list:
                        if sep != "":
                            mod_list.append(sep)

                #ret = ','.join(val)
                ret = ','.join(mod_list)
                #print("\t{}={}".format(vname, ret))

            else:
                ret = val

        return ret


    def get_ini_value(self, vname, ini):
        ''' get data from ini file
        ini handles values as strings
        '''

        ret = None

        if vname in ini.ini['vprimer']:

            val = ini.ini['vprimer'][vname]
            if type(val) == list:
                ret = ','.join(val)
            else:
                ret = self.cast_val(val, self.conf_dict[vname]['dtype'])

        return ret


    def cast_val(self, value, dtype):
        ''' for ini file data, casting data to fit data type
        ''' 

        #print("_cast_val: value={}, dtype={}".format(value, dtype))
        #print("type(value={}".format(type(value)))
        #print("type(dtype={}".format(type(dtype)))

        if dtype == 'int':
            #print("int")
            return int(value)

        elif dtype == 'float':
            #print("float")
            return float(value)

        elif dtype == 'bool':

            # for param
            if type(value) == bool:
                return value
            else:
                # form ini
                if value == "True":
                    return True
                elif value == "False":
                    return False
                else:
                    return None

        elif dtype == 'str':
            #print("str")
            return str(value)

        else:
            #print("else")
            return str(value)


    def make_out_dir_tree(self):
        '''
        '''

        # if already made at conf. _path are pathlib object
        dirs = [
            self.out_dir_path,
            self.log_dir_path,
            self.out_bak_dir_path
        ]

        for dir in dirs:
            # dir is pathlib object
            if dir.is_dir():
                # prelog
                utl.prelog("exist dir {}.".format(dir), __name__)
            else:
                utl.prelog("not exist dir {}.".format(dir), __name__)
                utl.makedirs(dir)


    def out_dir_logging_start(self):
        '''
        '''

        # user defined path
        self.user_out_dir = self.selected_value('out_dir')
        # absolute path
        self.out_dir_path = Path(self.user_out_dir).resolve()
        # log_dir
        self.log_dir_path = self.out_dir_path / glv.log_dir_name
        # bak_dir
        self.out_bak_dir_path = self.out_dir_path / glv.bak_dir_name

        # _path are pathlib object
        self.make_out_dir_tree()

        # for conf
        global log
        log = self.log.logging_start(__name__,
            self.out_dir_path, self.log_dir_path)

       # for utl
        utl.open_log()


    # --- after log file open
    def choice_variables(self):
        ''' called from main: prepare(self), glv.conf.choice_variables()
        '''

        # thread ==============================================
        self.thread = self.selected_value('thread')
        log.info("thread={}".format(self.thread))

        #self.use_joblib_threading = \
        #    self.selected_value('use_joblib_threading')

        #if not self.use_joblib_threading in ['yes', 'no']:
        #    er_m = "use_joblib_threading Choose from Yes or No."
        #    log.error("{} exit.".format(er_m))
        #    log.error("use_joblib_threading={}".format(
        #        self.use_joblib_threading))
        #    sys.exit(1)

        # thread adjust
        self.parallel_ok, \
        self.parallel_full_thread, \
        self.parallel_blast_cnt, \
        self.blast_num_threads \
            = self.thread_adjusting()

        # print param and ini variables
        self.print_param_ini()


        # ref_dir =============================================
        self.refs_dir_path = Path(glv.refs_dir_name).resolve()
        # make ref_dir, self.refs_dir_path is pathlib object
        utl.makedirs(self.refs_dir_path)


        # bed_dir =============================================
        self.bed_dir_path = self.refs_dir_path / glv.bed_dir_name
        # make into ref_dir
        utl.makedirs(self.bed_dir_path)


        # out_dir =============================================
        self.user_out_dir = self.selected_value('out_dir')
        self.out_dir_path = Path(self.user_out_dir).resolve()

        # timestamp_file
        self.bak_timestamp_path = self.out_bak_dir_path / glv.bak_timestamp


        # ref =================================================
        # glv.conf.user_ref_path: user specified fasta path
        self.user_ref_fasta = self.selected_value('ref')
        self.user_ref_path = Path(self.user_ref_fasta).resolve()

        # glv.conf.ref_bgzip_path for official system fasta path
        self.ref_bgzip_path = self.refs_dir_path / "{}{}".format(
            self.user_ref_path.name, glv.BGZIP_fasta_gz)

        # chrom name summary
        self.ref_bgzip_chrom_txt_path = self.refs_dir_path / "{}{}".format(
            self.ref_bgzip_path.name, glv.chrom_txt_ext)

        # blast for ref
        self.blastdb_title = self.ref_bgzip_path.stem
        self.blastdb_path = self.refs_dir_path / "{}{}".format(
            self.blastdb_title, glv.blastdb_ext)


        # vcf =================================================
        # glv.conf.user_vcf_path: user specified vcf path
        self.user_vcf = self.selected_value('vcf')
        self.user_vcf_path = Path(self.user_vcf).resolve()

        # glv.conf.vcf_gt_path for official system vcf path
        self.vcf_gt_path = self.refs_dir_path / "{}{}".format(
            self.user_vcf_path.name, glv.GTonly_vcf_ext)

        # sample name file
        self.vcf_sample_name_txt_path = \
            self.refs_dir_path / "{}{}".format(
                self.vcf_gt_path.name, glv.vcf_sample_name_ext)

        # Correspondence table between samples and bam
        self.vcf_sample_bam_table_path = \
            self.refs_dir_path / "{}{}".format(
                self.vcf_gt_path.name, glv.vcf_sample_bam_ext)

        # self.user_out_dir, self.user_ref_fasta, self.user_vcf
        #if self.user_out_dir == "" or \
        #    self.user_ref_fasta == "" or \
        #    self.user_vcf == "":
        if self.user_ref_fasta == "" or \
            self.user_vcf == "":

            er_m = "vcf={} and ref={} ".format(
                self.user_vcf,
                self.user_ref_fasta)
            er_m += "are all required. exit."
            log.error(er_m)
            sys.exit(1)


        # pick_mode ===========================================
        self.pick_mode = self.selected_value('pick_mode')
        # convert , to +: indel,caps => indel+caps
        self.pick_mode = re.sub(r",", "+", self.pick_mode)

        # check pick_mode
        if '+' in self.pick_mode and glv.MODE_SNP in self.pick_mode:
            er_m = "Only pick_mode snp must be used alone, exit."
            log.error(er_m)
            sys.exit(1)

        # it can use as, self.pick_mode == glv.MODE_SNP
        for pm in self.pick_mode.split('+'):
            if pm not in glv.pick_mode_list:
                er_m = "Pick mode ({}) must be ".format(self.pick_mode)
                er_m += "one of these {}.".format(glv.pick_mode_list)
                log.error(er_m)
                sys.exit(1)


        # GROUP MODE == self.is_auto_group ======================
        self.auto_group = self.selected_value('auto_group')
        # if auto_group is not specified.
        if self.auto_group == "":
            self.is_auto_group = False
        else:
            self.is_auto_group = True

        self.a_sample = self.selected_value('a_sample')
        self.b_sample = self.selected_value('b_sample')
        self.target = self.selected_value('target')


        # indel_size ==========================================
        self.indel_size = self.selected_value('indel_size')
        self.min_indel_len, self.max_indel_len = \
            [int(i) for i in self.indel_size.split('-')]


        # product_size ========================================
        self.product_size = self.selected_value('product_size')
        self.min_product_size, self.max_product_size = \
            [int(i) for i in self.product_size.split('-')]


        # bed_thal ==============================================

        # bam_tabelと、bed_tha

        # user specified bam_table ------------------------------
        self.user_bam_table = self.selected_value('bam_table')
        self.user_bam_table_path = Path(self.user_bam_table).resolve()

        # user specified bed_thal -------------------------------
        self.user_bed_thal = self.selected_value('bed_thal')
        self.user_bed_thal_path = Path(self.user_bed_thal).resolve()

        # user specified bed_bams -------------------------------
        #self.user_bed_bams_str = self.selected_value('bed_bams')
        if self.user_bam_table != "" and self.user_bed_thal != "":
            er_m = "bam_table and bed_thal cannot be specified together."
            log.error(er_m)
            sys.exit(1)

        # depth_check ----------------------
        self.depth_mode = glv.depth_no_check   # NoCheck

        # (1) self.user_bam_table
        if self.user_bam_table != "":
            self.depth_mode = glv.depth_bam_table

        # (2) self.user_bed_thal
        elif self.user_bed_thal != "":
            self.depth_mode = glv.depth_bed_thal

        # (3) self.user_bed_bams_str
        #elif self.user_bed_bams_str != "":
        #    self.depth_mode = glv.depth_bed_bams

        # thin_depth --------------------------------------------
        self.min_max_depth = self.selected_value('min_max_depth')
        self.min_depth, self.max_depth = \
            [int(i) for i in self.min_max_depth.split('-')]


        # enzyme ================================================

        self.user_enzyme_name_list = list()
        self.enzyme_name_list = list()
        #
        self.user_enzyme_path_list = list()
        self.enzyme_file_path = glv.NonePath

        # user specified two items
        # TaqI,BamHI
        self.user_enzyme_str = self.selected_value('enzyme')
        self.user_enzyme_files_str = self.selected_value('enzyme_file')

        # デフォルトのシステムファイル名
        self.enzyme_file_path = \
            self.refs_dir_path / glv.caps_enzyme_name_file

        # If an enzyme is specified by the user, add to list
        if self.user_enzyme_str != "":
            self.user_enzyme_name_list = self.user_enzyme_str.split(',')
            log.info("user specified enzyme={}".format(
                ", ".join(self.user_enzyme_name_list)))

        if self.user_enzyme_files_str != "":
            # ユーザ指定のファイル
            for ufile in self.user_enzyme_files_str.split(','):
                self.user_enzyme_path_list.append(Path(ufile).resolve())


        # p3_param ============================================
        self.primer3_header = dict()

        # self.p3_mode   : 'p3_normal', 'p3_amplicon'
        if self.pick_mode == glv.MODE_SNP:
            self.p3_mode = glv.p3_amplicon
        else:
            self.p3_mode = glv.p3_normal    # default

        # p3_normal --------------------------------------------
        # user specified file
        self.user_p3_normal_file = self.selected_value('p3_normal')
        self.user_p3_normal_path = glv.NonePath
        if self.user_p3_normal_file != "":
            self.user_p3_normal_path = \
                Path(self.user_p3_normal_file).resolve()

        # system unprepared
        self.p3_normal_path = \
            self.refs_dir_path / glv.p3_normal_file

        # p3_amplicon ------------------------------------------
        # user specified file
        self.user_p3_amplicon_file = self.selected_value('p3_amplicon')
        self.user_p3_amplicon_path = glv.NonePath
        if self.user_p3_amplicon_file != "":
            self.user_p3_amplicon_path = \
                Path(self.user_p3_amplicon_file).resolve()

        # system unprepared
        self.p3_amplicon_path = \
            self.refs_dir_path / glv.p3_amplicon_file


        # amplicon_param =======================================
        self.amplicon_param = self.selected_value('amplicon_param')
        if self.pick_mode != glv.MODE_SNP and self.amplicon_param != "":
            er_m = "{} can only be specified when ".format("amplicon_param")
            er_m += "pick_mode is snp."
            log.error(er_m)
            sys.exit(1)

        self.amplicon_forward_tag = ""
        self.amplicon_reverse_tag = ""
        self.hairpin_tm = 0.0
        self.dimer_tm = 0.0

        # check and separate
        if self.amplicon_param != "":
            self.amplicon_forward_tag, self.amplicon_reverse_tag, \
            self.hairpin_tm, self.dimer_tm = \
                self.check_amplicon_param(self.amplicon_param)

        # snp_filter ===========================================
        # sub_command default
        # --snp_filter gcrange:50-55 interval:1M
        self.snp_filter_gcrange = ""
        self.snp_filter_gc_min = 0.00
        self.snp_filter_gc_max = 0.00
        self.snp_filter_interval = 0

        self.snp_filter = self.selected_value('snp_filter')
        #print("self.snp_filter={}".format(self.snp_filter))

        if self.pick_mode == glv.MODE_SNP:
            self.snp_filter_gcrange, \
            self.snp_filter_gc_min, \
            self.snp_filter_gc_max, \
            self.snp_filter_interval = \
                self.check_snp_filter_sub_command()

        else:
            self.snp_filter = ""

        #print(self.snp_filter_gcrange)
        #print(type(self.snp_filter_gcrange))

        #print(self.snp_filter_gc_min)
        #print(type(self.snp_filter_gc_min))
        #print(self.snp_filter_gc_max)
        #print(type(self.snp_filter_gc_max))

        #print(self.snp_filter_interval)
        #print(type(self.snp_filter_interval))

        #sys.exit(1)

        # out_curr_setting ======================================
        self.curr_setting_file = glv.current_setting_ini
        self.curr_setting_path = \
            self.out_dir_path / self.curr_setting_file

        # show_samples ==========================================
        self.show_samples = self.selected_value('show_samples')

        # show_fasta ============================================
        self.show_fasta = self.selected_value('show_fasta')

        # start stop ============================================
        self.progress = self.selected_value('progress')
        self.stop = self.selected_value('stop')

        # homo_only =============================================
        self.homo_only = self.selected_value('homo_only')

        # for caps debug  =======================================
        self.analyse_caps = self.selected_value('analyse_caps')

        # -----------------------------------------------------

        # ini_version -----------------------------------------
        self.ini_version_user = self.selected_value('ini_version')
        self.ini_version_system = glv.ini_version

        # Full mode, three variables --------------------------
        self.regions_str = self.init_regions_str()
        self.group_members_str = self.init_group_members_str()
        self.distinguish_groups_str = self.init_distinguish_groups_str()

        # fragment_pad_len ------------------------------------
        self.fragment_pad_len = self.selected_value('fragment_pad_len')

        # blast -----------------------------------------------
        self.blast_distance = self.selected_value('blast_distance')
        # not set now
        self.blast_word_size = 0

        # for amplicon snp marker -----------------------------
        self.snp_marker_diff_len = self.selected_value('snp_marker_diff_len')


    def prepare_refs_filename(self):
        '''
        refsディレクトリの下に配置される、システム関連のファイルの
        扱い方とその値
        '''

        refs_files_dict = {

            'ref': {    # リファレンスfasta
                'type'  : 'required',       # ユーザからの指定が必須
                'user'  : self.user_ref_path,
                'sys'   : self.ref_bgzip_path,
            },

            'vcf': {    # vcf
                'type'  : 'required',       # ユーザからの指定が必須
                'user'  : self.user_vcf_path,
                'sys'   : self.vcf_gt_path,
            },

            'p3_normal': {      # primer3 config file 'normal'
                'type'  : 'unprepared',     # 準備されないので、出力
                'user'  : self.user_p3_normal_path,
                'sys'   : self.p3_normal_path,
            },

            'p3_amplicon': {    # primer3 config file 'amplicon'
                'type'  : 'unprepared',     # 準備されないので、出力
                'user'  : self.user_p3_amplicon_path,
                'sys'   : self.p3_amplicon_path,
            },

            'enzyme': { # enzyme name file
                'type'  : 'unprepared',     # 準備されないので、出力
                'user'  : self.user_enzyme_path_list,
                'sys'   : self.enzyme_file_path,
            },


            # bam 関連は ３つ。
            #   bam_table
            #   bams_bed
            #   bed_thal
            # refs/bed

            'bam_table': {    # 
                'type'  : 'unprepared',     # 準備されないので、出力
                #'user'  : self.user_thin_align_bams_path_list,
                #'sys'   : self.thin_align_bams_path_list,
            },
    
            'bed_bams': {    # 
                'type'  : 'user_specified', # ユーザ指定が必須
                #'user'  : self.user_thin_align_bams_path_list,
                #'sys'   : self.thin_align_bams_path_list,
            },
            'bed_thal': {
                'type'  : 'user_specified', # ユーザ指定が必須
                #'user'  : self.user_thin_align_table_path,
                #'sys'   : self.thin_align_table_path,
            },
        }

        return refs_files_dict


    def prepare_refs_dir(self):
        '''
        '''

        for refs_type in self.refs_files_dict.keys():
            # ref
            if refs_type == 'ref':
                self.prepare_ref(
                    self.refs_files_dict[refs_type]['user'],
                    self.refs_files_dict[refs_type]['sys'])

                if self.show_fasta == True:

                    self.touch_bak_timestamp()
                    log.info("only show_fasta mode, exit.")
                    log.info("program finished {}\n".format(
                        utl.elapse_epoch()))
                    sys.exit(1)


            # vcf
            if refs_type == 'vcf':

                self.prepare_vcf(
                    self.refs_files_dict[refs_type]['user'],
                    self.refs_files_dict[refs_type]['sys'])

                if self.show_samples == True:

                    self.touch_bak_timestamp()
                    log.info("only show_samples mode, exit.")
                    log.info("program finished {}\n".format(
                        utl.elapse_epoch()))
                    sys.exit(1)

            # p3_norm
            if refs_type == glv.p3_normal or refs_type == glv.p3_amplicon:

                p3_key = self.p3_key_normal
                if refs_type == glv.p3_amplicon:
                    p3_key = self.p3_key_amplicon

                # 上書きできるのか？
                # self.primer3_header[glv.p3_normal|glv.p3_amplicon]
                self.primer3_header[refs_type] = \
                    self.prepare_p3(
                        refs_type,
                        p3_key,
                        self.refs_files_dict[refs_type]['user'],
                        self.refs_files_dict[refs_type]['sys'])

                log.info("primer3_header:\n\n'{}'\n{}\n".format(
                    refs_type,
                    pprint.pformat(self.primer3_header[refs_type])))

            # enzyme
            if refs_type == 'enzyme':

                # 1) enzyme name from file 
                enzyme_name_list = \
                    self.prepare_enzyme(
                        self.refs_files_dict[refs_type]['user'],
                        self.refs_files_dict[refs_type]['sys'])

                # 2) add user enzyme
                enzyme_name_list += self.user_enzyme_name_list
                
                # reduce contents of the enzyme_name_list
                self.enzyme_name_list = \
                    self.check_enzyme_name_list(enzyme_name_list)

            # bed_thal
            if refs_type == 'bed_thal':
                pass
                #self.prepare_bam_bed()


        #print("end _prepare_refs_dir")


    def setup_variables(self):
        ''' called from main: prepare(self), glv.conf.setup_variables()
        '''

        log.info("setup_variables, START.")
        
        # ini_file
        self.user_ini_path = glv.NonePath
        if self.user_ini_file is not None:
            self.user_ini_path = Path(self.user_ini_file).resolve()

        # Prepare filenames to be placed in refs_dir
        self.refs_files_dict = self.prepare_refs_filename()

        # Prepare contents of refs_dir
        self.prepare_refs_dir()

        # setup bed
        #self.setup_all_combination_bed()

        # Satisfy three structural variables
        #   1) regions_dict
        #   2) group_members_dict
        #   3) distinguish_groups_list

        # 1) construct regions dictionary from regions_str
        self.regions_str, \
        self.regions_dict, \
        self.region_name_list \
            = self.set_regions_dict(self.regions_str)

        self.set_selected_value('regions', self.regions_str)
        log.info("chosen self.regions_str={}".format(self.regions_str))

        # 2) construct group_members_dict from group_members_str
        self.group_members_dict, \
        self.group_name_list \
            = self.set_group_members_dict(self.group_members_str)

        self.set_selected_value('group_members',
            self.group_members_str)
        log.info("selected self.group_members_str={}".format(
            self.group_members_str))


        # 3.1) distinguish_groups_str --------------------------------------
        #log.debug("org self.distinguish_groups_str={}".format(
        #    self.distinguish_groups_str))

        #   Easy mode lacks the region name, so make up for it here.
        if self.is_easy_mode():
            region_names_str = "+".join(self.region_name_list)
            self.distinguish_groups_str = re.sub(
                #r"<EASY_MODE>", region_names_str,
                r"{}".format(glv.EASY_MODE), region_names_str,
                self.distinguish_groups_str)

        # 3.2) make distinguish_groups_list from distinguish_groups_str ....
        self.distinguish_groups_str, \
        self.distinguish_groups_list = \
            self.set_distinguish_groups_list(
                self.distinguish_groups_str)

        self.set_selected_value('distinguish_groups',
            self.distinguish_groups_str)
        log.info("chosen self.distinguish_groups_str={}".format(
            self.distinguish_groups_str))

        # 4.2) blast_word_size = PRIMER_MAX_SIZE
        self.blast_word_size = \
            self.primer3_header['p3_normal']['PRIMER_MIN_SIZE']

        # 6) progress, stop
        if not self.check_progress_stop():
            if self.progress != "all" and self.stop != "no":
                er_m = "The progress or stop settings are incorrect."
                log.error("{} exit.".format(er_m))
                log.error("progress={}, stop={}".format(
                    self.progress, self.stop))
                log.error("{}".format(
                    ", ".join(glv.outlist.outf_prefix.keys())))
                sys.exit(1)


    def check_progress_stop(self):
        '''
        '''

        ret = True

        if self.progress == "all" and self.stop == "no":
            ret = True

        elif self.progress not in glv.outlist.outf_prefix.keys():
            ret = False

        elif self.stop not in glv.outlist.outf_prefix.keys():
            ret = False

        return ret


    def thread_adjusting(self):
        ''' in Parallel, if there are 10 threads blast cmd will use at least
            2 cores so par 1 parallel.
            main python always use 1,
            parallel use 1 thread, blast use 2 threads
        '''

        parallel_ok = True

        parallel_full_thread = 0
        parallel_blast_cnt = 0
        blast_num_threads = 0

        if self.thread < 6:  # or self.use_joblib_threading != "yes":
            parallel_ok = False
            mes = "Parallel execution mode is turned off "
            mes += "when the number of threads used is "
            mes += "less than or equal to 5. now={}."
            log.info(mes.format(self.thread))

        if parallel_ok == True:

            # unit is 4+1=5
            parallel_base = self.thread
            parallel_full_thread = parallel_base

            # blast = 4
            parallel_blast_cnt = int(parallel_base / 5)
            blast_num_threads = 4

        else:
            # 6 = 5
            full_thread = self.thread - 1
            parallel_full_thread = full_thread
            blast_num_threads = full_thread

        return parallel_ok, \
                parallel_full_thread, \
                parallel_blast_cnt, \
                blast_num_threads


    def selected_value(self, vname):
        ''' a_sample, b_sample, target are only param, not in ini

        '''

        selected_value = ""

        # The default for group_member is group_members_vcf_str
        # read from vcf.
        # Do not initialize the key for safety as we will update it later.
        if vname == 'group_members':
            return selected_value

        # If neither param nor ini has a key, use the default value
        if self.conf_dict[vname]['param'] is None and \
            self.conf_dict[vname]['ini'] is None:
            selected_value = self.conf_dict[vname]['default']

        elif self.conf_dict[vname]['param'] is not None:
            #print("cv 2")
            selected_value = self.conf_dict[vname]['param']

        elif self.conf_dict[vname]['ini'] is not None:
            #print("cv 3")
            selected_value = self.conf_dict[vname]['ini']

        elif self.conf_dict[vname]['default'] is not None:
            #print("cv 4")
            selected_value = self.conf_dict[vname]['default']

        else:
            utl.prelog("not found value of key {}.".format(vname), __name__)
            sys.exit(1)

        #print("vname={}".format(vname))
        #print("dtype={}".format(self.conf_dict[vname]['dtype']))
        #print(selected_value)
        #print(type(selected_value))

        # cast by dtype
        selected_value = self.cast_val(
            selected_value, self.conf_dict[vname]['dtype'])

        #print(type(selected_value))

        # selected_value
        self.set_selected_value(vname, selected_value)

        return selected_value


    def set_selected_value(self, vname, selected_value):

        # Assuming the chosen key does not exist
        self.conf_dict[vname]['chosen'] = selected_value


    def is_chrom_name(self, chrom_name):
        '''
        '''
        ret = False
        #print("_is_chrom_name, {}, {}".format(
        #    chrom_name, self.ref_fasta_chrom_list))

        # 20210922
        if chrom_name in self.ref_fasta_chrom_list:
            ret = True
        #print("{}".format(ret))
        return ret


    def is_region_name(self, region_name):
        '''
        '''
        ret = False
        #print("_is_region_name, {}, {}".format(
        #    region_name, self.region_name_list))
        if region_name in self.region_name_list:
            ret = True
        #print("{}".format(ret))
        return ret


    def is_group_name(self, group_name):
        '''
        '''
        ret = False
        #print("_is_group_name, {}, {}".format(
        #    group_name, self.group_name_list))
        if group_name in self.group_name_list:
            ret = True
        #print("{}".format(ret))
        return ret


    def is_valid_int_range(self, range_str):
        '''
        '''
        ret = True

        if "-" not in range_str:
            ret = False
        else:
            min_size, max_size = range_str.split("-")

            if not min_size.isdecimal() or \
                not max_size.isdecimal():
                ret = False
            elif int(min_size) > int(max_size):
                ret = False

        return ret


    def is_valid_chrom_range(self, range_str):

        ret = True

        #print("_is_valid_chrom_range, range_str={}".format(range_str))
        chrom_name, rg_str = range_str.split(':')
        #print("_is_valid_chrom_range, chrom_name={}, rg_str={}".format(
        #    chrom_name, rg_str))

        min_pos, max_pos = [int(i) for i in rg_str.split('-')]
        #print("_is_valid_chrom_range, min_pos={}, max_pos={}".format(
        #    min_pos, max_pos))

        chrom_info_list = self.get_chrom_info(chrom_name)
        start = chrom_info_list[0]
        end = chrom_info_list[1]
        length =chrom_info_list[2]
        region_def = chrom_info_list[3]

        #print("_is_valid_chrom_range, _get_chrom_info={}, {}, {}, {}".format(
        #    region_def, start, end, length))

        if min_pos < start or end < max_pos:
            ret = False
        #print("_is_valid_chrom_range, ret={}".format(ret))

        return ret


    def get_chrom_info(self, chrom_name):
        '''
        '''

        # glv.conf.ref_fasta_chrom_dict_list
        start = 0
        end = 0
        length = 0

        for d in self.ref_fasta_chrom_dict_list:
            #end': 30583384, 'length': 30583384, 'start': 1
            if chrom_name == d.get('chrom'):
                start = d.get('start')
                end = d.get('end')
                length = d.get('length')

        region_def = chrom_name

        if start is not None:
            region_def = "{}:{}-{}".format(region_def, start, end)

        #pprint.pprint(glv.conf.ref_fasta_chrom_dict_list)
        #print("{}, {}".format(region_def, length))

        return [start, end, length, region_def]


    def is_easy_mode(self):
        ''' On the command line, determine if we are currently in easy mode.
        A value is set for either a_sample and b_sample or auto_group.
        '''

        easy_mode = False

        a_sample = False
        b_sample = False

        if self.is_auto_group:
            easy_mode = True

        else:

            if utl.is_Not_NoneAndNull(self.conf_dict['a_sample']['param']):
                a_sample = True

            if utl.is_Not_NoneAndNull(self.conf_dict['b_sample']['param']):
                b_sample = True

            if a_sample == True or b_sample == True:
                easy_mode = True

        return easy_mode
    

    def print_param_ini(self):
        ''' for debug
        '''
        # parameter and ini_file variables

        #utl.prelog
        log.info("\n======== param.p ====================")
        log.info("self.param.p=\n\n{}\n".format(pprint.pformat(self.param.p)))

        log.info("\n======== ini.ini['vprimer'] =========")

        if self.param.p['ini_file'] is not None:
            log.info("\nini_file={}\n\n{}\n".format(
                self.param.p['ini_file'],
                pprint.pformat(dict(self.ini.ini['vprimer']))))
        else:
            log.info("ini_file not specified.")
        log.info("\n=====================================\n")


    def touch_bak_timestamp(self):

        # file name
        self.bak_timestamp_path = self.out_bak_dir_path / glv.bak_timestamp
        # touch
        self.bak_timestamp_path.touch(exist_ok=True)


class Conf(ConfBase, ConfDistinG, ConfRefFasta, ConfVcfFile,
    ConfCurrSet, ConfEnzyme, ConfBedFile, ConfP3Params, ConfAmplicon):
    ''' Split class and join with multiple inheritance
    '''
    pass

