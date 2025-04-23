# CCCD FastAPI Project

## Giới Thiệu

Đây là một dự án sử dụng **FastAPI** để xây dựng ứng dụng web API với nhiều chức năng, bao gồm:
- Quét mã QR từ hình ảnh CCCD (Căn cước công dân) và trả về thông tin người dùng
- Xử lý và chuyển đổi tài liệu Word sang HTML và JSON
- Trích xuất thông tin từ các văn bản pháp lý như Giấy khai sinh, Giấy chứng nhận kết hôn, Trích lục khai tử
- Tích hợp AI (Google Gemini) để phân tích nội dung và xử lý ngôn ngữ tự nhiên

## Cấu Trúc Dự Án
```
fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py                # Điểm vào chính của ứng dụng
│   ├── controllers/           # Tầng Controller (xử lý route)
│   │   ├── __init__.py
│   │   ├── item_controller.py
│   │   ├── qr_controller.py
│   │   ├── process_file_controller.py
│   │   └── gemini_controller.py
│   ├── helpers/               # Các hàm hỗ trợ
│   │   ├── __init__.py
│   │   ├── format_date.py
│   │   └── qr_utils.py
│   ├── models/                # Định nghĩa model hoặc schema
│   │   ├── __init__.py
│   │   ├── CCCD_dto.py
│   │   └── response_models.py
│   ├── services/              # Tầng Service (xử lý logic nghiệp vụ)
│   │   ├── __init__.py
│   │   ├── qr_service.py
│   │   ├── item_service.py
│   │   ├── process_file_service.py
│   │   ├── html_to_json_service.py
│   │   ├── json_to_html_input.py
│   │   └── gemini_service.py
│   └── config.py              # Cấu hình chung cho dự án
├── requirements.txt           # Danh sách các gói cần cài đặt
├── Dockerfile                 # Dockerfile để container hóa ứng dụng
└── README.md
```

## Chi Tiết Về Các Module

### 1. QR Module
Cung cấp API để quét và xử lý mã QR từ CCCD (Căn cước công dân)

#### Endpoints:
- **GET /qr/qr**: Kiểm tra trạng thái API
- **POST /qr/cccd/scan**: Quét mã QR từ hình ảnh CCCD và trả về thông tin người dùng
  - Input: File hình ảnh CCCD
  - Output: Thông tin người dùng (id, old_id, full_name, birthdate, sex, address, create_date)

### 2. Item Module
Cung cấp các API để xử lý và chuyển đổi tài liệu.

#### Endpoints:
- **POST /items/convert-docx-to-html**: Chuyển đổi tài liệu Word sang HTML
  - Input: File Word (.docx hoặc .doc)
  - Output: Nội dung HTML
  
- **POST /items/convert-html-to-json**: Chuyển đổi HTML sang cấu trúc JSON
  - Input: File HTML
  - Output: Cấu trúc JSON
  
- **POST /items/convert-json-to-html-input**: Chuyển đổi JSON sang HTML form
  - Input: File JSON và tiêu đề form
  - Output: Form HTML

### 3. Process File Module
Cung cấp API để xử lý tài liệu với hỗ trợ từ mô hình AI.

#### Endpoints:
- **POST /process/process_file**: Kiểm tra chính tả và ngữ pháp, đề xuất cải thiện nội dung
  - Input: File Word, các tùy chọn kiểm tra
  - Output: Nhận xét và gợi ý cải thiện
  
- **POST /process/process_question**: Trả lời câu hỏi dựa trên nội dung của tài liệu
  - Input: File Word và câu hỏi
  - Output: Câu trả lời dựa trên nội dung

### 4. Gemini Module
Tích hợp Google Gemini AI để xử lý và trích xuất thông tin từ tài liệu.

