"""0.4.0 -> 0.5.0 UI rebuild transform (one-shot).

Keeps: state, mails, palette var NAMES, helpers, mail adapter, nav/reply/model
logic. Replaces: palette VALUES, apply_theme, repaint, agent/mail color data,
and the whole UI layer (from "// ---- shared bits" to EOF) with the
forest-ink x warm-paper redesign (build/ui-new.splash).
"""
import re, sys

SRC = r'D:\Coding\Rust\agenticapp26\agentic-mail-card\bundle\main.splash'
UI = r'D:\Coding\Rust\agenticapp26\agentic-mail-card\build\ui-new.splash'

src = open(SRC, encoding='utf-8').read()

# ---- 1. cut at the shared-bits marker --------------------------------------
marker = '// ---- shared bits ---'
idx = src.find(marker)
assert idx > 0, 'marker not found'
head = src[:idx]

# ---- 2. palette lets --------------------------------------------------------
old_palette_start = head.find('// ---- deep-space palette')
old_palette_end = head.find('// ---- dual theme')
assert 0 < old_palette_start < old_palette_end
new_palette = '''// ---- forest-ink x warm-paper palette ---------------------------------------
// Token names follow the history of this file (violet:=accent green,
// cyan:=teal, mint:=ok green); values come from the UI design's index.css
// (light :root / dark [data-theme]), alpha pre-blended on each theme's ground.
let space    = #x161c1a      // page ground (bg)
let panel    = #x1d2622      // panels / sidebar
let panel2   = #x222c27      // raised panel
let glass    = #x1a211e      // top bar
let line     = #x292e2c      // hairline
let line2    = #x454945      // stronger hairline
let ink      = #xebe9de      // primary text
let ink66    = #x92938c
let ink55    = #x7a7c76
let ink45    = #x6b6e68
let ink38    = #x636661
let ink32    = #x565955
let violet   = #x8fcb9b      // acc
let accB     = #x6fb585      // acc-b (gradient second stop)
let violetT  = #xa8dbb2      // acc-text
let violetBg = #x25312a      // acc-soft (pre-blended)
let violetBgHv = #x2e3f34
let violetBd = #x445f4b      // acc-line
let violetHi = #xa8dbb2
let cyan     = #x5ec4b6      // teal
let cyanT    = #x8adccf
let cyanBg   = #x1f302d
let cyanBd   = #x305952
let mint     = #x7fcf96      // ok
let mintT    = #x9adcaa
let mintBg   = #x233129
let mintBd   = #x3c5c47
let amber    = #xe0a458
let amberT   = #xeab873
let amberBg  = #x2e2c22
let amberBd  = #x635032
let red      = #xe0785f
let redT     = #xea927b
let redBg    = #x2e2722
let redBd    = #x674136
let white7   = #x28332e      // panel-3 (tracks / hovers)
let inkHi    = #xebe9de      // near-primary text
let inkBody  = #xc0c0b7      // body paragraphs
let violet2  = #x6b6e68      // low-priority meter
let badgeInk = #x14201a      // text on accent badges
let inputBg  = #x222c27
let railPill   = #x25312a
let railPillBd = #x445f4b
let railTile   = #x28332e
let railDiv    = #x292e2c
let sepC     = #x292e2c      // sidebar / topbar hairline
let glowA    = #x212c26      // ambient blobs
let glowB    = #x22241e
let glowC    = #x1b2825
let accInk   = #x14201a      // text on accent gradients

'''
head = head[:old_palette_start] + new_palette + head[old_palette_end:]

