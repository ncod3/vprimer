# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
import errno
import pprint
import re
import copy

import logging
log = logging.getLogger(__name__)

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

# 20231120
# biopython 1.76 のインストールを不要とする一時措置
app_dir = os.path.dirname(os.path.realpath(__file__))
#print(app_dir)
# Bio, 1.76 を、このディレクトリから読み出す
sys.path.insert(0, app_dir)

from Bio import Restriction
from Bio.Seq import Seq

# biopython <= 1.76 for IUPACAmbiguousDNA()
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA

from vprimer.allele_select import AlleleSelect
from vprimer.product import Product

class EvalVariant(object):

    def __init__(self, enzyme_name_list):

        self.enzyme_name_list = enzyme_name_list

        # for make_seq_template_ref()
        self.fragment_pad_len = 0

        self.abs_frag_pad_pre_stt = 0
        self.abs_frag_pad_pre_end = 0

        self.abs_frag_pad_aft_stt = 0
        self.abs_frag_pad_aft_end = 0

        self.seq_template_ref_abs_pos = ''
        self.seq_template_ref_rel_pos = ''

        self.SEQUENCE_TARGET = ''

        self.frag_pad_pre = ''
        self.frag_pad_aft = ''

        self.seq_template_ref = ''

        self.frag_pad_pre_len = 0
        self.frag_pad_aft_len = 0
        self.seq_template_ref_len = 0


    #def evaluate_for_marker(self, variant_df_row, distin_file):
    def evaluate_for_marker(self, variant_df_row, distin_gdct):
        ''' 1 variant 1 exec for palallel
        '''

        # hdr_dict is a dictionary for translaing the header names
        # to row column_no
        hdr_dict = distin_gdct['variant']['hdr_dict']
        #hdr_dict = utl.remove_deepcopy_auto_grp_header_dict(
        #    distin_gdct['variant']['hdr_dict'])

        #print("in evaluate_for_marker")
        #print(hdr_dict)
        #sys.exit(1)


        # Read the data from the 010_variant file, save it locally,
        #   and split the variables as needed
        self.marker_id, \
        self.chrom, \
        self.pos, \
        self.targ_grp, \
        self.g0_name, \
        self.g1_name, \
        self.targ_ano, \
        self.g0_ano, \
        self.g1_ano, \
        self.vseq_gno_str, \
        self.gts_segr_lens, \
        self.var_type, \
        self.mk_type, \
        self.set_n, \
        self.marker_info, \
        self.vseq_lens_ano_str, \
        self.enzyme_name, \
        self.digest_pattern, \
        self.target_gno, \
        self.target_len, \
        self.auto_grp0, \
        self.auto_grp1 = \
            utl.get_basic_primer_info(variant_df_row, hdr_dict)

        #self.notice,

        self.gname_gno = [self.g0_name, self.g1_name]
        self.ano_gno = [self.g0_ano, self.g1_ano]
        self.set_my_no, self.set_total_no = map(int, self.set_n.split('/'))

        # 1,1,0,-1
        self.len_g0g1_dif_long = str(
            variant_df_row[hdr_dict['len_g0g1_dif_long']])
        # g0_len, g1_len, diff_len, long_gno
        self.g0_len, self.g1_len, self.diff_len, self.long_gno = \
            map(int, self.len_g0g1_dif_long.split(','))

        # T,G access to all vseq
        self.vseq_ano_str = str(variant_df_row[hdr_dict['vseq_ano_str']])
        self.vseq_ano = self.vseq_ano_str.split(',')
        self.vseq_lens_ano = [len(vseq_ano) for vseq_ano in self.vseq_ano]

        # short_gno
        self.long_gno = -1
        self.short_gno = -1
        if self.long_gno == glv.SAME_LENGTH:
            self.long_gno = 0
            self.short_gno = 1
        else:
            self.short_gno = 0 if self.long_gno == 1 else 1

        self.longer_len = self.vseq_lens_ano[0]
        self.shorter_len = self.vseq_lens_ano[1]

        # Cut out two around_seq before and after the REF variant.
        self.vseq_ref, \
        self.vseq_ref_len, \
        self.abs_around_seq_pre_stt, \
        self.abs_around_seq_pre_end, \
        self.abs_around_seq_aft_stt, \
        self.abs_around_seq_aft_end, \
        self.around_seq_pre, \
        self.around_seq_pre_len, \
        self.around_seq_aft, \
        self.around_seq_aft_len, \
        self.seq_target_ref, \
        self.seq_target_ref_len = \
            self.pick_ref_around_seq()

        # Product()
        # Hold related sequences for each group to be compared.
        self.g0_product = Product()
        self.g1_product = Product()
        self.gr_product = [self.g0_product, self.g1_product]

        for gno in range(2):
            ano = self.ano_gno[gno]
            self.gr_product[gno].set_info(
                gno,
                ano,
                self.gname_gno[gno],
                self.chrom,
                self.pos,
                self.var_type,
                self.vseq_ano[ano],
                self.vseq_lens_ano[ano],
                self.around_seq_pre,
                self.around_seq_aft,
            )


    def set_mk_type(self, mk_type):

        # for multiple mk_type: CAPS,SNP
        self.mk_type = mk_type
        

    def check_caps(self):
        '''
        '''

        marker_available = False

        caps_checked_list = list()

        # If you need a detailed report of the enzyme,
        # Specify the command parameter analyse_caps as True.
        mes_list = list()
        mes_list = ["\ntest start\n"]

        for gno in range(2):
            mes_list += self.analong_header(gno, mes_list)

            # Check the effect of enzyme on two group sequences
            # caps_check_dict
            # caps_check_dict[enzyme_string] = {
            #     'ResType': enzyme_RestrictionType,
            #     'result': caps_ResTyp_dict[enzyme_RestrictionType],
            # }
            caps_check_dict, \
            enzyme_map_txt = \
                self.check_effect_of_enzyme(
                    self.gr_product[gno].seq_target,
                    self.enzyme_name_list)

            mes_list += ["{}".format(enzyme_map_txt)]
            caps_checked_list.append(caps_check_dict)

        mes_list += ["\ntest end\n"]

        #log.debug("\n{}".format(pprint.pformat(mes_list)))

        # Compare the result of caps_check_dict to determine
        # if it is available in caps
        self.caps_found = \
            self.compare_digestion_of_enzymes(caps_checked_list)

        if self.caps_found > 0:
            marker_available = True
            mes_list += ["caps is available {}".format(self.caps_found)]

            for enzyme in self.caps_result.keys():
                enz_info = "{} {} {} {} {}".format(
                    enzyme,
                    self.caps_result[enzyme]['digested_gno'],
                    self.caps_result[enzyme]['found_pos'],
                    self.caps_result[enzyme]['digest_pattern'],
                    self.caps_result[enzyme]['digested_pos'])

            mes_list += [enz_info]

        else:    
            marker_available = False
            mes_list += ["caps is not available {}".format(self.caps_found)]

        mes_list += ["<><><><><><><><><><><><><><><><><>\n\n"]


        if glv.conf.analyse_caps == True:
            mes_line = "\n".join(mes_list)
            log.info("\n{}".format(mes_line))

        return marker_available


    def compare_digestion_of_enzymes(self, caps_checked_list):
        '''
        '''

        # caps_checked_list: Digest status of each group
        list_0 = list(caps_checked_list[0].keys())
        list_1 = list(caps_checked_list[1].keys())

        #pprint.pprint(caps_checked_list)
        #print(list_0)
        #print(list_1)

        # xor list
        uniq_list = list(set(list_0) ^ set(list_1))

        self.caps_result = dict()

        # type(BsmFI) RestrictionType
        for enzyme_name in uniq_list:

            digested_gno = 0

            if enzyme_name in list_1:
                digested_gno = 1

            enz_res_type = \
                caps_checked_list[digested_gno][enzyme_name]['ResType']
            result_list = \
                caps_checked_list[digested_gno][enzyme_name]['res_list']

            digest_pattern = enz_res_type.elucidate()
            found_pos = int(result_list[0])

            # digested_pos
            digested_pos = 0
            pattern_5_digest = ""

            if "_" in digest_pattern:
                pattern_5_digest = re.sub(r"_", "", digest_pattern)
                pos_0 = pattern_5_digest.find("^")
                if pos_0 != -1:
                    # Last position remaining on the 5'side
                    # AAT^_ATT | AAT^ATT -> 3
                    digested_pos = pos_0

            # new
            self.caps_result[enzyme_name] = {
                'digested_gno':     digested_gno,
                'found_pos':        found_pos,
                'digest_pattern':   digest_pattern,
                'digested_pos':     digested_pos}
            #log.debug("{} | {} -> {}".format(
            #    digest_pattern, pattern_5_digest, digested_pos))

        caps_found = len(self.caps_result)
        return caps_found


    def check_effect_of_enzyme(self, seq_target, enzyme_name_list):
        ''' http://biopython.org/DIST/docs/cookbook/Restriction.html
        biopython <= 1.76 for IUPACAmbiguousDNA()
        '''

        caps_ResTyp_dict = dict()
        caps_check_dict = dict()
        enzyme_map_txt = ""

        # 4.1 Setting up an Analysis
        # 4.2 Full restriction analysis
        multi_site_seq = Seq(seq_target, IUPACAmbiguousDNA())
        rb = Restriction.RestrictionBatch(enzyme_name_list)
        Analong = Restriction.Analysis(rb, multi_site_seq)

        # 4.5 Fancier restriction analysis
        #
        # full()
        #   all the enzymes in the RestrictionBatch
        #   {KpnI: [], EcoRV: [], EcoRI: [33]}
        # with_sites()
        #   output only the result for enzymes which have a site
        #   result_dict = {EcoRI: [33]}

        caps_ResTyp_dict = Analong.with_sites()

        # make dictionary as string enzyme name
        for enzyme_RestrictionType in caps_ResTyp_dict.keys():
            enzyme_string = str(enzyme_RestrictionType)

            # caps_check_dict
            caps_check_dict[enzyme_string] = {
                'ResType': enzyme_RestrictionType,
                'res_list': caps_ResTyp_dict[enzyme_RestrictionType],
            }

        # detail information: make a restriction map of a sequence
        if glv.conf.analyse_caps == True:
            Analong.print_as('map')
            enzyme_map_txt_all = Analong.format_output()
            enzyme_map_txt = ""

            for line in enzyme_map_txt_all.split('\n'):
                if " Enzymes which " in line:
                    break
                enzyme_map_txt += "{}\n".format(line)

            enzyme_map_txt += "caps_check_dict={}".format(
                caps_check_dict)

        return caps_check_dict, \
            enzyme_map_txt

            
    def analong_header(self, gno, mes_list):
        '''
        '''

        m_list = list()
        m_list = ["gno={}, chrom={}, pos={}".format(gno,
            self.gr_product[gno].chrom, self.gr_product[gno].pos)]
        m_list += ["seq_target={}".format(self.gr_product[gno].seq_target)]
        m_list += ["seq_target_len={}\n".format(
            len(self.gr_product[gno].seq_target))]

        return m_list



    def pick_ref_around_seq(self):
        ''' Cut out two around_seq before and after the REF variant.
        '''

        #-------------------------------------
        # around_seq is based on vseq_ano[0]
        vseq_ref = self.vseq_ano[0]
        vseq_ref_len = len(vseq_ref)

        # abs pos決め
        # pos=60, 60-1=59
        abs_around_seq_pre_end = self.pos - 1
        # 59-10+1 = 50
        abs_around_seq_pre_stt = \
            abs_around_seq_pre_end - glv.AROUND_SEQ_LEN + 1
        # 60+16 = 76
        # 60+1 = 61
        abs_around_seq_aft_stt = self.pos + vseq_ref_len
        # 76+10-1=85
        abs_around_seq_aft_end = \
            abs_around_seq_aft_stt + glv.AROUND_SEQ_LEN - 1
        # preの切り出し

        #for ch in glv.conf.refseq.keys():
        #    print("chrom={}".format(ch))

        around_seq_pre = glv.conf.pick_refseq(
            self.chrom,
            abs_around_seq_pre_stt,
            abs_around_seq_pre_end).upper()
        #sys.exit(1)

        # aftの切り出し
        around_seq_aft = glv.conf.pick_refseq(
            self.chrom,
            abs_around_seq_aft_stt,
            abs_around_seq_aft_end).upper()

        around_seq_pre_len = len(around_seq_pre)
        around_seq_aft_len = len(around_seq_aft)

        seq_target_ref = "{}{}{}".format(
            around_seq_pre,
            vseq_ref,
            around_seq_aft)

        seq_target_ref_len = len(seq_target_ref)

        return \
            vseq_ref, \
            vseq_ref_len, \
            abs_around_seq_pre_stt, \
            abs_around_seq_pre_end, \
            abs_around_seq_aft_stt, \
            abs_around_seq_aft_end, \
            around_seq_pre, \
            around_seq_pre_len, \
            around_seq_aft, \
            around_seq_aft_len, \
            seq_target_ref, \
            seq_target_ref_len


    def make_seq_template_ref(self):
        '''
        '''

        #self.seq_template_ref = ''
        #self.seq_template_ref_len = 0

        # get chrom_len
        chrom_info_list = glv.conf.get_chrom_info(self.chrom)
        chrom_len = chrom_info_list[2]

        # frag_padを切り出す
        self.fragment_pad_len = glv.conf.fragment_pad_len

        # abs_posを決める
        self.abs_frag_pad_pre_end = self.abs_around_seq_pre_stt - 1

        #=========================================================
        self.abs_frag_pad_pre_stt = \
            self.abs_frag_pad_pre_end - self.fragment_pad_len + 1
        # 2023.04.28
        if self.abs_frag_pad_pre_stt < 0:
            self.abs_frag_pad_pre_stt = 1
        #=========================================================

        self.abs_frag_pad_aft_stt = self.abs_around_seq_aft_end + 1

        #=========================================================
        self.abs_frag_pad_aft_end = \
            self.abs_frag_pad_aft_stt + self.fragment_pad_len - 1
        # 2023.04.28
        if self.abs_frag_pad_aft_end > chrom_len:
            self.abs_frag_pad_aft_end = chrom_len
        #=========================================================

        # templateの絶対pos stringを最初に作る。
        # 最初はposはすべて完成しているが、今後端を切るために。
        self.seq_template_ref_abs_pos = \
            self.make_abs_pos(
                self.abs_frag_pad_pre_stt,
                self.abs_frag_pad_aft_end)

        # これは最初の
        # templateの相対pos string
        self.seq_template_ref_rel_pos, \
        self.SEQUENCE_TARGET = \
            self.convert_to_rel_pos(self.seq_template_ref_abs_pos)

        # refのfragpadを取り出す。
        self.frag_pad_pre, self.frag_pad_aft, self.seq_template_ref = \
            self.get_seq_template_ref(
                self.chrom, self.seq_template_ref_abs_pos)

        self.frag_pad_pre_len = len(self.frag_pad_pre)
        self.frag_pad_aft_len = len(self.frag_pad_aft)
        self.seq_template_ref_len = len(self.seq_template_ref)

        # groupのproductにもセットする
        for gno in range(2):
            self.gr_product[gno].set_frag_pad(
                self.frag_pad_pre, self.frag_pad_aft)


    def make_abs_pos(
        self,
        abs_frag_pad_pre_stt,
        abs_frag_pad_aft_end):

        return "{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
            abs_frag_pad_pre_stt,
            self.abs_frag_pad_pre_end,
            self.abs_around_seq_pre_stt,
            self.abs_around_seq_pre_end,
            self.pos,
            self.abs_around_seq_aft_stt,
            self.abs_around_seq_aft_end,
            self.abs_frag_pad_aft_stt,
            abs_frag_pad_aft_end)


    def convert_to_rel_pos(self, seq_template_ref_abs_pos):

        abs_frag_pad_pre_stt, abs_frag_pad_pre_end, \
        abs_around_seq_pre_stt, abs_around_seq_pre_end, \
        abs_pos, \
        abs_around_seq_aft_stt, abs_around_seq_aft_end, \
        abs_frag_pad_aft_stt, abs_frag_pad_aft_end = \
            self.separate_pos_str(seq_template_ref_abs_pos)

        # 11......21
        # 1.......11
        dif = abs_frag_pad_pre_stt

        rel_frag_pad_pre_stt = 1
        rel_frag_pad_pre_end = abs_frag_pad_pre_end - dif + 1
        rel_around_seq_pre_stt = abs_around_seq_pre_stt - dif + 1
        rel_around_seq_pre_end = abs_around_seq_pre_end - dif + 1
        rel_pos = abs_pos - dif + 1
        rel_around_seq_aft_stt = abs_around_seq_aft_stt - dif + 1
        rel_around_seq_aft_end = abs_around_seq_aft_end - dif + 1
        rel_frag_pad_aft_stt = abs_frag_pad_aft_stt - dif + 1
        rel_frag_pad_aft_end = abs_frag_pad_aft_end - dif + 1

        #log.debug("{} {} {} {}".format(
        #    self.SEQUENCE_TARGET,
        #    rel_around_seq_pre_stt,
        #    rel_around_seq_aft_end,
        #    rel_around_seq_pre_stt))

        # 100-1=99+1=100
        sequence_target = "{},{}".format(
            rel_around_seq_pre_stt,
            rel_around_seq_aft_end - rel_around_seq_pre_stt + 1)

        return "{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
            rel_frag_pad_pre_stt,
            rel_frag_pad_pre_end,
            rel_around_seq_pre_stt,
            rel_around_seq_pre_end,
            rel_pos,
            rel_around_seq_aft_stt,
            rel_around_seq_aft_end,
            rel_frag_pad_aft_stt,
            rel_frag_pad_aft_end), \
            sequence_target


    def separate_pos_str(self, pos_str):

        return map(int, pos_str.split('/'))


    def get_seq_template_ref(self, chrom, seq_template_ref_abs_pos):

        abs_frag_pad_pre_stt, abs_frag_pad_pre_end, \
        abs_around_seq_pre_stt, abs_around_seq_pre_end, \
        abs_pos, \
        abs_around_seq_aft_stt, abs_around_seq_aft_end, \
        abs_frag_pad_aft_stt, abs_frag_pad_aft_end = \
            self.separate_pos_str(seq_template_ref_abs_pos)

        # update
        # pick frag_pad_pre
        frag_pad_pre = glv.conf.pick_refseq(
            chrom,
            abs_frag_pad_pre_stt,
            abs_frag_pad_pre_end).upper()

        # これは変わらない
        seq_target_ref = self.seq_target_ref

        # pick frag_pad_aft
        frag_pad_aft = glv.conf.pick_refseq(
            chrom,
            abs_frag_pad_aft_stt,
            abs_frag_pad_aft_end).upper()

        seq_template_ref = "{}{}{}".format(
            frag_pad_pre,
            seq_target_ref,
            frag_pad_aft)

        return frag_pad_pre, frag_pad_aft, seq_template_ref


    def copy_line_for_effective_restriction_enzymes(self):
        '''
        '''

        enzyme_cnt_per_variant = 0

        l_marker_id = list()
        l_marker_info = list()
        l_seq_t_abs_pos = list()
        l_seq_t_rel_pos = list()
        l_seq_t_ref = list()
        l_seq_target = list()

        # indel and snp behave the same as indel
        if self.mk_type == glv.MK_INDEL or \
            self.mk_type == glv.MK_SNP:

            enzyme_cnt_per_variant = 1

            marker_id = self.make_marker_id()
            l_marker_id = [marker_id]

            marker_info = self.make_marker_info()
            l_marker_info = [marker_info]

            l_seq_t_abs_pos = [self.seq_template_ref_abs_pos]
            l_seq_t_rel_pos = [self.seq_template_ref_rel_pos]
            l_seq_t_ref = [self.seq_template_ref]
            l_seq_target = [self.SEQUENCE_TARGET]

        else:   # CAPS
            # duplicate line information by enzyme
            enzyme_cnt_per_variant = len(self.caps_result)

            # Build information as a multi-line list.
            self.divide_information_by_enzyme(
                enzyme_cnt_per_variant,
                l_marker_id,
                l_marker_info,
                l_seq_t_abs_pos,
                l_seq_t_rel_pos,
                l_seq_t_ref,
                l_seq_target)
        
        line_for_each_enzyme = list()        

        for num in range(enzyme_cnt_per_variant):
            enzyme_cnt = "{}/{}".format(num+1, enzyme_cnt_per_variant)
            # set_enz_cnt とは、1/1-1/2 (self.set_n, enzyme_cnt)
            # "-" で区切られた最初が、set_n つまり、
            # バリアントで得られている アリルペアの数
            # その中での、CAPSの解析数
            set_enz_cnt = "{}-{}".format(self.set_n, enzyme_cnt)
            vseq_lens_ano_str = \
                "{}".format(','.join(map(str, self.vseq_lens_ano)))

            # enzyme_cnt
            #if enzyme_cnt_per_variant > 1:
            #    print()
            #    print("enzyme_cnt={}".format(enzyme_cnt))
            #    # set_enz_cnt
            #    print("set_enz_cnt={}".format(set_enz_cnt))
            #    # vseq_lens_ano_str
            #    print("vseq_lens_ano_str={}".format(vseq_lens_ano_str))

            l_list = list()

            #print(l_marker_id)
            #print(l_marker_info)
            #print(enzyme_cnt_per_variant)
            #print("")

            # out to marker out file
            # Synchronize with eval_variant.py outlist.py
            l_list += [l_marker_id[num]]

            # ----------------------------------
            l_list += [self.chrom]
            l_list += [self.pos]
            l_list += [self.targ_grp]
            l_list += [self.vseq_gno_str]
            l_list += [self.gts_segr_lens]
            l_list += [self.targ_ano]
            l_list += [self.var_type]
            # 2022-10-26 self.mk_type
            l_list += [self.mk_type]
            # auto_grp
            #if glv.conf.is_auto_group:
            l_list += [self.auto_grp0]
            l_list += [self.auto_grp1]
            # ----------------------------------

            # ----------------------
            l_list += [set_enz_cnt]
            # ----------------------
            l_list += [l_marker_info[num]]
            # vseq_lens_ano
            l_list += [vseq_lens_ano_str]
            # ----------------------

            # 1) g0_seq_target_len
            l_list += [self.gr_product[0].seq_target_len]
            # 2) g0_seq_target
            l_list += [self.gr_product[0].seq_target]

            # 1) g1_seq_target_len
            l_list += [self.gr_product[1].seq_target_len]
            # 2) g1_seq_target
            l_list += [self.gr_product[1].seq_target]

            # 1) seq_template_ref_len
            l_list += [len(l_seq_t_ref[num])]
            # 2) seq_template_ref_abs_pos
            l_list += [l_seq_t_abs_pos[num]]
            # 3) seq_template_ref_rel_pos
            l_list += [l_seq_t_rel_pos[num]]
            # 4) SEQUENCE_TARGET
            l_list += [l_seq_target[num]]
            # 5) seq_template_ref (SEQUENCE_TEMPLATE)
            l_list += [l_seq_t_ref[num]]

            line_for_each_enzyme.append('\t'.join(map(str, l_list)))

        self.line = '\n'.join(map(str, line_for_each_enzyme))


    def divide_information_by_enzyme(
        self,
        enzyme_cnt_per_variant,
        l_marker_id,
        l_marker_info,
        l_seq_t_abs_pos,
        l_seq_t_rel_pos,
        l_seq_t_ref,
        l_seq_target):
        '''
        '''

        #print(self.caps_result)

        #=============~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for enzyme in self.caps_result.keys():

            #print("enzyme={}".format(enzyme))

            # for marker id
            marker_id = self.make_marker_id(enzyme)
            l_marker_id.append(marker_id)

            # enzymeごとに、digest_posは、grに組み込む
            marker_info = self.make_marker_info(enzyme)
            l_marker_info.append(marker_info)

            # 何もなければすでにrefとしてセットされた値を
            seq_t_abs_pos = self.seq_template_ref_abs_pos
            seq_t_rel_pos = self.seq_template_ref_rel_pos
            seq_t_ref = self.seq_template_ref
            SEQUENCE_TARGET = self.SEQUENCE_TARGET

            text = ""
            caps_check_dict, text = \
                self.check_effect_of_enzyme(seq_t_ref, [enzyme])

            caps_result_cnt = len(caps_check_dict)
            #print(caps_result_cnt)
            #pprint.pprint(caps_check_dict)

            # 自分自身を除いて処理
            if caps_result_cnt != 0:
                # 切断されているなら、seq_templateを更新し、
                # 現在、
                # ref.
                # self.gr_product[num]

                # 20200715
                # それぞれ、メソッドで使っているだけ
                seq_t_abs_pos = \
                    self.change_abs_pos_by_digest(
                        caps_check_dict[enzyme]['res_list'])

                # templateの相対pos string
                seq_t_rel_pos, SEQUENCE_TARGET = \
                    self.convert_to_rel_pos(seq_t_abs_pos)

                # まとめてpick
                frag_pad_pre, frag_pad_aft, seq_t_ref = \
                    self.get_seq_template_ref(
                        self.chrom, seq_t_abs_pos)

                # 確認用 capsを検索する
                #caps_result_dict, caps_result_dict_str = \
                #    Products.get_caps_result(
                #        seq_t_ref, [enzyme])
                #log.debug("rechecked {}".format(caps_result_dict_str))
                #log.debug("{}\n".format(seq_t_rel_pos))

            else:
                pass

            l_seq_t_abs_pos.append(seq_t_abs_pos)
            l_seq_t_rel_pos.append(seq_t_rel_pos)
            l_seq_t_ref.append(seq_t_ref)
            l_seq_target.append(SEQUENCE_TARGET)


    def make_marker_info(self, enzyme_name=''):
        '''
        '''

        marker_info = ''

        # indel and snp behave the same as indel
        if self.mk_type == glv.MK_INDEL or \
            self.mk_type == glv.MK_SNP:

            longer_group = self.long_gno
            longer_length = self.longer_len
            shorter_length = self.shorter_len
            diff_length = self.diff_len
            digested_pos = 0

            marker_info = "{}.{}.{}.{}.{}".format(
                longer_group,
                longer_length,
                shorter_length,
                diff_length,
                digested_pos)

        # not INDEL
        else:

            marker_info = "{}.{}.{}.{}.{}".format(
                enzyme_name,
                self.caps_result[enzyme_name]['digested_gno'],
                self.caps_result[enzyme_name]['found_pos'],
                self.caps_result[enzyme_name]['digest_pattern'],
                self.caps_result[enzyme_name]['digested_pos'])

        return marker_info


    @classmethod
    def split_marker_info(cls, marker_info):
        '''
        '''

        # for indel
            # longer_group, 
            # longer_length,
            # shorter_length,
            # diff_length,
            # digested_pos

        # for !indel
            # enzyme_name,      str
            # digested_gno,
            # found_pos,
            # digest_pattern,   str
            # digested_pos

        return marker_info.split(".")


    def make_marker_id(self, enzyme_name=''):
        '''
        '''

        marker_id = ""

        # 1.chrom
        chrom = self.chrom
        # 2.pos
        pos = self.pos
        # 3. Allele number corresponding to groups 0 and 1
        ano_corresponding_to_g0_g1 = self.targ_ano
        # 4. variant type
        var_type = self.var_type
        # 5. mk type
        mk_type = self.mk_type

        # 5.SEQUENCE_TARGET detail
        # indel and snp behave the same as indel
        if self.mk_type == glv.MK_INDEL or \
            self.mk_type == glv.MK_SNP:

            # 5.1 The longer group
            longer_group = self.long_gno
            # 5.2 The longer one, the length
            longer_length = self.longer_len
            # 5.3 The shorter one, the length
            shorter_length = self.shorter_len

            seq_target_detail = "{},{},{}".format(
                longer_group,
                longer_length,
                shorter_length)

        else:
            # snp or else
            # 5.1 digested group
            digested_gno = self.caps_result[enzyme_name]['digested_gno']

            # 5.2 found point
            found_pos = self.caps_result[enzyme_name]['found_pos']

            # 5.3 restriction enzyme
            # enzyme_name

            seq_target_detail = "{},{},{}".format(
                digested_gno,
                found_pos,
                enzyme_name)
 
        # self.gts_segr_lens 11/00,hoho_1,1.1/1.1
        # 11/00
        alstr_gno = self.gts_segr_lens.split(",")[0]

        marker_id = "{}.{}.{}.{}.{}.{}.{}".format(
            chrom,
            pos,
            ano_corresponding_to_g0_g1,
            var_type,
            mk_type,
            alstr_gno,
            seq_target_detail)

        return marker_id


    def change_abs_pos_by_digest(self, caps_dig_pos):

        # sequence_target の外側にある digested_pointだけが
        # 変更対象である。

        fixed_pre_stt = self.abs_frag_pad_pre_stt
        fixed_pre_end = self.abs_frag_pad_pre_end
        fixed_aft_stt = self.abs_frag_pad_aft_stt
        fixed_aft_end = self.abs_frag_pad_aft_end

        five_prime_biggest_pos = fixed_pre_stt
        three_prime_smallest_pos = fixed_aft_end

        # EcoRI': {'digest_pattern': 'G^AATT_C'}
        # [17]
        # 123456789012345678901234567890
        # CTCTGTTCGGTGGAAGAATTCAGATTTCAGAGTCA
        #               G^AATT_C
        #                 /-> 17
        #                 AATTCAGATTTCAGAGTCA
        # 切断されるポイントは17。これは残る側。
        # 残る側に、切断ポイントを残していいのか。
        # 今は残している。

        # digest_positionごとに調査
        for rel_digest_pos in caps_dig_pos:
            # 絶対posに変換
            # 10001    100 -> 10001+100 - 10100
            abs_digest_pos = fixed_pre_stt + rel_digest_pos - 1

            #log.debug("rel={} abs={} pre_stt<{} pre_end>{} aftstt<{}".format(
            #    rel_digest_pos,
            #    abs_digest_pos,
            #    fixed_pre_stt,
            #    fixed_pre_end,
            #    fixed_aft_stt))

            # |fixed_pre_stt
            #                |fixed_pre_end
            #                               |fixed_aft_stt
            # <--------------><=============<-------------->

            # １つポジションをずらす。それにより認識サイトが
            # 壊れる
            if abs_digest_pos < fixed_pre_end:
                # 5'側では、一つ先で切る
                # always
                five_prime_biggest_pos = abs_digest_pos + 1

            elif fixed_aft_stt < abs_digest_pos:
                # only once
                # 3'側では、一つ手前で切る
                three_prime_smallest_pos = abs_digest_pos - 1
                break

        seq_template_ref_abs_pos = \
            self.set_seq_template_ref_abs_pos(
                five_prime_biggest_pos,
                three_prime_smallest_pos)

        #log.debug("{}".format(self.seq_template_ref_abs_pos))
        #log.debug("{}".format(seq_template_ref_abs_pos))

        #sys.exit(1)

        return seq_template_ref_abs_pos


    def get_seq_template_ref(self, chrom, seq_template_ref_abs_pos):

        abs_frag_pad_pre_stt, abs_frag_pad_pre_end, \
        abs_around_seq_pre_stt, abs_around_seq_pre_end, \
        abs_pos, \
        abs_around_seq_aft_stt, abs_around_seq_aft_end, \
        abs_frag_pad_aft_stt, abs_frag_pad_aft_end = \
            self.separate_pos_str(seq_template_ref_abs_pos)

        # update
        # pick frag_pad_pre
        frag_pad_pre = glv.conf.pick_refseq(
            chrom,
            abs_frag_pad_pre_stt,
            abs_frag_pad_pre_end).upper()

        # これは変わらない
        seq_target_ref = self.seq_target_ref

        # pick frag_pad_aft
        frag_pad_aft = glv.conf.pick_refseq(
            chrom,
            abs_frag_pad_aft_stt,
            abs_frag_pad_aft_end).upper()

        seq_template_ref = "{}{}{}".format(
            frag_pad_pre,
            seq_target_ref,
            frag_pad_aft)

        return frag_pad_pre, frag_pad_aft, seq_template_ref


    def set_seq_template_ref_abs_pos(
        self,
        abs_frag_pad_pre_stt,
        abs_frag_pad_aft_end):

        return "{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
            abs_frag_pad_pre_stt,
            self.abs_frag_pad_pre_end,
            self.abs_around_seq_pre_stt,
            self.abs_around_seq_pre_end,
            self.pos,
            self.abs_around_seq_aft_stt,
            self.abs_around_seq_aft_end,
            self.abs_frag_pad_aft_stt,
            abs_frag_pad_aft_end)





