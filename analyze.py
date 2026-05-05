import os
import re
import requests
import webbrowser
import google.generativeai as genai

genai.configure(api_key="")

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

files_to_analyze = [
    # "/Users/dhv06/develop/datn/DATN/routes/web.php",
    # "/Users/dhv06/develop/datn/DATN/app/Http/Controllers/UserController.php"
    # "C:\\dhv\\goal\\DATN\\routes\\web.php",
    "C:\\dhv\\goal\\DATN\\app\\Http\\Controllers\\UserController.php"
]

code_context = ""
for path in files_to_analyze:
    file_name = os.path.basename(path)
    content = read_file_content(path)
    code_context += f"--- START FILE: {file_name} ---\n{content}\n--- END FILE ---\n\n"

# 3. Tạo Prompt (Kỷ luật thép CHỐNG LỖI QUẢ BOM)
prompt = f"""
Role: Bạn là một Senior Solution Architect chuyên về vẽ sơ đồ hệ thống.
Nhiệm vụ: Đọc Source Code, TÌM VÀ CHỈ VẼ SƠ ĐỒ CHO DUY NHẤT 3 LUỒNG sau:
1. Đăng ký (Register/Signup)
2. Đăng nhập (Login/Auth)
3. Quên mật khẩu/Đổi mật khẩu (Forgot Password/Reset Password)

⚠️ LUẬT THÉP VỀ CÚ PHÁP MERMAID (NẾU SAI SẼ BỊ LỖI SYSTEM, BẮT BUỘC TUÂN THỦ 100%):
1. Dòng đầu tiên BẮT BUỘC là: `flowchart TD`
2. QUY TẮC ĐẶT ID NODE (QUAN TRỌNG NHẤT): ID của node CHỈ ĐƯỢC dùng chữ cái không dấu, số và dấu gạch dưới (tuyệt đối KHÔNG có khoảng trắng, KHÔNG có ký tự đặc biệt).
   - ✅ ĐÚNG: `DangNhap1["Nhập thông tin"]`
   - ❌ SAI: `Đăng Nhập 1["Nhập thông tin"]`
3. QUY TẮC SUBGRAPH: Bắt buộc dùng cú pháp `subgraph ID_Khong_Dau ["Tên Hiển Thị Có Dấu"]`
   - ✅ ĐÚNG: `subgraph DangKy ["1. Luồng Đăng Ký"]`
   - ❌ SAI: `subgraph 1. Luồng Đăng Ký`
4. QUY TẮC NỘI DUNG (CHỐNG MỜ): Nội dung text trong mỗi node phải CỰC KỲ NGẮN GỌN (2-5 từ).
5. CHỈ DÙNG 2 loại hình khối: Hình hộp `ID["Text"]` và Hình thoi If/Else `ID{{"Text"}}`.
6. TRẢ VỀ DUY NHẤT CODE MERMAID, KHÔNG CHÀO HỎI HAY GIẢI THÍCH THÊM BẤT CỨ TỪ NÀO.

Code Context:
{code_context}
"""

# 4. Gửi cho AI và Cắt gọt text
model = genai.GenerativeModel('gemini-2.5-flash')
print("Đang nhờ AI phân tích và vẽ sơ đồ cô đọng...")
try:
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    
    # THUẬT TOÁN "MÁY CHÉM": Bỏ qua mọi lời chào hỏi, chỉ lấy đúng code Mermaid
    match = re.search(r'(flowchart\s+TD.*)', raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        mermaid_code = match.group(1)
        # Gọt bỏ nốt dấu ``` ở cuối nếu AI lỡ sinh ra
        mermaid_code = mermaid_code.split('```')[0].strip() 
    else:
        mermaid_code = raw_text
        
    print("=== ĐÃ TRÍCH XUẤT MÃ MERMAID THÀNH CÔNG ===")
    print(mermaid_code) # In ra Terminal để bạn dễ kiểm tra nếu có lỗi
except Exception as e:
    print(f"Lỗi AI: {e}")
    exit()

# 5. Render Sơ đồ HTML (Tự động tải ảnh PNG)
print("\nĐang tạo file HTML sơ đồ chuyên nghiệp...")
try:
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sơ đồ Luồng Hệ Thống - Chuyên Nghiệp</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'default',
            flowchart: {{ curve: 'step-after' }} 
        }});
    </script>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 0; overflow: hidden; background-color: #f1f3f5; }}
        .header {{ 
            position: fixed; top: 0; left: 0; right: 0; height: 60px;
            display: flex; justify-content: space-between; align-items: center;
            padding: 0 30px;
            background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 10;
        }}
        h2 {{ margin: 0; color: #333; font-size: 18px; }}
        
        .btn-download {{
            background-color: #28a745; color: white; border: none; padding: 8px 16px;
            border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s;
        }}
        .btn-download:hover {{ background-color: #218838; }}
        
        .mermaid-container {{ 
            width: 100vw; height: calc(100vh - 60px); cursor: grab; margin-top: 60px;
        }}
        .mermaid-container:active {{ cursor: grabbing; }}
        .mermaid svg {{ max-width: none !important; width: auto !important; height: auto !important; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Sơ đồ: Đăng Ký - Đăng Nhập - Quên Mật Khẩu</h2>
        <button class="btn-download" onclick="downloadPNG()">📥 Tải file ảnh PNG (Đang tải tự động...)</button>
    </div>

    <div class="mermaid-container">
        <div class="mermaid" id="diagram">
{mermaid_code}
        </div>
    </div>

    <script>
        // 1. Gắn Zoom và Tự động tải ảnh
        setTimeout(() => {{
            const svgElement = document.querySelector('.mermaid svg');
            if(svgElement) {{
                window.panZoom = svgPanZoom(svgElement, {{
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: false,
                    center: true,
                    minZoom: 0.1,
                    maxZoom: 50
                }});

                // --- GỌI HÀM TỰ ĐỘNG TẢI ẢNH SAU KHI VẼ XONG 1 GIÂY ---
                setTimeout(() => {{
                    downloadPNG();
                }}, 1000);
            }}
        }}, 1500);

        // 2. Hàm chuyển SVG thành PNG
        function downloadPNG() {{
            const svg = document.querySelector('.mermaid svg');
            const svgData = new XMLSerializer().serializeToString(svg);
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const img = new Image();
            
            const svgRect = svg.getBBox();
            canvas.width = svgRect.width + 100;
            canvas.height = svgRect.height + 100;

            img.onload = function() {{
                ctx.fillStyle = "white"; 
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 50, 50); 
                
                const pngFile = canvas.toDataURL("image/png");
                const downloadLink = document.createElement("a");
                downloadLink.download = "so_do_auth.png";
                downloadLink.href = pngFile;
                
                // Tự động click vào link tải
                downloadLink.click();
                
                // Cập nhật lại text của nút bấm
                document.querySelector('.btn-download').innerText = "✅ Đã tự động tải PNG";
            }};
            
            img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgData)));
        }}
    </script>
</body>
</html>"""

    # Lưu và mở file
    file_name = "luong_he_thong.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"🎉 THÀNH CÔNG! Đã lưu file HTML và đang tự động tải ảnh PNG...")
    
    file_url = f"file://{os.path.abspath(file_name)}"
    webbrowser.open(file_url)
    
except Exception as e:
    print(f"Lỗi HTML: {e}")