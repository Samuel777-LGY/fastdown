import os
import tkinter as tk
import tkinter.messagebox as mes_box
import webbrowser
from tkinter import ttk, scrolledtext
import requests
import threading

class FastDownloader(object):
    __doc__ = '\n    快速下载工具界面\n    '

    def __init__(self, weight=800, height=600):
        self.ui_weight = weight
        self.ui_height = height
        self.title = '快速下载工具'
        self.ui_root = tk.Tk(className=self.title)
        self.ui_urls = tk.Text(self.ui_root, wrap=tk.WORD, height=10, width=70, font=('Helvetica', 12))
        self.download_button = None
        self.progress_bars = []
        self.status_text = scrolledtext.ScrolledText(self.ui_root, wrap=tk.WORD, height=10, width=70, font=('Helvetica', 12))
        self.progress_text = scrolledtext.ScrolledText(self.ui_root, wrap=tk.WORD, height=10, width=70, font=('Helvetica', 12))
        self.executor = None

        # 设置窗口属性
        self.ui_root.geometry(f'{self.ui_weight}x{self.ui_height}')
        self.ui_root.configure(bg='#f0f0f0')

        # 设置主题风格
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#f0f0f0", foreground="#333333")
        style.configure("TEntry", fieldbackground="#ffffff", foreground="#333333")
        style.configure("TButton", background="#4CAF50", foreground="#ffffff", font=("Helvetica", 12))
        style.map("TButton", background=[('active', '#45a049')])
        style.configure("Horizontal.TProgressbar", troughcolor="#e0e0df", background="#76A7FA")

        # 设置窗口图标
        try:
            self.ui_root.iconbitmap('lgy.ico')  # 替换为你的图标路径
        except Exception as e:
            print(f"无法设置窗口图标: {e}")

    def set_ui(self):
        """
        设置简易UI界面
        :return:
        """
        frame_1 = tk.Frame(self.ui_root, bg='#f0f0f0')
        frame_2 = tk.Frame(self.ui_root, bg='#f0f0f0')
        frame_3 = tk.Frame(self.ui_root, bg='#f0f0f0')
        frame_4 = tk.Frame(self.ui_root, bg='#f0f0f0')
        ui_menu = tk.Menu(self.ui_root, bg='#f0f0f0', fg='#333333')
        self.ui_root.config(menu=ui_menu)
        file_menu = tk.Menu(ui_menu, tearoff=0, bg='#f0f0f0', fg='#333333')
        ui_menu.add_cascade(label='菜单', menu=file_menu)
        file_menu.add_command(label='使用说明', command=(lambda: webbrowser.open('https://lgyfastdown.pages.dev')))
        file_menu.add_command(label='关于作者', command=(lambda: webbrowser.open('http://lgycompany.online')))
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=(self.ui_root.quit))
        
        input_label = tk.Label(frame_1, text='请输入下载链接（每行一个）：', font=('Helvetica', 14), bg='#f0f0f0')
        self.download_button = tk.Button(frame_2, text='开始下载', font=('Helvetica', 12), fg='white', bg='#4CAF50', activebackground='#45a049', width=15, command=(self.start_download))
        status_label = tk.Label(frame_3, text='下载状态：', font=('Helvetica', 14), bg='#f0f0f0')
        progress_label = tk.Label(frame_4, text='进度条：', font=('Helvetica', 14), bg='#f0f0f0')
        
        frame_1.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame_2.pack(fill=tk.X, padx=10, pady=10)
        frame_3.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame_4.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        input_label.pack(side=tk.TOP, padx=10, pady=10)
        self.ui_urls.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.download_button.pack(side=tk.TOP, padx=10, pady=10)
        status_label.pack(side=tk.TOP, padx=10, pady=10)
        self.status_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        progress_label.pack(side=tk.TOP, padx=10, pady=10)
        self.progress_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def start_download(self):
        """
        开始下载文件
        :return:
        """
        urls = self.ui_urls.get("1.0", tk.END).strip().split('\n')
        if not urls or all(not url.strip() for url in urls):
            mes_box.showerror(title='错误', message='未输入下载链接，请输入后重试！')
            return

        self.download_button.config(state=tk.DISABLED)
        self.status_text.delete("1.0", tk.END)
        self.progress_text.delete("1.0", tk.END)

        for i, url in enumerate(urls):
            url = url.strip()
            if url:
                progress_bar = ttk.Progressbar(self.progress_text, orient=tk.HORIZONTAL, length=600, mode='determinate', style="Horizontal.TProgressbar")
                progress_bar.pack(fill=tk.X, padx=10, pady=5)
                self.progress_bars.append((url, progress_bar))
                self.executor = threading.Thread(target=self.download_file, args=(url, progress_bar))
                self.executor.start()

    def download_file(self, url, progress_bar):
        """
        下载文件
        :param url: 文件的URL
        :param progress_bar: 对应的进度条
        :return:
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            response = requests.head(url, allow_redirects=True, headers=headers, timeout=10)
            if response.status_code != 200:
                self.update_status(progress_bar, f'无法访问链接 {url}，状态码: {response.status_code}\n')
                return

            content_length = int(response.headers.get('content-length', 0))
            if content_length == 0:
                self.update_status(progress_bar, f'无法获取文件大小，下载可能失败。链接: {url}\n')
                return

            filename = url.split('/')[-1]
            desktop_path = os.path.expanduser("~/Desktop")
            save_path = os.path.join(desktop_path, 'downloads', filename).replace('\\', '/')
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))

            progress_bar['maximum'] = content_length
            progress_bar['value'] = 0

            with requests.get(url, stream=True, headers=headers, timeout=10) as response:
                response.raise_for_status()
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        self.update_progress(progress_bar, len(chunk))

            self.update_status(progress_bar, f'文件已成功下载到 {os.path.abspath(save_path)}\n')

        except Exception as e:
            self.update_status(progress_bar, f'下载过程中发生错误: {e} (链接: {url})\n')
        finally:
            self.check_all_downloads_complete()

    def update_progress(self, progress_bar, increment):
        """
        更新进度条
        :param progress_bar: 进度条对象
        :param increment: 增加的字节数
        :return:
        """
        current_value = progress_bar['value']
        new_value = min(current_value + increment, progress_bar['maximum'])
        progress_bar['value'] = new_value
        percentage = (new_value / progress_bar['maximum']) * 100
        progress_bar['value'] = new_value
        progress_bar.config(value=new_value)
        progress_bar.update_idletasks()
        self.update_status(progress_bar, f'进度: {percentage:.2f}%\n')

    def update_status(self, progress_bar, message):
        """
        更新状态文本框
        :param progress_bar: 进度条对象
        :param message: 状态消息
        :return:
        """
        index = self.status_text.index(tk.END)
        self.status_text.insert(index, message)
        self.status_text.yview(tk.END)
        self.ui_root.update_idletasks()

    def check_all_downloads_complete(self):
        """
        检查所有下载是否完成
        :return:
        """
        all_completed = all(bar['value'] >= bar['maximum'] for _, bar in self.progress_bars)
        if all_completed:
            self.download_button.config(state=tk.NORMAL)
            mes_box.showinfo(title='下载完成', message='所有文件已下载完毕。')
            for _, progress_bar in self.progress_bars:
                progress_bar['value'] = 0  # 归零进度条

if __name__ == "__main__":
    app = FastDownloader()
    app.set_ui()
    app.ui_root.mainloop()