# ---- 3. apply_theme ---------------------------------------------------------
at_start = head.find('fn apply_theme(l){')
at_end = head.find('fn toggle_theme(){')
assert 0 < at_start < at_end
new_apply = '''fn apply_theme(l){
    themeLight = l
    space     = pick(l, #xf3f1e6, #x161c1a)
    panel     = pick(l, #xfaf8ef, #x1d2622)
    panel2    = pick(l, #xefede0, #x222c27)
    glass     = pick(l, #xf7f5ec, #x1a211e)
    line      = pick(l, #xdeddd2, #x292e2c)
    line2     = pick(l, #xc0c1b8, #x454945)
    ink       = pick(l, #x1f2926, #xebe9de)
    ink66     = pick(l, #x747973, #x92938c)
    ink55     = pick(l, #x898d86, #x7a7c76)
    ink45     = pick(l, #x9a9d95, #x6b6e68)
    ink38     = pick(l, #xa3a59d, #x636661)
    ink32     = pick(l, #xb3b5ac, #x565955)
    violet    = pick(l, #x2f5d43, #x8fcb9b)
    accB      = pick(l, #x3e7355, #x6fb585)
    violetT   = pick(l, #x2f5d43, #xa8dbb2)
    violetBg  = pick(l, #xdfe2d6, #x25312a)
    violetBgHv = pick(l, #xd4d9cc, #x2e3f34)
    violetBd  = pick(l, #xb0bfaf, #x445f4b)
    violetHi  = pick(l, #x2f5d43, #xa8dbb2)
    cyan      = pick(l, #x0f5a52, #x5ec4b6)
    cyanT     = pick(l, #x0c4f4a, #x8adccf)
    cyanBg    = pick(l, #xdce2d7, #x1f302d)
    cyanBd    = pick(l, #xaac1b7, #x305952)
    mint      = pick(l, #x2f7d4f, #x7fcf96)
    mintT     = pick(l, #x276a43, #x9adcaa)
    mintBg    = pick(l, #xdbe3d4, #x233129)
    mintBd    = pick(l, #xb0cab3, #x3c5c47)
    amber     = pick(l, #xb06f1f, #xe0a458)
    amberT    = pick(l, #x96601b, #xeab873)
    amberBg   = pick(l, #xece4d2, #x2e2c22)
    amberBd   = pick(l, #xdcc5a2, #x635032)
    red       = pick(l, #xbe4b38, #xe0785f)
    redT      = pick(l, #xa03d2c, #xea927b)
    redBg     = pick(l, #xeee0d5, #x2e2722)
    redBd     = pick(l, #xe0b5a7, #x674136)
    white7    = pick(l, #xe6e3d4, #x28332e)
    inkHi     = pick(l, #x1f2926, #xebe9de)
    inkBody   = pick(l, #x49514c, #xc0c0b7)
    violet2   = pick(l, #x9a9d95, #x6b6e68)
    badgeInk  = pick(l, #xf3f1e6, #x14201a)
    inputBg   = pick(l, #xefede0, #x222c27)
    railPill   = pick(l, #xdfe2d6, #x25312a)
    railPillBd = pick(l, #xb0bfaf, #x445f4b)
    railTile   = pick(l, #xe6e3d4, #x28332e)
    railDiv    = pick(l, #xdeddd2, #x292e2c)
    sepC      = pick(l, #xdeddd2, #x292e2c)
    glowA     = pick(l, #xdbdfd2, #x212c26)
    glowB     = pick(l, #xece4d2, #x22241e)
    glowC     = pick(l, #xdce2d7, #x1b2825)
    accInk    = pick(l, #xf3f1e6, #x14201a)
}
'''
head = head[:at_start] + new_apply + head[at_end:]

# ---- 4. repaint: four persistent roots --------------------------------------
rp_start = head.find('fn repaint(){')
rp_end = head.find('// ---- helpers')
assert 0 < rp_start < rp_end
new_repaint = '''fn repaint(){
    ui.railc.render()
    ui.barc.render()
    ui.body.render()
}

'''
head = head[:rp_start] + new_repaint + head[rp_end:]

# ---- 5. avatar pairs (warm palette from bits.tsx) ---------------------------
AV = {
    'priority: 94 cluster: "工作"': ('#x3e7355', '#x1f3a2a'),      # m1 林
    'priority: 61 cluster: "订阅"': ('#x0f5a52', '#x0a3e42'),      # m2 V
    'priority: 88 cluster: "工作"': ('#xbe4b38', '#x6e2418'),      # m3 陈
    'priority: 55 cluster: "财务"': ('#x488b5f', '#x24462f'),      # m4 Stripe
    'priority: 72 cluster: "工作"': ('#x7a6c3f', '#x3e3820'),      # m5 GitHub
    'priority: 90 cluster: "社交"': ('#xb06f1f', '#x6b4210'),      # m6 妈妈
    'priority: 28 cluster: "订阅"': ('#xb06f1f', '#x6b4210'),      # m7 AWS
    'priority: 40 cluster: "工作"': ('#x488b5f', '#x24462f'),      # m8 沈括
}
for ctx, (a, b) in AV.items():
    pat = re.compile(re.escape(ctx) + r'\n     av1: #x[0-9a-f]{6} av2: #x[0-9a-f]{6}')
    head, n = pat.subn(ctx + '\n     av1: ' + a + ' av2: ' + b, head)
    assert n == 1, f'avatar ctx not unique: {ctx} ({n})'

