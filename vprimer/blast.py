# -*- coding: utf-8 -*-

import sys
#import os
import errno
import re
from pathlib import Path

import logging
log = logging.getLogger(__name__)

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

import subprocess as sbp
import pandas as pd

class Blast(object):

    def __init__(self):
        pass

    @classmethod
    def primer_blast_check(cls,
            left_fasta_id, right_fasta_id,
            left_primer_seq, right_primer_seq):

        fasta_list = [">{}".format(left_fasta_id)]
        fasta_list += ["{}".format(left_primer_seq)]
        fasta_list += [">{}".format(right_fasta_id)]
        fasta_list += ["{}".format(right_primer_seq)]

        primer_fasta = '\n'.join(fasta_list)

        blast_check_result_list = cls._do_blastn_pipe(primer_fasta)
        return blast_check_result_list

    @classmethod
    def _do_blastn_pipe(cls, primer_fasta):

        # https://www.haya-programming.com/entry/2018/03/25/214957
        blastn_short = ['blastn']
        blastn_short += ['-db']
        blastn_short += ["{}".format(glv.conf.blastdb_path)]
        blastn_short += ['-num_threads']
        blastn_short += ["{}".format(glv.conf.blast_num_threads)]
        blastn_short += ['-word_size']
        blastn_short += ["{}".format(glv.conf.blast_word_size)]
        blastn_short += ['-ungapped']
        blastn_short += ['-task']
        blastn_short += ['blastn-short']

        blastn_short += ['-outfmt']
        outfmt = '6 qseqid sseqid qlen pident length mismatch'
        outfmt += ' gapopen qstart qend sstart send evalue sstrand'
        blastn_short += [outfmt]

        blastn_short_p = sbp.Popen(
            blastn_short,
            stdin=sbp.PIPE,
            stdout=sbp.PIPE)

        # https://minus9d.hatenablog.com/entry/2021/06/08/220614
        # res = subprocess.run(['python3', 'hello.py'],
        # capture_output=True, text=True)

        blastn_out = blastn_short_p.communicate(
            primer_fasta.encode())[0].decode()

        blast_check_result_list = cls._check_blast_alignment(blastn_out)

        return blast_check_result_list


    @classmethod
    def _check_blast_alignment(cls, blastn_out):

        blast_check_result_list = list()
        #print("{}".format(blastn_out))

        check_dict = dict()

