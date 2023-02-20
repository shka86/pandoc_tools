#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from sre_constants import FAILURE, SUCCESS
from pathlib import Path as p
import argparse
import pandas as pd
import json
import datetime

from pprint import pprint as pp

import md2html

# --- htmlツリー管理向け変数 --------------------------------
TREE_TITLE = "my tree"
# --- このスクリプト開発向け変数 --------------------------------
DEBUG = True
SOURCE_DIR = "mdsample"
# SOURCE_DIR = "../mdsamples"
LAST_CONVERSION = SOURCE_DIR + "/last_conversion.json"
TOC_DEPTH = 99
TOCNAME = "_toc"
# -----------------------------------


class Item():
    def __init__(self) -> None:
        self.path = None
        self.stamp = None
        self.category = None
        self.dirpath = None
        self.depth = None
        self.html = None
        self.result = None
        self.link_md = None


class Hierpan():
    def __init__(self) -> None:
        args = self.argparser()

        # 環境に関する変数
        self.tree_title = TREE_TITLE
        self.debug = DEBUG
        self.source_dir = p(SOURCE_DIR).resolve().as_posix()
        self.last_conversion = LAST_CONVERSION
        self.toc_depth = TOC_DEPTH
        self.tocname = TOCNAME
        self.toc_path = f"{SOURCE_DIR}/{TOCNAME}.md"

        self.rm_toc()
        # 前回の変換リスト
        self.last_tgts = {} if (args.renewal or args.delete) else self.read_last_conv()
        # 今回の変換対象リスト
        self.tgts = self.get_tgts()
        self.dirs = []

        # --- html生成 or html削除 --------------------------------
        # 削除
        if args.delete:
            self.tgts = self.delete_htmls()
        # 生成
        else:
            self.gen_html_tree()  # 個別html生成
            # self.set_placeholder()  # ファイル無しdirに対する措置（微妙だけど）
            self._make_toc()  # TOC生成
            self.insert_header_to_htmls()
            self.write_conv_log()

    # -----------------------------------
    def argparser(self):
        parser = argparse.ArgumentParser(description='Nothing')
        parser.add_argument('-r', '--renewal', action="store_true", default=False, help='全mdを変換しなおす')
        parser.add_argument('-d', '--delete', action="store_true", default=False, help='全htmlを削除(mdが存在するものに限る)')
        args = parser.parse_args()
        return args

    def read_last_conv(self) -> None:
        last_tgts = {}
        if p(LAST_CONVERSION).is_file():
            last_log = pd.read_json(LAST_CONVERSION, encoding="utf-8")
            for last_tgt in last_log:
                print(last_tgt)
                print(last_log[last_tgt])
                last_tgts[last_tgt] = Item()
                last_tgts[last_tgt].path = last_log[last_tgt]["path"]
                last_tgts[last_tgt].stamp = last_log[last_tgt]["stamp"]
                last_tgts[last_tgt].dirpath = last_log[last_tgt]["dirpath"]
                last_tgts[last_tgt].depth = last_log[last_tgt]["depth"]
                last_tgts[last_tgt].html = last_log[last_tgt]["html"]
                last_tgts[last_tgt].result = last_log[last_tgt]["result"]
                last_tgts[last_tgt].link_md = last_log[last_tgt]["link_md"]

        return last_tgts

    def get_tgts(self):
        items = list(p(self.source_dir).glob("**/*"))
        tgts = {}
        for item in items:
            path = p(item).resolve().as_posix()
            if p(path).is_file() and path.endswith(".md"):
                category = "md"
            elif p(path).is_dir():
                category = "dir"
            else:
                category = "others"

            if category in ["md", "dir"]:
                tgts[path] = Item()
                tgts[path].path = path
                tgts[path].stamp = datetime.datetime.fromtimestamp(
                    p(item).stat().st_ctime).strftime('%Y/%m/%d-%H:%M:%S')
                tgts[path].category = category
                tgts[path].depth = len(path.split("/")) - len(self.source_dir.split("/"))
                tgts[path].dirpath = p(path).parent.as_posix()

        self.tgts = tgts
        self.show_items()
        return tgts

    def delete_htmls(self):
        for tgt in self.tgts.values():
            html = tgt.path.replace(".md", ".html")
            if p(html).is_file():
                os.remove(html)
                tgt.stamp = "html_deleted"
            else:
                tgt.stamp = "html_notfound"
        if p(LAST_CONVERSION).is_file():
            os.remove(LAST_CONVERSION)

    def gen_html_tree(self) -> None:
        for tgt in self.tgts.values():
            if tgt.category == "md":

                tgt.html = tgt.path.replace(".md", ".html")

                print(vars(tgt))
                if tgt.path not in self.last_tgts.keys():  # 新しく追加されたファイル
                    do_conv = True
                elif tgt.stamp != self.last_tgts[tgt.path].stamp:  # 更新されたファイル
                    do_conv = True
                else:  # 更新がないファイル（前回htmlに変換済）
                    do_conv = False

                # md -> html 変換
                if do_conv:
                    m2h = md2html.main(tgt.path, css="style/hier.css", template="style/hier.html",
                                       opt_toc="--toc --toc-depth=3")
                    # print(vars(m2h))
                    if m2h.ret.returncode == 0:
                        tgt.result = SUCCESS
                    else:
                        tgt.result = FAILURE

    def relpath(self, path) -> str:
        return

    def rm_toc(self) -> None:
        if p(self.toc_path).is_file():
            os.remove(self.toc_path)

    def dir_crawler(self, dir_, depth=0):
        toc = ""
        items = list(p(dir_).glob("*"))

        # md処理
        mds = [p(x).resolve().as_posix() for x in items if p(x).is_file() and str(x).endswith(".md")]
        for md in mds:
            html = md.replace(".md", ".html")
            link = f'{"    "*depth}- [{p(html).stem}]({html})'
            if p(html).is_file() is False:
                link += "(link切れ)"
            toc += f"{link}\n"

        # dir処理
        dirs = [p(x).resolve().as_posix() for x in items if p(x).is_dir()]
        for dir_ in dirs:
            link = f'{"    "*depth}- **[{p(dir_).name}]({dir_})**'
            toc += f"{link}\n"
            toc += self.dir_crawler(dir_, depth+1)

        return toc

    def _make_toc(self) -> None:

        toc = self.dir_crawler(self.source_dir)

        with open(self.toc_path, "w", encoding="utf-8") as f:
            f.write(toc)

        m2h = md2html.main(self.toc_path, css="style/hier.css", template="style/hier.html", opt_toc="--toc")



    # def make_toc(self) -> None:
    #     toc = f""

    #     done_dir_list = []

    #     dict_order = sorted(self.tgts.keys())
    #     self.dict_order = dict_order

    #     for d in dict_order:
    #         tgt = self.tgts[d]
    #         print(d)
    #     # for tgt in self.tgts.values():
    #         # pp(vars(tgt))
    #         if tgt.depth <= self.toc_depth:

    #             # dir行の生成
    #             if (tgt.category == "dir") and (tgt.path not in done_dir_list):
    #                 indent = "    " * (int(tgt.depth) - 1)
    #                 link_md = f'{indent}- **[{tgt.path.split("/")[-1]}]({tgt.path})**'
    #                 tgt.link_md = link_md
    #                 toc += f'{link_md}\n'
    #                 done_dir_list.append(tgt.path)

    #             elif tgt.category == "md":
    #                 # ファイル行の生成
    #                 link = tgt.html
    #                 # print(link)
    #                 title = p(link).stem
    #                 indent = "    " * (int(tgt.depth) - 1)
    #                 # link_md = f'{indent}　[{title}]({link})  '
    #                 link_md = f'{indent}- [{title}]({link})'
    #                 if p(tgt.html).is_file() is False:
    #                     link_md += "(link切れ)  "
    #                 tgt.link_md = link_md
    #                 toc += f"{link_md}\n"

    #     with open(self.toc_path, "w", encoding="utf-8") as f:
    #         f.write(toc)

    #     m2h = md2html.main(self.toc_path, css="style/hier.css", template="style/hier.html", opt_toc="--toc")

    def insert_header_to_htmls(self):
        """ すべてのページにTOCへのリンクなどを挿入する
            ※ iframeではやりたいことできなかった。リンクを踏んでもiframe内が更新されるだけだった。
            pandoc で生成するページに<header>タグがつくようtemplateを仕込んでおき、いったん生成した後にhtmlを直接編集する。
        """
        # 各ページの編集
        for tgt in self.tgts.values():
            html = tgt.html
            mdfullpath = p(tgt.path).resolve().as_posix()
            mdparentpath = p(tgt.path).parent.resolve().as_posix()
            tocfullpath = p(self.toc_path).resolve().as_posix().replace(".md", ".html")
            htmlupdate = tgt.stamp

            if tgt.result is SUCCESS:
                with open(html, "r", encoding='utf-8') as f:
                    body = f.read()

                header_toc = f'<a class="headerlink_toc" href="{tocfullpath}"> {TREE_TITLE} TOC</a>'
                header_dir = f'<a class="headerlink" href="{mdparentpath}"> source_dir</a>'
                header_source = f'<a class="headerlink" href="{mdfullpath}"> source_file</a>'
                header_update = f'<span class="headerupdate">source update @ {htmlupdate}</span>'

                body = body.replace(
                    "HEREISHEADERHEREISHEADERHEREISHEADER",
                    f"{header_toc}  {header_dir} / {header_source} {header_update}"
                )

                with open(html, "w", encoding='utf-8') as f:
                    f.write(body)

        # TOCの編集
        with open(tocfullpath, "r", encoding='utf-8') as f:
            body = f.read()

        tocparentpath = p(tocfullpath).parent.resolve().as_posix()
        tocmdpath = tocfullpath.replace(".html", ".md")
        header_toc = f'<a class="headerlink_toc" href="{tocfullpath}"> {TREE_TITLE} TOC</a>'
        header_dir = f'<a class="headerlink" href="{tocparentpath}"> source_dir</a>'
        header_source = f'<a class="headerlink" href="{tocmdpath}"> source_file</a>'
        header_update = f'<span class="headerupdate">source update @ {htmlupdate}</span>'

        body = body.replace(
            "HEREISHEADERHEREISHEADERHEREISHEADER",
            f"{header_toc}  {header_dir} / {header_source} {header_update}"
        )

        with open(tocfullpath, "w", encoding='utf-8') as f:
            f.write(body)

    def write_conv_log(self) -> None:
        str_json = {}
        for label, item in self.tgts.items():
            str_json[label] = vars(item)
        with open(LAST_CONVERSION, "w", encoding="utf-8") as f:
            json.dump(str_json, f, indent=4, ensure_ascii=False)

    def show_list(self) -> None:
        # for key in self.tgts.keys():
        #     print(f'stamp: {self.tgts[key]["stamp"]}, file: {self.tgts[key]["path"]}')
        pp(self.tgts)

    def show_items(self) -> None:
        for tgt in self.tgts.values():
            pp(vars(tgt))

# -----------------------------------


def argparser():
    parser = argparse.ArgumentParser(description='Nothing')
    parser.add_argument('-r', '--renewal', action="store_true", default=False, help='全mdを変換しなおす')
    parser.add_argument('-d', '--delete', action="store_true", default=False, help='全htmlを削除(mdが存在するものに限る)')
    args = parser.parse_args()
    return args


def main(args):

    pass


if __name__ == '__main__':

    x = Hierpan()
    # for a in x.dict_order:
    # # for a in x.tgts.keys():
    #     print(a)
    
    
    # x.show_list()
