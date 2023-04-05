# -*- coding: utf-8 -*-

import sys
#import os
import re
import glob
import copy
import pprint

from pathlib import Path

#
import pandas as pd
import time
import datetime

import logging
import logging.config

# global configuration
import vprimer.glv as glv

import subprocess as sbp
from subprocess import PIPE

#=========================================================
def open_log():
    '''
    '''
    logging.config.dictConfig(glv.conf.log.config)
    global log
    log = logging.getLogger(__name__)
    log.info("logging start {}".format(__name__))


#def elapsed_time(now_time, start_time):
#
#    elapsed_time = now_time - start_time
#    #3:46:11.931354
#    return "elapsed_time {}".format(
#        datetime.timedelta(seconds=elapsed_time))
#
#def iso_datetime():

#    start = time.time()
#    # 2021-02-09 10:56:57.209040
#    now_datetime = str(datetime.datetime.now())
#    now_datetime = now_datetime.split('.')[0].replace(
#        ' ', 'T').replace('-', '').replace(':', '')
#
#    return start, now_datetime

def get_start_time():
    '''
    get start time
    '''
    return time.time()


def elapse(start_time):
    '''
    get elapsed time from start_time to now
    '''

    elapsed_time = time.time() - start_time
    elapsed_time_str = datetime.timedelta(seconds=elapsed_time)
    elapsed_time_str = str(elapsed_time_str).split('.')[0]
    return elapsed_time_str

def elapse_epoch():
    '''
    elapsed time from glv.now_epochtime
    '''

    return elapse_str(glv.now_epochtime)


def elapse_str(start_time):
    '''
    with 'elapsed_time'
    '''
    return "elapsed_time {}".format(elapse(start_time))


def get_path_mtime(file_path):
    '''
    '''

    # 1674173966.0
    st_mtime = file_path.stat().st_mtime
    #2023-01-20 09:19:26
    dtdt = datetime.datetime.fromtimestamp(st_mtime)
    return conv_datetime("{}.0".format(dtdt))


def get_path_size(file_path):
    '''
    '''

    # byte
    return file_path.stat().st_size



#def start_mes(mes=""):
#    '''
#    '''
#
#    now_datetime, stt = str_nowtime(0)
#    if mes == '' :
#        ret_mes = ""
#    else:
#        ret_mes = "{} {}".format(mes, now_datetime)
#
#    return stt, ret_mes
#
#
#def end_mes(start_time, mes=""):
#    '''
#    '''
#
#    now_datetime, stt, elaps = str_nowtime(start_time)
#    ret_mes = ''
#
#    if mes == '':
#        ret_mes = "elapsed time {}".format(elaps)
#    else:
#        ret_mes = "{}, elapsed time {}".format(mes, now_datetime, elaps)
#
#    return ret_mes


def datetime_str():
    '''
    2023_0131_1354_45
    '''
    return conv_datetime(datetime.datetime.now())


def conv_datetime(datetime):

    # 2023_0131_1354_45
    start_time_str = re.sub(
        r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\..*$',
        r'\1_\2\3_\4\5_\6',
        str(datetime))

    return start_time_str


#def str_nowtime(start_time):
#    '''
#    if start is zero, return 2 value.
#        now_datetime_str, now_time_str
#    else
#        return 3 value
#        now_datetime_str, now_time_str, elapsed_time_str
#    '''
#
#    start_time = float(start_time)
#    # 1674188456.3177614
#    now_time = time.time()
#    now_time_str = str(now_time).split('.')[0]
#
#    # 2023-01-20 12:56:50.894700
#    now_datetime_str = re.sub(
#        r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\..*$',
#        r'\1_\2\3_\4\5_\6',
#        str(datetime.datetime.now()))
#        #r'\1_\2\3_\4\5_\6',
#    # 2023_0120_1256_50
#
#    if start_time == 0:
#        return now_datetime_str, now_time_str
#    else:
#        elapsed_time = now_time - start_time
#        elapsed_time_str = datetime.timedelta(seconds=elapsed_time)
#        elapsed_time_str = str(elapsed_time_str).split('.')[0]
#        return now_datetime_str, now_time_str, elapsed_time_str


