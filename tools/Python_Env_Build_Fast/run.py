import datetime
import json
import shutil
import subprocess
import tempfile
import uuid
import psutil
import requests
import os
import time
import zipfile
import keyboard
import threading
import sys
import CLI
from colorama import Fore, Back, Style

Run_Dir = os.getcwd()
pip_config=os.getenv("APPDATA")
def is_file_in_use(file_path):
    try:
        os.rename(file_path, file_path) # 尝试修改文件名
    except OSError:
        return True
    else:
        return False

def kill_process_using_file(file_path):
    for proc in psutil.process_iter():
        try:
            files = proc.open_files()
            for f in files:
                if f.path == file_path:
                    proc.kill() # 杀死占用文件的进程
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def delete_file(file_path):
    try:
        os.remove(file_path) # 删除文件
    except:
        pass

def force_delete_file(file_path):
    if is_file_in_use(file_path):
        kill_process_using_file(file_path)
    delete_file(file_path)
def run_shell(shell):
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

    cmd.communicate()
    return cmd.returncode
def del_files(path):
    for i in os.listdir(path):
        # 不删除当前的py文件
        if '.py' in i:
            continue
        # 如果是文件夹就递归下去
        if os.path.isdir(os.path.join(path,i)):
            del_files(os.path.join(path,i))
        # 删除文件
        force_delete_file(os.path.join(path,i))
def clean_stdin():
    while True:
        os.system("cls")
        t1 = time.time()
        input("回车以继续...")
        t2 = time.time()
        if t2-t1 >= 0.01:
            os.system("cls")
            break
# 进度条模块
def progressbar(url,path,filename,prefix=""):
    if not os.path.exists(path):   # 看是否有该文件夹，没有则创建文件夹
        os.mkdir(path)
    filepath = path+filename  #设置图片name，注：必须加上扩展名
    if os.path.exists(filepath):
        return
    start = time.time() #下载开始时间
    response = requests.get(url, stream=True) #stream=True必须写上
    size = 0    #初始化已下载大小
    chunk_size = 1024  # 每次下载的数据大小
    content_size = int(response.headers['content-length'])  # 下载文件总大小
    try:
        if response.status_code == 200:   #判断是否响应成功
            print(prefix+'Start download,[File size]:{size:.2f} MB'.format(size = content_size / chunk_size /1024))   #开始下载，显示下载文件大小
            with open(filepath,'wb') as file:   #显示进度条
                for data in response.iter_content(chunk_size = chunk_size):
                    file.write(data)
                    size +=len(data)
                    print('\r'+prefix+'[下载进度]:%s%.2f%%' % ('>'*int(size*50/ content_size), float(size / content_size * 100)) ,end=' ')
        end = time.time()   #下载结束时间
        print("\r"+prefix+'Download completed!,times: %.2f秒                                   ' % (end - start))  #输出下载用时时间
    except Exception as e:
        print("\r"+prefix+"Download Failed because:                                   \n"+str(e))
        time.sleep(0)
        exit(0)
def unzip_file(zip_file, extract_dir,prefix=""):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        total_files = len(file_list)
        
        for idx, file in enumerate(file_list):
            zip_ref.extract(file, extract_dir)
            progress = (idx + 1) / total_files * 100
            print(f'\r'+prefix+'解压进度：{:.2f}% : '.format(progress)+file,end= "            ")
def copydirs(from_file, to_file):
    if not os.path.exists(to_file):  # 如不存在目标目录则创建
        os.makedirs(to_file)
    files = os.listdir(from_file)  # 获取文件夹中文件和目录列表
    for f in files:
        if os.path.isdir(from_file + '/' + f):  # 判断是否是文件夹
            copydirs(from_file + '/' + f, to_file + '/' + f)  # 递归调用本函数
        else:
            shutil.copy(from_file + '/' + f, to_file + '/' + f)  # 拷贝文件
