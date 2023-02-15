#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path as p
import argparse
import json

import md2html

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tgt', type=str,
                        help='specify a file or dir as convert target')
    parser.add_argument('-l', '--list', action='store_true',
                        help='show the target list')
    args = parser.parse_args()
    return args

class Cpan():
    def __init__(self, args) -> None:
        self.args = args
        self.histories = []  # 過去の変換履歴
        self.markdowns = []  # 変換したmarkdown
        self.htmls = []  # 生成したhtml

        self._init()

    def _init(self):
        history = "./history.json"
        if p(history).is_file():
            with open(history, "r", encoding="utf-8") as f:
                histories = json.load(f)['histories']
        else:
            histories = []

        self.histories = histories

        # -----------------------------------
        if args.list:
            args.tgt = self.select_from_history(histories)

        if args.tgt:
            tgt = args.tgt

            if p(tgt).is_dir():  # If dir, show list and receive which number to convert.
                newhistory = self.conv_a_dir(tgt)
            elif p(tgt).is_file():  # If file, convert to html. Expecting markdown.
                newhistory = self.conv_a_file(tgt)

        # -----------------------------------
        if newhistory:
            newhistory = str(p(newhistory).as_posix())
            newhistories = [newhistory]
            for x in histories:
                x = str(p(x).as_posix())
                if x != newhistory:
                    newhistories.append(x)

            with open(history, "w", encoding="utf-8") as f:
                jsondata = {'histories': newhistories}
                json.dump(jsondata, f, indent=4, ensure_ascii=False)

    def select_from_history(self, histories):
        print('-----------------------------------')
        for i in reversed(range(len(histories))):
            x = histories[i]
            print(f'{i}: {x}')
        print('-----------------------------------')
        tgtnum = input('Select a number: ')
        return str(histories[int(tgtnum)])

    def conv_a_dir(self, tgt):
        tgts = list(p(tgt).glob('**/*.md'))
        print('-----------------------------------')
        for i in reversed(range(len(tgts))):
            x = tgts[i]
            print(f'{i}: {x}')

        print('-----------------------------------')
        tgtnum = input('Select a file number. If all, enter "all": ')

        if tgtnum == "all":
            newhistory = str(tgt)
            for x in tgts:
                m2h = md2html.main(x)
                self.update_info(m2h)
            return newhistory

        else:
            tgt = tgts[int(tgtnum)]
            m2h = md2html.main(tgt)
            self.update_info(m2h)
            newhistory = str(tgt)
            return newhistory

    def conv_a_file(self, tgt):
        m2h = md2html.main(tgt)
        self.update_info(m2h)
        newhistory = str(tgt)
        return newhistory

    def update_info(self, m2h):
        self.markdowns.append(m2h.path_markdown)
        self.htmls.append(m2h.path_html)

# -----------------------------------
if __name__ == "__main__":

    args = argparser()
    cpan = Cpan(args)
    print(cpan.markdowns)
    print(cpan.htmls)
