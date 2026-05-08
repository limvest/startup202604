# Confidence Grading Framework

## Purpose
Every factual claim in this research report carries a ★N/★5 confidence indicator. This document defines what each grade means, what source types justify each grade, and how grades were applied consistently across 35 company profiles.

## Grade Definitions

### ★5 — Verified via Official Record
**Source requirement:** Public market filing (A-share, HKEX, SSE, ChiNext, STAR Market prospectus or annual report), government enforcement record, or three or more independent media sources with direct attribution.

**Examples in this dataset:**
- Hoymiles STAR Market IPO data (688032.SH annual report)
- Sigenergy HKEX IPO prospectus (6656.HK)
- Guoxia Technology HKEX prospectus (2655.HK)
- Guoneng Rixin ChiNext annual reports (301162.SZ)
- Jinko Power Technology SSE annual reports (601778.SH)
- Solarbao-SPI fraud: People's Energy News + SCMP + PRNewswire + 36Kr (4 independent sources)
- Hanergy SFC enforcement record (official regulatory action)

### ★4 — High Confidence via Institutional Source
**Source requirement:** Industry association report, established trade media (PV Magazine, PV-Tech, OFWeek Solar, BloombergNEF, Wood Mackenzie), or two independent sources that cross-corroborate.

**Examples in this dataset:**
- Chint Anneng metrics (EqualOcean + Dealroom + company website)
- SOLARMAN platform metrics (company corporate disclosure; authoritative for own figures)
- Huaxia Financial Leasing scale (CLBA annual report + secondary press)
- Yuexiu New Energy financials (OFWeek citing Yuexiu Capital disclosure)
- Skyworth Solar revenue (OFWeek + company website)

**Limitation:** Even institutional sources may carry self-reported data from company IR. ★4 claims are directionally reliable but not independently audited.

### ★3 — Moderate Confidence via Secondary Media
**Source requirement:** Single trade media source, or single company press release without cross-corroboration.

**Examples in this dataset:**
- SOLARMAN 220 GW managed (company website only; no independent verification found)
- Residential penetration rate (~3.5% of 100M+ rooftop resources): Zhongling Xingneng founding team statement
- Segment S-curve position assessments (analytical judgment from aggregated data)

**Limitation:** ★3 claims are used for context and directional framing. They are explicitly hedged in the text and should not be treated as independently verifiable.

### ★2 — Low Confidence via Single Report
**Source requirement:** Single non-industry press mention, or indirect reference in an unrelated report.

**Examples in this dataset:**
- S2B2C-PV-Platform (光伏行家) commercial status: referenced in 2017 WeChat industry newsletter; no corporate record found
- Zheguyun commercial scale: website active but no financial disclosure found; estimates based on product tier pricing

### ★1 — Minimal Confidence; Unverifiable
**Source requirement:** Claim cannot be independently verified from any accessible source.

**Usage:** ★1 claims are documented as gaps in the rigor audit (methodology/rigor-audit.md Section 8). No ★1 claim is included in the core analytical narrative. Presence in the dataset as a documented absence is itself informative (e.g., the failure to find any evidence of S2B2C-PV-Platform commercial activity is a ★4 negative finding).

---

## Application Rules

### Rule 1: Grade the Claim, Not the Company
A single company profile may contain ★5 claims (from public filings) alongside ★3 claims (from press estimates) for different metrics. The grade applies to the specific claim, not the company overall.

### Rule 2: No ★4+ Without Two Supporting Sources
Claims above ★3 require minimum two independent sources, or one official filing. Exception: company websites for their own metrics are treated as authoritative for ★4 (companies do not typically mis-state their own product coverage, though may round favorably).

### Rule 3: Distinguish Positive and Negative Findings
The absence of evidence is itself a finding — but grades differently than presence evidence. "No Korean residential solar leasing product found" is a ★4 negative finding (multiple search attempts via WebSearch confirmed the null). "No evidence of X company's commercial scale" is ★2 (insufficient effort may explain the gap).

### Rule 4: Korea Claims Are Graded Separately
Korea market data was separately verified in a dedicated WebSearch session (2026-05-08). See rigor-audit.md Section 5 for Korea-specific source list and grades.

---

## Source Hierarchy

| Rank | Source Type | Maximum Grade |
|------|-------------|--------------|
| 1 | Public market filing (A-share, HKEX, SSE) | ★5 |
| 2 | Government regulatory record (SFC, CSRC, MoF) | ★5 |
| 3 | 3+ independent corroborating media | ★5 |
| 4 | Industry association report (CLBA, CPIA) | ★4 |
| 5 | Established trade media (PV Magazine, WoodMac, OFWeek) | ★4 |
| 6 | Company IR / corporate website | ★4 |
| 7 | Company press release (single) | ★3 |
| 8 | Non-industry press | ★3 |
| 9 | Social media / WeChat public account | ★2 |
| 10 | No verifiable source | ★1 |

---

## Unit Conversion Protocol
Chinese financial figures are reported in 亿元 (100M CNY). Research agents converting these figures into "billions" are required to explicitly state the conversion: "320亿 = CNY 32 billion." All amounts in this report use the format "CNY XB" (CNY X billion) or "CNY XM" (CNY X million) to avoid ambiguity.

**Documented conversion errors and corrections:** See rigor-audit.md Section 4.
