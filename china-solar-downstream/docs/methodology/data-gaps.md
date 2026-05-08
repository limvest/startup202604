# Data Gaps — Independent/Startup Entrants Research (2026-05-08)

## Summary

8 verified independent companies were added to `data/raw/companies.yaml` in this round.
Target was 8–10 independent entrants; minimum achieved.

---

## What Was Found

| Slug | Segment | Confidence | Why Independent |
|------|---------|------------|-----------------|
| hoymiles-smiles-cloud | om_monitoring | high | Founded by Zhejiang Univ engineers, no parent OEM; STAR IPO 688032 |
| growatt-shinephone | om_monitoring | high | Bootstrapped by David Ding team, no parent; global #1 residential inverter |
| sigenergy-technology | om_monitoring | high | Ex-Huawei founders, VC-backed (Hillhouse), no parent; HK IPO 6656.HK |
| guoxia-technology | om_monitoring | high | Founded 2019 Wuxi, no parent; HK IPO 2655.HK |
| sunpure-technology | om_monitoring | high | Founded 2019 Hefei, no parent; Series A from Hillhouse Ventures |
| cyberlink-iot | om_monitoring | medium | Founded 2020 Beijing by electrical-measurement team; Angel+ |
| zhongling-xingneng | residential_installation | medium | Founded March 2023, angel round at inception, no panel/inverter parent |
| zheguyun-solar-saas | ecommerce_marketplace | low | Independent SaaS platform, active website, founder/funding history unknown |

---

## Segments With Remaining Gaps

### Solar Financing — Independent Fintech (0 added this round)

The existing file already has `solarbao-spi` (defunct) and `seeder-clean-energy` (small/foreign)
as the main independent financing examples. Research in this round failed to surface a
verifiable Chinese-domestic solar fintech startup in the 2016–2022 window:

- Searches for "光伏贷 创业" and "中国 solar loan fintech startup" returned only US/Western
  results or large SOE-backed leasing vehicles (e.g., Huaxia Financial Leasing, Yuexiu).
- The "光伏分期付款 互联网金融" wave of 2015–2018 produced platforms like Solarbao that have
  already been documented. Subsequent players appear to be bank subsidiaries or insurance
  company vehicles — not independent fintechs.
- **Gap**: 1–2 independent Chinese solar residential loan/ESCO fintech startups from
  2018–2023 that are genuinely non-SOE, non-bank-subsidiary. Likely candidates exist in
  secondary Chinese startup databases (IT橙子, 投资界) but were not surfaced by
  English-language web search.

### Residential Installation — County/Village Independent Aggregators (0 added)

- Searches for county-level independent solar installers that grew through organic
  agent-network expansion (similar to Qingtian Solar's model) did not surface
  additional verifiable companies.
- The Chinese article "超30家平台商的户用光伏渠道争夺战" (30+ platform operators competing
  for residential solar channels, 2024) implies a large number of regional independents
  exist, but naming them individually requires access to Chinese-language industry reports.
- **Gap**: 2–3 independent regional residential installers (e.g., Henan, Shandong, Guangdong
  based) that grew 2016–2022 without panel-OEM backing. High likelihood these exist;
  not discoverable through English-language search.

### O&M Monitoring — Pure SaaS Independent (partially addressed)

- Added cyberlink-iot and zheguyun as lower-confidence entries.
- The OFweek 2019 "卓越光伏智能运维服务商" award lists included companies like
  上海安轩自动化 (Shanghai Anxuan Automation) but founding details and independence
  status could not be fully confirmed from English-language sources.
- **Gap**: 1–2 additional independent distributed solar monitoring SaaS startups from
  2015–2019 with verified VC funding. Chinese database searches (Tianyancha, 36kr
  pitchhub) would likely surface these.

### E-Commerce / Marketplace — B2C Consumer Platforms (1 added, low confidence)

- Zheguyun was added at low confidence; founding year and investor identity unknown.
- Searches for "光伏O2O", "光伏帮", "光伏行家", and similar names did not surface
  verifiable independent consumer-facing platforms beyond what was already in the file.
- **Gap**: 1 verified independent B2C solar comparison or O2O installer-matching platform
  with known founding year, founders, and funding.

---

## Search Strategy Limitations

1. **Language barrier**: The most granular data about Chinese solar startup funding
   (angel, Pre-A, A rounds) resides on Chinese-language platforms (36kr, IT橙子,
   投资界, Tianyancha). English-language web search surfaces only the largest or
   most internationally prominent deals.

2. **Defunct companies**: Several waves of O2O solar platforms and solar fintech
   startups from 2015–2018 have no surviving web presence, making them unverifiable
   via web search even if they were historically significant.

3. **Aggregation platforms**: The task specification targeted platforms and operators,
   not component manufacturers. However, in China's solar ecosystem, the boundary
   between monitoring SaaS (Hoymiles, Growatt) and pure residential installers is
   often blurred — inverter makers are the dominant monitoring platform providers
   precisely because their hardware is in every installation.

---

## Recommended Next Steps

- Search Tianyancha / Qichacha for "户用光伏" companies registered 2018–2023 with
  paid-in capital > CNY 10M in Zhejiang, Shandong, Jiangsu, and Henan.
- Search 投资界 (pedaily.cn) for "光伏" A轮 deals from 2018–2022 to surface
  independent residential installers that raised institutional capital.
- Check 36kr pitchhub for all "光伏" tagged companies with angel or Series A status.

## Manual Corporate Database Lookup Protocol

For companies blocked by 企查查/天眼查 anti-bot protections:

1. Open Chrome browser, navigate to https://www.qcc.com or https://www.tianyancha.com
2. Search for the company's Chinese legal name
3. Navigate to the company detail page
4. Save the full page: Cmd+S → Web Page, Complete
5. Place saved HTML in `data/raw/chinese-db/<slug>_qcc.html`
6. Record in `source-index.csv`: kind=corporate_db, publisher=qcc.com, accessed_at=<today>

### Key data points to extract from corporate DB pages:
- 注册资本 (Registered capital)
- 成立日期 (Establishment date)
- 法人代表 (Legal representative)
- 实际控制人 (Actual controller — parent company if any)
- 融资历史 (Funding history, if available on public tier)
- 经营范围 (Business scope — shows if company description matches what we expect)
- 股权结构 (Equity structure — who owns what %)
