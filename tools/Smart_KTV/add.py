import csv
import easygui as eg
import uuid
import requests
import json

#  UUID  FileName  Name  Singer  Disc

# Details: http://music.163.com/api/song/detail/?id={歌曲ID}&ids=%5B{歌曲ID}%5D

rep = input("1 From DB File\n2 Provided\n3 Input By Hand")
if rep == "1":
    import sqlite3

    # 连接到SQLite数据库
    conn = sqlite3.connect(eg.fileopenbox())

    # 获取游标
    cur = conn.cursor()

    # 执行查询
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    select_list = []
    for i in cur.fetchall():
        select_list.append(i[0])

    print(select_list)
    for i in select_list:
        cur.execute(f'select * from {i}')
        songs = cur.fetchall()
        
    # 关闭连接
    conn.close()
elif rep == "2":
    songs = []
    while True:
        if input("Input Anything To Break.") != "":
            break
        UUID = uuid.uuid4()
        rep = input("Input Music163 ID To Fast Generate")
        if rep != "":
            try:
                rep = int(rep)
                if rep > 0:
                    
                    rep = requests.get(f"http://music.163.com/api/song/detail/?id={rep}&ids=%5B{rep}%5D")
                    if rep.status_code !=200:
                        raise RuntimeError
                    rep = json.loads(rep.content)
                    print(rep)
                    Name = rep["songs"][0]["name"]
                    singer = ""
                    for i in rep["songs"][0]["artists"]:
                        singer = singer + "|" + i["name"]
                    singer = singer[1:]
                    Disc = rep["songs"][0]["album"]["name"]
            except:
                Name = "Unknown"
                singer = "Unknown"
                Disc = "Unknown"
        else:
            Name = "Unknown"
            singer = "Unknown"
            Disc = "Unknown"
        rep = input("Input Music163 ID To Fast Generate")
        if rep != "":
            try:
                rep = int(rep)
            except:
                with open("../static/audios/"+UUID+".lrc","w",encoding="utf-8") as f:
                    f.write("[00:00.000] 无歌词")
        