#### Endpoints:
- **GET /gemini/gemini**: Kiểm tra trạng thái API
- **POST /gemini/extract-trich-luc-khai-tu**: Trích xuất thông tin từ Trích lục khai tử
- **POST /gemini/extract-giay-chung-nhan-ket-hon**: Trích xuất thông tin từ Giấy chứng nhận kết hôn
- **POST /gemini/extract-giay-khai-sinh**: Trích xuất thông tin từ Giấy khai sinh
- **POST /gemini/extract-content-from-file**: Trích xuất nội dung từ tệp tin dựa trên prompt
- **POST /gemini/extract-content-from-url**: Trích xuất nội dung từ URL dựa trên prompt

## Yêu Cầu Hệ Thống

Dự án yêu cầu cài đặt các thư viện sau (chi tiết trong requirements.txt):
- fastapi
- uvicorn
- python-multipart
- pillow
- pyzbar
- python-docx
- google-generativeai (cho Gemini)
- httpx
- beautifulsoup4

## Cài Đặt

### Sử dụng Python Venv

1. Clone repository:
   ```bash
   git clone <repository-url>
   cd fastapi_project
   ```

2. Tạo môi trường ảo và kích hoạt:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Trên Linux/MacOS
   venv\Scripts\activate      # Trên Windows
   ```

3. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```

### Sử dụng Anaconda

1. Tạo môi trường Anaconda:
   ```bash
   conda create --name CCCD-env python=3.10
   conda activate CCCD-env
   ```

2. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```

## Chạy Ứng Dụng

1. Khởi động ứng dụng với Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Truy cập API Swagger UI:
   ```
   http://localhost:8000/docs
   ```

## Tích Hợp Với Các Hệ Thống Khác

### 1. Tích Hợp Qua REST API

Tất cả các chức năng của hệ thống đều có thể được tích hợp qua REST API. Ví dụ:

```python
import requests

# Quét mã QR từ hình ảnh CCCD
def scan_cccd(image_path):
    url = "http://localhost:8000/qr/cccd/scan"
    files = {"file": open(image_path, "rb")}
    response = requests.post(url, files=files)
    return response.json()

# Trích xuất thông tin từ Giấy khai sinh
def extract_giay_khai_sinh(image_path):
    url = "http://localhost:8000/gemini/extract-giay-khai-sinh"
    files = {"file": open(image_path, "rb")}
    response = requests.post(url, files=files)
    return response.json()
```

### 2. Tích Hợp Qua Docker

Hệ thống đã được container hóa với Docker, giúp dễ dàng triển khai:

#### Chuẩn bị

1. Đảm bảo đã cài đặt Docker:
   ```bash
   docker --version
   ```

2. Tạo file `requirements.txt` từ môi trường hiện tại:
   ```bash
   pip freeze > requirements.txt
   ```

#### Xây dựng và triển khai

1. Build Docker image:
   ```bash
   docker build -t fastapi-app .
   ```

2. Chạy container từ image:
   ```bash
   docker run -d -p 8000:8000 fastapi-app
   ```
   - `-d`: Chạy container ở chế độ detached (chạy nền)
   - `-p 8000:8000`: Ánh xạ cổng 8000 của máy host với cổng 8000 của container

3. Kiểm tra container đang chạy:
   ```bash
   docker ps
   ```

#### Triển khai lên Docker Hub

1. Đặt tag cho image:
   ```bash
   docker tag fastapi-app:latest username/fastapi-app:latest
   ```

2. Đẩy image lên Docker Hub:
   ```bash
   docker push username/fastapi-app:latest
   ```

#### Quản lý container

1. Dừng container:
   ```bash
   docker stop <container_id>
   ```

2. Khởi động lại container:
   ```bash
   docker restart <container_id>
   ```

3. Xem logs:
   ```bash
   docker logs <container_id>
   ```

4. Dọn dẹp tài nguyên không sử dụng:
   ```bash
   docker system prune -a --volumes
   ```

### 3. Tích Hợp Với Web Frontend

Các API đã được cấu hình CORS để có thể tích hợp dễ dàng với các ứng dụng web frontend (React, Vue, Angular).

```javascript
// Ví dụ tích hợp với React
async function scanCCCD(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('http://localhost:8000/qr/cccd/scan', {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
}
```
