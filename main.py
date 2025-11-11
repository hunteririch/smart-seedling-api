from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np, json, os, io

app = FastAPI()

# ✅ เปิดให้เว็บอื่น (เช่น Netlify) เข้าถึงได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📄 จุดทดสอบว่าระบบออนไลน์อยู่ไหม
@app.get("/")
def home():
    return {"message": "Smart Seedling AI API is running"}

# 📄 คืนค่าข้อมูลสถานะทั้งหมด
@app.get("/grid_data.json")
def get_grid_data():
    grid_path = "grid_data.json"
    if not os.path.exists(grid_path):
        grid = [{"status": "not-ready"} for _ in range(80)]
        json.dump(grid, open(grid_path, "w"), indent=2)
    else:
        grid = json.load(open(grid_path, "r"))
    return JSONResponse(grid)

# 📸 จุดรับภาพจาก ESP32-CAM แล้วให้ AI วิเคราะห์
@app.post("/api/upload")
async def upload_image(slot_id: int = Form(...), file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # ✅ วิเคราะห์ความเป็นสีเขียว
    np_img = np.array(image)
    green_mask = (np_img[:, :, 1] > np_img[:, :, 0]) & (np_img[:, :, 1] > np_img[:, :, 2])
    green_ratio = np.mean(green_mask)

    if green_ratio > 0.3:
        status = "ready"
    elif green_ratio > 0.05:
        status = "preparing"
    else:
        status = "not-ready"

    # 📊 อัปเดตสถานะใน grid_data.json
    grid_path = "grid_data.json"
    if not os.path.exists(grid_path):
        grid = [{"status": "not-ready"} for _ in range(80)]
    else:
        grid = json.load(open(grid_path, "r"))
    if 0 <= slot_id < len(grid):
        grid[slot_id] = {"status": status}
    json.dump(grid, open(grid_path, "w"), indent=2)

    return JSONResponse({
        "slot_id": slot_id,
        "green_ratio": round(float(green_ratio), 3),
        "status": status
    })
