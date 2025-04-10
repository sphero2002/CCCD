# Hướng dẫn triển khai với Docker

## Yêu cầu

- Docker và Docker Compose đã được cài đặt trên máy
- Git (để clone repository)

## Các bước triển khai

### 1. Clone repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Cấu hình môi trường

```bash
cp .env.example .env
```

Sau đó chỉnh sửa file `.env` để cung cấp giá trị cho các biến môi trường cần thiết, đặc biệt là `GOOGLE_GENERATIVE_AI_API_KEY`.

### 3. Xây dựng và khởi chạy container với Docker Compose

```bash
docker-compose up -d
```

Ứng dụng sẽ chạy tại địa chỉ http://localhost hoặc IP của máy chủ triển khai với port 80.

### 4. Kiểm tra logs

```bash
docker-compose logs -f
```

### 5. Dừng ứng dụng

```bash
docker-compose down
```

## Các lệnh Docker hữu ích

- Xây dựng lại container: `docker-compose build`
- Khởi động lại container: `docker-compose restart`
- Xem tài nguyên container sử dụng: `docker stats`

### Building and running your application

When you're ready, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:8080.

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References

- [Docker's Python guide](https://docs.docker.com/language/python/)
