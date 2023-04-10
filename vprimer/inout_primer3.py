# -*- coding: utf-8 -*-

import sys
#import os
import errno
import re
import pprint
import primer3
from pathlib import Path

import logging
log = logging.getLogger(__name__)

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

class InoutPrimer3(object):

    def __init__(self):

        # self.p3_header_list = glv.conf.primer3_header_dict
        self.primer3_header_dict = glv.conf.primer3_header[glv.conf.p3_mode]

        self.p3_input_dict = {
            'P3_COMMENT' : '',
            'SEQUENCE_TARGET': '',
            'SEQUENCE_EXCLUDED_REGION': '',
            'SEQUENCE_ID' : '',
            'SEQUENCE_TEMPLATE' : ''}

        self.p3_out = ''
        self.p3_output_dict = dict()
        # reserve
        self.p3_output_dict['PRIMER_PAIR_NUM_RETURNED'] = 0
        self.p3_output_dict['PRIMER_ERROR'] = ''

        self.PRIMER_PAIR_NUM_RETURNED = \
            self.p3_output_dict['PRIMER_PAIR_NUM_RETURNED']
        self.PRIMER_ERROR = \
            self.p3_output_dict['PRIMER_ERROR']

        self.primer_region = ''
        self.left_primer_region = ''
        self.right_primer_region = ''

        self.left_fasta_id = ''
        self.right_fasta_id = ''

        self.product_chrom = ''
        self.product_sttpos = 0
        self.product_endpos = 0
        self.product_pos = ''
        self.product_seq = ''
        self.product_gc_contents = ''

    #--------------------------------------------
    # output
    #def get_product_pos(self):
    #    # chr01:194047-194068:plus, chr01:194226-194246:minus
    #    print('get_product_pos')
    #    print("{}, {}".format(self.left_fasta_id, self.right_fasta_id))
    #    sys.exit()
    #    return self.product_pos

    def get_product_pos(self):
        return self.product_pos

    def get_product_gc_contents(self):
        return self.product_gc_contents

    def get_product_seq(self):
        return self.product_seq

    def get_primer_left_id(self):
        return self.left_fasta_id

    def get_primer_right_id(self):
        return self.right_fasta_id

    def make_primer_seq(self, left_fasta_id, right_fasta_id):
        # summer 20210910

        # chr01:194047-194068:plus, chr01:194226-194246:minus
        self.left_fasta_id = left_fasta_id
        self.right_fasta_id = right_fasta_id
        left_info = self.left_fasta_id.split(':')
        right_info = self.right_fasta_id.split(':')


        self.product_chrom = str(left_info[0])
        self.product_sttpos = int((left_info[1].split('-'))[0])
        self.product_endpos = int((right_info[1].split('-'))[1])

        self.product_pos = "{}:{}-{}".format(
            self.product_chrom, self.product_sttpos, self.product_endpos)

        self.product_seq = glv.conf.pick_refseq(
            self.product_chrom, self.product_sttpos, self.product_endpos)

        self.product_gc_contents = utl.gc(self.product_seq)

        #print("{}".format(self.left_fasta_id))
        #print("{}".format(self.right_fasta_id))

        #print("{}".format(self.product_chrom))
        #print("{}".format(self.product_sttpos))
        #print("{}".format(self.product_endpos))
        #print("{}".format(self.product_pos))
        #print("{}".format(self.product_seq))
        #print("{}".format(self.product_gc_content))
        #sys.exit()

    #def set_primer_name(self, left_fasta_id, right_fasta_id):
    #    self.left_fasta_id = left_fasta_id
    #    self.right_fasta_id = right_fasta_id

    def get_primer_product_size(self):
        return self.p3_output_dict['PRIMER_PAIR_0_PRODUCT_SIZE']

    def get_primer_left_info(self):
        return map(int, self.p3_output_dict['PRIMER_LEFT_0'].split(','))

    def get_primer_right_info(self):
        return map(int, self.p3_output_dict['PRIMER_RIGHT_0'].split(','))

    def get_primer_region(self, primer_loc="both"):
        # 2022-12-28 for 'snp'
        region = self.primer_region

        if primer_loc == "left":
            region = self.left_primer_region

        elif primer_loc == "right":
            region = self.right_primer_region

        return region

    def get_primer_left_seq(self):
        return self.p3_output_dict['PRIMER_LEFT_0_SEQUENCE']

    def get_primer_right_seq(self):
        return self.p3_output_dict['PRIMER_RIGHT_0_SEQUENCE']

    def get_primer_left(self):
        return self.p3_output_dict['PRIMER_LEFT_0']

    def get_primer_right(self):
        return self.p3_output_dict['PRIMER_RIGHT_0']

    def get_p3_comment(self):
        return self.p3_output_dict['P3_COMMENT']

    def get_sequence_id(self):
        return self.p3_output_dict['SEQUENCE_ID']

    def get_primer3_out(self):
        return self.p3_out


    def set_primer3_out(self, p3_out):
        '''
        '''

        self.p3_out = p3_out
        primer_region_list = list()

        for item in p3_out.split('\n'):
            if item == '=' or item == '':
                continue
            tag, value = item.split('=')
            self.p3_output_dict[tag] = value

            if tag == 'PRIMER_PAIR_NUM_RETURNED':
                self.PRIMER_PAIR_NUM_RETURNED = int(value)

            elif tag == 'PRIMER_ERROR':
                self.PRIMER_ERROR = str(value)

            elif tag == 'PRIMER_LEFT_0':
                self.left_primer_region = value
                primer_region_list.append(self.left_primer_region)

            elif tag == 'PRIMER_RIGHT_0':
                end_rel_pos, length = map(int, value.split(','))
                # 525,5 => 521,5
                # 521...5
                plus_rel_pos = end_rel_pos - length + 1
                # 29221222 ncod3
                self.right_primer_region = "{},{}".format(
                    plus_rel_pos, length)
                primer_region_list.append(self.right_primer_region)

            if len(primer_region_list) != 0:
                self.primer_region = ' '.join(primer_region_list)

    #--------------------------------------------
    # input
    def get_sequence_excluded_region(self):
        return self.p3_input_dict['SEQUENCE_EXCLUDED_REGION']

    def set_p3_comment(self, p3_comment):
        self.p3_input_dict['P3_COMMENT'] = p3_comment

    def set_sequence_target(self, sequence_target):
        self.p3_input_dict['SEQUENCE_TARGET'] = sequence_target

    def add_ex_region(self, any_excluded_region):

        if self.p3_input_dict['SEQUENCE_EXCLUDED_REGION'] == '':
            ex_region = [any_excluded_region]
        else:
            ex_region = [
                self.p3_input_dict['SEQUENCE_EXCLUDED_REGION'],
                any_excluded_region]

        self.p3_input_dict['SEQUENCE_EXCLUDED_REGION'] = \
            ' '.join(ex_region)

    def set_sequence_id(self, sequence_id):
        self.p3_input_dict['SEQUENCE_ID'] = sequence_id

    def set_sequence_template(self, sequence_template):
        self.p3_input_dict['SEQUENCE_TEMPLATE'] = sequence_template


    def get_p3_input(self):

        # glv.conf.self.primer3_header_dict
        p3_input_list = list()

        # convert global dictionary to list
        for p3_key in glv.conf.primer3_header[glv.conf.p3_mode].keys():
            if p3_key == 'p3_key':
                continue

            p3_input_list += ["{}={}".format(
                p3_key,
                glv.conf.primer3_header[glv.conf.p3_mode][p3_key])]


        #self.p3_input_dict = {
        #    'P3_COMMENT' : '',
        #    'SEQUENCE_TARGET': '',
        #    'SEQUENCE_EXCLUDED_REGION': '',
        #    'SEQUENCE_ID' : '',
        #    'SEQUENCE_TEMPLATE' : ''}

        # add nessasary key=value
        p3_input_list += ['{}={}'.format(
            'P3_COMMENT',
            self.p3_input_dict['P3_COMMENT'])]
        p3_input_list += ['{}={}'.format(
            'SEQUENCE_TARGET',
            self.p3_input_dict['SEQUENCE_TARGET'])]
        p3_input_list += ['{}={}'.format(
            'SEQUENCE_EXCLUDED_REGION',
            self.p3_input_dict['SEQUENCE_EXCLUDED_REGION'])]
        p3_input_list += ['{}={}'.format(
            'SEQUENCE_ID',
            self.p3_input_dict['SEQUENCE_ID'])]
        p3_input_list += ['{}={}'.format(
            'SEQUENCE_TEMPLATE',
            self.p3_input_dict['SEQUENCE_TEMPLATE'])]
        p3_input_list += ['=\n']

        #pprint.pprint(p3_input_list)
        #txt = '\n'.join(map(str, p3_input_list))

        return '\n'.join(map(str, p3_input_list))


    # 2022-12-28
    def check_p3_pairpin_dimer(self):

        left_primer_ok = True
        right_primer_ok = True

        # 本来は、パラメータで指定すべき
        # not use
        self.FRtags_Hp_Dm = \
            "ACACTGACGACATGGTTCTACA,TACGGTAGCAGAGACTTGGTCT,45,40"

        # from parameter
        self.amplicon_forward_tag = glv.conf.amplicon_forward_tag
        self.amplicon_reverse_tag = glv.conf.amplicon_reverse_tag
        hairpin_tm = glv.conf.hairpin_tm
        dimer_tm = glv.conf.dimer_tm

        self.hairpin_tm = float(hairpin_tm)
        self.dimer_tm = float(dimer_tm)

        left_primer = self.get_primer_left_seq()
        right_primer = self.get_primer_right_seq()

        #################################################
        l_seq = self.amplicon_forward_tag + left_primer
        r_seq = self.amplicon_reverse_tag + right_primer
        #################################################

        #print("l_seq={}, r_seq={}".format(l_seq, r_seq))

        hd_dict = self.hairpin_dimer(l_seq, r_seq)

        # hairpin
        if hd_dict['hpin']['l']['stat'] and \
            hd_dict['hpin']['l']['tm'] >= self.hairpin_tm:
            left_primer_ok = False

        if hd_dict['hpin']['r']['stat'] and \
            hd_dict['hpin']['r']['tm'] >= self.hairpin_tm:
            right_primer_ok = False

        # hetero dimer
        if hd_dict['hetd']['stat'] and \
            hd_dict['hetd']['tm'] >= self.dimer_tm:
            left_primer_ok = False
            right_primer_ok = False

        # homo dimer
        if hd_dict['homd']['l']['stat'] and \
            hd_dict['homd']['l']['tm'] >= self.dimer_tm:
            left_primer_ok = False

        if hd_dict['homd']['r']['stat'] and \
            hd_dict['homd']['r']['tm'] >= self.dimer_tm:
            right_primer_ok = False

        return left_primer_ok, right_primer_ok

    def hairpin_dimer(self, l_seq, r_seq):


        #print("in hairpin_dimer")

        # hairpin
        l_hpin, r_hpin = self.calc_hairpin(l_seq, r_seq)
        # hetero dimer
        hetd = self.calc_hetero_dimer(l_seq, r_seq)
        # homo dimer
        l_homd, r_homd = self.calc_homo_dimer(l_seq, r_seq)

        hairpin_dimer_dict = {
            'hpin':  {
                'l': {
                    'stat':     l_hpin.structure_found,
                    'tm':       l_hpin.tm,
                    'detail':   l_hpin.ascii_structure,
                    'ok':       '.',
                    },
                'r': {
                    'stat':     r_hpin.structure_found,
                    'tm':       r_hpin.tm,
                    'detail':   r_hpin.ascii_structure,
                    'ok':       '.',
                    },
                },
            'hetd': {
                'stat':     hetd.structure_found,
                'tm':       hetd.tm,
                'detail':   hetd.ascii_structure,
                'ok':       '.',
                },
            'homd': {
                'l': {
                    'stat':     l_homd.structure_found,
                    'tm':       l_homd.tm,
                    'detail':   l_homd.ascii_structure,
                    'ok':       '.',
                    },
                'r': {
                    'stat':     r_homd.structure_found,
                    'tm':       r_homd.tm,
                    'detail':   r_homd.ascii_structure,
                    'ok':       '.',
                    },
                },
            }

        return hairpin_dimer_dict

    def calc_hairpin(self, l_seq, r_seq):
        #print("in calc_hairpin")
        #print("l_seq={}".format(l_seq))
        #print("r_seq={}".format(r_seq))

        l_hairpin = self.calcHairpin(l_seq)
        r_hairpin = self.calcHairpin(r_seq)
        return l_hairpin, r_hairpin

    def calc_hetero_dimer(self, l_seq, r_seq):
        hetd = self.calcHeterodimer(l_seq, r_seq)
        return hetd

    def calc_homo_dimer(self, l_seq, r_seq):
        l_homd, r_homd = self.calcHomodimer(l_seq, r_seq)
        return l_homd, r_homd

    def calcHairpin(self, seq):
        ''' calcHairpin(
                seq[, mv_conc=50.0, dv_conc=0.0, dntp_conc=0.8,
                dna_conc=50.0, temmp_c=37, max_loop=30])
        '''
        p3bc = primer3.bindings.calcHairpin(
            seq, output_structure=True)
        #print("in calcHairpin")
        #print(p3bc)
        #sys.exit(1)
        return p3bc

    def calcHeterodimer(self, seq1, seq2):
        ''' calcHeterodimer(seq1, seq2[, mv_conc=50.0, dv_conc=0.0,
            dntp_conc=0.8, dna_connc=50.0, temp_c=37, max_loop=30])
        '''
        p3hd = primer3.bindings.calcHeterodimer(
            seq1, seq2, output_structure=True)
        return p3hd

    def calcHomodimer(self, l_seq, r_seq):
        ''' calcHomodimer(seq[, mv_conc=50.0, dv_conc=0.0,
            dntp_conc=0.8, dna_conc=50.0, ttemp_c=37, max_loop=30])
        '''
        l_homd = primer3.bindings.calcHomodimer(
            l_seq, output_structure=True)
        r_homd = primer3.bindings.calcHomodimer(
            r_seq, output_structure=True)
        return l_homd, r_homd














