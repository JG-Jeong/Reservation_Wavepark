#!/usr/bin/env python3
import os, time, glob, requests
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
API_URL = os.getenv('API_URL')
if not API_URL:
    raise ValueError("API_URL 환경 변수가 설정되지 않았습니다.")

def read_temperature():
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    with open(device_file) as f:
        lines = f.readlines()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        with open(device_file) as f:
            lines = f.readlines()
    equals_pos = lines[1].find('t=')
    return float(lines[1][equals_pos+2:]) / 1000.0

def send_temperature_to_api(temp):
    payload = {
        'temperature': round(temp,2),
        'timestamp': datetime.now().isoformat()
    }
    r = requests.post(API_URL, json=payload)
    if r.status_code==200:
        print(f"전송 성공: {payload}")
    else:
        print(f"전송 실패 ({r.status_code}): {r.text}")

if __name__=='__main__':
    t = read_temperature()
    print(f"현재 수온: {t:.2f}°C")
    send_temperature_to_api(t)
