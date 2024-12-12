import random
import string
import time
from flask import Flask, request, jsonify, render_template
from threading import Thread

app = Flask(__name__)
rooms = {}
ROOM_TIMEOUT = 300  # 房间超时时间（秒）

# 生成唯一的联机代码
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create_room", methods=['POST'])
def create_room():
    """创建新房间"""
    room_name = request.json.get('room_name')
    tunnel_id = request.json.get('tunnel_id')
    players = request.json.get('players', 0)
    if not room_name:
        return jsonify({'error': 'Room name is required'}), 400
    
    if not tunnel_id:
        return jsonify({'error': 'Tunnel ID is required'}), 400

    room_code = generate_code()
    rooms[room_code] = {
        'name': room_name,
        'created_at': time.time(),
        'last_heartbeat': time.time(),
        'tunnel_id': tunnel_id,
        'players': players
    }
    return jsonify({'message': 'Room created successfully', 'room_code': room_code})

@app.route('/list_rooms', methods=['GET'])
def list_rooms():
    """列出所有房间"""
    active_rooms = [{'code': code, 'name': room['name'], 'players': room['players']} for code, room in rooms.items()]
    return jsonify({'rooms': active_rooms})

@app.route("/join_room", methods=['POST'])
def join_room():
    """加入房间"""
    room_code = request.json.get('room_code')
    room = rooms.get(room_code)
    if not room:
        return jsonify({'error': '房间未找到'}), 404

    # 这里可以添加其他验证，如检查房间是否已满等
    tunnel_id = room.get('tunnel_id')
    return jsonify({'message': '成功加入房间', 'tunnel_id': tunnel_id})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """更新房间的心跳时间"""
    room_code = request.json.get('room_code')
    players = request.json.get('players')
    if room_code not in rooms:
        return jsonify({'error': 'Room not found'}), 404

    rooms[room_code]['last_heartbeat'] = time.time()
    if players is not None:
        rooms[room_code]['players'] = players
    return jsonify({'message': 'Heartbeat updated successfully'})

def clean_expired_rooms():
    """定期清理过期房间"""
    while True:
        current_time = time.time()
        expired_rooms = [code for code, room in rooms.items() if current_time - room['last_heartbeat'] > ROOM_TIMEOUT]
        for code in expired_rooms:
            del rooms[code]
        time.sleep(10)  # 每 10 秒检查一次

# 启动清理线程
cleaner_thread = Thread(target=clean_expired_rooms, daemon=True)
cleaner_thread.start()

if __name__ == '__main__':
    app.run(debug=True)