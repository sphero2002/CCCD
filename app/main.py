from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.item_controller import router as item_router
from app.controllers.qr_controller import router as qr_router

app = FastAPI()

app = FastAPI()

# Thêm middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc thay "*" bằng danh sách các nguồn gốc cụ thể như ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Hoặc thay "*" bằng danh sách các phương thức như ["GET", "POST"]
    allow_headers=["*"],  # Hoặc thay "*" bằng danh sách các header được phép như ["Content-Type", "Authorization"]
)

# Đăng ký router cho các API
app.include_router(item_router, prefix="/items", tags=["Items"])
app.include_router(qr_router, prefix="/qr", tags=["QR Codes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Project"}
