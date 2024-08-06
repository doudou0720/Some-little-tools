# -*- coding: utf-8 -*-
import os
from alive_progress import alive_bar
import shutil


dir="./songs"  #文件夹名称
def CrossOver(dir,fl):
    for i in os.listdir(dir):  #遍历整个文件夹
        path = os.path.join(dir, i)
        if os.path.isfile(path) and path[-1] != "3":  #判断是否为一个文件，排除文件夹
            fl.append(path)
        elif os.path.isdir(path):
            newdir=path
            CrossOver(newdir,fl)
    return fl
filelist = CrossOver(dir,[])
with alive_bar(len(filelist), title = "转换编码") as bar:
    for i in filelist:
        try:
            with open(i,"rb") as f:
                temp = f.read()
            with open("text.lrc","wb") as f:
                #解码，需要指定原来是什么编码
                temp_unicode =temp.decode('utf-8','ignore')
                #拿unicode进行编码
                temp_gbk = temp_unicode.encode('gb18030','ignore')
                f.write(temp_gbk)
        except:
            pass
        shutil.copy2("./text.lrc",i)
        bar()
