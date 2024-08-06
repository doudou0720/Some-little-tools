from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import sqlite3
import time
import random
conn = sqlite3.connect("data.db")
cur = conn.cursor()
dict_list = {
    "云音乐特色榜_热歌榜":"3778678",
    "云音乐国风榜_Top_20":"5059642708",
    "网络热歌榜_Top_100":"6723173524"
    
}
for k,v in dict_list.items():
    sql = f"""CREATE TABLE IF NOT EXISTS {k}(
        排名 integer PRIMARY KEY,
        曲名 text,
        歌手 text,
        时长 text,
        播放链接 text,
        歌曲id integer
    )"""
    cur.execute(sql)
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("--headless")
    edge_options.binary_location = "/opt/microsoft/msedge/microsoft-edge"
    s = Service("msedgedriver")
    print("Starting...")
    driver = webdriver.Edge(service=s,options=edge_options)
    url = f"https://music.163.com/#/discover/toplist?id={v}"
    print("Getting...")
    driver.get(url)
    print("Wait for loading...")
    driver.implicitly_wait(10)
    driver.switch_to.frame("contentFrame")
    # //*[@id="song-list-pre-cache"]/div/div/table //*[@class="m-table m-table-rank"]/tbody/tr
    song_list = driver.find_elements(By.XPATH,'//*[@id="song-list-pre-cache"]/div/div/table/tbody/tr')
    print("Get Song List:\n",song_list)
    for song in song_list:
        herf = song.find_element(By.XPATH,'.//*[@class="txt"]/a').get_attribute("href")
        song_id = herf.split("=")[1]
        name = song.find_element(By.XPATH,'.//*[@class="txt"]/a/b').get_attribute("title")
        print("Now progress is :",name)
        artist = song.find_element(By.XPATH,'./td/div[@class="text"]').get_attribute("title")
        rank = song.find_element(By.XPATH,'.//*[@class="num"]').text
        long = song.find_element(By.XPATH,"./td/span[@class='u-dur ']").text
        cur.execute(f"INSERT INTO {k} (排名,曲名,歌手,时长,播放链接,歌曲id) VALUES (?,?,?,?,?,?)",(rank,name,artist,long,herf,song_id))
    conn.commit()
    t = random.randint(4,16)
    print(f"反反爬虫：休息{str(t)}秒")
    time.sleep(t)
cur.close()
conn.close()
