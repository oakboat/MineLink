import re
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox
import requests
from mcstatus import JavaServer
from tkinter import ttk  # 导入 ttk
from queue import Queue

# Flask 服务器的 URL（根据需要更新）
SERVER_URL_BASE = 'https://ml.hhhhhi.com/'
SERVER_URL_CREATE = SERVER_URL_BASE + '/create_room'
SERVER_URL_JOIN = SERVER_URL_BASE + '/join_room'
SERVER_URL_HEARTBEAT = SERVER_URL_BASE + '/heartbeat'

def create_room():
    """处理创建房间的逻辑"""
    room_name = room_name_entry.get()
    address = address_entry.get()

    # 输入验证
    if not room_name:
        messagebox.showerror("错误", "房间名称是必填的")
        return
    
    if not room_name:
        messagebox.showerror("错误", "房间名称是必填的")
        return
    
    try:
        players = get_players(address)
    except Exception as e:
        messagebox.showerror("错误", f"获取本地Minecraft服务器失败：{e}")
        return

    if ':' in address:
        port = address.split(':')[1]
    else:
        port = '25565'

    tunnel_id = create_tunnel(port)
    
    if not tunnel_id:
        return

    # 准备 POST 请求的 payload
    payload = {
        'room_name': room_name,
        'players': players,
        'tunnel_id': tunnel_id,
    }

    # 发送 POST 请求到 Flask 服务器
    try:
        response = requests.post(SERVER_URL_CREATE, json=payload)
        data = response.json()

        if response.status_code == 200:
            # 房间创建成功
            messagebox.showinfo("成功", f"房间创建成功！房间代码：{data['room_code']}")
        else:
            # 错误响应
            messagebox.showerror("错误", data.get('error', '发生了未知错误'))
    
    except requests.exceptions.RequestException as e:
        # 处理请求错误（例如，服务器无法连接）
        messagebox.showerror("错误", f"连接服务器失败：{e}")
    
    threading.Thread(target=heartbeat, args=(address, data['room_code'])).start()

def get_players(address):
    server = JavaServer.lookup(address)
    status = server.status()
    return status.players.online
    
def create_tunnel(port):
    """使用 subprocess 启动 p2ptunnel 并获取隧道 ID"""
    try:
        # 执行 p2ptunnel 命令并持续运行
        command = ['p2ptunnel', '-type', 'tcp', '-l', port]
        process = subprocess.Popen(
            command,  # 替换为你要运行的命令
            stderr=subprocess.PIPE,
            text=True  # 如果你希望输出是字符串类型
        )
        
        tunnel_id = None
        
        # 从 p2ptunnel 的输出中提取隧道 ID
        for line in process.stderr:
            match = re.search(r'Your id: ([\w]+)', line)
            if match:
                tunnel_id = match.group(1)
                break

        return tunnel_id

    except Exception as e:
        messagebox.showerror("错误", f"创建隧道时发生错误：{str(e)}")

def heartbeat(address, room_code):
    """更新房间的心跳时间"""
    while True:
        try:
            players = get_players(address)
        except Exception as e:
            messagebox.showerror("错误", f"获取本地Minecraft服务器失败：{e}")
            break
        payload = {
            'room_code': room_code,
            'players': players
        }
        try:
            response = requests.post(SERVER_URL_HEARTBEAT, json=payload)
            data = response.json()

            if response.status_code != 200:
                messagebox.showerror("错误", "心跳: "+data.get('error', '发生了未知错误'))
                break
        
        except requests.exceptions.RequestException as e:
            # 处理请求错误（例如，服务器无法连接）
            messagebox.showerror("错误", f"连接服务器失败：{e}")
            break
        time.sleep(10)

def join_room():
    """处理加入房间的逻辑"""
    room_code = room_code_entry.get()

    # 输入验证
    if not room_code:
        messagebox.showerror("错误", "房间代码是必填的")
        return
    
    # 准备 POST 请求的 payload
    payload = {
        'room_code': room_code
    }

    # 发送 POST 请求到 Flask 服务器
    try:
        response = requests.post(SERVER_URL_JOIN, json=payload)
        data = response.json()

        if response.status_code == 200:
            # 加入房间成功
            tunnel_id = data.get('tunnel_id')
        else:
            # 错误响应
            messagebox.showerror("错误", data.get('error', '发生了未知错误'))
    
    except requests.exceptions.RequestException as e:
        # 处理请求错误（例如，服务器无法连接）
        messagebox.showerror("错误", f"连接服务器失败：{e}")

    address = join_tunnel(tunnel_id)

    if not address:
        messagebox.showerror("错误", "加入隧道失败")
        return
    
    messagebox.showinfo("成功", f"成功加入房间！地址：{address}")

def join_tunnel(tunnel_id):
    """使用 subprocess 启动 p2ptunnel 并获取隧道 ID"""
    try:
        # 执行 p2ptunnel 命令并持续运行
        command = ['p2ptunnel', '-id', tunnel_id]
        process = subprocess.Popen(
            command,  # 替换为你要运行的命令
            stderr=subprocess.PIPE,
            text=True  # 如果你希望输出是字符串类型
        )
        
        address = None
        
        # 从 p2ptunnel 的输出中提取隧道 ID
        for line in process.stderr:
            match = re.search(r'Listening tcp (\d+\.\d+\.\d+\.\d+:\d+)', line)
            if match:
                address = match.group(1)
                break

        return address

    except Exception as e:
        messagebox.showerror("错误", f"加入隧道时发生错误：{str(e)}")

# 创建 tkinter 窗口
root = tk.Tk()
root.title("创建或加入房间")

# 房间名称输入框
tk.Label(root, text="房间名称").pack(padx=20, pady=5)
room_name_entry = tk.Entry(root, width=40)
room_name_entry.pack(padx=20, pady=5)

# 玩家人数输入框
tk.Label(root, text="地址").pack(padx=20, pady=5)
address_entry = tk.Entry(root, width=40)
address_entry.insert(0, "localhost:25565")
address_entry.pack(padx=20, pady=5)

# 创建房间按钮
create_button = tk.Button(root, text="创建房间", command=create_room)
create_button.pack(padx=20, pady=20)

# 使用 ttk.Separator 创建分隔符
separator = ttk.Separator(root, orient='horizontal')  # 修改为 ttk.Separator
separator.pack(fill='x', padx=20, pady=10)

# 房间代码输入框（用于加入房间）
tk.Label(root, text="房间代码").pack(padx=20, pady=5)
room_code_entry = tk.Entry(root, width=40)
room_code_entry.pack(padx=20, pady=5)

# 加入房间按钮
join_button = tk.Button(root, text="加入房间", command=join_room)
join_button.pack(padx=20, pady=20)

# 运行 tkinter 主循环
root.mainloop()
