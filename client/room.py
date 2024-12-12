import re
import subprocess
import threading
import time
import requests
from mcstatus import JavaServer

class RoomManager:
    """负责房间管理的逻辑类"""
    SERVER_URL_BASE = 'https://ml.hhhhhi.com/'
    SERVER_URL_CREATE = SERVER_URL_BASE + '/create_room'
    SERVER_URL_JOIN = SERVER_URL_BASE + '/join_room'
    SERVER_URL_HEARTBEAT = SERVER_URL_BASE + '/heartbeat'

    def __init__(self):
        pass

    def create_room(self, room_name, address):
        if not room_name:
            raise ValueError("房间名称是必填的")

        players = self.get_players(address)

        if ':' in address:
            port = address.split(':')[1]
        else:
            port = '25565'

        tunnel_id = self.create_tunnel(port)
        if not tunnel_id:
            raise RuntimeError("隧道创建失败")

        payload = {
            'room_name': room_name,
            'players': players,
            'tunnel_id': tunnel_id,
        }

        response = requests.post(self.SERVER_URL_CREATE, json=payload)
        if response.status_code == 200:
            data = response.json()
            threading.Thread(target=self.heartbeat, args=(address, data['room_code'])).start()
            return data['room_code']
        else:
            raise RuntimeError(response.json().get('error', '发生了未知错误'))

    def join_room(self, room_code):
        if not room_code:
            raise ValueError("房间代码是必填的")

        payload = {'room_code': room_code}
        response = requests.post(self.SERVER_URL_JOIN, json=payload)
        if response.status_code == 200:
            data = response.json()
            tunnel_id = data.get('tunnel_id')
            return self.join_tunnel(tunnel_id)
        else:
            raise RuntimeError(response.json().get('error', '发生了未知错误'))

    def get_players(self, address):
        server = JavaServer.lookup(address)
        status = server.status()
        return status.players.online

    def create_tunnel(self, port):
        command = ['p2ptunnel', '-type', 'tcp', '-l', port]
        try:
            process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
            for line in process.stderr:
                match = re.search(r'Your id: ([\w]+)', line)
                if match:
                    return match.group(1)
        except Exception as e:
            raise RuntimeError(f"创建隧道时发生错误：{str(e)}")

    def join_tunnel(self, tunnel_id):
        command = ['p2ptunnel', '-id', tunnel_id]
        try:
            process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
            for line in process.stderr:
                match = re.search(r'Listening tcp (\d+\.\d+\.\d+\.\d+:\d+)', line)
                if match:
                    return match.group(1)
        except Exception as e:
            raise RuntimeError(f"加入隧道时发生错误：{str(e)}")

    def heartbeat(self, address, room_code):
        while True:
            try:
                players = self.get_players(address)
                payload = {'room_code': room_code, 'players': players}
                response = requests.post(self.SERVER_URL_HEARTBEAT, json=payload)
                if response.status_code != 200:
                    raise RuntimeError(response.json().get('error', '发生了未知错误'))
            except Exception as e:
                print(f"心跳错误：{e}")
                break
            time.sleep(10)