# -*- coding: utf-8 -*-
"""六大來源抓取（全部 RSS）：
Yahoo / CNBC / MarketWatch / WSJ / Seeking Alpha / Investing.com
每個來源獨立容錯：失敗只回空清單，不影響整體。完全在 GitHub Actions 雲端執行。"""

import time
import feedparser
from bs4 import BeautifulSoup

PER_SOURCE = 5  # 每個來源取幾篇

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def _clean(text, limit=600):
    if not text:
        return ""
    t = BeautifulSoup(text, "lxml").get_text(" ", strip=True)
    return t[:limit]


def _ts(entry):
    for k in ("published_parsed", "updated_parsed"):
        v = entry.get(k)
        if v:
            return time.mktime(v)
    return 0.0


def from_rss(feed_urls, source_name, limit=PER_SOURCE):
    """讀多個 RSS，合併、去重、依時間新到舊排序，取前 limit 篇。"""
    items = []
    for url in feed_urls:
        try:
            d = feedparser.parse(url, request_headers=UA)
            for e in d.entries:
                items.append({
                    "source": source_name,
                    "title": (e.get("title") or "").strip(),
                    "url": (e.get("link") or "").strip(),
                    "summary": _clean(e.get("summary") or e.get("description") or ""),
                    "published": e.get("published") or e.get("updated") or "",
                    "ts": _ts(e),
                })
        except Exception as ex:
            print(f"[WARN] {source_name} RSS 失敗 {url} -> {ex}")
    seen, uniq = set(), []
    for it in sorted(items, key=lambda x: x["ts"], reverse=True):
        if it["url"] and it["title"] and it["url"] not in seen:
            seen.add(it["url"])
            uniq.append(it)
    return uniq[:limit]


# ---------- 1. Yahoo Finance ----------
def yahoo():
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "JPM"]
    feeds = ["https://finance.yahoo.com/news/rssindex"]
    feeds += [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={t}&region=US&lang=en-US"
        for t in tickers
    ]
    return from_rss(feeds, "Yahoo Finance")


# ---------- 2. CNBC ----------
def cnbc():
    base = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id="
    feeds = [
        base + "100003114",  # Top News
        base + "20910258",   # Markets
        base + "15839069",   # Investing
    ]
    return from_rss(feeds, "CNBC")


# ---------- 3. MarketWatch ----------
def marketwatch():
    feeds = [
        "https://www.marketwatch.com/rss/topstories",
        "https://www.marketwatch.com/rss/marketpulse",
        "https://www.marketwatch.com/rss/realtimeheadlines",
    ]
    return from_rss(feeds, "MarketWatch")


# ---------- 4. The Wall Street Journal（僅標題摘要） ----------
def wsj():
    feeds = [
        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
        "https://feeds.a.dj.com/rss/RSSWSJD.xml",
    ]
    return from_rss(feeds, "The Wall Street Journal")


# ---------- 5. Seeking Alpha（僅摘要；被擋會自動跳過） ----------
def seeking_alpha():
    feeds = [
        "https://seekingalpha.com/feed.xml",
        "https://seekingalpha.com/market_currents.xml",
    ]
    return from_rss(feeds, "Seeking Alpha")


# ---------- 6. Investing.com（被擋會自動跳過） ----------
def investing():
    feeds = [
        "https://www.investing.com/rss/news.rss",
        "https://www.investing.com/rss/stock.rss",
        "https://www.investing.com/rss/news_25.rss",
    ]
    return from_rss(feeds, "Investing.com")


# ---------- 統一入口 ----------
SOURCES = [
    ("Yahoo Finance", yahoo),
    ("CNBC", cnbc),
    ("MarketWatch", marketwatch),
    ("The Wall Street Journal", wsj),
    ("Seeking Alpha", seeking_alpha),
    ("Investing.com", investing),
]


def fetch_all():
    result = []
    for name, fn in SOURCES:
        try:
            items = fn()
        except Exception as ex:
            print(f"[ERROR] {name} 整體失敗 -> {ex}")
            items = []
        print(f"[OK] {name}: 取得 {len(items)} 篇")
        result.append({"source": name, "items": items})
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(fetch_all(), ensure_ascii=False, indent=2)[:2000])
