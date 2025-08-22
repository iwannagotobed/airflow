# api.py

from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"요청을 받았습니다! {current_time}")
    return {
        "message": "요청을 받았습니다!",
        "timestamp": current_time
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

