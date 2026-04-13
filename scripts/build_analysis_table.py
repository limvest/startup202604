from __future__ import annotations

from pathlib import Path

import pandas as pd

from load_datasets import load_core_datasets


PROCESSED_DIR = Path("data/processed")
CITY_ORDER = ["서울", "인천", "부산", "대구"]


def build_weather_aggregates(weather_daily: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [
        "temp_max_c",
        "temp_min_c",
        "temp_avg_c",
        "precipitation_mm",
        "solar_radiation_mj_m2",
        "wind_max_m_s",
        "wind_avg_m_s",
    ]

    national_weather = (
        weather_daily.groupby("date", as_index=False)[metric_columns]
        .mean()
        .rename(columns={column: f"weather_all_{column}" for column in metric_columns})
    )

    city_weather = (
        weather_daily[weather_daily["city"].isin(CITY_ORDER)]
        .pivot(index="date", columns="city", values=metric_columns)
        .sort_index(axis=1, level=1)
    )
    city_weather.columns = [
        f"weather_{city}_{metric}"
        for metric, city in city_weather.columns.to_flat_index()
    ]
    city_weather = city_weather.reset_index()

    return national_weather.merge(city_weather, on="date", how="left")


def build_daily_context(supply_daily: pd.DataFrame, weather_daily: pd.DataFrame) -> pd.DataFrame:
    weather_features = build_weather_aggregates(weather_daily)
    return supply_daily.merge(weather_features, on="date", how="left")


def build_analysis_hourly(project_root: Path | str = ".") -> pd.DataFrame:
    datasets = load_core_datasets(project_root)

    daily_context = build_daily_context(
        datasets["supply_daily"],
        datasets["weather_daily"],
    )

    hourly = datasets["load_hourly"].merge(
        datasets["smp_hourly"],
        on=["date", "hour"],
        how="left",
    )
    hourly = hourly.merge(
        datasets["dr_hourly"],
        on=["date", "hour"],
        how="left",
    )
    hourly = hourly.merge(
        daily_context,
        on="date",
        how="left",
    )

    dr_columns = [
        "economic_dr_bid_count",
        "peak_dr_bid_count",
        "dust_dr_bid_count",
        "economic_dr_award_count",
        "peak_dr_award_count",
        "dust_dr_award_count",
    ]
    hourly[dr_columns] = hourly[dr_columns].fillna(0).astype(int)
    hourly["has_smp"] = hourly["smp_krw_per_kwh"].notna()
    hourly["has_dr"] = (
        hourly[dr_columns].sum(axis=1) > 0
    )
    hourly["timestamp"] = hourly["date"] + pd.to_timedelta(hourly["hour"] - 1, unit="h")
    hourly["year"] = hourly["date"].dt.year
    hourly["month"] = hourly["date"].dt.month
    hourly["day"] = hourly["date"].dt.day
    hourly["day_of_week"] = hourly["date"].dt.dayofweek
    hourly["is_weekend"] = hourly["day_of_week"] >= 5

    ordered_columns = [
        "timestamp",
        "date",
        "year",
        "month",
        "day",
        "day_of_week",
        "is_weekend",
        "hour",
        "source",
        "load_mw",
        "smp_krw_per_kwh",
        "daily_max_smp",
        "daily_min_smp",
        "daily_weighted_avg_smp",
        "economic_dr_bid_count",
        "peak_dr_bid_count",
        "dust_dr_bid_count",
        "economic_dr_award_count",
        "peak_dr_award_count",
        "dust_dr_award_count",
        "has_smp",
        "has_dr",
        "installed_capacity_mw",
        "available_supply_mw",
        "peak_load_mw",
        "min_load_mw",
        "reserve_mw",
        "reserve_rate_pct",
        "peak_timestamp_raw",
        "min_timestamp_raw",
    ]

    weather_columns = sorted(
        column for column in hourly.columns if column.startswith("weather_")
    )
    ordered_columns.extend(weather_columns)

    return hourly[ordered_columns].sort_values(["timestamp", "source"]).reset_index(drop=True)


def save_analysis_outputs(project_root: Path | str = ".") -> tuple[Path, Path]:
    root = Path(project_root)
    output_dir = root / PROCESSED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_hourly = build_analysis_hourly(root)
    csv_path = output_dir / "analysis_hourly.csv"
    parquet_path = output_dir / "analysis_hourly.parquet"

    analysis_hourly.to_csv(csv_path, index=False, encoding="utf-8-sig")
    analysis_hourly.to_parquet(parquet_path, index=False)

    return csv_path, parquet_path


if __name__ == "__main__":
    csv_path, parquet_path = save_analysis_outputs(Path("."))
    print(f"saved: {csv_path}")
    print(f"saved: {parquet_path}")
