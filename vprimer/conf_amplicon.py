# -*- coding: utf-8 -*-

import sys
import errno
import re
from pathlib import Path
import pprint

# global variants
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf


class ConfAmplicon(object):

    def open_log_confampl(self):

        global log
        log = LogConf.open_log(__name__)


    def check_amplicon_param(self, amplicon_param):
        # "ACACTGACGACATGGTTCTACA,TACGGTAGCAGAGACTTGGTCT,45,40"

        amplicon_forward_tag = ""
        amplicon_reverse_tag = ""
        hairpin_tm = 0.0
        dimer_tm = 0.0

        ampl_p_list = amplicon_param.split(',')
        p_cnt = len(ampl_p_list)

        try:

            if p_cnt == 0 or p_cnt == 1:    # only amplicon_forward_tag error
                er_m = "--amplicon_param requires at least "
                er_m += "amplicon_forward_tag and amplicon_reverse_tag. "
                er_m += "exit."
                raise UserFormatErrorAmpl(er_m)

            elif p_cnt == 2:    # pair, tag: two tm value omitted

                amplicon_forward_tag = ampl_p_list[0]
                amplicon_reverse_tag = ampl_p_list[1]
                hairpin_tm = glv.hairpin_tm
                dimer_tm = glv.dimer_tm

                er_m = "Since hairpin_tm and dimer_tm are omitted, "
                er_m += "the system default values "
                er_m += "({},{}) are used for them.".format(
                    glv.hairpin_tm, glv.dimer_tm)

                log.info(er_m)

            elif p_cnt == 3:    # pair, tag, tm1: dimer_tm omitted

                amplicon_forward_tag = ampl_p_list[0]
                amplicon_reverse_tag = ampl_p_list[1]
                hairpin_tm = ampl_p_list[2]
                dimer_tm = glv.dimer_tm

                er_m = "Since dimer_tm is omitted, "
                er_m += "the system default values "
                er_m += "({}) are used for them.".format(glv.dimer_tm)

                log.info(er_m)

            elif p_cnt == 4:    # complete

                amplicon_forward_tag = ampl_p_list[0]
                amplicon_reverse_tag = ampl_p_list[1]
                hairpin_tm = ampl_p_list[2]
                dimer_tm = ampl_p_list[3]

            else:

                er_m = "Too many components of "
                er_m += "amplicon_param {}. exit.".format(p_cnt)
                raise UserFormatErrorAmpl(er_m)

            p_tag = re.compile('[atgcATGC]+')

            # forward_tag reverse_tag ATGC
            if not p_tag.fullmatch(amplicon_forward_tag) or \
                not p_tag.fullmatch(amplicon_reverse_tag):

                er_m = "Both tags must be ATGC sequences ({},{}).".format(
                    amplicon_forward_tag, amplicon_reverse_tag)
                raise UserFormatErrorAmpl(er_m)

            # hairpin_tm and dimer_tm
            if not utl.is_float(hairpin_tm) or not utl.is_float(dimer_tm):

                er_m = "Both ({},{})must be integers or floats.".format(
                    hairpin_tm, dimer_tm)
                raise UserFormatErrorAmpl(er_m)

        except UserFormatErrorAmpl as ex:
            log.error(ex)
            sys.exit(1)

        return \
            amplicon_forward_tag, \
            amplicon_reverse_tag, \
            float(hairpin_tm), \
            float(dimer_tm)


    def check_snp_filter_sub_command(self):
        # --snp_filter gcrange:50-55 interval:1M
        # aaa,bbb,ccc

        # default value

        #print("self.snp_filter={}".format(self.snp_filter))

        snp_filter_gcrange = "" # "50-55"
        snp_filter_gc_min = 0.00
        snp_filter_gc_max = 0.00
        snp_filter_interval = "" # "1M"

        sub_com_dict = dict()

        if self.snp_filter == "":

            er_m = "snp_filter is specified but the subcommand is empty. "
            er_m += "sub_command must be specified."
            raise UserFormatErrorAmpl(er_m)

        try:

            for sub_command in self.snp_filter.split(','):

                # separator :
                if not ":" in sub_command:
                    er_m = "snp_filter sub_command '{}' ".format(sub_command)
                    er_m += "must be separated "
                    er_m += "from the sub_command name and value by ':'."
                    raise UserFormatErrorAmpl(er_m)

                # com_name
                # gcrange:50-55, interval:1M[:top|mid|bot]
                sub_com_list = sub_command.split(':')
                com_name = sub_com_list[0]

                if not com_name in glv.snp_filter_sub_command_list:
                    er_m = "snp_filter sub_command '{}' ".format(com_name)
                    er_m += "must be one of these {}.".format(
                        glv.snp_filter_sub_command_list)
                    raise UserFormatErrorAmpl(er_m)

                # remove [0] item
                sub_com_dict[com_name] = sub_com_list[1:]

            # set value
            for subc in glv.snp_filter_sub_command_list:
                #print("{}={}".format(subc, sub_com_dict[subc]))

                value_str = sub_com_dict[subc]
                #print("{}, {}".format(subc, value_str))

                if subc == "gcrange":
                    # separator :
                    range_value = value_str[0]
                    if not "-" in range_value:
                
                        er_m = "gcrange value must be separated "
                        er_m += "by '-'. ({})".format(range_value)
                        raise UserFormatErrorAmpl(er_m)

                    mingc, maxgc = range_value.split('-')

                    if not utl.is_float(mingc) or not utl.is_float(maxgc):
                        er_m = "The min and max values of gcrange must be "
                        er_m += "int or float. min={}, max{}".format(
                            mingc, maxgc)
                        raise UserFormatErrorAmpl(er_m)

                    snp_filter_gc_min = float(mingc)
                    snp_filter_gc_max = float(maxgc)
                    snp_filter_gcrange = "{}-{}".format(mingc, maxgc)

                    #print("set snp_filter_gcrange {}-{}".format(
                    #    mingc, maxgc))

                elif subc == "interval":
                    # M G
                    distance_str = value_str[0]
                    #print("set distance_str {}".format(distance_str))
                    distance = distance_str[:-1]
                    if not utl.is_float(distance):
                        er_m = "interval must be "
                        er_m += "integer {}({}).".format(
                            distance, distance_str)
                        raise UserFormatErrorAmpl(er_m)
                        
                    if distance_str.endswith('M'):
                        distance = int(distance) *1000000

                    elif distance_str.endswith('G'):
                        distance = int(distance) *1000000000

                    snp_filter_interval = distance


        # snp_filter_gcrange
        # snp_filter_interval

        except UserFormatErrorAmpl as ex:
            log.error(ex)
            sys.exit(1)

        er_m = "{} was set to snp_filter_gcrange.".format(
            snp_filter_gcrange)
        log.info(er_m)
        er_m = "{:,} was set to snp_filter_interval.".format(
            snp_filter_interval)
        log.info(er_m)

        return \
            snp_filter_gcrange, \
            snp_filter_gc_min, \
            snp_filter_gc_max, \
            snp_filter_interval


class UserFormatErrorAmpl(Exception):
    """Detect user-defined format errors"""
    pass

