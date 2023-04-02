# -*- coding: utf-8 -*-

import sys
#import os
import errno
import time
import datetime
from pathlib import Path

import subprocess as sbp
import pandas as pd
import pickle
import pprint

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf

from vprimer.blast import Blast


class ConfRefFasta(object):

    def open_log_reffasta(self):

        global log
        log = LogConf.open_log(__name__)


    def prepare_ref(self, src_path, bgzip_path):

        # src_path: self.user_ref_path for symlink
        # bgzip_path: bgzipped fasta: used by the system

        log.info("prepare_ref start.")

        if bgzip_path.exists() and src_path == bgzip_path:

            mes = "The user-specified ref fasta is already used "
            mes += "by the system, so no preparation is required.\n"
            mes += "user={}\n sys={}.".format(src_path, bgzip_path)

            log.info(mes)
            return

        # symlink name for self.user_ref_path
        slink_path = self.refs_dir_path / "{}{}".format(
            glv.slink_prefix, src_path.name)
        # fai
        fai_bgzip_path = Path(
            "{}{}".format(bgzip_path, glv.fai_ext))
        # read fasta to dict vprimer.cnf.refseq
        pickle_bgzip_path = Path(
            "{}{}".format(bgzip_path, glv.pickle_ext))

        # Update the file with the old and new timestamps
        # between user_ref_path and symlink. backup and copy the files in refs
        utl.refs_file_slink_backup_and_copy(src_path, slink_path)

        # between user_ref_path and bgzip_path
        if glv.need_update == utl.is_need_update(src_path, bgzip_path):

            # update bgzip fasta
            self.update_bgzip_fasta(
                src_path,
                bgzip_path,
                fai_bgzip_path,
                pickle_bgzip_path)

        else:

            # 本来、pickleがあるべきだが、なにかエラーで落ちたとき
            # チェックしつつ作成
            self.update_alternate_files(
                fai_bgzip_path, bgzip_path, pickle_bgzip_path)

            log.info("Load an existing pickle {} and build a refseq.".format(
                pickle_bgzip_path))
            with pickle_bgzip_path.open('rb') as f:
                self.refseq = pickle.load(f)

            # dictionary
            self.ref_fasta_chrom_dict_list, \
            self.ref_fasta_chrom_list, \
            self.ref_fasta_chrom_region_list = \
                self.get_fai_info(fai_bgzip_path)


    def update_bgzip_fasta(self,
        src_path,
        bgzip_path,
        fai_bgzip_path,
        pickle_bgzip_path):

        # make bgzip fasta
        log.info("ext=[{}], self.user_ref_path={}.".format(
            src_path.suffix, src_path))

        # convert to bgz if ext is .gz and set to ref_fasta
        if src_path.suffix == '.gz':
            # half of thread?
            cmd1 = 'bgzip -cd -@ {} {} | bgzip -@ {} > {}'.format(
                self.parallel_full_thread,
                src_path,
                self.parallel_full_thread,
                bgzip_path)

        else:
            cmd1 = 'bgzip -c -@ {} {} > {}'.format(
                self.parallel_full_thread,
                src_path,
                bgzip_path)

        # execute
        utl.try_exec(cmd1)
 
        # fai, pickle, blastdb
        self.update_alternate_files(
            fai_bgzip_path, bgzip_path, pickle_bgzip_path)


    def update_alternate_files(self,
            fai_bgzip_path, bgzip_path, pickle_bgzip_path):
        # fai, pickle, blastdb

        # (1) ------------------------------------------
        # backup fai
        utl.save_to_tmpfile(fai_bgzip_path, can_log=True)

        # make fai file
        if not fai_bgzip_path.exists():
            cmd2 = 'samtools faidx {}'.format(bgzip_path)
            utl.try_exec(cmd2)

        # get fasta information
        self.ref_fasta_chrom_dict_list, \
        self.ref_fasta_chrom_list, \
        self.ref_fasta_chrom_region_list = \
            self.get_fai_info(fai_bgzip_path)

        # (2) ------------------------------------------
        # read fasta to refseq and save to pickle
        if not pickle_bgzip_path.exists():
            self.read_fasta_to_refseq(bgzip_path, pickle_bgzip_path)

        # (3) ------------------------------------------
        # makeblastdb for ref fasta
        Blast.makeblastdb()


    def read_fasta_to_refseq(self, bgzip_path, pickle_bgzip_path):
        '''
        '''

        start = utl.get_start_time()

        log.info("read refseq start ...")

        chrom_seq_list = []
        last_chrom = ''

        for chrom in self.ref_fasta_chrom_list:

            # get sequence from samtools command
            cmd1 = "samtools faidx {} {}".format(
                bgzip_path, chrom)
            cmd_list = cmd1.split(' ')

            # using command output by pipe, get sequence into python
            proc = sbp.Popen(
                cmd_list, stdout = sbp.PIPE, stderr = sbp.PIPE)

            # got bytes (b'')
            for byte_line in proc.stdout:
                # bytes to str, strip \n
                b_line = byte_line.decode().strip()

                #print("{}={}(top)".format(chrom, len(chrom_seq_list)))
                # fasta header
                if b_line.startswith('>'):
                    # not the first time
                    if len(chrom_seq_list) != 0:
                        # dictionary
                        self.refseq[last_chrom] = ''.join(chrom_seq_list)
                        chrom_seq_list = []
                        continue

                else:
                    # append to list
                    chrom_seq_list.append(b_line)
                    #print("{}={}(append)".format(chrom, len(chrom_seq_list)))

            last_chrom = chrom

        if len(chrom_seq_list) != 0:
            self.refseq[last_chrom] = ''.join(chrom_seq_list)
            #print("{},last_len={}".format(
            #    chrom, len(glv.ref.refseq[last_chrom])))

        log.info("read refseq done {}\n".format(utl.elapse_str(start)))

        # pickle
        with pickle_bgzip_path.open('wb') as f:
            pickle.dump(self.refseq, f)

        log.info('dumped glv.conf.refseq -> {}'.format(
            pickle_bgzip_path))


    def pick_refseq(self, chrom, start_coordinate, end_coordinate):
        ''' for refseq substr, etc...
        '''

        slice_stt = start_coordinate - 1
        slice_end = end_coordinate

        #   1   2   3   4   5   6   coordinate   3-5 tho
        # +---+---+---+---+---+---+
        # | 0 | 1 | 2 | 3 | 4 | 5 | idx
        # | P | y | t | h | o | n |
        # +---+---+---+---+---+---+
        # 0   1   2   3   4   5   6 slice        2-5
        #

        return self.refseq[chrom][slice_stt:slice_end]


    def get_fai_info(self, fai_bgzip_path):
        '''
        '''
