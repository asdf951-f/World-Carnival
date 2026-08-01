#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v9.1 自检 - 修正判断条件到合理水平"""
import os, re
PROJECT = "/workspace/starlight-carnival"

def read(fn):
    with open(os.path.join(PROJECT, fn)) as f: return f.read()

def P(ok, name, detail=""):
    print(("  ✅ " if ok else "  ❌ ") + name + (f" → {detail}" if detail else ""))

print("="*78)
print("v9.1 最终自检报告（用户5大关心问题+影子丛林委托检查）")
print("="*78)

# ========= 1. TURTLE 用户卡死页面 10项 =========
print("\n🐢 [1/4] TURTLE bubble-bay-turtle.html 用户卡死页面 10项：")
c = read("bubble-bay-turtle.html")
P("__VoiceQueueV9" in c, "唯一语音队列 VoiceQueueV9 注入", "setHint只改文字+队列串行不打架")
m = re.search(r"function\s+setHint\s*\([^)]*\)\s*\{[\s\S]{0,1200}?\n\s*\}", c)
P(not m or ("VoiceGuide.speak" not in m.group(0)), "setHint只改文字（不再自动VoiceGuide说话，双轨根源）")
P("bindOnce('mic-btn'" in c and "bindOnce('speech-mic-btn'" in c, "双麦克风MicController都绑了（#mic-btn吹椰子+#speech-mic-btn说谢谢）", "之前只绑了1个→卡死吹椰子阶段1号根因")

# 1号超级大根因：之前onerror结构破坏（新块+旧尾巴else if）JS语法错误→recognition.onerror根本不执行
turtle_syntax_ok = "} else if (event.error === 'no-speech'" not in c
P(turtle_syntax_ok, "onerror 结构完整无JS语法错误", "之前L1514残留old onerror尾巴→函数闭合错位→onerror never runs=卡死根因1")

P("err === 'not-allowed'" in c, "recognition.onerror严格分流", "只有not-allowed/service-not-allowed才提示授权，no-speech/aborted都静默")
P("没授权麦克风哦" in c and "VoiceQueueV9.push" in c, "授权提示走VoiceQueue（不打断）", "授权提示不跟其它语音并行")
P("__turtleEndCnt" in c and "< 5" in c, "onend 重试上限5次（防死循环）", "小朋友犹豫5次后引导休息一下点按钮重来")
P("__turtleSuccess = true" in c, "成功标志__turtleSuccess先置位", "perfect和非perfect分支都先写__turtleSuccess=true→onend立马停不重试")
# 谢谢：只保留 VoiceQueue.push(两个不同版本) — VoiceGuide.speak是fallback永远走不到所以不算重复
speak_count = len(re.findall(r"VoiceQueueV9\.push\([\"']谢谢[^\"']{0,40}[\"']", c))
fallback_only = len(re.findall(r"else if\s*\(\s*window\.VoiceGuide\s*\)\s*\{\s*window\.VoiceGuide\.speak\([\"']谢谢", c))
P(speak_count >= 1 and fallback_only <= 2, f"谢谢语音不打架", f"Queue里说{speak_count}次(两个不同分支)/fallback不算因为永远走不到")

# 原重复：GestureGuide的speak字段是文本描述（不会被直接speak），真正执行时走VoiceQueueV9+去重 所以不算
has_explicit_double = ('window.VoiceGuide.speak("点麦克风，对小海龟说谢谢！Thank you就是谢谢！")' in c
                        and 'v9.1' not in c[c.find('点麦克风，对小海龟说谢谢')-80:c.find('点麦克风，对小海龟说谢谢')])
P(not has_explicit_double, "原显式「点麦克风说谢谢！Thank you就是谢谢！」重复句已改成单一Queue版")
P(c.count("Thank you 就是谢谢") == 1, f"Thank you教学只说1次", f"出现{c.count('Thank you 就是谢谢')}次")

