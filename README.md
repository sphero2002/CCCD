# FastAPI Project

## Giới thiệu

Đây là một dự án sử dụng **FastAPI** để xây dựng một ứng dụng web API cho phép quét mã QR từ hình ảnh CCCD (Căn cước công dân) và trả về thông tin người dùng.

## Cấu trúc dự án
    fastapi_project/
    ├── app/
    │   ├── [__init__.py](app/__init__.py)
    │   ├── [main.py](app/main.py)                # Điểm vào chính của ứng dụng
    │   ├── controllers/           # Tầng Controller (xử lý route)
    │   │   ├── [__init__.py](app/controllers/__init__.py)
    │   │   ├── [item_controller.py](app/controllers/item_controller.py)
    │   │   └── [qr_controller.py](app/controllers/qr_controller.py)
    │   ├── helpers/               # Các hàm hỗ trợ
    │   │   ├── [__init__.py](app/helpers/__init__.py)
    │   │   ├── [format_date.py](app/helpers/format_date.py)
    │   │   └── [qr_utils.py](app/helpers/qr_utils.py)
    │   ├── models/                # Định nghĩa model hoặc schema
    │   │   ├── [__init__.py](app/models/__init__.py)
    │   │   └── [CCCD_dto.py](app/models/CCCD_dto.py)
    │   ├── services/              # Tầng Service (xử lý logic nghiệp vụ)
    │   │   ├── [__init__.py](app/services/__init__.py)
    │   │   └── [qr_service.py](app/services/qr_service.py)
    │   └── [config.py](app/config.py)              # Cấu hình chung cho dự án
    ├── [requirements.txt](requirements.txt)           # Danh sách các gói cần cài đặt
    ├── [Dockerfile](Dockerfile)               # Dockerfile để container hóa ứng dụng
    └── [README.md](README.md)

## Yêu cầu

Các gói cần cài đặt được liệt kê trong **requirements.txt**.

## Cài đặt

1. Clone repository về máy của bạn:
    ```bash
   git clone <repository-url>

2. Tạo môi trường ảo và kích hoạt:
    ```bash
    python -m venv venv
    source venv/bin/activate   # Trên Linux/MacOS
    venv\Scripts\activate      # Trên Windows

3. Cài đặt các gói phụ thuộc:
    ```bash
    pip install -r requirements.txt

## Chạy ứng dụng

1. Chạy ứng dụng với Uvicorn:
    ```bash
    uvicorn app.main:app --reload

Ứng dụng sẽ chạy tại http://localhost:8000.

## Anaconda

```bash
conda create --name CCCD-env python=3.10
conda activate CCCD-env
conda deactivate