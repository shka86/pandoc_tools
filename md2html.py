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

args = sys.argv
tgt = p(args[1]).resolve()
pagetitle = F"{tgt.stem}"
outfile = p(f"{tgt.parent}/{tgt.stem}.html")
cwd = p.cwd()

with tempfile.TemporaryDirectory() as td:
    # pandoc実行環境のコピー(UNCパス禁止への対応)
    tmp_wd = p(td) / p('pandoc_tools')
    shutil.copytree(cwd, tmp_wd)

    # 変換対象ファイルのコピー
    shutil.copytree(tgt.parent, tmp_wd / p("work"))
    os.chdir(tmp_wd / p("work"))

    css = p(tmp_wd) / p("style/test.css")
    template = p(tmp_wd) / p("style/test.html")
    cmd = f'pandoc {tgt} -o {outfile} -s --self-contained -c {css} --metadata pagetitle="{pagetitle}" --toc --toc-depth=3 --template={template} -t html5'

    subprocess.run(cmd.split(' '))

    os.chdir(cwd)
