#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
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
LAST_CONVERSION = SOURCE_DIR + "/last_conversion.json"
TOC_DEPTH = 3
TOCNAME = "_toc"
# -----------------------------------


class Markdowns():
    def __init__(self) -> None:

        args = self.argparser()

        # --- 対象リスト生成 --------------------------------
        # 前回の変換リスト読み込み
        if args.renewal or args.delete:
            self.last_mds = {}
        else:
            self.last_mds = self.read_last_conv()

        # 今回の対象リスト作成
        self.mds = {}
        mds = list(p(SOURCE_DIR).glob("**/*.md"))
        mds = [x for x in mds if not x.name.startswith("_")]
        for md in mds:
            path = p(md).as_posix()
            self.mds[path] = {
                "path": path,
                "html": path.replace(".md", ".html"),
                "stamp": datetime.datetime.fromtimestamp(p(md).stat().st_ctime).strftime('%Y/%m/%d-%H:%M:%S'),
            }

        # --- html生成 or html削除 --------------------------------
        # 削除
        if args.delete:
            self.mds = self.delete_htmls(self.mds)

        # 生成
        else:
            self.toc_path = self.gen_html_tree(self.mds, self.last_mds)
            self.insert_header_to_htmls(self.mds, self.toc_path)

        # --- 変換完了したらリストを更新 --------------------------------
        self.write_conv_log(self.mds)

    # -----------------------------------
    def argparser(self):
        parser = argparse.ArgumentParser(description='Nothing')
        parser.add_argument('-r', '--renewal', action="store_true", default=False, help='全mdを変換しなおす')
        parser.add_argument('-d', '--delete', action="store_true", default=False, help='全htmlを削除(mdが存在するものに限る)')
        args = parser.parse_args()
        return args

    def gen_html_tree(self, mds, last_mds):
        for md in mds.values():
            path = md["path"]
            stamp = md["stamp"]
            # md -> html 変換
            if path not in last_mds.keys():  # 新しく追加されたファイル
                do_conv = True
            elif stamp != last_mds[path]["stamp"]:  # 更新されたファイル
                do_conv = True
            else:  # 更新がないファイル（前回htmlに変換済）
                do_conv = False

            if do_conv:
                self.conv_a_file(path)

        # 目次を作成
        toc_path = self.make_toc(self.mds)
        return toc_path

    def delete_htmls(self, mds):
        for md in mds.values():
            tgt = md["html"]
            if p(tgt).is_file():
                os.remove()
                md["stamp"] = "html_deleted"
            else:
                md["stamp"] = "html_notfound"
        return mds

    def read_last_conv(self) -> None:
        if p(LAST_CONVERSION).is_file():
            last_mds = pd.read_json(LAST_CONVERSION, encoding="utf-8")
        else:
            last_mds = {}

        return last_mds

    def conv_a_file(self, tgt) -> None:
        m2h = md2html.main(tgt, css="style/hier.css", template="style/hier.html")

    def make_toc(self, mds) -> None:
        toc = f"# {TREE_TITLE}: Table of Contents\n"
        for md in mds.values():
            html = md["html"]
            relpath = p(html).parent.as_posix()
            dirpath = p(relpath).absolute().as_posix()
            depth = len(relpath.split("/"))
            md["dirpath"] = dirpath
            md["relpath"] = relpath
            md["depth"] = depth

        dir_list = [p(SOURCE_DIR).absolute().as_posix()]
        print(dir_list)
        # for depth in range(1, TOC_DEPTH + 1):
        for md in mds.values():
            if md["depth"] <= TOC_DEPTH:

                if md["dirpath"] not in dir_list:
                    dir_list.append(md["dirpath"])

                    indent = "#" * (int(md["depth"]))
                    link_md = f'{indent} [{md["dirpath"].split("/")[-1]}]({md["dirpath"]})  '
                    md["link_md"] = link_md
                    toc += "\n" + link_md + "\n"

                link = md["html"].replace(f"{SOURCE_DIR}/", "")
                print(link)
                title = p(link).stem
                indent = "    " * (int(md["depth"]) - 1)
                # link_md = f'{indent}- [{title}]({link})  '
                link_md = f'- [{title}]({link})  '
                md["link_md"] = link_md
                toc += link_md + "\n"

        toc_path = f"{SOURCE_DIR}/{TOCNAME}.md"
        with open(toc_path, "w") as f:
            f.write(toc)
        self.conv_a_file(toc_path)
        return toc_path

    def insert_header_to_htmls(self, mds, toc_path):
        """ すべてのページにTOCへのリンクなどを挿入する
            ※ iframeではやりたいことできなかった。リンクを踏んでもiframe内が更新されるだけだった。
            pandoc で生成するページに<header>タグがつくようtemplateを仕込んでおき、いったん生成した後にhtmlを直接編集する。
        """
        # 各ページの編集
        for md in mds.values():
            html = md["html"]
            mdfullpath = p(md["path"]).resolve().as_posix()
            mdparentpath = p(md["path"]).parent.resolve().as_posix()
            tocfullpath = p(toc_path).resolve().as_posix().replace(".md", ".html")
            htmlupdate = md["stamp"]

            with open(html, "r", encoding='utf-8') as f:
                body = f.read()

            header_toc = f'<a class="headerlink_toc" href="{tocfullpath}"> {TREE_TITLE} TOC</a>'
            header_dir = f'<a class="headerlink" href="{mdparentpath}"> source_dir</a>'
            header_source = f'<a class="headerlink" href="{mdfullpath}"> source_file</a>'
            header_update = f'<span class="headerupdate">htmlgen@{htmlupdate}</span>'

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

    def write_conv_log(self, mds) -> None:
        with open(LAST_CONVERSION, "w", encoding="utf-8") as f:
            json.dump(mds, f, indent=4, ensure_ascii=False)

    def show_list(self) -> None:
        for key in self.mds.keys():
            print(f'stamp: {self.mds[key]["stamp"]}, file: {self.mds[key]["path"]}')
        pp(self.mds)


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
