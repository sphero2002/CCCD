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
from app.helpers.qr_utils import QRHelper
from app.services.gemini_service import GeminiService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QRService:
    def __init__(self):
        # Khởi tạo QRDetector một lần duy nhất khi ứng dụng bắt đầu
        self.detector = QRDetector(model_size='s')  # Sử dụng model_size='s' để khởi tạo
        self.qr_helper = QRHelper()  # Khởi tạo lớp QRHelper để tiền xử lý ảnh
        self.gemini_service = GeminiService()  # Khởi tạo GeminiService để OCR

    async def scan_CCCD_qr_code(self, file: UploadFile) -> CCCDQRCodeDTO:
        """
        Quét mã QR CCCD và OCR để trả về thông tin theo DTO
        Ưu tiên lấy id, create_date, birthdate từ QR code
        Các thông tin còn lại ưu tiên lấy từ OCR
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
                
                # Lưu nội dung file để sử dụng cho cả QR và OCR
                image_bytes = BytesIO(contents)
                image = Image.open(BytesIO(contents))
                frame = np.array(image)
            except Exception as e:
                logger.error(f"Error reading image file: {str(e)}")
                raise HTTPException(status_code=400, detail="Error reading image file")

            # Khởi tạo DTO với các giá trị rỗng
            cccd_data = CCCDQRCodeDTO(
                id="",
                old_id="",
                full_name="",
                birthdate="",
                sex="",
                address="",
                create_date=""
            )

            # Lưu kết quả QR scan (None nếu không thành công)
            qr_result = None
            
            # Step 1: Thử phát hiện và quét mã QR trước
            try:
                qr_result = await self._extract_qr_data(frame)
                if qr_result:
                    logger.info("Successfully extracted data from QR code, fixing encoding issues...")
                    
                    # Tạo copy của image_bytes để sử dụng cho việc sửa lỗi encoding
                    image_bytes_copy = BytesIO(contents)
                    
                    # Sửa lỗi encoding bằng Gemini nếu có kết quả QR
                    fixed_result = await self._fix_encoding_with_gemini(qr_result, image_bytes_copy, file.content_type)
                    if fixed_result:
                        qr_result = fixed_result
                        logger.info("Successfully fixed QR data encoding with Gemini")
                    
                    # Cập nhật các trường dữ liệu từ QR code đã sửa
                    for key, value in qr_result.dict().items():
                        setattr(cccd_data, key, value)
            except Exception as e:
                logger.warning(f"QR code extraction failed: {str(e)}")
                # Tiếp tục với OCR nếu QR không thành công
            
            # Step 2: Thực hiện OCR nếu cần thiết
            if not qr_result or self._should_perform_ocr(qr_result):
                try:
                    # Đặt lại vị trí con trỏ tệp về đầu để đọc lại
                    image_bytes.seek(0)
                    ocr_result = await self._extract_ocr_data(image_bytes, file.content_type)
                    
                    if ocr_result:
                        # Cập nhật các trường dữ liệu từ OCR
                        # Ưu tiên giữ lại các trường quan trọng từ QR code nếu có
                        self._merge_data_with_priority(cccd_data, ocr_result, qr_result)
                        logger.info("Successfully extracted data from OCR")
                except Exception as e:
                    logger.error(f"OCR extraction failed: {str(e)}")
                    # Nếu OCR thất bại và không có QR result, trả về lỗi
                    if not qr_result:
                        raise HTTPException(status_code=500, detail="Both QR and OCR extraction failed")
            
            # Kiểm tra nếu không có dữ liệu hợp lệ
            if not self._is_valid_cccd_data(cccd_data):
                raise HTTPException(status_code=404, detail="Could not extract valid CCCD data")
                
            return cccd_data
                
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in scan_CCCD_qr_code: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    async def _extract_qr_data(self, frame: np.ndarray) -> CCCDQRCodeDTO:
        """
        Trích xuất dữ liệu từ QR code.
        Lưu ý: Các trường văn bản có thể bị lỗi encoding với tiếng Việt.
        """
        # Phát hiện QR trong ảnh sử dụng QRDetector
        detections = self.detector.detect(image=frame, is_bgr=True)
        
        # Nếu không tìm thấy mã QR
        if not detections:
            return None
            
        # Giải mã QR từ các vùng phát hiện trong ảnh
        for index, detection in enumerate(detections):
            # Giải mã QR trực tiếp từ vùng ảnh
            decoded_info = self.qr_helper._decode_qr_zbar_v2(frame, detection)
            
            # Nếu giải mã thành công, xử lý dữ liệu QR
            if decoded_info:
                # Lấy dữ liệu từ đối tượng 'Decoded'
                for result in decoded_info[0]['results']:
                    try:
                        # Thử nhiều cách decode khác nhau để xử lý tiếng Việt
                        decoded_str = None
                        try:
                            # Cách 1: UTF-8 mặc định
                            decoded_str = result.data.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                # Cách 2: UTF-8 với error handler
                                decoded_str = result.data.decode('utf-8', errors='replace')
                            except:
                                try:
                                    # Cách 3: cp1258 (Vietnamese)
                                    decoded_str = result.data.decode('cp1258', errors='replace')
                                except:
                                    # Fallback: Latin-1 (ít nhất decode được dạng số)
                                    decoded_str = result.data.decode('latin-1', errors='replace')
                        
                        if not decoded_str:
                            continue
                            
                        parts = decoded_str.split("|")
                        if len(parts) < 6:
                            continue  # Thử QR tiếp theo nếu có

                        # Chỉ lấy các trường số và ngày tháng từ QR (ít bị ảnh hưởng bởi encoding)
                        try:
                            raw_birthdate = parts[3]
                            formatted_birthdate = datetime.strptime(raw_birthdate, "%d%m%Y").strftime("%d/%m/%Y")

                            raw_create_date = parts[6]
                            formatted_create_date = datetime.strptime(raw_create_date, "%d%m%Y").strftime("%d/%m/%Y")

                            return CCCDQRCodeDTO(
                                id=parts[0],
                                old_id=parts[1],
                                full_name=parts[2],  # Có thể bị lỗi encoding
                                birthdate=formatted_birthdate,
                                sex=parts[4],  # Có thể bị lỗi encoding
                                address=parts[5],  # Có thể bị lỗi encoding
                                create_date=formatted_create_date
                            )
                        except Exception as e:
                            logger.warning(f"Error parsing QR date fields: {str(e)}")
                            continue
                    except Exception as e:
                        logger.warning(f"Error processing QR result: {str(e)}")
                        continue
        return None

    async def _extract_ocr_data(self, image_bytes: BytesIO, mime_type: str) -> dict:
        """
        Trích xuất dữ liệu từ OCR sử dụng GeminiService.
        """
        json_format = """{
            "id": "Số CCCD, chỉ gồm số, không có chữ",
            "old_id": "Số CMND cũ (nếu có), chỉ gồm số",
            "full_name": "Họ và tên đầy đủ",
            "birthdate": "Ngày sinh (định dạng dd/mm/yyyy)",
            "sex": "Giới tính (Nam/Nữ)",
            "address": "Nơi thường trú/Quê quán đầy đủ",
            "create_date": null
        }"""
        
        prompt = await self.gemini_service.build_prompt(
            loai_giay_to="Căn cước công dân", 
            json_format=json_format,
            rule="""
            Lưu ý quan trọng:
            - Trích xuất các thông tin CHÍNH XÁC từ hình ảnh CCCD
            - Với tiếng Việt, phải giữ đúng dấu và chính tả
            - Định dạng ngày sinh là dd/mm/yyyy
            - Số CCCD chỉ gồm các số, không bao gồm chữ "Số:" hoặc các ký tự khác
            - Họ và tên viết đúng chính tả, đúng chữ hoa chữ thường theo giấy tờ
            - Địa chỉ phải đầy đủ, chính xác theo giấy tờ, không viết tắt
            - Nếu không thấy thông tin ngày cấp (Ngày, tháng, năm), để create_date là null
            """
        )
        
        try:
            # Đặt lại vị trí con trỏ tệp về đầu để đọc
            image_bytes.seek(0)
            
            # Gọi Gemini API để trích xuất thông tin
            ocr_result = await self.gemini_service.extract_content_from_stream_async(
                image_bytes, 
                mime_type, 
                prompt
            )
            
            # Xử lý kết quả - nếu API trả về "null" thì không phải CCCD
            if ocr_result == "null":
                logger.warning("Image is not a valid CCCD")
                return None
                
            # Parse JSON kết quả
            try:
                import json
                ocr_data = json.loads(ocr_result)
                
                # Clean up data - ensure no "Số:" prefix in IDs
                if ocr_data.get("id"):
                    ocr_data["id"] = ocr_data["id"].replace("Số:", "").replace("Số", "").strip()
                if ocr_data.get("old_id"):
                    ocr_data["old_id"] = ocr_data["old_id"].replace("Số:", "").replace("Số", "").strip()
                
                return ocr_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OCR result as JSON: {str(e)}")
                # Có thể xử lý text không phải JSON ở đây nếu cần
                return None
                
        except Exception as e:
            logger.error(f"Error in OCR extraction: {str(e)}")
            return None
            
    def _should_perform_ocr(self, qr_result: CCCDQRCodeDTO) -> bool:
        """
        Kiểm tra xem có nên thực hiện OCR để bổ sung thông tin hay không.
        """
        # Thực hiện OCR nếu thiếu bất kỳ trường thông tin nào (trừ create_date)
        if not qr_result.id or not qr_result.full_name or not qr_result.birthdate:
            return True
        if not qr_result.sex or not qr_result.address:
            return True
        return False
    
    def _merge_data_with_priority(self, target: CCCDQRCodeDTO, ocr_data: dict, qr_data: CCCDQRCodeDTO = None):
        """
        Gộp dữ liệu từ OCR và QR theo ưu tiên.
        Ưu tiên id, birthdate, create_date từ QR code
        LUÔN ưu tiên các trường text từ OCR do QR thường bị lỗi encoding với tiếng Việt
        """
        # LUÔN ưu tiên các trường text từ OCR do QR thường bị lỗi encoding với tiếng Việt
        if ocr_data.get("full_name"):
            target.full_name = ocr_data["full_name"]
        if ocr_data.get("sex"):
            target.sex = ocr_data["sex"]
        if ocr_data.get("address"):
            target.address = ocr_data["address"]
        if ocr_data.get("old_id") and (not qr_data or not qr_data.old_id):
            target.old_id = ocr_data["old_id"]
            
        # Các trường ưu tiên từ QR nếu có, nếu không thì lấy từ OCR
        if qr_data:
            # Chỉ lấy các trường số và ngày tháng từ QR code
            if qr_data.id:
                target.id = qr_data.id
            if qr_data.birthdate:
                target.birthdate = qr_data.birthdate
            if qr_data.create_date:
                target.create_date = qr_data.create_date
        
        # Nếu không có QR data hoặc các trường quan trọng bị thiếu, lấy từ OCR
        if not target.id and ocr_data.get("id"):
            target.id = ocr_data["id"]
        if not target.birthdate and ocr_data.get("birthdate"):
            target.birthdate = ocr_data["birthdate"]
        # create_date thường không có trong ảnh CCCD, nên để trống nếu không có QR

    def _is_valid_cccd_data(self, data: CCCDQRCodeDTO) -> bool:
        """
        Kiểm tra xem dữ liệu CCCD có đủ các trường bắt buộc không.
        """
        # Ít nhất phải có id và tên
        if not data.id or not data.full_name:
            return False
        return True

    async def _fix_encoding_with_gemini(self, qr_data: CCCDQRCodeDTO, image_bytes: BytesIO, mime_type: str) -> CCCDQRCodeDTO:
        """
        Sửa lỗi encoding trong dữ liệu QR bằng cách gửi cả dữ liệu QR và ảnh đến Gemini.
        Gemini sẽ giữ nguyên các trường số và ngày tháng nhưng sửa các trường text bị lỗi encoding.
        
        Args:
            qr_data: Dữ liệu QR đã quét có thể bị lỗi encoding
            image_bytes: File ảnh CCCD để Gemini trích xuất text chính xác
            mime_type: Loại mime của file ảnh
            
        Returns:
            CCCDQRCodeDTO với các trường văn bản đã được sửa đúng
        """
        try:
            import json
            import re
            
            # Tạo prompt đặc biệt cho Gemini
            # Cung cấp cả dữ liệu QR đã quét và yêu cầu sửa lỗi encoding
            prompt = f"""Bạn là trợ lý sửa lỗi encoding tiếng Việt trong dữ liệu CCCD. 

