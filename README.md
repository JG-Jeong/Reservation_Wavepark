# 🌊 Water Temperature Monitoring Project (웨이브파크 수온 측정 시스템)

이 프로젝트는 **웨이브파크의 수온을 실시간으로 측정하고**, 측정된 데이터를 웹을 통해 제공하기 위한 시스템입니다.  
Python 기반으로 개발되었으며, **Raspberry Pi**를 활용한 온도 센서와 API 서버가 핵심 구성 요소입니다.

---

## 📌 프로젝트 개요

- **센서**: DS18B20 (라즈베리파이 공식 방식으로 구현)
- **프로그래밍 언어**: Python
- **서버 환경**: Raspberry Pi
- **웹서버 프레임워크**: Flask 또는 FastAPI
- **데이터 제공 방식**: REST API

---

## 📁 폴더 구조

```
/home/jg_jeong/water-temp-project/
├── sensor/                  # 수온 센서 측정 모듈
│   ├── read_temp.py         # 온도 읽기 함수
│   └── requirements.txt     # w1thermsensor 등 설치 패키지
│
    #아직 미구현 상태 5/21 정정길 _ water_sensor 구현하고 나서 작성할것
├── crawler/                 # 웹 크롤링 모듈
│   ├── crawler.py           # 크롤러 로직
│   └── requirements.txt     # requests, BeautifulSoup 등
│
├── data/                    # 측정값 및 크롤링 데이터 저장
│   ├── temp.csv             # 수온 로그
│   └── crawl_data.json      # wavepark에서 가져온 데이터
│
├── server/                  # API 서버
│   ├── app.py               # REST API 엔드포인트
│   └── requirements.txt
│
├── venv/                    # (선택) Python 가상환경
└── README.md
```

---

## 🔧 설치 방법

1. 레포지토리 클론:

```bash
git clone https://github.com/JG-Jeong/water-temp-project.git
cd water-temp-project
```

2. 각 디렉토리별 패키지 설치:

```bash
pip install -r sensor/requirements.txt
pip install -r crawler/requirements.txt
pip install -r server/requirements.txt
```

---

## 🚀 실행 예시

### 수온 센서 읽기

```bash
python sensor/read_temp.py
```

### 크롤링 실행

```bash
python crawler/crawler.py
```

### API 서버 실행 (Flask 예시)

```bash
python server/app.py
```

---

## 📡 사용된 센서

- **DS18B20**: 방수 디지털 온도 센서
- 라즈베리파이의 GPIO를 통해 직접 연결
- w1thermsensor 패키지를 사용해 온도 측정

---

## 📃 라이선스

MIT License

---

## 🙋 문의

문의사항은 [Issues](https://github.com/JG-Jeong/water-temp-project/issues) 혹은 이메일로 주세요.
