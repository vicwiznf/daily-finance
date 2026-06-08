# -*- coding: utf-8 -*-
"""把分析結果排版成 docs/index.html（暗色編輯風）。"""

import os
import html
import datetime as dt
from string import Template

PAGE = Template("""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>每日美股財經彙整</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0e0d0b; --panel:#16140f; --line:#2a261d;
    --ink:#ece6da; --muted:#9c948a; --gold:#d8a657; --gold-soft:#e8c98a;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--ink);
    font-family:"Newsreader",Georgia,serif;line-height:1.7;
    background-image:radial-gradient(900px 500px at 80% -10%,rgba(216,166,87,.10),transparent 60%);}
  .wrap{max-width:960px;margin:0 auto;padding:56px 22px 96px}
  header{border-bottom:2px solid var(--gold);padding-bottom:22px;margin-bottom:8px}
  .kicker{font-family:"Newsreader";letter-spacing:.32em;text-transform:uppercase;
    font-size:12px;color:var(--gold);margin-bottom:10px}
  h1{font-family:"Fraunces",serif;font-weight:700;font-size:clamp(34px,6vw,58px);
    line-height:1.04;color:var(--gold-soft)}
  .date{color:var(--muted);margin-top:12px;font-size:15px}
  .note{color:var(--muted);font-size:13px;margin-top:6px;font-style:italic}

  .source{margin-top:54px}
  .source-name{font-family:"Fraunces",serif;font-weight:700;font-size:26px;color:var(--ink);
    display:flex;align-items:baseline;gap:12px;border-bottom:1px solid var(--line);padding-bottom:8px}
  .source-name .count{font-family:"Newsreader";font-size:13px;color:var(--muted);font-weight:400}

  .article{padding:20px 0;border-bottom:1px solid var(--line)}
  .article h3{font-family:"Fraunces",serif;font-weight:500;font-size:21px;line-height:1.3;color:var(--gold-soft)}
  .article p{margin-top:8px;color:var(--ink);opacity:.92}
  .article a.src{display:inline-block;margin-top:10px;font-size:13px;color:var(--gold);
    text-decoration:none;border-bottom:1px dotted var(--gold)}
  .article a.src:hover{color:var(--gold-soft)}
  .empty{color:var(--muted);font-style:italic;padding:16px 0}

  .analysis{margin-top:64px;background:var(--panel);border:1px solid var(--line);
    border-left:4px solid var(--gold);border-radius:6px;padding:30px 28px}
  .analysis h2{font-family:"Fraunces",serif;font-size:24px;color:var(--gold-soft);margin-bottom:14px}
  .analysis pre{white-space:pre-wrap;font-family:"Newsreader",serif;font-size:17px;
    line-height:1.85;color:var(--ink)}

  footer{margin-top:60px;color:var(--muted);font-size:13px;text-align:center;
    border-top:1px solid var(--line);padding-top:22px}
  footer .disc{font-style:italic;margin-top:6px}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="kicker">Daily Market Digest</div>
    <h1>每日美股財經彙整</h1>
    <div class="date">$date_str（台北時間）</div>
    <div class="note">排序依各來源最新發佈順序；非依瀏覽／按讚數（該數據不公開）。WSJ 與 Seeking Alpha 僅含摘要。</div>
  </header>

  $sources_html

  <div class="analysis">
    <h2>摘要・結語・精選個股</h2>
    <pre>$analysis</pre>
  </div>

  <footer>
    來源：Yahoo Finance・CNBC・MarketWatch・The Wall Street Journal・Seeking Alpha・Investing.com<br>
    <span class="disc">本頁由程式自動翻譯與彙整，僅供參考，不構成投資建議。投資前請自行查證。</span>
  </footer>
</div>
</body>
</html>
""")

ARTICLE = Template("""
    <div class="article">
      <h3>$zh_title</h3>
      <p>$zh_point</p>
      <a class="src" href="$url" target="_blank" rel="noopener">原文連結 ↗</a>
    </div>""")


def _esc(s):
    return html.escape(s or "")


def build(grouped, analysis_text, out_path="docs/index.html"):
    blocks = []
    for block in grouped:
        name = _esc(block["source"])
        items = block["items"]
        if items:
            arts = "".join(
                ARTICLE.substitute(
                    zh_title=_esc(it.get("zh_title") or it.get("title")),
                    zh_point=_esc(it.get("zh_point") or ""),
                    url=_esc(it.get("url")),
                )
                for it in items
            )
        else:
            arts = '<div class="empty">本次未能取得文章（來源暫時無法存取）。</div>'
        blocks.append(
            f'<section class="source"><div class="source-name">{name}'
            f'<span class="count">本次 {len(items)} 篇</span></div>{arts}</section>'
        )

    now = dt.datetime.utcnow() + dt.timedelta(hours=8)  # 台北時間
    page = PAGE.substitute(
        date_str=now.strftime("%Y-%m-%d %H:%M"),
        sources_html="\n".join(blocks),
        analysis=_esc(analysis_text),
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[OK] 已寫出 {out_path}")
