# fastapi_project/app/models/json_response.py

from pydantic import BaseModel
from typing import List, Dict

class JSONResponse(BaseModel):
    data: List[List[Dict]]  # Danh sách các dictionary
