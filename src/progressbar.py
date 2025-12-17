#---------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# Python: 3.11.9
# Author: Killian Nallet
# Date: 04/07/2025
#---------------------------------------------------------------------------------


# imports
import os


# imports
def pbar(progress, total, text="", bar_length=50, show_count=True, bar_chr_ok="=", bar_chr_not_ok=" ",):
    """A progress bar"""
    # calculate percent
    percent = 100 * (progress / float(total))
    _bar = bar_chr_ok*int((bar_length * percent) /100) + bar_chr_not_ok*(bar_length - (int((bar_length * percent) /100)))

    # show element
    count = f" ({progress}/{total})" if show_count else ""
    _text = " "+text if text != "" else " "

    # show bar
    bar = f"[{_bar}] {percent:.1f}%{count}{_text}"
    bar += " " * (os.get_terminal_size()[0] - len(bar))
    print(bar, end="\n" if progress == total else "\r", flush=True)
