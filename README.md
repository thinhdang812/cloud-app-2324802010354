# Cloud Task Manager - MSSV 2324802010354

Ứng dụng web quản lý công việc triển khai trên Ubuntu VPS (FastAPI + PostgreSQL + Nginx + UFW).

## Hướng dẫn cài đặt
1. Cài đặt Python 3, PostgreSQL, Nginx.
2. Tạo database `cloud_app_db` và user `app_user`.
3. Sao chép `.env.example` thành `.env` và điền thông tin kết nối.
4. Cài thư viện: `pip install -r requirements.txt`.
5. Chạy ứng dụng qua `uvicorn main:app --host 127.0.0.1 --port 8000`.
