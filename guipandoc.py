#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path as p

import md2html


class TestCombobox2(ttk.Combobox):
    def __init__(self, choice, master=None):  # var(StringVar)を追加
        super().__init__(master=master, values=choice)
        self.selected = self.get()
        self.bind('<<ComboboxSelected>>', self.when_selected)

    def when_selected(self, event):  # event引数は必要
        self.selected = self.get()


if __name__ == "__main__":
    root = tk.Tk()

    # StringVarとラベルの生成
    var = tk.StringVar(root)
    # l = tk.Label(
    #     textvariable=var,  # textvariableオプションにStringVarをセット
    #     master=root
    # )
    # l.pack()

    choices = [
        p(r"./mdsample/test.md"),
        p(r"./mdsample/test2.md"),
        p(r"./mdsample/test3.md")
    ]
    c = TestCombobox2(master=root, choice=choices)  # TestCombobox2を生成
    c.pack()

    print(c.selected)
    print(c.get())

    # button
    entity = tk.Button(master=root, text='convert', command=lambda: md2html.main(c.selected))
    entity.pack()

    root.mainloop()
