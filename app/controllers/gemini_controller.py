from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from io import BytesIO
import mimetypes
import traceback
import logging
from app.services.gemini_service import GeminiService
from app.models.response_models import ApiResponse
import json

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Create an instance of GeminiService
gemini_service = GeminiService()

@router.get("/gemini", response_model=ApiResponse[Dict[str, str]])
async def get_gemini():
    """Get status of Gemini API endpoint"""
    return ApiResponse(
        success=True,
        message="API endpoint available",
        data={"status": "Gemini API endpoint is active"}
    )

@router.post("/extract-trich-luc-khai-tu", tags=["Gemini"])
async def extract_trich_luc_khai_tu(file: UploadFile = File(...)):
    """
    Extract information from a Trích lục khai tử document image.
    
    Args:
        file: The uploaded document image file
        
    Returns:
        JSON response containing extracted information or error message
    """
    try:
        # Read file content and create stream
        file_content = await file.read()
        media_stream = BytesIO(file_content)
        
        # Determine MIME type
        mime_type = file.content_type
        if not mime_type:
            mime_type = mimetypes.guess_type(file.filename)[0]
            
        logger.info(f"Processing file: {file.filename}, Content-Type: {mime_type}, Size: {len(file_content)} bytes")
        
        # Validate document type first
        is_valid = await gemini_service.validate_document_type(media_stream, mime_type, "Trích lục khai tử")
        if not is_valid:
            logger.warning("Document type validation failed")
            return {
                "success": False,
                "message": "Lỗi xác thực loại giấy tờ",
                "data": None,
                "errors": ["Đây không phải là Trích lục khai tử. Vui lòng tải lên đúng loại giấy tờ."]
            }
            
        # Reset stream position for further processing
        media_stream.seek(0)
        
        # Build JSON format and rules
        json_format = """{
    "ubnd": "", // UBND
    "so_giay_to": "", // Số giấy tờ
    "dia_diem_ngay_lam_giay_to": "", // Địa điểm ngày làm giấy tờ
    "nguoi_mat_ho_va_ten": "", // Họ và tên người mất
    "nguoi_mat_ngay_sinh": "", // Ngày sinh
    "nguoi_mat_gioi_tinh": "", // Giới tính
    "nguoi_mat_dan_toc": "", // Dân tộc
    "nguoi_mat_quoc_tich": "", // Quốc tịch
    "nguoi_mat_so_dinh_danh_ca_nhan": "", // Số định danh cá nhân
    "nguoi_mat_so_chung_minh_nhan_dan": "", // Số chứng minh nhân dân
    "nguoi_mat_so_can_cuoc_cong_dan": "", // Số căn cước công dân
    "nguoi_mat_giay_to_noi_cap": "", // Giấy tờ nơi cấp
    "nguoi_mat_giay_to_ngay_cap": "", // Ngày cấp
    "nguoi_mat_thoi_gian_mat": "", // Thời gian mất
    "nguoi_mat_noi_mat": "", // Nơi mất
    "nguoi_mat_nguyen_nhan_chet": "" // Nguyên nhân chết
}"""
        
        rules = """
1. Giữ nguyên định dạng ngày tháng (dd/mm/yyyy)
2. Giữ nguyên số giấy tờ
3. Nếu một trường nào đó không có thông tin, để giá trị là null
4. Không thêm bất kỳ ký tự nào khác ngoài thông tin trong giấy tờ
5. Hình ảnh có thể có dạng bảng người ta viết đè vào giữa 2 ô thì hãy coi đó là merge cell và extract ra kết quả
"""
        
        # Process the file
        result = await gemini_service.extract_content_from_stream_async(
            media_stream,
            mime_type,
            await gemini_service.build_prompt("Trích lục khai tử", json_format, rules)
        )
        
        # Return the result directly since it's already a JSON string
        return {
            "success": True,
            "message": "Trích xuất thông tin thành công",
            "data": result,
            "errors": []
        }
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            "success": False,
            "message": "Lỗi khi xử lý file",
            "data": None,
            "errors": [str(e)]
        }
    