Dữ liệu CCCD đã quét từ QR code: 
```
{json.dumps(qr_data.dict(), ensure_ascii=False, indent=2)}
```

Hình ảnh chứa thẻ CCCD đính kèm. Nhiệm vụ của bạn là:

1. Giữ nguyên giá trị các trường số và ngày tháng trong dữ liệu QR code (id, old_id, birthdate, create_date)
2. Sửa lại các trường văn bản (full_name, sex, address) dựa vào hình ảnh CCCD
3. Trả về kết quả định dạng JSON chính xác, giữ nguyên cấu trúc, chỉ sửa các trường bị lỗi encoding

Trả về kết quả dưới dạng JSON thuần túy (không có giải thích hay diễn giải):
{{
  "id": "{qr_data.id}",
  "old_id": "{qr_data.old_id}",
  "full_name": "TÊN THẬT TỪ ẢNH",
  "birthdate": "{qr_data.birthdate}",
  "sex": "GIỚI TÍNH THẬT TỪ ẢNH",
  "address": "ĐỊA CHỈ THẬT TỪ ẢNH",
  "create_date": "{qr_data.create_date}"
}}

CHÚ Ý: 
- KHÔNG thay đổi thông tin id, old_id, birthdate, và create_date
- CHỈ sửa full_name, sex, address để khớp với ảnh
- Phải giữ đúng định dạng ngày tháng dd/mm/yyyy
- Giữ đúng các dấu tiếng Việt trong tên và địa chỉ
"""

            # Gọi API Gemini để sửa dữ liệu
            image_bytes.seek(0)
            response = await self.gemini_service.extract_content_from_stream_async(
                image_bytes,
                mime_type,
                prompt
            )
            
            # Log original response for debugging
            logger.info(f"Gemini response: {response}")
            
            try:
                # Xử lý response để loại bỏ markdown code blocks nếu có
                # Pattern để tìm JSON trong code block markdown: ```json ... ```
                json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
                match = re.search(json_pattern, response)
                
                if match:
                    # Nếu tìm thấy JSON trong markdown code block, lấy nội dung bên trong
                    cleaned_response = match.group(1).strip()
                    logger.info(f"Extracted JSON from markdown: {cleaned_response}")
                else:
                    # Nếu không tìm thấy pattern, sử dụng response gốc
                    cleaned_response = response.strip()
                
                # Parse JSON response sau khi đã làm sạch
                fixed_data = json.loads(cleaned_response)
                
                # Tạo CCCDQRCodeDTO mới với dữ liệu đã sửa
                return CCCDQRCodeDTO(
                    id=qr_data.id,  # Giữ nguyên các trường số và ngày tháng từ QR code
                    old_id=qr_data.old_id,
                    birthdate=qr_data.birthdate,
                    create_date=qr_data.create_date,
                    # Sử dụng các trường text đã được sửa
                    full_name=fixed_data.get("full_name", qr_data.full_name),
                    sex=fixed_data.get("sex", qr_data.sex),
                    address=fixed_data.get("address", qr_data.address)
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
                return qr_data  # Return original data if parsing fails
                
        except Exception as e:
            logger.error(f"Error fixing encoding with Gemini: {str(e)}")
            return qr_data  # Return original data if any error occurs
