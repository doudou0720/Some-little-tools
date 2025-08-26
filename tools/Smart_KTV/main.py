import csv
import flask
import json
from flask import request
# 添加UUID支持
import uuid
import os
from datetime import datetime
import time

app = flask.Flask(__name__, template_folder="./templates", static_folder="./static")
app.secret_key = 'your-secret-key-here'

# 播放列表文件路径
PLAYLIST_FILE = 'playlists.json'

# 添加播放列表存储
# 格式: {session_id: {"songs": [song_uuid, ...], "created_at": timestamp, "updated_at": timestamp}}
playlists = {}

# 加载播放列表数据
def load_playlists():
    global playlists
    if os.path.exists(PLAYLIST_FILE):
        try:
            with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 转换旧格式数据（如果存在）
                for session_id, playlist_data in data.items():
                    if isinstance(playlist_data, list):
                        # 旧格式：直接存储歌曲列表
                        playlists[session_id] = {
                            "songs": playlist_data,
                            "created_at": time.time(),
                            "updated_at": time.time()
                        }
                    else:
                        # 新格式：包含元数据
                        playlists[session_id] = playlist_data
        except Exception as e:
            print(f"加载播放列表文件时出错: {e}")
            playlists = {}
    else:
        playlists = {}

# 保存播放列表数据
def save_playlists():
    try:
        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(playlists, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存播放列表文件时出错: {e}")

# 在应用启动时加载播放列表
load_playlists()

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
    # 使用更复杂的数据结构来存储不同类型的连接
    connections = {}  # {session_id: {'player': ws, 'remote': ws}}
    connections_lock = Lock()

    @sock.route('/websocket/<session_id>')
    def websocket(ws, session_id):
        # 主播放页面的WebSocket连接，使用传入的session_id
        with connections_lock:
            if session_id not in connections:
                connections[session_id] = {'player': None, 'remote': None}
            connections[session_id]['player'] = ws
        
        try:
            # 发送session_id给客户端
            ws.send(json.dumps({"type": "session_id", "session_id": session_id}))
            while True:
                data = ws.receive()
                # 可以处理来自播放页面的消息，并转发给遥控器
                try:
                    message_data = json.loads(data)
                    # 如果收到获取状态请求，发送当前状态
                    if message_data.get("type") == "get_status":
                        # 发送初始状态
                        ws.send(json.dumps({"type": "playback_status", "status": "paused"}))
                    elif message_data.get("type") == "get_volume":
                        # 发送初始音量
                        ws.send(json.dumps({"type": "volume_update", "audio1": 1.0, "audio2": 1.0}))
                    
                    # 将消息转发给遥控器
                    with connections_lock:
                        if session_id in connections and connections[session_id]['remote']:
                            try:
                                connections[session_id]['remote'].send(data)
                            except Exception as e:
                                print(f"转发消息到遥控器时出错: {e}")
                                connections[session_id]['remote'] = None
                except Exception as e:
                    print(f"处理WebSocket消息时出错: {e}")
        except Exception as e:
            print(f"WebSocket连接错误: {e}")
        finally:
            with connections_lock:
                if session_id in connections:
                    connections[session_id]['player'] = None

    # 添加一个新的路由来处理遥控器WebSocket连接
    @sock.route('/websocket_remote/<session_id>')
    def websocket_remote(remote_ws, session_id):
        # 遥控器页面的WebSocket连接
        with connections_lock:
            if session_id not in connections:
                connections[session_id] = {'player': None, 'remote': None}
            connections[session_id]['remote'] = remote_ws
            
        try:
            # 发送连接确认消息
            remote_ws.send(json.dumps({"type": "connected", "message": "Remote connected"}))
            
            while True:
                data = remote_ws.receive()
                # 将遥控器命令转发给播放页面
                command_data = json.loads(data)
                
                # 确保session_id在消息中
                command_data["session_id"] = session_id
                
                # 处理通过UUID切换歌曲的命令
                if command_data.get("command") == "change_song_by_uuid":
                    song_uuid = command_data.get("song_uuid")
                    if song_uuid:
                        # 从data.csv查找歌曲信息
                        song_data = None
                        with open('data.csv', 'r', encoding='utf-8') as file:
                            csv_reader = csv.DictReader(file)
                            for row in csv_reader:
                                if row['UUID'] == song_uuid:
                                    song_data = row
                                    break
                        
                        if song_data:
                            # 修改命令为change_song并发送歌曲名称
                            command_data["command"] = "change_song"
                            command_data["song_name"] = song_data['Song']
                
                with connections_lock:
                    if session_id in connections and connections[session_id]['player']:
                        try:
                            connections[session_id]['player'].send(json.dumps(command_data))
                        except Exception as e:
                            print(f"发送消息到播放页面时出错: {e}")
                            connections[session_id]['player'] = None
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
            with connections_lock:
                if session_id in connections:
                    connections[session_id]['remote'] = None

@app.route("/play")
def play():
    # 修改为通过UUID查找
    song_uuid = flask.request.args.get("uuid")
    # 获取可能存在的session_id参数
    session_id = flask.request.args.get("session_id")
    
    # 如果没有提供歌曲UUID，重定向到歌曲列表
    if not song_uuid:
        return flask.redirect(flask.url_for('song_list'))
    
    # 从data.csv读取歌曲信息
    song_data = None
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # 使用UUID进行匹配
            if row['UUID'] == song_uuid:
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
    
    # 如果没有session_id，则生成新的session_id
    if not session_id:
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
    显示歌曲列表或节目单
    """
    # 检查是否有主节目单
    main_playlist = load_main_playlist()
    
    if main_playlist:
        # 如果有节目单，显示节目单页面
        # 获取节目单中歌曲的详细信息
        songs_details = []
        with open('data.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            song_dict = {row['UUID']: row for row in csv_reader}
            
        for song_uuid in main_playlist:
            if song_uuid in song_dict:
                song_info = song_dict[song_uuid]
                songs_details.append({
                    'uuid': song_info['UUID'],
                    'name': song_info['Song'],
                    'artist': song_info['Artist'],
                    'disc': song_info['Disc'],
                    'img': song_info['Img']
                })
        
        return flask.render_template("playlist.html", playlist=songs_details)
    else:
        # 如果没有节目单，显示歌曲列表
        songs = []
        with open('data.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                songs.append(row)
        
        return flask.render_template("index.html", songs=songs)

@app.route("/playlist")
def view_playlist():
    """
    查看节目单
    """
    # 获取主节目单
    main_playlist = load_main_playlist()
    
    # 获取节目单中歌曲的详细信息
    songs_details = []
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        song_dict = {row['UUID']: row for row in csv_reader}
        
    for song_uuid in main_playlist:
        if song_uuid in song_dict:
            song_info = song_dict[song_uuid]
            songs_details.append({
                'uuid': song_info['UUID'],
                'name': song_info['Song'],
                'artist': song_info['Artist'],
                'disc': song_info['Disc'],
                'img': song_info['Img']
            })
    
    return flask.render_template("playlist.html", playlist=songs_details)

@app.route("/create_playlist")
def create_playlist():
    """
    创建节目单页面
    """
    # 获取所有歌曲
    songs = []
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            songs.append(row)
    
    # 获取当前主节目单
    main_playlist = load_main_playlist()
    
    # 获取节目单中歌曲的详细信息
    playlist_details = []
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        song_dict = {row['UUID']: row for row in csv_reader}
        
    for song_uuid in main_playlist:
        if song_uuid in song_dict:
            song_info = song_dict[song_uuid]
            playlist_details.append({
                'uuid': song_info['UUID'],
                'name': song_info['Song'],
                'artist': song_info['Artist'],
                'disc': song_info['Disc'],
                'img': song_info['Img']
            })
    
    return flask.render_template("create_list.html", songs=songs, playlist=playlist_details)

@app.route("/api/playlist/main", methods=["POST"])
def update_main_playlist():
    """
    更新主节目单
    """
    try:
        data = flask.request.get_json()
        songs = data.get("songs", [])
        
        # 保存主节目单
        save_main_playlist(songs)
        
        return flask.jsonify({
            "status": "success",
            "message": "主节目单已更新"
        })
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

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

@app.route("/api/song/<song_uuid>")
def get_song_by_name(song_uuid):
    """
    根据歌曲UUID获取歌曲信息
    """
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['UUID'] == song_uuid:
                return flask.jsonify({
                    'uuid': row['UUID'],
                    'name': row['Song'],
                    'artist': row['Artist'],
                    'disc': row['Disc'],
                    'img': row['Img'],
                    'ins': row['Ins'],
                    'vol': row['Vol'],
                    'lrc': row['Lrc']
                })
    return flask.jsonify({"error": "Song not found"}), 404

@app.route("/api/playlist", methods=["POST"])
def add_to_playlist():
    """
    添加歌曲到播放列表
    """
    try:
        data = flask.request.get_json()
        session_id = data.get("session_id")
        song_uuid = data.get("song_uuid")
        
        if not session_id or not song_uuid:
            return flask.jsonify({"error": "Missing session_id or song_uuid"}), 400
            
        # 初始化播放列表
        if session_id not in playlists:
            playlists[session_id] = {
                "songs": [],
                "created_at": time.time(),
                "updated_at": time.time()
            }
            
        # 添加歌曲到播放列表（如果尚未存在）
        if song_uuid not in playlists[session_id]["songs"]:
            playlists[session_id]["songs"].append(song_uuid)
            playlists[session_id]["updated_at"] = time.time()
            # 保存播放列表到文件
            save_playlists()
            
        return flask.jsonify({
            "status": "success", 
            "playlist": playlists[session_id]["songs"],
            "count": len(playlists[session_id]["songs"])
        })
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/api/playlist/<session_id>", methods=["GET"])
def get_playlist(session_id):
    """
    获取指定session的播放列表
    """
    try:
        playlist = playlists.get(session_id, [])
        
        # 获取播放列表中歌曲的详细信息
        songs_details = []
        with open('data.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            song_dict = {row['UUID']: row for row in csv_reader}
            
        for song_uuid in playlist:
            if song_uuid in song_dict:
                song_info = song_dict[song_uuid]
                songs_details.append({
                    'uuid': song_info['UUID'],
                    'name': song_info['Song'],
                    'artist': song_info['Artist'],
                    'disc': song_info['Disc'],
                    'img': song_info['Img']
                })
        
        return flask.jsonify({
            "status": "success",
            "songs": songs_details,
            "count": len(songs_details)
        })
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/api/playlist/<session_id>", methods=["DELETE"])
def clear_playlist(session_id):
    """
    清空指定session的播放列表
    """
    try:
        if session_id in playlists:
            del playlists[session_id]
            # 保存播放列表到文件
            save_playlists()
            
        return flask.jsonify({"status": "success", "message": "Playlist cleared"})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/api/playlist/<session_id>/<song_uuid>", methods=["DELETE"])
def remove_from_playlist(session_id, song_uuid):
    """
    从播放列表中移除指定歌曲
    """
    try:
        if session_id in playlists and song_uuid in playlists[session_id]["songs"]:
            playlists[session_id]["songs"].remove(song_uuid)
            playlists[session_id]["updated_at"] = time.time()
            
            # 如果播放列表为空，删除它
            if not playlists[session_id]["songs"]:
                del playlists[session_id]
            
            # 保存播放列表到文件
            save_playlists()
                
        return flask.jsonify({"status": "success", "message": "Song removed from playlist"})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

# 添加获取所有播放列表历史记录的API
@app.route("/api/playlists/history", methods=["GET"])
def get_playlists_history():
    """
    获取所有播放列表历史记录，按时间顺序排列
    """
    try:
        history = []
        # 从播放列表数据中提取历史记录
        for session_id, playlist_data in playlists.items():
            songs = playlist_data.get("songs", [])
            if songs:  # 只包含非空的播放列表
                # 获取播放列表中歌曲的详细信息
                songs_details = []
                with open('data.csv', 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    song_dict = {row['UUID']: row for row in csv_reader}
                    
                for song_uuid in songs:
                    if song_uuid in song_dict:
                        song_info = song_dict[song_uuid]
                        songs_details.append({
                            'uuid': song_info['UUID'],
                            'name': song_info['Song'],
                            'artist': song_info['Artist'],
                            'disc': song_info['Disc'],
                            'img': song_info['Img']
                        })
                
                if songs_details:  # 只添加有歌曲的播放列表
                    history.append({
                        'session_id': session_id,
                        'songs': songs_details,
                        'song_count': len(songs_details),
                        'created_at': playlist_data.get("created_at", 0),
                        'updated_at': playlist_data.get("updated_at", 0)
                    })
        
        # 按更新时间排序（最新的在前）
        history.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return flask.jsonify({
            "status": "success",
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

# 主节目单文件路径
MAIN_PLAYLIST_FILE = 'main_playlist.json'

# 加载主节目单
def load_main_playlist():
    if os.path.exists(MAIN_PLAYLIST_FILE):
        try:
            with open(MAIN_PLAYLIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载主节目单文件时出错: {e}")
    return []

# 保存主节目单
def save_main_playlist(playlist):
    try:
        with open(MAIN_PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(playlist, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存主节目单文件时出错: {e}")

app.run(debug=True,port=8000,host="0.0.0.0")