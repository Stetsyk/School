#!/usr/bin/env python3
"""Короткий опис задач eolymp за номерами: python3 .tools/eo.py 8800 8801 ..."""
import glob, re, sys
for a in sys.argv[1:]:
    g = glob.glob(f'/Users/oleksiistetsyk/Desktop/Eolymp/{int(a):04d} *.md')
    if not g:
        print(f'!! нема {a}'); continue
    s = open(g[0], encoding='utf-8').read()
    f = lambda k: (re.search(rf'^{k}: "?(.*?)"?$', s, re.M) or [None, '?'])[1]
    b = s.split('---\n', 2)[-1]; b = b[b.find('МБ'):]
    b = re.sub(r'^.*\n', '', b, count=1).strip()
    desc = ' '.join(re.split(r'\n## ', b)[0].split())[:130]
    ex = re.findall(r'```\n(.*?)\n```', b, re.S)
    io = ' -> '.join(' '.join(x.split())[:26] for x in ex[:2])
    print(f"{int(a)} [{f('difficulty_label')}] {f('title')} | {desc} | тест: {io}")
