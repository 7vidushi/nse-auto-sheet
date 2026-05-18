import io
import json
import os
import zipfile
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import gspread
import pandas as pd
import requests
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME = "Top 250 Stocks"


def get_google_sheet():
    credentials_json = os.environ.get("GCP_CREDENTIALS")
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")

    if not credentials_json:
        raise ValueError("Missing GitHub secret: GCP_CREDENTIALS")

    if not spreadsheet_id:
        raise ValueError("Missing GitHub secret: SPREADSHEET_ID")

    credentials_info = json.loads(credentials_json)

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(SHEET_NAME)

    return worksheet


def download_bhavcopy_for_date(date_obj):
    yyyymmdd = date_obj.strftime("%Y%m%d")
    ddmonyyyy = date_obj.strftime("%d%b%Y").upper()
    year = date_obj.strftime("%Y")
    mon = date_obj.strftime("%b").upper()

    possible_urls = [
        f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{yyyymmdd}_F_0000.csv.zip",
        f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{yyyymmdd}_F.csv.zip",
        f"https://archives.nseindia.com/content/historical/EQUITIES/{year}/{mon}/cm{ddmonyyyy}bhav.csv.zip",
        f"https://www1.nseindia.com/content/historical/EQUITIES/{year}/{mon}/cm{ddmonyyyy}bhav.csv.zip",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/zip,text/csv,*/*",
    }

    for url in possible_urls:
        print(f"Trying URL: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200 and response.content:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    csv_files = [
                        name for name in z.namelist()
                        if name.lower().endswith(".csv")
                    ]

                    if not csv_files:
                        continue

                    with z.open(csv_files[0]) as csv_file:
                        df = pd.read_csv(csv_file)

                    return df, date_obj.strftime("%Y-%m-%d"), url

        except Exception as e:
            print(f"Failed for {url}: {e}")
            continue

    return None, None, None


def get_latest_bhavcopy():
    india_time = datetime.now(ZoneInfo("Asia/Kolkata"))

    for days_back in range(0, 10):
        date_obj = india_time.date() - timedelta(days=days_back)
        df, bhavcopy_date, source_url = download_bhavcopy_for_date(date_obj)

        if df is not None and not df.empty:
            print(f"Using bhavcopy date: {bhavcopy_date}")
            print(f"Source URL: {source_url}")
            return df, bhavcopy_date

    raise RuntimeError("Could not download NSE bhavcopy for the last 10 days.")


def find_column(df, possible_names):
    normalized_columns = {
        col.strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        key = name.strip().lower()
        if key in normalized_columns:
            return normalized_columns[key]

    raise KeyError(f"Could not find any of these columns: {possible_names}")


def prepare_top_250_stocks(df):
    df.columns = [col.strip() for col in df.columns]

    symbol_col = find_column(df, ["TckrSymb", "SYMBOL"])
    volume_col = find_column(df, ["TtlTradgVol", "TOTTRDQTY"])
    close_col = find_column(df, ["ClsPric", "CLOSE"])
    series_col = find_column(df, ["SctySrs", "SERIES"])

    name_col = None
    for possible_name in ["FinInstrmNm", "SECURITY", "NAME OF COMPANY"]:
        if possible_name in df.columns:
            name_col = possible_name
            break

    clean_df = df.copy()

    clean_df[series_col] = clean_df[series_col].astype(str).str.strip().str.upper()
    clean_df[symbol_col] = clean_df[symbol_col].astype(str).str.strip().str.upper()

    # Keep only normal equity series
    clean_df = clean_df[clean_df[series_col] == "EQ"]

    clean_df[volume_col] = pd.to_numeric(clean_df[volume_col], errors="coerce")
    clean_df[close_col] = pd.to_numeric(clean_df[close_col], errors="coerce")

    clean_df = clean_df.dropna(subset=[symbol_col, volume_col, close_col])

    exclude_keywords = [
        "ETF",
        "LIQUID",
        "GOLD",
        "SILVER",
        "CASH",
        "BOND",
        "BEES",
        "NIFTYETF",
        "BANKETF",
        "DEBT",
        "SDL",
        "GSEC",
        "TBILL",
    ]

    combined_text = clean_df[symbol_col].astype(str)

    if name_col:
        combined_text = combined_text + " " + clean_df[name_col].astype(str)

    pattern = "|".join(exclude_keywords)
    clean_df = clean_df[
        ~combined_text.str.upper().str.contains(pattern, na=False)
    ]

    clean_df = clean_df.sort_values(
        by=volume_col,
        ascending=False
    ).head(250)

    output_df = clean_df[[symbol_col, volume_col, close_col]].copy()
    output_df.columns = ["NSE Code", "Volume", "Close Price"]

    output_df["Volume"] = output_df["Volume"].astype(int)
    output_df["Close Price"] = output_df["Close Price"].round(2)

    return output_df


def update_google_sheet(output_df, bhavcopy_date):
    worksheet = get_google_sheet()

    worksheet.update(
        values=[["NSE Code", "Volume", "Close Price"]],
        range_name="A1:C1",
    )

    worksheet.batch_clear(["A2:C251"])

    values = output_df.values.tolist()

    if values:
        end_row = len(values) + 1
        worksheet.update(
            values=values,
            range_name=f"A2:C{end_row}",
        )

    now_ist = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d %H:%M:%S IST")

    worksheet.update(
        values=[
            ["Last Updated", now_ist],
            ["Bhavcopy Date", bhavcopy_date],
        ],
        range_name="L1:M2",
    )

    print(f"Updated {len(values)} stocks into Google Sheet.")


def main():
    raw_df, bhavcopy_date = get_latest_bhavcopy()
    top_250_df = prepare_top_250_stocks(raw_df)
    update_google_sheet(top_250_df, bhavcopy_date)


if __name__ == "__main__":
    main()
