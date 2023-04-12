# -*- coding: utf-8 -*-

import sys
#import os
from pathlib import Path
import errno
import time
import re
import pprint

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
log = LogConf.open_log(__name__)

import pandas as pd
import vcfpy
import subprocess as sbp

from joblib import Parallel, delayed
#import dill as pickle

from vprimer.product import Product
from vprimer.allele_select import AlleleSelect
from vprimer.eval_variant import EvalVariant
from vprimer.variant import Variant
from vprimer.inout_primer3 import InoutPrimer3
from vprimer.blast import Blast

class Primer(object):

    def __init__(self):

        pass

    def construct_primer(self):

        proc_name = "primer"
        log.info("-------------------------------")
        log.info("Start processing {}\n".format(proc_name))

        # stop, action, gothrough
        ret_status = utl.decide_action_stop(proc_name)

        if ret_status == "stop":
            msg = "STOP. "
            msg += "Current process \'{}\' ".format(proc_name)
            msg += "has exceeded the User-specified stop point "
            msg += "\'{}', ".format(glv.conf.stop)
            msg += "so stop program. exit."
            log.info(msg)
            sys.exit(1)


        elif ret_status == "gothrough":
            msg = "SKIP \'{}\' proc, ".format(proc_name)
            msg += "glv.conf.progress = {}, ".format(glv.conf.progress)
            msg += "glv.conf.stop = {}, ".format(glv.conf.stop)
            msg += "so skip program."
            log.info(msg)
            return


        # for each distinguish_groups
        proc_cnt = 0
        for distin_gdct, reg in glv.conf.gdct_reg_list:
            proc_cnt += 1

            # logging current target
            utl.pr_dg("primer", distin_gdct, reg, proc_cnt)

            marker_file = distin_gdct['marker']['fn'][reg]['out_path']
            log.info("marker_file {}".format(marker_file))

            df_distin = pd.read_csv(
                marker_file, sep='\t', header=0, index_col=None)

            #print("in construct_primer")
            #print(df_distin)
            # 空欄を書き入れているのがそもそもの問題
            # ACTAG^I^I$

            out_txt_path = distin_gdct['primer']['fn'][reg]['out_path']
            utl.save_to_tmpfile(out_txt_path)

            with out_txt_path.open('a', encoding='utf-8') as f:
                # write header
                #f.write("{}\n".format(distin_file['primer']['hdr_text']))

                start = utl.get_start_time()

                if glv.conf.parallel == True:
                    log.info(
                        "do Parallel cpu {}, parallel {} blast {}".format(
                            glv.conf.thread,
                            glv.conf.parallel_blast_cnt,
                            glv.conf.blast_num_threads))

                    Parallel(
                        n_jobs=glv.conf.parallel_blast_cnt,
                        backend="threading")(
                        [
                            delayed(self.loop_p3_chk_blst) \
                                (distin_gdct, marker_df_row, f) \
                                for marker_df_row in \
                                    df_distin.itertuples()
                        ]
                    )

                else:
                    log.info(
                        "do Serial cpu {} / serial {} blast {}".format(
                            glv.conf.thread,
                            1,
                            glv.conf.blast_num_threads))

                    for marker_df_row in df_distin.itertuples():

                        self.loop_p3_chk_blst(
                            distin_gdct, marker_df_row, f)

            utl.sort_file(
                'primer', distin_gdct, out_txt_path,
                'chrom', 'pos', 'try_cnt', 'number')

            log.info("primer {} > {}.txt\n".format(
                utl.elapse_str(start),
                distin_gdct['variant']['fn'][reg]['base_nam']))


    def loop_p3_chk_blst(self, distin_gdct, marker_df_row, f):

        # プライマー情報クラスのインスタンスを作る
        prinfo = PrimerInfo()
        prinfo.prepare_from_marker_file(distin_gdct, marker_df_row)

        # bedファイルのpath
        bed_thal_path = distin_gdct['bed_thal_path']

        # add exluded region
        prinfo.get_excluded_region(bed_thal_path)

        prinfo.make_p3_info()
        blast_check_result_list = list()

        line = ''
        try_cnt = 0
        blast_check = ''

        complete = 0

        '''
        complete
        -1: hairpinもしくはblastで、primer再設計に回されたデータ
         0: プライマーが作成されずに終わった
         1: 正しくプライマーが作成された
        try_cnt
        '''

        while True:
            try_cnt += 1
            self.do_primer3_pipe(prinfo.iopr3)

            if prinfo.iopr3.PRIMER_ERROR != '':
                #log.info("{} PRIMER_ERROR={} try {}".format(
                #    prinfo.iopr3.get_sequence_id(),
                #    prinfo.iopr3.PRIMER_ERROR,
                #    try_cnt))
                complete = -10
                line, blast_check = self.primer_complete_to_line(
                    complete, blast_check_result_list, prinfo, try_cnt)
                f.write('{}\n'.format(line))
                break

            elif prinfo.iopr3.PRIMER_PAIR_NUM_RETURNED == 0:
                #log.info("{} RETURNED={} try {}".format(
                #    prinfo.iopr3.get_sequence_id(),
                #    prinfo.iopr3.PRIMER_PAIR_NUM_RETURNED,
                #    try_cnt))
                complete = -20
                line, blast_check = self.primer_complete_to_line(
                    complete, blast_check_result_list, prinfo, try_cnt)
                f.write('{}\n'.format(line))
                break


            # glv.MODE_SNP in self.pick_mode
            # distin_file に、pick_mode がなければならない。
            if distin_gdct['pick_mode'] == glv.MODE_SNP:

                #print("hairpin_check")

                l_primer_ok, r_primer_ok = \
                    prinfo.iopr3.check_p3_pairpin_dimer()
                #log.info("{} hairpin {},{} try {}".format(
                #    prinfo.iopr3.get_sequence_id(),
                #    l_primer_ok, r_primer_ok,
                #    try_cnt))

                if l_primer_ok and r_primer_ok:
                    pass
                else:
                    primer_loc = 'both'
                    if not l_primer_ok and not r_primer_ok:
                        pass
                    elif not l_primer_ok:
                        primer_loc = 'left'
                    elif not r_primer_ok:
                        primer_loc = 'right'
                    prinfo.iopr3.add_ex_region(
                        prinfo.iopr3.get_primer_region(primer_loc))
                    complete -= 1
                    '''
                    line, blast_check = \
                        self.primer_complete_to_line(
                        complete, \
                        blast_check_result_list, \
                        prinfo, try_cnt)
                    f.write('{}\n'.format(line))
                    '''
                    continue

            # calc abs pos
            abs_left_stt, abs_left_end, \
            abs_right_stt, abs_right_end = \
                self.get_primer_pos_info(prinfo)

            # make fasta id
            left_fasta_id = self.make_primer_name(
                prinfo.chrom, abs_left_stt, abs_left_end, "plus")
            right_fasta_id = self.make_primer_name(
                prinfo.chrom, abs_right_stt, abs_right_end, "minus")

            # set_primer_name
            prinfo.iopr3.make_primer_seq(left_fasta_id, right_fasta_id)
            #prinfo.iopr3.set_primer_name(left_fasta_id, right_fasta_id)

            # search my blastn-short
            blast_check_result_list = \
                Blast.primer_blast_check(
                    left_fasta_id, right_fasta_id,
                    prinfo.iopr3.get_primer_left_seq(),
                    prinfo.iopr3.get_primer_right_seq())

            # break if complete
            if len(blast_check_result_list) == 0:

                #------------------------------
                complete = 1
                line, blast_check = self.primer_complete_to_line(
                    complete, blast_check_result_list, prinfo, try_cnt)
                f.write('{}\n'.format(line))

                #log.info("{} ok_blast try {}".format(
                #    prinfo.iopr3.get_sequence_id(),
                #    try_cnt))

                break

            else:
                # go to next chance to add the primer pos to ex
                prinfo.iopr3.add_ex_region(prinfo.iopr3.get_primer_region())

                #------------------------------
                complete = 0
                line, blast_check = self.primer_complete_to_line(
                    complete, blast_check_result_list, prinfo, try_cnt)
                f.write('{}\n'.format(line))

                #log.info("{} ng_blast {} try {}".format(
                #    prinfo.iopr3.get_sequence_id(),
                #    blast_check,
                #    try_cnt))

        if len(blast_check_result_list) != 0:
            log.info("{} last blast {} try {}".format(
                prinfo.iopr3.get_sequence_id(),
                blast_check,
                try_cnt))

