#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pypinyin import pinyin, lazy_pinyin, Style,load_phrases_dict

def readHanz():
    with open('./qingsheng.txt') as f:
        for line in f.readlines():
            line = line.strip()
            for h in line.split(" "):
                yield h

def main():
    with open('qs-py.txt', 'w') as fout:
        for w in readHanz():
            w.strip()
            if len(w) > 0:
                py = lazy_pinyin(w, style=Style.TONE)
                
                fout.write("{}:{}".format(w, " ".join(py)))
                fout.write("\n")

if __name__ == '__main__':
    main()
