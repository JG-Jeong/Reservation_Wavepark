#!/usr/bin/env python3
import csv
import os
from datetime import datetime
import sys

# 프로젝트 루트를 import 경로에 추가
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from sensor.read_temp import read_temperature

def get_csv_path():
    """오늘 날짜에 해당하는 CSV 파일 경로 반환."""
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"temp_{today}.csv"
    return os.path.join(os.path.dirname(__file__), filename)

def write_header_if_needed(csv_file):
    """파일이 없으면 헤더를 쓰고 생성."""
    if not os.path.isfile(csv_file):
        with open(csv_file, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temperature_C"])

def append_temperature(csv_file):
    """현재 시간과 온도를 CSV에 한 줄 추가."""
    temp = read_temperature()
    timestamp = datetime.now().isoformat()
    with open(csv_file, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, f"{temp:.2f}"])
    print(f"[{timestamp}] 수온 기록됨: {temp:.2f}°C → {os.path.basename(csv_file)}")

if __name__ == "__main__":
    path = get_csv_path()
    write_header_if_needed(path)
    append_temperature(path)