@router.post("/extract-giay-chung-nhan-ket-hon", tags=["Gemini"])
async def extract_giay_chung_nhan_ket_hon(file: UploadFile = File(...)):
    """
    Extract information from a Giấy chứng nhận kết hôn document image.
    
    Args:
        file: The uploaded document image file
        
    Returns:
        JSON response containing extracted information or error message
    """
    try:
        # Read file content and create stream
        file_content = await file.read()
        media_stream = BytesIO(file_content)
        
        # Determine MIME type
        mime_type = file.content_type
        if not mime_type:
            mime_type = mimetypes.guess_type(file.filename)[0]
            
        logger.info(f"Processing file: {file.filename}, Content-Type: {mime_type}, Size: {len(file_content)} bytes")
        
        # Validate document type first
        is_valid = await gemini_service.validate_document_type(media_stream, mime_type, "Giấy chứng nhận kết hôn")
        if not is_valid:
            logger.warning("Document type validation failed")
            return {
                "success": False,
                "message": "Lỗi xác thực loại giấy tờ",
                "data": None,
                "errors": ["Đây không phải là Giấy chứng nhận kết hôn. Vui lòng tải lên đúng loại giấy tờ."]
            }
            
        # Reset stream position for further processing
        media_stream.seek(0)
        
        # Build JSON format and rules
        json_format = """{
    "so": "", // Số
    "quyen_so": "", // Quyển số
    "mau": "", // Mẫu
    "trich_yeu": "", // Trích yêu
    "ngay_dang_ky": "", // Ngày đăng ký
    "noi_dang_ky": "", // Nơi đăng ký
    
    "chong_ho_ten": "", // Họ tên chồng
    "chong_ngay_sinh": "", // Ngày sinh chồng
    "chong_que_quan": "", // Quê quán chồng
    "chong_noi_thuong_tru": "", // Nơi thường trú chồng
    "chong_nghe_nghiep": "", // Nghề nghiệp chồng
    "chong_dan_toc": "", // Dân tộc chồng
    "chong_quoc_tich": "", // Quốc tịch chồng

    "vo_ho_ten": "", // Họ tên vợ
    "vo_ngay_sinh": "", // Ngày sinh vợ
    "vo_que_quan": "", // Quê quán vợ
    "vo_noi_thuong_tru": "", // Nơi thường trú vợ
    "vo_nghe_nghiep": "", // Nghề nghiệp vợ
    "vo_dan_toc": "", // Dân tộc vợ
    "vo_quoc_tich": "" // Quốc tịch vợ
}"""
        
        rules = """
1. Giữ nguyên định dạng ngày tháng (dd/mm/yyyy)
2. Giữ nguyên số giấy tờ và quyển số
3. Nếu một trường nào đó không có thông tin, để giá trị là null
4. Không thêm bất kỳ ký tự nào khác ngoài thông tin trong giấy tờ
5. Hình ảnh có thể có dạng bảng người ta viết đè vào giữa 2 ô thì hãy coi đó là merge cell và extract ra kết quả
"""
        
        # Process the file
        result = await gemini_service.extract_content_from_stream_async(
            media_stream,
            mime_type,
            await gemini_service.build_prompt("Giấy chứng nhận kết hôn", json_format, rules)
        )
        
        # Return the result directly since it's already a JSON string
        return {
            "success": True,
            "message": "Trích xuất thông tin thành công",
            "data": result,
            "errors": []
        }
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            "success": False,
            "message": "Lỗi khi xử lý file",
            "data": None,
            "errors": [str(e)]
        }

@router.post("/extract-giay-khai-sinh", tags=["Gemini"])
async def extract_giay_khai_sinh(file: UploadFile = File(...)):
    """
    Extract information from a Giấy khai sinh document image.
    
    Args:
        file: The uploaded document image file
        
    Returns:
        JSON response containing extracted information or error message
    """
    try:
        # Read file content and create stream
        file_content = await file.read()
        media_stream = BytesIO(file_content)
        
        # Determine MIME type
        mime_type = file.content_type
        if not mime_type:
            mime_type = mimetypes.guess_type(file.filename)[0]
            
        logger.info(f"Processing file: {file.filename}, Content-Type: {mime_type}, Size: {len(file_content)} bytes")
        
        # Validate document type first
        is_valid = await gemini_service.validate_document_type(media_stream, mime_type, "Giấy khai sinh")
        if not is_valid:
            logger.warning("Document type validation failed")
            return {
                "success": False,
                "message": "Lỗi xác thực loại giấy tờ",
                "data": None,
                "errors": ["Đây không phải là Giấy khai sinh. Vui lòng tải lên đúng loại giấy tờ."]
            }
            
        # Reset stream position for further processing
        media_stream.seek(0)
        
        # Build JSON format and rules
        json_format = """{
    "so_giay_khai_sinh": "", // Số giấy khai sinh
    "ho_va_ten": "", // Họ và tên
    "gioi_tinh": "", // Giới tính
    "ngay_sinh": "", // Ngày sinh
    "noi_sinh": "", // Nơi sinh
    "quoc_tich": "", // Quốc tịch
    "dan_toc": "", // Dân tộc
    "que_quan": "", // Quê quán
    "noi_thuong_tru": "", // Nơi thường trú
    "ho_ten_cha": "", // Họ tên cha
    "nam_sinh_cha": "", // Năm sinh cha
    "dan_toc_cha": "", // Dân tộc cha
    "quoc_tich_cha": "", // Quốc tịch cha
    "noi_thuong_tru_hoac_tam_tru_cha": "", // Nơi thường trú hoặc tạm trú cha
    "que_quan_cha": "", // Quê quán cha
    "ho_ten_me": "", // Họ tên mẹ
    "nam_sinh_me": "", // Năm sinh mẹ
    "dan_toc_me": "", // Dân tộc mẹ
    "quoc_tich_me": "", // Quốc tịch mẹ
    "noi_thuong_tru_hoac_tam_tru_me": "", // Nơi thường trú hoặc tạm trú mẹ
    "que_quan_me": "", // Quê quán mẹ
    "ngay_dang_ky": "", // Ngày đăng ký
    "nguoi_dang_ky": "", // Người đăng ký
    "quan_he_voi_nguoi_duoc_khai_sinh": "" // Quan hệ với người được khai sinh
}"""
        
        rules = """
1. Giữ nguyên định dạng ngày tháng (dd/mm/yyyy)
2. Giữ nguyên số giấy khai sinh và quyển số
3. Nếu một trường nào đó không có thông tin, để giá trị là null
4. Không thêm bất kỳ ký tự nào khác ngoài thông tin trong giấy tờ
5. Hình ảnh có thể có dạng bảng người ta viết đè vào giữa 2 ô thì hãy coi đó là merge cell và extract ra kết quả
"""
        
        # Process the file
        result = await gemini_service.extract_content_from_stream_async(
            media_stream,
            mime_type,
            await gemini_service.build_prompt("Giấy khai sinh", json_format, rules)
        )
        
        # Return the result directly since it's already a JSON string
        return {
            "success": True,
            "message": "Trích xuất thông tin thành công",
            "data": result,
            "errors": []
        }
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            "success": False,
            "message": "Lỗi khi xử lý file",
            "data": None,
            "errors": [str(e)]
        }

