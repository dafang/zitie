#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import os

from pypinyin import pinyin, lazy_pinyin, Style, load_phrases_dict
from jinja2 import Template, Environment, FileSystemLoader


def printMsg(message=''):
    print(message)


def testArgs(args):
    inputHanziFile = args.infile
    if not os.path.isfile(inputHanziFile):
        printMsg(
            "输入的词语文件不存在，请用全路径，或者相对于当前程序的相对路径。运行是通过参数指定，如：python main.py ci.txt")
        sys.exit()


def readHanz(fromFile):
    with open(fromFile) as f:
        for line in f.readlines():
            if line.startswith('#'):
                title = line.strip()
                yield title
            else:
                line = line.strip()
                for h in line.split(" "):
                    yield h


def loadPhrasesDict():
    # qs-py.txt 是通过 qingsheng.py 生成的轻声词列表；需要增加或者修订轻声拼音，直接修改qs-py.txt即可
    with open('./pinyin-dict/qs-py.txt') as f:
        for line in f.readlines():
            hzPyList = line.split(':')
            hz = hzPyList[0]  # 眼睛
            py = [[p] for p in hzPyList[1].strip().split(' ')]
            load_phrases_dict({hz: py})


def genTest(phrasesStream):
    # 内部函数，处理是否换行的逻辑，懒的抽象成class了
    def startNewline(line=[], nextWord=[]):
        # line = [['liǎng', 'jí'], ['liǎng', 'páng']]
        lineWidth = 180  # 单位mm，每行最宽180mm
        hzWidth = 15  # 单位mm，每个汉字的格子宽15mm
        margin = 2.8  # 单位mm，词于词之间空2.8mm

        pyCnt = len(line)
        totalMargin = (pyCnt - 1) * margin  # 一行里，margin 占多宽

        lw = totalMargin
        for w in line:
            lw = lw + len(w) * hzWidth  # 词之间的间距宽，加上所有词的格子宽，就是一行的总宽度

        # 预测能不能再加入一个词，如果加入一个词就超了，则该换行了
        curWidth = lw + len(nextWord) * hzWidth + margin

        if curWidth >= lineWidth:
            return True
        else:
            return False

    def pageAppend(title='', pages=[], lines=[], cur=0):

        # 每页最多10行，超了的放到下一页
        pages.append({"title": title, "lines": lines[0:10], "cur": cur})

        return pages, lines[10:]

    # hard code, 勿改
    env = Environment(loader=FileSystemLoader('./html/'))

    tpl = env.get_template("test.html")
    maxLines = 10  # 每页10行

    # pages = [
    #     {"title":"小蝌蚪找妈妈", "lines":[[['liǎng', 'jí'], ['liǎng', 'páng']],[['liǎng', 'shǒu', 'kōng', 'kōng'], ['liǎng', 'páng']]],
    #     "cur":1},
    #     {"title":"植物妈妈有办法", "lines":[[['liǎng', 'jí'], ['liǎng', 'páng']],[['liǎng', 'shǒu', 'kōng', 'kōng'], ['liǎng', 'páng']]],
    #     "cur":1}
    # ]
    pages = []
    title = ''
    lines = []
    line = []

    linesCnt = 0
    curPage = 0
    for h in phrasesStream:
        if h.startswith('#'):
            if curPage > 0:  # the seconde page now；读到标题就换一个新页面，避免同一个页面出现两个标题
                # start a new page
                if len(line) > 0:  # 要换页了，当前行放进当前页中
                    lines.append(line)

                # lines 用于下一页
                curPage = curPage + 1
                pages, lines = pageAppend(title, pages, lines, curPage)

                # 换新页了，临时变量复原
                line = []
                linesCnt = 0

            title = h.strip('#')
        else:
            py = lazy_pinyin(h, style=Style.TONE)

            if startNewline(line, py):  # 当前行放不下py了，换行
                linesCnt = linesCnt + 1
                lines.append(line)

                line = [py]
            else:
                line.append(py)

            if linesCnt > maxLines:
                # start new page
                curPage = curPage + 1
                pages, lines = pageAppend(title, pages, lines, curPage)

                # 换页
                linesCnt = 0

    # 上面的for循环，没把最后一行line放进去，这里补充进来
    if len(line) > 0:
        lines.append(line)
    pages.append({"title": title, "lines": lines,
                  "cur": curPage+1})  # last page

    with open('test.html', 'w') as fout:
        render_content = tpl.render(pages=pages, total_page=len(pages))
        fout.write(render_content)


