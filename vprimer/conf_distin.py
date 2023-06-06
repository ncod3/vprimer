# -*- coding: utf-8 -*-

import sys
#import os
import errno
import re
import numpy as np
from pathlib import Path

import pprint

# global variants
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf


class ConfDistinG(object):

    def open_log_distin(self):

        global log
        log = LogConf.open_log(__name__)

    # #######################################
    # 1) init
    # #######################################
    def init_regions_str(self):
        ''' from choice_variable
            egions 

        Variable origin priority and standardize the string format
            1) command parameter        <target>    for Easy mode
            2) command parameter        <regions>
            3) ini file                 <regions>
        '''

        regions_str = ""

        # 1) Easy Mode: A value is set in either a_sample or b_sample.
        if self.is_easy_mode():
            regions_str = self.target

        # 2) param: regions
        if utl.is_Not_NoneAndNull(self.conf_dict['regions']['param']):
            regions_str = self.conf_dict['regions']['param']

        # 3) ini: regions
        elif utl.is_Not_NoneAndNull(self.conf_dict['regions']['ini']):
            regions_str = self.conf_dict['regions']['ini']

        # ; separator were converted to ,
        regions_str = re.sub(r";", ",", regions_str)
        # ini use '=' as separator, so substitute to ','
        regions_str = re.sub(r"=", ",", regions_str)

        # set to self.regions_str
        return regions_str


    # #######################################
    def init_group_members_str(self):
        ''' from choice_variable
            group_members

        self.is_auto_group == True;  self.auto_group
        else:

        Variable origin priority
            1) command parameter        <a_sample,b_sample> For Easy mode
            2) command parameter        <group_members>
            3) ini file                 <group_members>
            4) sample_name in_vcf_file  <vcf>

        Format:
            group0: m1, m2, m3, group1: m4, m5, m6
        '''

        group_members_str = ""

        #print("self.auto_group={}".format(self.auto_group))
        #print("self.is_auto_group={}".format(self.is_auto_group))
        #print("self.vcf_sample_nickname_list={}".format(
        #    self.vcf_sample_nickname_list))
        #sys.exit(1)

        if self.is_easy_mode():

            # auto_groupは、デフォルトの調査対象サンプル群

            # self.auto_group に値が設定されているならば、
            #   self.is_auto_group == True
            #   通常通り、group_members_str に auto_group のメンバを
            #   設定する

            # 0) auto_group
            if self.is_auto_group:

                # auto_group:Hitomebore,Ginganoshizuku,Takanari,Tupa121-3
                # グループ名 auto_groupを設定する
                group_members_str = "{}:{}".format(glv.AUTO_GROUP,
                    self.auto_group)

                group_members_str = re.sub(r",$", "", group_members_str)

            # 1) param: a_sample, b_sample   -> EASY_MODE
            #   In easy mode, the group name is automatically determined
            #   by 'a' and 'b'.
            else:

                # self.auto_group に値が設定されていないならば、
                group0 = "a"
                group1 = "b"

                group_members_str = "{}:{},{}:{}".format(
                    group0, self.a_sample, group1, self.b_sample)
                group_members_str = re.sub(r",$", "", group_members_str)

        # 2) from param or 3) from ini
        else:
            # from param or ini or default (self.group_members_vcf_str)
            #
            # in choice_variables in conf.py, 
            # # Default is handled differently for this group_members only
            # # self.conf_dict['group_members']['default'] = \
            # #    self.group_members_vcf_str
            group_members_str = self.selected_value('group_members')

        # auto_group:all という書き方を許し、全サンプルをここに書く
        # all_targetというグループ名も後にdict内で設定する

        # set to self.group_members_str
        return group_members_str


    # #######################################
    def init_distinguish_groups_str(self):
        ''' from choice_variable
            distinguish_groups

        Variable origin priority
            1. command parameter        <a_sample, b_sample>
            2. command parameter        <distinguish_groups>
            3. ini file                 <distinguish_groups>
        '''

        distinguish_groups_str = ""

        # EASY_MODE has all the information
        if self.is_easy_mode():

            if self.is_auto_group:
                group0 = glv.AUTO_GROUP
                group1 = glv.AUTO_GROUP
                 
            else:
                group0 = glv.GROUP_NAME[0]
                group1 = glv.GROUP_NAME[1]

            # EASY_MODE will format variables later
            region_name = glv.EASY_MODE

            # pick_mode
            pick_mode = self.pick_mode

            #print("in init_distinguish_groups_str")
            #print(self.pick_mode)

            # indel_size
            indel_size = self.indel_size

            distinguish_groups_str = "{}/{}:{}:{}:{}".format(
                group0, group1, region_name, pick_mode, indel_size)

            #print(distinguish_groups_str)

        else:
            distinguish_groups_str = \
                self.selected_value('distinguish_groups')

        # auto_group/auto_group:<EASY_MODE>:indel+caps:20-200
        #print("in init_distinguish_groups_str")
        #print("distinguish_groups_str >{}<".format(distinguish_groups_str))
        #sys.exit(1)

        return distinguish_groups_str


    # #######################################
    # 2) rectify
    # #######################################
    def rectify_regions_str(self, regions_str):
        ''' Check the contents of regions_str
        Format:
            range_str   ::= stt - end
            scope       ::= chrom_name | chrom_name:range_str
            target      ::= scope | target scope
            region_def  ::= target_name | target_name:scope
            regions     ::= region_def | regions region_def

        '''

        regions_str_rectified = ""
        er_m = ""

        try:

            # check 'all' in target
            for region_def in regions_str.split(','):
                # region_def  ::= target_name | target_name:scope
                if region_def.lower() == 'all':
                    # If target has only "all" region_def, cancel all other
                    # settings and set all only.
                    mes = "In EASY_MODE, 'all' key word was detected in "
                    mes += "target variable, so settings other than all "
                    mes += "are canceled."
                    log.info(mes)
                    # insert chrom name list
                    regions_str = ','.join(self.ref_fasta_chrom_list)
                    break

            # convert Easy Mode target
            if self.is_easy_mode():
                easy_regions_str = ""
                # get list count
                list_num = len(regions_str.split(','))
                # get num of digit
                num_digit = len(str(list_num))

                rg_cnt = 1
                for region_def in regions_str.split(','):

                    # region_name = region1
                    # Match the number of digits and output
                    target_name = "{}_{:0={}}".format(
                        glv.easy_region, rg_cnt, num_digit)

                    easy_regions_str += "{}:{},".format(
                        target_name, region_def)
                    rg_cnt += 1

                # complete
                easy_regions_str = re.sub(r",$", "", easy_regions_str)
                regions_str = easy_regions_str

            # region_def  ::= target_name | target_name:scope
            # regions     ::= region_def | regions region_def

            # temporary padding field
            regions_str_padding = ""

            # Align region_def to 3 fields
            for region_def in regions_str.split(','):

                # 0. check field_cnt
                field_cnt = len(region_def.split(':'))

                if field_cnt > 3:
                    er_m = "The number of fields exceeds 3({}).".format(
                        field_cnt)
                    raise UserFormatErrorDistin(er_m)

                elif field_cnt < 3:
                    # complement field_cnt, finally set field_cnt to 3
                    add_field = 3 - field_cnt
                    while add_field > 0:
                        region_def += ":"
                        add_field -= 1

                regions_str_padding += "{},".format(region_def)

            regions_str_padding = re.sub(r",+$", "", regions_str_padding)

            # check or insert
            target_name_dup_check = list()

            for region_def in regions_str_padding.split(','):

                # scope       ::= chrom_name | chrom_name:range_str
                # target      ::= scope | target scope
                # region_def  ::= target_name | target_name:scope

                target_name, chrom_name, range_str = region_def.split(':')

                # check chrom name
                if not self.is_chrom_name(chrom_name):
                    er_m = "Specified chromosome name does not exist."
                    raise UserFormatErrorDistin(er_m)

                # t_name:chr01: fill the chrom_info
                if range_str == "":

                    chrom_info_list = self.get_chrom_info(chrom_name)
                    start_pos = chrom_info_list[0]
                    end_pos = chrom_info_list[1]
                    length =chrom_info_list[2]
                    region_def_tmp = chrom_info_list[3]

                    #print("{},{},{},{}".format(
                    #    region_def_tmp, start_pos, end_pos, length))

                    range_str = "{}-{}".format(start_pos, end_pos)
                    region_def = "{}:{}".format(target_name, region_def_tmp)

                # rectify
                regions_str_rectified += '{},'.format(region_def)
                scope = "{}:{}".format(chrom_name, range_str)

                # target_name != chrom_name
                if self.is_chrom_name(target_name):
                    er_m = "Chromosome name as target_name cannot be "
                    er_m += "used because it is a reserved word that "
                    er_m += "indicates an entire chromosome."
                    raise UserFormatErrorDistin(er_m)

                elif not self.is_chrom_name(chrom_name):
                    er_m = "Specified chromosome name does not exist."
                    raise UserFormatErrorDistin(er_m)

                elif "-" not in range_str:
                    er_m = "Region must be separated by hyphens."
                    raise UserFormatErrorDistin(er_m)

                elif not self.is_valid_int_range(range_str):
                    er_m = "This scope ({}) ".format(scope)
                    er_m += "is incorrect."
                    raise UserFormatErrorDistin(er_m)

                elif not self.is_valid_chrom_range(scope):
                    er_m = "This range ({}) ".format(scope)
                    er_m += "is beyond the range of the chromosome."
                    raise UserFormatErrorDistin(er_m)

                if target_name in target_name_dup_check:
                    er_m += "target_name {} duplicated.".format(
                        target_name)
                    raise UserFormatErrorDistin(er_m)

                target_name_dup_check.append(target_name)

            # set all chrom info if not easy_mode
            if not self.is_easy_mode():
                for chrom_name in self.ref_fasta_chrom_list:

                    chrom_info_list = self.get_chrom_info(chrom_name)
                    start_pos = chrom_info_list[0]
                    end_pos = chrom_info_list[1]
                    length =chrom_info_list[2]
                    region_def = chrom_info_list[3]

                    # regist chromosome info as "each chromosome" name.
                    chrom_region_def = "{}:{}:{}-{}".format(
                        chrom_name, chrom_name, start_pos, end_pos)
                    regions_str_rectified += ",{}".format(chrom_region_def)

        except UserFormatErrorDistin as ex:
            rgst = "regions_str=\'{}\'.".format(regions_str)
            log.error("User conf error: {} {}".format(ex, rgst))
            sys.exit(1)

        else:
            log.info("ok, regions_str_rectified is valid format.")

        regions_str_rectified = re.sub(r",+$", "", regions_str_rectified)

        return regions_str_rectified


    # #######################################
    def rectify_group_members_str(self, group_members_str):
        ''' Check the contents of group_members_str
        Format:
            members         ::= member | members member
            group           ::= gname:members
            group_members   ::= group | group_members group
        '''

        group_members_str_rectified = ""
        er_m = ""

        # here, it can access to self.vcf_sample_nickname_list
        #print(self.vcf_sample_nickname_list)

        try:

            gname_dup_check = list()
            member_dup_check = list()
            gname = ""

            for member in group_members_str.split(','):

                if ":" in member:
                    gname, member = member.split(':')
                    group_members_str_rectified += "{}:".format(
                        gname)

                    if gname in gname_dup_check:
                        er_m = "gname {} duplicated.".format(
                            gname)
                        raise UserFormatErrorDistin(er_m)

                    gname_dup_check.append(gname)

                # gname check
                if gname == "":
                    er_m = "Group_name is blank."
                    raise UserFormatErrorDistin(er_m)

                # auto_group
                elif not glv.conf.is_auto_group and gname == glv.AUTO_GROUP:
                    er_m = "{} cannot be used as a group name.".format(
                        gname)
                    raise UserFormatErrorDistin(er_m)

                elif "ref" == gname.lower():
                    er_m = "{} cannot be used as a group name.".format(
                        gname)
                    raise UserFormatErrorDistin(er_m)

                elif self.is_chrom_name(gname):
                    er_m = "chrom name {} is a reserved word, ".format(
                        gname)
                    er_m += "so it cannot be used as a group name."
                    raise UserFormatErrorDistin(er_m)

                if self.is_easy_mode():

                    if member == "":
                        member = "ref"

                if not utl.is_sample_name(member):

                    # if auto_group:all
                    # all vcf samples are target
                    if gname.lower() == glv.AUTO_GROUP and \
                        member.lower() == glv.ALL_MEMBER:
                        member = ",".join(self.vcf_sample_nickname_list)

                    else:
                        er_m = "The sample name \'{}\' does not ".format(
                            member)
                        er_m += "match either the nickname, basename or "
                        er_m += "fullname in the vcf file."
                        raise UserFormatErrorDistin(er_m)

                elif member in member_dup_check:
                    er_m = "member {} duplicated.".format(
                        member_name)
                    raise UserFormatErrorDistin(er_m)
                
                group_members_str_rectified += "{},".format(
                    member)
                member_dup_check.append(member)

        except UserFormatErrorDistin as ex:
            gmst = " group_members_str=\'{}\'.".format(group_members_str)
            log.error("User conf error: {} {}".format(ex, gmst))
            sys.exit(1)

        else:
            log.info("ok, group_members_str_rectified is valid format.")

        # final , will be removed
        group_members_str_rectified = re.sub(
            r",+$", "", group_members_str_rectified)

        #print("group_members_str_rectified={}".format(
        #    group_members_str_rectified))
        #sys.exit(1)

        return group_members_str_rectified


    # #######################################
    def rectify_distinguish_groups_str(self, distinguish_groups_str):
        ''' Check the contents of gdistinguish_groups_str
        '''

        distinguish_groups_str_rectified = ""
        er_m = ""

        # default self.pick_mode
        # default self.indel_size

        try:

            # Completing and checking the content of each distin_str
            for distin_str in distinguish_groups_str.split(','):

                # remove space and tab to cp
                distin_str_cp = re.sub(r"\s", "", distin_str)

                #print("in rectify_distinguish_groups_str")
                #print(distin_str_cp)

                # -----------------------------------
                # 0. check field_cnt
                field_cnt = len(distin_str_cp.split(':'))
                if field_cnt > 4:
                    er_m = "The number of fields exceeds 4({}).".format(
                        field_cnt)
                    raise UserFormatErrorDistin(er_m)

                # complement field_cnt, finally set field_cnt to 4
                add_field = 4 - field_cnt

                while add_field > 0:
                    distin_str_cp += ":"
                    add_field -= 1

                # Check the contents of the four fields individually
                gname_pair, region_names, pick_mode, indel_size \
                    = distin_str_cp.split(':')

                # -----------------------------------
                # 1. check gname_pair
                # if it is void,
                if gname_pair == "":
                    er_m = "Group pairs must always be specified."
                    raise UserFormatErrorDistin(er_m)

                # separate to gname0, gname1
                gname_pair_cnt = len(gname_pair.split('/'))
                if gname_pair_cnt == 2:
                    # ok
                    pass

                elif gname_pair_cnt > 2:
                    er_m = "Group pair is two groups separated by /."
                    raise UserFormatErrorDistin(er_m)

                elif gname_pair_cnt == 1:
                    # If there is only one specification, compare with ref
                    gname_pair_add = "ref/{}".format(gname_pair)
                    er_m = "Added ref/ because gname_pair is only "
                    er_m += "'{}' => {}.".format(
                        gname_pair, gname_pair_add)
                    log.info(er_m)
                    gname_pair = gname_pair_add

                # Make sure the group name is a valid name
                g_name0, g_name1 = gname_pair.split('/')

                # when glv.conf.is_auto_group is True,
                # auto_group/auto_group:e_reg_1:indel+caps:20-200
                if g_name0 == glv.AUTO_GROUP:
                    pass

                elif g_name0 == g_name1:
                    er_m = "Two groups have the same name."
                    raise UserFormatErrorDistin(er_m)

                # check
                for g_name in [g_name0, g_name1]:
                    if not self.is_group_name(g_name):
                        er_m = "group name '{}' is not ".format(g_name)
                        er_m += "included in the group_name_list."
                        raise UserFormatErrorDistin(er_m)

                # -----------------------------------
                # 2. check region_names
                # if it is void,
                if region_names == "":
                    er_m = "region names must always be specified."
                    raise UserFormatErrorDistin(er_m)

                for r_name in region_names.split('+'):
                    if not self.is_region_name(r_name):
                        er_m = "region name '{}' is not ".format(r_name)
                        er_m += "included in the region name list."
                        raise UserFormatErrorDistin(er_m)

                # -----------------------------------
                # 4. check indel_size
                if indel_size == "":
                    # default setting
                    indel_size = self.indel_size

                if not self.is_valid_int_range(indel_size):
                    er_m = "indel_size ({}) must have ".format(indel_size)
                    er_m += "two integers separated by a \'-\' "
                    er_m += "and min <= max."
                    raise UserFormatErrorDistin(er_m)

                distin_str_rectified = "{}:{}:{}:{}".format(
                    gname_pair, region_names, pick_mode, indel_size)

                distinguish_groups_str_rectified += "{},".format(
                    distin_str_rectified)


        except UserFormatErrorDistin as ex:
            dstr = " distin_str=\'{}\'.".format(distin_str)
            gnlt = " group_name_list=\'{}\'.".format(
                ", ".join(self.group_name_list))
            rnlt = " region_name_list=\'{}\'.".format(
                ", ".join(self.region_name_list))
            log.error("User conf error: {} {}{}{}".format(
                ex, dstr, gnlt, rnlt))
            sys.exit(1)

        else:
            log.info("ok, distinguish_groups_str_rectified is valid format.")

        # final , will be removed
        distinguish_groups_str_rectified = re.sub(
            r",+$", "", distinguish_groups_str_rectified)

        return distinguish_groups_str_rectified


    # #######################################
    # 3) set dict
    # #######################################
    def set_regions_dict(self, regions_str):

        rectified_regions_str = self.rectify_regions_str(regions_str)

        regions_dict = dict()
        region_name_list = list()

        for region in rectified_regions_str.split(','):
            region_name, chrom_name, r_range = region.split(':')
            start_pos, end_pos = r_range.split('-')
            region_def = "{}:{}".format(chrom_name, r_range) 
            regions_dict[region_name] = \
                {   'chr': chrom_name,
                    'start': start_pos,
                    'end': end_pos,
                    'reg': region_def
                }

        region_name_list = list(regions_dict.keys())

        #pprint.pprint(regions_dict)
        #pprint.pprint(region_name_list)
        #sys.exit(1)

        return rectified_regions_str, regions_dict, region_name_list


    # #######################################
    # In the case of auto_group, only auto_group is registered in
    # rectified_group_members_str, so even if keys() is taken,
    # only one auto_group is extracted.
    def set_group_members_dict(self, group_members_str):

        rectified_group_members_str = \
            self.rectify_group_members_str(group_members_str)

        #print("self.vcf_sample_basename_list={}".format(
        #    self.vcf_sample_basename_list))
        #print("rectified_group_members_str={}".format(
        #    rectified_group_members_str))

        group_members_dict = dict()
        group_name_list = list()

        '''
        group_members_dict = {
            'a': {
                'gname': 'a',
                'sn_idx_lst': [0, 17],
                'sn_lst': ['Hitomebore', 'Takanari'],
                'sn_nd': array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 1, 0, 0, 0, 0])
            },
            'b': {
                'gname': 'b',
                'sn_idx_lst': [6, 1],
                'sn_lst': ['Tupa121-3', 'Ginganoshizuku'],
                'sn_nd': array([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0])
            }
        }
        '''

        # 定義の文字列を , で区切り、
        for sample_n in rectified_group_members_str.split(','):

            # :が入っているのはグループ名として扱う
            if ':' in sample_n:
                # snを上書き
                gname, sample_n = sample_n.split(':')
                # gname をリストへ
                group_name_list.append(gname)
                # gnameのdict
                group_members_dict[gname] = {
                    'gname': gname,
                    'sn_lst': list(),
                    'sn_idx_lst': list(),
                    'sn_nd': np.zeros(self.vcf_sample_cnt, dtype=np.int64),
                }

            # convert to nickname
            sn = utl.get_nickname(sample_n)

            # sn_lst
            group_members_dict[gname]['sn_lst'].append(sn)
            # sn_idx
            sn_idx = int(self.vcf_sample_nickname_dict[sn]['no'])
            group_members_dict[gname]['sn_idx_lst'].append(sn_idx)
            # sn_nd
            # 固定グループの onehot data
            group_members_dict[gname]['sn_nd'][sn_idx] = 1


        #print("group_members_dict={}".format(group_members_dict))
        #print("group_name_list={}".format(group_name_list))
        #sys.exit(1)

        return group_members_dict, group_name_list


    # #######################################
    def set_distinguish_groups_list(self, distinguish_groups_str):

        ''' ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        in:     distinguish_groups_str
        out:    distinguish_groups_str_rectified
                distinguish_groups_list

        distinguish_groups_str_rectified :=
            "distin_str,distin_str,distin_str,..."

        distinguish_groups_list :=
            [distin_grp_dict, distin_grp_dict, distin_grp_dict, ...]
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' '''

        # A string that can be converted into a list of dictionary
        # by complementing the original input string.
        distinguish_groups_str_rectified = \
            self.rectify_distinguish_groups_str(distinguish_groups_str)

        # A list of distin_grp_dict (dictionaries of units to be processed)
        distinguish_groups_list = list()

        # distin_str(units to process) are connected by ,
        for distin_str in distinguish_groups_str_rectified.split(','):

            # distin_str has 4 elements, connected by :
            # A/B, reg1+reg2+reg3, Join region name with +, caps, indel_size
            gname_pair, region_names, pick_mode, indel_size = \
                distin_str.split(':')

            # ----------------------------------------------------
            # must updata
            product_size = self.product_size
            # ----------------------------------------------------

            # separate two group name, A B from A/B
            gname0, gname1 = gname_pair.split("/")
            # make id with group0 and group1
            groups_id = "{}/{}".format(gname0, gname1)
            # [reg1, reg2, reg3]
            region_name_list = region_names.split("+")


            '''
            # ------------------------------
            # sample list in group
            # 1) from gname to nickname list (not sorted)
            g0mem_nm_lst = \
                utl.get_sample_list_from_group_list([gname0], 'nickname')
            # 2) from nickname_list to idx_list
            g0mem_idx_lst = [int(self.vcf_sample_nickname_dict[sn]['no'])
                for sn in g0mem_nm_lst]
            # https://deepage.net/features/numpy-zeros.html
            # 3) ndarray
            g0mem_nd = np.zeros(self.vcf_sample_cnt, dtype=np.int64)
            # 4) get group ndarray
            for sn_idx in g0mem_idx_lst:
                g0mem_nd[sn_idx] = 1

            print("gname0={}".format(gname0))
            print("a_sample={}".format(self.a_sample))
            print("g0mem_nm_lst={}".format(g0mem_nm_lst))
            print("g0mem_idx_lst={}".format(g0mem_idx_lst))
            print("g0mem_nd={}".format(g0mem_nd))

            # 1) from gname to nickname list (not sorted)
            g1mem_nm_lst = \
                utl.get_sample_list_from_group_list([gname1], 'nickname')
            # 2) from nickname_list to idx_list
            g1mem_idx_lst = [int(self.vcf_sample_nickname_dict[sn]['no'])
                for sn in g1mem_nm_lst]
            # 3) ndarray
            g1mem_nd = np.zeros(self.vcf_sample_cnt, dtype=np.int64)
            # 4) get group ndarray
            for sn_idx in g1mem_idx_lst:
                g1mem_nd[sn_idx] = 1
            

            print("gname1={}".format(gname1))
            print("b_sample={}".format(self.b_sample))
            print("g1mem_nm_lst={}".format(g1mem_nm_lst))
            print("g1mem_idx_lst={}".format(g1mem_idx_lst))
            print("g1mem_nd={}".format(g1mem_nd))
            '''

            # sorted and unique member's string separated by commma
            # 'Ginganoshizuku,Ginganoshizuku,Hitomebore,Hitomebore,
            #   Takanari,Takanari,Tupa121-3,Tupa121-3'
            sample_sorted_list_str = ','.join(sorted(set(
                self.group_members_dict[gname0]['sn_lst'] + 
                self.group_members_dict[gname1]['sn_lst'])))

            # 当初は空
            bed_thal_path = "-"

            # --------------------------------------------------------
            # sn_nd(sample name's onehot ndarray)'s list
            # Can be held even with auto_group
            group01_sn_nds = [
                self.group_members_dict[gname0]['sn_nd'],
                self.group_members_dict[gname1]['sn_nd']
            ]

            # distin_grp_dict is a dictionary with 9 elements
            # add to distin_grp_dict in prepare_distin_grp_files outlist.py
            distin_grp_dict = {
                0               : gname0,
                1               : gname1,
                'groups_id'     : groups_id,
                'sorted_samples': sample_sorted_list_str,
                'bed_thal_path' : bed_thal_path,
                'regions'       : region_name_list,
                'pick_mode'     : pick_mode,
                'indel_size'    : indel_size,
                'product_size'  : product_size,
                'group01_sn_nds': group01_sn_nds,
                'distin_str'    : distin_str,
                'hdimer_seq'    : list(),
                'hdimer_ng'     : list()}

            # append a dict to list
            distinguish_groups_list.append(distin_grp_dict)


        return \
            distinguish_groups_str_rectified, \
            distinguish_groups_list

class UserFormatErrorDistin(Exception):
    """Detect user-defined format errors"""
    pass


