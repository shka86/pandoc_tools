#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import subprocess
from pathlib import Path as p
import tempfile
import datetime

"""markdownからhtmlを生成する
    UNCパスはサポートされません。～
    と表示されても、カレントディレクトリが強制的に変更されるだけで、スクリプトの実行はできている。
    逆に言えばカレントがどこでも動作するように作れば問題ない。
    TemporaryDirectory で作業場所を作って実行する。
"""


class Md2Html():
    def __init__(self, markdown, css, template, opt_toc) -> None:
        self.css = css
        self.template = template
        self.path_markdown = p(markdown).absolute().as_posix()
        self.path_html = None
        self.stamp = datetime.datetime.fromtimestamp(p(markdown).stat().st_ctime).strftime('%Y%m%d-%H%M%S')

        self.generate_html(self.path_markdown, css, template, opt_toc)

    def generate_html(self, tgt, css, template, opt_toc):
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

            css = p(tmp_wd) / p(css)
            template = p(tmp_wd) / p(template)
            cmd = f'pandoc {tgt} -o {outfile} -s --self-contained -c {css} --metadata pagetitle="{pagetitle}" {opt_toc} --template={template} -t html5'
            print(cmd)
            subprocess.run(cmd.split(' '))

            os.chdir(cwd)

        print(f"Done!! output: \n{outfile}")
        self.path_html = p(outfile).absolute().as_posix()


def main(tgt, css="style/test.css", template="style/test.html", opt_toc="--toc --toc-depth=3"):
    m2h = Md2Html(tgt, css, template, opt_toc)
    return m2h


if __name__ == '__main__':
    args = sys.argv
    tgt = p(args[1])

    main(tgt)
