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

class ConfP3Params(object):

    def open_log_p3_params(self):

        global log
        log = LogConf.open_log(__name__)


    def prepare_p3(self, set_type, p3_key, user_path, sys_path):
        '''
        '''

        log.info("prepare_p3 start.")

        # make .original name
        sys_path_org = Path("{}{}".format(
            sys_path, glv.original_file_ext))

        p3_header_dict = dict()

        # もしオリジナルファイルがない場合、
        if not sys_path_org.exists():
            log.info("not found {}.".format(sys_path_org))
            # オリジナルファイルを作る。
            header_txt = "#"
            header_txt += "PARAM\t" + "VALUE\n"

            # オリジナルのファイル内容を作成
            line_list = list()
            for key, value in list(p3_key.items()):
                line_list.append("{}={}".format(key, value))
            # オリジナルを作り、バックアップしてコピー
            utl.refs_make_original_file_and_copy(
                header_txt, line_list, sys_path, sys_path_org)

        else:
            # compare timestamp for backup copy
            if utl.is_need_update(sys_path, "timestamp"):
                # copy if updated
                utl.save_to_tmpfile(sys_path, copy_mod=True)

        # 読み込むファイルは、システムファイルかユーザファイル
        read_file_path = sys_path

        # ユーザ指定がある場合 There is a file specification from user.
        # リードファイル変更
        #print( user_path)
        #print(user_path.resolve())
        #print(read_file_path)
        #sys.exit(1)

        if not None == user_path.resolve():
            # symlink name for user_path
            slink_path = self.refs_dir_path / "{}{}".format(
                glv.slink_prefix, user_path.name)

            utl.refs_file_slink_backup_and_copy(user_path, slink_path)
            read_file_path = user_path

        # read p3 params
        with read_file_path.open('r',  encoding='utf-8') as f:
            # iterator
            for r_liner in f:
                r_line = r_liner.strip()    # cr, ws

                if r_line.startswith('#') or r_line == '':
                    continue

                r_line = utl.strip_hash_comment(r_line)

                vname, value = r_line.split('=')
                if vname == 'PRIMER_PRODUCT_SIZE_RANGE' or \
                    vname == 'PRIMER_NUM_RETURN':
                    continue

                p3_header_dict[vname] = value

        # constant value for primer3
        # PRIMER_FIRST_BASE_INDEX=1
        p3_header_dict['PRIMER_FIRST_BASE_INDEX'] = str(1)
        # PRIMER_PRODUCT_SIZE_RANGE=???-???
        p3_header_dict['PRIMER_PRODUCT_SIZE_RANGE'] = \
            "{}-{}".format(self.min_product_size, self.max_product_size)
        # PRIMER_NUM_RETURN=1
        p3_header_dict['PRIMER_NUM_RETURN'] = str(1)

        return p3_header_dict