def strip_hash_comment(line):
    '''
    '''
    return line.split('#')[0].strip()


# user_ini_path = Path(user_ini_file).resolve()
# def full_path(file_name_str):
#     '''
#     file_name is string:
#         return full_path is pathlib object
#     '''

#     # if path.resolve() == None
#     full_path_pathlib = glv.NonePath

#     if file_name_str is None:
#         pass

#     elif file_name_str == '':
#         pass

#     else:
#         # if file_name == "", relative_to is '.'
#         relative_to = Path(file_name_str)
#         full_path_pathlib = relative_to.resolve()

#     return full_path_pathlib


def full_path_os(file_name):
    '''
    after checking either file_name is absolute one or relative one,
    make an appropriate absolute path
    '''

    full_path = ''

    if file_name == '' or file_name is None:
        pass

    else:
        if file_name.startswith('/'):
            full_path = file_name
        elif file_name == '':
            pass
        else:
            full_path = "{}/{}".format(glv.cwd, file_name)

    return full_path


def prelog(line, name):
    '''
    '''
    print("prelog: {} {}".format(name, line), file=sys.stderr)


def try_exec(cmd, can_log=True):
    '''
    '''
    try:
        if can_log == True:
            log.info("do {}".format(cmd))
        else:
            #print("do {}".format(cmd), file=sys.stderr)
            prelog("do {}".format(cmd), __name__)

        sbp.run(cmd,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            shell=True,
            check=True)

    except sbp.CalledProcessError as e:
        if can_log == True:
            log.error("{}.".format(e.stderr))
        else:
            prelog("{}.".format(e.stderr), cmd)

        sys.exit(1)


def try_exec_error(cmd):
    '''
    '''
    # https://qiita.com/HidKamiya/items/e192a55371a2961ca8a4

    err_str = ''

    try:
        log.info("do {}".format(cmd))

        sbp.run(cmd,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            shell=True,
            check=True)

    except sbp.CalledProcessError as e:
        err_str = e.stderr

    return err_str


def save_to_tmpfile(file_path_pathlib, can_log=True, copy_mod=False):
    '''
    '''

    ret = False

    #print(type(file_path_pathlib))
    #sys.exit(1)

    if not file_path_pathlib.exists():
    #if not file_path_pathlib.is_file():
    #if not Path.is_file(file_path_pathlib):
        #if can_log:
        #    log.info("not found {}, so didn't backup it.".format(
        #    file_path_pathlib))
        pass

    else:
        # /a/b/c.txt
        # /a/b/bak/c.txt
        dirname_file = file_path_pathlib.parent
        basename_file = file_path_pathlib.name

        file_bak_path = glv.conf.out_bak_dir_path / basename_file


        ret = True

        new_file_path = glv.conf.out_bak_dir_path / "{}.{}".format(
            glv.now_datetime_str, basename_file)

        #print(file_path_pathlib)
        #print(file_bak_path)
        #print(new_file_path)
        #sys.exit(1)

        mode = "mv"
        if copy_mod == True:
            mode = "cp"
            cp_f(file_path_pathlib, new_file_path, can_log)

        else:
            mv_f(file_path_pathlib, new_file_path, can_log)
        
        if can_log:
            log.info("done {}. {} to {}".format(
                file_path_pathlib, mode, new_file_path))

    return ret


def ln_s(source_file_pathlib, symbolic_link_file_pathlib, can_log=True):
    ''' source_file_pathlib.symlink_to(symbolic_link_file_pathlib)
    '''

    cmd1 = "{} {} {}".format(
        'ln -s', source_file_pathlib, symbolic_link_file_pathlib)
    try_exec(cmd1, can_log)


def rm_f(remove_file_pathlib):
    '''
    '''
    cmd1 = "{} {}".format(
        'rm -f', remove_file_pathlib)
    try_exec(cmd1)


