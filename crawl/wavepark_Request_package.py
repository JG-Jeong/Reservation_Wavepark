from datetime import datetime, timedelta
import requests, csv, html, re
from bs4 import BeautifulSoup
import os


# Wavepark 서버 설정
url_general = "https://www.wavepark.co.kr/generalbooking/ajaxSectionCheck"
headers_general = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": "PHPSESSID=..."  # 여기에 실 쿠키 넣기
}

# 예약 데이터 파싱
def parse_outHtml(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    inputs = soup.find_all("input", id=re.compile(r"^area\d{3}$"))

    area_map = {
        "101": ("초급", "좌"),
        "102": ("중급", "좌"),
        "103": ("상급", "좌"),
        "201": ("초급", "우"),
        "202": ("중급", "우"),
        "203": ("상급", "우"),
    }

    results = []
    for tag in inputs:
        area_id = tag.get("id", "")[-3:]
        grade, side = area_map.get(area_id, ("알 수 없음", "알 수 없음"))
        limits = tag.get("data-limitsqty", "?")
        results.append({
            "세션": grade,
            "방향": side,
            "남은좌석": int(limits)
        })
    return results

# 날짜별 반복
def get_reservations_for_date(date_str: str):
    pickdate = date_str
    payloads = [
        {"pickdatetime": f"{pickdate} 10:00:00", "itemidx": "18", "pannelCnt": "3"},
        {"pickdatetime": f"{pickdate} 11:00:00", "itemidx": "13", "pannelCnt": "1"},
        {"pickdatetime": f"{pickdate} 12:00:00", "itemidx": "14", "pannelCnt": "2"},
        {"pickdatetime": f"{pickdate} 13:00:00", "itemidx": "13", "pannelCnt": "1"},
        {"pickdatetime": f"{pickdate} 14:00:00", "itemidx": "18", "pannelCnt": "3"},
        {"pickdatetime": f"{pickdate} 15:00:00", "itemidx": "13", "pannelCnt": "1"},
        {"pickdatetime": f"{pickdate} 16:00:00", "itemidx": "18", "pannelCnt": "3"},
        {"pickdatetime": f"{pickdate} 17:00:00", "itemidx": "14", "pannelCnt": "2"},
    ]

    daily_result = []

    for payload in payloads:
        try:
            res = requests.post(url_general, data=payload, headers=headers_general)
            data = res.json()
            out_html = html.unescape(data.get("outHtml", ""))
            parsed = parse_outHtml(out_html)

            for row in parsed:
                daily_result.append({
                    "시간": payload["pickdatetime"],
                    "세션": row["세션"],
                    "방향": row["방향"],
                    "남은좌석": row["남은좌석"]
                })

        except Exception as e:
            print(f"❌ {payload['pickdatetime']} 요청 실패: {e}")
            
    return daily_result