from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import sqlite3
conn = sqlite3.connect("data.db")
cur = conn.cursor()
v = input("输入歌手与歌手id:\nid:")
k = input("name:")
print(f"请确认无误：{k}:{v}")
input(">>")
sql = f"""CREATE TABLE IF NOT EXISTS 歌手歌曲TOP50_{k}(
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
driver = webdriver.Edge(service=s,options=edge_options)
url = f"https://music.163.com/#/artist?id={v}"
driver.get(url)
driver.switch_to.frame("contentFrame")
song_list = driver.find_elements(By.XPATH,'//*[@class="m-table m-table-1 m-table-4"]/tbody/tr')
for song in song_list:
    herf = song.find_element(By.XPATH,'.//*[@class="txt"]/a').get_attribute("href")
    song_id = herf.split("=")[1]
    name = song.find_element(By.XPATH,'.//*[@class="txt"]/a/b').get_attribute("title")
    artist = song.find_element(By.XPATH,'./td/div[@class="text"]').get_attribute("title")
    rank = song.find_element(By.XPATH,'.//*[@class="num"]').text
    long = song.find_element(By.XPATH,"./td/span[@class='u-dur ']").text
    cur.execute(f"INSERT INTO 歌手歌曲TOP50_{k} (排名,曲名,歌手,时长,播放链接,歌曲id) VALUES (?,?,?,?,?,?)",(rank,name,artist,long,herf,song_id))
conn.commit()
cur.close()
conn.close()