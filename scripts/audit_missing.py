#!/usr/bin/env python3
"""Missing-content audit: walk each screen SCROLLING through it, and diff the
texts that SHOULD be visible against what /snap actually reports. In this
stack a squeezed widget vanishes from the tree entirely (its rect never
overflows), so right-edge audits cannot see it — presence checks can.

usage: python scripts/audit_missing.py [width ...]   (default 412 700 1200)
"""
import ctypes
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
CARD_HOST = r"D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\card-host.exe"
PORT = "8145"
BASE = f"http://127.0.0.1:{PORT}"

def get(p):
    return urllib.request.urlopen(BASE + p, timeout=15).read()

def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]

def visible_texts():
    """Everything currently in the (visible) tree."""
    return {w.get("t", "") for w in snap() if w.get("t") and w.get("ty") != "Splash"}

def harvest_screen(w):
    """Sweep each independently-scrolling pane top-to-bottom, collecting
    every visible text (0.5.1: the panes scroll separately). Pane centres
    for the 0.6.0 full sidebar layout: sidebar ≈132, list ≈474 (264+420/2),
    reader = 686..w (centre), and the right rail (compose AI / agents feed)
    hugs the right edge (340 wide)."""
    cols = (132, 474, 686 + (w - 686) // 2, w - 170)
    seen = set()
    for x in cols:
        for _ in range(3):                   # to top (wheel is heavily scaled)
            get(f"/m?k=scroll&x={x}&y=400&dy=-6000")
            time.sleep(0.25)
        for _ in range(14):
            seen |= visible_texts()
            get(f"/m?k=scroll&x={x}&y=400&dy=700")
            time.sleep(0.5)
    seen |= visible_texts()
    return seen

def tap_nav_agent():
    """Click the sidebar's Agent row EXACTLY — the top-bar title says the
    same words, so the hit must stay inside the 264px sidebar (x < 280)."""
    for w in snap():
        if w.get("ty") != "Splash" and w.get("t") == "Agent 小队":
            x, y, ww, h = w["r"]
            if x < 280 and 29 < y < 766:
                get(f"/click?x={x + ww // 2:.0f}&y={y + h // 2:.0f}&wait=1")
                time.sleep(1.4)
                return True
    return False

def tap(text):
    # /snap holds only the VISIBLE viewport: an off-screen target (above or
    # below) is simply absent, so the search alternates up/down hard scrolls
    for n in range(10):
        pos = None
        for w in snap():
            if w.get("ty") != "Splash" and w.get("t") and text in w["t"]:
                x, y, ww, h = w["r"]
                pos = (x + ww / 2, y + h / 2)
                break
        if pos and (29 < pos[1] < 766 or 776 < pos[1] < 855):
            get(f"/click?x={pos[0]:.0f}&y={pos[1]:.0f}&wait=1")
            time.sleep(1.4)
            return True
        dy = (-2400 if n % 2 == 0 else 600)
        get(f"/m?k=scroll&x={ (132, 474, CUR_W - 170)[n % 3] }&y=400&dy={dy}")
        time.sleep(0.5)
    return False

EXPECTED = {
    "inbox": [
        "智能收件箱", "Vibe Agent 已整理今日", "未添加邮箱账号",
        "全部", "紧急", "需回复", "可稍后",
        "VIBE AGENT · 运行中", "问 Vibe Agent",
        # 0.6.0 full sidebar: brand, CTA, nav, folders, clusters, mini card
        "VibeMail", "AGENTIC MAIL", "写信 · AI 起草", "Ctrl N",
        "收件箱", "Agent 小队",
        "邮箱", "已加星标", "稍后处理", "已发送", "草稿", "归档", "垃圾箱",
        "AI 智能分类", "工作", "财务", "订阅", "社交",
        "AGENT ACTIVE", "1.4h", "我",
        # every row: sender + subject + priority score + first two labels
        "林晓薇", "Re: Q4 联名方案 — 报价确认与签署排期", "合同", "今天 18:00", "94",
        "VibeMail 产品团队", "你的周报已生成:Agent 本周为你节省了 3.2 小时", "周报", "自动摘要", "61",
        "陈立群 · 招聘委员会", "终面反馈:高级产品设计师候选人", "招聘", "决策待办", "88",
        "Stripe", "发票 INV-2026-0917:云服务用量 ¥4,280.00", "发票", "55",
        "GitHub", "[vibemail/core] PR #482:Agent 调度器重构 请求你评审", "代码评审", "CI 通过", "72",
        "妈妈", "中秋回家的车票订好了吗?", "家人", "90",
        "AWS Summit", "早鸟票最后 48 小时:AWS Summit 上海 2026", "营销", "28",
        "沈括 · 数据平台", "数据看板权限申请已通过", "系统通知", "40",
        # desktop: the reader placeholder is visible before any selection
        "选择一封邮件开始阅读",
    ],
    "read-mail0": [
        # desktop: the reader pane fills IN PLACE — the list stays visible
        "邮件详情 · THREAD",
        "合同", "今天 18:00", "需回复",
        "林晓薇", "xiaowei.lin@", "今天 09:42",
        # 0.6.0: the AI brief is INLINE in the reading pane (no copilot column)
        "AI 速览 · BRIEF", "AI 生成",
        "对方已确认报价 v3,财务初审通过",
        "唯一变更:第 7 条付款节点改为 30 天账期",
        "希望本周五 18:00 前完成电子签署",
        "提议下周二 10:30 线上 kickoff",
        "由 Vibe Agent 生成",
        "待办提取", "确认接受账期调整", "回复签署排期意向", "将 kickoff 加入日历",
        "积极 · 推进中",
        "智能回复 · SMART REPLIES",
        "确认条款并安排签署", "账期需内部审批,申请延期", "转发给法务复核",
        "AI 识别到会议意向", "Q4 联名 Kickoff", "周二 10:30 – 11:30", "线上会议",
        "加入日历", "协商改期",
        "回复", "转发",
    ],
    "write": [
        "AI 写信", "新邮件", "AI-ASSISTED DRAFT", "COMPOSE WITH AI",
        "收件人", "林晓薇", "主题",
        "Re: Q4 联名方案 — 报价确认与签署排期",
        # all four tone chips + the trailing notes
        "专业", "友好", "简洁", "有说服力", "已引用原始邮件", "长度:适中",
        "AI 草稿 · 语气:", "本地模板",
        "采用草稿", "重新生成",
        "发送 →", "草稿已自动保存 · 09:47",
        "描述你想表达的内容", "告诉 AI 你想表达什么",
        "生成草稿", "GPT-Vibe 4",
        "试试这样开始", "跟进上周的报价", "婉拒一个会议邀请", "请求延期交付", "约客户下周面谈",
        "AI 上下文", "引用当前邮件线程", "练习:模拟服务中断",
    ],
    "agents": [
        "Agent 小队", "运行中的 AGENT", "今日已完成任务", "本周节省时间", "待你审批",
        "12", "3.2h",
        "我的 AGENT 小队", "SQUAD · 4 UNITS",
        "跟进卫士", "日程管家", "订阅清理", "周报生成",
        "监控 12 个线程", "本周已排 5 场会议", "已合并 14 个订阅源", "下次生成:周五 17:00",
        "自动化程度", "SEMI-AUTO", "仅建议", "半自动 · 关键动作需审批", "全自动",
        "实时活动流", "LIVE",
        "检测到「Q4 联名方案」超 20h 未回复,已起草跟进邮件",
        "拒绝了与 kickoff 冲突的 1 个会议邀请",
        "批准", "忽略",
    ],
}

CUR_W = 1200

# 0.6.0: the AI brief lives INLINE in the reading pane (one Fill column), so
# nothing is copilot-specific any more — no narrow-width drop list.
COPILOT_ONLY = set()

def audit(width):
    global CUR_W
    CUR_W = width
    subprocess.run(["taskkill", "/im", "card-host.exe", "/f"], capture_output=True)
    time.sleep(1.5)
    env = dict(os.environ, MAKEPAD_REMOTE=PORT)
    proc = subprocess.Popen(
        [CARD_HOST, "--bundle", "bundle", "--app-data", ".local-state-audit",
         "--allow-unsigned", "--stamp", "--size", f"{width}x860"],
        cwd=APP, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 20:
        try:
            get("/log?n=1")
            if any("已整理今日" in t or "未添加邮箱账号" in t for t in visible_texts()):
                break
        except OSError:
            pass
        time.sleep(0.6)
    ctypes.windll.user32.SetCursorPos(ctypes.windll.user32.GetSystemMetrics(0)//2, ctypes.windll.user32.GetSystemMetrics(1)-12)

    missing = {}
    seen = harvest_screen(width)
    want_in = [e for e in EXPECTED["inbox"]
               if not (width < 1150 and e in COPILOT_ONLY)]
    missing["inbox"] = [e for e in want_in if not any(e in t for t in seen)]

    if tap("Re: Q4 联名方案"):
        time.sleep(1.0)
        seen = harvest_screen(width)
        want = [e for e in EXPECTED["read-mail0"]
                if not (width < 1150 and e in COPILOT_ONLY)]
        missing["read-mail0"] = [e for e in want if not any(e in t for t in seen)]
        # desktop: selecting a mail fills the reader pane in place; the
        # placeholder line below only exists when NOTHING is selected, so
        # drop it from the post-click check
        missing["read-mail0"] = [e for e in missing["read-mail0"]
                                 if e != "选择一封邮件开始阅读"]

    if tap("写信"):
        time.sleep(1.0)
        seen = harvest_screen(width)
        missing["write"] = [e for e in EXPECTED["write"] if not any(e in t for t in seen)]

    # the nav bar is global — jump straight from wherever we are
    if tap_nav_agent():
        time.sleep(1.0)
        seen = harvest_screen(width)
        missing["agents"] = [e for e in EXPECTED["agents"] if not any(e in t for t in seen)]

    proc.kill()
    return missing

def main():
    widths = [int(a) for a in sys.argv[1:]] or [1000, 1200, 1440]
    report = []
    for w in widths:
        print(f"=== {w}px ===", flush=True)
        miss = audit(w)
        for screen, absent in miss.items():
            if absent:
                print(f"  [{screen}] MISSING:")
                for a in absent:
                    print(f"    - {a!r}")
                    report.append(f"{w} {screen}: {a}")
            else:
                print(f"  [{screen}] complete")
    Path(APP / "build" / "missing-report.txt").write_text(
        "\n".join(report), encoding="utf-8")
    print("report -> build/missing-report.txt")

if __name__ == "__main__":
    main()
