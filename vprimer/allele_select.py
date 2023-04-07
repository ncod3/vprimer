import sys
#import os
from pathlib import Path
import errno
import time
import re
import pprint

import logging
log = logging.getLogger(__name__)

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

class AlleleSelect(object):

    def __init__(self, min_indel_len, max_indel_len, pick_mode):

        # indel size threshold
        self.min_indel_len = min_indel_len
        self.max_indel_len = max_indel_len

        self.pick_mode = pick_mode


    def set_diff_allele_combination(self,
        record, group_tuple, alstr_tuple, member_dict):

        ''' Select different allele combination among 2x2 allele
            For each record, create an instance of AlleleSelect class
            and process it.
        '''

        #print()
        #print("in AlleleSelect.set_diff_allele_combination")
        #print("group_tuple={}".format(group_tuple))
        #print("alstr_tuple={}".format(alstr_tuple))
        #print("member_dict={}".format(member_dict))
        #print()

        self.record = record

        self.group_list = list(group_tuple)
        #print("self.group_list={}".format(self.group_list))
        self.member_dict = member_dict
        #print("self.member_dict={}".format(self.member_dict))

        self.alstr_gno = list(alstr_tuple) # list of string
        #print("self.alstr_gno={}".format(self.alstr_gno))

        self.chrom = self.record.CHROM
        self.pos = self.record.POS
        self.alt_var_cnt = len(self.record.ALT)   # alt variant count

        # variation sequences(str) list ordered by allele number [0,1..]
        self.vseq_ano = [self.record.REF]    # 'C' (str)
        [self.vseq_ano.append(alt.value) for alt in self.record.ALT]
        self.vseq_ano_str = ','.join(self.vseq_ano) # 'C,A'

        # append vseq length to list ordered by allele number
        #[self.len_vseq_ano.append(len(vseq)) for vseq in self.vseq_ano]
        self.len_vseq_ano = list()
        for vseq in self.vseq_ano:
            if vseq == '.':
                self.len_vseq_ano.append(0) # '.', None is zero length
            else:
                self.len_vseq_ano.append(len(vseq))

        # Transform two groups of alstr for ease of use
        # alstr '00'
        self.g0_alstr = self.alstr_gno[0]
        self.g1_alstr = self.alstr_gno[1]

        #        0,         -1  int
        self.g0_a0, self.g0_a1 = AlleleSelect.sepal(self.g0_alstr, 'int')
        self.g1_a0, self.g1_a1 = AlleleSelect.sepal(self.g1_alstr, 'int')

        # length int
        self.g0_a0L = self.len_vseq_ano[self.g0_a0]
        self.g0_a1L = self.len_vseq_ano[self.g0_a1]
        self.g1_a0L = self.len_vseq_ano[self.g1_a0]
        self.g1_a1L = self.len_vseq_ano[self.g1_a1]

        #    '0/0'  genotype by string
        self.g0_gt = AlleleSelect.sepal(self.g0_alstr, 'gt')
        self.g1_gt = AlleleSelect.sepal(self.g1_alstr, 'gt')

        # ano := allele number as int 0, 1, -1
        # ano__gno_aix      [[0, 0], [-1, -1]]
        self.ano__gno_aix = [[self.g0_a0, self.g0_a1],
                             [self.g1_a0, self.g1_a1]]

        # len := length of ano(str)
        # len__gno_aix      [[1, 1], [0, 0]]
        self.len__gno_aix = [[self.g0_a0L, self.g0_a1L],
                             [self.g1_a0L, self.g1_a1L]]

        # make a list for self.altype_gno
        self.altype_gno = list()
        for gno in range(2):
            # If two alleles are the same
            if self.ano__gno_aix[gno][0] == self.ano__gno_aix[gno][1]:
                # set homo to list of altype
                self.altype_gno.append(glv.AL_HOMO)
            else:
                self.altype_gno.append(glv.AL_HETERO)


        # get allele combination for marker among four alleles in two sample
        self.segr_ptn, \
        self.diff_allele_set, \
        self.diff_allele_cnt = \
            self.get_segregation_pattern()

        # Create lines for valid diff allele combinations.
        self.var_lines = list()
        self.var_types = list()

        # メンバーにアクセスしたい。
        for cnt, diff_allele in enumerate(self.diff_allele_set, 1):

            # get var_type
            # グループ名から、メンバにアクセスしたい
            var_type, variant_line = \
                self.construct_variant_line(cnt, diff_allele)

            self.var_lines.append(variant_line)
            self.var_types.append(var_type)


    def get_mk_type_str(self, var_type):

        #print("in _get_mk_type_str")
        #print("var_type={}".format(var_type))
        #print("self.pick_mode={}".format(self.pick_mode))
        #print()

        '''
        Table of mk_type
        |------------|------------|-----------|----------|----------|
        |            | pick_mode  |           |          |          |
        |------------|------------|-----------|----------|----------|
        | var_type   | MODE_INDEL | MODE_CAPS | MODE_OOR | MODE_SNP |
        |------------|------------|-----------|----------|----------|
        | INDEL      | MK_INDEL   | -         | -        | -        |
        | SNP        | -          | MK_CAPS   | -        | MK_SNP   |
        | MIND       | -          | MK_CAPS   | -        | MK_SNP   |
        | MNV        | -          | MK_CAPS   | -        | MK_SNP   |
        | OutOfRange | -          | -         | MK_INDEL | -        |
        |------------|------------|-----------|----------|----------|
        '''

        mk_type_str = ''

        # indel+caps+oor
        for pick_mode in self.pick_mode.split('+'):

            #print("var_type={}".format(var_type))
            #print("pick_mode={}".format(pick_mode))

            mk_type = glv.MK_NOTYPE
            #print("mk_type={}".format(mk_type))

            if var_type == glv.INDEL:

                if pick_mode == glv.MODE_INDEL:
                    mk_type = glv.MK_INDEL

            elif var_type == glv.SNP or \
                var_type == glv.MIND or \
                var_type == glv.MNV:

                if pick_mode == glv.MODE_CAPS:
                    mk_type = glv.MK_CAPS
                elif pick_mode == glv.MODE_SNP:
                    mk_type = glv.MK_SNP

            elif var_type == glv.OutOfRange:

                if pick_mode == glv.MODE_OOR:
                    mk_type = glv.MK_INDEL

            #print("mk_type={}".format(mk_type))
            #print()

            if mk_type != glv.MK_NOTYPE:
                mk_type_str += "{},".format(mk_type)

        mk_type_str = re.sub(r",$", "", mk_type_str) 
        #print("var_type={}, mk_type_str={}".format(var_type, mk_type_str))
        #sys.exit(1)

        return mk_type_str


    def is_var_type_in_pick_mode(self, var_type):

        # self.pick_mode: indel+caps+snp+oor
        # indel, caps, snp
        included = False
        mode = 0

        if var_type == glv.INDEL:
            if glv.MODE_INDEL in self.pick_mode:
                mode = 1
                included = True

        elif var_type == glv.SNP:
            if glv.MODE_SNP in self.pick_mode or \
                glv.MODE_CAPS in self.pick_mode:
                mode = 2
                included = True

        elif var_type == glv.MNV or \
            var_type == glv.MIND:
            if glv.MODE_CAPS in self.pick_mode:
                mode = 3
                included = True

        else:
            if glv.MODE_OOR in self.pick_mode:
                included = True
                mode = -1
            else:
                included = False

        #print("{}, {}, included={}".format(
        #    var_type, self.pick_mode, mode))

        return included


    def get_segregation_pattern(self):

        segr_ptn = glv.segr_ptn_NOP
        diff_allele_set = list()
        diff_allele_cnt = 0

        # 1.homo vs homo: int
        if utl.is_homo_homo(
            self.g0_a0, self.g0_a1, self.g1_a0, self.g1_a1):
            # AA,BB
            #   hoho        1     00/11 0,1
            segr_ptn = glv.segr_ptn_HOMO_HOMO
            #                           [      AA0,       BB0]
            diff_allele_set.append([self.g0_a0, self.g1_a0])

        # 2.homo vs hetero
        elif utl.is_homo_hetero(
            self.g0_a0, self.g0_a1, self.g1_a0, self.g1_a1):

            if utl.is_share(self.g0_a0, self.g0_a1, self.g1_a0, self.g1_a1):
                # AA,AB
                #   hohe_s      1     00/01 0,1
                segr_ptn = glv.segr_ptn_HOMO_HETERO_SHARE

                if self.altype_gno[0] == glv.AL_HETERO:
                    # AB,AA(BB)
                    if self.g0_a0 != self.g1_a0:
                        # AB,BB                     [      AB0,       BB0]
                        diff_allele_set.append([self.g0_a0, self.g1_a0])
                    else:
                        # AB,AA                     [      AB1,       AA0]
                        diff_allele_set.append([self.g0_a1, self.g1_a0])

                else:
                    # AA(BB),AB
                    if self.g0_a0 != self.g1_a0:
                        # BB,AB                     [      BB0,       AB0]
                        diff_allele_set.append([self.g0_a0, self.g1_a0])
                    else:
                        # AA,AB                     [      AA0,       AB1]
                        diff_allele_set.append([self.g0_a0, self.g1_a1])

            else:
                # AA,BC
                #   hohe_n      2     00/12 0,1 0,2
                segr_ptn = glv.segr_ptn_HOMO_HETERO_NOT_SHARE

                if self.altype_gno[0] == glv.AL_HETERO:
                    # BC,AA -> [B,A] [C,A]
                    diff_allele_set.append([self.g0_a0, self.g1_a0])
                    diff_allele_set.append([self.g0_a1, self.g1_a0])

                else:
                    # AA,BC -> [A,B] [A,C]
                    diff_allele_set.append([self.g0_a0, self.g1_a0])
                    diff_allele_set.append([self.g0_a0, self.g1_a1])

        # 3.hetero vs hetero
        else:

            if utl.is_share(self.g0_a0, self.g0_a1, self.g1_a0, self.g1_a1):
                # AB,AC
                #   hehe_s      3     01/02 0,2 1,0 1,2
                segr_ptn = glv.segr_ptn_HETERO_HETERO_SHARE


                # 01,02
                if self.g0_a0 == self.g1_a0:
                    # 0/2, 1/0, 1/2
                    #diff_allele_set.append([self.g0_a0, self.g1_a0])
                    diff_allele_set.append([self.g0_a0, self.g1_a1])
                    diff_allele_set.append([self.g0_a1, self.g1_a0])
                    diff_allele_set.append([self.g0_a1, self.g1_a1])

                # 01,20
                elif self.g0_a0 == self.g1_a1:
                    # 0/2, 1,2, 1,0
                    diff_allele_set.append([self.g0_a0, self.g1_a0])
                    #diff_allele_set.append([self.g0_a0, self.g1_a1])
                    diff_allele_set.append([self.g0_a1, self.g1_a0])
                    diff_allele_set.append([self.g0_a1, self.g1_a1])

                # 10,02
                elif self.g0_a1 == self.g1_a0:
                    # 1,0, 1,2, 0,2
                    diff_allele_set.append([self.g0_a0, self.g1_a0])
                    diff_allele_set.append([self.g0_a0, self.g1_a1])
                    #diff_allele_set.append([self.g0_a1, self.g1_a0])
                    diff_allele_set.append([self.g0_a1, self.g1_a1])

                # 10,20
                elif self.g0_a1 == self.g1_a1:
                    # 1,2, 1,0, 0,2
                    diff_allele_set.append([self.g0_a0, self.g1_a0])
                    diff_allele_set.append([self.g0_a0, self.g1_a1])
                    diff_allele_set.append([self.g0_a1, self.g1_a0])
                    #diff_allele_set.append([self.g0_a1, self.g1_a1])

            else:
                # AB,CD
                #   hehe_n      4     01/23 0,2 0,3 1,2 1,3
                segr_ptn = glv.segr_ptn_HETERO_HETERO_NOT_SHARE
                # all combination 4 type
                #                                   A.         C.
                diff_allele_set.append([self.g0_a0, self.g1_a0])
                #                                   A.         .D
                diff_allele_set.append([self.g0_a0, self.g1_a1])
                #                                   .B         C.
                diff_allele_set.append([self.g0_a1, self.g1_a0])
                #                                   .B         .D
                diff_allele_set.append([self.g0_a1, self.g1_a1])


        diff_allele_cnt = len(diff_allele_set)
        return segr_ptn, diff_allele_set, diff_allele_cnt


    def construct_variant_line(self, cnt, diff_allele):

        ''' self.diff_allele_cnt is the total number of different allele
            combinations between different genotypes of two individuals.
            Cnt indicates the order of the total number.
            This one process becomes one variant line.
            Genotype(alstr) corresponds to one group name.
        '''

        #print("in AlleleSelect._construct_variant_line")
        #print("self.diff_allele_cnt={}".format(self.diff_allele_cnt))
        #print("cnt={}".format(cnt))
        #print("diff_allele={}".format(diff_allele))
        #print()
        #print("self.group_list={}".format(self.group_list))
        #print("self.member_dict={}".format(self.member_dict))

        variant_line_list = list()

        # diff_allele: Elements of this list are of type integer.
        # If the allele number is -1, After this you will get an error.
        g0_ano = diff_allele[0]
        g1_ano = diff_allele[1]

        # vseq len
        g0_vseq_len = self.len_vseq_ano[g0_ano]
        g1_vseq_len = self.len_vseq_ano[g1_ano]

        # target group name string 'a,b'
        targ_grp = "{},{}".format(self.group_list[0], self.group_list[1])

        # target group allele number string '1,0'
        targ_ano = "{},{}".format(g0_ano, g1_ano)

        # variant sequence 
        vseq_gno_str = "{},{}".format(
            self.vseq_ano[g0_ano],
            self.vseq_ano[g1_ano])

        # gts_segr_lens 11/00,hoho_1,1.1/1.1
        gts_segr_lens = self.make_gts_segr_lens_id()

        # var_type, longest_gno, longest_len, diff_len
        var_type, longest_gno, longest_len, diff_len = \
            self.get_variant_type(g0_ano, g1_ano)

        # 2022-10-27 get mk_type_str
        mk_type_str = self.get_mk_type_str(var_type)

        # set number, diff_allele_cnt 1/1
        set_n = "{}/{}".format(cnt, self.diff_allele_cnt)

        # len_g0g1_dif_long 1,1,0,0
        len_g0g1_dif_long = "{},{},{},{}".format(
            g0_vseq_len, g1_vseq_len, diff_len, longest_gno)

        # vseq_gno_str C,A
        vseq_gno_str = "{},{}".format(
            self.vseq_ano[g0_ano],
            self.vseq_ano[g1_ano])

        # ---------------------------------------
        # Synchronize with outlist.py
        variant_line_list += [self.chrom]
        variant_line_list += [self.pos]
        variant_line_list += [targ_grp]
        variant_line_list += [targ_ano]
        variant_line_list += [vseq_gno_str]
        variant_line_list += [gts_segr_lens]
        variant_line_list += [var_type]
        # 2022-10-27
        variant_line_list += [mk_type_str]
        # ---------------------
        variant_line_list += [set_n]
        variant_line_list += [len_g0g1_dif_long]
        variant_line_list += [self.vseq_ano_str.upper()]

        # ---------------------
        # add members for auto_group
        auto_grp0 = "-"
        auto_grp1 = "-"

        if glv.conf.is_auto_group:

            gname = self.group_list[0]
            auto_grp0 = [",".join(self.member_dict[gname])]

            gname = self.group_list[1]
            auto_grp1 = [",".join(self.member_dict[gname])]

        variant_line_list += auto_grp0
        variant_line_list += auto_grp1


        return var_type, '\t'.join(map(str, variant_line_list))


    def make_gts_segr_lens_id(self):

        gts_segr_lens = "{}/{},{},{}.{}/{}.{}".format(
            self.alstr_gno[0],
            self.alstr_gno[1],
            self.segr_ptn,
            self.len__gno_aix[0][0],
            self.len__gno_aix[0][1],
            self.len__gno_aix[1][0],
            self.len__gno_aix[1][1])

        return gts_segr_lens


    def get_variant_type(self, g0_ano, g1_ano):

        # MODE
        #       type
        # glv.MODE_INDEL  = 'indel'
        #       glv.INDEL
        # glv.MODE_SNP    = 'snp'
                # glv.SNP
        # glv.MODE_CAPS   = 'caps'
                # glv.SNP
                # glv.MNV
                # glv.MIND
        # nop
                # glv.OutOfRange

        #print()
        #print("in _get_variant_type")

        # It exceeds the size of the longer indel, so it is not targeted.
        var_type = glv.OutOfRange

        longest_gno = glv.SAME_LENGTH
        longest_len = 0
        diff_len = 0

        g0_vseq_len = self.len_vseq_ano[g0_ano]
        g1_vseq_len = self.len_vseq_ano[g1_ano]

        #print("g0_vseq_len={}, g1_vseq_len={}".format(
        #    g0_vseq_len, g1_vseq_len))

        # decide the longer size and group
        longest_gno = 0
        longest_len = g0_vseq_len

        if g0_vseq_len < g1_vseq_len:
            longest_gno = 1
            longest_len = g1_vseq_len

        diff_len = abs(g0_vseq_len - g1_vseq_len)

        #print("longest_gno={}, longest_len={}, diff_len={}".format(
        #    longest_gno, longest_len, diff_len))

        #--------------------------------------------------------
        # if same length
        if diff_len == 0:
            if g0_vseq_len == 1:
                var_type = glv.SNP
            else:
                var_type = glv.MNV

        # if diff_len is between min and max
        elif self.min_indel_len <= diff_len and \
            diff_len <= self.max_indel_len:
            var_type = glv.INDEL

        # mini indel
        elif diff_len < self.min_indel_len:
            var_type = glv.MIND

        else:
            var_type = glv.OutOfRange

        #print("var_type={}".format(var_type))

        return var_type, longest_gno, longest_len, diff_len


    @classmethod
    def sepal(cls, alstr, mode):

        # alstr is string '00', '..'
        alstr_a0, alstr_a1 = list(alstr)

        if mode == 'str':

            return alstr_a0, alstr_a1

        elif mode == 'int':
            
            alstr_a0_int = -1
            alstr_a1_int = -1

            if alstr_a0 != '.':
                alstr_a0_int = int(alstr_a0)

            if alstr_a1 != '.':
                alstr_a1_int = int(alstr_a1)

            return alstr_a0_int, alstr_a1_int

        elif mode == 'gt':

            return "{}/{}".format(alstr_a0, alstr_a1)


    @classmethod
    def record_call_for_sample(cls, record, sample):
        ''' always return alstr '00' '01' '..'
        '''

        fullname = utl.get_fullname(sample)

        # for REF, '0/0'
        if sample == 'ref':
            # always allele no is 0
            s_0_str = '0'
            s_1_str = '0'

        else:
            s_0_str = '.'   # for None
            s_1_str = '.'   # for None
            
            # integer or None
            s_0_int_or_None = record.call_for_sample[fullname].gt_alleles[0]
            s_1_int_or_None = record.call_for_sample[fullname].gt_alleles[1]

            if s_0_int_or_None is not None:
                s_0_str = str(s_0_int_or_None)

            if s_1_int_or_None is not None:
                s_1_str = str(s_1_int_or_None)

        # alstr is the glue between two allele digits.
        alstr = "{}{}".format(s_0_str, s_1_str)

        return alstr