def install_programmes(path) -> int:
    """
    安装项目
    path : 索引文件路径

    返回码:
    0:Success
    1:Cancelled
    """
    global Run_Dir
    clean_stdin()

    with open(path,"r",encoding="utf-8") as f:
        data = json.loads(f.read().replace("\n",""))
    Base_dir = os.path.split(path)[0]
    # Step 1 Config
    try:
        name = data["name"]
    except:
        name = None
    if name == "":
        name = None
    if name!= None:
        choice = input("Step 1 Programme Name / 项目名称\n留空以使用: "+name+"\n>> ")
    else:
        choice = input("Step 1 Programme Name / 项目名称\n你必须给它起名\n项目名称: ")
    if choice == "":
        if name == None:
            name = "Unnamed_"+uuid.uuid4()
    print("Will use: "+name)
    time.sleep(1)
    os.system("cls")
    # Step 2 Install
    print("Step 2 安装依赖项")
    print(run_shell(f'{Run_Dir}/py38/python.exe -m pip install -r {os.path.join(Base_dir,"./requirements.txt")}'))
    os.system("cls")
    # Step 3 Copy
    print("Step 3 复制文件")
    os.makedirs(f'{Run_Dir}/Programmes/{name}')
    copydirs(Base_dir,f'{Run_Dir}/Programmes/{name}')
    os.system("cls")
    # Step 4 Run
    print("Step 4 运行安装程序")
    if os.path.exists(os.path.join(f'{Run_Dir}/Programmes/{name}',data["Install_Run"])) and data["Install_Run"].endswith(".py"):
        os.system(f'{Run_Dir}/py38/python.exe {os.path.join(f'{Run_Dir}/Programmes/{name}',data["Install_Run"])}')
        if data["Del_Install_File_After_Install"]:
            os.remove(os.path.join(f'{Run_Dir}/Programmes/{name}',data["Install_Run"]))
    os.system("cls")
    # Step 5 Write
    print("写入配置中...")
    with open("./settings.json","r") as f:
        tmp = json.loads(f.read().replace("\n",""))
    tmp["programmes"].append([name,os.path.abspath(os.path.join(f'{Run_Dir}/Programmes/{name}',data["Entrance"])),data["check_update_URL"]])
    with open("./settings.json","w") as f:
        f.write(json.dumps(tmp))
