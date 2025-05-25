from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import csv
import os

from mangum import Mangum
# wavepark 예약 데이터 크롤링 코드 임포트
from crawl.wavepark_Request import get_reservations_for_date

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ["http://localhost:3000"]처럼 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# wavepark 예약 데이터 조회
@app.get("/reservation/{date}")
def get_reservation(date):
    try:
        data = get_reservations_for_date(date)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not data:
        raise HTTPException(status_code=404, detail="예약 데이터가 없습니다.")

    return {"date": date, "data": data}


# 온도 데이터 측정
class TemperatureData(BaseModel):
    temperature: float
    timestamp: str

@app.post('/temperature')
def receive_temperature(data: TemperatureData):
    print("받은 데이터:", data)
    # 여기서 data를 DB에 저장하거나, 다른 로직을 실행
    return {"status": "ok"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


handler = Mangum(app)
