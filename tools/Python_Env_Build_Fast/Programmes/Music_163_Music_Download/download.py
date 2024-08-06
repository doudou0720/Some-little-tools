import logging
log = logging.getLogger("Downloader")
logging.basicConfig(filename='runtime.log',format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',level=logging.INFO,filemode="w")
import random
import re
import shutil
import time
import sqlite3
from alive_progress import alive_bar
import requests
import json
import os
from bs4 import BeautifulSoup
import eyed3
import imghdr
from eyed3.id3.frames import ImageFrame
import atexit
from eyed3 import mp3

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
}
cnt = 0
@atexit.register 
def exitf():
    log.info("Exiting...")
    try :
        global select_list , ii , i
        " ".join(select_list)
    except:
        select_list = "None"
    with open("Last.txt","w",encoding="utf-8") as f:
        f.write(f'{select_list}\n')
        try:
            f.write(f"{ii[0]}\n{i}")
        except :
            pass
select_list = None

log.info("正在对音乐进行扫描")

music_dir=r"./song" #此处改为你要扫描的音乐歌单文件夹
musicList=[]
def mp3_bit(mp3Path):
    mp3Info = mp3.Mp3AudioFile(mp3Path)
    print("音频采样率：",mp3Info.info.bit_rate[1])
    return(mp3Info.info.bit_rate[1])

def musicUrlLoader():
    fileList = os.listdir(music_dir)  # 加载当前目录的mp3音乐
    for music_dir1 in fileList:
        fileList2 = os.listdir(music_dir+"/"+music_dir1)
        for filename in fileList2:
            if filename.endswith(".mp3"):
                print("找到音频文件", filename)
                musicList.append(music_dir+"/"+music_dir1+"/"+filename)
musicUrlLoader()
with alive_bar(len(musicList), dual_line=True,title = "检查文件完整性") as bar:
    for i in range(len(musicList)):
        # print(musicList)
        try:
            # print(musicList[i])
            mp3_bit(musicList[i])
        except Exception as e:
            print(e)
            os.remove(musicList[i])#删掉损坏的歌曲
            bar.text = f"{musicList[i]} 已删除"
        bar()
del musicList

