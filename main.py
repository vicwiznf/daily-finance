# -*- coding: utf-8 -*-
"""總指揮：抓取 → 翻譯/分析 → 產生 HTML → 存原始資料。"""

import json
import sources
import analyze
import build


def main():
    print("=== 1) 抓取六大來源 ===")
    grouped = sources.fetch_all()

    print("=== 2) Groq 翻譯與整體分析 ===")
    grouped, analysis_text = analyze.analyze(grouped)

    print("=== 3) 產生網頁 ===")
    build.build(grouped, analysis_text, out_path="docs/index.html")

    print("=== 4) 存原始資料 data.json ===")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(
            {"analysis": analysis_text, "sources": grouped},
            f, ensure_ascii=False, indent=2, default=str,
        )
    print("=== 完成 ===")


if __name__ == "__main__":
    main()
