# 字帖生成器

```
//解析 hanzi.txt 中的中文字或者词，生成 看拼音写词语字帖
python main.py hanzi.txt
```

或者 

```
//解析 hanzi.txt 中的中文字或者词，生成 看词语写词语练习字帖
python main.py hanzi.txt -s practise
```

## 安装依赖

```
pip install pypinyin
pip install jinja2
```

## 限制

- 程序员奶爸自用，仅仅测试了 macOS；生成html后用浏览器（不支持 macOS 上的 chrome，请安装微软的 Edge浏览器）打印，或者打印的时候另存为 PDF
- Windows上应该是可以直接用的，唯一要注意的就是 你的词语文件的编码 要是 UTF-8。很久不用Windows了，印象里Python在Windows对 GBK的编码支持会有乱码；当然如果你的字帖跑出来是乱码，那多半是编码的问题了。没计划解决Windows上的问题。

## 版权说明

- 依赖第三方开源库 [pypinyin](https://pypinyin.readthedocs.io/zh_CN/master/)，这个库又依赖 [pinyin-data](https://github.com/mozillazg/pinyin-data) 和 [phrase-pinyin-data](https://github.com/mozillazg/phrase-pinyin-data) 能否商用，请遵从原作者的License说明
- 前端打印页面，直接基于[学习巴士](https://www.3415.cn/)的前端压缩过的HTML页面，不能商用，仅限制个人使用，也没有源码。不影响自己本地运行生成字帖。通常情况下，如果你对 多音字 的错误能容忍，建议直接付费学习巴士，不用通过技术的手段解决。本工具之所以诞生，是基于学习巴士的限制：
  - 不解决多音字问题，需要自己肉眼排查，然后修改
  - 作者对解决多音没有排期，故而只能自己撸一套词语转拼音的程序，直接套用了学习巴士的打印前端，本工具只是把 `词语->拼音` 这个过程优化了一下。
  - 感谢学习巴士，作为付费用户会一直支持