if not os.path.exists("./py38/installed"):
    print("Python38快速搭建 ver.2")

    time.sleep(1)

    os.system("cls")

    print("Step 0 Basic Settings")
    print("打印系统信息...")

    os.system("systeminfo")

    print("###########")

    cho = input("请在上方寻找‘系统类型’一栏\n若为x64开头,输1\n若为x32开头,输2\n若为其他数值,则无法提供该服务,请退出该程序\n>>>")
    if cho == "1":
        url = "https://mirror.bjtu.edu.cn/python/3.8.10/python-3.8.10-embed-amd64.zip"
    elif cho == "2":
        url = "https://mirror.bjtu.edu.cn/python/3.8.10/python-3.8.10-embed-win32.zip"
    else:
        exit(0)



    os.system("cls")

    print("Step 1 Download & Unzip py38")
    progressbar(url,"./","py38.zip")
    time.sleep(0.5)
    print("Unzipping...")



    def delete_files(directory):
        file_list = os.listdir(directory)
        for file in file_list:
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                delete_files(file_path)
                os.rmdir(file_path)

    directory_path = './py38'
    try:
        delete_files(directory_path)
        os.rmdir(directory_path)
    except:
        pass
    os.mkdir(directory_path)
    unzip_file("./py38.zip",directory_path)

    os.system("cls")

    print("Step 2 Install pip")
    print("|-- 2-1 Config python38._pth",end="...")
    with open("./py38/python38._pth","r",encoding="utf-8") as f:
        li = f.readlines()
    for i in range(len(li)):
        if li[i] == "#import site\n":
            li[i] = "import site\n"
    with open("./py38/python38._pth","w",encoding="utf-8") as f:
        f.writelines(li)

    print("\r|-- 2-1 Config python38._pth Done!")

    print("|-- 2-2 Get get-pip.py")
    progressbar("https://files.cnblogs.com/files/wutou/get-pip.zip","./","get-pip.zip",prefix="|---- ")

    print("|-- 2-3 Unzip get-pip.py")

    unzip_file("get-pip.zip","./py38","|---- ")

    print("\n|-- 2-4 Execute get-pip.py ...")
    try:
        os.mkdir(pip_config+"/pip")
    except:
        pass
    with open(pip_config+"/pip/pip.ini","w") as f:
        f.write("""[global]                
index-url = https://pypi.tuna.tsinghua.edu.cn/simple""")
    os.system(f"{Run_Dir}/py38/python.exe {Run_Dir}/py38/get-pip.py")

    print("|-- 2-4 Execute get-pip.py Done!")

    os.system("cls")

    print("Step 3 Config pip")

    print("|-- 3-1 Select pypi mirror")

    print("|---- Entering CLI...")
    time.sleep(0.5)
    Mirror = (
        ("BFSU 北京外国语大学 开源镜像站","https://mirrors.bfsu.edu.cn/pypi/web/simple"),
        ("DNUI 大连东软信息学院 开源镜像站","http://mirrors.neusoft.edu.cn/pypi/web/simple"),
        ("JLU  吉林大学 开源镜像站","https://mirrors.jlu.edu.cn/pypi/simple"),
        ("NJTech 南京工业大学 开源镜像站","https://mirrors.njtech.edu.cn/pypi/web/simple"),
        ("NJU  南京大学 开源镜像站","https://mirror.nju.edu.cn/pypi/web/simple"),
        ("NYIST 南阳理工学院 开源镜像站","https://mirror.nyist.edu.cn/pypi/simple"),
        ("PKU  北京大学 开源镜像站","https://mirrors.pku.edu.cn/pypi/web/simple"),
        ("SJTUG 上海交通大学 开源镜像站","https://mirror.sjtu.edu.cn/pypi/web/simple"),
        ("SUSTech 南方科技大学 开源镜像站","https://mirrors.sustech.edu.cn/pypi/web/simple"),
        ("TUNA(.NANO/.NEO) [首选]清华大学 开源镜像站","https://pypi.tuna.tsinghua.edu.cn/simple"),
        ("ZJU  浙江大学 开源镜像站","https://mirrors.zju.edu.cn/pypi/web/simple")
    )
    num = 9
    Last = ""
    is_selected = False
    flush_signal = threading.Event()
    def choose(x):
        global num,Last,is_selected,flush_signal
        up = keyboard.KeyboardEvent(event_type='down', scan_code=72, name='up')
        down = keyboard.KeyboardEvent(event_type='down', scan_code=80, name='down')
        enter = keyboard.KeyboardEvent(event_type='down', scan_code=28, name='enter')
        # # get key code and name
        # print("current key code:  {}".format(x.scan_code))
        # print("current key name:  {}".format(x.name))
        Last = ("You pressed {}.".format(x.name))
        if x.event_type == up.event_type and x.scan_code == up.scan_code:
            if num <= 0:
                return
            num -= 1
            flush_signal.set()
        elif x.event_type == down.event_type and x.scan_code == down.scan_code:
            if num >= 10:
                return
            num += 1
            flush_signal.set()
        elif x.event_type == enter.event_type and x.scan_code == enter.scan_code:
            is_selected = True
            flush_signal.set()


    keyboard.hook(choose)

    while True:
        os.system("cls")
        print("按 ↑ ↓ 选择  Enter(回车) 确定")
        print(Last)
        print()
        for i in range(len(Mirror)):
            if i == num:
                print("> "+ Mirror[i][0])
            else:
                print(Mirror[i][0])
        if is_selected:
            break
        flush_signal.wait()
        flush_signal.clear()

    os.system("cls")

    print("Step 3 Config pip")

    print("|-- 3-1 Select pypi mirror")
    print("|---- Use:")
    print("|------ Name:",Mirror[num][0])
    print("|------ URL:",Mirror[num][1])
    print("|---- Enabled global.extra-index-url")
    time.sleep(0.5)
    print("|-- 3-2 Apply(1/2)...")
    os.system(f"{Run_Dir}/py38/python.exe -m pip config set global.index-url "+Mirror[num][1])

    print("|-- 3-2 Apply(2/2)...")
    extra_url = ""
    for i in Mirror:
        extra_url = extra_url + " " + i[1]
    os.system(f'{Run_Dir}/py38/python.exe -m pip config set extra-index-url "'+extra_url+'"')

    os.system("cls")

    print("Step 4 Add sign file")
    with open("./py38/installed","w") as f:
        f.write("There is nothing in it")

    time.sleep(0.5)

    os.system("cls")

    print("Finished!")
    time.sleep(1)
    print("|-- F-1 Clean cache...")
    os.remove("./py38.zip")
    print("|---- Removed ./py38.zip")
    os.remove("./get-pip.zip")
    print("|---- Removed ./get-pip.zip")
    print()
    print("安装完成!稍后本程序将自动退出...")
    time.sleep(3)
