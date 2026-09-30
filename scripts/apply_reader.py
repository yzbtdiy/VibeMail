#!/usr/bin/env python3
"""One-shot: replace read_screen with the desktop reader_pane."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "bundle" / "main.splash"
src = p.read_text(encoding="utf-8")
s = src.index("fn read_screen(m){")
e = src.index("// ---- view 3: AI")

new = '''// The inbox's reader pane: the selected mail fills in place — desktop
// master-detail, no screen push. Nothing selected -> the placeholder.
fn reader_pane(){
    if selected {
        let m = mails[current]
        View{width: Fill height: Fit flow: Down spacing: 12 padding: Inset{top: 12 left: 18 right: 12 bottom: 12}
            View{width: Fill height: Fit flow: Right spacing: 8 align: Align{y: 0.5}
                Label{width: Fill text: m.cluster + " · " + m.time draw_text.color: ink38 draw_text.text_style.font_size: 9}
                Label{text: "···" draw_text.color: ink38 draw_text.text_style.font_size: 14}
            }
            Label{width: Fill text: m.subject draw_text.color: ink draw_text.text_style: theme.font_bold{font_size: 18}}
            label_row(m)
            View{width: Fill height: Fit flow: Right spacing: 11 align: Align{y: 0.5}
                avatar(m, 42)
                View{width: Fill height: Fit flow: Down spacing: 2
                    Label{width: Fill text: m.sender draw_text.color: ink draw_text.text_style.font_size: 13}
                    Label{width: Fill text: m.address + " → 发给我" draw_text.color: ink38 draw_text.text_style.font_size: 10}
                }
                Label{width: 44 text: m.time draw_text.color: ink38 draw_text.text_style.font_size: 9}
            }
            ai_summary_card(current)
            View{width: Fill height: Fit flow: Down spacing: 8
                for p in m.body.split("\\n\\n") {
                    if p != "" {
                        Label{width: Fill text: p draw_text.color: #xc0beba draw_text.text_style.font_size: 13}
                    }
                }
            }
            smart_replies(current, m)
            meeting_card(m)
'''

# reuse the inlined strip + buttons from the old read_screen verbatim
tail_start = src.index("            // the reply-state strip is inlined here", s)
tail_end = src.index("            View{width: Fill height: Fit flow: Right spacing: 8\n                    ButtonFlat{width: Fill text: \"回复\"", tail_start)
# the strip block only; the buttons row we rebuild
strip_block = src[tail_start:tail_end]
strip_block = "\n".join("    " + ln if ln.strip() else ln
                        for ln in strip_block.splitlines())

buttons = '''            View{width: Fill height: Fit flow: Right spacing: 8
                ButtonFlat{width: Fill text: "回复" on_click: || open_reply()
                    draw_bg +: {g1: violet g2: #x6a35e8 color_hover: violet color_down: #x6a35e8 border_radius: 9.0 border_size: 0.0}
                    draw_text +: {color: #xffffffff}}
                ButtonFlat{width: Fill text: "✦ AI 帮我回" on_click: || open_reply()
                    draw_bg +: {color: #x00000000 color_hover: white7 color_down: white7 border_radius: 9.0 border_size: 1.0 border_color: line2}
                    draw_text +: {color: violetT}}
                ButtonFlat{text: "转发" on_click: || open_forward()
                    draw_bg +: {color: #x00000000 color_hover: white7 color_down: white7 border_radius: 9.0 border_size: 1.0 border_color: line2}
                    draw_text +: {color: ink55}}
            }
        }
    } else {
        preview_pane()
    }
}

'''

p.write_text(src[:s] + new + strip_block + "\n" + buttons + src[e:],
             encoding="utf-8", newline="")
print("reader_pane installed, read_screen removed")
