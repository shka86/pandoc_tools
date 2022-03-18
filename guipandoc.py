#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path as p

# from matplotlib import container

import md2html

from input_list import *

def guipandoc(root):

    cb_selected = tk.StringVar()

    cb = ttk.Combobox(master=root, values=input_list, textvariable=cb_selected)  # TestCombobox2を生成
    cb.bind('<<ComboboxSelected>>')
    cb.current(0)
    cb.pack(ipadx=10, ipady=10, padx=15, pady=15)

    label = tk.Label(root, textvariable=cb_selected, wraplength=450)
    label.pack()

    btn_convert = tk.Button(master=root, text='convert', command=lambda: md2html.main(cb_selected.get()))
    btn_convert.pack(ipadx=10, ipady=10, padx=15, pady=15)


def button(root):
    btn_convert = tk.Button(master=root, text='btn', command=lambda: print("hello!!"))
    btn_convert.pack(ipadx=10, ipady=10, padx=15, pady=15)


if __name__ == "__main__":

    # main window
    root = tk.Tk()
    root.title("guipandoc")
    root.geometry("500x250")
    nb = ttk.Notebook(root)
    nb.pack(expand=1, fill='both')

    # tabs
    tab_guipandoc = tk.Frame(nb)
    nb.add(tab_guipandoc, text='pandoc')
    guipandoc(tab_guipandoc)

    tab_button = tk.Frame(nb)
    nb.add(tab_button, text='btn')
    button(tab_button)





    # Start App
    root.mainloop()
