import csv
import flask
import json
from flask import request
# 添加UUID支持
import uuid

app = flask.Flask(__name__, template_folder="./templates", static_folder="./static")
app.secret_key = 'your-secret-key-here'

# 添加WebSocket支持
try:
    from flask_sock import Sock
    sock = Sock(app)
    websocket_support = True
except ImportError:
    websocket_support = False
    print("flask_sock not installed. WebSocket功能将不可用。")

# 存储WebSocket连接
if websocket_support:
    from threading import Lock
    connections = {}  # 改为字典，以UUID为键
    connections_lock = Lock()

    @sock.route('/websocket/<session_id>')
    def websocket(ws, session_id):
        # 主播放页面的WebSocket连接，使用传入的session_id
        with connections_lock:
            connections[session_id] = ws
        
        try:
            # 发送session_id给客户端
            ws.send(json.dumps({"type": "session_id", "session_id": session_id}))
            while True:
                data = ws.receive()
                # 可以处理来自播放页面的消息
                try:
                    message_data = json.loads(data)
                    # 如果收到获取状态请求，发送当前状态
                    if message_data.get("type") == "get_status":
                        # 发送初始状态
                        ws.send(json.dumps({"type": "playback_status", "status": "paused"}))
                    elif message_data.get("type") == "get_volume":
                        # 发送初始音量
                        ws.send(json.dumps({"type": "volume_update", "audio1": 1.0, "audio2": 1.0}))
                except Exception as e:
                    print(f"处理WebSocket消息时出错: {e}")
        except Exception as e:
            print(f"WebSocket连接错误: {e}")
        finally:
            with connections_lock:
                if session_id in connections:
                    del connections[session_id]
    # 添加一个新的路由来处理遥控器WebSocket连接
    @sock.route('/websocket_remote/<session_id>')
    def websocket_remote(remote_ws, session_id):
        # 遥控器页面的WebSocket连接
        try:
            while True:
                data = remote_ws.receive()
                # 将遥控器命令转发给播放页面
                command_data = json.loads(data)
                
                # 确保session_id在消息中
                command_data["session_id"] = session_id
                
                with connections_lock:
                    if session_id in connections:
                        try:
                            connections[session_id].send(json.dumps(command_data))
                        except Exception as e:
                            print(f"发送消息到客户端时出错: {e}")
                            # 从连接字典中移除失效连接
                            del connections[session_id]
                    else:
                        print(f"未找到session_id {session_id} 的播放页面连接")
                        # 通知遥控器连接失败
                        try:
                            remote_ws.send(json.dumps({
                                "type": "error",
                                "message": "未找到对应的播放页面连接"
                            }))
                        except:
                            pass
        except Exception as e:
            print(f"遥控器WebSocket连接错误: {e}")
        finally:
            print(f"遥控器 {session_id} 连接已断开")

@app.route("/play")
def play():
    # 修改为通过歌曲名称查找
    song_name = flask.request.args.get("name")
    
    # 如果没有提供歌曲名称，重定向到歌曲列表
    if not song_name:
        return flask.redirect(flask.url_for('song_list'))
    
    # 从data.csv读取歌曲信息
    song_data = None
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # 使用歌曲名称进行匹配
            if row['Song'] == song_name:
                song_data = row
                break
    
    if song_data:
        name = song_data['Song']
        disc = song_data['Disc']
        song_name = song_data['Song']
        singer = song_data['Artist']
        img = song_data['Img']
    else:
        # 如果找不到歌曲，重定向到歌曲列表
        return flask.redirect(flask.url_for('song_list'))
    
    # 生成session_id并传递给模板
    session_id = str(uuid.uuid4())
    remote_url = f"/remote?session_id={session_id}"
    
    return flask.render_template("main.html", name=name, disc=disc, song_name=song_name, singer=singer, img=img, name_ins=song_data["Ins"], name_lrc=song_data["Lrc"], name_vol=song_data["Vol"], remote_url=remote_url, session_id=session_id)

@app.route("/get_song/<id>")
def get_song(id):
    with open('data.csv', 'r') as read_obj:
    
        # Return a reader object which will
        # iterate over lines in the given csvfile
        csv_reader = csv.reader(read_obj)
    
        # convert string to list
        list_of_csv = list(csv_reader)
    
        print(list_of_csv)

@app.route("/api/volume", methods=["POST"])
def set_volume():
    """
    设置音频音量的API
    请求格式: {"audio1": 0.5, "audio2": 0.8}
    """
    try:
        data = flask.request.get_json()
        if not data:
            return flask.jsonify({"error": "No data provided"}), 400
            
        response = {"status": "success"}
        
        if "audio1" in data:
            # 在实际应用中，这里会与前端通信设置audio1的音量
            response["audio1"] = data["audio1"]
            
        if "audio2" in data:
            # 在实际应用中，这里会与前端通信设置audio2的音量
            response["audio2"] = data["audio2"]
            
        return flask.jsonify(response)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/api/volume/<audio_id>", methods=["POST"])
def set_single_volume(audio_id):
    """
    设置单个音频音量的API
    """
    try:
        data = flask.request.get_json()
        volume = data.get("volume")
        
        if volume is None:
            return flask.jsonify({"error": "Volume not provided"}), 400
            
        if audio_id not in ["audio1", "audio2"]:
            return flask.jsonify({"error": "Invalid audio ID"}), 400
            
        # 在实际应用中，这里会与前端通信设置指定音频的音量
        return flask.jsonify({"status": "success", "audio": audio_id, "volume": volume})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/remote")
def remote_control():
    """
    遥控器界面 (不再需要歌曲名称参数)
    """
    return flask.render_template("remote.html")

@app.route("/")
def song_list():
    """
    显示歌曲列表
    """
    songs = []
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            songs.append(row)
    
    return flask.render_template("index.html", songs=songs)

@app.route("/api/songs")
def get_songs():
    """
    获取所有歌曲列表的API
    """
    songs = []
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            songs.append({
                'name': row['Song'],
                'artist': row['Artist'],
                'disc': row['Disc'],
                'img': row['Img']
            })
    return flask.jsonify(songs)

@app.route("/api/song/<song_name>")
def get_song_by_name(song_name):
    """
    根据歌曲名称获取歌曲信息
    """
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['Song'] == song_name:
                return flask.jsonify({
                    'name': row['Song'],
                    'artist': row['Artist'],
                    'disc': row['Disc'],
                    'img': row['Img'],
                    'ins': row['Ins'],
                    'vol': row['Vol'],
                    'lrc': row['Lrc']
                })
    return flask.jsonify({"error": "Song not found"}), 404



app.run(debug=True,port=8000,host="0.0.0.0")
