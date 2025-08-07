import tkinter as tk
import re
from tkinter import messagebox, scrolledtext, filedialog
import threading
import nlc_isbn
from formatting import format_metadata
import pyperclip
import webbrowser
import bookmarkget


def search_isbn():
    isbn = entry_isbn.get()
    log_message("检索 ISBN: " + isbn)
    update_status("正在检索...")
    text_result.delete('1.0', tk.END)
    text_bookmarks.delete('1.0', tk.END)
    root.update_idletasks()

    try:
        # 启动线程以异步获取书签信息
        threading.Thread(target=lambda: fetch_bookmark_info(isbn), daemon=True).start()

        # 同步执行元数据检索，并将update_status作为参数传递
        metadata = nlc_isbn.isbn2meta(isbn, update_status)
        if metadata:
            formatted_result = format_metadata(metadata)
            text_result.insert(tk.END, formatted_result)
            update_status("检索完成")
        else:
            text_result.insert(tk.END, "无法找到元数据。")
            update_status("未找到数据")
    except Exception as e:
        messagebox.showerror("错误", str(e))
        update_status("检索出错")


def fetch_bookmark_info(isbn):
    try:
        bookmarks_info = bookmarkget.get_book_details(isbn)
        text_bookmarks.insert(tk.END, bookmarks_info)
    except Exception as e:
        messagebox.showerror("错误", str(e))


def copy_to_clipboard():
    text = text_result.get("1.0", tk.END)
    pyperclip.copy(text)
    log_message("信息已复制到剪贴板。")


def copy_bookmarks_to_clipboard():
    bookmarks_text = text_bookmarks.get("1.0", tk.END)
    pyperclip.copy(bookmarks_text)
    log_message("书签信息已复制到剪贴板。")


def save_bookmarks_to_file():
    bookmarks_text = text_bookmarks.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(bookmarks_text)
        log_message("书签信息已保存到文件：" + file_path)


def open_github():
    webbrowser.open("https://github.com/Hellohistory/EbookDataTools")


def open_gitee():
    webbrowser.open("https://github.com/Hellohistory/EbookDataTools")


def log_message(message):
    text_log.insert(tk.END, message + "\n")


def update_status(message):
    status_label.config(text=message)


def filter_input(event):
    # 获取输入框的文本
    input_text = entry_isbn.get()

    # 使用正则表达式替换非数字字符为空字符串
    filtered_text = re.sub(r'[^0-9]', '', input_text)

    # 更新输入框的文本
    entry_isbn.delete(0, tk.END)
    entry_isbn.insert(0, filtered_text)


# GUI样式配置
FONT_NORMAL = ("Arial", 10)
FONT_BOLD = ("Arial", 10, "bold")
BACKGROUND_COLOR = "#F0F0F0"
BUTTON_COLOR = "#E0E0E0"

# 创建主窗口
root = tk.Tk()
root.title("EbookDataGeter")
root.geometry("900x600")
root.iconbitmap('logo.ico')
root.configure(bg=BACKGROUND_COLOR)

# 使用 Grid 布局
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# 状态栏
status_label = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=BACKGROUND_COLOR, font=FONT_NORMAL)
status_label.grid(row=2, column=0, columnspan=2, sticky="ew")

# 创建并放置控件
frame = tk.Frame(root, bg=BACKGROUND_COLOR)
frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

label_isbn = tk.Label(frame, text="请输入ISBN号码：", font=FONT_NORMAL, bg=BACKGROUND_COLOR)
label_isbn.pack(side=tk.LEFT)

# 创建输入框
entry_isbn = tk.Entry(frame, font=FONT_NORMAL)
entry_isbn.pack(side=tk.LEFT, padx=5)

# 绑定输入过滤函数到文本变化事件
entry_isbn.bind("<KeyRelease>", filter_input)

button_search = tk.Button(frame, text="查询", command=search_isbn, bg=BUTTON_COLOR, font=FONT_BOLD)
button_search.pack(side=tk.LEFT, padx=5)

button_copy = tk.Button(frame, text="复制信息", command=copy_to_clipboard, bg=BUTTON_COLOR, font=FONT_BOLD)
button_copy.pack(side=tk.LEFT, padx=5)

button_copy_bookmarks = tk.Button(frame, text="复制书签信息", command=copy_bookmarks_to_clipboard, bg=BUTTON_COLOR,
                                  font=FONT_BOLD)
button_copy_bookmarks.pack(side=tk.LEFT, padx=5)

button_save_bookmarks = tk.Button(frame, text="保存书签信息", command=save_bookmarks_to_file, bg=BUTTON_COLOR,
                                  font=FONT_BOLD)
button_save_bookmarks.pack(side=tk.LEFT, padx=5)

text_result = scrolledtext.ScrolledText(root, height=10, font=FONT_NORMAL)
text_result.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

text_bookmarks = scrolledtext.ScrolledText(root, height=10, font=FONT_NORMAL)
text_bookmarks.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

text_log = scrolledtext.ScrolledText(root, height=5, font=FONT_NORMAL)
text_log.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

# 创建一个Frame来包含两个链接
link_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
link_frame.grid(row=4, column=1, sticky="se", padx=10, pady=5)

# Gitee 链接
gitee_link = tk.Label(link_frame, text="Gitee地址", fg="blue", cursor="hand1", bg=BACKGROUND_COLOR, font=FONT_NORMAL)
gitee_link.pack(side=tk.RIGHT, padx=(2, 0))  # Pack用于在Frame内部排列
gitee_link.bind("<Button-1>", lambda e: open_gitee())

# Github 链接
github_link = tk.Label(link_frame, text="Github地址", fg="blue", cursor="hand2", bg=BACKGROUND_COLOR, font=FONT_NORMAL)
github_link.pack(side=tk.RIGHT, padx=(2, 2))
github_link.bind("<Button-1>", lambda e: open_github())

root.mainloop()
