# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import errno
import time
import pprint
import itertools

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
log = LogConf.open_log(__name__)

import pandas as pd

from vprimer.inout_primer3 import InoutPrimer3

class ChkHDimer(object):

    def __init__(self):

        pass


    def filter_and_check_hetero_dimer(self):

        # If pick_mode is not SNP, it does't need to do this
        if glv.conf.pick_mode != glv.MODE_SNP:
            return

        proc_name = "snpfilter"
        # stop or continue ---------------------------------
        ret_status = utl.decide_action_stop(proc_name)

        if ret_status == glv.progress_stop:
            log.info(utl.progress_message(ret_status, proc_name))
            sys.exit(1)

        if ret_status == glv.progress_gothrough:
            log.info(utl.progress_message(ret_status, proc_name))
        else:
            self.snp_filtering(proc_name)
        # --------------------------------------------------


        proc_name = "chkhdimer"
        # stop or continue ---------------------------------
        ret_status = utl.decide_action_stop(proc_name)

        if ret_status == glv.progress_stop:
            log.info(utl.progress_message(ret_status, proc_name))
            sys.exit(1)

        if ret_status == glv.progress_gothrough:
            log.info(utl.progress_message(ret_status, proc_name))
            return
        # --------------------------------------------------

        self.confirm_hetero_dimer(proc_name)


    def confirm_hetero_dimer(self, proc_name):
        '''
        '''
        log.info("-------------------------------")
        log.info("Start processing {}\n".format(proc_name))

        # conf_distin.py
        # set_distinguish_groups_list()
        # distin_gdct['hdimer_seq'] = list()

        proc_cnt = 0
        for distin_gdct, reg in glv.conf.gdct_reg_list:
            proc_cnt += 1
            # prepare file name
            read_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']
            # 
            df_snpfil = pd.read_csv(
                read_snpfilter, sep='\t', dtype=str, header=0, index_col=None)

            # PRIMER_LEFT_0_SEQUENCE
            lseq_list = df_snpfil['PRIMER_LEFT_0_SEQUENCE'].values.tolist()
            # uniq
            lseq_list = list(set(lseq_list))
            distin_gdct['hdimer_seq'] += lseq_list
            
            # PRIMER_RIGHT_0_SEQUENCE
            rseq_list = df_snpfil['PRIMER_RIGHT_0_SEQUENCE'].values.tolist()
            # uniq
            rseq_list = list(set(rseq_list))
            distin_gdct['hdimer_seq'] += rseq_list

        # distin_gdct['hdimer_seq']
        distin_cnt = 0
        for distin_gdct in glv.conf.distinguish_groups_list:
            distin_cnt += 1

            # 重複を削る
            ttl_org_cnt = len(distin_gdct['hdimer_seq'])
            distin_gdct['hdimer_seq'] = list(
                set(distin_gdct['hdimer_seq']))
            ttl_unq_cnt = len(distin_gdct['hdimer_seq'])

            log.info("total_cnt={}, uniq_cnt={}".format(
                ttl_org_cnt, ttl_unq_cnt))

            # count combined cnt
            cmb_cnt = self.cmb(ttl_unq_cnt, 2)
            log.info("all combination cnt={}".format(cmb_cnt))

            # 全組み合わせのリスト
            primer_cmb_list = list(itertools.combinations(
                distin_gdct['hdimer_seq'], 2))

            # コンビごとにチェック
            cnt = 0 
            for cmb_tuple in primer_cmb_list:
                rem = cnt % 10000
                if rem == 0:
                    log.info("check start {}/{}".format(cnt, cmb_cnt))
                cnt += 1

                hetero_dimer_ok = InoutPrimer3.check_all_primer_hetero_dimer(
                    cmb_tuple[0], cmb_tuple[1])

                if hetero_dimer_ok != True: 
                    distin_gdct['hdimer_ng'] += [
                        cmb_tuple[0], cmb_tuple[1]]

                    print("hetero dimer found {}".format(
                        distin_gdct['hdimer_ng']))

                    #print("{}\t{}\t{}".format(
                    #    hetero_dimer_ok, cmb_tuple[0], cmb_tuple[1]))

        # write
        proc_cnt = 0
        for distin_gdct, reg in glv.conf.gdct_reg_list:
            proc_cnt += 1

            # prepare file name
            read_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']
            write_chkhdimer = distin_gdct['chkhdimer']['fn'][reg]['out_path']

            # read file as str "00"
            df_snpfilter = pd.read_csv(
                read_snpfilter, sep='\t', dtype=str, header=0, index_col=None)

            # 入れてはいけないリスト1 [T T F F F] ^[F F T T T]
            # 逆転させて、T T = T
            left_ng_bool_idx = df_snpfilter['PRIMER_LEFT_0_SEQUENCE'].isin(
                distin_gdct['hdimer_ng'])
            # 入れてはいけないリスト2 [F F T F F] ^[T T F T T]
            # [F F F T T]
            right_ng_bool_idx = df_snpfilter['PRIMER_RIGHT_0_SEQUENCE'].isin(
                distin_gdct['hdimer_ng'])

            picked_df = df_snpfilter[
                ~left_ng_bool_idx & ~right_ng_bool_idx ]

            utl.save_to_tmpfile(write_chkhdimer)

            picked_df.to_csv(write_chkhdimer, sep = '\t',
                index = None, encoding='utf-8')


    def snp_filtering(self, proc_name):
        '''
        '''
        log.info("-------------------------------")
        log.info("Start processing {}\n".format(proc_name))

        gcrange = glv.conf.snp_filter_gcrange
        gc_min = glv.conf.snp_filter_gc_min
        gc_max = glv.conf.snp_filter_gc_max
        interval = glv.conf.snp_filter_interval

        # 1) filter and write to file
        proc_cnt = 0
        for distin_gdct, reg in glv.conf.gdct_reg_list:

            proc_cnt += 1
            # prepare file name
            read_formpass = distin_gdct['formpass']['fn'][reg]['out_path']
            write_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']

            # read file as str "00"
            df_formpass = pd.read_csv(
                read_formpass, sep='\t', dtype=str, header=0, index_col=None)
            # astype
            df_formpass = df_formpass.astype(
                {'pos': 'int', 'product_gc_contents': 'float'})

            # pick data by gc_contents
            if gcrange != "":
                q = "{} >= {} and {} <= {}".format(
                    "product_gc_contents", gc_min,
                    "product_gc_contents", gc_max)
                # product_gc_contents
                df_gc = df_formpass.query(q)
            else:
                df_gc = df_formpass

            # calc interval
            if interval != 0:
                # pos列を抽出
                pos_list = df_gc['pos'].values.tolist()
                # get_interval_list
                interval_list = self.get_interval_list(pos_list, interval)
                # pick df from interval_list
                picked_bool_idx = df_gc['pos'].isin(interval_list)
                picked_df = df_gc[picked_bool_idx]
                # filter condition and result
            else:
                picked_df = df_gc

            log.info("filtered condition: gcrange={}, interval={}".format(
                gcrange, interval))
            log.info("total record cnt {}".format(len(picked_df)))

            # save
            utl.save_to_tmpfile(write_snpfilter)
            log.info("Data for snp_filtered primers were output to {}".format(
                write_snpfilter))
            picked_df.to_csv(write_snpfilter, sep = '\t',
                index = None, encoding='utf-8')


    def get_interval_list(self, pos_list, interval):

        interval_list = list()

        # The first and last pos are reserved.
        top_pos = 0
        bottom_pos = 0

        next_border = 0

        '''
        1 origin < 0
        '''
        for pos in pos_list:

            if top_pos == 0:
                top_pos = pos
                next_border = self.get_next_border(pos, interval)
                interval_list.append(pos)
                continue

            # 次のしきい値を越える前はcontinue
            if pos <= next_border:
                #print("underpos={}, next_border={}".format(
                #    pos, next_border))
                continue

            #print("pos={}".format(pos))
            next_border = self.get_next_border(pos, interval)
            interval_list.append(pos)

            bottom_pos = pos

        if not bottom_pos in interval_list:
            interval_list.append(bottom_pos)

        pick_cnt = len(interval_list)

        # check if bottom same as last pos
        # pick_cnt += 1
        #print("----")
        #print("top_pos={}".format(top_pos))
        #print("pos_total={}".format(pos_total))
        #print("pick_cnt={}".format(pick_cnt))
        #print("bottom_pos={}".format(bottom_pos))
        #print()
        #print(interval_list)

        return interval_list


    def get_next_border(self, pos, interval):

        next_border = 0

        quotient = pos / interval
        q_int = int(quotient)

        #print()
        #print("pos={}".format(pos))
        #print("interval={}".format(interval))
        #print("quotient={}".format(quotient))
        #print("q_int={}".format(q_int))

        if q_int < quotient:
            next_border = (q_int + 1) * interval
        else:
            next_border = q_int * interval

        #print("next_border={}".format(next_border))

        return next_border


    def cmb(self, n, r):
        ''' https://qiita.com/derodero24/items/91b6468e66923a87f39f
        '''

        # n=824316, r=2
        # 339,748,021,770 3千億

        if n - r < r: r = n - r
        if r == 0: return 1
        if r == 1: return n

        numerator = [n - r + k + 1 for k in range(r)]
        denominator = [k + 1 for k in range(r)]

        for p in range(2,r+1):
            pivot = denominator[p - 1]
            if pivot > 1:
                offset = (n - r) % p
                for k in range(p-1,r,p):
                    numerator[k - offset] /= pivot
                    denominator[k] /= pivot

        result = 1
        for k in range(r):
            if numerator[k] > 1:
                result *= int(numerator[k])

        return result

