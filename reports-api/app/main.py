import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from random import randint, choice

from auth import validate_token


FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/reports")
async def get_reports(user=Depends(validate_token)):
    fake_reports = [
        {
            "id": i,
            "name": f"Report {i}",
            "status": choice(["pending", "completed", "failed"]),
            "created_at": datetime.utcnow().isoformat(),
            "value": randint(100, 1000),
        }
        for i in range(1, 6)
    ]
    return {"reports": fake_reports, "user": user}
