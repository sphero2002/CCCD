from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.item_controller import router as item_router
from app.controllers.qr_controller import router as qr_router
from app.controllers.process_file_controller import router as process_file_router
from app.controllers.gemini_controller import router as gemini_router

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
app.include_router(process_file_router, prefix="/process", tags=["Process Files Gemini"])
app.include_router(gemini_router, prefix="/gemini", tags=["Gemini"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Project"}
