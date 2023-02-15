#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path as p
import argparse
import pandas as pd
import json
import datetime

import md2html

DEBUG = True
MD_SOURCE_DIR = "./mdsample"
LAST_CONVERSION = MD_SOURCE_DIR + "/last_conversion.json"

class Markdowns():
    def __init__(self, renewal=False) -> None:

        # 前回の変換リスト読み込み
        if renewal:
            self.last_mds = {}
        else:
            self.last_mds = self.read_last_conv()

        # 今回の変換対象リスト作成
        self.mds = {}
        for md in p(MD_SOURCE_DIR).glob("**/*.md"):
            path = p(md).as_posix()
            # path = p(md).resolve().as_posix()
            stamp = datetime.datetime.fromtimestamp(p(md).stat().st_ctime).strftime('%Y%m%d-%H%M%S')
            html = path.replace(".md", ".html")

            self.mds[path] = {
                "path": path,
                "html": html,
                "stamp": stamp,
            }

            # md -> html 変換
            if path not in self.last_mds.keys():  # 新しく追加されたファイル
                do_conv = True
            elif stamp != self.last_mds[path]["stamp"]:  # 更新されたファイル
                do_conv = True
            else:  # 更新がないファイル（前回htmlに変換済）
                do_conv = False

            if do_conv:
                self.conv_a_file(path)

        # 目次を作成
        htmls = [self.mds[x]["html"] for x in self.mds]
        self.make_toc(htmls)

        # 変換完了したらリストを更新
        self.show_list()
        self.write_conv_log(self.mds)

    # -----------------------------------

    def read_last_conv(self) -> None:
        if p(LAST_CONVERSION).is_file():
            last_mds = pd.read_json(LAST_CONVERSION, encoding="utf-8")
        else:
            last_mds = {}

        return last_mds

    def conv_a_file(self, tgt) -> None:
        m2h = md2html.main(tgt)

    def make_toc(self, htmls) -> None:
        print(htmls)
        print("--- 未実装機能 --------------------------------")
        print("目次作成。toc.htmlを作る")
        print("hierpan.py専用のcssとtemplateを新たに作成し、左カラムにtoc.htmlを読み込むようにiframeを使う。")
        print("-----------------------------------")
        pass


    def write_conv_log(self, mds) -> None:
        with open(LAST_CONVERSION, "w", encoding="utf-8") as f:
            json.dump(mds, f, indent=4, ensure_ascii=False)
            # json.dump(mds, f, indent=4)

    def show_list(self) -> None:
        for key in self.mds.keys():
            print(f'stamp: {self.mds[key]["stamp"]}, file: {self.mds[key]["path"]}')


# -----------------------------------

def argparser():
    parser = argparse.ArgumentParser(description='Nothing')
    parser.add_argument('--renewal', action="store_true", default=False, help='全mdを変換しなおす')
    args = parser.parse_args()
    return args


def main(args):

    pass


if __name__ == '__main__':

    args = argparser()
    # main(args)

    print(args)
    x = Markdowns(args.renewal)
    # x.show_list()
