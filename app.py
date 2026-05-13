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
    
    if not project_path or not os.path.exists(project_path):
        messagebox.showerror("Lỗi", "Vui lòng chọn thư mục dự án!")
        return

    # Hiển thị trạng thái đang xử lý
    lbl_status.config(text="🚀 Đang xử lý... Vui lòng đợi AI", fg="blue")
    root.update()

    try:
        # Gọi file gốc của bạn y hệt như cách bạn gõ lệnh Terminal
        # python3 analyze.py /path/to/project
        result = subprocess.run(
            ["python3", "analyze.py", project_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            messagebox.showinfo("Thành công", "Đã xuất file PNG thành công từ analyze.py!")
            print(result.stdout) # In log ra terminal để theo dõi
        else:
            messagebox.showerror("Lỗi khi chạy script", result.stderr)
            
    except Exception as e:
        messagebox.showerror("Lỗi hệ thống", str(e))
    finally:
        lbl_status.config(text="Sẵn sàng", fg="green")

# --- GIAO DIỆN ---
root = tk.Tk()
root.title("Công cụ Vẽ Sơ đồ AI")
root.geometry("500x250")

tk.Label(root, text="CHỌN PROJECT ĐỂ VẼ SƠ ĐỒ", font=("Arial", 12, "bold")).pack(pady=20)

frame = tk.Frame(root)
frame.pack(pady=5)

entry_path = tk.Entry(frame, width=40)
entry_path.pack(side=tk.LEFT, padx=5)

btn_browse = tk.Button(frame, text="Browse", command=select_folder)
btn_browse.pack(side=tk.LEFT)

btn_run = tk.Button(root, text="BẮT ĐẦU", command=run_script, 
                   bg="#4CAF50", fg="black", font=("Arial", 10, "bold"), width=15, height=2)
btn_run.pack(pady=20)

lbl_status = tk.Label(root, text="Sẵn sàng", fg="green")
lbl_status.pack()

root.mainloop()