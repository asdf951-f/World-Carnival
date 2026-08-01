#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os
backup="/tmp/backup_v7"
current="/workspace/starlight-carnival"

print("="*70)
print("V9.2 紧急修复自检：<body>闭合+首页按钮DOM")
print("="*70)

fns = sorted([f for f in os.listdir(current) if f.endswith('.html')])
fail = 0
for fn in fns:
    with open(os.path.join(current, fn), errors='replace') as f: c = f.read()
    m = re.search(r'<body\b([^>]*)>', c, re.I)
    if not m:
        print(f"❌ {fn:30s} 找不到<body>"); fail+=1; continue
    attr = m.group(1)
    naked = re.findall(r':\s*url\(\s*data:image[^)]*\)', attr)
    if naked: 
        print(f"❌ {fn:30s} body里还有{naked}没加引号")
        fail+=1
print(f"\n✅ body闭合自检 {len(fns)-fail}/{len(fns)} 通过")

print("\n🏠 首页/地图/故事书 结构完整性：")
with open(os.path.join(current,'index.html'), errors='replace') as f: idx = f.read()
# 按钮在<main>内部
mm_s = [m.start() for m in re.finditer(r'<main\b', idx, re.I)]
mm_e = [m.start() for m in re.finditer(r'</main>', idx, re.I)]
ok = False
if mm_s and mm_e:
    ms, me = mm_s[0], mm_e[-1]
    mb = re.search(r'<button\s+[^>]*data-dom-id\s*=\s*"cta-start-adventure"', idx, re.I)
    ok = bool(mb and ms < mb.start() < me)
print(f"  index.html: cta按钮在<main>里? {'✅' if ok else '❌'}")

with open(os.path.join(current,'story-book.html'), errors='replace') as f: stb = f.read()
ni = len(re.findall(r'泡泡湾|回声谷|影子丛林', stb))
hwm = ('world-map-v2.html' in stb) or ('home-v2.html' in stb)
print(f"  story-book.html: 三岛提及={ni} 跳转链接={'✅' if hwm else '❌'}")

with open(os.path.join(current,'world-map-v2.html'), errors='replace') as f: wm = f.read()
nc = len(re.findall(r'window\.location\.href\s*=|addEventListener\s*\(\s*[\'\"]click', wm))
print(f"  world-map-v2.html: 点击跳转={nc}处 {'✅' if nc>=3 else '⚠️可能不足'}")

print("\n🐢 海龟/猴子 v9.1修复保留：")
with open(os.path.join(current,'bubble-bay-turtle.html'), errors='replace') as f: turt = f.read()
a = '__VoiceQueueV9' in turt
b = "err === 'not-allowed'" in turt
c = '__turtleEndCnt' in turt
d = "bindOnce('mic-btn'" in turt and "bindOnce('speech-mic-btn'" in turt
print(f"  🐢 Turtle: VoiceQueue={'✅'if a else '❌'} onerror分流={'✅'if b else '❌'} onend上限5次={'✅'if c else '❌'} 双麦双绑={'✅'if d else '❌'}")

with open(os.path.join(current,'shadow-jungle-monkey.html'), errors='replace') as f: mnk = f.read()
a2 = '__MicControllerV8' in mnk
b2 = "bindOnce('mic-btn'" in mnk
c2 = '__sjEndCnt' in mnk
print(f"  🐵 Monkey: MicController={'✅'if a2 else '❌'} bindOnce={'✅'if b2 else '❌'} onend上限5次={'✅'if c2 else '❌'}")
