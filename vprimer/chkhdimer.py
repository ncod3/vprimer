# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import errno
import time
import pprint
import itertools

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

# global configuration
import vprimer.glv as glv
import vprimer.utils as utl

from vprimer.logging_config import LogConf
log = LogConf.open_log(__name__)

import pandas as pd

from vprimer.inout_primer3 import InoutPrimer3

class ChkHDimer(object):

    def __init__(self):

        # 新規カラム名
        self.col_interval = "interval"  # interval は 0で初期化
        self.col_hdimer = "hdimer"      # hdimer は "" で初期化
        # 辞書を作るときに一時的に使う、軽いファイル内容
        self.ucols = ['chrom', 'pos',
            'PRIMER_LEFT_0_SEQUENCE','PRIMER_RIGHT_0_SEQUENCE']

    def filter_and_check_hetero_dimer(self):

        # If pick_mode is not SNP, it does't need to do this
        if glv.conf.pick_mode != glv.MODE_SNP:
            return

        # snpfilter (060)
        proc_name = "snpfilter"
        # stop or continue ---------------------------------
        ret_status = utl.decide_action_stop(proc_name)

        if ret_status == glv.progress_stop:
            log.info(utl.progress_message(ret_status, proc_name))
            sys.exit(1)

        if ret_status == glv.progress_gothrough:
            log.info(utl.progress_message(ret_status, proc_name))
        else:
            # snp_filter を実施して、060 に書き込む
            self.snp_filtering(proc_name)
        # --------------------------------------------------

        proc_name = "chkhdimer"
        # stop or continue ---------------------------------
        ret_status = utl.decide_action_stop(proc_name)

        if ret_status == glv.progress_stop:
            log.info(utl.progress_message(ret_status, proc_name))
            sys.exit(1)

        if ret_status == glv.progress_gothrough:
            log.info(utl.progress_message(ret_status, proc_name))
            return
        # --------------------------------------------------

        # すべてのヘテロダイマーが消えるまでループ
        self.loop_hetero_dimer(proc_name)

        # 070に書き出す
        self.write_to_chkhdimer()


    def write_to_chkhdimer(self):

        # 辞書を作るときに一時的に使う、軽いファイル内容
        for proc_cnt, (distin_gdct, reg) in enumerate(
            glv.conf.gdct_reg_list, 1):

            read_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']
            write_chkhdimer = distin_gdct['chkhdimer']['fn'][reg]['out_path']

            df_snpfil = pd.read_csv(read_snpfilter,
                sep='\t', dtype=str, header=0, index_col=None)
            df_snpfil = df_snpfil.astype({self.col_interval: 'int'})

            # 1が、現在適切とされているintervalのprimer, それだけを集める
            q = "{} == 1".format(self.col_interval)
            # 全カラム
            df_chkhdimer = df_snpfil.query(q)

            # save
            utl.save_to_tmpfile(write_chkhdimer)

            # write
            df_chkhdimer.to_csv(write_chkhdimer, sep = '\t',
                index = None, encoding='utf-8')
            log.info("write {}".format(write_chkhdimer))


    def snp_filtering(self, proc_name):
        ''' 050_primer のファイルから、gcrangeに適合するプライマーのみ
            抽出して、060_snpfilter にファイルとして保存する
            このファイル群が、interval で候補とされるプライマーである。
        '''

        log.info("-------------------------------")
        log.info("Start processing {}\n".format(proc_name))

        # 指定のgcrange でプライマーをピックアップする。
        gcrange = glv.conf.snp_filter_gcrange
        gc_min = glv.conf.snp_filter_gc_min
        gc_max = glv.conf.snp_filter_gc_max
        # 当初は、指定のインターバルで、DataFrameに印を付けておく
        interval = glv.conf.snp_filter_interval

        # 1) filter and write to file
        for proc_cnt, (distin_gdct, reg) in enumerate(
            glv.conf.gdct_reg_list, 1):

            log.info("")
            log.info("proc_cnt={}, distin_str={}".format(
                proc_cnt, distin_gdct['distin_str']))

            # 読み出し、書き出しのファイル名の準備
            read_formpass = distin_gdct['formpass']['fn'][reg]['out_path']
            write_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']

            # ファイルの読み出しは、最初は、strで行う
            df_formpass = pd.read_csv(
                read_formpass, sep='\t', dtype=str, header=0, index_col=None)
            # 検索に用いるastypeの調整
            df_formpass = df_formpass.astype(
                {'pos': 'int', 'product_gc_contents': 'float'})

            # pick data by gc_contents
            if gcrange != "":
                q = "{} >= {} and {} <= {}".format(
                    "product_gc_contents", gc_min,
                    "product_gc_contents", gc_max)
                # product_gc_contents
                df_gc = df_formpass.query(q)
            else:
                # gcrangeの指定がない場合は、すべてのデータを採用
                df_gc = df_formpass

            # ２つの新規列名を追加する。
            # 1) interval プライマーとして採用されたもの。1で示す。
            # 0は、未だ考慮されていない。2は、一度採用されたが、
            # ヘテロダイマーチェックで非採用となった。

            # 0 origin の34番目に、0で初期化して列を追加
            df_gc.insert(len(df_gc.columns), self.col_interval, 0,
                allow_duplicates=False)
            # 0 origin の35番目に、'-' で初期化して列を追加
            df_gc.insert(len(df_gc.columns), self.col_hdimer, '-',
                allow_duplicates=False)

            # もし、df_gcの数が０ならば、ヘッダを書いてここは終わり
            if len(df_gc) == 0:
                mes = "There is no value in reg({}) ".format(
                    glv.conf.regions_dict[reg]['reg'])
                mes += "where gcrange is between "
                mes += "gc_min({}) and gc_max({}. ".format(gc_min, gc_max)
                mes += "Stop working here."
                log.info(mes)
                df_gc.to_csv(write_snpfilter, sep = '\t',
                    index = None, encoding='utf-8')
                continue

            # インターバルによるピックアップ
            picked_cnt = 0    # インターバルで採用された数
            # 基盤としての全ポジションのリスト
            all_pos_list = df_gc['pos'].values.tolist()

            # 指定のintervalが０や、ポジションが１，２、３の場合は
            if interval == 0 or len(all_pos_list) <= 3:

                # ポジションが1-3の場合、先頭と最後と中間をとって
                # 終わりなので、調整が不要
                df_gc[self.col_interval] = 1
                picked_cnt = len(df_gc)

            else:
                # それ以外は、interval_pick を実施する
                intv_pos_list = self.get_interval_pos_list(
                    all_pos_list, interval)

                # intr_pos_list のposのboolian indexを取得
                picked_bool_idx = df_gc['pos'].isin(intv_pos_list)
                picked_cnt = picked_bool_idx.sum()

                # set 1 to interval record
                df_gc.loc[picked_bool_idx, [self.col_interval]] = 1

            log.info("filtered condition: gcrange={}, interval={:,}".format(
                gcrange, interval))
            mes = "filtered record cnt {}, ".format(len(df_gc))
            mes += "total interval start {}".format(picked_cnt)

            # 最初のインターバルを格納する場所
            distin_gdct['chkhdimer']['fn'][reg]['intv_stt'] = picked_cnt
            log.info(mes)

            # save
            utl.save_to_tmpfile(write_snpfilter)
            mes = "Data for snp_filtered primers were "
            mes += "output to {}".format(write_snpfilter)
            log.info(mes)
            df_gc.to_csv(write_snpfilter, sep = '\t',
                index = None, encoding='utf-8')


    def get_interval_pos_list(self, all_pos_list, interval):
        '''
        '''
        # 指定の 距離 interval を離したポジションを リストで確保する。
        intv_pos_list = list()

        # 候補は必ず４つ以上ある。

        top_pos = 0     # 確保すべき先頭ポジション
        bottom_pos = 0  # 確保すべき最後尾ポジション

        end_of_region = 0   # 今いる領域の最後のポジション

        '''
        1 origin < 0
        '''
        for pos in all_pos_list:

            # bottom_posは常に入れておく
            bottom_pos = pos

            # 最初の処理のときは、
            if top_pos == 0:
                top_pos = pos   # top_pos に入れる

                # 次のしきい値（内側）ここまでは今の範囲
                # 1-100, 101-200
                end_of_region = self.get_end_of_region(pos, interval)
                # appendした。
                intv_pos_list.append(pos)
                continue

            # 今の領域の最後を超えてないなら、このposは飛ばす
            if pos <= end_of_region:
                continue

            #print("pos={}".format(pos))
            end_of_region = self.get_end_of_region(pos, interval)
            # appendした。
            intv_pos_list.append(pos)

        # ループを抜けた最後に、bottom_pos がリストに入ってなければ、
        # ここで入れるこの処理をすることで、ダブったり足りなかったり
        # することが無くなるだろう。
        if not bottom_pos in intv_pos_list:
            intv_pos_list.append(bottom_pos)

        pick_cnt = len(intv_pos_list)

        return intv_pos_list


    def get_end_of_region(self, pos, interval):
        '''
        今いるポジションの最後部を返す
        '''

        next_border = 0

        # 商を計算
        quotient = pos / interval
        # 余りを切り捨てる
        q_int = int(quotient)

        # 次のボーダーラインを計算
        if q_int < quotient:
            next_border = (q_int + 1) * interval
        else:
            next_border = q_int * interval

        # もしボーダーが限界を超えていたら

        return next_border


    def cmb(self, n, r):
        ''' https://qiita.com/derodero24/items/91b6468e66923a87f39f
        '''

        # n=824316, r=2
        # 339,748,021,770 3千億

        if n - r < r: r = n - r
        if r == 0: return 1
        if r == 1: return n

        numerator = [n - r + k + 1 for k in range(r)]
        denominator = [k + 1 for k in range(r)]

        for p in range(2,r+1):
            pivot = denominator[p - 1]
            if pivot > 1:
                offset = (n - r) % p
                for k in range(p-1,r,p):
                    numerator[k - offset] /= pivot
                    denominator[k] /= pivot

        result = 1
        for k in range(r):
            if numerator[k] > 1:
                result *= int(numerator[k])

        return result


    def loop_hetero_dimer(self, proc_name):


        # ループを脱出できるフラグ
        loop_hdimer_exit = True
        loop_cnt = 1
        
        # すべての distin_gdct['hdimer_ngc'] が 0になるまで
        # ループ
        while True:

            log.info("-------------------------------")
            log.info("Start processing {}, loop={}\n".format(
                proc_name, loop_cnt))

            # 1) ループ開始時には辞書をクリアしてはじめる
            for distin_cnt, distin_gdct in enumerate(
                glv.conf.distinguish_groups_list, 1):

                # これは初期化が必要
                distin_gdct['hdimer_seq'].clear()
                distin_gdct['hdimer_ng'].clear()
                distin_gdct['hdimer_ngc'] = 0
                distin_gdct['hdimer_dict'].clear()

            # 2) 最新のinterval==1のprseqの出自dictを作成する
            # chromごとに追加していく
            for proc_cnt, (distin_gdct, reg) in enumerate(
                glv.conf.gdct_reg_list, 1):

                self.add_prseq_dict(proc_cnt, distin_gdct, reg)

            # 3) distin_gdct ごとに、ヘテロダイマーチェック
            for distin_cnt, distin_gdct in enumerate(
                glv.conf.distinguish_groups_list, 1):

                # NGだったペアをdistin_gdctに保存していく
                self.confirm_hdimer_check(distin_cnt, distin_gdct)

            # 4) NGのプライマペアがある場合
            loop_hdimer_exit = list()
            for proc_cnt, (distin_gdct, reg) in enumerate(
                glv.conf.gdct_reg_list, 1):

                # NGがある場合、
                #   4.1 bad_idx の interval と、hdimer 行を更新する
                #   4.2 good_idxの interval を更新する。
                #   前のファイルをbakに移動して
                #   あらためてdfを保存
                if distin_gdct['hdimer_ngc'] != 0:
                    # update_candidate_pos
                    self.update_candidate_pos(proc_cnt, distin_gdct, reg)
                    loop_hdimer_exit.append(False)
                else:
                    loop_hdimer_exit.append(True)

            # 全部がTrueならexit
            if not False in loop_hdimer_exit:
                log.info("loop_hdimer_exit {}".format(loop_hdimer_exit))
                log.info("hdimer check loop end.\n")
                break

            loop_cnt += 1


    def add_prseq_dict(self, proc_cnt, distin_gdct, reg):

        # distin_gdct['hdimer_dict'] ここはchromごとの処理なので、
        # もとの辞書には、prseqを追加していく。
        hd_dict = distin_gdct['hdimer_dict']

        # 読むファイル 060_
        read_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']

        # 060_snpfilterを読み込む
        df_snpfil = pd.read_csv(read_snpfilter,
            sep='\t', dtype=str, header=0, index_col=None)
        df_snpfil = df_snpfil.astype({self.col_interval: 'int'})

        # 1が、現在適切とされているintervalのprimer, それだけを集める
        q = "{} == 1".format(self.col_interval)
        # 必要なカラムのみで良い
        df_interval = df_snpfil.query(q)[self.ucols]

        # ファイルを読み設定する
        for index, row in df_interval.iterrows():
            # 染色体、位置、左prseq, 右prseq
            chrom = row['chrom']
            pos = row['pos']
            l_prseq = row['PRIMER_LEFT_0_SEQUENCE']
            r_prseq = row['PRIMER_RIGHT_0_SEQUENCE']

            for prseq, direct in zip([l_prseq, r_prseq], ["L", "R"]):

                # prseqが登録済みかどうか
                if prseq in hd_dict.keys():
                    # 登録済みなら、add
                    hd_dict[prseq].add_location(chrom, pos, direct)

                else:
                    # 未登録ならクラス
                    amplp = AmplPrimer(prseq, chrom, pos, direct)
                    hd_dict[amplp.sequence] = amplp

        mes = "The number of primer sequences in {} are {}".format(
            reg, len(hd_dict.keys()))
        log.info(mes)


    def confirm_hdimer_check(self, distin_cnt, distin_gdct):

        # 簡単アクセス
        hd_dict = distin_gdct['hdimer_dict']

        # 並列モードは、Processで。
        mode = "process"
        
        if mode == "process":
            mode_action = ProcessPoolExecutor
        else:
            mode_action = ThreadPoolExecutor

        cpu = glv.conf.parallel_full_thread
        cnt = len(hd_dict.keys())
        # 全組み合わせを実施する数
        combi_cnt = self.cmb(cnt, 2)
        # ここで、数が多すぎる場合に、止めたほうがいいか？
        
        log.info("mode={}, cpu={}, cnt={}, combi_cnt={}".format(
            mode, cpu, cnt, combi_cnt))

        # 並列処理を実施する。
        with mode_action(max_workers=cpu) as executor:
            futures = executor.map(
                self.wrapper, (
                    (combi_cnt, i, prseq1, prseq2) for
                        i, (prseq1, prseq2) in enumerate(
                            itertools.combinations(hd_dict.keys(), 2), 1)
                )
            )

        # futures はイテレータ
        for result in futures:
            # 結果を処理
            l_prseq_t, r_prseq_t, res_dict = result
            # res_dict
            # 'stat':     hetd.structure_found,
            # 'tm':       hetd.tm,
            # 'detail':   hetd.ascii_structure,
            # 'ok':       True
            false_or_true = res_dict['hetd']['ok']

            if false_or_true == False:
                # ここで示された 配列のペア、l_prseq_t, r_prseq_t は、
                # ヘテロダイマーチェックを通っていない
                # 通っていないリストに追加し、
                distin_gdct['hdimer_ng'].append(l_prseq_t)
                distin_gdct['hdimer_ng'].append(r_prseq_t)
                distin_gdct['hdimer_ngc'] += 1

                # 辞書にも、自分との不具合ペアを書き入れる
                hd_dict[l_prseq_t].add_ng_partner(
                    hd_dict[r_prseq_t].locations)
                hd_dict[r_prseq_t].add_ng_partner(
                    hd_dict[l_prseq_t].locations)

                # チェックを通らないペアは、ここで表示できる

        mes = "heterodimer check NG pair count {}".format(
            distin_gdct['hdimer_ngc'])
        log.info(mes)


    def wrapper(self, args):
        '''
        引数は、パックされてくるので、アンパックする
        '''

        combi_cnt, i, prseq1, prseq2 = args

        if i % 10000 == 1:
            log.info("{} / {}".format(i, combi_cnt)) 

        # ヘテロダイマーチェック
        res_dict = InoutPrimer3.check_all_primer_hetero_dimer(
            prseq1, prseq2)
        # 'stat':     hetd.structure_found,
        # 'tm':       hetd.tm,
        # 'detail':   hetd.ascii_structure,
        # 'ok':       True

        return prseq1, prseq2, res_dict


    def update_candidate_pos(self, proc_cnt, distin_gdct, reg):
        '''
        '''

        hd_dict = distin_gdct['hdimer_dict']
        # 当初のインターバル化ポジション
        intv_stt = distin_gdct['chkhdimer']['fn'][reg]['intv_stt']

        # bak移動、updateするファイル
        update_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']
        # utl.save_to_tmpfile(update_snpfilter)

        # 判断に使う一時的カラム
        tmp_col = [
            'chrom',
            'pos',
            'PRIMER_LEFT_0_SEQUENCE',
            'PRIMER_RIGHT_0_SEQUENCE',
            'interval',
            'hdimer'
        ]

        # NGのprseqリストが存在するレコードの１つあとを保存
        # 060_snpfilterのファイルを更新
        update_snpfilter = distin_gdct['snpfilter']['fn'][reg]['out_path']

        # 060_snpfilter 全体を読み込む
        df_snpfil = pd.read_csv(update_snpfilter,
            sep='\t', dtype=str, header=0, index_col=None)
        df_snpfil = df_snpfil.astype({self.col_interval: 'int'})

        # 0オリジンの行数なので、この数字 <= だとdfにアクセスできない。
        max_idx = len(df_snpfil)

        # PRIMER_LEFT_0_SEQUENCE と、PRIMER_RIGHT_0_SEQUENCE で
        # 排除すべきprseqが書かれた行を抽出する。
        left_seq_bool_idx = df_snpfil['PRIMER_LEFT_0_SEQUENCE'].isin(
            distin_gdct['hdimer_ng'])
        right_seq_bool_idx = df_snpfil['PRIMER_RIGHT_0_SEQUENCE'].isin(
            distin_gdct['hdimer_ng'])

        # bool_idx で、andを取る
        seq_bool_idx = left_seq_bool_idx | right_seq_bool_idx

        # もし、interval==1のデータがあるのなら、
        q = "{} == 1".format(self.col_interval)
        df_ng_interval = df_snpfil[seq_bool_idx].query(q)[tmp_col]

        #print()
        #print("intv_stt={}".format(intv_stt))
        #print("len_df={}".format(len(df_ng_interval)))
        #print()

        # ここでレコードが０なら 何もしない
        if len(df_ng_interval) == 0:
            mes = "This file does not contain bad prseq. {}".format(
                update_snpfilter)
            log.info(mes)
            return
        else:
            mes = "This file contain {} bad prseq. {}".format(
                len(df_ng_interval), update_snpfilter)
            log.info(mes)

        # ilocのための、カラムのindex番号を取得する
        # self.col_hdimer
        interval_col_idx = df_snpfil.columns.get_loc(self.col_interval)
        hdimer_col_idx = df_snpfil.columns.get_loc(self.col_hdimer)
        lpr_col_idx = df_snpfil.columns.get_loc('PRIMER_LEFT_0_SEQUENCE')
        rpr_col_idx = df_snpfil.columns.get_loc('PRIMER_RIGHT_0_SEQUENCE')

        # ヘテロダイマーチェックに引っかかった bad_idx を対象に
        # 変更があればファイル更新を実施する
        for bad_idx in df_ng_interval.index.to_list():

            # ヘテロダイマーチェックに引っかかった bad_idx を対象に
            # 1) intervalの値をilocで、+1する。
            df_snpfil.iloc[bad_idx, interval_col_idx] += 1

            # 2) col_hdimerに、チェック不通のペアの情報を入れる
            l_pr = df_snpfil.iloc[bad_idx, lpr_col_idx]
            r_pr = df_snpfil.iloc[bad_idx, rpr_col_idx]

            # プライマーチェックのエラー情報を、060_に更新する
            bad_pd_info = ""
            # プライマーのチェック辞書には、右か左に、チェックを通らなかった
            # ＰＤの情報が入っているはず
            if len(hd_dict[l_pr].ng_partners) != 0:
                # 辞書からエラー相手の情報取得、最後,
                bad_pd_info += ','.join(hd_dict[l_pr].ng_partners)
                bad_pd_info += ','

            if len(hd_dict[r_pr].ng_partners) != 0:
                # 辞書からエラー相手の情報取得、最後,
                bad_pd_info += ','.join(hd_dict[r_pr].ng_partners)
                bad_pd_info += ','

            # エラー情報があれば、書き入れる
            if bad_pd_info != "":
                # '-' は消して、
                if "-" == df_snpfil.iloc[bad_idx, hdimer_col_idx]:
                    df_snpfil.iloc[bad_idx, hdimer_col_idx] = ""

                df_snpfil.iloc[bad_idx, hdimer_col_idx] += bad_pd_info

            # good_idx 、チェックを通らなかったプライマの次をセットする。
            good_idx = bad_idx + 1

            # 最終行を超えていたらアクセスできないので、
            #print("good_idx={}, max_idx={}".format(good_idx, max_idx))
            #print("good_idx={}, interval={}".format(good_idx,
            #    df_snpfil.iloc[good_idx, interval_col_idx]))

            if good_idx >= max_idx:
                # 更新しない
                mes = "There are no more positions to update "
                mes += "in this file."
                log.info(mes)

            elif df_snpfil.iloc[good_idx, interval_col_idx] != 0:
                # intervalが0以外なら、すでにチェック済みなので更新しない
                mes = "There are no more positions to update "
                mes += "in this interval."
                log.info(mes)

            else:
                # 更新する
                df_snpfil.iloc[good_idx, interval_col_idx] += 1


        q = "{} == 1".format(self.col_interval)
        mes = "interval start {}, now update {}".format(
            len(df_snpfil.query(q)[self.ucols]), intv_stt)
        log.info(mes)

        # 既存のファイルをバックして、
        utl.save_to_tmpfile(update_snpfilter)
        # 新たに書き込む

        df_snpfil.to_csv(update_snpfilter, sep = '\t',
            index = None, encoding='utf-8')

        mes = "update {}".format(update_snpfilter)
        log.info(mes)


#-------------------------------------------------------
class AmplPrimer(object):
    # prseqをキーとして持つ辞書として
    # locationをキーとして持つ

    # メモリの節約、単純化されたdictionary
    __slots__ = ['sequence', 'locations', 'ng_partners']

    def __init__(self, *arg):

        sequence, chrom, pos, direct = arg

        self.sequence = sequence
        self.locations = []     # "chrom:pos:direct" の配列
        self.ng_partners = []    # "ngだったパートナーの配列
        self.add_location(chrom, pos, direct)

    def add_location(self, *arg):

        chrom, pos, direct = arg

        self.locations.append("{}:{}:{}".format(chrom, pos, direct))

    def add_ng_partner(self, locations):

        # 渡されたlocationsのリストを、追加する
        # appendだと、二重リストになってしまうので +=
        self.ng_partners += locations


