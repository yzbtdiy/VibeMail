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

# 1) compose rail prompt: drop the nested input shell — text sits directly
#    on the card (like the web reference)
rep('''                RoundedView{width: Fill height: Fit padding: Inset{top: 13 bottom: 13 left: 14 right: 14}
                    draw_bg +: {color: panel2 border_radius: 14.0 border_size: 1.0 border_color: line} flow: Down spacing: 10
                    RoundedView{width: Fill height: Fit draw_bg +: {color: panel border_radius: 10.0 border_size: 1.0 border_color: line}
                        TextInput{width: Fill height: 46 empty_text: "告诉 AI 你想表达什么…" on_change: |t| draft_input = t
                            draw_bg +: {color: #x00000000 color_hover: #x00000000 color_focus: #x00000000 border_radius: 10.0}
                            draw_text +: {color: inkHi color_hover: inkHi color_focus: inkHi color_empty: ink38 color_empty_hover: ink38}}
                    }
                    View{width: Fill height: Fit flow: Right spacing: 8
                        ButtonFlat{width: Fill height: 30 text: "生成草稿" on_click: || regen()
                            draw_bg +: {color: violet color_hover: violet color_down: cyan border_radius: 8.0 border_size: 0.0}
                            draw_text +: {color: accInk text_style.font_size: 11.5}}
                        chip("GPT-Vibe 4", "violet")
                    }
                }''',
'''                RoundedView{width: Fill height: Fit padding: Inset{top: 13 bottom: 13 left: 14 right: 14}
                    draw_bg +: {color: panel2 border_radius: 14.0 border_size: 1.0 border_color: line} flow: Down spacing: 10
                    TextInput{width: Fill height: 52 empty_text: "告诉 AI 你想表达什么…" on_change: |t| draft_input = t
                        draw_bg +: {color: #x00000000 color_hover: #x00000000 color_focus: #x00000000 border_radius: 10.0}
                        draw_text +: {color: inkHi color_hover: inkHi color_focus: inkHi color_empty: ink38 color_empty_hover: ink38}}
                    View{width: Fill height: Fit flow: Right spacing: 8
                        ButtonFlat{width: Fill height: 30 text: "生成草稿" on_click: || regen()
                            draw_bg +: {color: violet color_hover: violet color_down: cyan border_radius: 8.0 border_size: 0.0}
                            draw_text +: {color: accInk text_style.font_size: 11.5}}
                        chip("GPT-Vibe 4", "violet")
                    }
                }''', 'rail prompt single-layer')

