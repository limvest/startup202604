# China Solar Downstream Research Dataset

Information-sharing folder for a 2016-2026 research project on China's downstream solar market and Korea applicability.

## Contents

- `docs/reports/`: final research report, policy timeline, segment analyses, synthesis, Korea applicability analysis, and company profiles.
- `docs/methodology/`: source-confidence framework, data-source notes, data gaps, and rigor audit.
- `data/raw/companies.yaml`: curated company universe and classification fields.
- `data/raw/policy-events.yaml`: structured policy timeline inputs.
- `data/raw/news-articles/websearch/`: structured research notes, key facts, source notes, and confidence grades.
- `docs/pdf/china-solar-downstream-2026.pdf`: compiled English PDF report.
- `docs/pdf/china-solar-downstream-2026-ko.pdf`: Korean machine-translated PDF for quick review.

## Scope

Collection and processing code is intentionally kept local and is not part of the shared folder contents.

Raw Wayback HTML snapshots and full scraped article captures are also kept local to avoid republishing third-party pages.

## Data Notes

- Confidence ratings use the `docs/methodology/confidence-grading.md` rubric.
- Structured data is retained to make evidence trails inspectable without exposing the collection pipeline.
- The Korean PDF is machine-translated and should be treated as a review aid, not the authoritative text.