def makedirs(dir_name_pathlib):
    ''' dir_name is pathlib object
    '''

    cmd1 = "{} {}".format(
        'mkdir -p', dir_name_pathlib)
    try_exec(cmd1, False)


def mv_f(source_file_pathlib, renamed_file_pathlib, can_log=False):
    '''
    '''
    cmd1 = "{} {} {}".format(
        'mv', source_file_pathlib, renamed_file_pathlib)
    try_exec(cmd1, can_log)


def cp_f(source_file_pathlib, copyed_file_pathlib, can_log=False):
    '''
    '''
    cmd1 = "{} {} {}".format(
        'cp', source_file_pathlib, copyed_file_pathlib)
    try_exec(cmd1, can_log)


def tabix(vcf_gt_pathlib):
    '''
    '''
    #-f -p vcf
    cmd1 = "{} {} {}".format(
        'tabix',
        '-f -p vcf',
        vcf_gt_pathlib)

    try_exec(cmd1)


def refs_file_slink_backup_and_copy(src_pathlib, slink_pathlib, cp_mode=True):

    if glv.noneed_update == is_need_update(src_pathlib, slink_pathlib):

        log.info("do not need update between {} and {}.".format(
            src_pathlib, slink_pathlib))
        return

    log.info("need update between {} and {}.".format(
        src_pathlib, slink_pathlib))

    # もし渡されたファイルが、refs 以下ならば、シンボリックリンクを張らない
    # のがいいんじゃないか

    # 1) backup slink file
    save_to_tmpfile(slink_pathlib, can_log=True)

    # 2) slink src to slink
    ln_s(src_pathlib, slink_pathlib)

    # don't copy to refdir
    #if cp_mode:
    #    # 3) copy src to cp_path
    #    cp_pathlib = glv.conf.refs_dir_path / "{}{}".format(
    #        glv.cp_prefix, src_pathlib.name)
    #    # backup cp file
    #    save_to_tmpfile(cp_pathlib, can_log=True)
    #    cp_f(src_pathlib, cp_pathlib, True)


def refs_make_original_file_and_copy(
    header_txt, line_list, sys_pathlib, sys_pathlib_org):

    # 1) オリジナルを作る。
    with sys_pathlib_org.open('w', encoding='utf-8') as f:
        if header_txt != "":
            f.write("{}\n".format(header_txt))
    
        for line in line_list:
            f.write(line + "\n")
        f.write("\n")

    log.info("cp {} to {}.".format(sys_pathlib_org, sys_pathlib))
    # 1) システムをバックアップして、
    save_to_tmpfile(sys_pathlib, can_log=True)
    # 2) オリジナルをコピーする
    cp_f(sys_pathlib_org, sys_pathlib, True)



#=========================================================
def write_df_to_csv(dataframe, out_file, index=True, force=True):
    '''
    '''
    file_name = out_file
    moved = False
    if force == True:
        moved = save_to_tmpfile(out_file)

    dataframe.to_csv(out_file, sep='\t', index=index)


#def progress_check(now_progress):
#    '''
#    '''
#    stat = False    # False if don't do this progress
#    param_progress = glv.conf.progress

#    log.info("now_progress={} param_progress={}".format(
#        now_progress, param_progress))

    #log.debug("now_progress={} {} param_progress={} {}".format(
    #    now_progress,
    #    now_progress_no,
    #    param_progress,
    #    param_progress_no))

#    if param_progress == 'all':
#        stat = True

#    else:
#        now_progress_no = glv.outlist.outf_prefix[now_progress]['no']
#        param_progress_no = glv.outlist.outf_prefix[param_progress]['no']
#        if now_progress_no >= param_progress_no:
#            stat = True

#    return stat

