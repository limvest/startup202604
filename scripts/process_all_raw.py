from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import pandas as pd

from load_datasets import HOUR_COLUMNS_PLAIN, _to_numeric, load_core_datasets


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
MARKET_SHEETS_DIR = PROCESSED_DIR / "market_statistics_sheets"


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^\w가-힣]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unnamed"


def save_table(df: pd.DataFrame, csv_path: Path, parquet_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception:
        parquet_ready = df.copy()
        object_columns = parquet_ready.select_dtypes(include=["object"]).columns
        for column in object_columns:
            parquet_ready[column] = parquet_ready[column].astype("string")
        parquet_ready.to_parquet(parquet_path, index=False)


def process_core_outputs(root: Path) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    datasets = load_core_datasets(root)
    for name, df in datasets.items():
        csv_path = root / PROCESSED_DIR / f"{name}.csv"
        parquet_path = root / PROCESSED_DIR / f"{name}.parquet"
        save_table(df, csv_path, parquet_path)
        outputs.append(
            {
                "source_file": "core_pipeline",
                "dataset_name": name,
                "status": "processed",
                "rows": len(df),
                "columns": len(df.columns),
                "csv_path": str(csv_path.relative_to(root)),
                "parquet_path": str(parquet_path.relative_to(root)),
                "note": "Generated from normalized core loaders.",
            }
        )
    return outputs


def process_smp_weighted(root: Path) -> dict[str, Any]:
    path = root / RAW_DIR / "EPSIS_SMP_가중평균.csv"
    raw = pd.read_csv(path, encoding="cp949")
    columns = ["기간", "육지", "제주", "통합", "BLMP"]
    raw.columns = columns
    df = raw[raw["기간"].notna()].copy()
    df["period"] = pd.to_datetime(df["기간"], format="%Y/%m")
    df = _to_numeric(df, ["육지", "제주", "통합", "BLMP"])
    df = df.rename(
        columns={
            "육지": "smp_mainland",
            "제주": "smp_jeju",
            "통합": "smp_integrated",
            "BLMP": "blmp",
        }
    )[["period", "smp_mainland", "smp_jeju", "smp_integrated", "blmp"]].sort_values("period")
    csv_path = root / PROCESSED_DIR / "smp_weighted_monthly.csv"
    parquet_path = root / PROCESSED_DIR / "smp_weighted_monthly.parquet"
    save_table(df, csv_path, parquet_path)
    return {
        "source_file": path.name,
        "dataset_name": "smp_weighted_monthly",
        "status": "processed",
        "rows": len(df),
        "columns": len(df.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "Monthly SMP summary for mainland, Jeju, and integrated values.",
    }


def process_renewable_utilization(root: Path) -> dict[str, Any]:
    frames = []
    for filename in ["EPSIS_재생에너지이용률.xlsx", "EPSIS_신재생이용률.xlsx"]:
        path = root / RAW_DIR / filename
        df = pd.read_excel(path).copy()
        df["source_file"] = filename
        frames.append(df)
    merged = pd.concat(frames, ignore_index=True)
    merged["period"] = pd.to_datetime(merged["기간"], format="%Y/%m")
    merged = _to_numeric(merged, ["이용률"])
    merged = merged.rename(
        columns={"지역": "region", "이용률": "utilization_rate_pct", "연료원": "fuel_type"}
    )[["period", "region", "fuel_type", "utilization_rate_pct", "source_file"]]
    merged = merged.sort_values(["period", "region", "fuel_type", "source_file"]).reset_index(drop=True)
    csv_path = root / PROCESSED_DIR / "renewable_utilization_monthly.csv"
    parquet_path = root / PROCESSED_DIR / "renewable_utilization_monthly.parquet"
    save_table(merged, csv_path, parquet_path)
    return {
        "source_file": "EPSIS_재생에너지이용률.xlsx;EPSIS_신재생이용률.xlsx",
        "dataset_name": "renewable_utilization_monthly",
        "status": "processed",
        "rows": len(merged),
        "columns": len(merged.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "Combined monthly renewable utilization with source traceability.",
    }


def process_additional_hourly_loads(root: Path) -> dict[str, Any]:
    load_sources = [
        ("2013-2020-수요관리후-발전단-전력수요실적.csv", "cp949"),
        ("2021년-1-12월-수요관리후-발전단-수요실적.csv", "cp949"),
        ("한국전력거래소-시간별-전국-전력수요량-20221231.csv", "cp949"),
        ("시간별-전국-전력수요량-20231231.csv", "cp949"),
        ("한국전력거래소-시간별-전국-전력수요량-20241231.csv", "cp949"),
        ("KPX_시간별전국전력수요량_2025.csv", "cp949"),
        ("KPX_시간별전국전력수요량_2025_playwright.csv", "cp949"),
        ("한국전력거래소-시간별-전국-전력수요량-20251231.csv", "cp949"),
    ]
    frames = []
    for filename, encoding in load_sources:
        path = root / RAW_DIR / filename
        df = pd.read_csv(path, encoding=encoding).copy()
        df["date"] = pd.to_datetime(df["날짜"])
        df = _to_numeric(df, HOUR_COLUMNS_PLAIN)
        long_df = df.melt(
            id_vars=["date"],
            value_vars=HOUR_COLUMNS_PLAIN,
            var_name="hour_label",
            value_name="load_mw",
        )
        long_df["hour"] = long_df["hour_label"].str.extract(r"(\d+)").astype(int)
        long_df["source_file"] = filename
        frames.append(long_df[["date", "hour", "load_mw", "source_file"]])
    merged = pd.concat(frames, ignore_index=True).sort_values(["date", "hour", "source_file"]).reset_index(drop=True)
    csv_path = root / PROCESSED_DIR / "load_hourly_all_sources.csv"
    parquet_path = root / PROCESSED_DIR / "load_hourly_all_sources.parquet"
    save_table(merged, csv_path, parquet_path)
    return {
        "source_file": ";".join(filename for filename, _ in load_sources),
        "dataset_name": "load_hourly_all_sources",
        "status": "processed",
        "rows": len(merged),
        "columns": len(merged.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "Long-format hourly load table across all available nationwide load CSVs.",
    }


def process_regional_energy_usage(root: Path) -> dict[str, Any]:
    path = root / RAW_DIR / "한국전력거래소-행정구역별-에너지사용량-통합데이터-20241231.csv"
    df = pd.read_csv(path, encoding="cp949").copy()
    df["period"] = pd.to_datetime(df["년월"], format="%Y-%m")
    df = _to_numeric(df, ["사용량"])
    df = df.rename(
        columns={
            "행정구역": "region",
            "에너지사용량구분": "energy_usage_type",
            "세부용도": "usage_detail",
            "사용량": "usage_amount",
        }
    )[["period", "region", "energy_usage_type", "usage_detail", "usage_amount"]]
    csv_path = root / PROCESSED_DIR / "regional_energy_usage_2024.csv"
    parquet_path = root / PROCESSED_DIR / "regional_energy_usage_2024.parquet"
    save_table(df, csv_path, parquet_path)
    return {
        "source_file": path.name,
        "dataset_name": "regional_energy_usage_2024",
        "status": "processed",
        "rows": len(df),
        "columns": len(df.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "Regional monthly energy usage by category and detailed use.",
    }


def process_kepco_api_catalog(root: Path) -> dict[str, Any]:
    path = root / RAW_DIR / "한국전력공사-전력데이터서비스마켓-EDS-OPEN-API-서비스-목록-20250630.csv"
    df = pd.read_csv(path, encoding="utf-8-sig").copy()
    df = df.rename(
        columns={
            "서비스목록일련번호": "service_id",
            "API구분": "api_category",
            "API서비스명": "api_service_name",
            "API서비스단축명": "api_service_short_name",
            "제공내용": "description",
        }
    )
    csv_path = root / PROCESSED_DIR / "kepco_api_catalog_20250630.csv"
    parquet_path = root / PROCESSED_DIR / "kepco_api_catalog_20250630.parquet"
    save_table(df, csv_path, parquet_path)
    return {
        "source_file": path.name,
        "dataset_name": "kepco_api_catalog_20250630",
        "status": "processed",
        "rows": len(df),
        "columns": len(df.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "KEPCO EDS open API service catalog.",
    }


def process_market_statistics_workbooks(root: Path) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    workbook_files = [
        "2022년도_전력시장통계.xlsx",
        "2023년도_전력시장통계.xlsx",
        "2024년도_전력시장통계.xlsx",
        "2025년도_전력시장통계.xlsx",
    ]
    manifest_rows = []
    for filename in workbook_files:
        path = root / RAW_DIR / filename
        workbook_slug = slugify(path.stem)
        xls = pd.ExcelFile(path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet_name, header=None)
            df = df.dropna(axis=0, how="all").dropna(axis=1, how="all").reset_index(drop=True)
            if df.empty:
                manifest_rows.append(
                    {
                        "source_file": filename,
                        "sheet_name": sheet_name,
                        "status": "skipped_empty",
                        "rows": 0,
                        "columns": 0,
                    }
                )
                continue
            df.columns = [f"col_{i+1:03d}" for i in range(len(df.columns))]
            sheet_slug = slugify(sheet_name)
            csv_path = root / MARKET_SHEETS_DIR / f"{workbook_slug}__{sheet_slug}.csv"
            parquet_path = root / MARKET_SHEETS_DIR / f"{workbook_slug}__{sheet_slug}.parquet"
            save_table(df, csv_path, parquet_path)
            manifest_rows.append(
                {
                    "source_file": filename,
                    "sheet_name": sheet_name,
                    "status": "processed",
                    "rows": len(df),
                    "columns": len(df.columns),
                    "csv_path": str(csv_path.relative_to(root)),
                    "parquet_path": str(parquet_path.relative_to(root)),
                }
            )
        outputs.append(
            {
                "source_file": filename,
                "dataset_name": f"{workbook_slug}_sheets",
                "status": "processed",
                "rows": sum(row["rows"] for row in manifest_rows if row["source_file"] == filename and row["status"] == "processed"),
                "columns": None,
                "csv_path": str((root / PROCESSED_DIR / "market_statistics_sheet_index.csv").relative_to(root)),
                "parquet_path": "",
                "note": "Workbook sheets exported individually into market_statistics_sheets.",
            }
        )
    manifest_df = pd.DataFrame(manifest_rows)
    csv_path = root / PROCESSED_DIR / "market_statistics_sheet_index.csv"
    parquet_path = root / PROCESSED_DIR / "market_statistics_sheet_index.parquet"
    save_table(manifest_df, csv_path, parquet_path)
    return outputs


def process_legacy_plus_dr_specs(root: Path) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    legacy_files = [
        ("플러스DR_경제성DR_입낙찰.xlsx", "plus_dr_economic_schema"),
        ("플러스DR_수요자원입낙찰.xlsx", "plus_dr_resource_market_schema"),
        ("플러스DR_제주플러스DR실적.xlsx", "plus_dr_jeju_schema"),
    ]
    rename_map = {
        "항목명": "field_name_ko",
        "항목명(영문)": "field_name_en",
        "항목설명": "field_description",
        "도메인 분류": "domain_category",
        "데이터 타입": "data_type",
        "최대길이": "max_length",
        "단위": "unit",
        "표현형식": "format_expression",
        "정보시스템명": "source_system",
        "DB명": "db_name",
        "Table명": "table_name",
        "기타": "etc",
        "코드": "code",
        "코드명": "code_name",
    }
    ordered_columns = list(rename_map.values())

    for filename, dataset_name in legacy_files:
        path = root / RAW_DIR / filename
        # These files are legacy Excel binaries (.xls) and contain field definition sheets.
        df = pd.read_excel(path, header=1).copy()
        df = df.rename(columns=rename_map)
        for column in ordered_columns:
            if column not in df.columns:
                df[column] = pd.NA
        df = df[ordered_columns]
        if "max_length" in df.columns:
            df = _to_numeric(df, ["max_length"])
        df["source_file"] = filename
        df = df.dropna(how="all", subset=["field_name_ko", "field_description", "data_type"]).reset_index(drop=True)

        csv_path = root / PROCESSED_DIR / f"{dataset_name}.csv"
        parquet_path = root / PROCESSED_DIR / f"{dataset_name}.parquet"
        save_table(df, csv_path, parquet_path)
        outputs.append(
            {
                "source_file": filename,
                "dataset_name": dataset_name,
                "status": "processed",
                "rows": len(df),
                "columns": len(df.columns),
                "csv_path": str(csv_path.relative_to(root)),
                "parquet_path": str(parquet_path.relative_to(root)),
                "note": "Legacy Plus DR workbook converted as field-definition metadata table.",
            }
        )
    return outputs


def process_download_targets_manifest(root: Path) -> dict[str, Any]:
    path = root / RAW_DIR / "download_targets_manifest.csv"
    df = pd.read_csv(path).copy()
    for column in ["priority"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    csv_path = root / PROCESSED_DIR / "download_targets_manifest_normalized.csv"
    parquet_path = root / PROCESSED_DIR / "download_targets_manifest_normalized.parquet"
    save_table(df, csv_path, parquet_path)
    return {
        "source_file": path.name,
        "dataset_name": "download_targets_manifest_normalized",
        "status": "processed",
        "rows": len(df),
        "columns": len(df.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "Normalized download manifest for crawling/direct/institution tracks.",
    }


def process_institution_request_queue(root: Path) -> dict[str, Any]:
    path = root / RAW_DIR / "institution_request_queue.csv"
    df = pd.read_csv(path).copy()
    if "priority" in df.columns:
        df["priority"] = pd.to_numeric(df["priority"], errors="coerce")
    csv_path = root / PROCESSED_DIR / "institution_request_queue_normalized.csv"
    parquet_path = root / PROCESSED_DIR / "institution_request_queue_normalized.parquet"
    save_table(df, csv_path, parquet_path)
    return {
        "source_file": path.name,
        "dataset_name": "institution_request_queue_normalized",
        "status": "processed",
        "rows": len(df),
        "columns": len(df.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "Institution-request tracking queue normalized for workflow monitoring.",
    }


def process_kpx_playwright_notices(root: Path) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    kpx_files = [
        ("kpx_board0216_notices_playwright.csv", "kpx_board0216_notices"),
        ("kpx_output_related_notices_playwright.csv", "kpx_output_related_notices"),
        ("kpx_output_related_notice_details_playwright.csv", "kpx_output_related_notice_details"),
    ]

    def recover_notice_date(df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        if "date" not in result.columns:
            result["date"] = pd.NaT
        result["date"] = pd.to_datetime(result["date"], errors="coerce")

        # Recover from title patterns like "2026년 4월 11일"
        if "title" in result.columns:
            title_extract = result["title"].fillna("").astype(str).str.extract(r"(?P<y>\d{4})년\s*(?P<m>\d{1,2})월\s*(?P<d>\d{1,2})일")
            title_date = pd.to_datetime(
                title_extract.rename(columns={"y": "year", "m": "month", "d": "day"}),
                errors="coerce",
            )
            result["date"] = result["date"].fillna(title_date)

        # Recover from body text patterns like "작성일 2026/04/10"
        if "body_text" in result.columns:
            body_extract = result["body_text"].fillna("").astype(str).str.extract(r"작성일\s*(?P<y>\d{4})[./-](?P<m>\d{1,2})[./-](?P<d>\d{1,2})")
            body_date = pd.to_datetime(
                body_extract.rename(columns={"y": "year", "m": "month", "d": "day"}),
                errors="coerce",
            )
            result["date"] = result["date"].fillna(body_date)
        return result

    for source_name, dataset_name in kpx_files:
        path = root / RAW_DIR / source_name
        df = pd.read_csv(path).copy()
        df = recover_notice_date(df)
        if "body_text" in df.columns:
            df["body_length"] = df["body_text"].fillna("").astype(str).str.len()
        csv_path = root / PROCESSED_DIR / f"{dataset_name}.csv"
        parquet_path = root / PROCESSED_DIR / f"{dataset_name}.parquet"
        save_table(df, csv_path, parquet_path)
        outputs.append(
            {
                "source_file": source_name,
                "dataset_name": dataset_name,
                "status": "processed",
                "rows": len(df),
                "columns": len(df.columns),
                "csv_path": str(csv_path.relative_to(root)),
                "parquet_path": str(parquet_path.relative_to(root)),
                "note": "KPX board data captured by Playwright (list/detail).",
            }
        )
    return outputs


def build_unprocessed_report(root: Path, processed_source_files: set[str]) -> dict[str, Any]:
    raw_files = sorted(p.name for p in (root / RAW_DIR).iterdir() if p.is_file())
    report_rows = []
    for filename in raw_files:
        if filename == "기억장치관리전략-0408.ini":
            report_rows.append(
                {
                    "source_file": filename,
                    "status": "ignored",
                    "reason": "Configuration file, not an analysis dataset.",
                }
            )
        elif filename in processed_source_files:
            report_rows.append(
                {
                    "source_file": filename,
                    "status": "processed",
                    "reason": "Converted into one or more processed datasets.",
                }
            )
        else:
            report_rows.append(
                {
                    "source_file": filename,
                    "status": "unmapped",
                    "reason": "No processing rule matched this file.",
                }
            )
    df = pd.DataFrame(report_rows)
    csv_path = root / PROCESSED_DIR / "raw_processing_status.csv"
    parquet_path = root / PROCESSED_DIR / "raw_processing_status.parquet"
    save_table(df, csv_path, parquet_path)
    return {
        "source_file": "raw_inventory",
        "dataset_name": "raw_processing_status",
        "status": "processed",
        "rows": len(df),
        "columns": len(df.columns),
        "csv_path": str(csv_path.relative_to(root)),
        "parquet_path": str(parquet_path.relative_to(root)),
        "note": "Tracks which raw files were processed, blocked, or ignored.",
    }


def main() -> None:
    root = Path(".")
    outputs: list[dict[str, Any]] = []
    core_source_files = {
        "EPSIS_전력수급실적.csv",
        "EPSIS_SMP_시간별.csv",
        "기상_전국주요도시_일별_2013_2025.csv",
        "플러스DR_입낙찰_2020_2021.csv",
        "2013-2020-수요관리후-발전단-전력수요실적.csv",
        "2021년-1-12월-수요관리후-발전단-수요실적.csv",
        "KPX_시간별전국전력수요량_2025.csv",
    }

    outputs.extend(process_core_outputs(root))
    outputs.append(process_smp_weighted(root))
    outputs.append(process_renewable_utilization(root))
    outputs.append(process_additional_hourly_loads(root))
    outputs.append(process_regional_energy_usage(root))
    outputs.append(process_kepco_api_catalog(root))
    outputs.extend(process_market_statistics_workbooks(root))
    outputs.extend(process_legacy_plus_dr_specs(root))
    outputs.append(process_download_targets_manifest(root))
    outputs.append(process_institution_request_queue(root))
    outputs.extend(process_kpx_playwright_notices(root))

    processed_sources: set[str] = set()
    for row in outputs:
        source_file = row["source_file"]
        for item in str(source_file).split(";"):
            if item and item != "core_pipeline":
                processed_sources.add(item)
    processed_sources.update(core_source_files)
    outputs.append(build_unprocessed_report(root, processed_sources))

    summary_df = pd.DataFrame(outputs)
    csv_path = root / PROCESSED_DIR / "processed_dataset_manifest.csv"
    parquet_path = root / PROCESSED_DIR / "processed_dataset_manifest.parquet"
    save_table(summary_df, csv_path, parquet_path)
    print(f"saved: {csv_path}")
    print(f"saved: {parquet_path}")
    print(summary_df[["dataset_name", "status", "rows", "csv_path"]].to_string(index=False))


if __name__ == "__main__":
    main()
