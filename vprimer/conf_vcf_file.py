# -*- coding: utf-8 -*-

import sys
#import os
import errno
import re
from pathlib import Path

import pprint
import vcfpy
import pandas as pd

# global variants
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf

class ConfVcfFile(object):

    def open_log_vcffile(self):

        global log
        log = LogConf.open_log(__name__)


    def prepare_vcf(self, src_path, gtonly_path):

        # src_path: self.user_vcf_path for symlink
        # gtonly_path: user vcf is converted to GTonly vcf

        log.info("prepare_vcf start.")

        if gtonly_path.exists() and src_path == gtonly_path:

            mes = "The user-specified vcf is already used "
            mes += "by the system, so no preparation is required.\n"
            mes += "user={}\n sys={}.".format(src_path, gtonly_path)

            log.info(mes)
            return

        # symlink name for self.user_vcf_path
        slink_path = self.refs_dir_path / "{}{}".format(
            glv.slink_prefix, src_path.name)
        # sample name list is extracted from GTonly vcf
        sample_name_path = self.vcf_sample_name_txt_path
        # sample & bam corresponding table
        sample_bam_path = self.vcf_sample_bam_table_path

        # Update the file with the old and new timestamps
        # between user_vcf_path and symlink.
        utl.refs_file_slink_backup_and_copy(src_path, slink_path)

        # between user_vcf_path and gtonly_path
        if glv.need_update == utl.is_need_update(src_path, gtonly_path):

            # update gtonly vcf
            self.update_gtonly_vcf(src_path, gtonly_path)

        # sample name & bam table template
        # print sample_bam_path contents to STDOUT
        self.save_vcf_sample_name_and_bam_to_file(
            gtonly_path, sample_name_path, sample_bam_path)

        # sample variable
        # print sample_name_path contents to STDOUT
        self.vcf_sample_nickname_list, \
        self.vcf_sample_basename_list, \
        self.vcf_sample_fullname_list, \
        self.vcf_sample_nickname_dict, \
        self.vcf_sample_basename_dict, \
        self.vcf_sample_fullname_dict, \
        self.group_members_vcf_str = \
            self.make_vcf_sample_variable(sample_name_path)

        # total sample cnt
        self.vcf_sample_cnt = len(self.vcf_sample_nickname_list)

        # no := idx
        #pprint.pprint(self.vcf_sample_nickname_dict)


    def update_gtonly_vcf(self, src_path, gtonly_path):

        cmd1 = "{} annotate --threads {} -O z -x ^FMT/GT -o {} {}".format(
                'bcftools',
                self.parallel_full_thread,
                gtonly_path,
                src_path)

            # vcf_file(_GTonly.vcf.gz) summer
        
            # if bcftools 1.10.2, it have --force option.
            # if 1.9.0, if we have an error
            # No matching tag in -x ^FMT/GT
            # we will not worry, continue

        err_str = utl.try_exec_error(cmd1)

        if err_str == '':
            pass

        # >No matching tag in -x ^FMT/GT
        elif err_str.startswith('No matching tag in'):

            # error, but go ahead
            log.error("we will go ahead if bcftools says, >{}<.".format(
                err_str))

            # directly slink to vcf_file_slink_system
            # ln -s real_gtgz slink_
            utl.ln_s(src_path, gtonly_path)

        else:
            log.error(">{}<".format(err_str))
            sys.exit(1)

        # make tbi
        utl.tabix(gtonly_path)


    def save_vcf_sample_name_and_bam_to_file(self,
        gtonly_path, sample_name_path, sample_bam_path):

        ''' vcf_sample_name_ext =   '_sample_name.txt'
            vcf_sample_bam_ext =    '_sample_bam_table.txt'
        '''

        name_header = "#{}\t{}\t{}\t{}\t{}".format(
                    'no', 'group', 'nickname', 'basename', 'fullname')
        bam_header = "#{}\t{}".format('vcf_sample', 'bam_or_bed')

        # pick information from vcf
        sample_name_list, sample_bam_list = \
            self.pick_vcf_sample_list(gtonly_path)
        
        # pprint.pprint(sample_name_list)
        # ['1\t-\tHitomebore\tHitomebore\tHitomebore',
        #  '2\t-\tGinganoshizuku\tGinganoshizuku\tGinganoshizuku',

        # pprint.pprint(sample_bam_list)
        # ['Hitomebore\t-',
        #  'Ginganoshizuku\t-',

        for sample_path in [sample_name_path, sample_bam_path]:

            # vcf_txt: if exist
            if sample_path.exists():
                log.info("found. {}".format(sample_path))
                # this text file is editable for default groups
                # copy existed file as backup.
                # args are (fname, can_log, copy_mode)

                if glv.need_update == utl.is_need_update(
                    sample_path, self.bak_timestamp_path):
                    # backup if updated
                    utl.save_to_tmpfile(sample_path, True, True)

            else:

                # do not exist
                sample_list = list()

                if sample_path == sample_name_path:
                    sample_list = [name_header]
                    sample_list += sample_name_list
                else:
                    sample_list = [bam_header]
                    sample_list += sample_bam_list

                # if not, read vcf and pick sample_name
                log.info("not found {}.".format(sample_path))

                # backup
                utl.save_to_tmpfile(sample_path)

                # write to vcf_sample_name_file
                with sample_path.open('w', encoding='utf-8') as f:
                    f.write("{}\n".format("\n".join(sample_list)))

                log.info("saved. {}".format(sample_path))

            if sample_path == sample_name_path:
                # sample_name_path
                mes = "vcf samples are here."
            else:
                # sample_bam_path
                mes = "the correspondence between vcf sample and "
                mes += "bam/bed file is here."

            # pathlib read_txt, print
            s = sample_path.read_text()
            log.info("{}\n{}\n\n{}".format(mes, sample_path, s))


    def pick_vcf_sample_list(self, gtonly_path):
        ''' open vcf file and pick sample information as list
        '''

        sample_name_list = list()
        sample_bam_list = list()
        reader = vcfpy.Reader.from_path(gtonly_path)

        # it is important to convert name to idx
        start_idx = 0

        for (sample_no, vcf_sample_name) in enumerate(
            reader.header.samples.names, start_idx):

            #sample_basename_bam = os.path.basename(vcf_sample_name)

            sample_basename_bam = str(Path(vcf_sample_name).name)
            sample_basename = re.sub(r"\.bam$", "", sample_basename_bam)
            # The group name is taken as the default group when not specified
            # in parameters and ini files. This file is editable.

            group_name = "-"

            sample_name_list.append("{}\t{}\t{}\t{}\t{}".format(
                sample_no,
                group_name,
                sample_basename,
                sample_basename_bam,
                vcf_sample_name))

            # for bam list
            sample_bam_list.append("{}\t-".format(
                sample_basename))

        return sample_name_list, sample_bam_list


    def make_vcf_sample_variable(self, sample_path):
        '''
        print vcf_samples to STDOUT
        '''

        # a simple list. Used for existence confirmation, etc.
        vcf_sample_nickname_list = list()
        vcf_sample_basename_list = list()
        vcf_sample_fullname_list = list()

        # _is_sample_name(sample)
        # _get_nickname(sample)
        # _get_basename(sample)
        # _get_fullname(sample)

        # The key is nickname, which gives you the basename and fullname.
        vcf_sample_nickname_dict = dict()
        # The key is basename, which gives you the nickname and fullname.
        vcf_sample_basename_dict = dict()
        # The key is fullname, which gives you the nickname and basename.
        vcf_sample_fullname_dict = dict()

        group_members_vcf_str = ""

        group_dict = dict()
        # print list
        #print_list = list()

        with sample_path.open('r', encoding='utf-8') as f:
            # 'no', 'group', 'nickname', 'basename', 'fullname')]
            for liner in f:
                r_line = liner.strip()

                # for print to STDOUT
                if r_line == '':
                    continue

                # print except ''
                #print_list.append(r_line)
                #print("{}".format(r_line), file=sys.stdout)

                # comment line
                if r_line.startswith('#'):
                    continue

                # group may be separated by comma
                no, groups, nickname, basename, fullname = \
                    r_line.split('\t')

                # group_dict, group_members_vcf_str
                sep_groups = groups.split(',')
                for sep_group in sep_groups:
                    if not sep_group in group_dict:
                        group_dict[sep_group] = list()
                    group_dict[sep_group].append(nickname)

                sample_dict = dict()
                sample_dict = {
                    'no': int(no),
                    'nickname': nickname,
                    'basename': basename,
                    'fullname':fullname
                }

                # if nickname duplicated, it's ok if contents is same
                if nickname in vcf_sample_nickname_dict:
                    if basename == \
                        vcf_sample_nickname_dict[nickname]['basename'] and \
                        fullname == \
                        vcf_sample_nickname_dict[nickname]['fullname']:
                        # It's ok
                        pass
                    else:
                        log.info("{} >{}< {}".format(
                            "same nickname", nickname,
                            "have different contents. exit."))
                        sys.exit(1)

                vcf_sample_nickname_list.append(nickname)
                vcf_sample_basename_list.append(basename)
                vcf_sample_fullname_list.append(fullname)

                vcf_sample_nickname_dict[nickname] = sample_dict
                vcf_sample_basename_dict[basename] = sample_dict
                vcf_sample_fullname_dict[fullname] = sample_dict

        # print to stdout
        #log.info("\n{}\n{}\n".format(
        #    sample_path, "\n".join(print_list)))

        for group in sorted(group_dict):
            group_members_vcf_str += "{}:{},".format(
                group, ",".join(group_dict[group]))

        group_members_vcf_str = re.sub(r",$", "", group_members_vcf_str)

        return vcf_sample_nickname_list, \
            vcf_sample_basename_list, \
            vcf_sample_fullname_list, \
            vcf_sample_nickname_dict, \
            vcf_sample_basename_dict, \
            vcf_sample_fullname_dict, \
            group_members_vcf_str