def pr_dg(proc_name, distin_gdct, reg, proc_cnt, simple=False):

    reg_dict = glv.conf.regions_dict[reg]

    # ここは全処理数が必要だ
    log.info("")
    log.info("proc:         {}, {} / {}".format(proc_name, proc_cnt,
        glv.conf.all_proc_cnt))

    if simple == True:
        log.info("distin_str    {}\n".format(distin_gdct['distin_str']))
        return
    else:
        log.info("distin_str    {}".format(distin_gdct['distin_str']))

    log.info("now_region    {}".format(reg))
    log.info("all_regions   {}".format(distin_gdct['regions']))
    log.info("groups        {} / {}".format(
        distin_gdct[0], distin_gdct[1]))
    log.info("region_str    {}".format(reg_dict['reg']))
    log.info("pick_mode     {}".format(distin_gdct['pick_mode']))
    log.info("indel_size    {}".format(distin_gdct['indel_size']))
    log.info("product_size  {}".format(distin_gdct['product_size']))
    log.info("sort_samples  {}".format(distin_gdct['sorted_samples']))

    # auto_group
    log.info("members       {} : {}".format(
        distin_gdct[0],
        ', '.join(
            glv.conf.group_members_dict[distin_gdct[0]]['sn_lst']))
        )

    if not glv.conf.is_auto_group:
        log.info("members       {} : {}".format(
            distin_gdct[1],
            ', '.join(
                glv.conf.group_members_dict[distin_gdct[1]]['sn_lst']))
            )

    log.info("bed_thal_path {}\n".format(distin_gdct['bed_thal_path']))


def decide_action_stop(now_progress):
    '''
    '''

    # Current location number
    now_progress_no = glv.outlist.outf_prefix[now_progress]['no']

#    print("now_progress={}, now_progress_no={}".format(
#        now_progress, now_progress_no))

    # User-specified start point and number
    progress_name = glv.conf.progress
    progress_no = 100

    # User-specified stop point and number
    stop_name = glv.conf.stop
    stop_no = 100

    # If progress_name is "all", progress_no is 0
    if progress_name != "all":
        progress_no = glv.outlist.outf_prefix[progress_name]['no']

    # If stop_name is "no", stop_no is 100
    if stop_name != "no":
        stop_no = glv.outlist.outf_prefix[stop_name]['no']

    ret_status = "stop"

#    print("progress_name={}, progress_no={}".format(
#        progress_name, progress_no))
#    print("stop_name={}, stop_no={}".format(
#        stop_name, stop_no))

    # decide
    if progress_no == 100:
        ret_status = "action"
    elif now_progress_no < progress_no:
        ret_status = "gothrough"
    else:
        ret_status = "action"

    if stop_no < now_progress_no:
        ret_status = "stop"

#    print("ret_status={}".format(ret_status))

    return ret_status


#def stop(now_progress):
#    '''
#    '''
#    if glv.conf.stop == 'no':
#        return

#    now_progress_no = glv.outlist.outf_prefix[now_progress]['no']
#    param_stop_no = glv.outlist.outf_prefix[glv.conf.stop]['no']
#    if now_progress_no >= param_stop_no:
#        log.info("stop {}".format(glv.conf.stop))
#        sys.exit(1)


def check_for_files(filepath):
    '''
    '''
    # filepath is pattern
    fobj_list = list()

    ga
    '''
    for filepath_object in glob.glob(filepath):

        if os.path.isfile(filepath_object):
            fobj_list.append(filepath_object)

    return sorted(fobj_list)
    '''


def is_same_gt(s0_a0, s0_a1, s1_a0, s1_a1):
    ''' not use
    '''
    same_gt = False

    # same homo: AA,AA
    if is_same_homo(s0_a0, s0_a1, s1_a0, s1_a1):
        same_gt = True

    # same hetero: AB,AB
    elif is_same_hetero(s0_a0, s0_a1, s1_a0, s1_a1):
        same_gt = True

    return same_gt


def is_DOT(s0_a0, s0_a1, s1_a0, s1_a1):
    ''' element is all integer type, DOT is -1
    '''
    return s0_a0 == -1 or s0_a1 == -1 or \
           s1_a0 == -1 or s1_a1 == -1 


def is_homo_homo(s0_a0, s0_a1, s1_a0, s1_a1):
    '''
    '''
           #   1 == 2             3 == 4
    return s0_a0 == s0_a1 and s1_a0 == s1_a1


