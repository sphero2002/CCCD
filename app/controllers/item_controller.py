# fastapi_project/app/controllers/item_controller.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.models.json_response import JSONResponse
from typing import List, Dict
from app.services.item_service import ItemService
from app.services.html_to_json_service import HtmlToJsonService
import logging

router = APIRouter()
service = ItemService()
html_to_json_service = HtmlToJsonService()

logger = logging.getLogger(__name__)

@router.post("/convert-docx-to-html")
async def convert_docx_to_html(file: UploadFile = File(...)) -> Response:
    if not (file.filename.endswith(".docx") or file.filename.endswith(".doc")):
        raise HTTPException(status_code=400, detail="File phải có định dạng .docx hoặc .doc")
    try:
        file_bytes = await file.read()
        file_extension = ".docx" if file.filename.endswith(".docx") else ".doc"
        html_output = service.convert_docx_to_html(file_bytes, file_extension)
        # print(f"HTML Output:\n#####################\n {html_output}")
        return Response(content=html_output, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in convert_docx_to_html: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi chuyển đổi tệp.")

@router.post("/convert-html-to-json", response_model=JSONResponse)
async def convert_html_to_json(html_file: UploadFile = File(...)) -> Dict[str, List[Dict]]:
    if not html_file.filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="File phải có định dạng .html")
    
    try:
        html_content = await html_file.read()
        html_str = html_content.decode('utf-8')
        json_output = html_to_json_service.convert_html_to_json(html_str)
        if json_output is None:
            raise HTTPException(status_code=500, detail="Failed to convert HTML to JSON")
        return {"data": json_output}  # Sử dụng 'data' nếu bạn đã đổi tên trường
        # Hoặc nếu bạn giữ 'json':
        # return {"json": json_output}
    except Exception as e:
        logger.error(f"Error in convert_html_to_json: {e}")
        raise HTTPException(status_code=500, detail=str(e))
