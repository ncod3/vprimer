#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
#import os
import errno
import time
import pprint

# global variables declaration
import vprimer.glv as glv
import vprimer.utils as utl
from vprimer.logging_config import LogConf

# --- read conf and param
glv.init('vprimer')
log = LogConf.open_log(__name__)

# using Class
from vprimer.variant import Variant
from vprimer.marker import Marker
from vprimer.primer import Primer
from vprimer.formtxt import FormTxt

def main():


    log.info('vprimer started at {}'.format(glv.now_datetime_form))

    # run
    vpr = VPrimer()
    vpr.run()

    log.info("vprimer finished {}\n".format(utl.elapse_epoch()))


class VPrimer(object):

    def __init__(self):

        self.variant = Variant()
        self.marker = Marker()
        self.primer = Primer()
        self.formtxt = FormTxt()


    def prepare(self):

        # Determine the value of a variable according to the priority
        # of the parameter

        # Choice of variables by priority
        glv.conf.choice_variables()

        # Setup all variables
        glv.conf.setup_variables()

        # prepare bed_thal.bed
        glv.conf.prepare_bed_thal()

        # Write the current settings to a file
        glv.conf.out_current_settings()

        # Prepare distin_grp_dict info
        glv.outlist.prepare_distin_grp_files()

        # touch bak_timestamp file in bak directory
        glv.conf.touch_bak_timestamp()

    def run(self):

        self.prepare()

        # variant
        self.variant.pick_variant()
        # marker
        self.marker.design_marker()
        # primer
        self.primer.construct_primer()
        # format
        self.formtxt.format_text()


if __name__ == '__main__':
    main()


