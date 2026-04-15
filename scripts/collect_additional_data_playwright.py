from __future__ import annotations

import asyncio
import re
from pathlib import Path
from urllib.parse import quote_plus, urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


RAW_DIR = Path("data/raw")
ARCHIVE_DIR = RAW_DIR / "kpx_notice_archives"
KPX_LIST_URL = "https://www.kpx.or.kr/board.es?mid=a10109050000&bid=0216"
TITLE_KEYWORDS = [
    "출력제어",
    "경부하기",
    "수급",
    "재생에너지",
    "제주",
    "육지",
]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def build_detail_url(href: str) -> str:
    if href.startswith("http"):
        return href
    return urljoin("https://www.kpx.or.kr", href)


def extract_notice_rows(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, str]] = []
    for anchor in soup.select("a[href*='act=view'][href*='list_no=']"):
        href = anchor.get("href", "")
        title = clean_text(anchor.get_text(" ", strip=True))
        if not href or not title:
            continue
        tr = anchor.find_parent("tr")
        cells = tr.find_all(["td", "th"]) if tr else []
        date_text = ""
        for c in cells:
            text = clean_text(c.get_text(" ", strip=True))
            if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
                date_text = text
                break
        rows.append(
            {
                "title": title,
                "url": build_detail_url(href),
                "date": date_text,
            }
        )
    # dedupe by url
    unique = {}
    for row in rows:
        unique[row["url"]] = row
    return list(unique.values())


def extract_notice_body(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    candidates = [
        soup.select_one(".board_view"),
        soup.select_one(".view_cont"),
        soup.select_one(".bbs_view"),
        soup.select_one("article"),
        soup.select_one("main"),
    ]
    for node in candidates:
        if node:
            text = clean_text(node.get_text(" ", strip=True))
            if len(text) > 40:
                return text
    return clean_text(soup.get_text(" ", strip=True))


def keyword_match(title: str) -> bool:
    return any(keyword in title for keyword in TITLE_KEYWORDS)


async def collect_kpx_notices(max_pages: int = 20) -> pd.DataFrame:
    records: list[dict[str, str]] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        for npage in range(1, max_pages + 1):
            url = f"{KPX_LIST_URL}&nPage={npage}"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = await page.content()
            rows = extract_notice_rows(html)
            for row in rows:
                row["list_page"] = npage
            records.extend(rows)
        await browser.close()
    df = pd.DataFrame(records).drop_duplicates(subset=["url"]).reset_index(drop=True)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


async def collect_kpx_notice_details(df: pd.DataFrame) -> pd.DataFrame:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    details: list[dict[str, str]] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        for row in df.itertuples(index=False):
            url = row.url
            title = str(row.title)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                html = await page.content()
                body_text = extract_notice_body(html)
                slug = quote_plus(url)
                (ARCHIVE_DIR / f"{slug}.html").write_text(html, encoding="utf-8")
                details.append(
                    {
                        "title": title,
                        "url": url,
                        "date": row.date if hasattr(row, "date") else None,
                        "body_text": body_text,
                        "archive_html": str((ARCHIVE_DIR / f"{slug}.html").as_posix()),
                    }
                )
            except Exception as exc:
                details.append(
                    {
                        "title": title,
                        "url": url,
                        "date": row.date if hasattr(row, "date") else None,
                        "body_text": "",
                        "archive_html": "",
                        "error": str(exc),
                    }
                )
        await browser.close()
    detail_df = pd.DataFrame(details)
    if "date" in detail_df.columns:
        detail_df["date"] = pd.to_datetime(detail_df["date"], errors="coerce")
    return detail_df


def save_outputs(all_notices: pd.DataFrame, filtered: pd.DataFrame, details: pd.DataFrame) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    all_path = RAW_DIR / "kpx_board0216_notices_playwright.csv"
    filtered_path = RAW_DIR / "kpx_output_related_notices_playwright.csv"
    detail_path = RAW_DIR / "kpx_output_related_notice_details_playwright.csv"
    all_notices.to_csv(all_path, index=False, encoding="utf-8-sig")
    filtered.to_csv(filtered_path, index=False, encoding="utf-8-sig")
    details.to_csv(detail_path, index=False, encoding="utf-8-sig")
    print(f"saved: {all_path}")
    print(f"saved: {filtered_path}")
    print(f"saved: {detail_path}")
    print(f"all_notices={len(all_notices)} filtered={len(filtered)} details={len(details)}")


async def main() -> None:
    all_notices = await collect_kpx_notices(max_pages=20)
    filtered = all_notices[all_notices["title"].apply(keyword_match)].copy()
    filtered = filtered.sort_values(["date", "title"], ascending=[False, True]).reset_index(drop=True)
    details = await collect_kpx_notice_details(filtered)
    save_outputs(all_notices, filtered, details)


if __name__ == "__main__":
    asyncio.run(main())
