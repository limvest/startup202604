from __future__ import annotations

import asyncio
import argparse
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from playwright.async_api import async_playwright


MANIFEST_PATH = Path("data/raw/download_targets_manifest.csv")
OUT_DIR = Path("data/raw/playwright_batch_capture")


async def capture_pages(rows: pd.DataFrame, threads: int = 10) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    async def capture_one_url(browser, sem: asyncio.Semaphore, url: str) -> dict[str, str]:
        slug = quote_plus(url)
        html_path = OUT_DIR / f"{slug}.html"
        png_path = OUT_DIR / f"{slug}.png"
        status = "ok"
        error = ""
        async with sem:
            page = await browser.new_page()
            try:
                html = ""
                for attempt in range(3):
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                        await page.wait_for_timeout(1500)
                        await page.wait_for_load_state("load", timeout=20000)
                        html = await page.content()
                        break
                    except Exception:
                        if attempt == 2:
                            raise
                        await page.wait_for_timeout(1500)
                await page.screenshot(path=str(png_path), full_page=True)
                html_path.write_text(html, encoding="utf-8")
            except Exception as exc:
                status = "failed"
                error = str(exc)
            finally:
                await page.close()
        return {
            "landing_url": url,
            "capture_status": status,
            "error": error,
            "html_archive": str(html_path) if html_path.exists() else "",
            "screenshot": str(png_path) if png_path.exists() else "",
        }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        sem = asyncio.Semaphore(threads)
        tasks = []
        unique_urls = sorted(set(rows["landing_url"].astype(str).tolist()))
        for url in unique_urls:
            if not url.startswith("http"):
                continue
            tasks.append(asyncio.create_task(capture_one_url(browser, sem, url)))
        if tasks:
            url_results = await asyncio.gather(*tasks)
            url_map = {r["landing_url"]: r for r in url_results}
            for row in rows.to_dict(orient="records"):
                url = str(row["landing_url"])
                if not url.startswith("http"):
                    continue
                captured = url_map.get(url, {})
                results.append(
                    {
                        "dataset_name": row["dataset_name"],
                        "landing_url": url,
                        "capture_status": captured.get("capture_status", "failed"),
                        "error": captured.get("error", "url capture missing"),
                        "html_archive": captured.get("html_archive", ""),
                        "screenshot": captured.get("screenshot", ""),
                    }
                )
        await browser.close()
    return pd.DataFrame(results)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=10, help="동시 수집 스레드 수")
    parser.add_argument("--priority", type=int, nargs="*", default=None, help="수집 우선순위 필터(예: --priority 1 2)")
    args = parser.parse_args()

    manifest = pd.read_csv(MANIFEST_PATH)
    targets = manifest[manifest["playwright_needed"].astype(str).str.lower() == "yes"].copy()
    if args.priority:
        targets = targets[targets["priority"].astype(int).isin(args.priority)].copy()

    result_df = await capture_pages(targets, threads=max(1, args.threads))
    out_csv = OUT_DIR / "capture_results.csv"
    result_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"saved: {out_csv}")
    print(result_df.to_string(index=False))


if __name__ == "__main__":
    asyncio.run(main())
