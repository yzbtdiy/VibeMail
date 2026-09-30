"""0.5.2: replace text glyphs (日/月 knob, 历/设 footer) with native-widget
icons — runtime SVG rasterises blank on this stack, so icons are composed
from RoundedViews (same shapes as the lucide references)."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'D:\Coding\Rust\agenticapp26\agentic-mail-card\bundle\main.splash'
src = open(P, encoding='utf-8').read()

def rep(old, new, tag):
    global src
    assert old in src, 'MISSING: ' + tag
    assert src.count(old) == 1, 'NOT UNIQUE: ' + tag
    src = src.replace(old, new)
    print('ok:', tag)

# ---- 1. icon helpers (after live_dot) ---------------------------------------
rep('''fn live_dot(){
    RoundedView{width: 6 height: 6 draw_bg +: {color: mint border_radius: 3.0}}
}''',
'''fn live_dot(){
    RoundedView{width: 6 height: 6 draw_bg +: {color: mint border_radius: 3.0}}
}
// ---- native-widget icons ---------------------------------------------------
// Runtime SVG rasterises blank on this stack, so the few icons the chrome
// needs are composed from RoundedViews (sun / moon / calendar / sliders —
// the same shapes as the design's lucide set). `cut` is the surrounding
// surface colour used to bite shapes out (crescent, knob gaps).
fn sun_icon(color, size){
    View{width: size height: size flow: Overlay
        View{width: size height: size align: Align{x: 0.5 y: 0.0}
            RoundedView{width: 2 height: size * 0.24 draw_bg +: {color: color border_radius: 1.0}}}
        View{width: size height: size align: Align{x: 0.5 y: 1.0}
            RoundedView{width: 2 height: size * 0.24 draw_bg +: {color: color border_radius: 1.0}}}
        View{width: size height: size align: Align{x: 0.0 y: 0.5}
            RoundedView{width: size * 0.24 height: 2 draw_bg +: {color: color border_radius: 1.0}}}
        View{width: size height: size align: Align{x: 1.0 y: 0.5}
            RoundedView{width: size * 0.24 height: 2 draw_bg +: {color: color border_radius: 1.0}}}
        View{width: size height: size align: Align{x: 0.5 y: 0.5}
            RoundedView{width: size * 0.5 height: size * 0.5 draw_bg +: {color: color border_radius: size * 0.25}}}
    }
}
fn moon_icon(color, size, cut){
    View{width: size height: size flow: Overlay
        RoundedView{width: size * 0.8 height: size * 0.8 draw_bg +: {color: color border_radius: size * 0.4}}
        View{width: size height: size align: Align{x: 0.66 y: 0.14}
            RoundedView{width: size * 0.8 height: size * 0.8 draw_bg +: {color: cut border_radius: size * 0.4}}}
    }
}
fn calendar_icon(color, size, cut){
    View{width: size height: size flow: Overlay
        View{width: size height: size align: Align{x: 0.3 y: 0.0}
            RoundedView{width: 2 height: size * 0.32 draw_bg +: {color: color border_radius: 1.0}}}
        View{width: size height: size align: Align{x: 0.7 y: 0.0}
            RoundedView{width: 2 height: size * 0.32 draw_bg +: {color: color border_radius: 1.0}}}
        View{width: size height: size align: Align{x: 0.5 y: 1.0}
            RoundedView{width: size * 0.88 height: size * 0.72 draw_bg +: {color: color border_radius: 2.5}}}
        View{width: size height: size align: Align{x: 0.5 y: 0.5}
            RoundedView{width: size * 0.88 height: 2 draw_bg +: {color: cut border_radius: 1.0}}}
    }
}
fn sliders_icon(color, size, cut){
    View{width: size height: size flow: Overlay
        View{width: size height: size align: Align{x: 0.5 y: 0.16}
            View{width: size * 0.9 height: 2 flow: Overlay
                RoundedView{width: Fill height: 2 draw_bg +: {color: color border_radius: 1.0}}
                View{width: Fill height: 2 align: Align{x: 0.24 y: 0.5}
                    RoundedView{width: 5 height: 5 draw_bg +: {color: cut border_size: 1.0 border_color: color border_radius: 3.0}}}}}
        View{width: size height: size align: Align{x: 0.5 y: 0.5}
            View{width: size * 0.9 height: 2 flow: Overlay
                RoundedView{width: Fill height: 2 draw_bg +: {color: color border_radius: 1.0}}
                View{width: Fill height: 2 align: Align{x: 0.72 y: 0.5}
                    RoundedView{width: 5 height: 5 draw_bg +: {color: cut border_size: 1.0 border_color: color border_radius: 3.0}}}}}
        View{width: size height: size align: Align{x: 0.5 y: 0.84}
            View{width: size * 0.9 height: 2 flow: Overlay
                RoundedView{width: Fill height: 2 draw_bg +: {color: color border_radius: 1.0}}
                View{width: Fill height: 2 align: Align{x: 0.42 y: 0.5}
                    RoundedView{width: 5 height: 5 draw_bg +: {color: cut border_size: 1.0 border_color: color border_radius: 3.0}}}}}
    }
}''', 'icon helpers')

# ---- 2. theme toggle: knob icon + static track hint -------------------------
rep('''        RoundedView{width: 58 height: 30 draw_bg +: {color: white7 border_radius: 15.0 border_size: 1.0 border_color: line2} flow: Overlay
            View{width: 58 height: 30 align: pick(themeLight, Align{x: 0.0 y: 0.5}, Align{x: 1.0 y: 0.5})
                View{width: 27 height: 30 align: Align{x: 0.5 y: 0.5}
                    RoundedView{width: 24 height: 24 draw_bg +: {color: violet border_radius: 12.0} align: Align{x: 0.5 y: 0.5}
                        Label{text: pick(themeLight, "日", "月") draw_text.color: accInk draw_text.text_style.font_size: 11}}
                }
            }
        }''',
'''        RoundedView{width: 58 height: 30 draw_bg +: {color: white7 border_radius: 15.0 border_size: 1.0 border_color: line2} flow: Overlay
            // static hint on the idle side: sun when dark (tap for light),
            // moon when light (tap for dark)
            View{width: 58 height: 30 align: pick(themeLight, Align{x: 1.0 y: 0.5}, Align{x: 0.0 y: 0.5})
                View{width: 17 height: 30 align: Align{x: 0.5 y: 0.5}
                    if themeLight {
                        moon_icon(ink45, 12, white7)
                    } else {
                        sun_icon(ink45, 12)
                    }
                }
            }
            View{width: 58 height: 30 align: pick(themeLight, Align{x: 0.0 y: 0.5}, Align{x: 1.0 y: 0.5})
                View{width: 27 height: 30 align: Align{x: 0.5 y: 0.5}
                    RoundedView{width: 24 height: 24 draw_bg +: {color: violet border_radius: 12.0} align: Align{x: 0.5 y: 0.5}
                        if themeLight {
                            sun_icon(accInk, 13)
                        } else {
                            moon_icon(accInk, 13, violet)
                        }
                    }
                }
            }
        }''', 'theme toggle icons')

# ---- 3. sidebar footer: calendar + sliders ----------------------------------
rep('''            RoundedView{width: 30 height: 30 draw_bg +: {color: #x00000000 border_radius: 8.0} align: Align{x: 0.5 y: 0.5}
                Label{text: "历" draw_text.color: ink45 draw_text.text_style.font_size: 13}}
            RoundedView{width: 30 height: 30 draw_bg +: {color: #x00000000 border_radius: 8.0} align: Align{x: 0.5 y: 0.5}
                Label{text: "设" draw_text.color: ink45 draw_text.text_style.font_size: 13}}''',
'''            RoundedView{width: 30 height: 30 draw_bg +: {color: #x00000000 border_radius: 8.0} align: Align{x: 0.5 y: 0.5}
                calendar_icon(ink45, 15, panel)}
            RoundedView{width: 30 height: 30 draw_bg +: {color: #x00000000 border_radius: 8.0} align: Align{x: 0.5 y: 0.5}
                sliders_icon(ink45, 15, panel)}''', 'footer icons')

open(P, 'w', encoding='utf-8', newline='').write(src)

d = 0
ok = True
for n, l in enumerate(src.splitlines(), 1):
    if l.startswith('fn ') and d != 0:
        print('FN AT DEPTH', d, 'line', n, l[:50])
        ok = False
    d += l.count('{') - l.count('}')
print('final depth:', d, 'balanced:', d == 0 and ok)
