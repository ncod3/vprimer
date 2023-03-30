# -*- coding: utf-8 -*-

import sys
#import os
from pathlib import Path
import errno
import time

import logging
log = logging.getLogger(__name__)

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl


class Product(object):

    def __init__(self):

        pass


    def set_info(self,
            gno, ano, gname, chrom, pos, var_type,
            vseq, vseq_len, around_seq_pre, around_seq_aft):

        # group number 0 or 1
        self.gno = gno
        # allele number corresponding to the group
        self.ano = ano
        # group name
        self.gname = gname
        # chrom
        self.chrom = chrom
        # pos
        self.pos = pos
        # var type
        self.var_type = var_type

        # Variant sequence corresponding to allele number
        self.vseq = vseq
        # length of variant sequence
        self.vseq_len = vseq_len

        # SEQUENCE_TARGET and length
        self.seq_target = "{}{}{}".format(
            around_seq_pre, vseq, around_seq_aft)
        self.seq_target_len = len(self.seq_target)

        # |around_seq_pre_stt
        #     around_seq_pre_end|
        #                     pos|
        #                             |around_seq_aft_stt
        #                                 around_seq_aft_end|

        # relative position information
        rel_around_seq_pre_stt = 1
        rel_around_seq_pre_end = \
            rel_around_seq_pre_stt + len(around_seq_pre) - 1
        rel_pos = rel_around_seq_pre_end + 1
        rel_around_seq_aft_stt = \
            rel_pos + self.vseq_len
        rel_around_seq_aft_end = \
            rel_around_seq_aft_stt + len(around_seq_aft) - 1

        self.seq_target_rel_pos = "{}/{}/{}/{}/{}".format(
            rel_around_seq_pre_stt,
            rel_around_seq_pre_end,
            rel_pos,
            rel_around_seq_aft_stt,
            rel_around_seq_aft_end)


    def set_frag_pad(self, frag_pad_pre, frag_pad_aft):

        self.frag_pad_pre = frag_pad_pre
        self.frag_pad_aft = frag_pad_aft

        self.seq_template = "{}{}{}".format(
            self.frag_pad_pre,
            self.seq_target,
            self.frag_pad_aft)

        self.frag_pad_pre_len = len(self.frag_pad_pre)
        self.frag_pad_aft_len = len(self.frag_pad_aft)
        self.seq_template_len = len(self.seq_template)

        rel_around_seq_pre_stt, \
        rel_around_seq_pre_end, \
        rel_pos, \
        rel_around_seq_aft_stt, \
        rel_around_seq_aft_end = \
            Product.separate_seq_target_pos(
                self.seq_target_rel_pos)

        rel_frag_pad_pre_stt = 1
        rel_frag_pad_pre_end = \
            rel_frag_pad_pre_stt + self.frag_pad_pre_len - 1

        rel_around_seq_pre_stt += self.frag_pad_pre_len
        rel_around_seq_pre_end += self.frag_pad_pre_len
        rel_pos += self.frag_pad_pre_len
        rel_around_seq_aft_stt += self.frag_pad_pre_len
        rel_around_seq_aft_end += self.frag_pad_pre_len

        rel_frag_pad_aft_stt = rel_around_seq_aft_end + 1
        rel_frag_pad_aft_end = \
            rel_frag_pad_aft_stt + self.frag_pad_aft_len - 1

        self.seq_template_rel_pos = "{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
            rel_frag_pad_pre_stt,
            rel_frag_pad_pre_end,

            rel_around_seq_pre_stt,
            rel_around_seq_pre_end,
            rel_pos,
            rel_around_seq_aft_stt,
            rel_around_seq_aft_end,

            rel_frag_pad_aft_stt,
            rel_frag_pad_aft_end)


    @classmethod
    def separate_seq_template_pos(cls, seq_template_pos):

        frag_pad_pre_stt, \
        frag_pad_pre_end, \
        around_seq_pre_stt, \
        around_seq_pre_end, \
        pos, \
        around_seq_aft_stt, \
        around_seq_aft_end, \
        frag_pad_aft_stt, \
        frag_pad_aft_end = \
            map(int, seq_template_pos.split('/'))

        return \
            frag_pad_pre_stt, \
            frag_pad_pre_end, \
            around_seq_pre_stt, \
            around_seq_pre_end, \
            pos, \
            around_seq_aft_stt, \
            around_seq_aft_end, \
            frag_pad_aft_stt, \
            frag_pad_aft_end


    @classmethod
    def separate_seq_target_pos(cls, seq_target_pos):

        around_seq_pre_stt, \
        around_seq_pre_end, \
        pos, \
        around_seq_aft_stt, \
        around_seq_aft_end = \
            map(int, seq_target_pos.split('/'))

        return \
            around_seq_pre_stt, \
            around_seq_pre_end, \
            pos, \
            around_seq_aft_stt, \
            around_seq_aft_end

