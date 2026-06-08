# -*- coding: utf-8 -*-
"""用 Groq 翻譯每篇文章，並產生整體摘要 / 結語 / 選股。"""

import os
import time
from groq import Groq

MODEL = "llama-3.1-8b-instant"
SLEEP_BETWEEN = 2.5  # 秒；放慢避免超過免費 TPM

_client = None


def client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def _chat(prompt, max_tokens=500):
    try:
        resp = client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except Exception as ex:
        print(f"[WARN] Groq 呼叫失敗 -> {ex}")
        return ""


def translate_item(item):
    """回傳 (中文標題, 中文重點)。失敗則退回原文。"""
    prompt = (
        "你是專業財經編輯。把以下英文財經新聞翻成自然的繁體中文。\n"
        f"標題：{item['title']}\n"
        f"摘要：{item.get('summary') or '（無摘要，僅依標題翻譯）'}\n\n"
        "嚴格依此格式輸出，不要任何多餘文字：\n"
        "標題：<繁體中文標題>\n"
        "重點：<120字內繁體中文重點；若只有標題就用一句話說明可能含義>"
    )
    out = _chat(prompt, max_tokens=350)
    zh_title, zh_point = item["title"], ""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("標題："):
            zh_title = line.replace("標題：", "", 1).strip() or item["title"]
        elif line.startswith("重點："):
            zh_point = line.replace("重點：", "", 1).strip()
    time.sleep(SLEEP_BETWEEN)
    return zh_title, zh_point


def overall(items):
    """items 為已翻譯的扁平清單，含 zh_title / zh_point。"""
    digest = "\n".join(
        f"- [{it['source']}] {it['zh_title']}：{it.get('zh_point', '')}"
        for it in items
    )[:6000]
    prompt = (
        "以下是今天各大財經來源的新聞重點（繁體中文）：\n"
        f"{digest}\n\n"
        "請用繁體中文輸出三段，標題用【】框住：\n"
        "【今日摘要】200字內，綜整今天市場主軸與情緒。\n"
        "【結語】100字內，給散戶投資人的務實提醒。\n"
        "【精選個股】挑3到5檔『基本面良好、可考慮買進』的美股。每檔一行，"
        "格式：代號 - 公司名 - 一句話理由（結合今日新聞與基本面）。"
        "最後另起一行寫風險提醒。"
    )
    return _chat(prompt, max_tokens=1000)


def analyze(grouped):
    """輸入 sources.fetch_all() 的結果；就地補上中文，並回傳整體分析字串。"""
    flat = []
    for block in grouped:
        for it in block["items"]:
            zh_title, zh_point = translate_item(it)
            it["zh_title"] = zh_title
            it["zh_point"] = zh_point
            flat.append(it)
    summary_text = overall(flat) if flat else "（今日沒有抓到任何文章，無法產生分析。）"
    return grouped, summary_text
