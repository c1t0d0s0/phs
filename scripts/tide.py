#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import requests
import json
import datetime
import math
from astral import LocationInfo
from astral.sun import sun

JST = datetime.timezone(datetime.timedelta(hours=9))

# --- 設定 ---
# 東京都港区の緯度経度
LATITUDE = 35.6586
LONGITUDE = 139.7454


def get_tide_data():
    """tide736.netのAPIから潮汐情報を取得する"""
    try:
        now = datetime.datetime.now(JST)
        year = now.year
        month = now.month
        day = now.day
        
        # 芝浦の潮汐情報を取得
        url = f"https://tide736.net/api/get_tide.php?pc=13&hc=2&yr={year}&mn={month}&dy={day}&rg=day"
        response = requests.get(url)
        response.raise_for_status()
        api_data = response.json()

        tide_summary = []
        tide_hourly = []
        
        # 今日の日付のキー 'YYYY-MM-DD'
        date_key = now.strftime('%Y-%m-%d')
        
        if api_data.get("status") == 1 and date_key in api_data.get("tide", {}).get("chart", {}):
            chart_data = api_data["tide"]["chart"][date_key]
            
            # 満潮・干潮のデータを整形
            for event in chart_data.get("flood", []): # 満潮
                time_str = event.get("time")
                cm_val = event.get("cm")
                if time_str and cm_val is not None:
                    tide_summary.append(f"{time_str} ({int(cm_val)}cm)")
            
            for event in chart_data.get("edd", []): # 干潮
                time_str = event.get("time")
                cm_val = event.get("cm")
                if time_str and cm_val is not None:
                    tide_summary.append(f"{time_str} ({int(cm_val)}cm)")
            
            # 1時間ごとの潮位データを整形
            for event in chart_data.get("tide", []):
                time_str = event.get("time")
                cm_val = event.get("cm")
                if time_str and cm_val is not None:
                    tide_hourly.append({"time": time_str, "cm": cm_val})

        # 時間でソート
        def sort_key(item):
            time_str = item.split(' ')[0]
            return datetime.datetime.strptime(time_str, '%H:%M')

        tide_summary.sort(key=sort_key)
        return {"summary": tide_summary, "hourly": tide_hourly}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching tide data from API: {e}")
        return {"summary": [], "hourly": []}
    except Exception as e:
        print(f"An error occurred while parsing tide data: {e}")
        return {"summary": [], "hourly": []}


def get_tide_name(moon_age):
    """月齢から潮の名前を返す"""
    if 28.0 <= moon_age or moon_age <= 1.5:
        return "大潮"
    elif 1.6 <= moon_age <= 5.8:
        return "中潮"
    elif 5.9 <= moon_age <= 8.9:
        return "小潮"
    elif 9.0 <= moon_age <= 10.4:
        return "長潮"
    elif 10.5 <= moon_age <= 11.9:
        return "若潮"
    elif 12.0 <= moon_age <= 16.3:
        return "大潮"
    elif 16.4 <= moon_age <= 20.6:
        return "中潮"
    elif 20.7 <= moon_age <= 23.7:
        return "小潮"
    elif 23.8 <= moon_age <= 25.2:
        return "長潮"
    elif 25.3 <= moon_age <= 26.7:
        return "若潮"
    else: # 26.8 - 27.9
        return "中潮"


def get_moon_age():
    """月齢を計算する"""
    # 月齢の計算は複雑なので、ここでは簡易的な計算式を用います
    # 朔望月(新月から次の新月まで)を約29.53日とする
    # 特定の既知の新月からの経過日数を計算する
    # 2000年1月6日を基準とする
    known_new_moon = datetime.datetime(2000, 1, 6, 18, 14, tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(JST)
    days_since_new_moon = (now - known_new_moon).total_seconds() / (24 * 3600)
    lunation_period = 29.53058867
    moon_age = days_since_new_moon % lunation_period
    return round(moon_age, 1)


def main():
    tide_data_dict = get_tide_data()
    moon_age = get_moon_age()
    tide_name = get_tide_name(moon_age)

    city = LocationInfo(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        name="Tokyo",
        region="JP",
        timezone="Asia/Tokyo"
    )

    date = datetime.date.today()
    s = sun(city.observer, date=date, tzinfo=city.timezone)

    sunrise = s["sunrise"]
    sunset = s["sunset"]
    
    sunrise_time = sunrise.strftime('%H:%M') if sunrise else "N/A"
    sunset_time = sunset.strftime('%H:%M') if sunset else "N/A"

    now = datetime.datetime.now(JST)

    # 最終的なデータ構造
    data = {
        "last_updated": now.isoformat(),
        "sunrise": sunrise_time,
        "sunset": sunset_time,
        "tide": tide_data_dict.get("summary"),
        "tide_hourly": tide_data_dict.get("hourly"),
        "tide_name": tide_name
    }

    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
