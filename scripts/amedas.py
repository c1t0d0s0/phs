#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import re
from datetime import datetime, timezone, timedelta

import requests


LATEST_TIME_URL = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
AMEDAS_MAP_URL = "https://www.jma.go.jp/bosai/amedas/data/map/{timestamp}.json"
STATION_CODE = "44132"


def latest_timestamp_string():
    """
    latest_time.txt 例: 2026-02-19T17:30:00+09:00
    -> map 用の YYYYMMDDHHMMSS へ変換（SSまで）
    """
    t = requests.get(LATEST_TIME_URL, timeout=10)
    t.raise_for_status()
    text = t.text.strip()

    # ISO 8601 をざっくり分解（+09:00 を含む）
    # 例: 2026-02-19T17:30:00+09:00
    m = re.match(
        r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-]\d{2}):(\d{2})",
        text
    )
    if not m:
        raise ValueError(f"Unexpected latest_time format: {text}")

    y, mo, d, hh, mm, ss, tzh, tzm = m.groups()

    # 気象庁の map JSON は YYYYMMDDHHMMSS 形式
    return f"{y}{mo}{d}{hh}{mm}{ss}"


def main():
    ts = latest_timestamp_string()
    url = AMEDAS_MAP_URL.format(timestamp=ts)

    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()

    if STATION_CODE not in data:
        raise KeyError(f"Station code {STATION_CODE} not found in {url}")

    station = data[STATION_CODE]

    # 保存用にメタ情報を付与（任意）
    payload = {
        "station_code": STATION_CODE,
        "source": {
            "latest_time_url": LATEST_TIME_URL,
            "map_url": url,
            "fetched_at": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        },
        "data": station
    }

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
