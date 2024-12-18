from pydantic import BaseModel
from typing import List

class CCCDQRCodeDTO(BaseModel):
    id: str  # Số CCCD gắn chip
    old_id: str  # Số CMND cũ
    full_name: str  # Họ và tên
    birthdate: str  # Ngày tháng năm sinh (định dạng ISO 8601)
    sex: str  # Giới tính (Nam/Nữ)
    address: str  # Địa chỉ thường trú
    create_date: str