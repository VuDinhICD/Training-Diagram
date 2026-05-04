
import os
import base64
import requests
import google.generativeai as genai

# Cấu hình API Key của bạn (Nhớ xóa key này trên AI Studio và tạo key mới sau khi test xong nhé)
genai.configure(api_key="")

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

files_to_analyze = [
    "/Users/dhv06/develop/datn/DATN/routes/web.php",
    "/Users/dhv06/develop/datn/DATN/app/Http/Controllers/UserController.php"
]

code_context = ""
for path in files_to_analyze:
    file_name = os.path.basename(path)
    content = read_file_content(path)
    code_context += f"--- START FILE: {file_name} ---\n{content}\n--- END FILE ---\n\n"

# 3. Tạo Prompt (Phiên bản Luật Thép)
prompt = f"""
Role: Bạn là một Senior Solution Architect.
Nhiệm vụ: Đọc Source Code và vẽ Activity Diagram (Sơ đồ luồng) bằng Mermaid.js.

LUẬT THÉP (BẮT BUỘC PHẢI TUÂN THỦ ĐỂ KHÔNG BỊ LỖI SYNTAX):
1. BẮT BUỘC dùng: `flowchart TD` ở dòng đầu tiên.
2. Cấu trúc node chuẩn: `ID["Nội dung text"]`. BẮT BUỘC phải có dấu ngoặc kép bọc nội dung text.
3. TUYỆT ĐỐI CẤM sử dụng các ký tự sau bên trong nội dung text: ( ) {{ }} [ ] / \ . Hãy thay bằng chữ bình thường hoặc dấu gạch ngang.
   - ❌ SAI: A["Login Form (username)"]
   - ✅ ĐÚNG: A["Login Form username"]
4. CHỈ DÙNG 2 loại hình khối: 
   - Hình chữ nhật thông thường: `ID["Text"]`
   - Hình thoi (If/Else): `ID{{"Text"}}`
   - (CẤM dùng các hình phức tạp như `[/ /]`, `(( ))`)
5. Chỉ trả về mã Mermaid thuần, không bọc trong ```mermaid, không giải thích gì thêm.

Code Context:
{code_context}
"""

# 4. Gửi cho AI
model = genai.GenerativeModel('gemini-2.5-flash')
print("Đang nhờ AI phân tích code...")
response = model.generate_content(prompt)

# Dọn dẹp text an toàn
raw_text = response.text.strip()
clean_lines = []
for line in raw_text.split('\n'):
    if not line.strip().startswith("```"):
        clean_lines.append(line)

mermaid_code = '\n'.join(clean_lines).strip()
print("=== ĐÃ TẠO XONG MÃ MERMAID ===")
print(mermaid_code)

# 5. Render Sơ đồ bằng HTML (Bản Pro: Zoom Fill + Nút Tải PNG)
print("\nĐang tạo file công cụ Sơ đồ chuyên nghiệp...")
try:
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sơ đồ Luồng Hệ Thống</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; overflow: hidden; background-color: #f8f9fa; }}
        .header {{ 
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 30px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            position: relative; z-index: 10; 
        }}
        h2 {{ margin: 0; color: #333; font-size: 18px; }}
        .btn-download {{
            background-color: #28a745; color: white; border: none; padding: 8px 16px;
            border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s;
        }}
        .btn-download:hover {{ background-color: #218838; }}
        
        .mermaid-container {{ width: 100vw; height: calc(100vh - 60px); cursor: grab; }}
        .mermaid svg {{ max-width: none !important; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h2>Sơ đồ Luồng Nghiệp Vụ</h2>
            <span style="font-size: 12px; color: #666;">💡 Cuộn chuột để Zoom | Kéo để di chuyển</span>
        </div>
        <button class="btn-download" onclick="downloadPNG()">📥 Tải file ảnh PNG</button>
    </div>

    <div class="mermaid-container">
        <div class="mermaid" id="diagram">
{mermaid_code}
        </div>
    </div>

    <script>
        // 1. Kích hoạt tính năng Zoom & Fill màn hình
        setTimeout(() => {{
            const svgElement = document.querySelector('.mermaid svg');
            if(svgElement) {{
                window.panZoom = svgPanZoom(svgElement, {{
                    zoomEnabled: true, controlIconsEnabled: true,
                    fit: false, center: true, minZoom: 0.1, maxZoom: 50
                }});
                const sizes = window.panZoom.getSizes();
                const targetZoom = sizes.height / sizes.viewBox.height;
                window.panZoom.zoom(targetZoom * 0.9);
                window.panZoom.center();
            }}
        }}, 1500);

        // 2. Hàm chuyển đổi SVG sang PNG và tải về
        function downloadPNG() {{
            const svg = document.querySelector('.mermaid svg');
            const svgData = new XMLSerializer().serializeToString(svg);
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const img = new Image();
            
            // Lấy kích thước thực tế của sơ đồ
            const svgRect = svg.getBBox();
            canvas.width = svgRect.width + 100;
            canvas.height = svgRect.height + 100;

            img.onload = function() {{
                ctx.fillStyle = "white"; // Tạo nền trắng cho ảnh
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 50, 50);
                
                const pngFile = canvas.toDataURL("image/png");
                const downloadLink = document.createElement("a");
                downloadLink.download = "so_do_luong.png";
                downloadLink.href = pngFile;
                downloadLink.click();
            }};
            
            img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgData)));
        }}
    </script>
</body>
</html>"""

    file_name = "luong_he_thong.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"🎉 ĐÃ XUẤT CÔNG CỤ: {file_name}")
    os.system(f"open {file_name}")
    
except Exception as e:
    print(f"Lỗi: {e}")