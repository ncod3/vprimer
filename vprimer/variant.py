# -*- coding: utf-8 *-*

import sys
#import os
from pathlib import Path
import errno
import time
import pprint
import numpy as np
import itertools

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
log = LogConf.open_log(__name__)

import vcfpy

from vprimer.allele_select import AlleleSelect

class Variant(object):

    def __init__(self):

        pass


    def pick_variant(self):
        """
        """

        proc_name = "variant"
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


        # open vcf through vcfpy
        reader = vcfpy.Reader.from_path(glv.conf.vcf_gt_path)

        # for all combination,
        proc_cnt = 0
        for distin_gdct, reg in glv.conf.gdct_reg_list:
            proc_cnt += 1
            # vcf_ittr for each distinguish groups
            vcf_ittr = reader.fetch(glv.conf.regions_dict[reg]['reg'])
            # pickup variant
            self.iterate_vcf(vcf_ittr, distin_gdct, reg, proc_cnt)


    def iterate_vcf(self, vcf_ittr, distin_gdct, reg, proc_cnt):
        '''
        '''

        # start time
        start = utl.get_start_time()
        # logging current target
        utl.print_dg("variant", distin_gdct, reg, proc_cnt)

        # File name to export variant data
        out_txt_path = distin_gdct['variant']['fn'][reg]['out_path']
        # If there is old data with the same name, back it up
        utl.save_to_tmpfile(out_txt_path)

        # header: if glv.conf.is_auto_group, remove last 2 columns
        header_txt = utl.remove_autogrp_header_txt(
            distin_gdct['variant']['hdr_text'])

        # pick mode and indel length
        pick_mode = distin_gdct['pick_mode']
        indel_size = distin_gdct['indel_size']
        min_indel_len, max_indel_len = \
            [int(i) for i in indel_size.split('-')]
        #product_size =

        with out_txt_path.open('a', encoding='utf-8') as f:
            # write header
            f.write("{}\n".format(header_txt))
            # access to vcf using iterater
            for record in vcf_ittr:

                # ここでするのは、genotype_pairを作ること
                skip, \
                group_tuple_list, \
                alstr_tuple_list, \
                member_dict = \
                    self.make_genotype_pair(record, distin_gdct)

                #### print("after make_genotype_pair")
                #### print("skip={}".format(skip))
                #### print("group_tuple_list={}".format(group_tuple_list))
                #### print("alstr_tuple_list={}".format(alstr_tuple_list))
                #### print("member_dict={}".format(member_dict))
                #### print()

                # if this genotype_pair is out of interest
                if skip:
                    continue

                # allele_pairを、テキストで保存すること
                #for alstr_tuple in alstr_combi_tuple_list:
                for group_tuple, alstr_tuple in zip(
                    group_tuple_list, alstr_tuple_list):

                    #print(group_tuple)
                    #print(alstr_tuple)

                    # Select different allele combination among 2x2 allele
                    # for each record, create an instance of AlleleSelect
                    asel = AlleleSelect(
                        min_indel_len, max_indel_len, pick_mode)

                    # set all diff allele combination to asel instance
                    asel.set_diff_allele_combination(
                        record, group_tuple, alstr_tuple, member_dict)

                    #=====================================================
                    # Save variant information as text file
                    #=====================================================
                    for var_type, var_line in zip(
                        asel.var_types, asel.var_lines):

                        # If the pick_mode and the current var_type match
                        if asel.is_var_type_in_pick_mode(var_type):
                            # out to file
                            f.write("{}\n".format(var_line))


        ### print("STOP")
        ### sys.exit(1)


    def make_genotype_pair(self, record, distin_gdct):

        #print("in make_genotype_pair")

        # 戻す値
        # skipの条件が当てはまる場合、処理をしない
        skip = False
        # 1) tuple's group list # [('c', 'd'), ('c', 'e'), ('d', 'e')]
        group_tuple_list = list()
        # 2) make a combination of unique alstr tuple(uq_alstr_ndary)
        # [('00', '01'), ('00', '11'), ('01', '11')]
        alstr_tuple_list = list()
        # 3) dictionary of members belonging to group name
        # {'c': ['Ginganoshizuku', 'Takanari']}
        member_dict = dict()

        # 扱うサンプルは、指定された全サンプル
        all_target_samples = distin_gdct['sorted_samples'].split(',')

        # 指定された全サンプル内で、ユニークなgenotype(alstr)を得る ndarray
        alstr_list, uq_alstr_ndary = \
            self.get_unique_alstr(all_target_samples, record, distin_gdct)

        # 要素が１つならば、このバリアントはスキップする
        if len(uq_alstr_ndary) <= 1:
            skip = True
            #print("SKIP {}".format(uq_alstr_ndary))
            return skip, group_tuple_list, alstr_tuple_list, member_dict

        ### print("in make_genotype_pair PASS {}".format(uq_alstr_ndary))
        # alstrの全組み合わせのタプルを作り、仮のグループ名でメンバ構成を作る
        # group_listは、順番

        # for vcf
        #group_tuple_list, alstr_tuple_list, member_dict = \

        vcf_grtpl_list, vcf_altpl_list, vcf_mem_dict, vcf_algnm_dict = \
            self.alstr_combination(
                all_target_samples, alstr_list, uq_alstr_ndary)


        ### print("vcf_algnm_dict")
        ### pprint.pprint(vcf_algnm_dict)

        reverse_group = False

        if not glv.conf.is_auto_group:
            # 固定グループならば、グループ通りに分離しているかどうか調査する
            skip, reverse_group = self.judge_fixed_group_segregation(
                vcf_grtpl_list, vcf_mem_dict, distin_gdct)

            gname_0 = distin_gdct[0]
            gname_1 = distin_gdct[1]

            group_tuple_list = [(gname_0, gname_1)]
            member_dict = {
                gname_0: glv.conf.group_members_dict[gname_0]['sn_lst'],
                gname_1: glv.conf.group_members_dict[gname_1]['sn_lst'],
            }

            if not reverse_group:
                alstr_tuple_list = vcf_altpl_list
            else:
                alstr_tuple_list = [
                    (vcf_altpl_list[0][1], vcf_altpl_list[0][0])
                ]

        else:
            group_tuple_list = vcf_grtpl_list
            alstr_tuple_list = vcf_altpl_list
            member_dict = vcf_mem_dict

        ### print("reverse_group={}".format(reverse_group))

        # 固定グループ名と、仮グループ名を対応させて返す
        return \
            skip, \
            group_tuple_list, \
            alstr_tuple_list, \
            member_dict


    def judge_fixed_group_segregation(self,
        vcf_grtpl_list, vcf_mem_dict, distin_gdct):
        '''
        '''

        skip = False
        reverse_group = False     # group corespondance

        #### print()
        #### print("in judge_fixed_group_segregation, {}".format(
        ####     vcf_grtpl_list))

        #### print("--------------------------------")

        for grp_tuple in vcf_grtpl_list:

            #### print("{}".format(vcf_grtpl_list))
            #### print("{}".format(grp_tuple))
            #### print("a_sample: {}".format(glv.conf.a_sample))
            #### print("b_sample: {}".format(glv.conf.b_sample))

            fix_sn_nds = [
                distin_gdct['group01_sn_nds'][0],
                distin_gdct['group01_sn_nds'][1], 
            ]

            # vcf sample name ndarray list
            vcf_sn_nds = list()

            for grp in grp_tuple:
                # grp=a
                #print("grp={}".format(grp))
                vcf_sn_nd = \
                    np.zeros(glv.conf.vcf_sample_cnt, dtype=np.int64)
                # vcf_sn_nd=[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
                vcf_sn_list = vcf_mem_dict[grp]
                # vcf_sn_list=['Ginganoshizuku', 'Hitomebore']
                #### print("vcf_sn_list={}".format(vcf_sn_list))

                for sn in vcf_sn_list:
                    sn_idx = \
                        int(glv.conf.vcf_sample_nickname_dict[sn]['no'])
                    # sn:Ginganoshizuku=1
                    # sn:Hitomebore=0
                    #print("sn:{}={}".format(sn, sn_idx))
                    vcf_sn_nd[sn_idx] = 1
                # vcf_sn_nd=[1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
                #print("vcf_sn_nd={}".format(vcf_sn_nd))
                vcf_sn_nds.append(vcf_sn_nd)

            # 0は、違いがない、ということで、SKIP = False
            # 0以外は、違いがあるということで、SKIP = True
            ret = 0

            #### #print("--------------------------------")
            #### print(" fix {}, {}".format(fix_sn_nds[0], fix_sn_nds[1]))
            #### print(" vcf {}, {}".format(vcf_sn_nds[0], vcf_sn_nds[1]))

            # 0と0を比較
            #### print("1({}) {}, {}".format(
            ####     self.compare_nds(fix_sn_nds[0], vcf_sn_nds[0]),
            ####     fix_sn_nds[0], vcf_sn_nds[0]))

            if 0 == self.compare_nds(fix_sn_nds[0], vcf_sn_nds[0]):
                # 0と0が同じなら、
                # 1と1の結果が最終結果
                ret = self.compare_nds(fix_sn_nds[1], vcf_sn_nds[1])

                #### print("2({}) {}, {}".format(
                ####     self.compare_nds(fix_sn_nds[1], vcf_sn_nds[1]),
                ####     fix_sn_nds[1], vcf_sn_nds[1]))

            elif 0 == self.compare_nds(fix_sn_nds[0], vcf_sn_nds[1]):
                reverse_group = True

                # 0と0が違う時、0と1を比べて
                # 同じなら、
                #### print("3({}) {}, {}".format(
                ####     self.compare_nds(fix_sn_nds[0], vcf_sn_nds[1]),
                ####     fix_sn_nds[0], vcf_sn_nds[1]))

                # 1と0を比べる
                ret = self.compare_nds(fix_sn_nds[1], vcf_sn_nds[0])

                #### print("4({}) {}, {}".format(
                ####     self.compare_nds(fix_sn_nds[1], vcf_sn_nds[0]),
                ####     fix_sn_nds[1], vcf_sn_nds[0]))

            else:
                #違うなら
                #### print("5({}) {}, {}".format(
                ####     self.compare_nds(fix_sn_nds[0], vcf_sn_nds[1]),
                ####     fix_sn_nds[0], vcf_sn_nds[1]))
                ret = 1

            #### print("{} ------------------------------".format(ret))
            
            if ret != 0:
                skip = True

        return skip, reverse_group


    def compare_nds(self, fix_nd, vcf_nd):

        # if 0, fix_nd was included in vcf_nd
        res = np.count_nonzero(((fix_nd | vcf_nd) ^ vcf_nd))
        return res


    def alstr_combination(self,
        all_target_samples, alstr_list, uq_alstr_ndary):
        '''
        '''

        # return for vcf data
        vcf_grtpl_list = list()
        vcf_altpl_list = list()
        vcf_mem_dict = dict()
        # a dictionary that determines the group name from alstr
        vcf_algnm_dict = dict()

        group_cnt = len(uq_alstr_ndary)

        # アリルストリングのtupleの組み合わせを作る
        # make a combination of unique alstr tuple(uq_alstr_ndary)
        # [('00', '01'), ('00', '11'), ('01', '11')]
        vcf_altpl_list = list(itertools.combinations(uq_alstr_ndary, 2))

        # グループに名前をつける。indexで配列より名前を持ってくる
        # name the group, for 2 groups from 'a', for 3 groups, from 'c'
        # もし、グループが２つしかなかったら、a,b
        # ３つ以上あるものは、cから始まる
        idx_pad = 0
        if group_cnt > 2:
            idx_pad = 2

        # ['00', '01', '11']
        # ２つ以上のグループについて、グループごとに(idxを追いながら）
        for idx, alstr in enumerate(uq_alstr_ndary):
            # 1) alstr_gname_dict {'00': 'c'}
            group_name = glv.GROUP_NAME[idx + idx_pad]
            vcf_algnm_dict[alstr] = group_name
            # 2) gname_member_dict
            # From the original array of samples (alstr_ndary),
            # get the index of the currently focused alstr.
            mem_idxes = [i for i, v in enumerate(alstr_list) if v == alstr]
            # alstr '00'
            # alstr_list ['01', '00', '00', '11']
            # mem_idxes [1, 2]

            # ここで、idxが得られている。
            vcf_mem_dict[vcf_algnm_dict[alstr]] = list()

            # リスト内包表記
            [vcf_mem_dict[vcf_algnm_dict[alstr]].append(
                all_target_samples[midx]) for midx in mem_idxes]

        # alstr_tuple_list
        for alstr_tuple in vcf_altpl_list:
            group_tuple = \
                (vcf_algnm_dict[alstr_tuple[0]],
                vcf_algnm_dict[alstr_tuple[1]])
            vcf_grtpl_list.append(group_tuple)

        return vcf_grtpl_list, vcf_altpl_list, vcf_mem_dict, vcf_algnm_dict


    def get_unique_alstr(self, all_target_samples, record, distin_gdct):
        '''
        '''

        # 対象サンプルのアリルストリングを取得 listにて
        # make alstr ndarray from sample_name list
        # ['01', '00', '00', '11']
        alstr_list = [AlleleSelect.record_call_for_sample(
            record, sn) for sn in all_target_samples]

        # ユニークなアリルストリングを得る ndarray
        # pick unique items array(['00' '01' '11'], dtype='<U2')
        uq_alstr_ndary = np.unique(alstr_list)

        # .. のNAは除く
        # --------------------------------------------------------
        # .. indicates no alignment status. remove it
        # --------------------------------------------------------
        uq_alstr_ndary = uq_alstr_ndary[uq_alstr_ndary != ".."]

        return alstr_list, uq_alstr_ndary


