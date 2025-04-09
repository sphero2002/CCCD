import json
import base64
import os
import httpx
import asyncio
import mimetypes
import logging
from typing import Optional, List, Dict, Any
from io import BytesIO

# Setup logging
logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self):
        self._api_keys = self._load_api_keys()
        self._current_key_index = 0
        self._gemini_api_base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    def _load_api_keys(self) -> List[str]:
        """Load API keys from api_key.json file."""
        try:
            with open("api_key.json", "r") as file:
                data = json.load(file)
                if "api_keys" not in data or not data["api_keys"]:
                    raise ValueError("API keys not found in configuration")
                return data["api_keys"]
        except Exception as e:
            logger.error(f"Failed to load API keys: {str(e)}")
            raise ValueError(f"Failed to load API keys: {str(e)}")
    
    def _get_next_api_key(self) -> str:
        """Get the next API key in rotation."""
        key = self._api_keys[self._current_key_index]
        self._current_key_index = (self._current_key_index + 1) % len(self._api_keys)
        return key
    
    async def extract_content_from_stream_async(self, media_stream: BytesIO, mime_type: str, prompt: str = "Describe the content of this media.") -> str:
        """
        Extract content from a media file using Gemini API.
        
        Args:
            media_stream: The media file as BytesIO.
            mime_type: The MIME type of the media.
            prompt: Optional prompt to guide the content extraction.
            
        Returns:
            Extracted content as text.
        """
        if not media_stream or media_stream.getbuffer().nbytes == 0:
            logger.error("Media stream is null or empty")
            raise ValueError("Media stream cannot be null or empty")
        
        if not mime_type:
            logger.error("MIME type is not provided")
            raise ValueError("MIME type must be provided")
        
        if not self._is_valid_mime_type(mime_type):
            logger.error(f"Unsupported MIME type: {mime_type}")
            raise ValueError(f"Unsupported MIME type: {mime_type}")
        
        # Check file size
        media_size_mb = media_stream.getbuffer().nbytes / (1024 * 1024)
        if media_size_mb > 20:  # Gemini API typically has a limit around 20MB
            logger.error(f"File size too large: {media_size_mb:.2f}MB")
            raise ValueError(f"File size too large: {media_size_mb:.2f}MB. Maximum allowed is 20MB.")
        
        max_retries = 3
        current_retry = 0
        base_delay = 1
        
        while current_retry < max_retries:
            try:
                api_key = self._get_next_api_key()
                url = f"{self._gemini_api_base_url}?key={api_key}"
                
                media_stream.seek(0)
                base64_content = base64.b64encode(media_stream.read()).decode('utf-8')
                
                request_data = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": mime_type,
                                        "data": base64_content
                                    }
                                },
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generation_config": {
                        "temperature": 0.4,
                        "top_p": 0.95,
                        "top_k": 40
                    }
                }
                
                logger.info(f"Sending request to Gemini API (attempt {current_retry + 1}/{max_retries})")
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, 
                        json=request_data,
                        timeout=60.0  # Longer timeout for media processing
                    )
                    
                    if response.status_code == 429:  # Too Many Requests
                        current_retry += 1
                        if current_retry >= max_retries:
                            logger.error("Rate limit exceeded after maximum retries")
                            raise Exception("Đã vượt quá giới hạn yêu cầu. Vui lòng thử lại sau.")
                        
                        delay = base_delay * (2 ** (current_retry - 1))
                        logger.warning(f"Rate limit exceeded, retrying in {delay} seconds")
                        await asyncio.sleep(delay)
                        continue
                    
                    # Try to get detailed error information if available
                    if response.status_code >= 400:
                        error_json = response.json() if response.content else {}
                        error_message = f"API Error {response.status_code}"
                        
                        if "error" in error_json:
                            if "message" in error_json["error"]:
                                error_message = f"{error_message}: {error_json['error']['message']}"
                            if "details" in error_json["error"]:
                                error_details = "; ".join([str(detail) for detail in error_json["error"]["details"]])
                                error_message = f"{error_message} - Details: {error_details}"
                        
                        logger.error(f"API Error: {error_message}")
                        raise Exception(error_message)
                    
                    response.raise_for_status()
                    response_data = response.json()
                    
                    if (response_data.get("candidates") and 
                        len(response_data["candidates"]) > 0 and 
                        response_data["candidates"][0].get("content") and 
                        response_data["candidates"][0]["content"].get("parts") and 
                        len(response_data["candidates"][0]["content"]["parts"]) > 0):
                        logger.info("Successfully extracted content from media")
                        return response_data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    logger.error("Invalid response format from API")
                    raise Exception("Không thể trích xuất nội dung từ media: Phản hồi không hợp lệ từ API.")
                
            except httpx.HTTPStatusError as ex:
                current_retry += 1
                if current_retry >= max_retries:
                    error_message = f"HTTP Error {ex.response.status_code}"
                    try:
                        error_json = ex.response.json()
                        if "error" in error_json and "message" in error_json["error"]:
                            error_message = f"{error_message}: {error_json['error']['message']}"
                    except:
                        pass
                    logger.error(f"HTTP Error after maximum retries: {error_message}")
                    raise Exception(f"Lỗi khi gọi API Gemini: {error_message}")
                
                delay = base_delay * (2 ** (current_retry - 1))
                logger.warning(f"HTTP Error, retrying in {delay} seconds: {str(ex)}")
                await asyncio.sleep(delay)
                
            except Exception as ex:
                current_retry += 1
                if current_retry >= max_retries:
                    logger.error(f"Error after maximum retries: {str(ex)}")
                    raise Exception(f"Lỗi khi gọi API Gemini: {str(ex)}")
                
                delay = base_delay * (2 ** (current_retry - 1))
                logger.warning(f"Error, retrying in {delay} seconds: {str(ex)}")
                await asyncio.sleep(delay)
        
        logger.error("Exceeded maximum number of retries")
        raise Exception("Đã vượt quá số lần thử lại cho phép.")
    
    async def extract_content_from_url_async(self, file_url: str, prompt: str = "Describe the content of this media.") -> str:
        """
        Extract content from a media file URL using Gemini API.
        
        Args:
            file_url: URL of the media file.
            prompt: Optional prompt to guide the content extraction.
            
        Returns:
            Extracted content as text.
        """
        if not file_url:
            raise ValueError("File URL cannot be empty")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(file_url)
                response.raise_for_status()
                
                content_type = response.headers.get("content-type")
                if not content_type:
                    content_type = self._get_mime_type_from_url(file_url)
                
                if not content_type:
                    raise ValueError("Could not determine MIME type from URL or response")
                
                if not self._is_valid_mime_type(content_type):
                    raise ValueError(f"Unsupported MIME type: {content_type}")
                
                # Check file size
                content_length = len(response.content)
                content_length_mb = content_length / (1024 * 1024)
                if content_length_mb > 20:  # Gemini API typically has a limit around 20MB
                    raise ValueError(f"File size too large: {content_length_mb:.2f}MB. Maximum allowed is 20MB.")
                
                memory_stream = BytesIO(response.content)
                
                return await self.extract_content_from_stream_async(memory_stream, content_type, prompt)
                
        except Exception as ex:
            raise Exception(f"Lỗi khi xử lý URL: {str(ex)}")
    
    def _is_valid_mime_type(self, mime_type: str) -> bool:
        """Check if the MIME type is valid for Gemini API."""
        if not mime_type:
            return False
        
        # List of mime types supported by Gemini Vision
        valid_types = [
            "image/jpeg", 
            "image/png",
            "image/gif",
            "image/webp",
            "image/heic",
            "application/pdf"
        ]
        
        # Check exact match first
        if mime_type.lower() in valid_types:
            return True
            
        # Check for broader types
        valid_prefixes = [
            "image/",
            "application/pdf"
        ]
        
        return any(mime_type.lower().startswith(t) for t in valid_prefixes)
    
    def _get_mime_type_from_url(self, url: str) -> Optional[str]:
        """Get MIME type from URL file extension."""
        extension = os.path.splitext(url)[1].lower()
        
        mime_mapping = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".heic": "image/heic",
            ".pdf": "application/pdf"
        }
        
        return mime_mapping.get(extension)
    
    async def build_prompt(self, loai_giay_to: str, json_format: str, rule: str = "") -> str:
        """
        Builds a prompt for the Gemini API to extract information from document images
        and structure it according to a provided JSON format.
        
        Args:
            loai_giay_to: The expected document type (e.g., "CCCD", "CMND", "Passport")
            json_format: The JSON format/template to be filled with extracted information
            rule: Additional rules or instructions for processing the document
            
        Returns:
            A structured prompt for the Gemini API
        """
        return f"""Bạn là một trợ lý phân tích dữ liệu. Nhiệm vụ đầu tiên và QUAN TRỌNG NHẤT của bạn là xác định xem hình ảnh có đúng là "{loai_giay_to}" không.

LOẠI GIẤY TỜ CẦN KIỂM TRA: {loai_giay_to}

==== QUY TRÌNH XỬ LÝ ====

1. KIỂM TRA LOẠI GIẤY TỜ (QUAN TRỌNG NHẤT):
   - Nếu hình ảnh KHÔNG PHẢI "{loai_giay_to}":
     + Phản hồi của bạn PHẢI CHÍNH XÁC là: null
     + KHÔNG trả về JSON
     + KHÔNG thêm dấu ngoặc {{}}
     + KHÔNG thêm dấu ngoặc kép ""
     + KHÔNG thêm bất kỳ giải thích nào
     + CHỈ trả về chữ "null" (không có dấu ngoặc kép)

2. CHỈ KHI hình ảnh ĐÚNG LÀ "{loai_giay_to}", hãy trích xuất thông tin theo mẫu JSON:
```json
{json_format}
```
HƯỚNG DẪN NẾU ĐÚNG LOẠI GIẤY TỜ:

Trích xuất tất cả thông tin từ hình ảnh và điền vào mẫu JSON.
Nếu một trường nào đó không có thông tin, để giá trị là null.
Định dạng ngày tháng tiêu chuẩn là dd/mm/yyyy.
Giữ số CMND/CCCD và các số khác như trong hình ảnh.
{rule}

===== VÍ DỤ =====
Nếu hình KHÔNG PHẢI {loai_giay_to}, toàn bộ phản hồi của bạn là:
null
Nếu hình ĐÚNG LÀ {loai_giay_to}, phản hồi của bạn là dạng JSON:
{{
"trường_1": "giá_trị_1",
"trường_2": "giá_trị_2",
...
}}
===== NHẮC NHỞ =====
ĐÂY LÀ QUY TẮC QUAN TRỌNG NHẤT: Nếu hình ảnh KHÔNG PHẢI "{loai_giay_to}", chỉ trả về null (không dấu ngoặc, không giải thích)
"""

    async def validate_document_type(self, media_stream: BytesIO, mime_type: str, expected_type: str) -> bool:
        """
        Validate if the document matches the expected type using Gemini API.
        
        Args:
            media_stream: The document image as BytesIO
            mime_type: The MIME type of the image
            expected_type: The expected document type to validate against
            
        Returns:
            bool: True if document matches expected type, False otherwise
        """
        try:
            logger.info(f"Validating document type: {expected_type}")
            result = await self.extract_content_from_stream_async(media_stream, mime_type, self._get_validation_prompt(expected_type))
            is_valid = result.strip().lower() == "true"
            logger.info(f"Document type validation result: {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Error validating document type: {str(e)}")
            return False
            
    def _get_validation_prompt(self, expected_type: str) -> str:
        """Generate validation prompt for document type checking."""
        return f"""Bạn là một trợ lý kiểm tra loại giấy tờ. Nhiệm vụ của bạn là xác định xem hình ảnh có đúng là "{expected_type}" không.

HƯỚNG DẪN:
1. Kiểm tra kỹ hình ảnh để xác định loại giấy tờ
2. Nếu hình ảnh ĐÚNG LÀ "{expected_type}", trả về "true"
3. Nếu hình ảnh KHÔNG PHẢI "{expected_type}", trả về "false" kèm theo loại giấy tờ thực tế
4. CHỈ trả về "true" hoặc "false", không thêm bất kỳ văn bản nào khác

VUI LÒNG CHỈ TRẢ VỀ "true" HOẶC "false", KHÔNG THÊM BẤT KỲ GIẢI THÍCH NÀO."""