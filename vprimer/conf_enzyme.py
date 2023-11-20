# -*- coding: utf-8 -*-

# http://rebase.neb.com/rebase/rebase.enz.html
# https://international.neb.com/tools-and-resources/selection-charts/isoschizoomers

import sys
import os
import re
import errno
from pathlib import Path
import pprint

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf

# 20231120
# biopython 1.76 のインストールを不要とする一時措置
app_dir = os.path.dirname(os.path.realpath(__file__))
#print(app_dir)
# Bio, 1.76 を、このディレクトリから読み出す
sys.path.insert(0, app_dir)

from Bio import Restriction
import Bio.Restriction.Restriction_Dictionary as ResDict

class ConfEnzyme(object):

    def open_log_enzyme(self):

        # in glv
        global log
        log = LogConf.open_log(__name__)


    def get_default_enzyme(self):

        default_enzyme_list = [
            'AluI', 'ApaI', 'AscI', 'AvrII', 'BamHI',
            'BbsI', 'BclI', 'BglII', 'BsaI', 'BsiWI',
            'BsmFI', 'BspHI', 'BssHII', 'Bst1107I', 'BstBI',
            'BstEII', 'BstXI', 'ClaI', 'DdeI', 'DpnI',
            'DraI', 'DraIII', 'Eco52I', 'EcoO109I', 'EcoO65I',
            'EcoRI', 'EcoRV', 'EcoT14I', 'FseI', 'HaeII',
            'HincII', 'HindIII', 'HinfI', 'HpaI', 'HphI',
            'KpnI', 'MluI', 'MseI', 'NcoI', 'NdeI',
            'NheI', 'NlaIII', 'NotI', 'NruI', 'NsiI',
            'PacI', 'PmeI', 'PmlI', 'Psp1406I', 'PstI',
            'PvuII', 'RsaI', 'SacI', 'SacII', 'SalI',
            'SapI', 'SbfI', 'ScaI', 'SfiI', 'SmaI',
            'SnaBI', 'SpeI', 'SphI', 'SspI', 'StuI',
            'SwaI', 'TaqI', 'Tth111I', 'XbaI', 'XhoI',
            'XmaI',
            ] # 71

        return default_enzyme_list


    def prepare_enzyme(self, user_enzyme_path_list, sys_path):

        # default enzyme
        default_enzyme_list = self.get_default_enzyme()

        # header
        header_list = ["# enzyme_name", "recogseq", "elucidate", "seqlen"]

        h = "#\n"
        h += "# When specifying the restriction enzymes to use in this\n"
        h += "# file, vprimer picks up only the restriction enzyme name,\n"
        h += "# so you only need to write the restriction enzyme name\n"
        h += "# on one line.\n"
        h += "# Lines starting with # and blank lines are ignored.\n"
        h += "#\n"

        header_txt = h
        header_txt += "\n"
        header_txt += "\t".join(header_list)

        # ----------------------------------------------------
        # make .whole_enzyme name
        ex_txt_sys_path = re.sub(r"\.txt$", "", str(sys_path))
        sys_path_whole = Path("{}{}".format(
            ex_txt_sys_path, glv.whole_enzyme_file_ext))

        # もし全制限酵素ファイルがない場合、
        if not sys_path_whole.exists():

            log.info("not found {}.".format(sys_path_whole))
            # 全制限酵素ファイルの内容を作成
            self.save_enzyme_file(
                sys_path_whole, header_txt, ResDict.rest_dict)

        # ----------------------------------------------------
        # make .original name
        sys_path_org = Path("{}{}".format(
            sys_path, glv.original_file_ext))

        # もしオリジナルファイルがない場合、
        if not sys_path_org.exists():

            log.info("not found {}.".format(sys_path_org))
            # オリジナルのファイル内容を作成
            # make enzyme file contents
            line_list = self.make_enzyme_file_contents(default_enzyme_list)

            # オリジナルを作り、バックアップしてコピー
            utl.refs_make_original_file_and_copy(
                header_txt, line_list, sys_path, sys_path_org)

        else:
            # compare timestamp for backup copy
            if utl.is_need_update(sys_path, "timestamp"):
                # copy if updated
                utl.save_to_tmpfile(sys_path, copy_mod=True)

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


        # return list
        enzyme_name_list = list()

        # -----------------------------------------------------
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


    def save_enzyme_file(self, file_path, header_txt, enzyme_name_list):
        '''
        '''

        # make enzyme file contents
        line_list = self.make_enzyme_file_contents(enzyme_name_list)

        with file_path.open('w',  encoding='utf-8') as f:

            f.write(header_txt + '\n')
            for line in line_list:
                f.write(line + '\n')


    def make_enzyme_file_contents(self, enzyme_name_list):

        """
        in Restriction_Dictionary.py
            Used REBASE emboss files version 908 (2019).

        in Restriction.py

        # @classmethod
        # def elucidate(cls):
        Return a string representing the recognition site and cuttings.

        Return a representation of the site with the cut on the (+) strand
        represented as '^' and the cut on the (-) strand as '_'.
        ie:

        >>> from Bio.Restriction import EcoRI, KpnI, EcoRV, SnaI
        >>> EcoRI.elucidate()   # 5' overhang
        'G^AATT_C'
        >>> KpnI.elucidate()    # 3' overhang
        'G_GTAC^C'
        >>> EcoRV.elucidate()   # blunt
        'GAT^_ATC'
        >>> SnaI.elucidate()    # NotDefined, cut profile unknown.
        '? GTATAC ?'
        >>>
        """

        total = 0
        cut_profile_unknown = 0
        cut_twice_not_implemented = 0
        last_topc = ""

        line_list = list()

        # ResDict.rest_dict is sorted by alphabet
        for enzyme_name in enzyme_name_list:

            topc = list(enzyme_name)[0]
            if topc != last_topc:

                line_list += [""]
                line_list += ["# {}".format(topc)]

            # RBを用いて、strからRestrictionTypeに変換する
            rb = Restriction.RestrictionBatch()
            rb.add(enzyme_name)
            # evaluate enzyme (name) and return it (as RestrictionType)
            enz_RestrictionType = rb.get(enzyme_name)

            recogseq = enz_RestrictionType.site
            elucidate = enz_RestrictionType.elucidate()
            seqlen = str(enz_RestrictionType.size)

            line_list += ["{}\t{}\t{}\t{}".format(
                enzyme_name, recogseq, elucidate, seqlen)]

            if '?' in elucidate:
                cut_profile_unknown += 1
            if 'cut twice' in elucidate:
                cut_twice_not_implemented += 1

            total += 1
            last_topc = topc

        valid_cnt = total - cut_profile_unknown - cut_twice_not_implemented
        line_list += [""]
        line_list += ["# total\t{}".format(total)]
        line_list += ["# cut_profile_unknown\t{}".format(cut_profile_unknown)]
        line_list += ["# cut_twice_not_implemented\t{}".format(
            cut_twice_not_implemented)]
        line_list += ["# valid_cnt\t{}".format(valid_cnt)]

        return line_list


    def check_enzyme_name_list(self, enzyme_name_list):

        # original count
        original_cnt = len(enzyme_name_list)
        log.info("original count={}, enzyme_name_list".format(original_cnt))

        # sorted remove duplicated list
        reduced_enzyme_name_list = sorted(list(set(enzyme_name_list)))
        set_cnt = len(reduced_enzyme_name_list)
        log.info("duplicate removed count={}, enzyme_name_list".format(
            set_cnt))

        for enzyme_name in reduced_enzyme_name_list:
            if enzyme_name not in ResDict.rest_dict:
                log.critical("your ENZYME <{}> is not in list, exit.".format(
                    enzyme_name))
                sys.exit(1)

        if original_cnt != set_cnt:
            diff_cnt = original_cnt - set_cnt
            log.info("There were {} duplicates out of {}.".format(
                diff_cnt, original_cnt))

        #log.info("{}".format(enzyme_name_list))
        log.info("total enzyme cnt={}.".format(set_cnt))

        return reduced_enzyme_name_list

