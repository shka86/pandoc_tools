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


class Markdowns():
    def __init__(self) -> None:
        args = self.argparser()

        # 環境に関する変数
        self.tree_title = TREE_TITLE
        self.debug = DEBUG
        self.source_dir = p(SOURCE_DIR).resolve().as_posix()
        self.last_conversion = LAST_CONVERSION
        self.toc_depth = TOC_DEPTH
        self.tocname = TOCNAME

        # 未定義の変数（メソッド内で更新）
        self.toc_path = None

        # 前回の変換リスト
        self.last_tgts = {} if (args.renewal or args.delete) else self.read_last_conv()
        # 今回の変換対象リスト
        self.tgts = self.get_tgts()

        # --- html生成 or html削除 --------------------------------
        # 削除
        if args.delete:
            self.tgts = self.delete_htmls()
        # 生成
        else:
            self.gen_html_tree()  # 個別html生成
            self.make_toc()  # TOC生成
            self.insert_header_to_htmls()

        # --- 変換完了したらリストを更新 --------------------------------
        self.write_conv_log()

    # -----------------------------------
    def argparser(self):
        parser = argparse.ArgumentParser(description='Nothing')
        parser.add_argument('-r', '--renewal', action="store_true", default=False, help='全mdを変換しなおす')
        parser.add_argument('-d', '--delete', action="store_true", default=False, help='全htmlを削除(mdが存在するものに限る)')
        args = parser.parse_args()
        return args

    def read_last_conv(self) -> None:
        if p(LAST_CONVERSION).is_file():
            last_mds = pd.read_json(LAST_CONVERSION, encoding="utf-8")
        else:
            last_mds = {}

        return last_mds

    def get_tgts(self):
        mds = list(p(self.source_dir).glob("**/*.md"))
        mds = [x for x in mds if not x.name.startswith("_")]
        tgts = {}
        for md in mds:
            path = p(md).resolve().as_posix()
            tgts[path] = {
                "path": path,
                "stamp": datetime.datetime.fromtimestamp(p(md).stat().st_ctime).strftime('%Y/%m/%d-%H:%M:%S'),
            }
        return tgts

    def delete_htmls(self):
        for tgt in self.tgts.values():
            html = tgt["html"]
            if p(html).is_file():
                os.remove(html)
                tgt["stamp"] = "html_deleted"
            else:
                tgt["stamp"] = "html_notfound"

    def gen_html_tree(self) -> None:
        for tgt in self.tgts.values():
            path = tgt["path"]
            tgt["dirpath"] = p(tgt["path"]).parent.as_posix()
            tgt["depth"] = len(tgt["path"].split("/")) - len(self.source_dir.split("/"))
            tgt["html"] = path.replace(".md", ".html")

            if path not in self.last_tgts.keys():  # 新しく追加されたファイル
                do_conv = True
            elif tgt["stamp"] != self.last_tgts[p(path)]["stamp"]:  # 更新されたファイル
                do_conv = True
            else:  # 更新がないファイル（前回htmlに変換済）
                do_conv = False

            # md -> html 変換
            if do_conv:
                m2h = md2html.main(path, css="style/hier.css", template="style/hier.html",
                                   opt_toc="--toc --toc-depth=3")
                if m2h.ret.returncode == 0:
                    tgt["result"] = SUCCESS
                else:
                    tgt["result"] = FAILURE

    def make_toc(self) -> None:
        toc = f""

        dir_list = [p(self.source_dir).absolute().as_posix()]
        print(dir_list)

        for tgt in self.tgts.values():
            if tgt["depth"] <= self.toc_depth:
                pp(tgt)

                # dir行の生成
                if tgt["dirpath"] not in dir_list:
                    dir_list.append(tgt["dirpath"])

                    indent = "    " * (int(tgt["depth"]) - 2)
                    link_md = f'{indent}- 【 [{tgt["dirpath"].split("/")[-1]}]({tgt["dirpath"]}) 】  '
                    tgt["link_md"] = link_md
                    toc += f"\n{link_md}\n"

                # ファイル行の生成
                link = tgt["html"].replace(f"{SOURCE_DIR}/", "")
                print(link)
                title = p(link).stem
                indent = "    " * (int(tgt["depth"]) - 1)
                link_md = f'{indent}[{title}]({link})  '
                if tgt["result"] is FAILURE:
                    link_md += "(link切れ)  "
                tgt["link_md"] = link_md
                toc += f"{link_md}\n"

        toc_path = f"{SOURCE_DIR}/{TOCNAME}.md"
        with open(toc_path, "w", encoding="utf-8") as f:
            f.write(toc)

        m2h = md2html.main(toc_path, css="style/hier.css", template="style/hier.html", opt_toc="--toc")
        self.toc_path = toc_path

    def insert_header_to_htmls(self):
        """ すべてのページにTOCへのリンクなどを挿入する
            ※ iframeではやりたいことできなかった。リンクを踏んでもiframe内が更新されるだけだった。
            pandoc で生成するページに<header>タグがつくようtemplateを仕込んでおき、いったん生成した後にhtmlを直接編集する。
        """
        # 各ページの編集
        for tgt in self.tgts.values():
            html = tgt["html"]
            mdfullpath = p(tgt["path"]).resolve().as_posix()
            mdparentpath = p(tgt["path"]).parent.resolve().as_posix()
            tocfullpath = p(self.toc_path).resolve().as_posix().replace(".md", ".html")
            htmlupdate = tgt["stamp"]


            if tgt["result"] == "SUCCESS":
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
        with open(LAST_CONVERSION, "w", encoding="utf-8") as f:
            json.dump(self.tgts, f, indent=4, ensure_ascii=False)

    def show_list(self) -> None:
        # for key in self.tgts.keys():
        #     print(f'stamp: {self.tgts[key]["stamp"]}, file: {self.tgts[key]["path"]}')
        pp(self.tgts)


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

    x = Markdowns()
    x.show_list()
