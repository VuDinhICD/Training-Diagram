# 🚀 AI Code-to-Diagram Generator

Công cụ tự động đọc mã nguồn (Source Code) và vẽ Sơ đồ luồng hoạt động (Activity Diagram) bằng sức mạnh của AI Gemini. 

Sơ đồ được render trực tiếp ra file HTML tương tác xịn xò (chuẩn Miro/Figma) với tính năng cuộn chuột để zoom, kéo thả để di chuyển và hỗ trợ tải ảnh PNG sắc nét chỉ với 1 cú click.

## 📋 Yêu cầu hệ thống
* Python 3.x đã được cài đặt trên máy.
* Cần có **API Key** của Google Gemini (Lấy miễn phí tại [Google AI Studio](https://aistudio.google.com/app/apikey)).

## ⚙️ Hướng dẫn cài đặt

**Bước 1:** (Tùy chọn nhưng khuyên dùng) Tạo và kích hoạt môi trường ảo để không làm rác thư viện trên máy:
```bash
# Tạo môi trường ảo tên là ai_env
python3 -m venv ai_env

# Kích hoạt trên Mac/Linux:
source ai_env/bin/activate
# (Nếu dùng Windows, chạy lệnh: ai_env\Scripts\activate)