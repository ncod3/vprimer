#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse

import re
import time
import datetime

from pathlib import Path

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import subprocess as sbp

import pprint

# for md5
import os
import glob
import hashlib


def main():

    global log
    log = LOG()
    global glv
    glv = GLV()
    global utl
    utl = UTL()

    bta = BedThinAlign()
    log.info("start, {}".format(utl.datetime_str()))

    # get command arg
    bta.get_arg()

    # read bam_table
    sorted_samples_str = bta.make_bam_table_dict()

    # make bam_bed_file
    require_bam_bed_list = bta.get_require_bam_bed_list(sorted_samples_str)
    bta.build_bam_bed(require_bam_bed_list)

    # Collect bibliographic information for bam_bed to see
    # if there already exists a bed_thin_align made from
    # the specified bam_bed.
    bta.pick_provenance_with_depth(sorted_samples_str)

    # checks if there is a bed_thin_align from the given origin 
    found_bed_thal, bed_thal_path = bta.find_suitable_bed_thal()

    # if found, only print file name
    if found_bed_thal:
        mes = "Found a bed_thin_align file that satisfies "
        mes += "the conditions:\n\n{}\n{}\n".format(
            bed_thal_path.name, bed_thal_path)
        log.info(mes)

    else:
        # make
        mes = "not found suitable bed_thin_align file, "
        mes += "so we will create it:\n\n{}\n{}\n".format(
            bed_thal_path.name, bed_thal_path)
        log.info(mes)
        bta.build_bed_thin_align(bed_thal_path)

    log.info("finished, {}".format(utl.elapse_epoch()))


class LOG(object):
    '''
    '''

    def __init__(self):
        pass

    def error(self, message, outfile=sys.stderr):
        '''
        '''
        print(message, file=outfile)


    def info(self, message, outfile=sys.stdout):
        '''
        '''
        print(message, file=outfile)


class GLV(object):
    '''
    '''

    def __init__(self):

        # now_epochtime 1612835817.20904
        self.now_epochtime = datetime.datetime.now().timestamp()

        # now_stat
        self.bed_now_nop        = "now_nop"

        self.bed_now_zero       = "Z"
        self.bed_now_thin       = "thin"
        self.bed_now_valid      = "valid"
        self.bed_now_thick      = "THICK"

        # stat_changed
        self.bed_stat_nop       = "bed_stat_nop"

        self.bed_stat_init      = "bed_stat_init"
        self.bed_stat_continue  = "bed_stat_continue"
        self.bed_stat_changed   = "bed_stat_changed"

        # bam_bed
        self.min_max_ext        = ".mMin_xMax"

        self.bam_bed_ext        = ".bb.bed"
        self.bam_bed_tmp_ext    = ".bed_tmp"

        # bed_thin_align
        self.bed_thal_prefix    = "bed_thal_"
        self.bed_thal_ext       = ".bta.bed"
        self.bed_thal_tmp_ext   = ".bed_thal_sort"

        self.na_group_names     = "NAGRP"

class UTL(object):

    def __init__(self):

        pass


    def datetime_str(self):
        '''
        2023_0131_1354_45
        '''
        # 2023-02-09 15:03:45.582786
        # datetime.datetime.now()
        # 2023_0131_1354_45
        return self.conv_datetime(datetime.datetime.now())


    def elapse_epoch(self):
        '''
        elapsed time from glv.now_epochtime
        '''
        # glv.now_epochtime
        # 1675922956.929297
        # self.elapse_str(glv.now_epochtime)
        # elapsed_time 0:00:00
        return self.elapse_str(glv.now_epochtime)


    def get_start_time(self):
        '''
        get start time
        '''
        return time.time()


    def conv_datetime(self, datetime):

        # 2023_0131_1354_45
        start_time_str = re.sub(
            r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\..*$',
            r'\1_\2\3_\4\5_\6',
            str(datetime))

        return start_time_str


    def get_path_mtime(self, file_path):

        # 1674173966.0
        st_mtime = file_path.stat().st_mtime
        #2023-01-20 09:19:26
        dtdt = datetime.datetime.fromtimestamp(st_mtime)
        return self.conv_datetime("{}.0".format(dtdt))


    def get_path_size(self, file_path):

        # byte
        return file_path.stat().st_size


    def elapse_str(self, start_time):
        '''
        with 'elapsed_time'
        '''
        return "elapsed_time {}".format(self.elapse(start_time))


    def elapse(self, start_time):
        '''
        get elapsed time from start_time to now
        '''

        elapsed_time = time.time() - start_time
        # 0:00:02.212885
        elapsed_time_str = datetime.timedelta(seconds=elapsed_time)
        # 0:00:02
        elapsed_time_str = str(elapsed_time_str).split('.')[0]
        return elapsed_time_str


    def strip_hash_comment(self, line):
        '''
        '''
        return line.split('#')[0].strip()


