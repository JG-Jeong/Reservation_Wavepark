from datetime import datetime
import requests, html, re
from bs4 import BeautifulSoup

# 서버 설정
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.wavepark.co.kr",
    "Referer": "https://www.wavepark.co.kr/packagebooking",
    "Cookie": "PHPSESSID=..."  # 실제 값 교체 불필요, 프론트엔드에서 동적 주입 가정
}

# 엔드포인트 URL
URL_GENERAL = "https://www.wavepark.co.kr/generalbooking/ajaxSectionCheck"
URL_CAPA_CHECK = "https://www.wavepark.co.kr/packagebooking/capaAllCheck"
URL_RESERV_PANNEL = "https://www.wavepark.co.kr/packagebooking/reserv_pannel"

# 주말 날짜 (18:00~20:00 세션 추가 조회)
WEEKEND_DATES = [
    "2025-06-07",
    "2025-06-08",
    "2025-06-14",
    "2025-06-15",
    "2025-06-21",
    "2025-06-22",
    "2025-06-28",
    "2025-06-29"
]

# `generalbooking/ajaxSectionCheck` 정규 세션 데이터 파싱
def parse_general_outHtml(html_text):
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
            "남은좌석": int(limits) if limits.isdigit() else 0
        })
    return results

# `packagebooking/capaAllCheck` 패키지 세션 데이터 파싱
def parse_capa_check(data, schidx_info):
    grade = schidx_info.get("grade", "알 수 없음")
    return [{
        "세션": grade,
        "방향": "구분없음",  # capaAllCheck는 좌/우 구분 없음
        "남은좌석": int(data["limit_qty"]) if data.get("limit_qty") else 0
    }]

# `reserv_pannel`로 schidx와 구역 정보 수집
def get_schidx_for_night_session(date_str):
    # 패키지별 payload 설정 (초급/중급/상급별로 다를 수 있음)
    payloads = [
        # 초급
        {
            "pickdate": date_str,
            "possaleid": "Z2506254518060MM9399",
            "cate3": "0",
            "cate2": "30",
            "cate1": "9",
            "sectype": "90",

            "subject": "%5BNIGHT%5D+%EB%A6%AC%ED%94%84%EC%9E%90%EC%9C%A0%EC%84%9C%ED%95%91(%EC%A4%91%EA%B8%89)+2%EC%8B%9C%EA%B0%84+",
            "idx": "28855"
        },
        # 중급
        {
            "pickdate": date_str,
            "possaleid": "Z2506254518060MM9399",
            "cate3": "0",
            "cate2": "30",
            "cate1": "9",
            "sectype": "90",
            "subject": "%5BNIGHT%5D+%EB%A6%AC%ED%94%84%EC%9E%90%EC%9C%A0%EC%84%9C%ED%95%91(%EC%B4%88%EA%B8%89)+2%EC%8B%9C%EA%B0%84+",
            "idx": "25859"
        },
        #상급
        {
        "pickdate": date_str,
        "possaleid": "K1008252211068P26152",
        "cate3": "0",
        "cate2": "30",
        "cate1": "9",
        "sectype": "90",
        "subject": "%5BNIGHT%5D+%EB%A6%AC%ED%94%84%EC%9E%90%EC%9C%A0%EC%84%9C%ED%95%91(%EC%83%81%EA%B8%89)+2%EC%8B%9C%EA%B0%84+",
        "idx": "28854"
        }

    ]

    schidx_map = {}
    for payload in payloads:
        try:
            res = requests.post(URL_RESERV_PANNEL, data=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            soup = BeautifulSoup(html.unescape(data.get("outHtml", "")), "html.parser")
            items = soup.find_all("li", class_="reg_items")
            
            for item in items:
                schidx = item.get("data-schidx")
                picktime = item.get("data-picktime")
                subject = html.unescape(payload["subject"])
                # 정규 표현식으로 초급/중급/상급 추출
                grade_match = re.search(r'\((초급|중급|상급)\)', subject)
                grade = grade_match.group(1) if grade_match else "알 수 없음"
                schidx_map[schidx] = {"picktime": picktime, "grade": grade}
        except Exception as e:
            print(f"❌ {date_str} reserv_pannel 요청 실패 (item_idx={payload['idx']}): {e}")
    
    return schidx_map

# 날짜별 예약 현황 크롤링
def get_reservations_for_date(date_str: str):
    daily_result = []

    # 주말인지 확인 (18:00~20:00 세션은 주말에만 추가)
    is_weekend = date_str in WEEKEND_DATES

    # 10:00~17:00 (generalbooking, 모든 날짜)
    payloads_general = [
        {"pickdatetime": f"{date_str} 10:00:00", "itemidx": "18", "pannelCnt": "3"},
        {"pickdatetime": f"{date_str} 11:00:00", "itemidx": "13", "pannelCnt": "1"},
        {"pickdatetime": f"{date_str} 12:00:00", "itemidx": "14", "pannelCnt": "2"},
        {"pickdatetime": f"{date_str} 13:00:00", "itemidx": "13", "pannelCnt": "1"},
        {"pickdatetime": f"{date_str} 14:00:00", "itemidx": "18", "pannelCnt": "3"},
        {"pickdatetime": f"{date_str} 15:00:00", "itemidx": "13", "pannelCnt": "1"},
        {"pickdatetime": f"{date_str} 16:00:00", "itemidx": "18", "pannelCnt": "3"},
        {"pickdatetime": f"{date_str} 17:00:00", "itemidx": "14", "pannelCnt": "2"},
    ]

    for payload in payloads_general:
        try:
            res = requests.post(URL_GENERAL, data=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            out_html = html.unescape(data.get("outHtml", ""))
            parsed = parse_general_outHtml(out_html)
            for row in parsed:
                daily_result.append({
                    "시간": payload["pickdatetime"],
                    "세션": row["세션"],
                    "방향": row["방향"],
                    "남은좌석": row["남은좌석"]
                })
        except Exception as e:
            print(f"❌ {payload['pickdatetime']} generalbooking 요청 실패: {e}")

    # 18:00~20:00 (packagebooking, 주말 특정 날짜)
    if is_weekend:
        schidx_map = get_schidx_for_night_session(date_str)
        for schidx, info in schidx_map.items():
            try:
                payload = {"idx": schidx}
                res = requests.post(URL_CAPA_CHECK, data=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                parsed = parse_capa_check(data, info)
                for row in parsed:
                    daily_result.append({
                        "시간": f"{date_str} {info['picktime']}",
                        "세션": row["세션"],
                        "방향": row["방향"],
                        "남은좌석": row["남은좌석"]
                    })
            except Exception as e:
                print(f"❌ {date_str} {info['picktime']} capaAllCheck 요청 실패: {e}")

    return daily_result