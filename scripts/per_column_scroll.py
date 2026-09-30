"""0.5.0 -> 0.5.1 per-column scroll (idempotent-ish; run once)."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'D:\Coding\Rust\agenticapp26\agentic-mail-card\bundle\main.splash'
src = open(P, encoding='utf-8').read()

def rep(old, new, tag):
    global src
    if new in src and old not in src:
        print('skip (done):', tag)
        return
    assert old in src, 'MISSING: ' + tag
    assert src.count(old) == 1, 'NOT UNIQUE: ' + tag
    src = src.replace(old, new)
    print('ok:', tag)

# ---- R1 root body -----------------------------------------------------------
rep('''            body := ScrollYView{width: Fill height: Fill flow: Down padding: Inset{top: 0 bottom: 0 left: 0 right: 0} spacing: 0 on_render: || {
                if screen == "inbox" { inbox_screen() }
                if screen == "write" { write_screen() }
                if screen == "agents" { agents_screen() }
            }}''',
'''            // body is a FIXED viewport area; each pane scrolls itself (the
            // web design's overflow-y-auto columns) — one page scroll made
            // the columns push each other around. The page ground is the
            // first Overlay child here, under every screen.
            body := View{width: Fill height: Fill flow: Overlay on_render: || {
                RoundedView{width: Fill height: Fill draw_bg +: {color: space border_radius: 0.0}}
                if screen == "inbox" { inbox_screen() }
                if screen == "write" { write_screen() }
                if screen == "agents" { agents_screen() }
            }}''', 'root body')

# ---- R2 inbox_screen --------------------------------------------------------
i0 = src.find('fn inbox_screen(){')
i1 = src.find('// Placeholder rail')
assert 0 < i0 < i1
old_inbox = src[i0:i1]

def line_start(s, idx):
    return s.rfind('\n', 0, idx) + 1

a_key = 'View{width: Fill height: Fit flow: Down spacing: 10 padding: Inset{top: 14 bottom: 10 left: 18 right: 18}'
ai = old_inbox.find(a_key)
assert ai > 0
a0 = line_start(old_inbox, ai)

b_key = 'View{width: Fill height: 1 draw_bg +: {color: line border_radius: 0.0}}'
bi = old_inbox.find('for i in mails.len() {')
assert bi > 0
# chunk A ends right before the hairline that precedes the rows block
sep_line = old_inbox.rfind(b_key, 0, bi)
a1 = line_start(old_inbox, sep_line)
chunkA = old_inbox[a0:a1].rstrip() + '\n'

b0 = a1
b_tail = 'View{width: Fill height: 24}'
bti = old_inbox.find(b_tail, b0)
assert bti > 0
b1 = line_start(old_inbox, bti) + len('                View{width: Fill height: 24}\n')
chunkB = old_inbox[b0:b1]

new_inbox = '''fn inbox_screen(){
    // Three independently-scrolling panes on a fixed viewport. Column
    // backgrounds are Overlay underlays so no black shows below shorter
    // content when a pane scrolls.
    View{width: Fill height: Fill flow: Right
        View{width: 360 height: Fill flow: Overlay
            RoundedView{width: Fill height: Fill draw_bg +: {color: panel border_radius: 0.0}}
            ScrollYView{width: Fill height: Fill flow: Down
''' + chunkA + '''                RoundedView{width: Fill height: 1 draw_bg +: {color: line border_radius: 0.0}}
''' + chunkB + '''            }
        }}
        RoundedView{width: 1 height: Fill draw_bg +: {color: line border_radius: 0.0}}
        ScrollYView{width: Fill height: Fill flow: Down
            if selected { reading_pane(current) } else { preview_pane() }
        }
        RoundedView{width: 1 height: Fill draw_bg +: {color: line border_radius: 0.0}}
        View{width: 310 height: Fill flow: Overlay
            RoundedView{width: Fill height: Fill draw_bg +: {color: panel border_radius: 0.0}}
            ScrollYView{width: Fill height: Fill flow: Down
                if selected { copilot_panel(current) } else { copilot_hint() }
            }
        }
    }
}

'''
src = src[:i0] + new_inbox + src[i1:]
print('ok: inbox three panes')

# ---- R3 write head ----------------------------------------------------------
rep('''fn write_screen(){
    RoundedView{width: Fill height: Fit flow: Right draw_bg +: {color: space border_radius: 0.0}
        View{width: Fill height: Fit flow: Down padding: Inset{top: 20 bottom: 28 left: 30 right: 20}''',
'''fn write_screen(){
    View{width: Fill height: Fill flow: Right
        ScrollYView{width: Fill height: Fill flow: Down
        View{width: Fill height: Fit flow: Down padding: Inset{top: 20 bottom: 28 left: 30 right: 20}''',
    'write head')

# ---- R4 rail junction -------------------------------------------------------
rep('''        RoundedView{width: 1 height: Fill draw_bg +: {color: line border_radius: 0.0}}
        RoundedView{width: 340 height: Fit flow: Down draw_bg +: {color: panel border_radius: 0.0}
            View{width: Fill height: 50 flow: Right spacing: 8 align: Align{y: 0.5} padding: Inset{left: 16 right: 14}''',
'''        }
        }
        RoundedView{width: 1 height: Fill draw_bg +: {color: line border_radius: 0.0}}
        View{width: 340 height: Fill flow: Overlay
            RoundedView{width: Fill height: Fill draw_bg +: {color: panel border_radius: 0.0}}
            ScrollYView{width: Fill height: Fill flow: Down
        View{width: Fill height: Fit flow: Down
            View{width: Fill height: 50 flow: Right spacing: 8 align: Align{y: 0.5} padding: Inset{left: 16 right: 14}''',
    'rail junction')

# ---- R5 write tail ----------------------------------------------------------
rep('''                View{width: Fill height: 240}
            }
        }
    }
}''',
'''                View{width: Fill height: 40}
            }
        }
        }
    }
    }
}''', 'write tail')

# ---- R7 draft input height --------------------------------------------------
rep('TextInput{width: Fill height: 120 text: draft_text',
    'TextInput{width: Fill height: 240 text: draft_text', 'draft input')

# ---- R8 agents --------------------------------------------------------------
rep('''fn agents_screen(){
    RoundedView{width: Fill height: Fit flow: Down padding: Inset{top: 20 bottom: 30 left: 28 right: 24} spacing: 16 draw_bg +: {color: space border_radius: 0.0}''',
'''fn agents_screen(){
    ScrollYView{width: Fill height: Fill flow: Down
    View{width: Fill height: Fit flow: Down padding: Inset{top: 20 bottom: 30 left: 28 right: 24} spacing: 16''',
    'agents head')

rep('''                        act_row(i)
                    }
                }
            }
        }
    }
}''',
'''                        act_row(i)
                    }
                }
            }
        }
    }
    }
}''', 'agents tail')

open(P, 'w', encoding='utf-8', newline='').write(src)

d = 0
ok = True
for n, l in enumerate(src.splitlines(), 1):
    if l.startswith('fn ') and d != 0:
        print('FN AT DEPTH', d, 'line', n, l[:50])
        ok = False
    d += l.count('{') - l.count('}')
print('final depth:', d, 'balanced:', d == 0 and ok)