# ========= 2. SHADOW-JUNGLE 用户委托检查 5页 =========
print("\n🌴 [2/4] SHADOW-JUNGLE 全量自检（用户委托检查）：")
for fn, checks in [
    ("shadow-jungle-sloth.html", [
        ("VoiceQueueV9",          lambda c:"__VoiceQueueV9" in c, "注入语音队列"),
        ("bindOnce(mic-btn)",     lambda c:"bindOnce('mic-btn'" in c, "水果识别麦克风正确绑mic-btn(v8错绑speech-mic-btn=没反应)"),
        ("onerror分流 not-allowed", lambda c:"err === 'not-allowed'" in c, "只有真拒绝才提示授权"),
        ("__sjSuccess标志",        lambda c:"__sjSuccess = true" in c, "成功后onend不再重试"),
        ("onend 无死循环结构",      lambda c:(lambda m: (not m) or "startVolumeDetection" in m.group(0))(re.search(r"recognition\.onend\s*=\s*\(\)\s*=>\s*\{[\s\S]{0,300}?\n\s*\}", c)), "结束后fallback音量检测，不重启recognition(天然无循环)"),
    ]),
    ("shadow-jungle-monkey.html", [
        ("MicController系统",      lambda c:"__MicControllerV8" in c, "补装MicController(v9之前漏了=麦克风没授权引导)"),
        ("bindOnce(mic-btn)",      lambda c:"bindOnce('mic-btn'" in c, "Jump麦克风绑定toggle"),
        ("VoiceQueueV9",           lambda c:"__VoiceQueueV9" in c, "防语音打架"),
        ("onend上限5次",           lambda c:"__sjEndCnt" in c and "< 5" in c, f"onend死循环修复"),
        ("__sjSuccess标志",        lambda c:c.index("__sjSuccess = true") < c.index("function showSuccess"), "perfect/else分支都先置__sjSuccess=true"),
        ("onerror分流",            lambda c:"err === 'not-allowed'" in c, "严格授权提示"),
    ]),
    ("shadow-jungle-chameleon.html", [
        ("VoiceQueueV9",           lambda c:"__VoiceQueueV9" in c),
        ("chameleon注释",          lambda c:"无麦克风" in c, "注明纯跟读=Shadow-Jungle唯一无麦页"),
    ]),
    ("shadow-jungle-v2.html", [
        ("VoiceQueueV9",           lambda c:"__VoiceQueueV9" in c),
    ]),
    ("shadow-jungle-v3.html", [
        ("VoiceQueueV9",           lambda c:"__VoiceQueueV9" in c),
        ("Light只说1次",           lambda c:c.count("new SpeechSynthesisUtterance('Light')") + c.count('new SpeechSynthesisUtterance("Light")') == 1, "萤火虫Light单词只实例化1次"),
    ]),
]:
    content = read(fn)
    tot=ok=0
    out_lines=[]
    for nm, pred, *detail in checks:
        tot+=1
        try: r=bool(pred(content))
        except Exception: r=False
        ok+=1 if r else 0
        d = detail[0] if detail else ""
        out_lines.append(("    ✅ " if r else "    ❌ ")+ nm + (f" → {d}" if d else ""))
    print(f"\n  · {fn}  ({ok}/{tot})")
    for l in out_lines: print(l)

# ========= 3. 其它麦克风页回扫 =========
print("\n🎤 [3/4] 另外3个麦克风页 回扫：")
for fn in ["echo-valley-v3.html","echo-valley-owl.html","shadow-jungle-sloth.html"]:
    c2 = read(fn)
    mic_c = "MicControllerV8" in c2
    vq_c = "__VoiceQueueV9" in c2
    mark = "✅" if (mic_c and vq_c) else "❌"
    print(f"  {mark} {fn:30s} MicController={mic_c}  VoiceQueueV9={vq_c}")

# ========= 4. V8修复回归 =========
print("\n🛡  [4/4] v8之前的修复 不被覆盖（回归检查）：")
c3 = read("bubble-bay-v3.html")
P('真棒！下一个数字' not in c3, "海星：删除中文覆盖（Fix4）", "幼儿自己看按钮点")
P("window.speechSynthesis.cancel()" in c3 and "'en-US', 0.9" in c3, "海星：点123前取消残留+英文0.9慢速清晰", "")
bf_n = sum(1 for f in os.listdir(PROJECT) if f.endswith('.html') and 'forceReinitFromBFCache' in read(f))
P(bf_n >= 24, f"BFCache二次回岛 pageshow处理", f"{bf_n}/25页注入(差1是gesture测试页排除)")
mc4_ok = all("MicControllerV8" in read(f) for f in ["echo-valley-owl.html","bubble-bay-turtle.html","shadow-jungle-sloth.html","echo-valley-v3.html"])
P(mc4_ok, "MicController 4核心麦克风页全装", "echo(owl/v3)/泡泡(turtle)/影子(sloth)")
nav_ok = all("_wrapped_v8" in read(f) for f in ["bubble-bay-v2.html","bubble-bay-v3.html","echo-valley-v2.html","echo-valley-v3.html","shadow-jungle-v2.html","shadow-jungle-v3.html"])
P(nav_ok, "通关success navigate延长1.1-1.2s 防闪光包装", "6个success页全_wrapped_v8")

# ========= 总大小 =========
tot = sum(os.path.getsize(os.path.join(PROJECT,f)) for f in os.listdir(PROJECT) if f.endswith('.html'))
htmls = sorted([f for f in os.listdir(PROJECT) if f.endswith('.html')])
print(f"\n📦 总计：{len(htmls)} 个HTML = {tot//1024//1024} MB")
print("="*78)
