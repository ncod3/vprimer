# -*- coding: utf-8 -*-

# http://rebase.neb.com/rebase/rebase.enz.html
# https://international.neb.com/tools-and-resources/selection-charts/isoschizoomers

import sys
#import os
import errno
from pathlib import Path
import pprint

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
import Bio.Restriction.Restriction_Dictionary as ResDict

class ConfEnzyme(object):

    def open_log_enzyme(self):

        # in glv
        global log
        log = LogConf.open_log(__name__)


    def prepare_enzyme(self, user_enzyme_path_list, sys_path):
        # ----------------------------
        # self.enzyme_name_list

        # return list
        enzyme_name_list = list()

        # default enzyme
        self.set_default_enzyme()

        # make .original name
        sys_path_org = Path("{}{}".format(
            sys_path, glv.original_file_ext))

        # もしオリジナルファイルがない場合、
        if not sys_path_org.exists():

            log.info("not found {}.".format(sys_path_org))
            # オリジナルファイルを作る
            header_txt = "#"
            header_txt += "enzyme_name\t" + "recogseq\t"
            header_txt += "elucidate\t" + "seqlen\n"

            # オリジナルのファイル内容を作成
            line_list = list()
            for line in self.default_enzyme_names:
                line_list.append("{}".format("\t".join(line)))
            # オリジナルを作り、バックアップしてコピー
            utl.refs_make_original_file_and_copy(
                header_txt, line_list, sys_path, sys_path_org)

        else:
            # sys_path backup
            if glv.need_update == utl.is_need_update(
                sys_path, self.bak_timestamp_path):
                    # copy if updated
                    utl.save_to_tmpfile(sys_path, True, True)

        # 読み込むファイルは、システムファイルかユーザファイル
        if user_enzyme_path_list:
            read_file_path_list = user_enzyme_path_list
            #print("user list exist")
            #print(read_file_path_list)

        else:
            read_file_path_list = [sys_path]
            #print("user list not exist")
            #print(read_file_path_list)
            #print(sys_path)
            
        # リスト内のpathから読み出す
        for read_file_path in read_file_path_list:
            #print(read_file_path)
            if not read_file_path.exists():
                
                # ファイルがない場合、exit
                er_m = "user specified enzyme file is not found, "
                er_m += "{}".format(read_file_path)
    
                log.error("{} exit.".format(er_m))
                log.error("read_file_path_list={}".format(
                    ", ".join(map(str, read_file_path_list))))
                sys.exit(1)


            # backup and copy the files in refs
            slink_path = self.refs_dir_path / "{}{}".format(
                glv.slink_prefix, read_file_path.name)

            # backup and copy the files in refs
            utl.refs_file_slink_backup_and_copy(read_file_path, slink_path)

            # read enzyme content
            enzname_list = list()
            with read_file_path.open('r',  encoding='utf-8') as f:
                # iterator
                for r_liner in f:
                    r_line = r_liner.strip()    # cr, ws

                    if r_line.startswith('#') or r_line == '':
                        continue

                    r_line = utl.strip_hash_comment(r_line)
                    enzymes = r_line.split("\t")
                    enzname_list.append(enzymes[0])

            log.info("enzyme cnt={},{}".format(
                len(enzname_list), read_file_path))
            enzyme_name_list += enzname_list

        return enzyme_name_list


    def check_enzyme_name_list(self, enzyme_name_list):

        # ResDict.rest_dict

        #print(enzyme_name_list)

        lower_to_upper_dict = dict()
        enzyme_name_list_lower = list()

        # for check
        for En in enzyme_name_list:
            en = En.lower()
            lower_to_upper_dict[en] = En
            enzyme_name_list_lower.append(en)

        # convert enzyme name to lower
        #enzyme_name_list_lower = [en.lower() for en in enzyme_name_list]

        # original count
        original_cnt = len(enzyme_name_list_lower)
        log.info("original count={}, enzyme_name_list".format(original_cnt))

        # sorted remove duplicated list
        reduced_enzyme_name_list = sorted(list(set(enzyme_name_list_lower)))
        set_cnt = len(reduced_enzyme_name_list)
        log.info("duplicate removed count={}, enzyme_name_list".format(
            set_cnt))

        # to lower
        ResDict_lower = [en.lower() for en in ResDict.rest_dict]

        for enzyme_name in reduced_enzyme_name_list:
            if enzyme_name not in ResDict_lower:
                log.critical("your ENZYME <{}> is not in list, exit.".format(
                    enzyme_name))
                sys.exit(1)

        if original_cnt != set_cnt:
            diff_cnt = original_cnt - set_cnt
            log.info("There were {} duplicates out of {}.".format(
                diff_cnt, original_cnt))

        #log.info("{}".format(enzyme_name_list))
        log.info("total enzyme cnt={}.".format(set_cnt))

        reduced_enzyme_name_list_upper = \
            [lower_to_upper_dict[en] for en in reduced_enzyme_name_list]

        #print(reduced_enzyme_name_list_upper)
        #sys.exit(1)

        return reduced_enzyme_name_list_upper


    def set_default_enzyme(self):

        # header = "# name\trecogseq\telucidate\tseqlen\n\n"
        self.default_enzyme_names = [
        ['# A'],
            ['AluI',        'AGCT',             'AG^_CT',           '4'],
            ['ApaI',        'GGGCCC',           'G_GGCC^C',         '6'],
            ['AscI',        'GGCGCGCC',         'GG^CGCG_CC',       '8'],
            ['AvrII',       'CCTAGG',           'C^CTAG_G',         '6'],
            [''],
        ['# B'],
            ['BamHI',       'GGATCC',           'G^GATC_C',         '6'],
            ['BbsI',        'GAAGAC',           'GAAGACNN^NNNN_N',  '6'],
            ['BclI',        'TGATCA',           'T^GATC_A',         '6'],
            ['BglII',       'AGATCT',           'A^GATC_T',         '6'],
            ['BsaI',        'GGTCTC',           'GGTCTCN^NNNN_N',   '6'],
            ['BsiWI',       'CGTACG',           'C^GTAC_G',         '6'],
            ['BsmFI',       'GGGAC',            'GGGACNNNNNNNNNN^NNNN_N','5'],
            ['BspHI',       'TCATGA',           'T^CATG_A',         '6'],
            ['BssHII',      'GCGCGC',           'G^CGCG_C',         '6'],
            ['Bst1107I',    'GTATAC',           'GTA^_TAC',         '6'],
            ['BstBI',       'TTCGAA',           'TT^CG_AA',         '6'],
            ['BstEII',      'GGTNACC',          'G^GTNAC_C',        '7'],
            ['BstXI',       'CCANNNNNNTGG',     'CCAN_NNNN^NTGG',   '12'],
            [''],
        ['# C'],
            ['ClaI',        'ATCGAT',           'AT^CG_AT',         '6'],
            [''],
        ['# D'],
            ['DdeI',        'CTNAG',            'C^TNA_G',          '5'],
            ['DpnI',        'GATC',             'GA^_TC',           '4'],
            ['DraI',        'TTTAAA',           'TTT^_AAA',         '6'],
            ['DraIII',      'CACNNNGTG',        'CAC_NNN^GTG',      '9'],
            [''],
        ['# E'],
            ['Eco52I',      'CGGCCG',           'C^GGCC_G',         '6'],
            ['EcoO109I',    'RGGNCCY',          'RG^GNC_CY',        '7'],
            ['EcoO65I',     'GGTNACC',          'G^GTNAC_C',        '7'],
            ['EcoRI',       'GAATTC',           'G^AATT_C',         '6'],
            ['EcoRV',       'GATATC',           'GAT^_ATC',         '6'],
            ['EcoT14I',     'CCWWGG',           'C^CWWG_G',         '6'],
            [''],
        ['# F'],
            ['FseI',        'GGCCGGCC',         'GG_CCGG^CC',       '8'],
            [''],
        ['# H'],
            ['HaeII',       'RGCGCY',           'R_GCGC^Y',         '6'],
            ['HincII',      'GTYRAC',           'GTY^_RAC',         '6'],
            ['HindIII',     'AAGCTT',           'A^AGCT_T',         '6'],
            ['HinfI',       'GANTC',            'G^ANT_C',          '5'],
            ['HpaI',        'GTTAAC',           'GTT^_AAC',         '6'],
            ['HphI',        'GGTGA',            'GGTGANNNNNNN_N^N', '5'],
            [''],
        ['# K'],
            ['KpnI',        'GGTACC',           'G_GTAC^C',         '6'],
            [''],
        ['# M'],
            ['MluI',        'ACGCGT',           'A^CGCG_T',         '6'],
            ['MseI',        'TTAA',             'T^TA_A',           '4'],
            [''],
        ['# N'],
            ['NcoI',        'CCATGG',           'C^CATG_G',         '6'],
            ['NdeI',        'CATATG',           'CA^TA_TG',         '6'],
            ['NheI',        'GCTAGC',           'G^CTAG_C',         '6'],
            ['NlaIII',      'CATG',             '_CATG^',           '4'],
            ['NotI',        'GCGGCCGC',         'GC^GGCC_GC',       '8'],
            ['NruI',        'TCGCGA',           'TCG^_CGA',         '6'],
            ['NsiI',        'ATGCAT',           'A_TGCA^T',         '6'],
            [''],
        ['# P'],
            ['PacI',        'TTAATTAA',         'TTA_AT^TAA',       '8'],
            ['PmeI',        'GTTTAAAC',         'GTTT^_AAAC',       '8'],
            ['PmlI',        'CACGTG',           'CAC^_GTG',         '6'],
            ['Psp1406I',    'AACGTT',           'AA^CG_TT',         '6'],
            ['PstI',        'CTGCAG',           'C_TGCA^G',         '6'],
            ['PvuII',       'CAGCTG',           'CAG^_CTG',         '6'],
            [''],
        ['# R'],
            ['RsaI',        'GTAC',             'GT^_AC',           '4'],
            [''],
        ['# S'],
            ['SacI',        'GAGCTC',           'G_AGCT^C',         '6'],
            ['SacII',       'CCGCGG',           'CC_GC^GG',         '6'],
            ['SalI',        'GTCGAC',           'G^TCGA_C',         '6'],
            ['SapI',        'GCTCTTC',          'GCTCTTCN^NNN_N',   '7'],
            ['SbfI',        'CCTGCAGG',         'CC_TGCA^GG',       '8'],
            ['ScaI',        'AGTACT',           'AGT^_ACT',         '6'],
            ['SfiI',        'GGCCNNNNNGGCC',    'GGCCN_NNN^NGGCC',  '13'],
            ['SmaI',        'CCCGGG',           'CCC^_GGG',         '6'],
            ['SnaBI',       'TACGTA',           'TAC^_GTA',         '6'],
            ['SpeI',        'ACTAGT',           'A^CTAG_T',         '6'],
            ['SphI',        'GCATGC',           'G_CATG^C',         '6'],
            ['SspI',        'AATATT',           'AAT^_ATT',         '6'],
            ['StuI',        'AGGCCT',           'AGG^_CCT',         '6'],
            ['SwaI',        'ATTTAAAT',         'ATTT^_AAAT',       '8'],
            [''],
        ['# T'],
            ['TaqI',        'TCGA',             'T^CG_A',           '4'],
            ['Tth111I',     'GACNNNGTC',        'GACN^N_NGTC',      '9'],
            [''],
        ['# X'],
            ['XbaI',        'TCTAGA',           'T^CTAG_A',         '6'],
            ['XhoI',        'CTCGAG',           'C^TCGA_G',         '6'],
            ['XmaI',        'CCCGGG',           'C^CCGG_G',         '6'],
            [''],
        ['# end'],
        ]


