import tkinter as tk
from tkinter import filedialog
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox

import nlc_isbn
from formatting import format_metadata
import pyperclip
import webbrowser
import bookmarkget


class EbookDataGeterApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")  # 主题可选: cosmo, superhero, darkly, flatly
        self.title("EbookDataGeter Pro")
        self.geometry("1000x700")
        try:
            self.iconbitmap('logo.ico')
        except:
            pass

        self.create_widgets()

    def create_widgets(self):
        # --- 顶部输入区 ---
        input_frame = ttk.Labelframe(self, text="检索控制台", padding=15)
        input_frame.pack(fill=X, padx=15, pady=10)

        # ISBN 输入
        ttk.Label(input_frame, text="ISBN 号码:").pack(side=LEFT, padx=(0, 5))

        # 验证命令
        vcmd = (self.register(self.validate_isbn_input), '%P')
        self.entry_isbn = ttk.Entry(input_frame, width=30, validate='key', validatecommand=vcmd)
        self.entry_isbn.pack(side=LEFT, padx=5)
        self.entry_isbn.bind("<Return>", lambda event: self.search_isbn())  # 回车键查询

        # 功能按钮群
        self.btn_search = ttk.Button(input_frame, text="🔍 开始查询", command=self.search_isbn, bootstyle=PRIMARY)
        self.btn_search.pack(side=LEFT, padx=10)

        ttk.Separator(input_frame, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=10)

        self.btn_copy_meta = ttk.Button(input_frame, text="📋 复制元数据", command=self.copy_to_clipboard,
                                        bootstyle="outline-secondary")
        self.btn_copy_meta.pack(side=LEFT, padx=5)

        self.btn_copy_bm = ttk.Button(input_frame, text="📑 复制书签", command=self.copy_bookmarks_to_clipboard,
                                      bootstyle="outline-secondary")
        self.btn_copy_bm.pack(side=LEFT, padx=5)

        self.btn_save = ttk.Button(input_frame, text="💾 保存书签", command=self.save_bookmarks_to_file,
                                   bootstyle="outline-success")
        self.btn_save.pack(side=LEFT, padx=5)

        # --- 进度条 (默认隐藏) ---
        self.progress = ttk.Progressbar(self, mode=INDETERMINATE, bootstyle="info-striped")

        # --- 主要内容展示区 (PanedWindow 分割) ---
        paned_window = ttk.Panedwindow(self, orient=HORIZONTAL)
        paned_window.pack(fill=BOTH, expand=True, padx=15, pady=5)

        # 左侧：元数据
        frame_left = ttk.Labelframe(paned_window, text="📚 图书元数据", padding=10)
        paned_window.add(frame_left, weight=1)
        self.text_result = ScrolledText(frame_left, font=("Consolas", 10))
        self.text_result.pack(fill=BOTH, expand=True)

        # 右侧：目录书签
        frame_right = ttk.Labelframe(paned_window, text="🔖 目录书签", padding=10)
        paned_window.add(frame_right, weight=1)
        self.text_bookmarks = ScrolledText(frame_right, font=("Consolas", 10))
        self.text_bookmarks.pack(fill=BOTH, expand=True)

        # --- 底部日志与状态区 ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=X, padx=15, pady=10)

        # 日志区
        log_frame = ttk.Labelframe(bottom_frame, text="运行日志", padding=5)
        log_frame.pack(side=TOP, fill=X)
        self.text_log = ScrolledText(log_frame, height=5, font=("Arial", 9))
        self.text_log.pack(fill=BOTH, expand=True)

        # 状态栏与链接
        status_frame = ttk.Frame(bottom_frame)
        status_frame.pack(side=TOP, fill=X, pady=(5, 0))

        self.status_label = ttk.Label(status_frame, text="就绪", bootstyle="inverse-secondary", padding=5)
        self.status_label.pack(side=LEFT, fill=X, expand=True)

        link_frame = ttk.Frame(status_frame)
        link_frame.pack(side=RIGHT)

        btn_gitee = ttk.Button(link_frame, text="Gitee", command=self.open_gitee, bootstyle="link")
        btn_gitee.pack(side=LEFT)
        btn_github = ttk.Button(link_frame, text="GitHub", command=self.open_github, bootstyle="link")
        btn_github.pack(side=LEFT)

    def validate_isbn_input(self, new_value):
        return new_value.isdigit() or new_value == ""

    def search_isbn(self):
        isbn = self.entry_isbn.get()
        if not isbn:
            Messagebox.show_warning("请输入ISBN号码", title="提示")
            return

        self.log_message(f"准备检索 ISBN: {isbn}")
        self.update_status("正在连接数据库检索...")

        self.text_result.text.delete('1.0', tk.END)
        self.text_bookmarks.text.delete('1.0', tk.END)

        # UI 状态切换
        self.btn_search.config(state=DISABLED)
        # 将进度条插入到输入框所在的 Labelframe 底部
        self.progress.pack(in_=self.entry_isbn.master, fill=X, padx=15, pady=(5, 0))
        self.progress.start(10)

        threading.Thread(target=self.perform_search, args=(isbn,), daemon=True).start()

    def perform_search(self, isbn):
        # 1. 抓取元数据
        try:
            metadata = nlc_isbn.isbn2meta(isbn, lambda msg: self.safe_update_status(f"NLC: {msg}"))
            self.after(0, lambda: self.handle_metadata_result(metadata))
        except Exception as e:
            self.after(0, lambda: self.log_message(f"❌ 元数据错误: {e}"))

        # 2. 抓取书签
        try:
            self.safe_update_status("正在书葵网检索书签...")
            bookmarks_info = bookmarkget.get_book_details(isbn)
            self.after(0, lambda: self.text_bookmarks.text.insert(tk.END, bookmarks_info))
        except Exception as e:
            self.after(0, lambda: self.log_message(f"❌ 书签错误: {e}"))

        self.after(0, self.finish_search)

    def finish_search(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_search.config(state=NORMAL)
        self.update_status("检索任务结束")

    def safe_update_status(self, message):
        self.after(0, lambda: self.update_status(message))

    def update_status(self, message):
        self.status_label.config(text=message)

    def handle_metadata_result(self, metadata):
        if metadata:
            formatted_result = format_metadata(metadata)
            self.text_result.text.insert(tk.END, formatted_result)
            self.log_message("✅ 元数据检索成功")
        else:
            self.text_result.text.insert(tk.END, "❌ 未找到元数据。")
            self.log_message("⚠️ 未找到元数据")

    def log_message(self, message):
        self.text_log.text.insert(tk.END, message + "\n")
        self.text_log.text.see(tk.END)

    def copy_to_clipboard(self):
        text = self.text_result.text.get("1.0", tk.END)
        pyperclip.copy(text)
        self.update_status("元数据已复制")

    def copy_bookmarks_to_clipboard(self):
        text = self.text_bookmarks.text.get("1.0", tk.END)
        pyperclip.copy(text)
        self.update_status("书签已复制")

    def save_bookmarks_to_file(self):
        text = self.text_bookmarks.text.get("1.0", tk.END)
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            self.log_message(f"书签保存至: {path}")

    def open_github(self):
        webbrowser.open("https://github.com/Hellohistory/EbookDataTools")

    def open_gitee(self):
        webbrowser.open("https://github.com/Hellohistory/EbookDataTools")


if __name__ == "__main__":
    app = EbookDataGeterApp()
    app.mainloop()