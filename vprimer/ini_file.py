# -*- coding: utf-8 -*-

import sys
#import os
import errno
import time
from pathlib import Path

import re
import pprint

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

import configparser

class IniFile(object):

    def __init__(self):

        # for default
        self.ini = dict()

    def read_ini_file(self, user_ini_file):
        '''
        '''
        user_ini_path = Path(user_ini_file).resolve()

        # don't permit empty_lines_in_values
        self.ini = configparser.ConfigParser(
            empty_lines_in_values=False
        )
        # don't convert to lower case
        self.ini.optionxform = str

        utl.prelog(
             "ini_file_path = {}".format(user_ini_path), __name__)
 
        if user_ini_path.exists():
            with user_ini_path.open('r', encoding='utf-8') as f:
                # configparser: read_file
                self.ini.read_file(f)
                #  adjustment of variable format
                self.ini = self.format_ini_variable(self.ini)

        else:
             utl.prelog(
                 "not found {}. exit.".format(user_ini_file), __name__)
             sys.exit(1)


    def format_ini_variable(self, ini):

        for section in ini.sections():
            for key in ini[section]:

                val = ini[section][key]
                # remove hash comment
                val = utl.strip_hash_comment(val)
                # remove \n at the beginning of value, not necessary \n
                val = val.lstrip()
                # replace internal \n to semicolons
                val = val.replace('\n', ',')

                # replace white space to one space
                if key == 'group_members':
                    val = re.sub(r"\s+", " ", val)
                    val = re.sub(r"\s*:\s*", ":", val)
                    val = re.sub(r" ", ",", val)
                    val = re.sub(r",+", ",", val)
                    val = re.sub(r",;", ";", val)
                    val = re.sub(r";", ",", val)

                else:
                    # remove white space
                    val = re.sub(r"\s+", "", val)

                # reset
                ini[section][key] = val

        return ini