# glv.conf.ref_fasta_fai
#chr01   43270923    7   60  61
#chr02   35937250    43992120    60  61
#chr03   36413819    80528332    60  61
#chr04   35502694    117549055   60  61
#chr05   29958434    153643468   60  61
#chr06   31248787    184101217   60  61
#chr07   29697621    215870825   60  61
#chr08   28443022    246063414   60  61
#chr09   23012720    274980494   60  61
#chr10   23207287    298376767   60  61
#chr11   29021106    321970850   60  61
#chr12   27531856    351475649   60  61

        # get chrom list from fai text
        df_fai = pd.read_csv(fai_bgzip_path, sep = '\t',
            header = None, index_col = None)

        # list of dictionary between chrom name and length
        ref_fasta_chrom_dict_list = list()
        # list of chrom name(string)
        ref_fasta_chrom_list = list()
        # list of start pos - end pos "chrom:from-to"
        ref_fasta_chrom_region_list = list()

        # print_list
        print_header = ['#no', 'chrom', 'start', 'end', 'length']
        # convert to [tsv]
        print_list = ['\t'.join(map(str, print_header))]

        genome_total_len = 0
        # 20210922

        chrom_dict = dict()
        #for row in df_fai.itertuples():
        for index, row in df_fai.iterrows():
            #row[0]: chrom, 'chr01'
            #row[1]: length, 43270923

            no = index + 1
            chrom = str(row[0])
            length = int(row[1])

            start = int(1)
            end = int(length)

            chrom_dict = {
                # string
                'chrom': chrom,
                'start': start,
                'end': end,
                'length': length,
            }

            # add length to total
            genome_total_len += length
            ref_fasta_chrom_dict_list.append(chrom_dict)

            # print_line
            pl = "{}\t{}\t{}\t{}\t{}".format(no, chrom, start, end, length)
            print_list += [pl]

            # string
            ref_fasta_chrom_list.append(chrom)
            region = "{}:{}-{}".format(chrom, start, end)
            ref_fasta_chrom_region_list.append(region)

        # add total length information
        # can get as 'genome_total_len'
        chrom_dict = {
            # string
            'chrom': glv.genome_total_len,
            'start': 1,
            'end': genome_total_len,
            'length': genome_total_len,
        }
        ref_fasta_chrom_dict_list.append(chrom_dict)

        # self.ref_bgzip_chrom_txt
        if self.ref_bgzip_chrom_txt_path.exists():

            log.info("found. {}".format(self.ref_bgzip_chrom_txt_path))

        else:

            log.info("not found. {}".format(self.ref_bgzip_chrom_txt_path))

            # write to vcf_sample_name_file
            with self.ref_bgzip_chrom_txt_path.open("w",
                encoding='utf-8') as f:
                f.write("{}\n".format("\n".join(print_list)))

            log.info("saved. {}".format(self.ref_bgzip_chrom_txt_path))

        # pathlib read_txt, print
        s = self.ref_bgzip_chrom_txt_path.read_text()
        mes = "fasta's chromosome information is here."
        log.info("{}\n{}\n\n{}".format(mes, self.ref_bgzip_chrom_txt_path, s))

        return ref_fasta_chrom_dict_list, \
            ref_fasta_chrom_list, \
            ref_fasta_chrom_region_list