def is_homo_hetero(s0_a0, s0_a1, s1_a0, s1_a1):
    '''
    '''
           #   1 == 2             3 != 4
    return s0_a0 == s0_a1 and s1_a0 != s1_a1 or \
           s0_a0 != s0_a1 and s1_a0 == s1_a1
           #   1 != 2             3 == 4


def is_hetero_hetero(s0_a0, s0_a1, s1_a0, s1_a1):
    ''' o: 01 02
    '''
           #   1 != 2             3 != 4
    return s0_a0 != s0_a1 and s1_a0 != s1_a1


def is_same_homo(s0_a0, s0_a1, s1_a0, s1_a1):
    '''
    '''
    return is_homo_homo(s0_a0, s0_a1, s1_a0, s1_a1) and \
           s0_a0 == s1_a0
           #  o: 00 00 x: 00 11


def is_same_hetero(s0_a0, s0_a1, s1_a0, s1_a1):
    '''
    '''
    return is_hetero_hetero(s0_a0, s0_a1, s1_a0, s1_a1) and \
           s0_a0 == s1_a0 and s0_a1 == s1_a1
           #   1 == 3             2 == 4

def is_share(s0_a0, s0_a1, s1_a0, s1_a1):
    '''
    '''
           #   1 == 3            1 == 4
    return s0_a0 == s1_a0 or s0_a0 == s1_a1 or \
           s0_a1 == s1_a0 or s0_a1 == s1_a1
           #   2 == 3            2 == 4


def is_Not_NoneAndNull(value):
    '''
    '''

    ret = False

    is_none = False
    is_null = False

    if value is None:
        is_none = True

    if value == "":
        is_null = True

    if is_none != True and is_null != True:
        ret = True

    return ret


def sort_file(
        proc, distin_gdct, out_txt_path,
        nm_chrom, nm_pos, nm_order, n):
    '''
    '''

    # sort command option
    if n == 'number':
        n = 'n'
    else:
        n = ''


    # cmd.sort
    hdr_dict = distin_gdct[proc]['hdr_dict']
    sorted_file = "{}.sorted".format(out_txt_path)

    col_chrom = hdr_dict[nm_chrom]
    col_pos = hdr_dict[nm_pos]
    col_order = hdr_dict[nm_order]

    cmd_sort = "{} -k {},{} -k {},{}n -k {},{}{} {} > {}".format(
        'sort',
        col_chrom, col_chrom,
        col_pos, col_pos,
        col_order, col_order,
        n,
        out_txt_path,
        sorted_file)

    try_exec(cmd_sort)

    # rm file
    rm_f(out_txt_path)

    # make header.txt
    out_txt_header = "{}.header_txt".format(out_txt_path)
    out_txt_header_path = Path(out_txt_header).resolve()

        # header
    header_txt = distin_gdct[proc]['hdr_text']
    # if glv.conf.is_auto_group, remove last 2 columns
    #header_txt = remove_auto_grp_header_txt(header_txt)

    with out_txt_header_path.open('w', encoding='utf-8') as f:
        f.write("{}\n".format(header_txt))


    # cat header file
    cmd_cat = "{} {} {} > {}".format(
        'cat',
        out_txt_header,
        sorted_file,
        out_txt_path)

    try_exec(cmd_cat)

    # rm header sorted
    rm_f(out_txt_header)
    rm_f(sorted_file)


