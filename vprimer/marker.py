# -*- coding: utf-8 -*-

import sys
#import os
from pathlib import Path
import errno
import time
import pprint

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
log = LogConf.open_log(__name__)

import pandas as pd
from joblib import Parallel, delayed

#from vprimer.enzyme import Enzyme
from vprimer.eval_variant import EvalVariant


class Marker(object):

    def __init__(self):

        self.enzyme_name_list = list()


    def design_marker(self):

        self.enzyme_name_list = glv.conf.enzyme_name_list

        # start marker
        start = utl.get_start_time()

        proc_name = "marker"
        log.info("-------------------------------")
        log.info("Start processing {}\n".format(proc_name))

        # stop, action, gothrough
        ret_status = utl.decide_action_stop(proc_name)

        if ret_status == "stop":
            msg = "STOP. "
            msg += "Current process \'{}\' ".format(proc_name)
            msg += "has exceeded the User-specified stop point "
            msg += "\'{}', ".format(glv.conf.stop)
            msg += "so stop program. exit."
            log.info(msg)
            sys.exit(1)


        elif ret_status == "gothrough":
            msg = "SKIP \'{}\' proc, ".format(proc_name)
            msg += "glv.conf.progress = {}, ".format(glv.conf.progress)
            msg += "glv.conf.stop = {}, ".format(glv.conf.stop)
            msg += "so skip program."
            log.info(msg)
            return

        # Design a fragment sequence for primer3
        proc_cnt = 0
        for distin_gdct, reg in glv.conf.gdct_reg_list:
            proc_cnt += 1

            # logging current target
            utl.pr_dg("marker", distin_gdct, reg, proc_cnt)

            # read variant file 
            variant_file = distin_gdct['variant']['fn'][reg]['out_path']
            log.info("variant_file {}".format(variant_file))

            df_distin = pd.read_csv(
                variant_file, sep='\t', header=0, index_col=None)

            # file name to write out result to text
            out_txt_path = distin_gdct['marker']['fn'][reg]['out_path']
            utl.save_to_tmpfile(out_txt_path)

            # header
            header_txt = distin_gdct['marker']['hdr_text']
            # if glv.conf.is_auto_group, remove last 2 columns
            #header_txt = utl.remove_auto_grp_header_txt(header_txt)

            with out_txt_path.open('a', encoding='utf-8') as f:

                # write header (no parallel mode)
                f.write("{}\n".format(header_txt))

                ''' eval_variant.py
                class EvalVariant(object):
                def _check_effect_of_enzyme(
                    self, seq_target, enzyme_name_list):
                    http://biopython.org/DIST/docs/cookbook/Restriction.html
                    biopython <= 1.76 for IUPACAmbiguousDNA()

                    multi_site_seq = Seq(seq_target, IUPACAmbiguousDNA())
                    rb = Restriction.RestrictionBatch(enzyme_name_list)
                    Analong = Restriction.Analysis(rb, multi_site_seq)
                    caps_ResTyp_dict = Analong.with_sites()

                This RestrictionBatch method sometimes returned slightly
                inaccurate results when executed in parallel.
                Therefore, parallel is not used now.
                '''

                #if glv.conf.parallel == True:
                # always False
                if False:

                    log.info("do Parallel cpu {} parallel {}".format(
                        glv.conf.thread,
                        glv.conf.parallel_full_thread))

                    Parallel(
                        n_jobs=glv.conf.parallel_full_thread,
                        backend="threading")(
                        [
                            delayed(self.loop_evaluate_for_marker)
                                (distin_file, variant_df_row, f) \
                                for variant_df_row in \
                                    df_distin.itertuples()
                        ]
                    )

                else:

                    log.info("do Serial cpu 1")

                    # each variant
                    for variant_df_row in df_distin.itertuples():

                        # Determine if the variant can be used as a marker.
                        # For those that can be marked, prepare the
                        # information for primer3.
                        #self.loop_evaluate_for_marker(
                        #    distin_file, variant_df_row, f)
                        self.loop_evaluate_for_marker(
                            distin_gdct, variant_df_row, f)

            # don't need in parallel mode
            #utl.sort_file(
            #    'marker', distin_file, out_txt_path,
            #    'chrom', 'pos', 'marker_info', 'string')

            log.info("marker {} > {}.txt\n".format(
                utl.elapse_str(start),
                distin_gdct['marker']['fn'][reg]['base_nam']))


    #def loop_evaluate_for_marker(self, distin_file, variant_df_row, f):
    def loop_evaluate_for_marker(self, distin_gdct, variant_df_row, f):
        '''
        '''

        # In order to perform parallel processing safely,
        # an instance is created for each processing unit here.
        evalv = EvalVariant(self.enzyme_name_list)
        #evalv.evaluate_for_marker(variant_df_row, distin_file)
        evalv.evaluate_for_marker(variant_df_row, distin_gdct)

        for mk_type in evalv.mk_type.split(','):

            # self.mk_type: CAPS,SNP
            evalv.set_mk_type(mk_type)
            marker_available = False

            if mk_type == glv.MK_INDEL:
                marker_available = True

            elif mk_type == glv.MK_CAPS:
                # If mk_type is CAPS, after checking caps
                marker_available = evalv.check_caps()

            elif mk_type == glv.MK_SNP:
                # glv.conf.snp_marker_diff_len is 0 as default
                if evalv.diff_len <= glv.conf.snp_marker_diff_len:
                    marker_available = True
                    
                #print()
                #print("in _loop_evaluate_for_marker: mk_type == glv.MK_SNP")
                
                #print("glv.conf.snp_marker_diff_len={}".format(
                #    glv.conf.snp_marker_diff_len))
                #print("evalv.var_type={}".format(evalv.var_type))
                #print("evalv.len_g0g1_dif_long={}".format(
                #    evalv.len_g0g1_dif_long))
                #print("evalv.shorter_len={}".format(evalv.shorter_len))
                #print("evalv.longer_len={}".format(evalv.longer_len))

                #print("evalv.diff_len={}".format(evalv.diff_len))
                #print("marker_available={}".format(marker_available))

            elif mk_type == glv.MK_NOTYPE:
                marker_available = False

            # indel or CAPS marker by SNP with restriction enzyme site
            # effective
            if marker_available == True:

                # Create seq_template_ref if markerable
                evalv.make_seq_template_ref()

                # Lines are copied as many as the number of effective
                # restriction enzymes.
                evalv.copy_line_for_effective_restriction_enzymes()

                # write out to file
                f.write("{}\n".format(evalv.line))