def genPractise(phrasesStream):
    def startNewline(line=[], nextWord=[]):
        if len(line) == 0:
            return False

        lineLen = len(line)
        nextWordLen = len(nextWordLen)

        if lineLen + nextWordLen >= 12:  # 一行最多12个格子
            return True

        return False

    # 返回当前行，以及如果当前行超过12个格子，返回需要append到下一行的词list
    # list 的数据格式如下，py或者hz为空则表示是个空田字格，用于书写：
    # line = [{"py": 'shén', "hz":'什'}, {"py": 'me', "hz":'么'},{"py":'',"hz":''}]
    def lineAppend(line=[], py=[], h=''):
        cc = len(py)

        if cc <= 0:  # 当前行为空
            return line, []

        for i, c in enumerate(py):
            hz = ''
            if len(h) > i:
                hz = h[i]
            line.append({"py": c, "hz": hz})

        # 每个词，加两遍空格，用于练习；也就是一个 汉字词组，写两遍
        for i in range(cc * 2):
            line.append({"py": '', "hz": ''})  # 用于空格子

        return line[0:12], line[12:]

    # 增加一页，如果当前页的行数少于11行，则用空行填补；pages 的数据机构如下：
    # pages = [
    #     {"title":"小蝌蚪找妈妈", "lines":[[{'py':'','hz':''},{'py':'','hz':''}],[{'py':'','hz':''},{'py':'','hz':''}]],
    #     "cur":1},
    #     {"title":"植物妈妈有办法", "lines":[[{'py':'','hz':''},{'py':'','hz':''}],[{'py':'','hz':''},{'py':'','hz':''}]],
    #     "cur":2}
    # ]
    # page 表示一页内容
    def pageAppend(title='', pages=[], lines=[], cur=0):
        lineLen = len(lines)
        if lineLen < 11:  # 一页最多11行
            needAppendLine = 11 - lineLen
            line = []

            # 如果1页少于11行，则少的部分用空田字格代替
            for i in range(needAppendLine):
                line, nouse = lineAppend(line, ['' for i in range(12)], '')
                lines.append(line)
                line = []

        pages.append({"title": title, "lines": lines[0:11], "cur": cur})

        return pages, lines[11:]

    env = Environment(loader=FileSystemLoader('./html/'))
    tpl = env.get_template('practise.html')

    maxLines = 11

    # object {'title':'', 'lines':[[{'py':'','hz':''},{'py':'','hz':''}]], 'cur':1} 的list
    pages = []
    title = ''  # 当前页上的标题
    lines = []  # 临时保持当前页的行数据
    line = []  # 某一行结构，[{'py':'','hz':''},{'py':'','hz':''}]，py表示拼音，hz表示对应的汉字

    linesCnt = 0
    curPage = 0
    for h in phrasesStream:  # 循环每一个词
        if h.startswith('#'):  # 标题行
            if curPage > 0:  # the seconde page now；读到标题就换一个新页面，避免同一个页面出现两个标题
                # start a new page
                if len(line) > 0:
                    # 由于读到了 标题，要新开一页，所以当前line不会再有词语进来，用空个字把当前行补充完，然后塞到当前页中去
                    line, _ = lineAppend(line, ['' for _ in range(12)], '')
                    lines.append(line)
                curPage = curPage + 1  # 翻页了

                pages, lines = pageAppend(title, pages, lines, curPage)

                # 重置临时变量，因为保存的是当前页的信息，换页了清空
                line = []
                linesCnt = 0

            title = h.strip('#')
        else:
            # 词语转拼音
            py = lazy_pinyin(h, style=Style.TONE)

            line, nextLineBuffer = lineAppend(line, py, h)
            if len(nextLineBuffer) > 0:  # 当前行超过了12个格子
                linesCnt = linesCnt + 1  # 换行了，行数增加
                lines.append(line)

                line = nextLineBuffer

            # 当前页满11行了...
            if linesCnt > maxLines:
                # start new page
                curPage = curPage + 1
                pages, lines = pageAppend(title, pages, lines, curPage)

                line = nextLineBuffer[0:]  # 把前一页多出来的行用于下一页
                nextLineBuffer = []
                linesCnt = 0

    if len(line) > 0:
        line, nouse = lineAppend(line, ['' for _ in range(12)], '')
        lines.append(line)
    pages, lines = pageAppend(title, pages, lines, curPage+1)
    if len(lines) > 0:  # 最后超了...
        pages, lines = pageAppend(title, pages, lines, curPage+2)

    with open('practise.html', 'w') as fout:
        render_content = tpl.render(pages=pages, total_page=len(pages))
        fout.write(render_content)


stylesImpl = {'test': genTest, 'practise': genPractise}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', "--example",
                        action="store_true", help="输入词列表的例子，供参考")
    parser.add_argument("-s", "--style", type=str, choices=['test', 'practise'], default="test",
                        help="字体的风格，看拼音写汉字，输入 -s test 做抄写练习，输入 -s practise")
    parser.add_argument(
        'infile', help="汉字或者词语的列表文件，如果需要查看文件格式，制定 - e 或者 - -example 参数查看输出的内容")
    args = parser.parse_args()

    if args.example:
        sample = '''参考中横线以下的内容，其中：
# 后面的为词语的分组；汉字 或者 词语 之间用 空格 分隔
----------------------------------------------
# 小蝌蚪找妈妈
眼睛 看见 那里 蝌蚪 妈妈
千里挑一 开开心心'''
        printMsg(sample)
        sys.exit()

    testArgs(args)

    printMsg('拼音轻声词库初始化中，稍等...')
    loadPhrasesDict()
    printMsg('初始化完毕，开始工作...')

    if args.style in stylesImpl:
        stylesImpl[args.style](readHanz(args.infile))
    else:
        printMsg('暂时不支持的字帖类型，仅支持 test or practice。')
        sys.exit()

    printMsg(
        "生成完毕，请(用IE浏览器或者微信的Edge浏览器)打开当前目录下的{}.html 进行打印或者另存为pdf后打印。".format(args.style))


if __name__ == '__main__':
    main()
