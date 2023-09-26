# -*- coding: utf-8 -*-

import sys
import errno
import re
from pathlib import Path
import numpy as np
import pandas as pd

import pprint

# global variants
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
from vprimer.bed_thin_align import BedThinAlign


'''
    distin_grp_dict の数は上限なし。
    個々の解析において、合計の比較サンプルに対応する
    bed_thal ファイルが必要。

    bed_thalファイルは、
    distin_grp_dictの 'bed_thal_path' に書かれている。
    bed_thalファイルを検索可能にした、DataFrame を、
    distin_grp_dict に格納すれば良い。
    distin_grp_dict['df_query_bed'] になるといい。


'''

class ConfBedFile(object):

    def open_log_bedfile(self):

        global log
        log = LogConf.open_log(__name__)


    def prepare_bed_thal(self):
        ''' from main
        '''

        # 一時ファイルを消す
        for fpath in self.bed_dir_path.iterdir():

            if str(fpath).endswith(glv.bam_bed_tmp_ext):
                log.info("delete leftover tmp file ({}), {}.".format(
                    glv.bam_bed_tmp_ext, fpath))
                fpath.unlink()

            if str(fpath).endswith(glv.bed_thal_sort_ext):
                log.info("delete leftover tmp file ({}), {}.".format(
                    glv.bed_thal_sort_ext, fpath))
                fpath.unlink()

            if str(fpath).endswith(glv.bed_thal_merge_ext):
                log.info("delete leftover tmp file ({}), {}.".format(
                    glv.bed_thal_merge_ext, fpath))
                fpath.unlink()

        # 202309
        #print()
        #print("main.py: glv.conf.prepare_bed_thal")
        #print()
        #print("conf_bed_file.py: prepare_bed_thal")
        #print("\tglv.conf.depth_mode\t{}".format(glv.conf.depth_mode))
        #print("1")
        #print()
        #sys.exit(1)

        # これは本当に必要か？
        if self.depth_mode == glv.depth_no_check:
            return

        bed_thal_path_list = list()

        # prepare bed_thal
        for distin_grp_dict in self.distinguish_groups_list:
            # get bed_thal_path to list

            # 202309
            #print()
            #print("conf_bed_file.py: prepare_bed_thal")
            #print("\tglv.conf.depth_mode\t{}".format(glv.conf.depth_mode))
            #print("\tdo self.select_depth_mode ->")
            #print("2")
            #print()

            bed_thal_path = self.select_depth_mode(distin_grp_dict)

            if bed_thal_path != "":

                # 202309
                #print()
                #print("conf_bed_file.py: prepare_bed_thal")
                #print("\tglv.conf.depth_mode\t{}".format(
                #    glv.conf.depth_mode))
                #print("\tdo self.select_depth_mode ->")
                #print("2.1")
                #print()

                bed_thal_path_list += self.select_depth_mode(distin_grp_dict)

                #print("444")

        # a list of paths to use as dictionary keys
        if glv.conf.depth_mode != glv.depth_no_check:
            for bed_thal_path in bed_thal_path_list:
                self.read_bed_into_dict(bed_thal_path)


    def select_depth_mode(self, distin_grp_dict):

        print("conf_bed_file.py: select_depth_mode")

        bed_thal_path = ""

        groups_id = distin_grp_dict['groups_id']
        #print("group_id={}".format(groups_id))

        # 当初作成したサンプル名のstringで行く(リストへは各自変換)
        sorted_samples_str = distin_grp_dict['sorted_samples']
        #print("sorted_samples_str={}".format(sorted_samples_str))

        # self.depth_mode ４のモード
        #   glv.depth_no_check
        #   glv.depth_bam_table
        #   glv.depth_bed_bams
        #   glv.depth_bed_thal

        # これはモードに対応するので、ここでは不要
        #bed_thal_path = distin_grp_dict['bed_thal_path']
        #print("bed_thal_path={}".format(bed_thal_path))
        # 起動オプションで指定されていない場合、- である。

        # *******************************************************
        # BedThinAlignクラスのインスタンスを作成して処理
        bta = BedThinAlign()
        # *******************************************************

        log.info("start, depth mode: {}.".format(self.depth_mode))
        # bamテーブルによるデプスチェック
        # glv.conf.user_bam_table_path
        bta.make_bam_table_dict()

        # make bam_bed_file
        # self.require_bam_bed_list

        #print()
        #print("conf_bed_file.py: select_depth_mode")
        #print("\tdo bta.get_require_bam_bed_list->")
        #print("3")
        #print()

        bta.get_require_bam_bed_list(sorted_samples_str)

        #print("glv.conf.depth_mode\t{}".format(glv.conf.depth_mode))
        #print("5")

        if self.depth_mode == glv.depth_bam_table:
            # bamテーブルによるデプスチェック
            # glv.conf.user_bam_table_path
            #  bta.make_bam_table_dict()

            # make bam_bed_file
            # self.require_bam_bed_list
            #  bta.get_require_bam_bed_list(sorted_samples_str)

            # build bam_bed
            bta.build_bam_bed()

            # Collect bibliographic information for bam_bed to see
            # if there already exists a bed_thal made from
            # the specified bam_bed.
            bta.pick_provenance_with_depth(sorted_samples_str, groups_id)

            # checks if there is a bed_thal from the given origin
            found_bed_thal, bed_thal_path = bta.find_suitable_bed_thal()

            # 設定されるべき名前。無いならなら今から作る
            distin_grp_dict['bed_thal_path'] = bed_thal_path
            #pprint.pprint(distin_grp_dict)

            #print("found_bed_thal={}".format(found_bed_thal))
            #print("bed_thal_path={}".format(bed_thal_path))

            # if found, only print file name
            if found_bed_thal:
                mes = "Found a bed_thal file that satisfies "
                mes += "the conditions:\n{}".format(bed_thal_path)
                log.info(mes)

            else:
                # make
                mes = "not found suitable bed_thal file, "
                mes += "so it will be generated, {}".format(bed_thal_path)
                log.info(mes)
                bta.build_bed_thal(bed_thal_path)

            log.info("finished, {}".format(utl.elapse_epoch()))

        #elif self.depth_mode == glv.depth_bed_bams:
            # 共通bamを指定
            # glv.conf.user_bed_bams_str
            # bamを指定した、bed_thal を作成
        #    pass


        elif self.depth_mode == glv.depth_bed_thal:
            # 共通bed_thalを指定
            bed_thal_path = glv.conf.user_bed_thal_path

            # 存在の確認
            if not bed_thal_path.exists():
                er_m = "not found bed_thal {}".format(bed_thal_path)
                log.error(er_m)
                sys.exit(1)

            else:
                # bedとしての動作チェック
                err_str = utl.bed_validation(bed_thal_path)
                if err_str != "":
                    er_m = "For the following bed_thal "
                    er_m += "file that already exists, "
                    er_m += "bedtools says that:\n\n{}".format(err_str)
                    log.error(er_m)
                    sys.exit(1)


            # glv.conf.user_bed_thal_path
            distin_grp_dict['bed_thal_path'] = bed_thal_path
            mes = "All analyzes are set to use "
            mes += "the bed_thal {}".format(bed_thal_path)
            log.info(mes)

        else:
            # glv.depth_no_check:
            pass


        #for distin_grp_dict in self.distinguish_groups_list:
        # ここまでで、distin_grp_dict['bed_thal_path'] が準備完了である。
        # distin_grp_dict の辞書としてファイル名をキーとして読むか
        # 辞書名は、何にするといいか。
        # 例えば、bed_thin_alignファイルが、同じものの場合、
        # 指定されたパスをもとに、dictにすればいいか。

        # 準備が終わったbed を、pandasに読み込んで、
        # search_bedができるようにする:

        # bed_thin_align
        #self.bed_thin_align = self.choice_variables('bed_thin_align')


        #if (self.bed_thin_align != ""):
        #
        #    self.user_bed_path = utl.full_path(self.bed_thin_align)
        #    basename_user_bed = os.path.basename(self.user_bed_path)
        #    self.bed_slink_system = "{}/{}{}".format(
        #        self.ref_dir_path, 'slink_', basename_user_bed)
        #    self.bed_path = "{}/{}".format(
        #        self.ref_dir_path, basename_user_bed)
        #
        #    self.prepare_bed()
        #
        #sys.exit(1)

        #return list
        return [bed_thal_path]


    def read_bed_into_dict(self, bed_thal_path):
        """
        """

        # don't register same path bed file
        if bed_thal_path in self.bed_thal_dict.keys():
            return
        else:
            self.bed_thal_dict[bed_thal_path] = dict()

        bed_header = ['chrom', 'start', 'end']

        # read bed into pandas
        df_bed = pd.read_csv(bed_thal_path, sep = '\t', header = None,
            index_col = None, comment = '#')
        df_bed.columns = bed_header

        # start is open pos so +1
        df_bed['start'] = df_bed['start'] + 1 

        # pick uniq.chrom
        chrom_name = np.unique(df_bed['chrom'])

        for chrom in chrom_name:
            self.bed_thal_dict[bed_thal_path][chrom] = \
                df_bed[df_bed['chrom'] == chrom]

        mes = "finished reading "
        mes += "self.bed_thal_dict[{}], ".format(bed_thal_path)
        mes += "chrom={}".format(chrom_name)

        log.info("{}".format(mes))


