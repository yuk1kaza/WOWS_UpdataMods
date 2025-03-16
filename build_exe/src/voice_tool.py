#————————少司命 编辑于2025/3/15——————————
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import json
from pathlib import Path
from datetime import datetime


class AdvancedFolderCopyApp:
    CONFIG_FILE = "user_config.json"
    DEFAULT_CONFIG = {
        "source_path": "",
        "target_path": "",
        "mode": "banks",
        "dev_message": "欢迎使用窝批语音包复制工具！\n请选择源文件夹和目标路径后开始操作。"
    }

    def __init__(self, master):
        self.master = master
        master.title("窝批语音包复制工具 v1.1 by 少司命")
        master.geometry("840x560")

        # 初始化配置
        self.config = self.load_config()

        # 初始化变量
        self.mode = tk.StringVar(value=self.config["mode"])
        self.source_path = tk.StringVar(value=self.config["source_path"])
        self.target_path = tk.StringVar(value=self.config["target_path"])

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 布局配置
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(5, weight=1)

        # 源文件夹选择
        ttk.Label(self.master, text="语音包文件夹：").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.source_entry = ttk.Entry(self.master, textvariable=self.source_path, width=50)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self.master, text="浏览...", command=self.browse_source).grid(row=0, column=2, padx=5)

        # 目标路径选择
        ttk.Label(self.master, text="游戏文件基础路径：").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.target_entry = ttk.Entry(self.master, textvariable=self.target_path, width=50)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self.master, text="浏览...", command=self.browse_target).grid(row=1, column=2, padx=5)

        # 模式选择
        mode_frame = ttk.LabelFrame(self.master, text="安装模式")
        mode_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        ttk.Radiobutton(mode_frame, text="banks模式 (适用于语音包文件夹名称为banks)",
                        variable=self.mode, value="banks").pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="Mods模式 (适用于语音包文件夹名称为Mods)",
                        variable=self.mode, value="mods").pack(side="left", padx=10)

        # 操作按钮
        btn_frame = ttk.Frame(self.master)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.copy_btn = ttk.Button(btn_frame, text="开始安装", command=self.start_copy_thread)
        self.copy_btn.pack(side="left", padx=5)

        ttk.Button(btn_frame, text="重置设置", command=self.reset_config).pack(side="left", padx=5)

        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.master, textvariable=self.status_var, foreground="gray").grid(row=4, column=0, columnspan=3)

        # 开发人员提示区域
        dev_frame = ttk.LabelFrame(self.master, text="开发人员提示：暂无  2025/3/15")
        dev_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.dev_text = tk.Text(dev_frame, height=4, wrap="word")
        self.dev_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.dev_text.insert("1.0", self.config["dev_message"])
        self.dev_text.config(state="disabled")

        # 日志区域
        self.log_text = tk.Text(self.master, height=8, state="disabled")
        self.log_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_path.set(path)
            self.save_config()

    def browse_target(self):
        path = filedialog.askdirectory()
        if path:
            self.target_path.set(path)
            self.save_config()

    def load_config(self):
        """加载用户配置"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存当前配置"""
        self.config.update({
            "source_path": self.source_path.get(),
            "target_path": self.target_path.get(),
            "mode": self.mode.get(),
            "dev_message": self.dev_text.get("1.0", "end-1c")
        })
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def reset_config(self):
        """重置为默认设置"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.source_path.set(self.config["source_path"])
        self.target_path.set(self.config["target_path"])
        self.mode.set(self.config["mode"])
        self.dev_text.config(state="normal")
        self.dev_text.delete("1.0", "end")
        self.dev_text.insert("1.0", self.config["dev_message"])
        self.dev_text.config(state="disabled")
        self.save_config()
        messagebox.showinfo("提示", "已重置为默认设置")

    def log_message(self, message, color="black"):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.tag_add(color, "end-1c linestart", "end-1c lineend")
        self.log_text.tag_config(color, foreground=color)
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.status_var.set(message)

    def start_copy_thread(self):
        Thread(target=self.perform_copy, daemon=True).start()

    def perform_copy(self):
        self.copy_btn.config(state="disabled")
        try:
            # 获取输入参数
            source = self.source_path.get()
            target_base = self.target_path.get()
            mode = self.mode.get()

            # 验证输入
            if not source or not target_base:
                raise ValueError("请先选择源文件夹和目标路径")

            if not os.path.exists(source):
                raise FileNotFoundError(f"源语音包文件夹不存在: {source}")

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
            self.log_message(f"找到最新游戏版本文件夹: {max_folder}", "darkgreen")

            # 根据模式构建最终路径
            base_target = os.path.join(target_bin, max_folder, "res_mods")
            if mode == "mods":
                base_target = os.path.join(base_target, "banks")

            final_target = os.path.join(base_target, os.path.basename(source))
            self.log_message(f"目标路径: {final_target}")

            # 创建目录
            os.makedirs(os.path.dirname(final_target), exist_ok=True)

            # 删除已有内容
            if os.path.exists(final_target):
                self.log_message("正在清理旧版本...", "blue")
                shutil.rmtree(final_target)

            # 执行复制
            self.log_message("正在复制文件...", "blue")
            shutil.copytree(source, final_target)

            self.log_message("操作成功完成！\n完成于" + str(datetime.now()), "darkgreen")
            messagebox.showinfo("成功", "语音包安装完成！")
            self.save_config()  # 保存成功配置

        except Exception as e:
            self.log_message(f"错误: {str(e)}", "red")
            messagebox.showerror("错误", str(e))

        finally:
            self.copy_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFolderCopyApp(root)
    root.mainloop()