#        if line != '':
#            f.write('{}\n'.format(line))
#            # if you need
#            f.flush()


    def primer_complete_to_line(
        self, complete, blast_check_result_list, prinfo, try_cnt):

        # blast_check
        blast_check = "-"
        add_cnt = len(blast_check_result_list) - 1
        if add_cnt == -1:
            pass
        elif add_cnt == 0:
            blast_check = "{}".format(blast_check_result_list[0])
        else:
            blast_check = "{}(+{})".format(
                blast_check_result_list[0], add_cnt)


        l_list = list()

        # to primer out file
        l_list += [prinfo.marker_id]

        #----------------------------------
        l_list += [prinfo.chrom]
        l_list += [prinfo.pos]
        l_list += [prinfo.targ_grp]
        l_list += [prinfo.vseq_gno_str]
        l_list += [prinfo.gts_segr_lens]
        l_list += [prinfo.targ_ano]
        l_list += [prinfo.var_type]
        # 2022-10-26 add
        l_list += [prinfo.mk_type]
        # auto_grp
        l_list += [prinfo.auto_grp0]
        l_list += [prinfo.auto_grp1]
        #----------------------------------
        # --------------
        l_list += [prinfo.set_enz_cnt]
        # --------------
        l_list += [prinfo.marker_info]
        l_list += [prinfo.vseq_lens_ano_str]
        # --------------
        l_list += [prinfo.g0_seq_target_len]
        l_list += [prinfo.g0_seq_target]
        l_list += [prinfo.g1_seq_target_len]
        l_list += [prinfo.g1_seq_target]

        l_list += [prinfo.seq_template_ref_len]
        l_list += [prinfo.seq_template_ref_abs_pos]
        l_list += [prinfo.seq_template_ref_rel_pos]
        # --------------
        # 2023-04-10
        l_list += [prinfo.in_target]
        l_list += [try_cnt]
        l_list += [complete]
        l_list += [blast_check]
        # --------------

        if complete < 0:
            l_list += [0]       # prinfo.iopr3.get_primer_product_size
            l_list += [0.0]     # prinfo.iopr3.get_product_gc_contents

            l_list += ['-']     # prinfo.iopr3.get_primer_left
            l_list += ['-']     # prinfo.iopr3.get_primer_left_id
            l_list += ['-']     # prinfo.iopr3.get_primer_left_seq

            l_list += ['-']     # prinfo.iopr3.get_primer_right
            l_list += ['-']     # prinfo.iopr3.get_primer_right_id
            l_list += ['-']     # prinfo.iopr3.get_primer_right_seq

        else:
            l_list += [prinfo.iopr3.get_primer_product_size()]
            l_list += [prinfo.iopr3.get_product_gc_contents()]

            l_list += [prinfo.iopr3.get_primer_left()]
            l_list += [prinfo.iopr3.get_primer_left_id()]
            l_list += [prinfo.iopr3.get_primer_left_seq()]

            l_list += [prinfo.iopr3.get_primer_right()]
            l_list += [prinfo.iopr3.get_primer_right_id()]
            l_list += [prinfo.iopr3.get_primer_right_seq()]

        l_list += [prinfo.SEQUENCE_TARGET]
        # 
        l_list += [prinfo.iopr3.get_sequence_excluded_region()]
        l_list += [prinfo.seq_template_ref]


        #print(">{}<".format(','.join(map(str, l_list))))
        #sys.exit(1)

        return '\t'.join(map(str, l_list)), blast_check


    def make_primer_name(
            self, chrom, abs_primer_stt_pos, abs_primer_end_pos, strand):

        # {NC_028450.1}44676.44700.plus
        #primer_name = "{{{}}}{}.{}.{}".format(
        #    chrom,
        #    abs_primer_stt_pos,
        #    abs_primer_end_pos,
        #    strand)

        # NC_028450.1:44676-44700:plus
        primer_name = "{}:{}-{}:{}".format(
            chrom,
            abs_primer_stt_pos,
            abs_primer_end_pos,
            strand)

        return primer_name


    def do_primer3_pipe(self, iopr3):

        # exec primer3 through pipe
        primer3_in = iopr3.get_p3_input()

        # subprocess
        primer3_out_p = sbp.Popen(
            ['primer3_core'],
            stdin=sbp.PIPE,
            stdout=sbp.PIPE)

        primer3_out = primer3_out_p.communicate(
            primer3_in.encode())[0].decode()

        iopr3.set_primer3_out(primer3_out)


    def get_primer_pos_info(self, prinfo):
        '''
        '''

        # This value brings PRIMER_LEFT_0 value directly.
        # 353,25
        PRIMER_LEFT_0_stt, PRIMER_LEFT_0_len = \
            prinfo.iopr3.get_primer_left_info()

        # For PRIMER_LEFT_0, the starting point is reported
        # in the 5'-3'direction as usual.
        # Therefore, the absolute position is calculated
        # based on the length as usual.
        abs_PRIMER_LEFT_0_stt = self.get_abspos(
            PRIMER_LEFT_0_stt, prinfo.abs_frag_pad_pre_stt)
        abs_PRIMER_LEFT_0_end = abs_PRIMER_LEFT_0_stt + PRIMER_LEFT_0_len - 1

        # This value brings PRIMER_RIGHT_0 value directly.
        # 567,25
        # On the other hand, for PRIMER_RIGHT_0,
        # the position on the 3'side is reported.
        PRIMER_RIGHT_0_end, PRIMER_RIGHT_0_len = \
            prinfo.iopr3.get_primer_right_info()

        # Therefore, the starting point is obtained using the length.
        PRIMER_RIGHT_0_stt = PRIMER_RIGHT_0_end - PRIMER_RIGHT_0_len + 1
        # After that, just convert to absolute position.
        abs_PRIMER_RIGHT_0_stt = self.get_abspos(
            PRIMER_RIGHT_0_stt, prinfo.abs_frag_pad_pre_stt)
        abs_PRIMER_RIGHT_0_end = \
            abs_PRIMER_RIGHT_0_stt + PRIMER_RIGHT_0_len - 1

        return \
            abs_PRIMER_LEFT_0_stt, abs_PRIMER_LEFT_0_end, \
            abs_PRIMER_RIGHT_0_stt, abs_PRIMER_RIGHT_0_end


    def get_abspos(self, ref_pos, abs_template_stt):

        # 11
        #  1234567890
        #        7 11+7=18 -1

        return abs_template_stt + ref_pos - 1