# 0 qseqid # 1 sseqid # 2 qlen # 3 pident # 4 length # 5 mismatch
# 6 gapopen # 7 qstart # 8 qend # 9 sstart # 10 send
# 11 evalue # 12 sstrand

        for row in blastn_out.split('\n'):

            if row == '':
                continue

            item = row.split('\t')

            #log.debug("")
            #log.debug("start row {}".format(row))

            query_id, primer_chrom, primer_abs_stt_pos, \
                primer_abs_end_pos, primer_strand, \
                subject_id, query_length, alignment_length, \
                mismatches, gap_opens, \
                subject_abs_stt_pos, subject_abs_end_pos, \
                subject_strand = \
                    cls._get_align_info(item)

            #log.debug("query_length={}, alignment_length={}".format(
            #    query_length, alignment_length))
            #log.debug("mismatches={}, gap_opens={}".format(
            #    mismatches, gap_opens))

            if query_length != alignment_length or \
                    mismatches != 0 or gap_opens != 0:
                #log.debug("found mismatch continue")
                #log.debug("")
                continue

            #else:
            #    log.debug("not found mismatch continue")
            #    log.debug("")

            # check own alignment
            if cls._check_own_alignment(
                    primer_chrom,
                    primer_abs_stt_pos, primer_abs_end_pos,
                    primer_strand,
                    subject_id,
                    subject_abs_stt_pos, subject_abs_end_pos, \
                    subject_strand) == True:
                continue

            # 辞書を作成する
            align_info = "{}:{}:{}".format(
                subject_abs_stt_pos, subject_abs_end_pos, subject_strand)

            #log.debug("align_info {}".format(align_info))

            # キーが存在しない場合は、
            if not subject_id in check_dict:
                check_dict[subject_id] = dict()
                check_dict[subject_id]['plus'] = list()
                check_dict[subject_id]['minus'] = list()

            check_dict[subject_id][primer_strand].append(align_info)
            #log.debug("check_dict {}".format(check_dict))

        # primerのdistanceを確認する
        blast_check_result_list = cls._primer_distance_check(check_dict)
        #log.debug("distance_result {}".format(blast_check_result_list))

        return blast_check_result_list

    @classmethod
    def _check_own_alignment(
        cls, primer_chrom,
        primer_abs_stt_pos, primer_abs_end_pos,
        primer_strand,
        subject_id,
        subject_abs_stt_pos, subject_abs_end_pos,
        subject_strand):

        own = False

        check_stt = primer_abs_stt_pos
        check_end = primer_abs_end_pos

        #log.debug("{} {}".format(primer_strand, subject_strand))

        if primer_strand != subject_strand:
            check_stt = primer_abs_end_pos
            check_end = primer_abs_stt_pos

        if primer_chrom == subject_id and \
            check_stt == subject_abs_stt_pos and \
            check_end == subject_abs_end_pos:

            #log.debug("Me next {} q {} == s {} and q {} == s {}".format(
            #    primer_chrom,
            #    check_stt, subject_abs_stt_pos,
            #    check_end, subject_abs_end_pos))
            own = True

        #else:
        #    log.debug("NotMe {} q {} == {} s {} and q {} == s {}".format(
        #        primer_chrom,
        #        check_stt,
        #        subject_id,
        #        subject_abs_stt_pos,
        #        check_end, subject_abs_end_pos))

        return own


    @classmethod
    def _get_align_info(cls, item):

        query_id = str(item[0])

        primer_chrom, primer_abs_stt_pos, \
            primer_abs_end_pos, primer_strand = \
                cls._separate_primer_name(query_id)

        subject_id = str(item[1])
        query_length = int(item[2])
        alignment_length = int(item[4])
        mismatches = int(item[5])
        gap_opens = int(item[6])
        s_stt = int(item[9])
        s_end = int(item[10])
        subject_strand = str(item[12])

        # chrom:small-big:strand small always small < big
        subject_abs_stt_pos = s_stt
        subject_abs_end_pos = s_end
        if subject_strand == 'minus':
            subject_abs_stt_pos = s_end
            subject_abs_end_pos = s_stt

        return \
            query_id,  primer_chrom, primer_abs_stt_pos, \
            primer_abs_end_pos, primer_strand, \
            subject_id, query_length, alignment_length, \
            mismatches, gap_opens, \
            subject_abs_stt_pos, subject_abs_end_pos, \
            subject_strand


    @classmethod
    def _primer_distance_check(cls, check_dict):

        #log.debug("{}".format(check_dict))

        # 指定の距離
        blast_distance = glv.conf.blast_distance

        blast_check_result_list = list()
            # {
            #     'NC_028450.1':
            #         {
            #             'plus':
            #                 [
            #                     '9985:10009:plus',
            #                     '32680:32704:plus',
            #                     '56651:56675:plus',
            #                     '3033129:3033153:plus',
            #                     '3055745:3055769:plus',
            #                     '3067736:3067760:plus',
            #                     '3079717:3079741:plus'
            #                 ],
            #              'minus':
            #                 [
            #                     '10365:10341:minus',
            #                     '33060:33036:minus',
            #                     '45056:45032:minus',
            #                     '57031:57007:minus',
            #                     '3033509:3033485:minus',
            #                     '3056125:3056101:minus',
            #                     '3068116:3068092:minus',
            #                     '3080097:3080073:minus'
            #                 ]
            #         }
            # }

        # contigごとにplusのリストの方向と向かい合うminusのリストを調べて、
        # 距離を測り適用になる場合にリストに入れる。
        for contig in check_dict:
            #log.debug("(1) {}".format(contig))

            for plus_primer in check_dict[contig]['plus']:
                #log.debug("{}".format(plus_primer))
                p_stt, p_end, p_strand = plus_primer.split(':')
                p_stt = int(p_stt)
                p_end = int(p_end)

                #log.debug("(2) \t{} p_stt={} p_end={} p_strand={}".format(
                #    plus_primer, p_stt, p_end, p_strand))

                for minus_primer in check_dict[contig]['minus']:
                    #log.debug("\t{}".format(minus_primer))
                    m_stt, m_end, m_strand = minus_primer.split(':')
                    m_stt = int(m_stt)
                    m_end = int(m_end)
                    #log.debug(
                    #    "(3) \t\t{} m_stt={} m_end={} m_strand={}".format(
                    #        minus_primer, m_stt, m_end, m_strand))

                    if p_strand != m_strand:
                        # 逆である。
                        # 向かい合っているかどうか
                        #log.debug("(4) \t\t\t{} not {} p={} m={}".format(
                        #    p_strand, m_strand, plus_primer, minus_primer))
                        # (4) plus not minus p=9985:10009:plus
                        # m=10365:10341:minus

                        dist_start = 0
                        dist_end = blast_distance + 1

                        if p_strand == 'plus':

                            # p=p
                            #     p_end| |m_stt
                            # +++++++++> <--------- ok
                            if p_end < m_stt:
                                # ok
                                dist_start = p_stt
                                dist_end = m_end

                        else:
                            # p=m
                            #     m_end| |p_stt
                            # ---------> <+++++++++ ok
                            if m_end < p_stt:
                                # ok
                                dist_start = m_stt
                                dist_end = p_end

                        distance = dist_end - dist_start
                        if distance <= blast_distance:
                            alt = "{}:{}-{}({})".format(
                                contig, dist_start,
                                dist_end, distance)
                            blast_check_result_list.append(alt)
                            #log.debug("{}".format(alt))

        return blast_check_result_list


    @classmethod
    def _separate_primer_name(cls, primer_name):

        # [NC_028450.1]44676.44700.plus
        #chrom_str, remain_str = primer_name.split('}')

        #chrom = chrom_str.lstrip('{')
        #abs_primer_stt_pos, abs_primer_end_pos, strand = \
        #remain_str.split('.')

        #s = 'NC_0:28450.1:44676-44700:plus'
        m = re.match(r'^(.*):([0-9]+)-([0-9]+):([a-z]+)$', primer_name)
        #print(m.groups())
        #('NC_0:28450.1', '44676', '44700', 'plus')

        #log.debug("{}".format(primer_name))
        #log.debug("{}".format(m))
        #log.debug("{}".format(m[0]))
        #log.debug("{}".format(m[1]))


        chrom = str(m[1])

        abs_primer_stt_pos = int(m[2])
        abs_primer_end_pos = int(m[3])
        strand = str(m[4])

        #log.debug("{}".format(type(m[1])))
        #sys.exit(1)

        return \
            chrom, \
            abs_primer_stt_pos, \
            abs_primer_end_pos, \
            strand


    @classmethod
    def makeblastdb(cls):

        # glv.conf.blastdb_title
        # glv.conf.blastdb_path

        blastdb_nsq = Path("{}{}".format(glv.conf.blastdb_path, ".nsq"))
        if blastdb_nsq.exists():
            return

        bgzip = "bgzip -cd -@ {} {}"
        mkdb = "makeblastdb -in - -title {} -dbtype nucl -out {}"
        cmd1 = "{} | {}".format(
            bgzip.format(
                glv.conf.parallel_full_thread,
                glv.conf.ref_bgzip_path),
            mkdb.format(
                glv.conf.blastdb_title,
                glv.conf.blastdb_path))

        utl.try_exec(cmd1)

