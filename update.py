import os
import tkinter as tk
import urllib.request
from tkinter import messagebox


def get_local_version():
    if os.path.exists("version.txt"):
        with open("version.txt", "r") as file:
            return file.read().strip()
    return None


def get_remote_version(remote_url):
    try:
        response = urllib.request.urlopen(remote_url)
        return response.read().decode("utf-8").strip()
    except Exception as e:
        messagebox.showinfo("提示", "无法获取远程版本信息")
        return None


def download_update(update_url):
    try:
        os.system("start " + update_url)
    except Exception as e:
        messagebox.showinfo("提示", "无法打开更新文件")
        return


def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)  # 窗口置顶
    messagebox.showinfo("提示", "正在检查版本...")

    local_version = get_local_version()
    if local_version is None:
        messagebox.showinfo("提示", "本地版本文件不存在或无法读取")
        return

    remote_version = get_remote_version("https://c.mhkvm.com/version.txt")
    if remote_version is None:
        return

    message = f"本地版本: {local_version}\n远程版本: {remote_version}\n"
    if local_version < remote_version:
        remote_url = "https://c.mhkvm.com/mess.txt"
        try:
            response = urllib.request.urlopen(remote_url)
            content = response.read().decode("utf-8")
            message += f"\n更新内容:\n{content}\n"
            message += "该版本需要更新\n是否打开链接进行更新？\n"
            result = messagebox.askquestion("版本信息", message)
            if result == 'yes':
                download_update("https://www.minebbs.com/resources/4-0-paper-1-20-2-je-be.4663/updates")
        except Exception as e:
            messagebox.showinfo("提示", "无法获取远程文件内容")

    else:
        message += "已经是最新版本\n放心游玩哦~"
        messagebox.showinfo("版本信息", message)


if __name__ == "__main__":
    main()