def get_specified_sample_list(group_list, add_remain=False):
    ''' The sample names are listed in the order of the groups
    specified by group_list, and it is decided whether to add
    the sample names of the groups not specified.
    '''

    sample_nickname_ordered_list = list()
    sample_basename_ordered_list = list()
    sample_fullname_ordered_list = list()

    # Deep copy is required here
    # sample_nickname_ordered_list
    sample_nickname_ordered_list = \
        get_sample_list_from_group_list(group_list, "nickname")
    sample_basename_ordered_list = \
        get_sample_list_from_group_list(group_list, "basename")
    sample_fullname_ordered_list = \
        get_sample_list_from_group_list(group_list, "fullname")


    #print(sample_fullname_ordered_list)
    #sys.exit(1)

    if add_remain:

        auto_grp_nickname_list = list()
        auto_grp_basename_list = list()
        auto_grp_fullname_list = list()

        # Add members other than the nickname specified in the group
        # to the end of ordered_list
        for nickname in glv.conf.vcf_sample_nickname_list:
            basename = get_basename(nickname)
            fullname = get_fullname(nickname)

            if nickname not in sample_nickname_ordered_list:
                auto_grp_nickname_list += [nickname]
                auto_grp_basename_list += [basename]
                auto_grp_fullname_list += [fullname]

        sample_nickname_ordered_list += auto_grp_nickname_list
        sample_basename_ordered_list += auto_grp_basename_list
        sample_fullname_ordered_list += auto_grp_fullname_list

    return \
        sample_nickname_ordered_list, \
        sample_basename_ordered_list, \
        sample_fullname_ordered_list


def get_sample_list_from_group_list(group_list, need_name):
    '''
    '''

    all_sample_list = list()

    for group_name in group_list:

        if group_name == "ref":

            all_sample_list.append("ref")

        else:

            sample_list = glv.conf.group_members_dict[group_name]['sn_lst']
            #print(glv.conf.group_members_dict[group_name])
            #print(sample_list)
            #sys.exit(1)

            for sn in sample_list:

                if need_name == "nickname":
                    sample_name = get_nickname(sn)
                elif need_name == "basename":
                    sample_name = get_basename(sn)
                elif need_name == "fullname":
                    sample_name = get_fullname(sn)
                else:
                    sample_name = get_nickname(sn)

                all_sample_list.append(sample_name)

    return all_sample_list


#-----------------------------------------------------
def is_sample_name(sample_name):
    '''
    '''
    ret = False

    if sample_name.lower() == "ref":
        ret = True

    elif sample_name in glv.conf.vcf_sample_nickname_list:
        ret = True

    elif sample_name in glv.conf.vcf_sample_basename_list:
        ret = True

    elif sample_name in glv.conf.vcf_sample_fullname_list:
        ret = True

    return ret


def get_nickname(sample_name):
    '''
    '''
    nickname = ""

    #print("get_nickname={}".format(sample_name))
    #print(glv.conf.vcf_sample_fullname_dict)

    if sample_name.lower() == "ref":
        nickname = "ref"

    elif sample_name in glv.conf.vcf_sample_nickname_list:
        nickname = sample_name

    elif sample_name in glv.conf.vcf_sample_basename_list:
        nickname = glv.conf.vcf_sample_basename_dict[sample_name]['nickname']

    elif sample_name in glv.conf.vcf_sample_fullname_list:
        nickname = glv.conf.vcf_sample_fullname_dict[sample_name]['nickname']

    return nickname


def get_basename(sample_name):
    '''
    '''
    basename = ""

    if sample_name.lower() == "ref":
        basename = "ref"

    elif sample_name in glv.conf.vcf_sample_nickname_list:
        basename = glv.conf.vcf_sample_nickname_dict[sample_name]['basename']

    elif sample_name in glv.conf.vcf_sample_basename_list:
        basename = sample_name

    elif sample_name in glv.conf.vcf_sample_fullname_list:
        basename = glv.conf.vcf_sample_fullname_dict[sample_name]['basename']

    return basename


def get_fullname(sample_name):
    '''
    '''
    fullname = ""

    if sample_name.lower() == "ref":
        fullname = "ref"

    elif sample_name in glv.conf.vcf_sample_nickname_list:
        fullname = glv.conf.vcf_sample_nickname_dict[sample_name]['fullname']

    elif sample_name in glv.conf.vcf_sample_basename_list:
        fullname = glv.conf.vcf_sample_basename_dict[sample_name]['fullname']

    elif sample_name in glv.conf.vcf_sample_fullname_list:
        fullname = sample_name

    return fullname


