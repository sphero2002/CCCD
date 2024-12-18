from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.qr_service import QRService
from app.models.CCCD_dto import CCCDQRCodeDTO

router = APIRouter()

# Tạo instance của QRService
qr_service = QRService()

@router.get("/qr")
async def get_qr():
    return {"message": "QR code endpoint"}

@router.post("/cccd/scan", response_model=CCCDQRCodeDTO)
async def scan_CCCD_qr_code(file: UploadFile = File(...)):
    """
    API quét mã QR CCCD.
    """
    return await qr_service.scan_CCCD_qr_code(file)