else:
    while True:
        choice = CLI.SclectBox("Welcome to Windows (7+) Software Manager\nVersion 2.\n##########","##########\nBuild in 2024.8",(("Python管理",0),("项目管理",1),("版本更新",2))).start()
        if choice[1] == 0:
            while True:
                choice = CLI.SclectBox("当前位置 Python管理","Python38 Path :"+os.path.abspath("./py38"),(("<<返回上一层",0),("pip 安装 Python 包",1),("运行Python终端",2),(Back.RED+Style.BRIGHT+"卸载Python"+Style.RESET_ALL,3))).start()
                if choice[1] == 0:
                    break
                elif choice[1] == 1:
                    choice = CLI.SclectBox("当前位置 Python管理 > pip 安装 Python 包","pip Path :"+os.path.abspath("./py38\\Scripts\\pip.exe"),(("<<返回上一层",0),("直接输入名称安装",1),("从文件安装",2))).start()
                    if choice[1] == 0:
                        continue
                    elif choice[1] == 1:
                        clean_stdin()
                        print("输入库名,若有版本要求,请加双引号")
                        packges = input("python -m pip install ")
                        print(run_shell(f'{Run_Dir}/py38/python.exe -m pip install {packges}'))
                    elif choice[1] == 2:
                        os.system("cls")
                        print("请选择以txt结尾且符合标准的文件\nWill continue in 1s...")
                        time.sleep(1)
                        res = CLI.FileOpenBox(os.getcwd()).start()
                        if res.endswith(".txt"):
                            print(run_shell(f'{Run_Dir}/py38/python.exe -m pip install -r {res}'))
                elif choice[1] == 2:
                    clean_stdin()
                    os.system(f'{Run_Dir}/py38/python.exe')
                elif choice[1] == 3:
                    clean_stdin()
                    time.sleep(0.5)
                    if CLI.ynBox("您将删除Python38所有文件(不含用户目录下的镜像配置文件和项目文件)\n执行时，该程序将会关闭","#########\n你仍可以再次运行本软件以安装Python38"):
                        with open("./tmp.bat","w") as f:
                            f.write(f"@echo off\nping -n 3 127.0.0.1 >nul\nrd /s /Q {os.path.abspath('./py38')}\necho 操作完成，你可以关闭此窗口了\ndel %0")
                        os.system(f"start "+os.path.abspath("./tmp.bat"))
                        exit()
        elif choice[1] == 1:
            def flush_data():
                global data
                if os.path.exists("./settings.json"):
                    try:
                        with open("./settings.json","r") as f:
                            data = json.loads(f.read().replace("\n",""))["programmes"]
                    except:
                        with open("./settings.json","w") as f:
                            f.write('{"programmes":[]}')
                            data = json.loads('{"programmes":[]}')["programmes"]
                else:
                    with open("./settings.json","w") as f:
                        f.write('{"programmes":[]}')
                    data = json.loads('{"programmes":[]}')["programmes"]
                data.insert(0,["<<返回上一层","back",None])
                data.append(["添加新程序","add",None])
            flush_data()
            while True:
                choice = CLI.SclectBox("当前位置 项目管理\n选择程序\n---------","---------",data).start()
                if choice[1] == "back":
                    break
                elif choice[1] == "add":
                    
                    choice = CLI.SclectBox("当前位置 项目管理 > 添加新程序\n选择添加方式\n---------","---------\n说明\n本地:从zip安装\n网络(URL):通过索引文件下载\n网络(Git):需安装Git 克隆储存库",(("<<返回上一层",0),("本地",1),("网络(URL)",2),("网络(Git)",3))).start()
                    if choice[1] == 0:
                        continue
                    elif choice[1] == 1:

                        path = CLI.FileOpenBox(os.getcwd()).start()
                        if path.endswith(".zip"):
                            with tempfile.TemporaryDirectory(prefix="PEBF_",suffix="_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S")) as dir:
                                unzip_file(path,dir)
                                install_programmes(os.path.join(dir,"./index.json"))
                            flush_data()
                    elif choice[1] == 2:
                        pass
                    elif choice[1] == 3:
                        pass
                else:
                    entrance = choice[1]
                    Base_dir = os.path.split(choice[1])[0]
                    choice = CLI.SclectBox("当前位置 项目管理 > "+choice[0],f"项目文件夹:{Base_dir}\n更新链接:{choice[2]}",(("<<返回上一层",0),("运行项目",1),("检查更新\n---------",2),(Back.RED+Style.BRIGHT+"删除项目"+Style.RESET_ALL,3))).start()
                    if choice[1] == 0:
                        continue
                    elif choice[1] == 1:
                        clean_stdin()
                        os.system(f'cmd /c "{Run_Dir}/py38/python.exe" "{os.path.abspath(entrance)}"')
                    elif choice[1] == 2:
                        pass
                    elif choice[1] == 3:
                        clean_stdin()
                        time.sleep(0.5)
                        if CLI.ynBox("您将删除该项目所有文件(不含依赖库)\n执行时，该程序将会关闭",""):
                            print("写入配置中...")
                            with open("./settings.json","r") as f:
                                tmp = json.loads(f.read().replace("\n",""))
                            for i in tmp["programmes"]:
                                if os.path.split(i[1])[0] == Base_dir:
                                    tmp["programmes"].remove(i)
                            with open("./settings.json","w") as f:
                                f.write(json.dumps(tmp))                            
                            shutil.rmtree(Base_dir)
        elif choice[1] == 2:
            pass