@router.post("/extract-content-from-file", response_model=ApiResponse[Dict[str, str]])
async def extract_content_from_file(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form("Describe the content of this media.")
):
    """
    Extract content from a media file using Gemini API.
    
    Args:
        file: The media file to analyze
        prompt: Optional prompt to guide the content extraction
    
    Returns:
        ApiResponse with the extracted content
    """
    try:
        # Log basic file info
        logger.info(f"Processing file: {file.filename}, Content-Type: {file.content_type}, Size: unknown")
        
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        logger.info(f"File size: {file_size_mb:.2f}MB")
        
        mime_type = file.content_type
        
        if not mime_type:
            # Try to determine MIME type from filename
            mime_type, _ = mimetypes.guess_type(file.filename)
            logger.info(f"MIME type from filename: {mime_type}")
            
        if not mime_type:
            logger.warning("Could not determine file MIME type")
            return ApiResponse(
                success=False,
                message="Invalid file format",
                errors=["Could not determine file MIME type"]
            )
        
        # Validate MIME type before sending to service
        if not gemini_service._is_valid_mime_type(mime_type):
            logger.warning(f"Unsupported MIME type: {mime_type}")
            return ApiResponse(
                success=False,
                message="Unsupported file format",
                errors=[f"Unsupported MIME type: {mime_type}. Gemini API only supports images and PDFs."]
            )
        
        # Check file size before sending to service
        if file_size_mb > 20:
            logger.warning(f"File too large: {file_size_mb:.2f}MB")
            return ApiResponse(
                success=False,
                message="File too large",
                errors=[f"File size {file_size_mb:.2f}MB exceeds the 20MB limit for Gemini API."]
            )
        
        file_stream = BytesIO(content)
        result = await gemini_service.extract_content_from_stream_async(file_stream, mime_type, prompt)
        
        return ApiResponse(
            success=True,
            message="Content extracted successfully",
            data={"content": result}
        )
    except ValueError as e:
        # Handle validation errors (invalid MIME type, empty file, etc.)
        logger.warning(f"Validation error: {str(e)}")
        return ApiResponse(
            success=False,
            message="Validation error",
            errors=[str(e)]
        )
    except Exception as e:
        # Handle API errors and other exceptions
        logger.error(f"Error extracting content: {str(e)}")
        logger.error(traceback.format_exc())
        error_details = str(e)
        return ApiResponse(
            success=False,
            message="An error occurred while extracting content",
            errors=[error_details]
        )

@router.post("/extract-content-from-url", response_model=ApiResponse[Dict[str, str]])
async def extract_content_from_url(
    file_url: str = Form(...),
    prompt: Optional[str] = Form("Describe the content of this media.")
):
    """
    Extract content from a media file URL using Gemini API.
    
    Args:
        file_url: URL of the media file
        prompt: Optional prompt to guide the content extraction
    
    Returns:
        ApiResponse with the extracted content
    """
    try:
        logger.info(f"Processing file URL: {file_url}")
        
        result = await gemini_service.extract_content_from_url_async(file_url, prompt)
        return ApiResponse(
            success=True,
            message="Content extracted successfully",
            data={"content": result}
        )
    except ValueError as e:
        # Handle validation errors (invalid URL, unsupported MIME type)
        logger.warning(f"Validation error: {str(e)}")
        return ApiResponse(
            success=False,
            message="Validation error",
            errors=[str(e)]
        )
    except Exception as e:
        # Handle API errors and other exceptions
        logger.error(f"Error extracting content from URL: {str(e)}")
        logger.error(traceback.format_exc())
        return ApiResponse(
            success=False,
            message="An error occurred while extracting content from URL",
            errors=[str(e)]
        )