# live_mail default avatar
head = head.replace('av1: #x8642ff av2: #x4c1d95\n            labels:',
                    'av1: #x3e7355 av2: #x1f3a2a\n            labels:')
assert 'av1: #x8642ff' not in head

# ---- 6. agent color keys ------------------------------------------------------
head = head.replace('color: #x8642ff on: true glyph: "卫"', 'color: "acc" on: true glyph: "卫"')
head = head.replace('color: #x22d3ee on: true glyph: "管"', 'color: "teal" on: true glyph: "管"')
head = head.replace('color: #x34d399 on: true glyph: "清"', 'color: "ok" on: true glyph: "清"')
head = head.replace('color: #xfbbf24 on: false glyph: "报"', 'color: "amber" on: false glyph: "报"')
assert 'color: "acc" on: true' in head and 'color: "amber" on: false' in head

# ---- 7. View does not paint draw_bg on this stack — RoundedView does -------
# (probed: inline or fn-minted, plain View bgs are silently skipped)
ui = open(UI, encoding='utf-8').read()
RV = [
    ('View{width: 264 height: Fill flow: Down draw_bg.color: panel',
     'RoundedView{width: 264 height: Fill flow: Down draw_bg +: {color: panel border_radius: 0.0}'),
    ('View{width: Fill height: 58 flow: Right spacing: 12 align: Align{y: 0.5} padding: Inset{left: 20 right: 16} draw_bg.color: glass',
     'RoundedView{width: Fill height: 58 flow: Right spacing: 12 align: Align{y: 0.5} padding: Inset{left: 20 right: 16} draw_bg +: {color: glass border_radius: 0.0}'),
    ('View{width: 360 height: Fit flow: Down draw_bg.color: panel',
     'RoundedView{width: 360 height: Fit flow: Down draw_bg +: {color: panel border_radius: 0.0}'),
    ('View{width: 310 height: Fit flow: Down draw_bg.color: panel',
     'RoundedView{width: 310 height: Fit flow: Down draw_bg +: {color: panel border_radius: 0.0}'),
    ('View{width: 1 height: Fill draw_bg.color: line}',
     'RoundedView{width: 1 height: Fill draw_bg +: {color: line border_radius: 0.0}}'),
    ('View{width: 1 height: Fit draw_bg.color: line}',
     'RoundedView{width: 1 height: Fit draw_bg +: {color: line border_radius: 0.0}}'),
    ('View{width: Fill height: 1 draw_bg.color: line}',
     'RoundedView{width: Fill height: 1 draw_bg +: {color: line border_radius: 0.0}}'),
    ('View{width: Fill height: 1 draw_bg.color: sepC}',
     'RoundedView{width: Fill height: 1 draw_bg +: {color: sepC border_radius: 0.0}}'),
    ('View{width: 1 height: Fill draw_bg.color: sepC}',
     'RoundedView{width: 1 height: Fill draw_bg +: {color: sepC border_radius: 0.0}}'),
    ('View{width: Fill height: Fit flow: Right spacing: 7 align: Align{y: 0.5} padding: Inset{top: 8 bottom: 8 left: 14 right: 14} draw_bg.color: violetBg',
     'RoundedView{width: Fill height: Fit flow: Right spacing: 7 align: Align{y: 0.5} padding: Inset{top: 8 bottom: 8 left: 14 right: 14} draw_bg +: {color: violetBg border_radius: 0.0}'),
    ('View{width: 1 height: 14 draw_bg.color: line2}',
     'RoundedView{width: 1 height: 14 draw_bg +: {color: line2 border_radius: 0.0}}'),
    ('View{width: Fill height: Fit flow: Down padding: Inset{top: 12 bottom: 12 left: 18 right: 18} spacing: 4\n                draw_bg +: {color: pick(sel, violetBg, #x00000000)}',
     'RoundedView{width: Fill height: Fit flow: Down padding: Inset{top: 12 bottom: 12 left: 18 right: 18} spacing: 4\n                draw_bg +: {color: pick(sel, violetBg, #x00000000) border_radius: 0.0}'),
    ('View{width: 340 height: Fit flow: Down draw_bg.color: panel',
     'RoundedView{width: 340 height: Fit flow: Down draw_bg +: {color: panel border_radius: 0.0}'),
]
for a, b in RV:
    n = ui.count(a)
    if n == 0:
        print(f'skip (absent): {a[:52]}')
        continue
    ui = ui.replace(a, b)
    print(f'{n}x {a[:52]}')

out = head + ui
open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('written', len(out), 'bytes,', out.count('\n'), 'lines')
