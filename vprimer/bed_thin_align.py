# -*- coding: utf-8 -*-

import sys
import re
import time
import datetime

from pathlib import Path
import pandas as pd

import logging
log = logging.getLogger(__name__)

import vprimer.glv as glv
import vprimer.utils as utl

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import subprocess as sbp

import pprint

# for md5
import os
import glob
import hashlib


class BedThinAlign(object):

    def __init__(self):

        self.require_bam_bed_list = list()

        ###### self.concurrent_mode = "thread"
        self.concurrent_mode = "process"
        if glv.conf.parallel_ok == False:
            self.concurrent_mode = "serial"

        self.open_pos = True        # bedのposition法を、open, closeにする
        self.valid_print = True     # depthが無問題の部分も出力する

        # ユーザ指定のbam_table
        self.bam_table_dict = dict()

        # glv.conf.bed_dir_path
        self.bed_dir_path = glv.conf.bed_dir_path

        # for command line
        self.command            = Path(sys.argv[0]).name
        self.na_com = "Not assigned, created by {}".format(self.command)

        # for vprimer inline
        self.ref = glv.conf.user_ref_path
        self.vcf = glv.conf.user_vcf_path

        #self.now_datetime       = utl.datetime_str()

        # bed_thal
        # 解析で指定されたbam_bedの情報
        self.bta_req_dict = dict()

        self.uname = "{}, {}".format(os.uname()[0], os.uname()[2])
        self.hostname = os.uname()[1]


        # header for bam_bed
        self.h_bbed = {
            'vcf_sample':       'vcf_sample',
            'bam_bed_name':     'bam_bed_name',
            'date':             'date',
            'min_max_depth':    'min_max_depth',

            'associated_bam':   'associated_bam',
            'user_bam_path':    'user_bam_path',
            'bam_mtime':        'bam_mtime',
            'bam_size':         'bam_size',
            'bam_md5':          'bam_md5',

            'vcf':              'vcf',
            'ref':              'ref',

            'uname':            'uname',
            'hostname':         'hostname',
            #-----------------------------------

            'genome_total_len':             'genome_total_len',
            'width_coverage_nozero':        'width_coverage_nozero',
            'width_coverage_nozero_rate':   'width_coverage_nozero_rate',

            'width_coverage_valid':         'width_coverage_valid',
            'width_coverage_valid_rate':    'width_coverage_valid_rate',

            'width_coverage_thin':          'width_coverage_thin',
            'width_coverage_thin_rate':     'width_coverage_thin_rate',

            'width_coverage_zero':          'width_coverage_zero',
            'width_coverage_thick':         'width_coverage_thick',

            #-----------------------------------

            'depth_valid_average':   'depth_valid_average',
            'depth_thin_average':    'depth_thin_average',

            'depth_zero':       'depth_zero',
            'depth_thin':       'depth_thin',
            'depth_thick':      'depth_thick',
            'depth_valid':      'depth_valid',
            'depth_total':      'depth_total',

            #-----------------------------------
            'bed_thal_valid_length':    'bed_thal_valid_length',
            'bed_thal_valid_rate':      'bed_thal_valid_rate',
        }

        # header for bed_thal
        self.h_bthl = {
            'bam_bed_path':             'bam_bed_path',
            #-----------------------------------------------
            'groups_id':                'groups_id',
            'sorted_samples':           'sorted_samples',
            'bta_min_max_depth':        'bta_min_max_depth',
        }

        self.user_bam_table_path = glv.conf.user_bam_table_path
        self.min_depth = glv.conf.min_depth
        self.max_depth = glv.conf.max_depth
        self.parallel_cnt = glv.conf.parallel_full_thread
        # always true
        #self.dont_show_valid = True
        self.dont_show_valid = False

        self.bta_min_max_depth = glv.conf.min_max_depth

        # for bam stat
        self.count_dict = dict()


    #~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
    # 1/6. make_bam_table_dict, from conf_bed_file.py 
    def make_bam_table_dict(self):
        '''
        '''

        log.info("start 1/6 bta.make_bam_table_dict")

        log.info("read {}".format(self.user_bam_table_path))
        with self.user_bam_table_path.open('r', encoding='utf-8') as f:

            # iterator
            for r_liner in f:
                r_line = r_liner.strip()    # ct, ws

                # remove header # and comment
                if r_line.startswith('#') or r_line == '':
                    continue

                r_line = utl.strip_hash_comment(r_line)
                vcf_sample, associated_bam = r_line.split()

                # これは、本来外部からやってくる
                ### sorted_samples_list.append(vcf_sample)

                # init
                user_bam_path = "-"              # ユーザ指定bamのPath
                bam_bed_path = "-"          # 変換後のbam_bedのPath
                bta_min_max_depth = "-"

                if associated_bam != "-":
                    # user_bam_path
                    user_bam_path = Path(associated_bam).resolve()
                    bta_min_max_depth = self.bta_min_max_depth

                    # user_bam_file_path existance check
                    if not user_bam_path.exists():
                        er = "bam_file not found "
                        er += "{}.".format(associated_bam)
                        log.error(er)
                        sys.exit(1)

                    # make bed file name and get pathlib
                    bam_bed_path = self.make_name_bam_bed_path(
                        user_bam_path, self.min_depth, self.max_depth)

                # dictionary
                self.bam_table_dict[vcf_sample] = {
                    'vcf_sample': vcf_sample,
                    'associated_bam': associated_bam,
                    'user_bam_path': user_bam_path,
                    #'slink_bam_path': bam_path,
                    'min_max_depth': bta_min_max_depth,
                    'bam_bed_path': bam_bed_path,
                }

        vcf_sample_cnt = len(self.bam_table_dict.keys())

        # - も含みで、全エントリを辞書化

        # this is required vcf_samples
        #sorted_samples_str = ','.join(sorted(set(sorted_samples_list)))
        #return sorted_samples_str

    #~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
    # 2/6. get_require_bam_bed_list, from conf_bed_file.py 
    def get_require_bam_bed_list(self, sorted_samples_str):
        '''
        bam_bed_dict = {
            'bam_num': bam_num,
            'ttl_num': bam_num,
            'vcf_sample': vcf_sample,
            'associated_bam': associated_bam,
            'user_bam_path': user_bam_path,
            #'bam_path': slink_bam_path,
            'bam_bed_path': bam_bed_path,
            'min_depth': min_depth,
            'max_depth': max_depth,
        }
        '''

        log.info("start 2/6 bta.get_require_bam_bed_list")

        # リストに変換
        sorted_samples_list = sorted_samples_str.split(',')
        # bam_bed の要作成リストの構築
        bam_num = 1
        # num of not '-'
        bam_exist = 0

        # 調査対象の、sorted_samples_list にて
        for vcf_sample in sorted_samples_list:

            associated_bam = \
                self.bam_table_dict[vcf_sample]['associated_bam']

            # it doesn't have a bam file
            if associated_bam == '-':
                continue
            else:
                bam_exist += 1

            user_bam_path = \
                self.bam_table_dict[vcf_sample]['user_bam_path']
            #slink_bam_path = \
            #     self.bam_table_dict[vcf_sample]['slink_bam_path']
            bam_bed_path = self.bam_table_dict[vcf_sample]['bam_bed_path']

            # すでに、指定のファイル名のbedがあれば、何もしない
            if bam_bed_path.exists():
                log.info("bam_bed {} already exist.".format(bam_bed_path))
                continue

            #----------------------------------------------
            bam_bed_dict = {
                'bam_num': bam_num,
                'ttl_num': 0,
                'vcf_sample': vcf_sample,
                'associated_bam': associated_bam,
                'user_bam_path': user_bam_path,
                #'bam_path': slink_bam_path,
                'bam_bed_path': bam_bed_path,
                'min_depth': self.min_depth,
                'max_depth': self.max_depth,
            }
            self.require_bam_bed_list.append(bam_bed_dict)
            bam_num += 1

        if bam_exist == 0:
            # all the bam missed
            err = "There are {} samples for analyse: {}, ".format(
                len(sorted_samples_list), sorted_samples_str)
            err += "but no bam is specified (-). "
            err += "Please check bam_table file. "
            err += "exit."
            log.info(err)
            sys.exit(1)

        # set total num
        self.set_total_num(self.require_bam_bed_list)


    #~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
    # 3/6. build_bam_bed, from conf_bed_file.py 
    def build_bam_bed(self):
        '''
        '''

        log.info("start 3/6 bta.build_bam_bed")

        reqcnt = len(self.require_bam_bed_list)
        #self.parallel_cnt
        if reqcnt == 0:
            mes = "It seems that all the bam_bed file has already "
            mes += "been prepared."
            mes += "\n"
            log.info(mes)
            return

        # 処理開始
        start = utl.get_start_time()

        mes = "start build_bam_bed, {} bam_bed file will create.".format(
            len(self.require_bam_bed_list))
        log.info(mes)

        para_cnt = self.parallel_cnt
        if para_cnt > reqcnt:
            para_cnt = reqcnt

        # bed作成は、threadではなく processで
        if self.concurrent_mode == "process":

            mes = "Parallelize in process mode. "
            mes += "{} samples are parallelized from {} totals.".format(
                para_cnt, reqcnt)
            log.info(mes)

            with ProcessPoolExecutor(self.parallel_cnt) as e:
                ret = e.map(
                    self.make_bam_bed_file,
                    self.require_bam_bed_list)

        #elif self.concurrent_mode == "thread":
        #
        #   mes = "Parallelize in thread mode. "
        #   mes += "{} samples are parallelized from {} totals.".format(
        #       para_cnt, reqcnt)
        #   log.info(mes)

        #   with ThreadPoolExecutor(self.parallel_cnt) as e:
        #       ret = e.map(
        #           self.make_bam_bed_file,
        #           self.require_bam_bed_list)

        else:

            mes = "No parallelization mode. "
            mes += "Total {} serial executions.".format(reqcnt)
            log.info(mes)

            for bam_bed_dict in self.require_bam_bed_list:
                self.make_bam_bed_file(bam_bed_dict)

        log.info("finished build_bam_bed, {}".format(
            utl.elapse_str(start)))


    #~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
    # 4/6. pick_provenance_with_depth, from conf_bed_file.py 
    def pick_provenance_with_depth(self, sorted_samples_str, groups_id):
        '''
        '''

        log.info("start 4/6 bta.pick_provenance_with_depth")

        # リストにする
        sorted_samples_list = sorted_samples_str.split(',')
        #print(sorted_samples_list)

        # it's one dict
        self.bta_req_dict = {
            'sorted_samples': sorted_samples_str,
            'groups_id': groups_id,
            'bta_min_max_depth': self.bta_min_max_depth,
            'bam_bed_path_list': list(),
            'prov_info': dict()
        }

        # for each vcf_sample
        for vcf_sample in sorted_samples_list:

            #print(vcf_sample)

            user_bam_path = self.bam_table_dict[vcf_sample]['user_bam_path']
            #print(user_bam_path)
            min_max_depth = self.bam_table_dict[vcf_sample]['min_max_depth']
            #print(min_max_depth)
            bam_bed_path = self.bam_table_dict[vcf_sample]['bam_bed_path']
            #print(bam_bed_path)

            # dict: key => vcf_sample
            prov_info = {
                vcf_sample: {
                    'user_bam_path': user_bam_path,
                    'bam_md5': "",
                    'min_max_depth': min_max_depth,
                    'bam_bed_path': bam_bed_path,
                    'width_coverage_valid_rate': 0.00,
                    'depth_valid_av': 0.00,
                }
            }

            # read bam_hed_header
            with bam_bed_path.open('r', encoding='utf-8') as f:
                for r_liner in f:
                    r_line = r_liner.strip()    # ct, ws

                    # continue if ^#
                    if not r_line.startswith('#'):
                        continue

                    if not '\t' in r_line:
                        continue

                    # # and space, contine
                    r_line = r_line.replace('#', '').strip()
                    if r_line == '':
                        continue

                    # read header
                    # # vcf_sample    Ginganoshizuku
                    #print(r_line)

                    key, val = r_line.split('\t')

                    #print("key={}, val={}".format(key, val))
                    if key == 'bam_md5' or \
                        key == self.h_bbed['depth_valid_average'] or \
                        key == self.h_bbed['width_coverage_valid_rate']:
                        prov_info[vcf_sample][key] = val

            # add tha bam_bed info to a bed_thal file
            self.bta_req_dict['bam_bed_path_list'].append(
                bam_bed_path)
            self.bta_req_dict['prov_info'].update(prov_info)

        mes = "finished pick_provenance_with_depth."
        log.info(mes)


    #~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
    # 5/6. find_suitable_bed_thal, from conf_bed_file.py 
    def find_suitable_bed_thal(self):
        '''
        デプスが同一
            ユーザ指定サンプル群の中で、bamがあるもの。
            bed_thalのbam構成とデプスが同一構成のもの
        
        '''

        log.info("start 5/6 bta.find_suitable_bed_thal")

        found_bed_thal = False
        bed_thal_path = ""

        bta_bed_cnt = 0
        # 今度は、bed_thal を１つづつ探す
        for fpath in self.bed_dir_path.iterdir():

            # glv.bed_thal_ext       = ".bta.bed"
            if str(fpath).endswith(glv.bed_thal_ext):
                bta_bed_cnt += 1

                # .bta.bed ファイルから来歴を読み出す
                bta_prov_dict = self.read_bta_provenance_info(fpath)

                '''
                bta_prov_dict = {
                    'sorted_samples': "",
                    'groups_id': "",
                    'bta_min_max_depth': "",
                    'prov_info': dict()
                }
                '''

                # 来歴のチェック
                # 既存の .bta.bed の来歴と、今作ろうとしている サンプルを
                # 比較して、同じものならば、既存のファイルを用いる
                found_bed_thal = self.check_bta_provenance(bta_prov_dict)

                if found_bed_thal:
                    bed_thal_path = Path(fpath).resolve()
                    break

        if not found_bed_thal:
            bed_thal_path = self.make_name_bed_thal_path(
                self.min_depth, self.max_depth)

        return found_bed_thal, bed_thal_path


    #~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
    # 6/6. build_bed_thal, from conf_bed_file.py 
    def build_bed_thal(self, new_bed_thal_path):
        '''
        '''

        log.info("start 6/6 bta.build_bed_thal")

        # 使用する bam_bed のリスト pathlibから、fullpath textのリストへ
        bam_bed_path_list = list(map(str,
            self.bta_req_dict['bam_bed_path_list']))

        # awk, sort処理後の、書き出し用bedファイル
        # bed_thal_sort_ext
        new_bed_thal_sort_path = \
            Path(str(new_bed_thal_path) + glv.bed_thal_sort_ext).resolve()

        # make_header
        header_bed_thal_r = self.ident_bed_thal_header()

        #    groups, sorted_samples, bed_path_list,)
        # (1) awk: remove line that include "(valid)", remain only $1~$3
        '''
        # [header]
        chr01   0       1000    Z
        chr01   1000    1005    thin
        chr01   1005    29758   (valid)
        chr01   29758   29761   thin
        '''


        cmd_awk = ['awk']
        cmd_awk += ['-F', '\\t']
        cmd_awk += \
            ['$1!~/^#/ && $4!~/valid/ {printf("%s\\t%s\\t%s\\n",$1,$2,$3)}']
        # argument: bam_bed files
        cmd_awk += bam_bed_path_list

        # (2) | sort: by first column "chrom" and second column position
        cmd_sort = ['sort']
        cmd_sort += ['-k', '1,1', '-k', '2,2n']

        # (3) cmd_awk | cmd_sort > file
        # cmd_redirect = ['>']
        # cmd_redirect += ["{}".format(bed_thal_tmp_path)]
        with new_bed_thal_sort_path.open('w', encoding='utf-8') as f:

            # この内部でのエラーをピックアップできるか
            # awk - awka にすると、エラーで止まる。
            #p_awk = sbp.Popen(cmd_awk, stdout=sbp.PIPE, stderr=sbp.PIPE)
            #print("(2) cmd_awk and cmd_sort")

            p_awk = sbp.Popen(cmd_awk, stdout=sbp.PIPE)
            p_sort = sbp.Popen(cmd_sort,
                stdin=p_awk.stdout, stdout=f, stderr=sbp.PIPE)
            p_awk.stdout.close()  # SIGPIPE if p2 exits.
            # bed ファイルにエラーがあった場合
            result, err = p_sort.communicate()
            #print("(3) cmd_awk and cmd_sort end")
            # エラーは確認しない。


        #print("result={}, err={}".format(result, err))
        #sys.exit(1)

        #proc = sbp.Popen(cmd1, stdout=sbp.PIPE, stderr=sbp.PIPE, text=True)
        #result = proc.communicate()

        # (4) bedtools merge
        cmd_bedtools = ['bedtools']
        cmd_bedtools += ['merge']
        cmd_bedtools += ['-nobuf']
        cmd_bedtools += ['-i', '{}'.format(new_bed_thal_sort_path)]

        new_bed_thal_merge_path = \
            Path(str(new_bed_thal_path) + glv.bed_thal_merge_ext).resolve()

        # (5) cmd_bedtools > file
        # エラーをキャプチャして、logに残す
        with new_bed_thal_merge_path.open('w', encoding='utf-8') as f:
            #print("(4) cmd_bedtools")
            self.print_single(f, header_bed_thal_r)

            p3 = sbp.Popen(cmd_bedtools, stdout=f, stderr=sbp.PIPE, text=True)
            result, err = p3.communicate()
            #print("(5) cmd_bedtools end")

        if err != "":
            log.error("bedtools says, {}".format(err))
            log.error("It is serious error. exit.")
            sys.exit(1)

        # 再度読み込んで、statを作る
        valid_statline = self.get_bed_thal_valid_stat(new_bed_thal_merge_path)

        log.info("\n{}".format(valid_statline))

        # statを追加する
        with new_bed_thal_merge_path.open('a', encoding='utf-8') as f:
            f.write(valid_statline)

        # 終了したら、tmpを消す
        new_bed_thal_sort_path.unlink()
        # 終了したら、mvする。
        new_bed_thal_merge_path.rename(new_bed_thal_path)

        log.info("finished, creating {}".format(new_bed_thal_path.name))


    ######################################################################
    # sub-routine
    def make_name_bam_bed_path(self, user_bam_path, min_depth, max_depth):
        '''
        '''
        # m8_x300.bb.bed
        bam_bed_ext = self.get_bed_ext(glv.bam_bed_ext, min_depth, max_depth)
        bam_bed_path = Path("{}{}".format(
            self.bed_dir_path / user_bam_path.name, bam_bed_ext)).resolve()
        return bam_bed_path


    def make_name_bed_thal_path(self, min_depth, max_depth):
        '''
        '''

        # m8_x300.bb.bed
        bed_thal_ext = self.get_bed_ext(
            glv.bed_thal_ext, min_depth, max_depth)

        # now
        dt = utl.datetime_str()

        #
        #print("make_name_bed_thal_path")
        #sys.exit(1)

        bed_thal = "{}/{}{}{}".format(
            self.bed_dir_path,
            glv.bed_thal_prefix,
            dt,
            bed_thal_ext)

        # fullpath: pathlib
        new_bed_thal_path = Path(bed_thal).resolve()

        return new_bed_thal_path


    def get_bed_ext(self, ext, min_depth, max_depth):
        ''' bedの拡張子は、depthのしきい値、Min, Maxを含んでいる。
        '''

        # glv.min_max_ext        = ".mMin_xMax"
        # glv.bam_bed_ext        = ".bb.bed"
        # glv.bed_thal_ext       = ".bta.bed"

        bed_ext = glv.min_max_ext + ext
        # substitute .mMin_xMax.bed => .m8_x300.bed

        bed_ext = re.sub('Min', str(min_depth), bed_ext)
        bed_ext = re.sub('Max', str(max_depth), bed_ext)

        return bed_ext


    def set_total_num(self, require_list):
        '''
        '''
        # 辞書の中の ttl_num を更新
        ttl_num = len(require_list)
        for d_dict in require_list:
            d_dict['ttl_num'] = ttl_num


    def make_bam_bed_file(self, bam_bed_dict):

        '''
        bam_bed_dict = {
            'bam_num': bam_num,
            'ttl_num': bam_num,
            'vcf_sample': vcf_sample,
            'associated_bam': associated_bam,
            'user_bam_path': user_bam_path,
            #'bam_path': slink_bam_path,
            'bam_bed_path': bam_bed_path,
            'min_depth': min_depth,
            'max_depth': max_depth,
        }
        '''

        bam_num = bam_bed_dict['bam_num']
        ttl_num = bam_bed_dict['ttl_num']
        vcf_sample = bam_bed_dict['vcf_sample']
        associated_bam = bam_bed_dict['associated_bam']
        user_bam_path = bam_bed_dict['user_bam_path']

        #bam_path = bam_bed_dict['bam_path']
        bam_bed_path = bam_bed_dict['bam_bed_path']
        min_depth = bam_bed_dict['min_depth']
        max_depth = bam_bed_dict['max_depth']

        bam_bed_tmp_path = Path(
            str(bam_bed_path) + glv.bam_bed_tmp_ext).resolve()

        # add header to bam_bed
        bam_bed_header = self.ident_bam_bed_header(
            vcf_sample, associated_bam,
            user_bam_path, min_depth, max_depth, bam_bed_path)

        start = utl.get_start_time()
        log.info("start ({}/{}){}".format(
            bam_num, ttl_num, vcf_sample))

        # samtools depth から、depth bed を作成
        with bam_bed_tmp_path.open('w',  encoding='utf-8') as f:

            # bedが作られたときのログ。作成コマンドまでたどり着くこと。
            self.print_single(f, bam_bed_header)
            self.calc_bam_depth(
                f, vcf_sample, associated_bam, user_bam_path,
                min_depth, max_depth, bam_num, ttl_num, start)

        # ここで、書き出せる

        # get chrom total length
        chrom_info_list = glv.conf.get_chrom_info(glv.genome_total_len)
        genome_total_len = chrom_info_list[2]

        # --------------------------------------------------------------
        wdc_total = self.count_dict['width_coverage']['total']

        wdc_valid = self.count_dict['width_coverage'][glv.bed_now_valid]
        wdc_valid_r = self.wdc_rate(wdc_valid, genome_total_len)

        wdc_thin = self.count_dict['width_coverage'][glv.bed_now_thin]
        wdc_thin_r = self.wdc_rate(wdc_thin, genome_total_len)

        wdc_zero = self.count_dict['width_coverage'][glv.bed_now_zero]
        wdc_thick = self.count_dict['width_coverage'][glv.bed_now_thick]

        wdc_nozero = wdc_total- wdc_zero

        # exclude zero
        wdc_nozero_r = self.wdc_rate(wdc_nozero, genome_total_len)

        # --------------------------------------------------------------
        dep_zero = self.count_dict['depth'][glv.bed_now_zero]
        dep_thin = self.count_dict['depth'][glv.bed_now_thin]
        dep_thick = self.count_dict['depth'][glv.bed_now_thick]
        dep_valid = self.count_dict['depth'][glv.bed_now_valid]
        dep_total = self.count_dict['depth']['total']

        dep_valid_ave = self.depth_ave(dep_valid, wdc_valid)
        dep_thin_ave = self.depth_ave(dep_thin, wdc_valid)


        # 追加書き出し
        # here document https://qiita.com/ykhirao/items/c7cba73a3a563be5eac6

        bam_stat = ""
        bam_stat += "# [{}]\n".format(bam_bed_dict['associated_bam'])

        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['genome_total_len'],            genome_total_len)

        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['width_coverage_nozero'],       wdc_nozero)
        bam_stat += "# {}\t{}%\n".format(
            self.h_bbed['width_coverage_nozero_rate'],  wdc_nozero_r)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['width_coverage_valid'],        wdc_valid)
        bam_stat += "# {}\t{}%\n".format(
            self.h_bbed['width_coverage_valid_rate'],   wdc_valid_r)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['width_coverage_thin'],         wdc_thin)
        bam_stat += "# {}\t{}%\n".format(
            self.h_bbed['width_coverage_thin_rate'],    wdc_thin_r)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['width_coverage_zero'],         wdc_zero)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['width_coverage_thick'],        wdc_thick)
        bam_stat += "#\n"

        bam_stat += "# {}\t{}\n".format(
            self.h_bbed['depth_valid_average'],         dep_valid_ave)
        bam_stat += "# {}\t{}\n".format(
            self.h_bbed['depth_thin_average'],          dep_thin_ave)
        bam_stat += "#\n"

        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['depth_total'],                 dep_total)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['depth_valid'],                 dep_valid)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['depth_thin'],                  dep_thin)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['depth_thick'],                 dep_thick)
        bam_stat += "# {}\t{:,}\n".format(
            self.h_bbed['depth_zero'],                  dep_zero)

        # 追加書き込み
        with bam_bed_tmp_path.open('a',  encoding='utf-8') as f:
            self.print_single(f, bam_stat)

        log.info("\n\n{}".format(bam_stat))
        
        # 終了したら、mvする。
        bam_bed_tmp_path.rename(bam_bed_path)

        log.info("finished ({}/{}){}, {}".format(
            bam_num, ttl_num, vcf_sample, utl.elapse_str(start)))


    def wdc_rate(self, area, total):

        rate = 0.00

        if total != 0:
            rate = "{:.2f}".format(100 * area / total)

        return rate


    def depth_ave(self, depth, area):

        ave_dep = 0.00

        if area != 0:
            ave_dep = "{:.2f}".format(depth / area)

        return ave_dep


    def ident_bam_bed_header(self, vcf_sample, associated_bam,
        user_bam_path, min_depth, max_depth, bam_bed_path):

        # ログを見れば、作成の際のコマンドまでたどり着くこと。
        # bamと、bed_thal は全く異なるコンピュータ環境で
        # 生成され使用される可能性があることから、
        # すべての基本となる bam_bedファイルに、bamの詳細な情報を
        # 残す。そして、bed_thal 内部にも、これらの情報を
        # 引き継ぐ

        # bamの情報
        #   vcf_sample
        #   associated_bam(on bam_table)
        #   user_bam_path
        #   ls -l information(size, and date)
        #   bam_md5_value

        date = utl.datetime_str()
        ref = self.ref
        vcf = self.vcf

        bam_mtime = utl.get_path_mtime(user_bam_path)
        bam_size = utl.get_path_size(user_bam_path)

        bam_md5 = self.get_MD5(vcf_sample, user_bam_path)

        # 9 keys
        bam_bed_header = ""

        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['vcf_sample'], vcf_sample)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['bam_bed_name'], bam_bed_path.name)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['date'], date)

        bam_bed_header += "# {}\t{}-{}\n".format(
            self.h_bbed['min_max_depth'], min_depth, max_depth)
        # ref
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['ref'],ref)
        # vcf
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['vcf'],vcf)

        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['associated_bam'], associated_bam)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['user_bam_path'], user_bam_path)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['bam_mtime'], bam_mtime)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['bam_size'], bam_size)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['bam_md5'], bam_md5)

        #key, val = (bam_bed_header.replace('#', '')).strip().split('\t')
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['uname'], self.uname)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['hostname'], self.hostname)

        bam_bed_header += "#\n"

        return bam_bed_header


    def get_MD5(self, vcf_sample, user_bam_path):
        '''
        Calculates md5 hash of a file
        '''
        mes = "calcurate the md5 of bam {} ({}). ".format(
            user_bam_path.name, vcf_sample)
        mes += "It will take some time."
        log.info(mes)

        # We don't use pathlib here because we want to read in chunks.
        # pathlib 0:00:25 open 0:00:17
        hash = hashlib.md5()

        # using os.open
        #print(hash.block_size)  # block_size=64, 131072
        with open(user_bam_path, "rb") as f:
            while True:
                chunk = f.read(2048 * hash.block_size)
                if len(chunk) == 0:
                    break
                hash.update(chunk)

        path_hash = hash.hexdigest()

        mes = "finished calcurating md5 of bam {} ({}) {}".format(
            user_bam_path.name, vcf_sample, path_hash)
        log.info(mes)

        return path_hash


    def calc_bam_depth(self,
        f, vcf_sample, associated_bam, user_bam_path,
        min_depth, max_depth, bam_num, ttl_num, stt):
        '''
        '''

        # init
        self.count_dict = {
            'width_coverage': {
                glv.bed_now_zero: 0,
                glv.bed_now_thin: 0,
                glv.bed_now_valid: 0,
                glv.bed_now_thick: 0,
                'total': 0,
            },
            'depth': {
                glv.bed_now_zero: 0,
                glv.bed_now_thin: 0,
                glv.bed_now_valid: 0,
                glv.bed_now_thick: 0,
                'total': 0,
            }
        }

        # 最初はサンプルのスタート
        start = stt

        # glv
        last_stat = glv.bed_now_nop
        last_chrom = ""

        # always check
        chrom_start = 0
        chrom_end = 0

        # for bed
        bed_close_stt = 1
        bed_open_stt =  1
        bed_close_end = 1

        expected_pos = 1

        # as generate function
        # Code that runs in parallel depending on each argument
        for r_depth_line in self.genfunc_samtools_depth(user_bam_path):

            # 単純に、samtools depth から出力された行を読み込むだけでも、
            # processが早い
            # つまり、今回の samtools depth
            #continue

            depth_line = r_depth_line.strip()
            chrom, pos, depth = depth_line.split()
            # cast to integer
            pos = int(pos)
            depth = int(depth)


            # Get information about changing status
            now_stat, stat_changed = \
                self.get_bed_stat(chrom, pos, depth,
                    min_depth, max_depth, last_stat, last_chrom)

            # count depth by now_stat
            self.count_dict['depth'][now_stat] += depth
            self.count_dict['depth']['total'] += depth

            # next chromosome start
            if stat_changed == glv.bed_stat_init:

                # if end of chromosome,
                if last_chrom != "":
                    # get last_chrom's length
                    chrom_info_list = glv.conf.get_chrom_info(last_chrom)
                    chrom_start = chrom_info_list[0]
                    chrom_end = chrom_info_list[1]

                    # if chromosome end is Z,
                    if (expected_pos - 1) != chrom_end:

                        # found Z area, insert one record
                        # The order of this line is reversed
                        self.print_line(f, glv.bed_now_zero,
                            last_chrom, expected_pos,
                            chrom_end, glv.bed_now_zero)

                        self.print_single(f, "#end {} 1-{}\n".format(
                            last_chrom, chrom_end))

                    mes = "{} finished ({}/{}){}, {}".format(
                        last_chrom, bam_num, ttl_num,
                        vcf_sample, utl.elapse_str(start))
                    log.info(mes)
                    start = utl.get_start_time()

                expected_pos = 1
                # 20230126 mod
                # force to stat_changed
                stat_changed = glv.bed_stat_changed

            # position at depth 0 does not appear in depth
            if expected_pos != pos:

                if last_chrom != "":
                    # write last_stat
                    self.print_line(f, last_stat,
                        last_chrom, bed_close_stt, bed_close_end,
                        last_stat)

                # force to stat_changed
                stat_changed = glv.bed_stat_changed
                # adjust positions to write bed in next step
                bed_close_stt = expected_pos

                bed_close_end = pos - 1
                last_stat = glv.bed_now_zero
                last_chrom = chrom

            # *****************************************************
            if stat_changed == glv.bed_stat_changed:

                # print last start end
                self.print_line(f, last_stat,
                    last_chrom, bed_close_stt, bed_close_end,
                    last_stat)

                # and next bed start from now
                bed_close_stt = pos

            # set next at end
            bed_close_end = pos
            last_stat = now_stat
            last_chrom = chrom
            expected_pos = pos + 1

        # ========================================================

        # final print
        self.print_line(f, last_stat,
            last_chrom, bed_close_stt, bed_close_end, last_stat)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # もし、ここで最後のbpが出てない時は、ZERO

        chrom_info_list = glv.conf.get_chrom_info(last_chrom)
        chrom_start = chrom_info_list[0]
        chrom_end = chrom_info_list[1]

        if bed_close_end != chrom_end:
            # fill by glv.bed_now_zero
            self.print_line(f, glv.bed_now_zero,
                last_chrom, bed_close_end + 1,
                chrom_end, glv.bed_now_zero)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        self.print_single(f, "#end {} 1-{}\n".format(last_chrom, chrom_end))

        # (5.2) chr filal end message
        mes = "{} finished ({}/{}){}, {}".format(
            last_chrom, bam_num, ttl_num,
            vcf_sample, utl.elapse_str(start))
        log.info(mes)


    # ここが、貴重。
    # yield を用いた function が、generator
    def genfunc_samtools_depth(self, bam):
        '''
        subprocessで実行したコマンドの標準出力を非同期で1行ずつ取得します。

        - Popen.stdout.readline() で標準出力をポーリング
        - 標準出力があれば yield で返す
        - Popen.poll() でプロセスの完了を検知
        '''

        # cpuは1で良い
        #cmd = ['samtools', 'depth', bam]
        cmd = ['samtools', 'depth', bam]
        proc = sbp.Popen(cmd, stdout=sbp.PIPE, stderr=sbp.PIPE, text=True)

        # https://qiita.com/megmogmog1965/items/5f95b35539ed6b3cfa17
        while True:
            r_line = proc.stdout.readline()
            if r_line:
                yield r_line

            if not r_line and proc.poll() is not None:
                break


    def get_bed_stat(self, chrom, pos, depth,
        min_depth, max_depth, last_stat, last_chrom):
        '''
        '''

        now_stat        = glv.bed_now_nop
        stat_changed    = glv.bed_stat_nop

        # 1) now_stat by depth
        if depth == 0:
            now_stat = glv.bed_now_zero

        elif depth < min_depth:
            now_stat = glv.bed_now_thin

        elif depth > max_depth:
            now_stat = glv.bed_now_thick

        else:
            now_stat = glv.bed_now_valid

        # 2) stat_changed
        if chrom != last_chrom:
            stat_changed = glv.bed_stat_init

        elif last_stat == now_stat:
            stat_changed = glv.bed_stat_continue

        else:
            stat_changed = glv.bed_stat_changed

        return now_stat, stat_changed


    def print_single(self, f, header_r):
        '''
        '''
        # ヘッダは確実にflushしておこう 書き出しの順番のために
        utl.w_flush_r(f, header_r)


    def print_line(self, f, last_stat,
        chrom, bed_close_stt, bed_close_end, comment=""):
        '''
        '''

        chrom_info_list = glv.conf.get_chrom_info(chrom)
        chrom_end = chrom_info_list[1]

        if self.open_pos:
            bed_open_stt = bed_close_stt - 1
        else:
            bed_open_stt = bed_close_stt

        if chrom_end > 0:
            # chech over position
            #-----------------------------------
            # 長さを超えてる
            if bed_open_stt > chrom_end and  bed_close_end > chrom_end:
                #print("bed_open_stt {}".format(bed_open_stt))
                #print("bed_close_end {}".format(bed_close_end))
                #print("case 1")
                #print("")
                return

            elif bed_open_stt > chrom_end:
                #print("bed_open_stt {}".format(bed_open_stt))
                #print("bed_close_end {}".format(bed_close_end))
                #print("case 2")
                #print("")
                return

            elif bed_close_end > chrom_end:
                #print("bed_open_stt {}".format(bed_open_stt))
                #print("bed_close_end {}".format(bed_close_end))
                #print("case 3")
                #print("")
                bed_close_end = chrom_end
            #-----------------------------------

        # dont show valid line
        if self.dont_show_valid:
            if 'valid' in comment:
                return

        # 15-15のときは、14-15になるから。
        length = bed_close_end - bed_open_stt

        # 直前のもののステータス
        if last_stat != glv.bed_now_valid:
            # no \n
            utl.w_flush(f, "{}\t{}\t{}\t{}_{}".format(
                chrom, bed_open_stt,
                bed_close_end, comment, length))

        else:
            if self.valid_print:
                utl.w_flush(f, "{}\t{}\t{}\t({}_{})".format(
                    chrom, bed_open_stt,
                    bed_close_end, comment, length))

        # summary: for width coverage
        width_coverage = length
        self.count_dict['width_coverage'][comment] += width_coverage
        self.count_dict['width_coverage']['total'] += width_coverage


    def get_bed_thal_valid_stat(self, merge_path):

        bed_thal_stat = ""

        bed_thal_header = ['chrom', 'start', 'end']

        # read bed into pandas
        df_merge = pd.read_csv(merge_path, sep='\t', header=None, comment='#')
        df_merge.columns = bed_thal_header
        df_merge = df_merge.astype({'start': int, 'end': int})

        # thin_lengthを得る
        thin_length = (df_merge['end'] - df_merge['start']).sum()

        # genomeの全長
        chrom_info_list = glv.conf.get_chrom_info(glv.genome_total_len)
        genome_total_len = chrom_info_list[2]

        valid_length = genome_total_len - thin_length

        valid_r = "{:.02f}".format(100*(valid_length / genome_total_len))

        bed_thal_stat = ""
        bed_thal_stat += "#\n"
        bed_thal_stat += "# {}\t{:,}\n".format(
            self.h_bbed['genome_total_len'],        genome_total_len)
        bed_thal_stat += "# {}\t{:,}\n".format(
            self.h_bbed['bed_thal_valid_length'],   valid_length)
        bed_thal_stat += "# {}\t{}%\n".format(
            self.h_bbed['bed_thal_valid_rate'],     valid_r)
        bed_thal_stat += "#\n"


        return bed_thal_stat


    def ident_bed_thal_header(self):
        #, groups, sorted_samples, bed_path_list, min_depth, max_depth):

        date = utl.datetime_str()
        ref = self.ref
        vcf = self.vcf

        #----------------
        sorted_samples = self.bta_req_dict['sorted_samples']
        groups_id = self.bta_req_dict['groups_id']
        bta_min_max_depth = self.bta_req_dict['bta_min_max_depth']

        #
        bta_header = ""
        bta_header += "# {}\t{}\n".format(
            self.h_bbed['date'], date)

        bta_header += "# {}\t{}\n".format(
            self.h_bbed['uname'], self.uname)

        bta_header += "# {}\t{}\n".format(
            self.h_bbed['hostname'], self.hostname)

        bta_header += "# {}\t{}\n".format(
            self.h_bbed['ref'], ref)

        bta_header += "# {}\t{}\n".format(
            self.h_bbed['vcf'], vcf)

        bta_header += "# {}\t{}\n".format(
            self.h_bthl['groups_id'], groups_id)

        bta_header += "# {}\t{}\n".format(
            self.h_bthl['sorted_samples'], sorted_samples)

        bta_header += "# {}\t{}\n".format(
            self.h_bthl['bta_min_max_depth'], 
            bta_min_max_depth)

        #----------------
        for vcf_sample in self.bta_req_dict['prov_info'].keys():

            min_max_depth = \
                self.bta_req_dict['prov_info'][vcf_sample]['min_max_depth']
            bam_bed_path = \
                self.bta_req_dict['prov_info'][vcf_sample]['bam_bed_path']
            bam_md5 = \
                self.bta_req_dict['prov_info'][vcf_sample]['bam_md5']
            user_bam_path = \
                self.bta_req_dict['prov_info'][vcf_sample]['user_bam_path']

            width_coverage_valid_rate = \
                self.bta_req_dict[
                    'prov_info'][vcf_sample][
                        self.h_bbed['width_coverage_valid_rate']]

            depth_valid_average = \
                self.bta_req_dict['prov_info'][vcf_sample][
                    self.h_bbed['depth_valid_average']]


            bta_header += "#\n"
            bta_header += "# {}\t{}\n".format(
                self.h_bbed['vcf_sample'], vcf_sample)

            bta_header += "# {}\t{}\n".format(
                self.h_bbed['min_max_depth'], min_max_depth)

            # *****
            bta_header += "# {}\t{}\n".format(
                self.h_bthl['bam_bed_path'], bam_bed_path)

            bta_header += "# {}\t{}\n".format(
                self.h_bbed['bam_md5'], bam_md5)

            bta_header += "# {}\t{}\n".format(
                self.h_bbed['user_bam_path'], user_bam_path)

            bta_header += "# {}\t{}\n".format(
                self.h_bbed['width_coverage_valid_rate'],
                width_coverage_valid_rate)

            bta_header += "# {}\t{}\n".format(
                self.h_bbed['depth_valid_average'],
                depth_valid_average)

            # add header

        bta_header += "#\n"

        return bta_header


    def read_bta_provenance_info(self, bed_thal_path):
        '''
        '''

        # from pick_provenance_with_depth, cp self.bta_req_dict
        # return this dict
        bta_prov_dict = {
            'sorted_samples': "",
            'groups_id': "",
            'bta_min_max_depth': "",
            #'bam_bed_path_list': list(),
            'prov_info': dict()
        }

        bta_prov_part = False

        # bed_thal_path 
        with bed_thal_path.open('r', encoding='utf-8') as f:
            for r_liner in f:
                r_line = r_liner.strip()    # ct, ws

                if not r_line.startswith('#'):
                    break

                r_line = r_line.replace('#', '').strip()
                if r_line == '':
                    continue

                # # vcf_sample    Ginganoshizuku
                key, val = r_line.split('\t')
                #print("{},{}".format(key, val))

                if not bta_prov_part and \
                    key == 'sorted_samples' or \
                    key == 'groups_id' or \
                    key == 'bta_min_max_depth':

                    bta_prov_dict[key] = val
                    continue

                if key == 'vcf_sample':
                    vcf_sample = val
                    # if vcf_sample tag found, it will start the bta_prov_part
                    bta_prov_part = True
                    bta_prov_dict['prov_info'][vcf_sample] = dict()

                if bta_prov_part:
                    bta_prov_dict['prov_info'][vcf_sample][key] = val

                    # vcf_sample    Ginganoshizuku
                    # min_max_depth 8-300
                    # bam_bed_path  /home/sunnysidest/software/vprimer_v2/
                    #   vprimer/bed_thin_align_new/
                    #   s_Ginganoshizuku.chr01_03_1M.bam.m8_x300.bb.bed
                    # bam_md5       a5165c2e2d46b5211c4d7ad04817a64d
                    # user_bam_path /home/sunnysidest/software/vprimer_v2/
                    #   vprimer/bed_thin_align_new/data_dir/
                    #   s_Ginganoshizuku.chr01_03_1M.bam

        return bta_prov_dict


    def check_bta_provenance(self, bta_prov_dict):
        '''
        渡された .bta.bedのヘッダ、bta_prov_dict の内容と
        bam_table で指定された self.bta_req_dict の内容を
        比較し、同一構成で作られたファイルかどうかを確認する
        '''

        found_bed_thal = False
        er_m = ""

        try:

            # 構成されているbam_bedの数
            req_cnt = len(self.bta_req_dict['prov_info'].keys())
            bta_cnt = len(bta_prov_dict['prov_info'].keys())

            if req_cnt != bta_cnt:
                er_m = "included vcf_sample number are not same."
                raise UserFormatErrorBTA(er_m)

            # ソートされた vcf_sample 文字列
            req_srt_smpls = self.bta_req_dict['sorted_samples']
            bta_srt_smpls = bta_prov_dict['sorted_samples']

            if req_srt_smpls != bta_srt_smpls:
                er_m = "sorted_samples are not same."
                raise UserFormatErrorBTA(er_m)

            # 指定されたmin_max_depth
            req_dep = self.bta_req_dict['bta_min_max_depth']
            bta_dep = bta_prov_dict['bta_min_max_depth']

            if req_dep != bta_dep:
                er_m = "bta_min_max_depth are not same."
                raise UserFormatErrorBTA(er_m)

            # vcf_sampleごとに
            for vcf_sample in self.bta_req_dict['prov_info'].keys():

                # bamのmd5
                bam_md5 = \
                    self.bta_req_dict['prov_info'][vcf_sample]['bam_md5']
                bta_md5 = \
                    bta_prov_dict['prov_info'][vcf_sample]['bam_md5']

                if bam_md5 != bta_md5:
                    # bamのmd5が違う場合、NG
                    er_m = "bam md5 are not same."
                    raise UserFormatErrorBTA(er_m)

                # bamごとに指定されたmin_max_depth
                s_req_dep = \
                    self.bta_req_dict[
                        'prov_info'][vcf_sample]['min_max_depth']
                s_bta_dep = \
                    bta_prov_dict[
                        'prov_info'][vcf_sample]['min_max_depth']

                if s_req_dep != s_bta_dep:
                    # depthが違う場合、NG
                    er_m = "depth are not same."
                    raise UserFormatErrorBTA(er_m)

                # don't need checking
                s_req_bpath = \
                    self.bta_req_dict['prov_info'][vcf_sample]['bam_bed_path']
                s_bta_bpath = \
                    bta_prov_dict['prov_info'][vcf_sample]['bam_bed_path']

        except UserFormatErrorBTA as ex:
            log.info("not same {}, {}".format(found_bed_thal, ex))

        else:
            found_bed_thal = True
            log.info("same file found, {}".format(found_bed_thal))

        return found_bed_thal


class UserFormatErrorBTA(Exception):
    """Detect user-defined format errors"""
    pass

