# Getech PVOM (国电科仪) — Industrial AI from TCL factories to solar portfolios: the enterprise O&M platform that SOLARMAN cannot reach

**Entrant Type:** independent (TCL-incubated, VC-backed)
**Primary Segment:** O&M platform (enterprise / utility-scale solar portfolio)
**Founded:** 2018 (Shenzhen)
**Status:** active (Series C closed 2025, pre-IPO stage)

## Confidence Grade: ★3/★5

## Founding Narrative

Getech (国电科仪, Guodian Keyi) was founded in 2018 in Shenzhen as an industrial AI company incubated within TCL Technology Group's manufacturing ecosystem. TCL — the global consumer electronics and display manufacturer — had by 2018 developed internal AI capabilities for predictive maintenance of its own factory production lines (panel manufacturing, semiconductor fabs, injection molding equipment) and recognized that the underlying industrial fault-detection logic was transferable to other asset-intensive verticals. The decision to incubate Getech as a legally separate entity rather than as an internal IT department reflects the same capital-markets optionality logic seen in Sungrow New Energy's separation from Sungrow Power: the AI platform's valuation multiple is categorically different from TCL's hardware manufacturing multiple, and a separate entity can raise external venture capital against the software-platform story.

The pivot to solar O&M as the primary commercial vertical is the analytically interesting founding choice. By 2018, China's solar installed base exceeded 170 GW nationally and the distributed segment was growing rapidly post-531 (the May 2018 subsidy cut paradoxically increased the asset-management pressure on project owners, who now could not rely on guaranteed FIT revenue to cover suboptimal performance and needed genuine O&M optimization). Large-portfolio solar asset owners — financial investors, SOE developers, IPP operators — had an acute need for enterprise-grade O&M analytics that exceeded what residential-focused platforms (SOLARMAN, SolisCloud) could provide. Getech's TCL manufacturing AI pedigree gave it credibility for the enterprise segment that a pure software startup would not have had, and its founding moment coincides precisely with the inflection at which Chinese solar portfolios became large enough to justify enterprise-software O&M investment.

The first disclosed external financing — a Series A of CNY 100M in 2020 — came two years post-founding, suggesting an initial period of internal TCL-supported development before external capital was sought (★3, from 36Kr article on Getech). The Series A size is substantial for a B2B software company at the early-growth stage, consistent with the capital requirements of building out a large-portfolio digital-twin system that requires significant compute infrastructure and data engineering before the software product is demonstrably better than simpler alternatives.

## Business Model Evolution