class BedThinAlign(object):

    def __init__(self):


        #self.concurrent_mode = "thread"
        self.concurrent_mode = "process"
        #self.concurrent_mode = "serial"

        self.open_pos = True        # bedのposition法を、open, closeにする
        self.valid_print = True     # depthが無問題の部分も出力する

        # ユーザ指定のbam_table
        self.bam_table_dict = dict()

        # here
        self.bed_dir_path = Path(".")

        self.command            = Path(sys.argv[0]).name
        self.comment = "Not assigned, created by {}".format(self.command)

        self.now_datetime       = utl.datetime_str()

        # bed_thin_align
        # 解析で指定されたbam_bedの情報
        self.bta_req_dict = dict()

        self.uname = "{}, {}".format(os.uname()[0], os.uname()[2])
        self.hostname = os.uname()[1]

        # for header
        self.h_bbed = {
            'vcf_sample':       'vcf_sample',
            'bam_bed_name':     'bam_bed_name',
            'date':             'date',
            'min_max_depth':    'min_max_depth',

            'associated_bam':   'associated_bam',
            'bam_path':         'bam_path',
            'bam_mtime':        'bam_mtime',
            'bam_size':         'bam_size',
            'bam_md5':          'bam_md5',

            'vcf':              'vcf',
            'ref':              'ref',

            'uname':            'uname',
            'hostname':         'hostname',
        }


    def get_arg(self):
        '''
        '''

        parser = argparse.ArgumentParser(description='')

        # -f, --file
        parser.add_argument('-f', '--file', action='store',
            required=True,
            help="")

        # -m, --min_depth
        parser.add_argument('-m', '--min_depth', action='store',
            required=True, type=int,
            help="")

        # -x, --max_depth
        parser.add_argument('-x', '--max_depth', action='store',
            required=True, type=int,
            help="")

        # -p, --parallel_cnt
        parser.add_argument('-p', '--parallel_cnt', action='store',
            required=True, type=int,
            help="")

        # -d, --dont_show_valid
        parser.add_argument('-d', '--dont_show_valid', action='store_true',
            required=False,
            help="")

        self.args = parser.parse_args()

        #
        self.user_bam_table_path = Path(self.args.file).resolve()
        self.min_depth = self.args.min_depth
        self.max_depth = self.args.max_depth
        self.parallel_cnt = self.args.parallel_cnt
        self.dont_show_valid = self.args.dont_show_valid

        self.bta_min_max_depth = "{}-{}".format(
            self.min_depth, self.max_depth)


    def  make_bam_table_dict(self):
        '''
        '''

        sorted_samples_list = list()

        with self.user_bam_table_path.open('r', encoding='utf-8') as f:
            # iterator
            for r_liner in f:
                r_line = r_liner.strip()    # ct, ws

                # remove header # and comment
                if r_line.startswith('#') or r_line == '':
                    continue
                r_line = utl.strip_hash_comment(r_line)

                vcf_sample, associated_bam = r_line.split()

                # append to list
                sorted_samples_list.append(vcf_sample)

                # init
                user_bam_path = "-"
                bam_bed_path = "-"

                # 
                if associated_bam != "-":
                    # user_bam_path
                    user_bam_path = Path(associated_bam).resolve()

                    # user_bam_file_path existance check
                    if not user_bam_path.exists():
                        er = "bam_file not found "
                        er += "{}.".format(associated_bam)
                        log.error(er)
                        sys.exit(1)

                    # make bed file name and get pathlib
                    bam_bed_path = self.get_bam_bed_path_name(
                        user_bam_path.name,
                        self.min_depth, self.max_depth)


                # dictionary
                self.bam_table_dict[vcf_sample] = {
                    'vcf_sample': vcf_sample,
                    'associated_bam': associated_bam,
                    'user_bam_path': user_bam_path,
                    'slink_bam_path': user_bam_path,
                    'min_max_depth': "{}-{}".format(
                        self.min_depth, self.max_depth),
                    'bam_bed_path': bam_bed_path,
                }

        #pprint.pprint(self.bam_table_dict)
        # this is required vcf_samples
        sorted_samples_str = ','.join(sorted(set(sorted_samples_list)))
        return sorted_samples_str


    def get_bam_bed_path_name(self, bam_path, min_depth, max_depth):
        '''
        '''
        bam_bed_ext = self.get_bam_bed_ext(min_depth, max_depth)
        bam_bed_path = Path("{}{}".format(bam_path, bam_bed_ext)).resolve()
        return bam_bed_path


    def get_bam_bed_ext(self, min_depth, max_depth):
        ''' bedの拡張子は、depthのしきい値、Min, Maxを含んでいる。
        '''
        # glv.min_max_ext        = ".mMin_xMax"
        # glv.bam_bed_ext        = ".bb.bed"

        # substitute .mMin_xMax.bed => .m8_x300.bed
        bam_bed_ext = glv.min_max_ext + glv.bam_bed_ext
        bam_bed_ext = re.sub('Min', str(min_depth), bam_bed_ext)
        bam_bed_ext = re.sub('Max', str(max_depth), bam_bed_ext)
        return bam_bed_ext


    def get_require_bam_bed_list(self, sorted_samples):
        '''
        bam_bed_dict = {
            'bam_num': bam_num,
            'ttl_num': bam_num,
            'vcf_sample': vcf_sample,
            'associated_bam': associated_bam,
            'user_bam_path': user_bam_path,
            'bam_path': slink_bam_path,
            'bam_bed_path': bam_bed_path,
            'min_depth': min_depth,
            'max_depth': max_depth,
        }
        '''
        require_bam_bed_list = list()


        # カンマ区切りをリストに
        sorted_sample_list = sorted_samples.split(',')

        # bam_bed の要作成リストの構築
        require_bam_bed_list = list()
        bam_num = 1

        # 調査対象の、sorted_sample_list にて
        for vcf_sample in sorted_sample_list:

            associated_bam = \
                self.bam_table_dict[vcf_sample]['associated_bam']

            # it hasn't bam file
            if associated_bam == '-':
                continue

            user_bam_path = \
                self.bam_table_dict[vcf_sample]['user_bam_path']
            slink_bam_path = \
                 self.bam_table_dict[vcf_sample]['slink_bam_path']
            bam_bed_path = self.bam_table_dict[vcf_sample]['bam_bed_path']

            # すでに、指定のファイル名のbedがあれば、何もしない
            if bam_bed_path.exists():
                log.info("bam_bed {} already exist.".format(bam_bed_path))
                continue

                continue

            bam_bed_dict = {
                'bam_num': bam_num,
                'ttl_num': 0,
                'vcf_sample': vcf_sample,
                'associated_bam': associated_bam,
                'user_bam_path': user_bam_path,
                'bam_path': slink_bam_path,
                'bam_bed_path': bam_bed_path,
                'min_depth': self.min_depth,
                'max_depth': self.max_depth,
            }
            require_bam_bed_list.append(bam_bed_dict)
            bam_num += 1

        # set total num
        self.set_total_num(require_bam_bed_list)

        return require_bam_bed_list


    def set_total_num(self, require_list):
        '''
        '''
        # 辞書の中の ttl_num を更新
        ttl_num = len(require_list)
        for d_dict in require_list:
            d_dict['ttl_num'] = ttl_num


    def build_bam_bed(self, require_bam_bed_list):
        '''
        '''
        reqcnt = len(require_bam_bed_list)
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
            len(require_bam_bed_list))
        log.info(mes)

        para_cnt = self.parallel_cnt
        if para_cnt > reqcnt:
            para_cnt = reqcnt

        if self.concurrent_mode == "process":

            mes = "Parallelize in process mode. "
            mes += "{} samples are parallelized from {} totals.".format(
                para_cnt, reqcnt)
            log.info(mes)

            with ProcessPoolExecutor(self.parallel_cnt) as e:
                ret = e.map(
                    self.make_bam_bed_file,
                    require_bam_bed_list)

        elif self.concurrent_mode == "thread":

            mes = "Parallelize in thread mode. "
            mes += "{} samples are parallelized from {} totals.".format(
                self.parallel_cnt, reqcnt)
            log.info(mes)

            with ThreadPoolExecutor(self.parallel_cnt) as e:
                ret = e.map(
                    self.make_bam_bed_file,
                    require_bam_bed_list)

        else:

            mes = "No parallelization mode. "
            mes += "Total {} serial executions.".format(reqcnt)
            log.info(mes)

            for bam_bed_dict in require_bam_bed_list:
                self.make_bam_bed_file(bam_bed_dict)

        log.info("finished build_bam_bed, {}".format(
            utl.elapse_str(start)))


    def make_bam_bed_file(self, bam_bed_dict):

        '''
        bam_bed_dict = {
            'bam_num': bam_num,
            'ttl_num': bam_num,
            'vcf_sample': vcf_sample,
            'associated_bam': associated_bam,
            'user_bam_path': user_bam_path,
            'bam_path': slink_bam_path,
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

        bam_path = bam_bed_dict['bam_path']
        bam_bed_path = bam_bed_dict['bam_bed_path']
        min_depth = bam_bed_dict['min_depth']
        max_depth = bam_bed_dict['max_depth']

        bam_bed_tmp_path = Path(
            str(bam_bed_path) + glv.bam_bed_tmp_ext).resolve()

        # add header to bam_bed
        bam_bed_header = self.ident_bam_bed_header(
            vcf_sample, associated_bam,
            bam_path, min_depth, max_depth, bam_bed_path)

        start = utl.get_start_time()
        log.info("start ({}/{}){}.".format(
            bam_num, ttl_num, vcf_sample))

        # samtools depth から、depth bed を作成
        with bam_bed_tmp_path.open('w',  encoding='utf-8') as f:

            # bedが作られたときのログ。作成コマンドまでたどり着くこと。
            f.write(bam_bed_header)
            # ヘッダは確実にflushしておこう 書き出しの順番のために
            f.flush()
            self.calc_bam_depth(f, vcf_sample, associated_bam,
                bam_path, min_depth, max_depth, bam_num, ttl_num, start)

        # 終了したら、mvする。
        bam_bed_tmp_path.rename(bam_bed_path)

        log.info("finished ({}/{}){}, {}".format(
            bam_num, ttl_num, vcf_sample, utl.elapse_str(start)))


    def ident_bam_bed_header(self, vcf_sample, associated_bam,
        bam_path, min_depth, max_depth, bam_bed_path):

        # ログを見れば、作成の際のコマンドまでたどり着くこと。
        # bamと、bed_thin_align は全く異なるコンピュータ環境で
        # 生成され使用される可能性があることから、
        # すべての基本となる bam_bedファイルに、bamの詳細な情報を
        # 残す。そして、bed_thin_align 内部にも、これらの情報を
        # 引き継ぐ

        # bamの情報
        #   vcf_sample
        #   associated_bam(on bam_table)
        #   bam_path
        #   ls -l information(size, and date)
        #   bam_md5_value

        date = utl.datetime_str()
        vcf = self.comment
        ref = self.comment

        bam_mtime = utl.get_path_mtime(bam_path)
        bam_size = utl.get_path_size(bam_path)

        bam_md5 = self.get_MD5(vcf_sample, bam_path)

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
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['vcf'],vcf)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['ref'],ref)

        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['associated_bam'], associated_bam)
        bam_bed_header += "# {}\t{}\n".format(
            self.h_bbed['bam_path'], bam_path)
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


    def get_MD5(self, vcf_sample, bam_path):
        '''
        Calculates md5 hash of a file
        '''
        mes = "calcurate the md5 of bam {} ({}). ".format(
            bam_path.name, vcf_sample)
        mes += "It will take some time."
        log.info(mes)

        # We don't use pathlib here because we want to read in chunks.
        # pathlib 0:00:25 open 0:00:17
        hash = hashlib.md5()

        # using os.open
        #print(hash.block_size)  # block_size=64, 131072
        with open(bam_path, "rb") as f:
            while True:
                chunk = f.read(2048 * hash.block_size)
                if len(chunk) == 0:
                    break
                hash.update(chunk)

        path_hash = hash.hexdigest()

        mes = "finished calcurating md5 of bam {} ({}) {}".format(
            bam_path.name, vcf_sample, path_hash)
        log.info(mes)

        return path_hash


    def calc_bam_depth(self, f, vcf_sample, associated_bam,
        bam_path, min_depth, max_depth, bam_num, ttl_num, stt):
        '''
        '''

        # 最初はサンプルのスタート
        start = stt

        # glv
        last_stat = glv.bed_now_nop
        last_chrom = ""

        # for bed
        bed_close_stt = 1
        bed_open_stt =  1
        bed_close_end = 1

        expected_pos = 1

        # as generate function
        # Code that runs in parallel depending on each argument
        for r_depth_line in self.genfunc_samtools_depth(bam_path):

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

            #if pos > 1000000 or pos < 10:
            #    print("now_stat={}, stat_changed={}, chrom={}, pos={}".\
            #        format(now_stat, stat_changed, chrom, pos))

            if stat_changed == glv.bed_stat_init:
                expected_pos = 1
                # 20230126 mod
                # force to stat_changed
                stat_changed = glv.bed_stat_changed

                if last_chrom != "":
                    # 単なるメッセージ
                    mes = "{} finished ({}/{}){}, {}".format(
                        last_chrom, bam_num, ttl_num,
                        vcf_sample, utl.elapse_str(start))
                    log.info(mes)
                    start = utl.get_start_time()

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
            # *****************************************************

        # final print
        self.print_line(f, last_stat,
            last_chrom, bed_close_stt, bed_close_end, last_stat)

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
        if depth < min_depth:
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


    def print_line(self, f, last_stat,
        chrom, bed_close_stt, bed_close_end, comment=""):
        '''
        '''

        if self.open_pos:
            bed_open_stt = bed_close_stt - 1
        else:
            bed_open_stt = bed_close_stt

        # dont show valid line
        if self.dont_show_valid:
            if 'valid' in comment:
                return

        # 直前のもののステータス
        if last_stat != glv.bed_now_valid:
            f.write("{}\t{}\t{}\t{}\n".format(
                chrom, bed_open_stt, bed_close_end, comment))
        else:
            if self.valid_print:
                f.write("{}\t{}\t{}\t({})\n".format(
                    chrom, bed_open_stt,
                    bed_close_end, comment))


    def pick_provenance_with_depth(self, sorted_samples):
        '''
        '''

        mes = "start pick_provenance_with_depth."
        log.info(mes)

        # it's one dict
        self.bta_req_dict = {
            'sorted_samples': sorted_samples,
            'groups_id': glv.na_group_names,
            'bta_min_max_depth': self.bta_min_max_depth,
            'bam_bed_path_list': list(),
            'prov_info': dict()
        }

        # for each vcf_sample
        for vcf_sample in sorted_samples.split(','):

            # if '-'

            user_bam_path = self.bam_table_dict[vcf_sample]['user_bam_path']
            print("user_bam_path={}".format(user_bam_path))
            min_max_depth = self.bam_table_dict[vcf_sample]['min_max_depth']
            print("min_max_depth={}".format(min_max_depth))
            bam_bed_path = self.bam_table_dict[vcf_sample]['bam_bed_path']
            print("bam_bed_path={}".format(bam_bed_path))

            # dict: key => vcf_sample
            prov_info = {
                vcf_sample: {
                    'user_bam_path': user_bam_path,
                    'bam_md5': "",
                    'min_max_depth': min_max_depth,
                    'bam_bed_path': bam_bed_path,
                }
            }

            # read bam_hed_header
            with bam_bed_path.open('r', encoding='utf-8') as f:
                for r_liner in f:
                    r_line = r_liner.strip()    # ct, ws

                    if not r_line.startswith('#'):
                        break

                    r_line = r_line.replace('#', '').strip()
                    if r_line == '':
                        continue

                    # # vcf_sample    Ginganoshizuku
                    key, val = r_line.split('\t')
                    #print("key={}, val={}".format(key, val))
                    if key == 'bam_md5':
                        prov_info[vcf_sample][key] = val

            # add tha bam_bed info to a bed_thal file
            self.bta_req_dict['bam_bed_path_list'].append(
                bam_bed_path)
            self.bta_req_dict['prov_info'].update(prov_info)

        mes = "finished pick_provenance_with_depth."
        log.info(mes)


    def find_suitable_bed_thal(self):

        mes = "start find_suitable_bed_thal."
        log.info(mes)

        found_bed_thal = False
        bed_thal_path = ""

        bta_bed_cnt = 0
        # 今度は、bed_thal を１つづつ探す
        for fpath in self.bed_dir_path.iterdir():

            # glv.bed_thal_ext       = ".bta.bed"
            if str(fpath).endswith(glv.bed_thal_ext):
                bta_bed_cnt += 1

                # 見つかった .bta.bed ファイルから来歴を読み出す
                bta_prov_dict = self.read_bta_provenance_info(fpath)
                # 来歴のチェック
                # 既存の .bta.bed の来歴と、今作ろうとしている サンプルを
                # 比較して、同じものならば、既存のファイルを用いる
                found_bed_thal = self.check_bta_provenance(bta_prov_dict)

                if found_bed_thal:
                    bed_thal_path = Path(fpath).resolve()
                    break

        if not found_bed_thal:
            bed_thal_path = self.make_new_bed_thal_path()

        return found_bed_thal, bed_thal_path


    def make_new_bed_thal_path(self):

        bed_thal = "{}/{}{}_{}{}".format(
            self.bed_dir_path,
            glv.bed_thal_prefix,
            glv.na_group_names,
            self.now_datetime,
            glv.bed_thal_ext)

        # fullpath: pathlib
        new_bed_thal_path = Path(bed_thal).resolve()

        return new_bed_thal_path


    def build_bed_thin_align(self, new_bed_thal_path):

        # 使用する bam_bed のリスト pathlibから、fullpath textのリストへ
        bam_bed_path_list = list(map(str,
            self.bta_req_dict['bam_bed_path_list']))

        # awk, sort処理後の、書き出し用bedファイル
        new_bed_thal_tmp_path = \
            Path(str(new_bed_thal_path) + glv.bed_thal_tmp_ext).resolve()

        # make_header
        header_bed_thal = self.ident_bed_thal_header()

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
            ['$1!~/^#/ && $4!~/(valid)/ {printf("%s\\t%s\\t%s\\n",$1,$2,$3)}']
        # argument: bam_bed files
        cmd_awk += bam_bed_path_list

        # (2) | sort: by first column "chrom" and second column position
        cmd_sort = ['sort']
        cmd_sort += ['-k', '1,1', '-k', '2,2n']

        # (3) cmd_awk | cmd_sort > file
        # cmd_redirect = ['>']
        # cmd_redirect += ["{}".format(bed_thal_tmp_path)]
        with new_bed_thal_tmp_path.open('w', encoding='utf-8') as f:
            #f.write(header_bed_thal)
            #f.write("{}".format(header_bed_thin_align)
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
        cmd_bedtools += ['-i', '{}'.format(new_bed_thal_tmp_path)]

        # (5) cmd_bedtools > file
        # エラーをキャプチャして、logに残す
        with new_bed_thal_path.open('w', encoding='utf-8') as f:
            #print("(4) cmd_bedtools")
            f.write(header_bed_thal)
            # need f.flush()
            f.flush()
            p3 = sbp.Popen(cmd_bedtools, stdout=f, stderr=sbp.PIPE, text=True)
            result, err = p3.communicate()
            #print("(5) cmd_bedtools end")

        if err != "":
            log.info("bedtools={}".format(err))

        # 終了したら、tmpを消す
        new_bed_thal_tmp_path.unlink()

        log.info("finished, creating {}".format(new_bed_thal_path.name))


    def ident_bed_thal_header(self):
        #, groups, sorted_samples, bed_path_list, min_depth, max_depth):

        date = utl.datetime_str()
        vcf = self.comment
        ref = self.comment

        #----------------
        sorted_samples = self.bta_req_dict['sorted_samples']
        groups_id = self.bta_req_dict['groups_id']
        bta_min_max_depth = self.bta_req_dict['bta_min_max_depth']

        #
        bed_thal_header = ""
        bed_thal_header += "# date\t{}\n".format(date)
        bed_thal_header += "# uname\t{}\n".format(self.uname)
        bed_thal_header += "# hostname\t{}\n".format(self.hostname)
        bed_thal_header += "# vcf\t{}\n".format(vcf)
        bed_thal_header += "# ref\t{}\n".format(ref)
        bed_thal_header += "# groups_id\t{}\n".format(groups_id)
        bed_thal_header += "# sorted_samples\t{}\n".format(sorted_samples)
        bed_thal_header += "# bta_min_max_depth\t{}\n".format(
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

            bed_thal_header += "#\n"
            bed_thal_header += "# vcf_sample\t{}\n".format(vcf_sample)
            bed_thal_header += "# min_max_depth\t{}\n".format(min_max_depth)
            bed_thal_header += "# bam_bed_path\t{}\n".format(bam_bed_path)
            bed_thal_header += "# bam_md5\t{}\n".format(bam_md5)
            bed_thal_header += "# user_bam_path\t{}\n".format(user_bam_path)

        bed_thal_header += "#\n"

        return bed_thal_header


    def read_bta_provenance_info(self, bed_thal_path):

        # from copy from self.bta_req_dict
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
                    self.bta_req_dict['prov_info'][vcf_sample]['min_max_depth']
                s_bta_dep = \
                    bta_prov_dict['prov_info'][vcf_sample]['min_max_depth']

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


if __name__ == '__main__':
    main()

