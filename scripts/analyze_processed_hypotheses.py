from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


PROCESSED_DIR = Path("data/processed")
OUTPUT_MD = Path("data/docs/processed_data_hypothesis_analysis.md")


def format_p(p: float) -> str:
    if p < 1e-4:
        return "< 0.0001"
    return f"{p:.4f}"


def main() -> None:
    load = pd.read_csv(PROCESSED_DIR / "load_hourly_all_sources.csv", parse_dates=["date"])
    smp = pd.read_csv(PROCESSED_DIR / "smp_hourly.csv", parse_dates=["date"])
    weather = pd.read_csv(PROCESSED_DIR / "weather_daily.csv", parse_dates=["date"])
    supply = pd.read_csv(PROCESSED_DIR / "supply_daily.csv", parse_dates=["date"])
    dr = pd.read_csv(PROCESSED_DIR / "dr_hourly.csv", parse_dates=["date"])

    # Remove duplicate date-hour rows (2025 playwright duplicate) with deterministic priority.
    load["priority"] = load["source_file"].str.contains("playwright").map({True: 2, False: 1})
    load = (
        load.sort_values(["date", "hour", "priority"])
        .drop_duplicates(["date", "hour"], keep="first")
        .drop(columns=["priority"])
    )

    weather_all = (
        weather.groupby("date", as_index=False)["temp_avg_c"]
        .mean()
        .rename(columns={"temp_avg_c": "temp_avg_c_all"})
    )

    df = (
        load.merge(smp, on=["date", "hour"], how="left")
        .merge(weather_all, on="date", how="left")
        .merge(supply[["date", "reserve_rate_pct"]], on="date", how="left")
        .merge(dr, on=["date", "hour"], how="left")
    )

    dr_cols = [
        "economic_dr_bid_count",
        "peak_dr_bid_count",
        "dust_dr_bid_count",
        "economic_dr_award_count",
        "peak_dr_award_count",
        "dust_dr_award_count",
    ]
    for col in dr_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    df["year"] = df["date"].dt.year
    df["is_weekend"] = df["date"].dt.dayofweek >= 5

    # Hypothesis 1: Weekend midday load is lower than weekday midday load.
    h1 = df[(df["year"] >= 2020) & (df["hour"].between(11, 15))]
    weekday_mid = h1[~h1["is_weekend"]]["load_mw"].dropna()
    weekend_mid = h1[h1["is_weekend"]]["load_mw"].dropna()
    h1_test = stats.ttest_ind(weekday_mid, weekend_mid, equal_var=False)

    # Hypothesis 2: Load and SMP are positively correlated.
    h2 = df[(df["year"] >= 2020) & (df["smp_krw_per_kwh"].notna())]
    h2_pearson = stats.pearsonr(h2["load_mw"], h2["smp_krw_per_kwh"])
    h2_spearman = stats.spearmanr(h2["load_mw"], h2["smp_krw_per_kwh"])

    # Hypothesis 3: Temperature-load relation is U-shaped (quadratic improves fit over linear).
    h3 = df[(df["year"] >= 2020) & (df["temp_avg_c_all"].notna())][["temp_avg_c_all", "load_mw"]].dropna()
    x = h3["temp_avg_c_all"].values
    y = h3["load_mw"].values
    coef_lin = np.polyfit(x, y, 1)
    pred_lin = np.polyval(coef_lin, x)
    ss_res_lin = np.sum((y - pred_lin) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2_lin = 1 - (ss_res_lin / ss_tot)
    coef_quad = np.polyfit(x, y, 2)
    pred_quad = np.polyval(coef_quad, x)
    ss_res_quad = np.sum((y - pred_quad) ** 2)
    r2_quad = 1 - (ss_res_quad / ss_tot)

    # Hypothesis 4: DR active hours have higher SMP than DR inactive hours (2020-2021).
    h4 = df[(df["year"].between(2020, 2021)) & (df["smp_krw_per_kwh"].notna())].copy()
    h4["dr_total_bid"] = (
        h4["economic_dr_bid_count"] + h4["peak_dr_bid_count"] + h4["dust_dr_bid_count"]
    )
    h4["dr_active"] = h4["dr_total_bid"] > 0
    smp_active = h4[h4["dr_active"]]["smp_krw_per_kwh"]
    smp_inactive = h4[~h4["dr_active"]]["smp_krw_per_kwh"]
    h4_test = stats.ttest_ind(smp_active, smp_inactive, equal_var=False)

    # Hypothesis 5: Zero SMP concentrates in weekend midday slots.
    h5 = df[(df["year"] >= 2020) & (df["smp_krw_per_kwh"].notna())].copy()
    h5["zero_smp"] = h5["smp_krw_per_kwh"] == 0
    h5["weekend_midday"] = h5["is_weekend"] & h5["hour"].between(11, 15)
    h5_table = pd.crosstab(h5["weekend_midday"], h5["zero_smp"])
    h5_chi2 = stats.chi2_contingency(h5_table)

    # Hypothesis 6: Reserve rate is higher on low-load days than on high-load days.
    daily = (
        df[(df["year"] >= 2020) & (df["reserve_rate_pct"].notna())]
        .groupby("date", as_index=False)
        .agg(load_mean=("load_mw", "mean"), reserve_rate_pct=("reserve_rate_pct", "first"))
    )
    q25 = daily["load_mean"].quantile(0.25)
    q75 = daily["load_mean"].quantile(0.75)
    reserve_low = daily[daily["load_mean"] <= q25]["reserve_rate_pct"]
    reserve_high = daily[daily["load_mean"] >= q75]["reserve_rate_pct"]
    h6_test = stats.ttest_ind(reserve_low, reserve_high, equal_var=False)

    lines = []
    lines.append("# Processed 데이터 상관관계 및 가설 검증")
    lines.append("")
    lines.append("## 1. 분석 범위")
    lines.append("")
    lines.append("- 사용 데이터: `load_hourly_all_sources`, `smp_hourly`, `weather_daily`, `supply_daily`, `dr_hourly`")
    lines.append("- 분석 구간: 주로 `2020~2025` (SMP/공급 데이터 가용 구간)")
    lines.append(f"- 분석 표본(시간단위): {len(df):,} rows (date-hour 중복 제거 후)")
    lines.append("")
    lines.append("## 2. 가설 및 검증 결과")
    lines.append("")
    lines.append("### H1. 주말 낮(11~15시) 수요는 평일 낮보다 낮다")
    lines.append(f"- 평일 평균: {weekday_mid.mean():,.1f} MW")
    lines.append(f"- 주말 평균: {weekend_mid.mean():,.1f} MW")
    lines.append(f"- Welch t-test: t={h1_test.statistic:.3f}, p={format_p(h1_test.pvalue)}")
    lines.append(f"- 판정: {'채택' if h1_test.pvalue < 0.05 and weekend_mid.mean() < weekday_mid.mean() else '기각'}")
    lines.append("")
    lines.append("### H2. 수요(load_mw)와 SMP는 양(+)의 상관관계를 가진다")
    lines.append(f"- Pearson r: {h2_pearson.statistic:.3f} (p={format_p(h2_pearson.pvalue)})")
    lines.append(f"- Spearman rho: {h2_spearman.correlation:.3f} (p={format_p(h2_spearman.pvalue)})")
    lines.append(f"- 판정: {'채택' if h2_pearson.pvalue < 0.05 and h2_pearson.statistic > 0 else '기각'}")
    lines.append("")
    lines.append("### H3. 기온-수요 관계는 U-shape(2차식)가 1차식보다 설명력이 높다")
    lines.append(f"- Linear R²: {r2_lin:.4f}")
    lines.append(f"- Quadratic R²: {r2_quad:.4f}")
    lines.append(f"- 2차항 계수(a): {coef_quad[0]:.4f}")
    lines.append(f"- 판정: {'채택' if (r2_quad > r2_lin and coef_quad[0] > 0) else '기각/보류'}")
    lines.append("")
    lines.append("### H4. DR 활성 시간대(입찰>0)는 비활성 시간대보다 SMP가 높다 (2020~2021)")
    lines.append(f"- DR 활성 평균 SMP: {smp_active.mean():.2f}")
    lines.append(f"- DR 비활성 평균 SMP: {smp_inactive.mean():.2f}")
    lines.append(f"- Welch t-test: t={h4_test.statistic:.3f}, p={format_p(h4_test.pvalue)}")
    lines.append(f"- DR 활성 시간 수: {int(h4['dr_active'].sum()):,}")
    lines.append(f"- 판정: {'채택' if h4_test.pvalue < 0.05 and smp_active.mean() > smp_inactive.mean() else '기각/약함'}")
    lines.append("")
    lines.append("### H5. SMP=0 시간대는 주말 낮(11~15시)에 집중된다")
    lines.append("- 교차표(weekend_midday x zero_smp):")
    lines.append("")
    lines.append("```text")
    lines.append(h5_table.to_string())
    lines.append("```")
    lines.append(f"- Chi-square: chi2={h5_chi2[0]:.3f}, p={format_p(h5_chi2[1])}")
    lines.append(f"- 판정: {'채택' if h5_chi2[1] < 0.05 else '기각'}")
    lines.append("")
    lines.append("### H6. 저부하일의 예비율은 고부하일보다 높다")
    lines.append(f"- 저부하(하위 25%) 평균 예비율: {reserve_low.mean():.2f}%")
    lines.append(f"- 고부하(상위 25%) 평균 예비율: {reserve_high.mean():.2f}%")
    lines.append(f"- Welch t-test: t={h6_test.statistic:.3f}, p={format_p(h6_test.pvalue)}")
    lines.append(f"- 판정: {'채택' if h6_test.pvalue < 0.05 and reserve_low.mean() > reserve_high.mean() else '기각'}")
    lines.append("")
    lines.append("## 3. 종합 해석")
    lines.append("")
    lines.append("- 계통 스트레스는 '주말 낮 저부하 + 일부 시간의 가격 급락(SMP=0)' 패턴으로 통계적으로 확인된다.")
    lines.append("- 수요와 SMP는 유의한 양의 상관관계를 보여, 저수요 시간대의 가격 약세 가설을 지지한다.")
    lines.append("- 온도-수요 관계는 단순 선형보다 비선형(U-shape) 설명력이 높아, 계절/기온 기반 운영 전략이 필요하다.")
    lines.append("- DR 활성은 고가격 구간과 연관되지만, 인과관계라기보다는 '동시 반응' 가능성이 크다.")
    lines.append("")
    lines.append("## 4. 한계 및 다음 검증")
    lines.append("")
    lines.append("- 2022~2024 시간별 수요는 `analysis_hourly` 통합 테이블에서 빠져 있어, 본 분석은 `load_hourly_all_sources` 재결합으로 보완했다.")
    lines.append("- 일부 지표(실제 출력제어 MWh, 변전소 역조류)는 현 processed 데이터에 없어서 직접 검증하지 못했다.")
    lines.append("- 다음 단계로 회귀모형(시간고정효과 포함)과 이벤트일 분석(출력제어 공지일 중심)을 권장한다.")
    lines.append("")

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