The founding business model (2018–2020) was industrial AI consulting and platform licensing for manufacturing clients (primarily TCL's own factories and supply chain partners). The solar O&M application was developed in parallel as a reference use case — TCL operates factory rooftop solar installations, providing a natural internal testbed for the O&M product before external commercialization. This internal-testbed-to-external-product path is a common enterprise software incubation pattern and gives Getech a claim to real operating data that cold-start competitors cannot replicate in early sales cycles.

The Phase 2 growth model (2020–2023) was enterprise solar portfolio O&M, defined by three distinguishing features versus residential platforms like SOLARMAN. First, the digital-twin approach: rather than monitoring sensor data and flagging threshold exceedances (the SOLARMAN model), Getech creates a virtual replica of each power station — modeling inverter performance curves, soiling loss rates, shading dynamics, and equipment degradation trajectories — that enables predictive fault prioritization rather than reactive alert management. For large portfolios (50+ stations, 500+ MW), the operational cost difference between reactive and predictive maintenance is significant enough to justify enterprise software pricing. Second, the portfolio-level analytics layer: multi-station owners care about cross-portfolio benchmarking, budget allocation for capital replacements, and IRR modeling under alternative maintenance scenarios — capabilities that single-station monitoring tools are not designed to provide. Third, the AI model training advantage: with each new enterprise portfolio contract, Getech's fault-detection models improve on data from a broader range of equipment types, geographic conditions, and failure modes, creating a feedback loop that widens the performance gap with competitors over time.

Revenue exceeded CNY 1B as of the most recent disclosed data point (★3, from company disclosure, year unspecified but likely 2024). This places Getech in the same revenue tier as Guoneng Rixin (301162.SZ, CNY 550M in 2024) — and meaningfully above it — suggesting that the enterprise O&M platform has achieved genuine commercial scale rather than remaining a technology demonstration. The SAIC Capital Series B investment in 2022 adds an analytically significant dimension: SAIC (Shanghai Automotive Industry Corp) is a logical strategic investor in solar O&M because automotive manufacturing factories are among the largest C&I rooftop solar installations in China, and SAIC's own factory network represents a substantial captive O&M addressable market for Getech.

Phase 3 (2024–2026) is the pre-IPO scale-up phase. The Series C closed in 2025 with Optical Valley Finance (武汉光谷金融) as lead investor, and the HKU (Hong Kong University) joint AI lab established in April 2025 positions Getech for international market credibility. The HKU partnership is analytically interesting for its signaling function: a research partnership with a top-ranked global university is a defensible claim in enterprise sales processes where technical credibility (rather than price or brand) determines vendor selection. For large asset owners in the Middle East, Southeast Asia, or European markets — where Chinese solar platforms are not automatically trusted — the HKU imprimatur reduces selection risk perception.

## Hypothesis and Counter-Hypothesis

**Primary Hypothesis:** Getech occupies a distinct and defensible market segment — large enterprise solar portfolios requiring industrial-grade predictive analytics — that is structurally inaccessible to residential-focused platforms (SOLARMAN is too mass-market, too single-station-oriented) and grid-operator-focused companies (Guoneng Rixin 301162.SZ serves the grid interconnection analytics need, not the asset owner O&M need). Getech is the enterprise-software layer between these two established players.

**Evidence For:**
1. Revenue exceeding CNY 1B — at a scale that confirms genuine commercial adoption, not pilot-stage customer counts. The revenue level is the single strongest piece of evidence for the hypothesis (★3, unverified year, but order-of-magnitude is meaningful).
2. SAIC Capital Series B — a strategic investor whose factory solar assets are the exact enterprise customer Getech targets; SAIC's investment is implicitly a customer validation (★3).
3. TCL manufacturing AI pedigree — provides both technical credibility and a reference customer (TCL's own factories) that closes enterprise sales cycles faster than a pure-software competitor could (★4, logical inference from TCL's manufacturing scale and internal AI deployment).
4. HKU AI lab partnership (2025) — signals international enterprise market ambitions at a moment when the Chinese domestic enterprise market is becoming more competitive (★3).

**Counter-Hypothesis:** The digital-twin and predictive-analytics claims are technically ambitious but commercially vulnerable: large SOE solar portfolio owners (SPIC, CGN, China Energy) have internal data science teams and proprietary O&M platforms, meaning Getech's TAM may be limited to mid-market private-sector portfolio owners who cannot afford internal IT infrastructure.

**Evidence Against Counter:** The counter-hypothesis correctly identifies that China's largest SOE power operators are unlikely to be Getech customers for their primary portfolios — the SOE O&M market is largely closed to private software vendors. However, the counter-hypothesis underestimates the mid-market private-sector segment, which is large. China's 2021 Whole-County Rooftop Solar Pilot and the broader C&I distributed expansion created thousands of mid-sized project portfolios (10–500 MW) owned by private industrial companies, real estate developers, and financial investors who do not have internal O&M capabilities. This is the segment that the CNY 1B+ revenue figure most plausibly reflects. Additionally, the SAIC investment suggests that automotive-sector factory rooftop portfolios — owned by private and JV automotive manufacturers — are a commercially accessible segment of the enterprise market that SOE restrictions do not close off.

**Verdict:** ★3/★5. The enterprise O&M positioning is analytically coherent and the revenue figure suggests commercial validation, but the precise customer concentration, geographic split, and gross margin profile remain unverified from available sources.

## Key Metrics Summary

| Metric | Value | Year | Source Confidence |
|--------|-------|------|-------------------|
| Revenue | CNY 1B+ | ~2024 (unspecified) | ★3 |
| Series A | CNY 100M | 2020 | ★3 |
| Series B | Hundreds of millions CNY | 2022 | ★3 |
| Series B lead | SAIC Capital | 2022 | ★3 |
| Series C | Hundreds of millions CNY | 2025 | ★3 |
| Series C lead | Optical Valley Finance | 2025 | ★3 |
| HKU AI lab | Joint lab established | April 2025 | ★3 |
| Founded | 2018 (Shenzhen) | — | ★4 |
| Parent / incubator | TCL Technology Group | — | ★4 |

## Korea Applicability

**Transferability: ★4/★5**

Getech's enterprise O&M platform model is the most directly applicable to the Korean B2B context among the five profiles, because Korea's solar policy environment and industrial structure most closely match Getech's target customer profile — large private-sector industrial and commercial solar asset owners who need portfolio-level analytics, not household-level monitoring.

Korea's 2020 Korean Green New Deal and subsequent RPS (Renewable Portfolio Standard) obligation expansions have driven significant C&I distributed solar deployment, particularly on factory and warehouse rooftops. The primary owners of these assets — Samsung Electronics, Hyundai Motor, POSCO, LG Chem, SK Hynix — are exactly the enterprise customer profile that Getech's digital-twin platform targets. These companies have internal IT organizations sophisticated enough to demand enterprise-grade software (not SOLARMAN-style consumer monitoring) but are not themselves power companies with proprietary O&M infrastructure. The gap Getech fills in China — enterprise AI-driven O&M for the large private-sector C&I portfolio owner — exists and is unfilled in Korea.

The transferability constraint is vendor trust: Korean chaebols have historically preferred Korean IT vendors (Samsung SDS, LG CNS, SK C&C) or established global enterprise software firms (SAP, Oracle) for core operational systems. A Chinese AI company — even a TCL-incubated one with HKU academic credentials — faces significant reputational and supply-chain-security headwinds in the Korean enterprise procurement process as of 2026. The more viable transfer path is not Getech entering Korea directly, but rather a Korean IT vendor (Samsung SDS, KT Cloud, or a specialized energy IT firm) building a comparable industrial AI + solar O&M platform using the Getech model as the design reference. The product architecture — digital twin per power station, portfolio-level benchmarking, predictive fault prioritization — is replicable by a Korean software team without licensing Getech's technology. The competitive moat Getech holds in China (AI model trained on years of Chinese installed-base data) does not transfer internationally; a Korean competitor starting fresh in 2025–2026 would face the same cold-start data problem that Getech solved through TCL's internal factory installations.

## Unresolved Questions

- What is Getech's gross margin profile, and how much of the CNY 1B+ revenue is recurring SaaS contract versus one-time integration and consulting? The business's long-term defensibility depends on the recurring/non-recurring revenue split in a way that the available data does not resolve.
- What is the customer concentration — is the CNY 1B+ revenue distributed across many mid-market portfolio owners, or concentrated in a small number of large customers (e.g., SAIC-affiliated factory portfolios, TCL captive)? High concentration would materially revise the moat assessment downward.
- How does Getech's predictive fault detection performance compare to SOLARMAN's and Guoneng Rixin's on a controlled benchmark? The digital-twin and AI claims are marketing-level without independent technical validation — the HKU lab partnership may generate this validation, but published results are not available as of mid-2026.