# 2) AI draft: drop the nested bordered shell — draft text sits directly on
#    the tinted card; height back to a sane 150
rep('''                        RoundedView{width: Fill height: Fit padding: Inset{top: 14 bottom: 12 left: 13 right: 13}
                            draw_bg +: {color: violetBg border_radius: 12.0 border_size: 1.0 border_color: violetBd} flow: Down spacing: 9
                            View{width: Fill height: Fit flow: Right spacing: 7 align: Align{y: 0.5}
                                RoundedView{width: Fit height: Fit padding: Inset{top: 2 bottom: 2 left: 8 right: 8}
                                    draw_bg +: {color: panel border_radius: 9.0 border_size: 1.0 border_color: violetBd}
                                    Label{text: "✦ AI 草稿 · 语气:" + tone draw_text.color: violetT draw_text.text_style.font_size: 9}}
                                View{width: Fill height: 1}
                                RoundedView{width: Fit height: Fit padding: Inset{top: 2 bottom: 2 left: 7 right: 7}
                                    draw_bg +: {color: violetBg border_radius: 9.0 border_size: 1.0 border_color: violetBd}
                                    Label{text: draft_pill_text() draw_text.color: violetT draw_text.text_style.font_size: 9}}
                            }
                            if draft_text == "" {
                                Label{width: Fill text: "在右侧描述你想表达的内容,点「生成草稿」由模型起草;无模型服务时回退本地模板。" draw_text.color: ink55 draw_text.text_style.font_size: 11}
                            }
                            RoundedView{width: Fill height: Fit draw_bg +: {color: panel2 border_radius: 10.0 border_size: 1.0 border_color: line}
                                TextInput{width: Fill height: 240 text: draft_text empty_text: "草稿会出现在这里…" on_change: |t| draft_text = t
                                    draw_bg +: {color: #x00000000 color_hover: #x00000000 color_focus: #x00000000 border_radius: 10.0}
                                    draw_text +: {color: inkHi color_hover: inkHi color_focus: inkHi color_empty: ink38 color_empty_hover: ink38}}
                            }
                            View{width: Fill height: Fit flow: Right spacing: 8
                                ButtonFlat{height: 28 text: "✓ 采用草稿" on_click: || insert_draft()
                                    draw_bg +: {color: violetBgHv color_hover: violetBd color_down: violetBgHv border_radius: 7.0 border_size: 1.0 border_color: violet}
                                    draw_text +: {color: violetT text_style.font_size: 10.5}}
                                ButtonFlat{height: 28 text: "↻ 重新生成" on_click: || regen()
                                    draw_bg +: {color: #x00000000 color_hover: white7 color_down: white7 border_radius: 7.0 border_size: 1.0 border_color: line2}
                                    draw_text +: {color: ink55 text_style.font_size: 10.5}}
                            }
                            if draft_status == "unavailable" {
                                Label{width: Fill text: "模型服务不可用,已回退本地模板:" + draft_error draw_text.color: redT draw_text.text_style.font_size: 9.5}
                            }
                        }''',
'''                        RoundedView{width: Fill height: Fit padding: Inset{top: 14 bottom: 12 left: 13 right: 13}
                            draw_bg +: {color: violetBg border_radius: 12.0 border_size: 1.0 border_color: violetBd} flow: Down spacing: 9
                            View{width: Fill height: Fit flow: Right spacing: 7 align: Align{y: 0.5}
                                RoundedView{width: Fit height: Fit padding: Inset{top: 2 bottom: 2 left: 8 right: 8}
                                    draw_bg +: {color: panel border_radius: 9.0 border_size: 1.0 border_color: violetBd}
                                    Label{text: "✦ AI 草稿 · 语气:" + tone draw_text.color: violetT draw_text.text_style.font_size: 9}}
                                View{width: Fill height: 1}
                                RoundedView{width: Fit height: Fit padding: Inset{top: 2 bottom: 2 left: 7 right: 7}
                                    draw_bg +: {color: violetBg border_radius: 9.0 border_size: 1.0 border_color: violetBd}
                                    Label{text: draft_pill_text() draw_text.color: violetT draw_text.text_style.font_size: 9}}
                            }
                            if draft_text == "" {
                                Label{width: Fill text: "在右侧描述你想表达的内容,点「生成草稿」由模型起草;无模型服务时回退本地模板。" draw_text.color: ink55 draw_text.text_style.font_size: 11}
                            }
                            TextInput{width: Fill height: 150 text: draft_text empty_text: "草稿会出现在这里…" on_change: |t| draft_text = t
                                draw_bg +: {color: #x00000000 color_hover: #x00000000 color_focus: #x00000000 border_radius: 10.0}
                                draw_text +: {color: inkHi color_hover: inkHi color_focus: inkHi color_empty: ink38 color_empty_hover: ink38}}
                            View{width: Fill height: Fit flow: Right spacing: 8
                                ButtonFlat{height: 28 text: "✓ 采用草稿" on_click: || insert_draft()
                                    draw_bg +: {color: violetBgHv color_hover: violetBd color_down: violetBgHv border_radius: 7.0 border_size: 1.0 border_color: violet}
                                    draw_text +: {color: violetT text_style.font_size: 10.5}}
                                ButtonFlat{height: 28 text: "↻ 重新生成" on_click: || regen()
                                    draw_bg +: {color: #x00000000 color_hover: white7 color_down: white7 border_radius: 7.0 border_size: 1.0 border_color: line2}
                                    draw_text +: {color: ink55 text_style.font_size: 10.5}}
                            }
                            if draft_status == "unavailable" {
                                Label{width: Fill text: "模型服务不可用,已回退本地模板:" + draft_error draw_text.color: redT draw_text.text_style.font_size: 9.5}
                            }
                        }''', 'draft single-layer')

open(P, 'w', encoding='utf-8', newline='').write(src)

d = 0
ok = True
for n, l in enumerate(src.splitlines(), 1):
    if l.startswith('fn ') and d != 0:
        print('FN AT DEPTH', d, 'line', n, l[:50])
        ok = False
    d += l.count('{') - l.count('}')
print('final depth:', d, 'balanced:', d == 0 and ok)
