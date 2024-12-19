import os
import cv2
import numpy as np
from qrdet import QRDetector
from app.models.CCCD_dto import CCCDQRCodeDTO
from fastapi import UploadFile, HTTPException
from io import BytesIO
from PIL import Image
import logging
from datetime import datetime
from app.helpers.qr_utils import QRHelper   # Import the QRHelper class

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QRService:
    def __init__(self):
        # Khởi tạo QRDetector một lần duy nhất khi ứng dụng bắt đầu
        self.detector = QRDetector(model_size='s')  # Sử dụng model_size='s' để khởi tạo
        self.qr_helper = QRHelper()  # Khởi tạo lớp QRHelper để tiền xử lý ảnh

    async def scan_CCCD_qr_code(self, file: UploadFile) -> CCCDQRCodeDTO:
        """
        Quét mã QR CCCD và trả về thông tin theo DTO
        """
        try:
            # Kiểm tra file
            if not file:
                raise HTTPException(status_code=400, detail="No file uploaded")

            # Kiểm tra định dạng file
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")

            # Đọc file ảnh
            try:
                contents = await file.read()
                if not contents:
                    raise HTTPException(status_code=400, detail="Empty file")
                image = Image.open(BytesIO(contents))
                frame = np.array(image)
            except Exception as e:
                logger.error(f"Error reading image file: {str(e)}")
                raise HTTPException(status_code=400, detail="Error reading image file")

            # Phát hiện QR trong ảnh sử dụng QRDetector
            try:
                detections = self.detector.detect(image=frame, is_bgr=True)
            except Exception as e:
                logger.error(f"Error detecting QR code with QRDetector: {str(e)}")
                raise HTTPException(status_code=500, detail="Error detecting QR code")

            # Nếu không tìm thấy mã QR
            if not detections:
                raise HTTPException(status_code=404, detail="No QR code detected")

            # Tạo thư mục để lưu ảnh crop nếu chưa tồn tại
            output_folder = "output_crops"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Giải mã QR từ các vùng phát hiện trong ảnh
            for index, detection in enumerate(detections):
                try:
                    # Giải mã QR trực tiếp từ vùng ảnh sử dụng _decode_qr_zbar_v2
                    decoded_info = self.qr_helper._decode_qr_zbar_v2(frame, detection)

                    # Nếu giải mã thành công, xử lý dữ liệu QR
                    if decoded_info:
                        logger.info(f"QR code decoded: {decoded_info}")
                        # Sửa lỗi truy cập thuộc tính 'data' từ đối tượng 'Decoded'
                        for result in decoded_info[0]['results']:
                            decoded_str = result.data.decode('utf-8')  # Lấy dữ liệu từ đối tượng 'Decoded'
                            parts = decoded_str.split("|")
                            if len(parts) < 6:
                                raise ValueError("Invalid QR code data format")

                            raw_birthdate = parts[3]
                            formatted_birthdate = datetime.strptime(raw_birthdate, "%d%m%Y").strftime("%d/%m/%Y")

                            raw_create_date = parts[6]
                            formatted_create_date = datetime.strptime(raw_create_date, "%d%m%Y").strftime("%d/%m/%Y")

                            return CCCDQRCodeDTO(
                                id=parts[0],
                                old_id=parts[1],
                                full_name=parts[2],
                                birthdate=formatted_birthdate,
                                sex=parts[4],
                                address=parts[5],
                                create_date=formatted_create_date
                            )
                    else:
                        raise HTTPException(status_code=404, detail="QR code not decoded")
                except Exception as e:
                    logger.error(f"Error processing QR code {index+1}: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Error processing QR code {index+1}: {str(e)}")
        except Exception as e:
            logger.error(f"Error in scan_CCCD_qr_code: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
