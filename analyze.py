import os
import re
import sys
import subprocess
import ollama

# ==============================
# CONFIG
# ==============================
# Danh sách các thư mục cần bỏ qua để tập trung vào code nghiệp vụ
IGNORE_DIRS = {
    "node_modules", "vendor", ".git", "storage", "dist", "build", 
    "__pycache__", ".next", "config", "tests", "database", 
    "resources", "public", "bootstrap"
}

# Các định dạng file logic phổ biến
ALLOWED_EXTENSIONS = {
    ".php", ".js", ".ts", ".jsx", ".tsx", ".py", ".java", ".cs", ".go"
}

MAX_FILE_SIZE = 300000 

# ==============================
# GET ARGUMENTS
# ==============================
if len(sys.argv) < 3:
    print("❌ Usage: python3 analyze.py <project_path> <requirement>")
    sys.exit(1)

PROJECT_PATH = sys.argv[1]
USER_REQUIREMENT = sys.argv[2] 

if not os.path.exists(PROJECT_PATH):
    print("❌ Project path not found")
    sys.exit(1)

# ==============================
# FIND SOURCE FILES (Tập trung vào luồng thực thi: Route, Controller, Service, Middleware)
# ==============================
def find_source_files(root):
    files = []
    # Từ khóa nhận diện file điều hướng và xử lý logic nghiệp vụ
    logic_keywords = ["controller", "router", "route", "api", "web", "service", "middleware"]
    
    for current_root, dirs, filenames in os.walk(root):
        # Loại bỏ các thư mục rác
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in filenames:
            ext = os.path.splitext(file)[1]
            if ext.lower() not in ALLOWED_EXTENSIONS:
                continue

            # Lấy các file liên quan đến luồng xử lý chính
            full_path = os.path.join(current_root, file)
            path_lower = full_path.lower()
            
            if not any(key in path_lower for key in logic_keywords):
                continue

            # Loại bỏ các file config/env/package có thể chứa từ khóa nhưng không phải logic
            if any(k in file.lower() for k in ["config", ".env", "constant", "package", "webpack"]):
                continue
                
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    continue
                files.append(full_path)
            except:
                continue
    return files

# ==============================
# READ FILES
# ==============================
def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# ==============================
# BUILD CONTEXT
# ==============================
def build_context(files):
    context = ""
    for path in files:
        try:
            rel = os.path.relpath(path, PROJECT_PATH)
            content = read_file(path)
            if not content.strip():
                continue
            context += f"\nFILE: {rel}\n{content}\n"
        except:
            pass
    # Giới hạn context để AI không bị quá tải
    return context[:120000]

# ==============================
# PROMPT (Tối ưu cực hạn để loại bỏ rác)
# ==============================
def build_prompt(context, requirement):
    return f"""
You are a Senior Software Architect. Analyze the provided source code to visualize a COMPLETE EXECUTION FLOW.

USER REQUEST: 
Create a highly detailed flowchart for the process: "{requirement}"

STRICT INSTRUCTIONS:
1. TRACE EVERYTHING: Trace from the Route entry point -> Middleware -> Controller logic -> Service calls -> Database -> Final Response.
2. BRANCHING: Include all validation checks and error cases as Decision nodes.
3. NAMING: Use professional, descriptive Vietnamese labels.
4. FORMAT: Use Mermaid syntax. Start with `flowchart TD`.
5. STRICT OUTPUT: Output ONLY the Mermaid code. 
   - DO NOT include the route definition like `Route::get(...)` in the diagram.
   - DO NOT explain the diagram with bullet points or text.
   - DO NOT use markdown code blocks (```).

PROJECT SOURCE CODE:
{context}
"""

# ==============================
# AI (Ollama - Llama3)
# ==============================
def call_ai(prompt):
    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional Mermaid generator. You output ONLY valid code. You NEVER include explanations, comments, or programming code snippets in your output."
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"❌ AI connection error: {e}")
        return ""

# ==============================
# SANITIZE (Cải tiến mạnh mẽ để lọc bỏ rác)
# ==============================
def sanitize(raw):
    if not raw: return None
    
    # Loại bỏ lời chào của AI
    raw = re.sub(r'^(Sure|Here|Certainly|Of course|This is).*\n', '', raw, flags=re.IGNORECASE)
    
    lines = raw.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        
        # Bỏ qua dòng trống, markdown block, hoặc các giải thích bắt đầu bằng * hoặc -
        if not line or "```" in line or line.startswith(("*", "-", "Note:")):
            continue
            
        # Bỏ qua các dòng tiêu đề lặp lại
        if line.lower().startswith("flowchart"):
            continue
        
        # Loại bỏ triệt để code PHP/JS/Python lọt vào (VD: Route::get, function, app.get)
        if re.search(r'^(Route::|function|class|public|private|protected|namespace|use|import|from|return|app\.|const|let|var)\b', line):
            continue

        # Dọn dẹp ký tự gây lỗi cú pháp mmdc
        line = line.replace(";", "").replace("$", "")
        
        # Chuẩn hóa nhãn (labels) và đảm bảo bọc trong ngoặc kép để tránh lỗi ký tự đặc biệt
        line = re.sub(r'\[([^"\]]+)\]', r'["\1"]', line)
        line = re.sub(r'\{([^"}]+)\}', r'{"\1"}', line)
        line = re.sub(r'\(([^")]+)\)', r'("\1")', line)

        # Chỉ giữ lại các dòng có cấu trúc Mermaid thực thụ
        if any(x in line for x in ['-->', '[', '{', '(', '])']):
            cleaned.append(line)

    if len(cleaned) < 2:
        return None
        
    return "flowchart TD\n" + "\n".join(cleaned)

# ==============================
# EXPORT
# ==============================
def export(code):
    mmd_file = "project_flow.mmd"
    svg_file = "project_flow.svg"
    png_file = "project_flow.png"
    
    with open(mmd_file, "w", encoding="utf-8") as f:
        f.write(code)
        
    try:
        # Xuất SVG và PNG
        subprocess.run(["mmdc", "-i", mmd_file, "-o", svg_file], check=True, capture_output=True)
        subprocess.run(["mmdc", "-i", mmd_file, "-o", png_file], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"❌ mmdc Error: {e}")
        return False

# ==============================
# MAIN
# ==============================
def main():
    print(f"🔍 Đang truy vết logic (Route/Controller/Service) cho: {USER_REQUIREMENT}")
    
    files = find_source_files(PROJECT_PATH)
    if not files:
        print("❌ Lỗi: Không tìm thấy file Router, Controller hay Service nào.", file=sys.stderr)
        sys.exit(1)

    print(f"📄 Tìm thấy {len(files)} file logic quan trọng.")
    context = build_context(files)
    
    print("🤖 AI đang phân tích luồng thực thi chi tiết...")

    for i in range(3):
        try:
            raw = call_ai(build_prompt(context, USER_REQUIREMENT))
            clean = sanitize(raw)
            
            if not clean:
                raise Exception("AI trả về kết quả chứa rác hoặc không phải Mermaid hợp lệ.")
            
            if export(clean):
                print(f"\n--- Sơ đồ Mermaid (Lần thử {i+1}) ---\n{clean}\n")
                print("✅ THÀNH CÔNG: Đã tạo file project_flow.png!")
                return
            else:
                raise Exception("mmdc không thể render sơ đồ.")
                
        except Exception as e:
            print(f"⚠️ Lần thử {i+1} thất bại: {e}")

    print("\n❌ LỖI NGHIÊM TRỌNG: Không thể tạo sơ đồ chi tiết.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()