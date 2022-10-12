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
    parser.add_argument('-a', '--addlist', type=str,
                        help='set this option if you want to add current target file to the targetlist')
    args = parser.parse_args()
    return args


def conv_a_file(tgt):
    md2html.main(tgt)
    newhistory = str(tgt)
    return newhistory


def conv_a_dir(tgt):
    tgts = list(p(tgt).glob('**/*.md'))
    for i, x in enumerate(tgts):
        print(f'{i}: {x}')

    tgtnum = input('Select a file number. If all, enter "all": ')

    if tgtnum == "all":
        newhistory = str(tgt)
        for x in tgts:
            md2html.main(x)
        return newhistory

    else:
        tgt = tgts[int(tgtnum)]
        md2html.main(tgt)
        newhistory = str(tgt)
        return newhistory


def select_from_history(histories):
    for i, x in enumerate(histories):
        print(f'{i}: {x}')
    tgtnum = input('Select a number: ')
    return str(histories[int(tgtnum)])

# -----------------------------------
if __name__ == "__main__":

    args = argparser()

    history = "./history.json"
    if p(history).is_file():
        with open(history, "r", encoding="utf-8") as f:
            histories = json.load(f)['histories']
    else:
        histories = []

    # -----------------------------------
    if args.list:
        args.tgt = select_from_history(histories)

    if args.tgt:
        tgt = args.tgt

        if p(tgt).is_dir():  # If dir, show list and receive which number to convert.
            newhistory = conv_a_dir(tgt)
        elif p(tgt).is_file():  # If file, convert to html. Expecting markdown.
            newhistory = conv_a_file(tgt)


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