class PrimerInfo(object):

    def __init__(self):

        pass


    def prepare_from_marker_file(self, distin_gdct, marker_df_row):

        hdr_dict = distin_gdct['marker']['hdr_dict']
        #hdr_dict = utl.remove_deepcopy_auto_grp_header_dict(
        #    distin_gdct['marker']['hdr_dict'])
        #hdr_dict = utl.deepcopy_grp_header_dict(
        #    distin_gdct['marker']['hdr_dict'])

        # basic
        self.marker_id, \
        self.chrom, \
        self.pos, \
        self.targ_grp, \
        self.g0_name, \
        self.g1_name, \
        self.targ_ano, \
        self.g0_ano_i, \
        self.g1_ano_i, \
        self.vseq_gno_str, \
        self.gts_segr_lens, \
        self.var_type, \
        self.mk_type, \
        self.set_enz_cnt, \
        self.marker_info, \
        self.vseq_lens_ano_str, \
        self.enzyme_name, \
        self.digest_pattern, \
        self.target_gno, \
        self.target_len, \
        self.auto_grp0, \
        self.auto_grp1 = \
            utl.get_basic_primer_info(marker_df_row, hdr_dict)

        # start -
        self.in_target = "-"
        #self.notice,

        self.g0_seq_target_len = \
            int(marker_df_row[hdr_dict['g0_seq_target_len']])
        self.g0_seq_target = \
            str(marker_df_row[hdr_dict['g0_seq_target']])
        self.g1_seq_target_len = \
            int(marker_df_row[hdr_dict['g1_seq_target_len']])
        self.g1_seq_target = \
            str(marker_df_row[hdr_dict['g1_seq_target']])

        self.seq_template_ref_len = \
            int(marker_df_row[hdr_dict['seq_template_ref_len']])
        self.seq_template_ref_abs_pos = \
            str(marker_df_row[hdr_dict['seq_template_ref_abs_pos']])

        #log.debug("{}".format(self.seq_template_ref_abs_pos))

        self.seq_template_ref_rel_pos = \
            str(marker_df_row[hdr_dict['seq_template_ref_rel_pos']])

        #log.debug("{}".format(self.seq_template_ref_rel_pos))

        self.SEQUENCE_TARGET = \
            str(marker_df_row[hdr_dict['SEQUENCE_TARGET']])
        self.seq_template_ref = \
            str(marker_df_row[hdr_dict['SEQUENCE_TEMPLATE']])
            #str(marker_df_row[hdr_dict['seq_template_ref']])

        # abs template info
        self.abs_frag_pad_pre_stt, \
        self.abs_frag_pad_pre_end, \
        self.abs_around_seq_pre_stt, \
        self.abs_around_seq_pre_end, \
        self.abs_pos, \
        self.abs_around_seq_aft_stt, \
        self.abs_around_seq_aft_end, \
        self.abs_frag_pad_aft_stt, \
        self.abs_frag_pad_aft_end = \
            Product.separate_seq_template_pos(
                self.seq_template_ref_abs_pos)

        # rel template info
        self.rel_frag_pad_pre_stt, \
        self.rel_frag_pad_pre_end, \
        self.rel_around_seq_pre_stt, \
        self.rel_around_seq_pre_end, \
        self.rel_pos, \
        self.rel_around_seq_aft_stt, \
        self.rel_around_seq_aft_end, \
        self.rel_frag_pad_aft_stt, \
        self.rel_frag_pad_aft_end = \
            Product.separate_seq_template_pos(
                self.seq_template_ref_rel_pos)


    def get_relpos(self, abs_pos):

        #   | self.abs_frag_pad_pre_stt
        #                 self.abs_frag_pad_aft_end|
        #   <-------><========>P<=========><------->
        #            |self.abs_around_seq_pre_stt
        #      self.abs_around_seq_aft_end|
        #   |101 109|
        #   123456789
        #       |105
        #   105-101+1 = 5

        rel_pos = abs_pos - self.abs_frag_pad_pre_stt + 1

        return rel_pos


    def get_excluded_region(self, bed_thal_path):
        ''' 辞書を指定して
            excludeするファイルが別
        '''

        #print("in get_excluded_region={}".format(bed_thal_path))

        self.SEQUENCE_EXCLUDED_REGION = ""
        list_SEQUENCE_EXCLUDED_REGION = list()

        # get now search region from vcf
        region = "{}:{}-{}".format(
            self.chrom,
            self.abs_frag_pad_pre_stt,
            self.abs_frag_pad_aft_end)
            # self.seq_template_ref_len

        #print("region={}".format(region))

        # ['123-456', '789'-1011']
        if bed_thal_path != "-":
            # search thin_region_list from bed
            exclude_region_list = self.search_bed(
                # bed_thal_path にて登録された辞書を使う
                bed_thal_path,
                self.chrom,
                self.abs_frag_pad_pre_stt,  # templateの開始
                self.abs_frag_pad_aft_end)  # templateの終了

            # 返ってきた thin リージョンそれぞれについて
            # 絶対posを、相対posに変換
            for ex in exclude_region_list:
                start, end = map(int, ex.split('-'))

                # get relative position
                rel_start = self.get_relpos(start)
                rel_end = self.get_relpos(end)

                # 開始点、終了点を調整
                # 1-{self.seq_template_ref_len}
                if rel_start < 1: # also 0
                    rel_start = 1

                if self.seq_template_ref_len < rel_end:
                    rel_end = self.seq_template_ref_len

                # calc len
                rel_len = rel_end - rel_start + 1

                # append
                list_SEQUENCE_EXCLUDED_REGION.append(
                    "{},{}".format(rel_start, rel_len))

        # メンバ名のリストを作り、gtがREF以外ならSNPありなので、excludeする
        if not glv.conf.is_auto_group:
            all_samples = \
                glv.conf.group_members_dict[self.g0_name]['sn_lst'] + \
                glv.conf.group_members_dict[self.g1_name]['sn_lst']
        else:
            all_samples = \
                glv.conf.group_members_dict[glv.AUTO_GROUP]['sn_lst']

        reader = vcfpy.Reader.from_path(glv.conf.vcf_gt_path)
        vcf_ittr = reader.fetch(region)

        # access to vcf using iterater
        for record in vcf_ittr:

            for member_name in all_samples:

                fullname = utl.get_fullname(member_name)
                alstr = AlleleSelect.record_call_for_sample(record, fullname)

                #if alstr == "..":
                #    print("{} {}".format(alstr, member_name))

                # 00と違うけれど、./. は評価しないようにしないと
                # いけないな。マーカー可能かどうか別にして、
                # 存在するバリアントを見てるから
                if alstr != "00" and alstr != ".." and \
                    self.pos != record.POS:

                    #if alstr == "..":
                    #    print(">> {} {}".format(alstr, member_name))

                    # variantのref側の長さ この分を避ける
                    variant_len = len(record.REF)
                    rel_pos = self.get_relpos(record.POS)

                    if False:
                        print()
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print("member_name  = {}".format(member_name))
                        print("alstr        = {}".format(alstr))
                        print("region       = {} {}-{}-{} {}".format(
                            self.abs_frag_pad_pre_stt,
                            self.abs_around_seq_pre_stt,
                            self.pos,
                            self.abs_around_seq_aft_end,
                            self.abs_frag_pad_aft_end))
                        print("record.POS   = {}".format(record.POS))
                        #print(record)

                        if record.POS < self.abs_frag_pad_pre_stt:
                            print()
                            print("\t+++++++++++++++++++++++++++")
                            print("\trecord.POS < region start")
                            print()

                        print("variant_le   = {}".format(variant_len))
                        print("rel_pos      = {}".format(rel_pos))
                        print()

                        # もし、target_sequence内に、ヴァリアントが
                        # 見つかったら、noticeにサンプル名を追記する。
                        if self.abs_around_seq_pre_stt <= record.POS and \
                            record.POS <= self.abs_around_seq_aft_end:

                            # concat by ','
                            self.in_target = utl.make_in_target(
                                self.in_target,
                                member_name, record.POS, self.pos, 
                                variant_len)
                            # add member_name to notice field
                            #self.notice = utl.make_notice(
                            #    self.notice, member_name)

                            # chrom_01        166779

                            # to notice
                            #if self.pos == 463670:
                            if False:
                                print("-------------------------")
                                print("in target_seq")
                                print()
                                print(self.in_target)
                                print()
                                print("-------------------------")
                                print()

                    # ただし、このvariantの長さは、
                    # seq_templateの終点を越えることが
                    # あるので、指定は終点を越えないようにする。
                    rel_end_pos = rel_pos + variant_len - 1

                    # 調整
                    if rel_end_pos > self.seq_template_ref_len:
                        # 越えている分を引いてseq_templateの終点まで
                        diff_len = rel_end_pos - self.seq_template_ref_len
                        variant_len = variant_len - diff_len

                    # 登録する領域
                    exr = "{},{}".format(rel_pos, variant_len)

                    # add
                    list_SEQUENCE_EXCLUDED_REGION += [exr]

                    # １つ異なるのがあればそれでいい break
                    break

        self.SEQUENCE_EXCLUDED_REGION = \
            " ".join(list_SEQUENCE_EXCLUDED_REGION)
        #print(self.SEQUENCE_EXCLUDED_REGION)
        #print("\n========================================")
        #print("{}, {}, {}, {}".format(
        #    self.pos, record.POS,
        #    region,
        #    self.SEQUENCE_EXCLUDED_REGION))


    def search_bed(self, bed_thal_path, chrom, abs_start, abs_end):

        #print("search_bed {} {} {}".format(chrom, abs_start, abs_end))

        exclude_list = list()

        # 1) Wrap the whole
        # start------------------end
        #    abs_start  abs_end
        q = 'start < {} and {} < end'.format(
            abs_start,
            abs_end)

        #print("{} {}".format(1, q))

        #print("bed_thal_path={}".format(bed_thal_path))
        #print("glv.conf.bed_thal_dict[bed_thal_path][chrom]")

        #print(glv.conf.bed_thal_dict[bed_thal_path][chrom])
        #print("end")

        df_s = glv.conf.bed_thal_dict[bed_thal_path][chrom].query(q)

        #print("df_s")
        #print(df_s)
        #print("end")

        #df_s = glv.conf.bed_dict[chrom].query(q)

        if len(df_s) > 0:
            for row in df_s.itertuples():
                pos_str = "{}-{}".format(row[2], row[3])
            exclude_list.append(pos_str)

        # 2) Sandwich the start
        # start-------end
        #    abs_start       abs_end
        #
        # 2) start < 30551
        #    30551 <= end
        #    end <= 31591
        q = 'start < {} and {} <= end and end <= {}'.format(
            abs_start,
            abs_start,
            abs_end)

        #print()
        #print("{} {}".format(2, q))
        #df_s = glv.conf.bed_dict[chrom].query(q)
        df_s = glv.conf.bed_thal_dict[bed_thal_path][chrom].query(q)

        #print("df_s")
        #print(df_s)
        #print("end")
        
        if len(df_s) > 0:
            for row in df_s.itertuples():
                pos_str = "{}-{}".format(row[2], row[3])
            exclude_list.append(pos_str)

        # 3) Sandwich the end
        #                start-------end
        #    abs_start       abs_end
        #
        # 3) 30551 <= start
        #    start <= 31591
        #    31591 < end
        q = '{} <= start and start <= {} and {} < end'.format(
            abs_start,
            abs_end,
            abs_end)

        #print()
        #print("{} {}".format(3, q))
        #df_s = glv.conf.bed_dict[chrom].query(q)
        df_s = glv.conf.bed_thal_dict[bed_thal_path][chrom].query(q)

        #print("df_s")
        #print(df_s)
        #print("end")

        if len(df_s) > 0:
            for row in df_s.itertuples():
                pos_str = "{}-{}".format(row[2], row[3])
            exclude_list.append(pos_str)

        # 4) inner
        #            start-end
        # abs_start              abs_end
        q = '{} <= start and {} >= end'.format(
            abs_start,
            abs_end)

        #print()
        #print("{} {}".format(4, q))
        #df_s = glv.conf.bed_dict[chrom].query(q)
        df_s = glv.conf.bed_thal_dict[bed_thal_path][chrom].query(q)

        #print("df_s")
        #print(df_s)
        #print("end")

        if len(df_s) > 0:
            for row in df_s.itertuples():
                pos_str = "{}-{}".format(row[2], row[3])
            exclude_list.append(pos_str)

        return exclude_list


    def make_p3_info(self):

        # save information
        self.p3_comment = self.make_p3_comment()
        #log.debug("{}".format(self.p3_comment))

        self.iopr3 = InoutPrimer3()
        self.iopr3.set_p3_comment(self.p3_comment)
        self.iopr3.set_sequence_target(self.SEQUENCE_TARGET)
        self.iopr3.add_ex_region(self.SEQUENCE_EXCLUDED_REGION)
        self.iopr3.set_sequence_id(self.marker_id)
        self.iopr3.set_sequence_template(self.seq_template_ref)

        #log.debug("")
        #log.debug("{}".format(self.iopr3.get_p3_input()))


    def make_p3_comment(self):

        p3_comment = list()
        p3_comment += ["{}:{}".format('marker_id', self.marker_id)]
        p3_comment += ["{}:{}".format('var_type', self.var_type)]
        p3_comment += ["{}:{}".format('g0_name', self.g0_name)]
        p3_comment += ["{}:{}".format('g1_name', self.g1_name)]
        p3_comment += ["{}:{}".format('marker_info', self.marker_info)]


        p3_comment += ["{}:{}".format(
            'g0_seq_target_len', self.g0_seq_target_len)]
        p3_comment += ["{}:{}".format(
            'g0_seq_target', self.g0_seq_target)]
        p3_comment += ["{}:{}".format(
            'g1_seq_target_len', self.g1_seq_target_len)]
        p3_comment += ["{}:{}".format(
            'g1_seq_target', self.g1_seq_target)]

        p3_comment += ["{}:{}".format(
            'seq_template_ref_len', self.seq_template_ref_len)]
        p3_comment += ["{}:{}".format(
            'seq_template_ref_abs_pos', self.seq_template_ref_abs_pos)]
        p3_comment += ["{}:{}".format(
            'seq_template_ref_rel_pos', self.seq_template_ref_rel_pos)]

        return ';'.join(map(str, p3_comment))




