import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def select_folder():
    path = filedialog.askdirectory()
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)

def run_script():
    project_path = entry_path.get()
    user_req = entry_req.get() # Lấy thông tin chức năng từ ô nhập liệu
    
    if not project_path or not os.path.exists(project_path):
        messagebox.showerror("Lỗi", "Vui lòng chọn thư mục dự án!")
        return
    
    if not user_req.strip():
        messagebox.showerror("Lỗi", "Vui lòng nhập chức năng cần vẽ!")
        return

    lbl_status.config(text="🚀 AI đang phân tích chức năng...", fg="blue")
    root.update()

    try:
        # Truyền thêm tham số user_req vào sau project_path
        result = subprocess.run(
            ["python3", "analyze.py", project_path, user_req],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            messagebox.showinfo("Thành công", f"Đã vẽ xong sơ đồ cho: {user_req}")
        else:
            messagebox.showerror("Lỗi", result.stderr)
            
    except Exception as e:
        messagebox.showerror("Lỗi hệ thống", str(e))
    finally:
        lbl_status.config(text="Sẵn sàng", fg="green")

# --- GIAO DIỆN ---
root = tk.Tk()
root.title("AI Diagram Pro")
root.geometry("550x350")

# 1. Chọn Folder
tk.Label(root, text="1. Thư mục dự án:", font=("Arial", 10, "bold")).pack(pady=(20,0), anchor="w", padx=50)
frame1 = tk.Frame(root)
frame1.pack(pady=5)
entry_path = tk.Entry(frame1, width=40)
entry_path.pack(side=tk.LEFT, padx=5)
tk.Button(frame1, text="Browse", command=select_folder).pack(side=tk.LEFT)

# 2. Nhập yêu cầu
tk.Label(root, text="2. Chức năng cần vẽ (ví dụ: flow thanh toán, upload ảnh...):", font=("Arial", 10, "bold")).pack(pady=(15,0), anchor="w", padx=50)
entry_req = tk.Entry(root, width=56)
entry_req.insert(0, "- authentication flow, login, register") # Gợi ý mặc định
entry_req.pack(pady=5)

# 3. Nút bấm
btn_run = tk.Button(root, text="GENERATE DIAGRAM", command=run_script, 
                   bg="#2ecc71", font=("Arial", 11, "bold"), width=20, height=2)
btn_run.pack(pady=25)

lbl_status = tk.Label(root, text="Sẵn sàng", fg="green")
lbl_status.pack()

root.mainloop()