# -*- coding: utf-8 -*-

import sys
#import os
import errno
import re
from pathlib import Path

import pprint

# global variants
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf

class ConfCurrSet(object):

    def open_log_currset(self):

        global log
        log = LogConf.open_log(__name__)


    def out_current_settings(self):
        ''' Output to a file with config (ini format)
        '''

        current_setting_ini = list()
        whole_command_line = ' '.join(sys.argv)

        # [vprimer]
        current_setting_ini.append("{}".format(glv.ini_section))

        # now date
        current_setting_ini.append(
            "\n# start at: {}".format(glv.now_datetime_form))

        # ini file
        specified_ini_file = "ini file not specified."
        if self.user_ini_file is not None:
            specified_ini_file = "specified ini file is {}".format(
                self.user_ini_path)
        current_setting_ini.append("\n# {}".format(specified_ini_file))

        # whole_command_line
        whole_command_line = "\n# {}".format(whole_command_line)
        current_setting_ini.append(whole_command_line)

        current_setting_ini.append("\n#")

        for vname in self.conf_dict.keys():

            if 'chosen' in self.conf_dict[vname]:
                key_value = "{} = {}".format(
                    vname, self.conf_dict[vname]['chosen'])

                current_setting_ini.append(key_value)

                # # separating,
                if vname == "ref" or \
                    vname == "stop" or \
                    vname == "product_size" or \
                    vname == "enzyme" or \
                    vname == "group_members" or \
                    vname == "blast_distance" or \
                    vname == "use_joblib_threading" or \
                    vname == "amplicon_param":

                    current_setting_ini.append("\n#")

        # exist or not, self.curr_setting_path
        if self.curr_setting_path.exists():
            # If the file exists, move it to bak
            log.info("found {}".format(self.curr_setting_path))
            utl.save_to_tmpfile(self.curr_setting_path)
        else:
            log.info("not found {}".format(self.curr_setting_path))

        # write to sample_name_file
        with self.curr_setting_path.open('w', encoding='utf-8') as f:
            # Export while adjusting
            #line = self.convert_setting_ini(current_setting_ini)
            #f.write("{}\n".format("\n".join(current_setting_ini)))

            pprint.pprint(current_setting_ini)
            line = self.convert_setting_ini(current_setting_ini)
            f.write("{}\n".format(line))

        log.info("save {}".format(self.curr_setting_path))

        # ====
        # これは、デバッグ用かもしれない
        log.info("self.conf_dict=\n{}".format(
            pprint.pformat(self.conf_dict)))

        # これらは必須。
        log.info("self.regions_dict=\n{}".format(
            pprint.pformat(self.regions_dict)))
        log.info("self.group_members_dict=\n{}".format(
            pprint.pformat(self.group_members_dict)))
        log.info("self.distinguish_groups_list=\n{}".format(
            pprint.pformat(self.distinguish_groups_list)))


    def convert_setting_ini(self, current_setting_ini):
        '''
        '''

        oline = list()

        for line in current_setting_ini:
            if line.startswith("regions") or \
                line.startswith("distinguish_groups") or \
                line.startswith("group_members"):

                line = self.format_distin(line)

            elif "," in line:
                line = re.sub(r",", ", ", line)
            oline.append(line)
            
        return "\n".join(oline)


    def format_distin(self, line):

        # insert cr after =
        line = re.sub(r" = ", " = \n    ", line) 
        # separate value to 2nd line, etc
        line = re.sub(r"(,)([^,:]+)(:)", r"\n    \2\3", line) 

        # space both side / :
        line = re.sub(r"/"," / ", line)
        line = re.sub(r":", " : ", line) 
        # space one side ,
        line = re.sub(r",", ", ", line) 

        line += "\n"
        return line




