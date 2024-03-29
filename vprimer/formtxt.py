# -*- coding: utf-8 -*-

import sys
#import os
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
# ok
import vcfpy

from vprimer.eval_variant import EvalVariant
from vprimer.product import Product
from vprimer.primer import PrimerInfo
from vprimer.allele_select import AlleleSelect
from vprimer.inout_primer3 import InoutPrimer3

class FormTxt(object):

    def __init__(self):

        # debug
        #self.alstr_stop = True
        self.alstr_stop = False
        pass


    def format_text(self):
        ''' called from main: self.formtxt.format_text()
            After primer generation process, all information is formatted
            and output.
        '''

        proc_cnt = 0
        for distin_gdct, reg in glv.conf.gdct_reg_list:
            proc_cnt += 1

            # init
            primer_file = distin_gdct['primer']['fn'][reg]['out_path']
            df_distin = pd.DataFrame()

            # out to 040_FormatF
            proc_name = "formfail"
            df_distin = self.write_form(primer_file, proc_name, df_distin,
                proc_cnt, distin_gdct, reg)

            # out to 050_FormatP
            proc_name = "formpass"
            df_distin = self.write_form(primer_file, proc_name, df_distin,
                proc_cnt, distin_gdct, reg)


    def write_form(self, primer_file, proc_name, df_distin,
            proc_cnt, distin_gdct, reg):
        '''
        '''

        # stop or continue ---------------------------------
        ret_status = utl.decide_action_stop(proc_name)

        if ret_status == glv.progress_stop:
            log.info(utl.progress_message(ret_status, proc_name))
            sys.exit(1)

        if ret_status == glv.progress_gothrough:
            log.info(utl.progress_message(ret_status, proc_name))
            return df_distin
        # --------------------------------------------------

        
        if len(df_distin) == 0:
            df_distin = pd.read_csv(
                primer_file, sep='\t', header=0, index_col=None)

        if proc_name == "formfail": 
            df_distin_form = df_distin[df_distin['complete'] <= 0]
        else:
            df_distin_form = df_distin[df_distin['complete'] > 0]

        log.info("-------------------------------")
        log.info("Start processing {}\n".format(proc_name))

        # write the formatted result to 040_formfail
        out_txt_path = distin_gdct[proc_name]['fn'][reg]['out_path']
        log.info("out_txt_path={}.".format(out_txt_path))

        # If the specified file already exists, move that file
        # to the bak directory.
        utl.save_to_tmpfile(out_txt_path, pre_log=True)

        #====================================================
        # header
        header_txt = distin_gdct['formpass']['hdr_text']

        #====================================================
        # final check dict for 050_FormatP
        duplicate_pos_dict = dict()
        same_primer_dict = dict()

        if proc_name == "formpass":
            # 1) duplicate position, make duplicate_pos_dict
            duplicate_pos_dict = self.make_duplicate_pos_dict(df_distin_form)
            # 2) same primer sequence make same_primer_dict
            same_primer_dict = self.make_same_primer_dict(df_distin_form)

            # 3) add header -------------------------------------------------
            if glv.conf.is_auto_group:
                gr_list = [distin_gdct[0]]
            else:
                gr_list = [distin_gdct[0], distin_gdct[1]]

            sample_nickname_ordered_list, \
            sample_basename_ordered_list, \
            sample_fullname_ordered_list = \
                utl.get_specified_sample_list(gr_list)

            
            # add sample header to original formpass header
            if not self.alstr_stop:
                header_txt = "{}\t{}".format(header_txt, "\t".join(
                sample_nickname_ordered_list))

            # open vcf for alstr in formpass
            vcf_reader_formpass = vcfpy.Reader.from_path(
                glv.conf.vcf_gt_path)

        #====================================================

        # file open with append mode
        with out_txt_path.open('a', encoding='utf-8') as f:
        #with open(out_txt_path, mode='a') as f:

            start = utl.get_start_time()

            # write header no \n
            utl.w_flush(f, header_txt)

            # each of fail or safe line from primer file
            for primer_df_row in df_distin_form.itertuples():

                # index_no = primer_df_row[0]
                # marker_id = primer_df_row[1]
                #chrom_name = primer_df_row[2]
                #pos = primer_df_row[3]

                self.prepare_from_primer_file(
                    primer_df_row, distin_gdct)

                #print("self.marker_id={}".format(self.marker_id))
                #print("self.chrom={}".format(self.chrom))
                #print("self.pos={}".format(self.pos))
                #print("self.targ_grp={}".format(self.targ_grp))
                #print("self.g0_name={}".format(self.g0_name))
                #print("self.g1_name={}".format(self.g1_name))
                #print("self.targ_ano={}".format(self.targ_ano))
                #print("self.g0_ano={}".format(self.g0_ano))
                #print("self.g1_ano={}".format(self.g1_ano))
                #print("self.vseq_gno_str={}".format(self.vseq_gno_str))
                #print()

                # REF=
                #ano_gno = self.targ_ano.split(',')

                #if split(self.targ_ano).split(',')[1] ==

                # ********************************************
                # duplicate_pos_dict: format duplicate line
                line = self.format_product(distin_gdct,
                    duplicate_pos_dict, same_primer_dict)
                # ********************************************

                # For formpass, append the allele string to the end
                if not self.alstr_stop and proc_name == "formpass":
                #if proc_name == "formpass":

                    # add member's alstr
                    alstr_list = self.get_members_alstr(
                        self.chrom, self.pos,
                        vcf_reader_formpass,
                        sample_fullname_ordered_list)

                    line = "{}\t{}".format(line, "\t".join(alstr_list))

                # no \n
                utl.w_flush(f, line)

        log.info("{} {} > {}.txt\n".format(
            proc_name, utl.elapse_str(start),
            distin_gdct[proc_name]['fn'][reg]['base_nam']))

        return df_distin


    def get_members_alstr(self, chrom_name, pos,
            vcf_reader_formpass, sample_fullname_ordered_list):
        '''
        '''

        alstr_list = list()

        # zero based: open start
        open_stt = pos - 1
        # close end
        close_end = open_stt + 1

        alstr_list = list()

        # Since fetch may bring multiple records, only those whose
        # pos is close_end are targeted.
        for record in vcf_reader_formpass.fetch(
            chrom_name, open_stt, close_end):

            # here
            #print("{}, {}\t{}\t{}\t{}".format(
            #    close_end,
            #    record.CHROM, record.POS, record.REF, record.ALT))

            # (1) vcf_readerによって集められたrecordのPOSが、formpassのposと
            # 異なる場合には、variantの関連領域はかぶるが、
            # 解析に用いられたバリアントではないことがわかるので、扱わない
            mes = self.confirm_selected_variant(record, close_end)
            if mes != "":
                #log.info(mes)
                continue

            # サンプルを検索し、alstrを作る
            for fn in sample_fullname_ordered_list:
                alstr = \
                    AlleleSelect.record_call_for_sample(
                        record, fn)
                #gt = AlleleSelect.sepal(alstr, 'gt')
                # directly 00, 01, 11
                alstr_list += [alstr]

        #alstr_line = '\t'.join(alstr_list)
        return alstr_list


    def confirm_selected_variant(self, record, close_end):
        '''
        '''
        mes = ""

        # positionが異なる場合、使わない
        if record.POS != close_end:
            mes = "{} != {}, {}".format(record.POS, close_end, record)
            return mes

        # formpassの、グループの２つのseqが、recordのseqと等しい場合に
        # このレコードが解析に用いたバリアントであるとする。

        # レコードの vseq_by_ano のリスト
        rec_vseq_ano = [record.REF]
        [rec_vseq_ano.append(alt.value) for alt in record.ALT]
        #print("{}\trec_vseq_ano".format(rec_vseq_ano))

        # レコードの ano のリスト
        rec_ano = list(range(len(rec_vseq_ano)))
        #print("{}\trec_ano".format(rec_ano))

        # formpassの vseq_by_gno のリスト
        form_2vseq_gno = self.vseq_gno_str.split(',')
        #print("{}\tform_2vseq_gno".format(form_2vseq_gno))

        # formpassの ano_by_gno のリスト
        form_ano_gno = list(map(int, self.targ_ano.split(',')))
        #print("{}\tform_ano_gno".format(form_ano_gno))

        # 情報を集約したdict
        form_2vseq_list = [
            {'ano': form_ano_gno[0], 'seq': form_2vseq_gno[0]},
            {'ano': form_ano_gno[1], 'seq': form_2vseq_gno[1]},
        ]

        #print("{}\tform_2vseq_list".format(form_2vseq_list))

        form_ano0 = form_2vseq_list[0]['ano']
        #print("{}\tform_ano0".format(form_ano0))
        form_ano1 = form_2vseq_list[1]['ano']
        #print("{}\tform_ano1".format(form_ano1))

        form_seq0 = form_2vseq_list[0]['seq']
        #print("{}\tform_seq0".format(form_seq0))
        form_seq1 = form_2vseq_list[1]['seq']
        #print("{}\tform_seq1".format(form_seq1))

        # formのanoが、recordのanoにない場合、探索終わり
        for f_ano in form_ano_gno:
            if not f_ano in rec_ano:
                # over
                mes = "{} not in {}".format(f_ano, rec_ano)
                return mes

        # formのseq1が、recと違うなら、探索終わり
        if rec_vseq_ano[form_ano0] != form_seq0:
            mes = "\nover form_ano0 {} ".format(form_ano0)
            mes += "form_seq0 {} ".format(form_seq0)
            mes += "!= {}\n\n".format(rec_vseq_ano[form_ano0])
            #print(mes)
            return mes

        if rec_vseq_ano[form_ano1] != form_seq1:
            mes = "\nover form_ano1 {} ".format(form_ano1)
            mes += "form_seq1 {} ".format(form_seq1)
            mes += "!= {}\n\n".format(rec_vseq_ano[form_ano1])
            #print(mes)
            return mes 

        return mes


    def make_duplicate_pos_dict(self, df_distin_form):
        # notice when position duplicated(diferent enzyme
        # for caps in same pos)
        duplicate_pos_dict = dict()

        # ========================================================
        # keep chrom-pos dupulicate line information
        # complete であるdfの中に、chrom:posが 重複したものが
        # どれだけあるのかを、調査する。df.duplicatedは、重複したもの
        # を抽出する。
        # ========================================================
        df_chrom_pos = df_distin_form.loc[:, ['chrom', 'pos']]
        df_chrom_pos_duplicated = df_chrom_pos[df_chrom_pos.duplicated()]

        for c_p_row in df_chrom_pos_duplicated.itertuples():

            # index_no = c_p_row[0]
            chrom = c_p_row[1]
            pos = c_p_row[2]

            # 辞書オブジェクトに対してinを使うとキーの存在確認になる
            # keys()メソッドを使っても同じ。
            if not chrom in duplicate_pos_dict:
                duplicate_pos_dict[chrom] = dict();

            # [chrom][pos] = pos の辞書を作成する。
            if not pos in duplicate_pos_dict[chrom]:
                duplicate_pos_dict[chrom][pos] = pos

        return duplicate_pos_dict


    def make_same_primer_dict(self, df_distin_form):
        # notice for same primer sequence pair
        same_primer_dict = dict()

        #df_primers = df_distin_form.loc[:,
        df_primers = df_distin_form.loc[:,
            ['chrom',
             'pos',
             'PRIMER_LEFT_0_SEQUENCE',
             'PRIMER_RIGHT_0_SEQUENCE']]

        df_primers['PRIMERs'] = \
            df_primers['PRIMER_LEFT_0_SEQUENCE'] + \
            df_primers['PRIMER_RIGHT_0_SEQUENCE']

        # all duplicated records
        df_primers_duplicated = df_primers[
            df_primers.duplicated(subset='PRIMERs', keep=False)]
        
        # for each duplicated record
        for pr_row in df_primers_duplicated.itertuples():

            # index_no = pr_row[0]
            chrom = pr_row[1]
            pos = pr_row[2]
            l_seq = pr_row[3]
            r_seq = pr_row[4]
            lr_seq = "{},{}".format(l_seq, r_seq)

            # 辞書オブジェクトに対してinを使うとキーの存在確認になる
            # keys()メソッドを使っても同じ。
            if not lr_seq in same_primer_dict:
                same_primer_dict[lr_seq] = list();

            chrom_pos = "{}:{}".format(chrom, pos)
            # append chrom:pos as list
            if not chrom_pos in same_primer_dict[lr_seq]:
                same_primer_dict[lr_seq].append(chrom_pos)

        return same_primer_dict



    def prepare_from_primer_file(self, primer_df_row, distin_gdct):
        ''' from primer raw, pick up each value and information
        '''

        # hdr_dict is a dictionary for translaing the header names
        # to row column_no
        hdr_dict = distin_gdct['primer']['hdr_dict']

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
        self.set_enz_cnt, \
        self.marker_info, \
        self.vseq_lens_ano_str, \
        self.enzyme_name, \
        self.digest_pattern, \
        self.target_gno, \
        self.target_len, \
        self.auto_grp0, \
        self.auto_grp1 = \
            utl.get_basic_primer_info(primer_df_row, hdr_dict)

        #self.notice,
        # in_target
        self.in_target = primer_df_row[hdr_dict['in_target']]

        self.g0_vseq, self.g1_vseq = self.vseq_gno_str.split(",")
        #11/00,hoho_1,1.1/1.1
        self.g0_gt, self.g1_gt = self.get_genotype()

        #log.debug("self.chrom={} pos={}".format(self.chrom, self.pos))

        self.try_cnt = str(primer_df_row[hdr_dict['try_cnt']])
        self.complete = str(primer_df_row[hdr_dict['complete']])
        self.blast_check = str(primer_df_row[hdr_dict['blast_check']])

        self.g0_seq_target_len = \
            int(primer_df_row[hdr_dict['g0_seq_target_len']])
        self.g0_seq_target = \
            str(primer_df_row[hdr_dict['g0_seq_target']])
        self.g1_seq_target_len = \
            int(primer_df_row[hdr_dict['g1_seq_target_len']])
        self.g1_seq_target = \
            str(primer_df_row[hdr_dict['g1_seq_target']])

        self.seq_template_ref_len = \
            int(primer_df_row[hdr_dict['seq_template_ref_len']])
        self.seq_template_ref_abs_pos = \
            str(primer_df_row[hdr_dict['seq_template_ref_abs_pos']])
        self.seq_template_ref_rel_pos = \
            str(primer_df_row[hdr_dict['seq_template_ref_rel_pos']])

        self.PRIMER_PAIR_0_PRODUCT_SIZE = \
            int(primer_df_row[hdr_dict['PRIMER_PAIR_0_PRODUCT_SIZE']])
        self.PRIMER_LEFT_0 = \
            str(primer_df_row[hdr_dict['PRIMER_LEFT_0']])
        self.left_primer_id = \
            str(primer_df_row[hdr_dict['left_primer_id']])
        self.PRIMER_LEFT_0_SEQUENCE = \
            str(primer_df_row[hdr_dict['PRIMER_LEFT_0_SEQUENCE']])
        self.PRIMER_RIGHT_0 = \
            str(primer_df_row[hdr_dict['PRIMER_RIGHT_0']])
        self.right_primer_id = \
            str(primer_df_row[hdr_dict['right_primer_id']])
        self.PRIMER_RIGHT_0_SEQUENCE = \
            str(primer_df_row[hdr_dict['PRIMER_RIGHT_0_SEQUENCE']])
        self.SEQUENCE_TEMPLATE = \
            str(primer_df_row[hdr_dict['SEQUENCE_TEMPLATE']])

        # summer 20210910 add
        self.product_gc_contents = \
            str(primer_df_row[hdr_dict['product_gc_contents']])


    def get_genotype(self):
        '''
        '''

        # 11/00,hoho_1,1.1/1.1
        # self.gts_segr_lens
        #print("self.gts_segr_lens={}".format(self.gts_segr_lens))
        gts = self.gts_segr_lens.split(",")[0]
        #print("gts={}".format(gts))
        g0_gt, g1_gt = gts.split("/")
        #print("g0_gt={}, g1_gt={}".format(g0_gt, g1_gt))
        g0_gtl = list(g0_gt)
        #print("g0_gtl={}".format(g0_gtl))
        g1_gtl = list(g1_gt)

        g0_genotype = "{}/{}".format(g0_gtl[0], g0_gtl[1])
        g1_genotype = "{}/{}".format(g1_gtl[0], g1_gtl[1])

        #print("{}, {}".format(g0_genotype, g1_genotype))

        return g0_genotype, g1_genotype


    def format_product(self, distin_gdct,
        duplicate_pos_dict, same_primer_dict):

        if self.PRIMER_PAIR_0_PRODUCT_SIZE == 0:
            product_size_0 = -1
            product_size_1 = -1
            digested_gno = -1
            digested_ano = -1
            digested_size_0 = -1
            digested_size_1 = -1
            diff_product_size = -1
            digest_diff = -1

        else:
            product_size_0, \
            product_size_1, \
            digested_gno, \
            digested_ano, \
            digested_size_0, \
            digested_size_1, \
            diff_product_size, \
            digest_diff = \
                self.get_group_product_size()

        #--------------------
        line_list = list()


        line_list += [self.chrom]
        line_list += [self.pos]

        line_list += [self.g0_vseq]
        line_list += [self.g1_vseq]
        line_list += [self.g0_gt]
        line_list += [self.g1_gt]
        line_list += [self.targ_ano]

        line_list += [self.var_type]
        # 2022-10-26 add
        line_list += [self.mk_type]

        # auto_grp
        # primer.py primer_complete_to_line
        #if glv.conf.is_auto_group:
        line_list += [self.auto_grp0]
        line_list += [self.auto_grp1]

        #line_list += [comment]
        # if this pos is duplicated, insert comment to this column
        # notice_line = 'dup,1/1-1/2;

        # in_target
        line_list += [self.in_target]

        # dup_pos
        dup_pos = self.add_dup_info(duplicate_pos_dict)
        line_list += [dup_pos]

        # same primer sequence

        same_primer = self.add_same_primer(
            same_primer_dict,
            self.PRIMER_LEFT_0_SEQUENCE,
            self.PRIMER_RIGHT_0_SEQUENCE)
        line_list += [same_primer]

        # dimer check
        dimer_check = "-"
        line_list += [dimer_check]

        # add ';'
        #notice_line = utl.make_notice(self.notice, notice_line)

        # for notice
        #line_list += [notice_line]

        line_list += [self.enzyme_name]
        line_list += [self.g0_name]
        line_list += [self.g1_name]
        line_list += [product_size_0]
        line_list += [product_size_1]
        # summer 20210910
        line_list += [self.product_gc_contents]

        # **
        #line_list += [digest_diff]
        line_list += [diff_product_size]
        line_list += [digested_size_0]
        line_list += [digested_size_1]

        line_list += [digested_gno]
        line_list += [digested_ano]
        line_list += [self.try_cnt]
        line_list += [self.complete]

        line_list += [self.marker_id]
        line_list += [self.gts_segr_lens]

        # for amplicon
        if distin_gdct['pick_mode'] == glv.MODE_SNP and \
            self.PRIMER_LEFT_0_SEQUENCE != "-" and \
            self.PRIMER_RIGHT_0_SEQUENCE != "-":

            line_list += [self.left_primer_id]
            line_list += ["{}{}".format(
                glv.conf.amplicon_forward_tag,
                self.PRIMER_LEFT_0_SEQUENCE)]

            line_list += [self.right_primer_id]
            line_list += ["{}{}".format(
                glv.conf.amplicon_reverse_tag,
                self.PRIMER_RIGHT_0_SEQUENCE)]

        else:
            line_list += [self.left_primer_id]
            line_list += [self.PRIMER_LEFT_0_SEQUENCE]
            line_list += [self.right_primer_id]
            line_list += [self.PRIMER_RIGHT_0_SEQUENCE]

        return '\t'.join(map(str, line_list))


    def add_dup_info(self, duplicate_pos_dict):

        dup_notice_str = "-"

        if self.chrom in duplicate_pos_dict:
            if self.pos in duplicate_pos_dict[self.chrom]:
                dup_notice_str = "{},{}".format(
                    glv.COMMENT_dup, self.set_enz_cnt)

        # dup_notice_str = 'dup,1/1-1/2;

        #print()
        #print("self.pos={}".format(self.pos))
        #print("duplicate_pos_dict={}".format(duplicate_pos_dict))
        #print("dup_notice_str={}".format(dup_notice_str))
        #print()


        return dup_notice_str


    def add_same_primer(self, same_primer_dict,
        LEFT_SEQUENCE, RIGHT_SEQUENCE):

        same_primer = "-"

        lr_seq = "{},{}".format(LEFT_SEQUENCE, RIGHT_SEQUENCE)
        if lr_seq in same_primer_dict:
            same_primer = ",".join(same_primer_dict[lr_seq])

        return same_primer


    def get_group_product_size(self):
        ''' The product size obtained by the output of primer3 is the product
        size on the REF sequence, and the products of each group need to be
        adjusted by the difference from the variant length of REF.
        indel has no digest. CAPS can get the size information to be digested.
        Obtain the digest size by CAPS from the product size of the group.

            # self.target_gno 1,0
            # rel_frag_pad_pre_end
            #                   ||rel_around_seq_pre_stt
            #                   ||        |rel_pos
            #                   ||        --- vseq_len_ref
            # <-----------------><========<=>========><----------------->
            #                500|
            #       |313
                    <--len 188--> 
            #       |313             len=421                  733|
            #       <==>......................................<==>
            #       |product_stt_pos              product_end_pos|
            #                    188+21+1=210
            #                    <========<=>========>
            #             found_pos 21|>d_pos 1
            #       |313             len=421                  733|
            #       <g0_prod_stt   vseq_g0<=>         g0_prod_end>
            #       <g1_prod_stt   vseq_g1<=>         g1_prod_end>
            #       |313             len=421                  733|
            #       <=== L_digested ===><====== R_digested ======>
            #
            #  <-- len 188 -->1234567890123456789012
            #                                     |found
            #                                      >digest
            #                 9012345678901234567890 => 210 digest pos


        '''

        # Get information on the relative position of seq_template
        rel_frag_pad_pre_stt, \
        rel_frag_pad_pre_end, \
        rel_around_seq_pre_stt, \
        rel_around_seq_pre_end, \
        rel_pos, \
        rel_around_seq_aft_stt, \
        rel_around_seq_aft_end, \
        rel_frag_pad_aft_stt, \
        rel_frag_pad_aft_end = \
            Product.separate_seq_template_pos(
                self.seq_template_ref_rel_pos)

        #----------------------------------------------------
        # vseq information etc.
        #----------------------------------------------------
        # Correspondence table of ano to gno
        ano_gno = [self.g0_ano, self.g1_ano]

        # List the lengths of variants in allele number order.
        vseq_lens_ano = [int(x) for x in self.vseq_lens_ano_str.split(',')]

        # Variant length of REF
        vseq_len_ref = vseq_lens_ano[0]

        #----------------------------------------------------
        # positions and lengths of left and right primers reported by primer3
        #----------------------------------------------------
        # The position of PRIMER_LEFT is the starting point of the product.
        ref_product_stt, left_len = map(int, self.PRIMER_LEFT_0.split(','))

        # The position of PRIMER_RIGHT is the end point of the product
        # because it is the start point of the reverse complement sequence.
        ref_product_end, right_len = map(int, self.PRIMER_RIGHT_0.split(','))

        #----------------------------------------------------
        # Calculation of product size considering the difference between the
        # variant length of ref and that of group 0 and group 1.
        l_product_size = list()
        l_product_end_pos = list()
        len_padding_left = rel_frag_pad_pre_end - ref_product_stt + 1

        # For each group
        for gno in range(2):
            # Calculate the length difference from REF for vseq
            vseq_len_gno = vseq_lens_ano[ano_gno[gno]]
            diff_vseq_len = vseq_len_ref - vseq_len_gno
            # Adjusting the product size and end point for each group
            my_product_end = ref_product_end - diff_vseq_len
            my_product_size = my_product_end - ref_product_stt + 1

            l_product_end_pos.append(my_product_end)
            l_product_size.append(my_product_size)

        # Difference in product size between groups
        diff_product_size = abs(l_product_size[0] - l_product_size[1])

        # ----------------------------------------------------------------
        # Digest size calculation

        # for indel
        # longer_group,
        # longer_length,
        # shorter_length,
        # diff_length,
        # digested_pos

        # If !indel, For those who are digested, use'/' to enter two numbers
        # (large or small). If not, enter the product size directly.
        digested_size = [[0 for j in range(0)] for i in range(2)]

        # Group number to be digested or longer indel_len
        digested_gno = self.target_gno
        not_digested_gno = utl.flip_gno(digested_gno)

        digested_ano = ano_gno[digested_gno]
        not_digested_ano = ano_gno[not_digested_gno]

        # if glv.INDEL, this is indel length diff. !=INDEL, it is digest pos
        digest_diff = diff_product_size

        # indel and snp behave the same as indel
        if self.mk_type == glv.MK_INDEL or \
            self.mk_type == glv.MK_SNP:

            # If indel, put two product sizes directly
            digested_size_str_g0 = str(l_product_size[0])
            digested_size_str_g1 = str(l_product_size[1])
            # indel is completed
            digested_size_str_g0 = "-"
            digested_size_str_g1 = "-"

        else:
            # for ! INDEL
            enzyme_name, \
            d_gno, \
            found_pos, \
            digest_pattern, \
            digested_pos \
                = EvalVariant.split_marker_info(self.marker_info)

            found_pos = int(found_pos)
            digested_pos = int(digested_pos)

            dig_pos = len_padding_left + found_pos + digested_pos

            L_digested_len = dig_pos
            R_digested_len = l_product_size[digested_gno] - L_digested_len

            #                    |ref_pos
            # <----------><======<.....>=====><----------->
            # <----------><======|=====><----------->

            # dig_gno=0
            # <----------><======<.....>=====><----------->
            #                       <-^-->
            # <----------><======|=====><----------->

            # dig_gno=1
            # <----------><======<.....>=====><----------->
            # <----------><======|=====><----------->
            #                   <-^-->

            #                    |ref_pos
            # <----------><======|=====><----------->
            # <----------><======<.....>=====><----------->

            # dig_gno=0
            #                    |ref_pos
            # <----------><======|=====><----------->
            #                   <-^-->
            # <----------><======<.....>=====><----------->

            # dig_gno=1
            #                    |ref_pos
            # <----------><======|=====><----------->
            # <----------><======<.....>=====><----------->
            #               <-^-->


            if str(digested_ano) in self.g0_gt:
                digested_size[0].append(L_digested_len)
                digested_size[0].append(R_digested_len)

            if str(not_digested_ano) in self.g0_gt:
                digested_size[0].append(
                    l_product_size[not_digested_gno])
                
            if str(digested_ano) in self.g1_gt:
                digested_size[1].append(L_digested_len)
                digested_size[1].append(R_digested_len)

            if str(not_digested_ano) in self.g1_gt:
                digested_size[1].append(
                    l_product_size[not_digested_gno])
                
            digested_size_str_g0 = \
                "/".join(
                    map(str, sorted(set(digested_size[0]), reverse=True)))
            digested_size_str_g1 = \
                "/".join(
                    map(str, sorted(set(digested_size[1]), reverse=True)))

        return \
            l_product_size[0], \
            l_product_size[1], \
            digested_gno, \
            digested_ano, \
            digested_size_str_g0, \
            digested_size_str_g1, \
            diff_product_size, \
            digest_diff

