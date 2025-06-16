from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from datetime import datetime
from crawl.wavepark_Request import get_reservations_for_date

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 프론트엔드 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 예약 데이터 조회
@app.get("/reservation/{date}")
async def get_reservation(date: str):
    try:
        # 날짜 형식 검증 (YYYY-MM-DD)
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.")
        
        data = get_reservations_for_date(date)
        if not data:
            raise HTTPException(status_code=404, detail="예약 데이터가 없습니다.")
        
        return {"date": date, "data": data}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# Lambda 핸들러
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)