# eval_variant.py:      utl.get_basic_primer_info(variant_df_row, hdr_dict)
# formtxt.py:           utl.get_basic_primer_info(primer_df_row, hdr_dict)
# primer.py:            utl.get_basic_primer_info(marker_df_row, hdr_dict)

# primer.py             prinfo.prepare_from_marker_file
# primer.py             def prepare_from_marker_file

def get_basic_primer_info(df_row, hdr_dict):


    # get_basic_primer_info
    #print("in get_basic_primer_info")
    #print()
    #print(df_row)
    #print()
    #print(hdr_dict)
    #sys.exit(1)

    marker_id = ""
    if 'marker_id' in hdr_dict.keys():
        marker_id = str(df_row[hdr_dict['marker_id']])
    #print("marker_id={}".format(marker_id))

    chrom = str(df_row[hdr_dict['chrom']])
    #print("chrom={}".format(chrom))
    pos = int(df_row[hdr_dict['pos']])
    #print("pos={}".format(pos))

    targ_grp = str(df_row[hdr_dict['targ_grp']])
    #print("targ_grp={}".format(targ_grp))
    g0_name, g1_name = targ_grp.split(',')
    #print("g0_name={}".format(g0_name))
    #print("g1_name={}".format(g1_name))

    targ_ano = str(df_row[hdr_dict['targ_ano']])
    #print("targ_ano={}".format(targ_ano))
    g0_ano, g1_ano = map(int, targ_ano.split(','))

    #print("g0_ano={}".format(g0_ano))
    #print("g1_ano={}".format(g1_ano))

    vseq_gno_str = df_row[hdr_dict['vseq_gno_str']]
    #print("vseq_gno_str={}".format(vseq_gno_str))

    gts_segr_lens = df_row[hdr_dict['gts_segr_lens']]
    #print("gts_segr_lens={}".format(gts_segr_lens))
    var_type = str(df_row[hdr_dict['var_type']])
    #print("var_type={}".format(var_type))

    # 2022-10-27 add
    mk_type = str(df_row[hdr_dict['mk_type']])

    set_enz_cnt = ""
    if 'set_enz_cnt' in hdr_dict:
        set_enz_cnt = str(df_row[hdr_dict['set_enz_cnt']])
    else:
        set_enz_cnt = str(df_row[hdr_dict['set_n']])
    #print("set_enz_cnt={}".format(set_enz_cnt))

    marker_info = ''
    enzyme_name = '-'
    digest_pattern = '-'
    target_gno = -1
    target_len = 0

    if 'marker_info' in hdr_dict:

        marker_info = str(df_row[hdr_dict['marker_info']])

        # indel and snp behave the same as indel
        if mk_type == glv.MK_INDEL or \
            mk_type == glv.MK_SNP:

            longer_group, \
            longer_length, \
            shorter_length, \
            diff_length, \
            digested_pos = \
                map(int, marker_info.split('.'))

            target_gno = longer_group
            target_len = longer_length

        else:
            enzyme_name, \
            digested_gno, \
            found_pos, \
            digest_pattern, \
            digested_pos = \
                marker_info.split('.')

            target_gno = int(digested_gno)
            target_len = int(found_pos)

    vseq_lens_ano_str = ""
    if 'vseq_lens_ano_str' in hdr_dict:
        vseq_lens_ano_str = str(df_row[hdr_dict['vseq_lens_ano_str']])

    # when glv.conf.is_auto_group, get group string separated by ,.
    #auto_grp0 = "-"
    #auto_grp1 = "-"
    #if glv.conf.is_auto_group:

    auto_grp0 = str(df_row[hdr_dict['auto_grp0']])
    auto_grp1 = str(df_row[hdr_dict['auto_grp1']])

    return \
        marker_id, \
        chrom, \
        pos, \
        targ_grp, \
        g0_name, \
        g1_name, \
        targ_ano, \
        g0_ano, \
        g1_ano, \
        vseq_gno_str, \
        gts_segr_lens, \
        var_type, \
        mk_type, \
        set_enz_cnt, \
        marker_info, \
        vseq_lens_ano_str, \
        enzyme_name, \
        digest_pattern, \
        target_gno, \
        target_len, \
        auto_grp0, \
        auto_grp1

