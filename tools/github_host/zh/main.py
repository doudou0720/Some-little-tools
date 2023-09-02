# !/usr/bin/python3
# coding: utf-8
import os
import subprocess
import requests
import time

 
with open("./hosts.txt","w") as f:
    f.write("-------------\n请将下面的数据复制,关闭并粘贴到下一个打开的记事本中(替代上一次复制的)\n-------------\n\n")
    f.write(requests.get("https://gitee.com/frankwuzp/github-host/raw/main/hosts").text)
os.system("notepad {path}".format(path=os.getcwd()+"/hosts.txt"))
subprocess.call('cmd /c shell.vbs')
input("复制完成了吗?请在复制完成后回到本页面按下回车(hosts文件记得Ctrl+S保存再回车)")
os.system("ipconfig /flushdns")
print("修改完成!一秒后自动退出。")
time.sleep(1)
