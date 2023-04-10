# -*- coding: utf-8 -*-

import sys
#import os
from pathlib import Path
import errno
import time
import pprint

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf


class OutList(object):

    def __init__(self):

        self.outf_prefix = {
            'prepare'       : {'no':  0,  'fn': ''},
            'variant'       : {'no': 10,  'fn': '010_variant'},
            'marker'        : {'no': 20,  'fn': '020_marker'},
            'primer'        : {'no': 30,  'fn': '030_primer'},
            'formfail'      : {'no': 40,  'fn': '040_formatF'},
            'formpass'      : {'no': 50,  'fn': '050_formatP'},
        }

        # stopと、progressと。
        # ある地点の、現在地番号。
        #   現在地番号が、   <progress(ここから実行)  飛ばす
        #                   ==progress(ここから実行)  実行する
        #                    >progress(ここから実行)  実行する
        #   現在地番号が、   <stop(ここが終わったら止まる)  実行する 
        #                   ==stop(ここが終わったら止まる)  実行する
        #                    >stop(ここが終わったら止まる)  止まる
        # 
        # のprogressのstatusと stopのstatusを返して、
        #               prepare variant marker  primer  formfail  formpass
        # progress(all) x         |->     |->     |->     |->       |-> 
        # stop(no)      x       ->|     ->|     ->|     ->|       ->|

    def open_log(self):

        global log
        log = LogConf.open_log(__name__)


    def prepare_distin_grp_files(self):

        for distin_grp_dict in glv.conf.distinguish_groups_list:

            # distin_grp_dict を更新する
            for key, no_fn in self.outf_prefix.items():

                if key == 'prepare':
                    continue

                # キーに対応するヘッダ情報 variant, marker, primer...
                distin_grp_dict[key] = dict()
                distin_grp_dict[key]['fn'] = dict()

                hdr_text, hdr_list, hdr_dict = self.make_header(key)

                # キーに対応させてヘッダを登録する
                distin_grp_dict[key]['hdr_text'] = hdr_text
                distin_grp_dict[key]['hdr_list'] = hdr_list
                distin_grp_dict[key]['hdr_dict'] = hdr_dict

                # 個々のリージョンにファイル名登録
                for reg in distin_grp_dict['regions']:


                    out_file_path, base_name = self.make_distin_fname(
                        no_fn['fn'],
                        distin_grp_dict[0],             # g0
                        distin_grp_dict[1],             # g1
                        reg,                            # region
                        distin_grp_dict['pick_mode'])   # pick_mode

                    distin_grp_dict[key]['fn'][reg] = dict()
                    distin_grp_dict[key]['fn'][reg]['out_path'] = \
                        out_file_path
                    distin_grp_dict[key]['fn'][reg]['base_nam'] = \
                        base_name

        # make argment list
        glv.conf.gdct_reg_list = list()
        glv.conf.all_proc_cnt = 0

        # use 
        # for gdct_reg_list, reg in glv.conf.gdct_reg_list:
        for distin_gdct in glv.conf.distinguish_groups_list:
            for reg in distin_gdct['regions']:
                glv.conf.all_proc_cnt += 1
                glv.conf.gdct_reg_list += [[distin_gdct, reg]]

        log.info("glv.conf.gdct_reg_list complete, size = {}".format(
            glv.conf.all_proc_cnt))


    def make_distin_fname(
        self, outf_pref, distin_0, distin_1, rg, pick_mode):
        """
        """

        # if auto_group, group_pair_name is only 'auto_group'
        group_vs = distin_0
        if group_vs != glv.AUTO_GROUP:
            group_vs = "{}~{}".format(distin_0, distin_1)

        #distin~gHitomebore~gKaluheenati~rg0~all~50-200.txt
        #basename = "{}~{}~{}~{}~{}~i{}-{}~p{}-{}".format(
        basename = "{}~{}~{}~{}~i{}-{}~p{}-{}".format(
                outf_pref,
                group_vs,
                rg,
                pick_mode,
                glv.conf.min_indel_len,
                glv.conf.max_indel_len,
                glv.conf.min_product_size,
                glv.conf.max_product_size)

        # pathlib
        out_file_name = "{}/{}.txt".format(glv.conf.out_dir_path, basename)
        out_file_path = Path(out_file_name).resolve()

        return out_file_path, basename


    def make_header(self, type):

        # var_type  in  variant
        # var_type  in  marker
        # var_type  in  primer
        # var_type  in  formfail
        # var_type  in  formpass

        hd_l = list()
        hd_d = dict()
        i = 1   # 0 is index

        if type == 'variant':
            # ----------------------------------------------------------------
            # Synchronize with allele_select.py construct_variant_line
            hd_l, hd_d, i = self.mkmap('chrom',                hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('pos',                  hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('targ_grp',             hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('targ_ano',             hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('vseq_gno_str',         hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('var_type',             hd_l, hd_d, i)
            # 2022-10-27 add mk_type
            hd_l, hd_d, i = self.mkmap('mk_type',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('gts_segr_lens',        hd_l, hd_d, i)
            #hd_l, hd_d, i = self.mkmap('notice',               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('auto_grp0',            hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('auto_grp1',            hd_l, hd_d, i)
            # ----------------------------------------------------------------

            hd_l, hd_d, i = self.mkmap('vseq_ano_str',         hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('set_n',                hd_l, hd_d, i)
            # ----------------------
            hd_l, hd_d, i = self.mkmap('len_g0g1_dif_long',    hd_l, hd_d, i)


        elif type == 'marker':
            # Sync with eval_variant.py
            # copy_line_for_effective_restriction_enzymes
            hd_l, hd_d, i = self.mkmap('marker_id',            hd_l, hd_d, i)

            # ----------------------------------------------------------------
            hd_l, hd_d, i = self.mkmap('chrom',                hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('pos',                  hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('targ_grp',             hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('targ_ano',             hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('vseq_gno_str',         hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('var_type',             hd_l, hd_d, i)
            # 2022-10-26 add mk_type
            hd_l, hd_d, i = self.mkmap('mk_type',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('gts_segr_lens',        hd_l, hd_d, i)
            #hd_l, hd_d, i = self.mkmap('notice',               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('auto_grp0',            hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('auto_grp1',            hd_l, hd_d, i)
            # ----------------------------------------------------------------

            hd_l, hd_d, i = self.mkmap('set_enz_cnt',          hd_l, hd_d, i)
            # ----------------------
            hd_l, hd_d, i = self.mkmap('marker_info',          hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('vseq_lens_ano_str',    hd_l, hd_d, i)
            # --------------

            # g0
            hd_l, hd_d, i = self.mkmap('g0_seq_target_len',    hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g0_seq_target',        hd_l, hd_d, i)
            # g1
            hd_l, hd_d, i = self.mkmap('g1_seq_target_len',    hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_seq_target',        hd_l, hd_d, i)

            # seq_template_ref
            hd_l, hd_d, i = self.mkmap('seq_template_ref_len', hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('seq_template_ref_abs_pos',
                                                               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('seq_template_ref_rel_pos',
                                                               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('SEQUENCE_TARGET',      hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('seq_template_ref',     hd_l, hd_d, i)


        elif type == 'primer':  # there is no header

            # Synchronize with primer.py primer_complete_to_line
            hd_l, hd_d, i = self.mkmap('marker_id',            hd_l, hd_d, i)

            # ----------------------------------------
            hd_l, hd_d, i = self.mkmap('chrom',                hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('pos',                  hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('targ_grp',             hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('targ_ano',             hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('vseq_gno_str',         hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('var_type',             hd_l, hd_d, i)
            # 2022-10-26 add
            hd_l, hd_d, i = self.mkmap('mk_type',              hd_l, hd_d, i)
            # 2023-04-10
            hd_l, hd_d, i = self.mkmap('in_target',            hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('gts_segr_lens',        hd_l, hd_d, i)
            #hd_l, hd_d, i = self.mkmap('notice',               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('auto_grp0',            hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('auto_grp1',            hd_l, hd_d, i)
            # ----------------------------------------

            hd_l, hd_d, i = self.mkmap('set_enz_cnt',          hd_l, hd_d, i)
            # --------------
            hd_l, hd_d, i = self.mkmap('marker_info',          hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('vseq_lens_ano_str',    hd_l, hd_d, i)
            # --------------
            hd_l, hd_d, i = self.mkmap('g0_seq_target_len',    hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g0_seq_target',        hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_seq_target_len',    hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_seq_target',        hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('seq_template_ref_len', hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('seq_template_ref_abs_pos',
                                                               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('seq_template_ref_rel_pos',
                                                               hd_l, hd_d, i)
            # --------------

            hd_l, hd_d, i = self.mkmap('try_cnt',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('complete',             hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('blast_check',          hd_l, hd_d, i)
            # --------------

            hd_l, hd_d, i = self.mkmap('PRIMER_PAIR_0_PRODUCT_SIZE',
                                                               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('product_gc_contents',  hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('PRIMER_LEFT_0',        hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('left_primer_id',       hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('PRIMER_LEFT_0_SEQUENCE',
                                                               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('PRIMER_RIGHT_0',       hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('right_primer_id',      hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('PRIMER_RIGHT_0_SEQUENCE',
                                                               hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('SEQUENCE_TARGET',      hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('SEQUENCE_EXCLUDED_REGION',
                                                               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('SEQUENCE_TEMPLATE',    hd_l, hd_d, i)


        elif type == 'formpass':

            # Synchronize with formtxt.py format_product

            hd_l, hd_d, i = self.mkmap('chrom',                hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('pos',                  hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('g0_vseq',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_vseq',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g0_gt',                hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_gt',                hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('targ_ano',             hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('var_type',             hd_l, hd_d, i)
            # 2022-10-26 add
            hd_l, hd_d, i = self.mkmap('mk_type',              hd_l, hd_d, i)
            # 2023-04-10
            hd_l, hd_d, i = self.mkmap('in_target',            hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('dup_pos',              hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('auto_grp0',            hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('auto_grp1',            hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('enzyme',               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g0_name',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_name',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g0_product_size',      hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_product_size',      hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('product_gc_contents',  hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('diff_length',          hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g0_digested_size',     hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('g1_digested_size',     hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('digested_gno',         hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('digested_ano',         hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('try_cnt',              hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('complete',             hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('marker_id',            hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('gts_segr_lens',        hd_l, hd_d, i)

            hd_l, hd_d, i = self.mkmap('left_primer_id',       hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('PRIMER_LEFT_0_SEQUENCE',
                                                               hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('right_primer_id',      hd_l, hd_d, i)
            hd_l, hd_d, i = self.mkmap('PRIMER_RIGHT_0_SEQUENCE',
                                                               hd_l, hd_d, i)
            #hd_l, hd_d, i = self.mkmap('notice',               hd_l, hd_d, i)

            #Allele string '00' information for each sample will be added


        hd_str = '\t'.join(map(str, hd_l))

        #print(type)
        #print(hd_str)
        #print(hd_l)
        #print(hd_d)
        #sys.exit(1)

        return hd_str, hd_l, hd_d


    def mkmap(self, key, header_list, header_dict, idx):

        #log.debug("{} {} {} {}".format(
        #    key, header, header_dict, idx,
        #    ))

        header_list += [key]
        add_dict = {key: idx}
        header_dict.update(add_dict)
        idx += 1

        return header_list, header_dict, idx


