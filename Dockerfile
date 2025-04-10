# Sử dụng Python phiên bản chính thức làm base image
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app


# Copy file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .

# Cài đặt các thư viện hệ thống cần thiết (bao gồm zbar)
RUN apt-get update && apt-get install -y \
    zbar-tools \
    libzbar0 \
    libgl1 \
    libreoffice \
    build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose cổng mặc định của FastAPI
EXPOSE 80

# Chạy ứng dụng bằng uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
