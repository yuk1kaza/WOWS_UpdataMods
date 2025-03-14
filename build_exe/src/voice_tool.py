#————————少司命 编辑于2025/3/13——————————
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import sys
import os

# 资源路径兼容处理
def resource_path(relative_path):
    """ 获取打包后资源的绝对路径 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 设置工作目录
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

class SmartFolderCopyApp:
    def __init__(self, master):
        self.master = master
        master.title("窝批语音包复制工具 by 少司命")
        master.geometry("680x400")

        # 界面样式配置
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        self.style.configure("TLabel", padding=5)

        self.create_widgets()

    def create_widgets(self):
        # 源文件夹选择
        ttk.Label(self.master, text="源文件夹（桌面）：").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.source_entry = ttk.Entry(self.master, width=50)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="浏览...", command=self.browse_source).grid(row=0, column=2, padx=5)

        # 目标路径选择
        ttk.Label(self.master, text="游戏文件基础路径：").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.target_entry = ttk.Entry(self.master, width=50)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="浏览...", command=self.browse_target).grid(row=1, column=2, padx=5)

        # 操作按钮
        self.copy_btn = ttk.Button(self.master, text="开始复制", command=self.start_copy_thread)
        self.copy_btn.grid(row=3, column=1, pady=15)

        # 状态显示
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.master, textvariable=self.status_var, foreground="gray")
        self.status_label.grid(row=4, column=0, columnspan=3)

        # 日志区域
        self.log_text = tk.Text(self.master, height=10, state="disabled")
        self.log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 布局配置
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(1, weight=1)

    def browse_source(self):
        path = filedialog.askdirectory(initialdir=os.path.join(os.path.expanduser('~'), 'Desktop'))
        if path:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, path)

    def browse_target(self):
        path = filedialog.askdirectory()
        if path:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, path)

    def log_message(self, message, color="black"):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.tag_add(color, "end-1c linestart", "end-1c lineend")
        self.log_text.tag_config(color, foreground=color)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.status_var.set(message)

    def start_copy_thread(self):
        Thread(target=self.perform_copy, daemon=True).start()

    def perform_copy(self):
        self.copy_btn.config(state="disabled")
        try:
            # 获取输入参数
            source_path = self.source_entry.get()
            target_base = self.target_entry.get()
            subpath = "res_mods"

            # 验证输入
            if not source_path or not target_base:
                raise ValueError("请先选择banks源文件夹和游戏文件路径")

            # 检查源文件夹
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"banks源文件夹不存在: {source_path}")

            # 构建目标路径
            target_bin = os.path.join(target_base, "bin")
            if not os.path.exists(target_bin):
                raise FileNotFoundError(f"目标路径中不存在bin文件夹: {target_bin}")

            # 查找数字文件夹
            subdirs = [d for d in os.listdir(target_bin)
                       if os.path.isdir(os.path.join(target_bin, d)) and d.isdigit()]

            if not subdirs:
                raise ValueError("bin文件夹中没有纯数字命名的子文件夹")

            max_folder = max(subdirs, key=lambda x: int(x))
            self.log_message(f"找到最新版本文件夹: {max_folder}", "darkgreen")

            # 构建最终路径
            final_target = os.path.join(target_bin, max_folder, subpath, os.path.basename(source_path))
            self.log_message(f"目标路径: {final_target}")

            # 创建目录
            os.makedirs(os.path.dirname(final_target), exist_ok=True)

            # 删除已有内容
            if os.path.exists(final_target):
                self.log_message("正在清理旧版本...", "blue")
                shutil.rmtree(final_target)

            # 执行复制
            self.log_message("正在复制文件...", "blue")
            shutil.copytree(source_path, final_target)

            self.log_message("操作成功完成！", "darkgreen")
            messagebox.showinfo("成功", "文件夹复制完成！")

        except Exception as e:
            self.log_message(f"错误: {str(e)}", "red")
            messagebox.showerror("错误", str(e))

        finally:
            self.copy_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartFolderCopyApp(root)
    root.mainloop()