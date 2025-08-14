# -*- coding: utf-8 -*-
# 用法：python crawler.py service_tags.txt   生成：dell_assets.csv
import asyncio, random, sys
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

URL = "https://www.dell.com/support/product-details/zh-cn/servicetag/{tag}/overview"  # 中文站

def clean(s: str) -> str:
    return " ".join((s or "").replace("\u3000", " ").split())

async def wait_page_ready(page):
    await page.wait_for_load_state("domcontentloaded", timeout=60000)
    # Cookie
    try:
        btn = page.locator("#onetrust-accept-btn-handler, button:has-text('接受全部'), button:has-text('Accept All')")
        if await btn.count() > 0:
            await btn.first.click(timeout=2000)
            await page.wait_for_timeout(300)
    except Exception:
        pass
    # 关键节点；不出就刷新一次
    js_ready = "() => document.querySelector('#serviceTagLabel') || document.querySelector('a.primaryWarrantyName')"
    try:
        await page.wait_for_function(js_ready, timeout=6000)
    except PWTimeout:
        await page.reload(wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_function(js_ready, timeout=8000)
    await page.wait_for_timeout(500 + random.randint(0, 700))

async def scrape_one(page, tag, max_retry=4):
    for attempt in range(max_retry):
        try:
            await page.context.clear_cookies()  # 防止上一次会话把语言带回去
            await page.goto(URL.format(tag=tag), wait_until="domcontentloaded", timeout=60000, referer="https://www.dell.com/support/home/zh-cn")
            await wait_page_ready(page)

            # 有“管理服务/主要支持服务状态”按钮就点
            if await page.locator("a.primaryWarrantyName").count() > 0:
                await page.locator("a.primaryWarrantyName").first.click()
                await page.wait_for_selector("#pss-status, #pss-timeline, #supp-svc-status-txt", timeout=10000)

            row = {"输入标签": tag}

            # 基本信息（语言无关）
            base = {
                "服务标签":   "#serviceTagLabel > div:nth-of-type(2)",
                "快速服务码": "#expressservicelabel > div:nth-of-type(2)",
                "出货日期":   "#shippingDateLabel > div:nth-of-type(2)",
                "国家/地区":  "#countryLabel > div:nth-of-type(2)",
            }
            for k, sel in base.items():
                loc = page.locator(sel).first
                row[k] = clean(await loc.inner_text()) if await loc.count() > 0 else ""

            # 保修信息（中文 DOM）
            STATUS_XP = "//*[@id='supp-svc-status-txt']/ancestor::div[contains(@class,'dds__pt-1')][1]/following-sibling::div[1]//span[contains(@class,'dds__body-2')]"
            PLAN_XP   = "//*[@id='supp-svc-plan-txt-2']/ancestor::div[contains(@class,'dds__pt-1')][1]/following-sibling::div[1]//span[contains(@class,'dds__body-2')]"

            status_loc = page.locator(f"xpath={STATUS_XP}").first
            plan_loc   = page.locator(f"xpath={PLAN_XP}").first
            row["状态"]     = clean(await status_loc.inner_text()) if await status_loc.count() > 0 else ""
            row["当前计划"] = clean(await plan_loc.inner_text())   if await plan_loc.count() > 0 else ""

            for k, sel in {
                "开始日期": "#dsk-purchaseDt strong",
                "结束日期": "#dsk-expirationDt strong",
            }.items():
                loc = page.locator(sel).first
                row[k] = clean(await loc.inner_text()) if await loc.count() > 0 else ""

            # 兜底（中文标签→紧邻值）
            if not (row.get("服务标签") or row.get("快速服务码")):
                for label, out_key in {
                    "服务标签": "服务标签",
                    "快速服务代码": "快速服务码",
                    "出货日期": "出货日期",
                    "位置": "国家/地区",
                    "国家/地区": "国家/地区",
                }.items():
                    xp = f"//*[normalize-space(text())='{label}']/following::*[not(self::script or self::style)][normalize-space()][1]"
                    loc = page.locator(f"xpath={xp}").first
                    if await loc.count() > 0:
                        row[out_key] = clean(await loc.inner_text())

            if row.get("服务标签") or row.get("快速服务码"):
                return row

            await page.wait_for_timeout(1200 + attempt * 600 + random.randint(0, 500))
        except Exception:
            await page.wait_for_timeout(1200 + attempt * 600 + random.randint(0, 500))

    keys = ["服务标签","快速服务码","出货日期","国家/地区","状态","当前计划","开始日期","结束日期"]
    return {"输入标签": tag, **{k: "" for k in keys}}

async def main():
    tags_file = sys.argv[1] if len(sys.argv) > 1 else "service_tags.txt"
    tags = [t.strip() for t in Path(tags_file).read_text(encoding="utf-8").splitlines() if t.strip()]
    random.shuffle(tags)

    async with async_playwright() as p:
        # 用系统 Chrome，并强制中文首选
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            no_viewport=True,
            locale="zh-CN",
            bypass_csp=True,
            ignore_https_errors=True,
            extra_http_headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5"},
        )
        # 伪装浏览器首选语言（防止站点用 JS 读 navigator.language）
        await context.add_init_script("""
            Object.defineProperty(navigator, 'language', {get: () => 'zh-CN'});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN','zh','en']});
        """)
        page = await context.new_page()

        rows = []
        for i, tag in enumerate(tags, 1):
            rows.append(await scrape_one(page, tag))
            await page.wait_for_timeout(400 + random.randint(0, 600))
            if i % 20 == 0:
                await page.wait_for_timeout(2500 + random.randint(0, 1200))

        await browser.close()

    cols = ["输入标签","服务标签","快速服务码","出货日期","国家/地区","状态","当前计划","开始日期","结束日期"]
    pd.DataFrame(rows, columns=cols).to_csv("dell_assets.csv", index=False, encoding="utf-8")
    print("保存完成 -> dell_assets.csv")

if __name__ == "__main__":
    asyncio.run(main())
