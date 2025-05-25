import os
import time
import glob
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 엔드포인트 설정
API_URL = os.getenv('API_URL')
if not API_URL:
    raise ValueError("API_URL 환경 변수가 설정되지 않았습니다.")

def read_temperature():
    """DS18B20 센서에서 온도를 읽어옵니다."""
    try:
        # DS18B20 센서의 디바이스 파일 경로를 찾습니다
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        device_file = device_folder + '/w1_slave'

        # 센서에서 데이터를 읽습니다
        with open(device_file, 'r') as f:
            lines = f.readlines()

        # 온도 데이터를 추출합니다
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            with open(device_file, 'r') as f:
                lines = f.readlines()

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        
    except Exception as e:
        print(f"온도 읽기 오류: {e}")
        return None

def send_temperature_to_api(temperature):
    """측정된 온도를 API로 전송합니다."""
    try:
        data = {
            'temperature': temperature,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            print(f"온도 데이터 전송 성공: {temperature}°C")
        else:
            print(f"API 전송 실패: {response.status_code}")
    except Exception as e:
        print(f"API 전송 오류: {e}")

def main():
    print("수온 측정 시스템 시작...")
    
    while True:
        temperature = read_temperature()
        if temperature is not None:
            print(f"현재 수온: {temperature}°C")
            send_temperature_to_api(temperature)
        else:
            print("온도 측정 실패")
        
        # for test 1분마다 측정
        time.sleep(60)

        # 1시간마다 측정/ 실제로는 이걸로 측정 할거임.
        # time.sleep(3600)

if __name__ == "__main__":
    main() 