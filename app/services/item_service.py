# fastapi_project/app/services/item_service.py

from .docx_converter import DocxToHtmlConverter
import os
from tempfile import NamedTemporaryFile

class ItemService:
    def convert_docx_to_html(self, file_bytes: bytes) -> str:
        with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        
        try:
            converter = DocxToHtmlConverter(tmp_path)
            html_output = converter.convert_document()
        finally:
            os.remove(tmp_path)
        
        return html_output
