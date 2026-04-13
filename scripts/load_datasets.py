from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
HOUR_COLUMNS_PADDED = [f"{hour:02d}시" for hour in range(1, 25)]
HOUR_COLUMNS_PLAIN = [f"{hour}시" for hour in range(1, 25)]


def _raw_path(project_root: Path, filename: str) -> Path:
    return project_root / RAW_DIR / filename


def _read_csv(project_root: Path, filename: str, encoding: str) -> pd.DataFrame:
    return pd.read_csv(_raw_path(project_root, filename), encoding=encoding)


def _to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column].astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            )
    return df


def load_supply_daily(project_root: Path | str = ".") -> pd.DataFrame:
    df = _read_csv(Path(project_root), "EPSIS_전력수급실적.csv", "cp949").copy()
    df["date"] = pd.to_datetime(
        df[["년", "월", "일"]].rename(columns={"년": "year", "월": "month", "일": "day"})
    )
    df = _to_numeric(
        df,
        [
            "설비용량(MW)",
            "공급능력(MW)",
            "최대전력(MW)",
            "최소전력(MW)",
            "공급예비력(MW)",
            "공급예비율(%)",
        ],
    )
    return (
        df.rename(
            columns={
                "설비용량(MW)": "installed_capacity_mw",
                "공급능력(MW)": "available_supply_mw",
                "최대전력(MW)": "peak_load_mw",
                "최소전력(MW)": "min_load_mw",
                "공급예비력(MW)": "reserve_mw",
                "공급예비율(%)": "reserve_rate_pct",
                "최대전력기준일시": "peak_timestamp_raw",
                "최소전력기준일시": "min_timestamp_raw",
            }
        )[
            [
                "date",
                "installed_capacity_mw",
                "available_supply_mw",
                "peak_load_mw",
                "min_load_mw",
                "reserve_mw",
                "reserve_rate_pct",
                "peak_timestamp_raw",
                "min_timestamp_raw",
            ]
        ]
        .sort_values("date")
        .reset_index(drop=True)
    )


def load_smp_hourly(project_root: Path | str = ".") -> pd.DataFrame:
    df = _read_csv(Path(project_root), "EPSIS_SMP_시간별.csv", "cp949").copy()
    df["date"] = pd.to_datetime(df["기간"], format="%Y/%m/%d")
    df = _to_numeric(df, HOUR_COLUMNS_PADDED + ["최대", "최소", "가중평균"])
    long_df = df.melt(
        id_vars=["date", "최대", "최소", "가중평균"],
        value_vars=HOUR_COLUMNS_PADDED,
        var_name="hour_label",
        value_name="smp_krw_per_kwh",
    )
    long_df["hour"] = long_df["hour_label"].str.extract(r"(\d+)").astype(int)
    return (
        long_df.rename(
            columns={
                "최대": "daily_max_smp",
                "최소": "daily_min_smp",
                "가중평균": "daily_weighted_avg_smp",
            }
        )[
            [
                "date",
                "hour",
                "smp_krw_per_kwh",
                "daily_max_smp",
                "daily_min_smp",
                "daily_weighted_avg_smp",
            ]
        ]
        .sort_values(["date", "hour"])
        .reset_index(drop=True)
    )


def load_weather_daily(project_root: Path | str = ".") -> pd.DataFrame:
    df = _read_csv(Path(project_root), "기상_전국주요도시_일별_2013_2025.csv", "utf-8-sig").copy()
    df["date"] = pd.to_datetime(df["날짜"])
    df = _to_numeric(
        df,
        ["최고기온", "최저기온", "평균기온", "강수량mm", "일사량MJm2", "최대풍속ms", "평균풍속ms"],
    )
    return (
        df.rename(
            columns={
                "도시": "city",
                "최고기온": "temp_max_c",
                "최저기온": "temp_min_c",
                "평균기온": "temp_avg_c",
                "강수량mm": "precipitation_mm",
                "일사량MJm2": "solar_radiation_mj_m2",
                "최대풍속ms": "wind_max_m_s",
                "평균풍속ms": "wind_avg_m_s",
            }
        )[
            [
                "date",
                "city",
                "temp_max_c",
                "temp_min_c",
                "temp_avg_c",
                "precipitation_mm",
                "solar_radiation_mj_m2",
                "wind_max_m_s",
                "wind_avg_m_s",
            ]
        ]
        .sort_values(["date", "city"])
        .reset_index(drop=True)
    )


def load_dr_hourly(project_root: Path | str = ".") -> pd.DataFrame:
    df = _read_csv(Path(project_root), "플러스DR_입낙찰_2020_2021.csv", "cp949").copy()
    df["date"] = pd.to_datetime(df["날짜"])
    df = _to_numeric(
        df,
        [
            "시간",
            "경제성DR입찰건수",
            "피크수요입찰건수",
            "미세먼지입찰건수",
            "경제성DR낙찰건수",
            "피크수요낙찰건수",
            "미세먼지낙찰건수",
        ],
    )
    return (
        df.rename(
            columns={
                "시간": "hour",
                "경제성DR입찰건수": "economic_dr_bid_count",
                "피크수요입찰건수": "peak_dr_bid_count",
                "미세먼지입찰건수": "dust_dr_bid_count",
                "경제성DR낙찰건수": "economic_dr_award_count",
                "피크수요낙찰건수": "peak_dr_award_count",
                "미세먼지낙찰건수": "dust_dr_award_count",
            }
        )[
            [
                "date",
                "hour",
                "economic_dr_bid_count",
                "peak_dr_bid_count",
                "dust_dr_bid_count",
                "economic_dr_award_count",
                "peak_dr_award_count",
                "dust_dr_award_count",
            ]
        ]
        .sort_values(["date", "hour"])
        .reset_index(drop=True)
    )


def load_hourly_load(project_root: Path | str = ".") -> pd.DataFrame:
    root = Path(project_root)
    load_sources = [
        ("2013-2020-수요관리후-발전단-전력수요실적.csv", "cp949", "load_after_demand_management"),
        ("2021년-1-12월-수요관리후-발전단-수요실적.csv", "cp949", "load_after_demand_management"),
        ("KPX_시간별전국전력수요량_2025.csv", "cp949", "kpx_hourly_demand"),
    ]
    frames: list[pd.DataFrame] = []
    for filename, encoding, source in load_sources:
        df = _read_csv(root, filename, encoding).copy()
        df["date"] = pd.to_datetime(df["날짜"])
        df = _to_numeric(df, HOUR_COLUMNS_PLAIN)
        long_df = df.melt(
            id_vars=["date"],
            value_vars=HOUR_COLUMNS_PLAIN,
            var_name="hour_label",
            value_name="load_mw",
        )
        long_df["hour"] = long_df["hour_label"].str.extract(r"(\d+)").astype(int)
        long_df["source"] = source
        frames.append(long_df[["date", "hour", "load_mw", "source"]])
    return pd.concat(frames, ignore_index=True).sort_values(["date", "hour", "source"]).reset_index(drop=True)


def load_core_datasets(project_root: Path | str = ".") -> dict[str, pd.DataFrame]:
    root = Path(project_root)
    return {
        "supply_daily": load_supply_daily(root),
        "smp_hourly": load_smp_hourly(root),
        "weather_daily": load_weather_daily(root),
        "dr_hourly": load_dr_hourly(root),
        "load_hourly": load_hourly_load(root),
    }


if __name__ == "__main__":
    datasets = load_core_datasets(Path("."))
    for name, frame in datasets.items():
        print(f"{name}: rows={len(frame)}, cols={len(frame.columns)}")
        print(frame.head(3).to_string(index=False))
        print()
