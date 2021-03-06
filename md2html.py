#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import subprocess
from pathlib import Path as p
import tempfile

"""markdownからhtmlを生成する
    UNCパスはサポートされません。～
    と表示されても、カレントディレクトリが強制的に変更されるだけで、スクリプトの実行はできている。
    逆に言えばカレントがどこでも動作するように作れば問題ない。
    TemporaryDirectory で作業場所を作って実行する。
"""


def main(tgt):
    tgt = p(tgt).resolve()
    print("---")
    print(f"convert tgt: \n{tgt}")
    print("---")
    if (not tgt.is_file()) or (str(tgt) == "."):
        return 0

    pagetitle = f"{tgt.stem}"
    outfile = p(f"{tgt.parent}/{tgt.stem}.html")
    cwd = p.cwd()

    with tempfile.TemporaryDirectory() as td:
        # pandoc実行環境のコピー(UNCパス禁止への対応)
        tmp_wd = p(td) / cwd.stem
        shutil.copytree(cwd, tmp_wd)

        # 変換対象ファイルのコピー
        shutil.copytree(tgt.parent, tmp_wd / p("work"))
        items = tmp_wd.glob("**/*")
        for item in items:
            item.chmod(0o777)
        os.chdir(tmp_wd / p("work"))

        css = p(tmp_wd) / p("style/test.css")
        template = p(tmp_wd) / p("style/test.html")
        cmd = f'pandoc {tgt} -o {outfile} -s --self-contained -c {css} --metadata pagetitle="{pagetitle}" --toc --toc-depth=3 --template={template} -t html5'

        subprocess.run(cmd.split(' '))

        os.chdir(cwd)

    print(f"Done!! output: \n{outfile}")

if __name__ == '__main__':
    args = sys.argv
    tgt = p(args[1])
    main(tgt)
