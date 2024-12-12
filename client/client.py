import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from room import RoomManager

class RoomManagerGUI:
    """负责 GUI 交互的类"""
    def __init__(self, master):
        self.master = master
        self.room_manager = RoomManager()
        self.master.title("创建或加入房间")
        self.create_widgets()

    def create_widgets(self):
        # 创建房间部分
        tk.Label(self.master, text="房间名称").pack(padx=20, pady=5)
        self.room_name_entry = tk.Entry(self.master, width=40)
        self.room_name_entry.pack(padx=20, pady=5)

        tk.Label(self.master, text="地址").pack(padx=20, pady=5)
        self.address_entry = tk.Entry(self.master, width=40)
        self.address_entry.insert(0, "localhost:25565")
        self.address_entry.pack(padx=20, pady=5)

        create_button = tk.Button(self.master, text="创建房间", command=self.handle_create_room)
        create_button.pack(padx=20, pady=20)

        separator = ttk.Separator(self.master, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=10)

        # 加入房间部分
        tk.Label(self.master, text="房间代码").pack(padx=20, pady=5)
        self.room_code_entry = tk.Entry(self.master, width=40)
        self.room_code_entry.pack(padx=20, pady=5)

        join_button = tk.Button(self.master, text="加入房间", command=self.handle_join_room)
        join_button.pack(padx=20, pady=20)

    def handle_create_room(self):
        room_name = self.room_name_entry.get()
        address = self.address_entry.get()
        try:
            room_code = self.room_manager.create_room(room_name, address)
            messagebox.showinfo("成功", f"房间创建成功！房间代码：{room_code}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def handle_join_room(self):
        room_code = self.room_code_entry.get()
        try:
            address = self.room_manager.join_room(room_code)
            messagebox.showinfo("成功", f"成功加入房间！地址：{address}")
        except Exception as e:
            messagebox.showerror("错误", str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app = RoomManagerGUI(root)
    root.mainloop()
