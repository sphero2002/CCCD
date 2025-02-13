# fastapi_project/app/controllers/item_controller.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
from app.models.json_response import JSONResponse
from typing import List, Dict
from app.services.process_file_service import ProcessFileService
import logging
import json
import re

router = APIRouter()
service = ProcessFileService()

logger = logging.getLogger(__name__)

@router.post("/process_file")
async def process_file_endpoint(
    file: UploadFile = File(...),
    spelling_grammar: bool = Form(True),
    content_suggestion: bool = Form(True),
    selected_model: str = Form("default"),
):
    """
    Endpoint nhận file Word (.docx) và tiến hành kiểm tra:
      - Lỗi chính tả và ngữ pháp (nếu `spelling_grammar` = True)
      - Đề xuất cải thiện nội dung (nếu `content_suggestion` = True)
    """
    try:
        file_bytes = await file.read()
        result = service._process_single_file(
            file_bytes,
            spelling_grammar,
            content_suggestion,
            selected_model,
        )
        return {"filename": file.filename, "comments": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process_question")
async def process_question_endpoint(
    file: UploadFile = File(...),
    question: str = Form(...),
    selected_model: str = Form("default"),
):
    """
    Endpoint nhận file Word (.docx) và một câu hỏi,
    sau đó trả lời dựa trên nội dung của file.
    """
    try:
        file_bytes = await file.read()
        answer = service.process_question_logic(
            file_bytes,
            question,
            selected_model,
        )
        return {"filename": file.filename, "question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))