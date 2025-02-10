# fastapi_project/app/controllers/item_controller.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
from app.models.json_response import JSONResponse
from typing import List, Dict
from app.services.item_service import ItemService
from app.services.html_to_json_service import HtmlToJsonService
from app.services.json_to_html_input import JsonConverterService
import logging
import json

router = APIRouter()
service = ItemService()
html_to_json_service = HtmlToJsonService()
json_service = JsonConverterService()

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
        # html_finally = html_to_json_service.html_ai_processing(html_output)
        html_finally = html_to_json_service.html_ai_processing(html_output)
        html_finallyx = html_to_json_service.flatten_id_spans(html_finally)
        return Response(content=html_finallyx, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in convert_docx_to_html: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi chuyển đổi tệp.")

@router.post("/convert-html-to-json", response_model=JSONResponse)
async def convert_html_to_json(html_file: UploadFile = File(...)):
    if not html_file.filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="File phải có định dạng .html")
    
    try:
        html_content = await html_file.read()
        html_str = html_content.decode('utf-8')
        json_output = html_to_json_service.convert_html_to_json(html_str)
        if json_output is None:
            raise HTTPException(status_code=500, detail="Failed to convert HTML to JSON")
        content_str = json.dumps(json_output, ensure_ascii=False)
        return Response(content=content_str, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in convert_html_to_json: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/convert-json-to-html-input")
async def convert_json_to_html_input(
    file: UploadFile = File(...),
    title: str = Form("HTML Input Form")
    ) -> Response:
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File phải có định dạng .json")
    try:
        json_content = await file.read()
        json_str = json_content.decode('utf-8')
        print(f"JSON Content: {json_str}")
        html_output = json_service.convert_json_to_html(title, json_str)
        return Response(content=html_output, media_type="text/html")
    except Exception as e:
        logger.error(f"Error in convert_json_to_html_input: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra khi chuyển đổi tệp.")