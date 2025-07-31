import csv
import flask
import json

app = flask.Flask(__name__, template_folder="./templates", static_folder="./static")

@app.route("/play")
def play():
    song_id = flask.request.args.get("id")
    
    # 如果没有提供歌曲ID，重定向到歌曲列表
    if not song_id:
        return flask.redirect(flask.url_for('song_list'))
    
    # 从data.csv读取歌曲信息
    song_data = None
    with open('data.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # 假设第一列"Song"作为歌曲ID进行匹配
            if row['Song'] == song_id:
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
        return flask.redirect(flask.url_for('/'))
    
    return flask.render_template("main.html", name=name, disc=disc, song_name=song_name, singer=singer, img=img, name_ins=song_data["Ins"], name_vol=song_data["Vol"], name_lrc=song_data["Lrc"])

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

app.run(debug=True,port=8000,host="0.0.0.0")