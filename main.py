from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json, os

app = FastAPI()

# อนุญาตให้เว็บทั้งหมดเข้าถึงได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Smart Seedling API is running"}

@app.get("/grid_data.json")
def get_grid_data():
    grid_path = "grid_data.json"
    if not os.path.exists(grid_path):
        grid = [{"status": "not-ready"} for _ in range(80)]
        json.dump(grid, open(grid_path, "w"), indent=2)
    else:
        grid = json.load(open(grid_path, "r"))
    return JSONResponse(grid)