def flip_gno(gno):

    flip_gno = 0
    if gno == 0:
        flip_gno = 1

    return flip_gno


def gc(seq):
    ''' calc gc content %
    2022.01.25 cap and little
    '''
    gc = seq.count('G') + seq.count('C') + seq.count('g') + seq.count('c')
    #print("{}".format(gc))
    #print("{}".format(len(ref)))
    GC = gc / len(seq) *100
    GC_f = f'{GC:.01f}'

#    print("seq={}, seq.count('G')={}, seq.count('C')={}, gc={}, len(seq)*100={}, GC={}, GC_f={}".format(
#        seq, seq.count('G'), seq.count('C'),
#        gc, len(seq) * 100, GC, GC_f))

    #print(GC)
    return GC_f

def exec_thin_to_bed(bam, depth_txt, thin_depth, thick_depth):

    print("in utl.exec_thin_to_bed")
    print("bam={}".format(bam))
    print("depth_txt={}".format(depth_txt))
    print("thin_depth={}".format(thin_depth))
    print("thick_depth={}".format(thick_depth))
    print("thread={}".format(glv.conf.thread))

    # https://dev.classmethod.jp/articles/python-subprocess-shell-command/
    # samtools depth -@ cpu bam > depth_txt
    cpu = glv.conf.thread - 1
    cmd1 = "{} {} {} {} {} {} {}".format(
        'samtools',
        'depth',
        '-@',
        cpu,
        bam,
        '>', 
        depth_txt)

    try_exec(cmd1, True)
    sys.exit(1)


def is_need_update(src_pathlib, dist_pathlib):

    er_m = ""
    do_update = glv.noneed_update

    try:

        # 1) if src(file) not exist, it's error, stop.
        if not src_pathlib.exists() or not src_pathlib.is_file():
            er_m = "not found {}.".format(src_pathlib)
            raise UserFormatErrorUtl(er_m)

        # 2) if dist(ex. symlink) not exist, need_update
        if not dist_pathlib.exists():
            do_update = glv.need_update

        else:

            # if dist(ex. symlink) exist,
            # 3) if dist is symlink,
            if dist_pathlib.is_symlink():
                # It's error if the src and dist are not identical.
                if not dist_pathlib.samefile(src_pathlib):
                    er_m = "{} and {} are different files.".format(
                        src_pathlib, dist_pathlib)
                    raise UserFormatErrorUtl(er_m)

            # confirm src time is old than dist time
            st_mtime_src_pathlib = src_pathlib.stat().st_mtime
            st_mtime_dist_pathlib = dist_pathlib.stat().st_mtime

            if st_mtime_src_pathlib > st_mtime_dist_pathlib:
                do_update = glv.need_update

    except UserFormatErrorUtl as ex:
        log.error("Error: {}".format(ex))
        sys.exit(1)

    else:
        log.info("{} update {}, {}.".format(
            do_update, src_pathlib, dist_pathlib))
        return do_update


#def remove_auto_grp_header_txt(header_txt):
#    ''' auto_grp0, auto_grp1
#        When grouped, remove the last two headers auto_grp0 and auto_grp1
#    '''
#
#    # grouped
#    if not glv.conf.is_auto_group:
#
#        # Remove the last two items: auto_grp0 auto_grp1 for sample list
#        header_list = header_txt.split('\t')
#        del header_list[-2:]
#        header_txt = '\t'.join(header_list)
#
#    return header_txt


#def remove_deepcopy_auto_grp_header_dict(header_dict):
#def deepcopy_grp_header_dict(header_dict):

#    hdr_dict = copy.deepcopy(header_dict)

    # grouped
    #if not glv.conf.is_auto_group:
    #    rm_dict = hdr_dict.pop('auto_grp0')
    #    rm_dict = hdr_dict.pop('auto_grp1')

#    return hdr_dict


class UserFormatErrorUtl(Exception):
    """Detect user-defined format errors"""
    pass