try:
    def can_save(s):
        if len(s) >= 40:
            s = s[0:40]
            s += "..."
            print("文件名超过40字符，自动截断，你仍可在某些播放器上看到全名！")
        return re.sub('[\\/?*<>|":]','',s)

    def renewdir(url):
        if os.path.exists(url) == False:
            os.mkdir(url)
        pass
    def get_other(id):
        url = f"https://music.163.com/song?id={id}"
        r = requests.get(url,headers=headers)
        #利用.text方法提取响应的文本信息
        html = r.text
        #利用BS库对网页进行解析，得到解析对象soup
        soup =BeautifulSoup(html,'html.parser')
        res_img = soup.find("img",attrs={'class':'j-img'})
        res_album = soup.find_all("a",attrs={'class':'s-fc7'})[2].get_text()
        return (res_img["src"],res_album)

    def saveMp3(mp3_path , artist , title , id):
        audioFile = eyed3.load(path=mp3_path)
        # audioFile.tag.artist = u"五条人"
        # audioFile.tag.title = u"世界的理想"
        # audioFile.tag.album = u"乐队的夏天"
        audioFile.tag.artist = artist
        audioFile.tag.title = title
        temp = get_other(id)
        audioFile.tag.album = temp[1]
        download_img(temp[0])
        img_type = imghdr.what('./Temp.jpg')
        audioFile.tag.images.set(ImageFrame.FRONT_COVER, open('./Temp.jpg', 'rb').read(), 'image/' + img_type)
        # audioFile.tag.save()
        audioFile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
    def download_img(url):
        # 下载图片
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            open('./Temp.jpg', 'wb').write(r.content) # 将内容写入图片
        del r
    try:

        raise RuntimeError
    except:
        is_tty = True
        print("Entering to tty mode...")
        conn = sqlite3.connect("./data.db")
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        if select_list == None:
            select_list = []
            for i in cur.fetchall():
                select_list.append(i[0])
        print("注意：数据库名称参照下表，序号为从左到右")
        print(select_list)

    log.debug(f"Start with select_list={select_list}")
    for i in select_list:
        log.info(f"Now database {i}")
        renewdir(f"./song/{i}")
        cur.execute(f'select * from {i}')
        songs = cur.fetchall()
        cnt += 1
        if is_tty == False:
            title = f"数据库：{i}  下载"
        else:
            title = cnt
        with alive_bar(len(songs), dual_line=True,title = title) as bar:
            icnt = 0
            for ii in songs:
                icnt += 1
                log.info(f"Start to download : {ii}")
                if ii[0] < 0:
                    bar()
                    continue
                if os.path.exists(f'./song/{i}/'+ f"{can_save(ii[1])}" + '.mp3') and os.path.exists(f'./song/{i}/'+ f"{can_save(ii[1])}" + '.lrc'):
                    bar.text("文件已存在!")
                    bar()
                    log.info(f"{ii[1]} MP3已存在!")
                    continue
                song_url = "https://music.163.com/song/media/outer/url?id="+str(ii[-1])+".mp3"
                lrc_url = "http://music.163.com/api/song/lyric?id="+str(ii[-1])+"&lv=1&kv=1&tv=-1"
                bar.text = f"{ii[1]} MP3获取中...(歌曲时间:{ii[-3]})"
                log.info(f"{ii[1]} MP3获取中...(歌曲时间:{ii[-3]})")
                song_response = requests.get(song_url, headers=headers ,timeout=(5,15))
                try:
                    if "<!DOCTYPE html>" in song_response.text:
                        t = random.randint(3,8)
                        if is_tty:
                            bar.text = f"{(icnt/len(songs))*100}% Pass 反反爬虫：休息{str(t)}秒"
                        else:
                            bar.text = f"VIP歌曲自动跳过\n反反爬虫：休息{str(t)}秒"
                        log.info(f"VIP歌曲自动跳过\n反反爬虫：休息{str(t)}秒")
                        time.sleep(t)
                        bar()
                        continue
                except:
                    pass
                with open(f'./song/{i}/'+ f"{can_save(ii[1])}" + '.mp3', 'wb') as file_mp3:
                    file_mp3.write(song_response.content)
                bar.text = f"{ii[1]} MP3获取完成..."
                log.info(f"{ii[1]} MP3获取完成...")
                lrc_response = requests.get(lrc_url, headers=headers)
                lrc_json = json.loads(lrc_response.text)
                with open(f'./song/{i}/'+ f"{can_save(ii[1])}" + '.lrc', 'a',encoding="utf-8") as file_lrc:
                    if lrc_json['lrc']['lyric'] != "" or lrc_json['lrc']['lyric'] != None:
                        file_lrc.write(lrc_json['lrc']['lyric'])
                    else:
                        file_lrc.write("[00:00.000] 无歌词/纯音乐，请欣赏\n")
                bar.text = f"{ii[1]} MP3获取完成 已获取lrc..."
                log.info(f"{ii[1]} 已获取lrc...")
                saveMp3(f'./song/{i}/'+ f"{can_save(ii[1])}" + '.mp3' , ii[2] , ii[1] , ii[-1])
                bar.text = f"{ii[1]} MP3获取完成 已获取lrc 歌曲信息获取完毕 已获取完毕"
                log.info(f"{ii[1]} 歌曲信息获取完毕 已获取完毕")
                t = random.randint(3,10)
                if is_tty:
                    bar.text = f"{(icnt/len(songs))*100}% OK 反反爬虫：休息{str(t)}秒"
                else:
                    bar.text = f"{ii[1]} MP3获取完成 已获取lrc 歌曲信息获取完毕 已获取完毕\n  反反爬虫：休息{str(t)}秒"
                time.sleep(t)
                bar()
            
    cur.close()
    conn.close()
except Exception as e:
    log.critical(f"Error happened !See the log below:\n{e}")
    if is_tty:
        print(f"Error happened !See the log below:\n{e}")
        exit(-1)
    exit(-1)
