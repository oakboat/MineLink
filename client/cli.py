import argparse
from room import RoomManager

class RoomManagerCLI:
    """命令行界面 (CLI) 用于操作 RoomManager 类"""

    def __init__(self):
        self.room_manager = RoomManager()

    def create_room(self, room_name, address):
        try:
            room_code = self.room_manager.create_room(room_name, address)
            print(f"房间创建成功！房间代码：{room_code}")
        except Exception as e:
            print(f"错误：{e}")

    def join_room(self, room_code):
        try:
            address = self.room_manager.join_room(room_code)
            print(f"成功加入房间！地址：{address}")
        except Exception as e:
            print(f"错误：{e}")

    def run(self):
        parser = argparse.ArgumentParser(description="房间管理 CLI")
        subparsers = parser.add_subparsers(dest="command", required=True, help="子命令")

        # 创建房间子命令
        create_parser = subparsers.add_parser("create", help="创建房间")
        create_parser.add_argument("room_name", type=str, help="房间名称")
        create_parser.add_argument("address", type=str, help="Minecraft 服务器地址 (如 localhost:25565)")

        # 加入房间子命令
        join_parser = subparsers.add_parser("join", help="加入房间")
        join_parser.add_argument("room_code", type=str, help="房间代码")

        # 解析命令行参数
        args = parser.parse_args()

        # 根据子命令调用对应方法
        if args.command == "create":
            self.create_room(args.room_name, args.address)
        elif args.command == "join":
            self.join_room(args.room_code)

if __name__ == "__main__":
    cli = RoomManagerCLI()
    cli.run()
