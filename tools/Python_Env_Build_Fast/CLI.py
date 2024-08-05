import os
import threading
import keyboard
from colorama import Fore, Back, Style

class SclectBox():

    def hook(self,x):
        up = keyboard.KeyboardEvent(event_type='down', scan_code=72, name='up')
        down = keyboard.KeyboardEvent(event_type='down', scan_code=80, name='down')
        enter = keyboard.KeyboardEvent(event_type='down', scan_code=28, name='enter')
        space = keyboard.KeyboardEvent(event_type='down', scan_code=57, name='space')
        # # get key code and name
        # print("current key code:  {}".format(x.scan_code))
        # print("current key name:  {}".format(x.name))
        self.Last = ("You pressed {}.".format(x.name))
        if x.event_type == up.event_type and x.scan_code == up.scan_code:
            if self.sclected <= 0:
                return
            self.sclected -= 1
            self.flush_signal.set()
        elif x.event_type == down.event_type and x.scan_code == down.scan_code:
            if self.sclected >= self.length-1:
                return
            self.sclected += 1
            self.flush_signal.set()
        elif x.event_type == enter.event_type and x.scan_code == enter.scan_code:
            self.is_selected = True
            self.flush_signal.set()
        elif x.event_type == space.event_type and x.scan_code == space.scan_code and self.is_multi:
            if self.sclected in self.sclected_list:
                self.sclected_list.remove(self.sclected)
            else:
                self.sclected_list.append(self.sclected)
            self.flush_signal.set()


    def __init__(self,header:str,footer:str,choices:list | tuple,multi:bool = False,default_number = 0) -> None:
        self.header = header
        self.footer = footer
        self.choices = choices
        self.is_multi = multi
        self.sclected_list = []
        self.sclected = default_number
        self.flush_signal = threading.Event()
        self.is_selected = False
        self.Last = ""
        self.length = len(self.choices)

        keyboard.hook(self.hook)

    
    def loop(self) -> None:
        print(self.header)
        if self.is_multi:
            print("* 按 ↑ ↓ 选择  Space(空格)选中  Enter(回车) 确定")
        else:
            print("* 按 ↑ ↓ 选择  Enter(回车) 确定")
        print(self.Last)
        print()
        for i in range(len(self.choices)):
            this_word = self.choices[i][0]
            if i in self.sclected_list:
                this_word = Fore.WHITE + Back.WHITE + self.choices[i][0] + Style.RESET_ALL
            if i == self.sclected:
                this_word = "> " + this_word
            else:
                this_word = "  " + this_word
            print(this_word)
        print()
        print(self.footer)   
    
    def start(self) -> list | str:
        while True:
            os.system("cls")
            if self.is_selected:
                break
            self.loop()
            self.flush_signal.wait()
            self.flush_signal.clear()
        if self.is_multi:
            res = []
            for i in self.sclected_list:
                res.append(self.choices[i])
            return res
        else:
            return self.choices[self.sclected]

class InputBox():
    def __init__(self,header:str,footer:str,CompatibilityMode:bool = False) -> None:
        self.header = header
        self.footer = footer
        self.CompatibilityMode = CompatibilityMode
        if CompatibilityMode == False:
            del self
            print("THE PART IS WIP!")
            return

class FileOpenBox():
    def get_available_drives(self):
        drives = []
        for drive in range(ord('A'), ord('Z')+1):
            drive_name = chr(drive) + ":\\"
            if os.path.exists(drive_name):
                drives.append([drive_name])

        return drives
    def hook(self,x):
        up = keyboard.KeyboardEvent(event_type='down', scan_code=72, name='up')
        down = keyboard.KeyboardEvent(event_type='down', scan_code=80, name='down')
        enter = keyboard.KeyboardEvent(event_type='down', scan_code=28, name='enter')
        space = keyboard.KeyboardEvent(event_type='down', scan_code=57, name='space')
        back = keyboard.KeyboardEvent(event_type='down', scan_code=14, name='back')
        # # get key code and name
        # print("current key code:  {}".format(x.scan_code))
        # print("current key name:  {}".format(x.name))
        self.Last = ("You pressed {}.".format(x.name))
        if x.event_type == up.event_type and x.scan_code == up.scan_code:
            if self.sclected <= 0:
                return
            self.sclected -= 1
            self.flush_signal.set()
        elif x.event_type == down.event_type and x.scan_code == down.scan_code:
            if self.sclected >= len(self.dir_list)-1:
                return
            self.sclected += 1
            self.flush_signal.set()
        elif x.event_type == enter.event_type and x.scan_code == enter.scan_code:
            self.is_selected = True
            self.flush_signal.set()
        elif x.event_type == space.event_type and x.scan_code == space.scan_code and self.multi:
            try:
                if self.sclected_list[self.path] != []:
                    pass
            except:
                self.sclected_list[self.path] = []
            if self.dir_list[self.sclected][2] in self.sclected_list[self.path]:
                self.sclected_list[self.path].remove(self.dir_list[self.sclected][2])
            else:
                self.sclected_list[self.path].append(self.dir_list[self.sclected][2])
            self.flush_signal.set()
        elif x.event_type == back.event_type and x.scan_code == back.scan_code:
            if os.path.split(self.path)[1] == '':
                self.change_disk = True
                self.flush_signal.set()
                return
            self.path = os.path.split(self.path)[0]
            self.sclected = 0
            self.flush_signal.set()
    def __init__(self,path:str,multi:bool = False) -> None:
        self.path = path
        self.multi = multi
        self.flush_signal = threading.Event()
        self.is_selected = False
        self.Last = ""
        self.change_disk = False
        self.dir_list = []
        self.sclected = 0
        keyboard.hook(self.hook)
        if multi :
            self.sclected_list = {}
    def loop(self) -> None:
        sclected_word = ""
        if self.multi:
            sclected_word = "You have Sclected:\n"
            cnt = 0
            for v in self.sclected_list.values():
                for i in v:
                    sclected_word += i + "\n"
                    cnt += 1
                    if cnt >= 5:
                        sclected_word += "... "
        self.footer = sclected_word
        self.header = "注:蓝色字体为文件夹\nYou are now at : " + self.path
        res = os.listdir(self.path)
        self.dir_list = []
        for i in res:
            self.dir_list.append([i,os.path.isfile(os.path.join(self.path,i)),os.path.abspath(os.path.join(self.path,i))])
        print(self.header)
        if self.multi:
            print("* 按 ↑ ↓ 选择  Back(退格键) 返回上一层  Space(空格) 选中(文件)  Enter(回车) 确定(文件)/打开(文件夹)")
        else:
            print("* 按 ↑ ↓ 选择  Back(退格键) 返回上一层  Enter(回车) 确定(文件)/打开(文件夹)")
        print(self.Last)
        print()
        front = True
        back = True
        for i in range(len(self.dir_list)):
            this_word = self.dir_list[i][0]
            if i-self.sclected < -3:
                if front:
                    front = False
                    print("  ...")
                continue
            if i-self.sclected > 3:
                if back:
                    back = False
                    print("  ...")
                continue
            try:
                if self.dir_list[i][2] in self.sclected_list[self.path]:
                    this_word = Fore.WHITE + Back.WHITE + self.dir_list[i][0] + Style.RESET_ALL
            except:
                pass
            if not self.dir_list[i][1]:
                this_word = Fore.BLUE + self.dir_list[i][0] + Style.RESET_ALL
            if i == self.sclected:
                this_word = "> " + this_word
            else:
                this_word = "  " + this_word
            print(this_word)
        print()
        print(self.footer)   
    
    def start(self) -> list | str:
        while True:
            os.system("cls")
            if self.is_selected:
                if self.change_disk:
                    self.is_selected = False
                    self.change_disk = False
                    continue
                if self.dir_list[self.sclected][1] == False:
                    self.is_selected = False
                    self.path = self.dir_list[self.sclected][2]
                    self.sclected = 0
                    continue
                break
            if self.change_disk:
                self.path = SclectBox("Change Disk\n请选择你的盘符","",self.get_available_drives()).start()[0]
            self.loop()
            self.flush_signal.wait()
            self.flush_signal.clear()
        res = []
        os.system("cls")
        if self.multi:
            for v in self.sclected_list.values():
                for i in v:
                    res.append(i)
            return res
        else:
            return self.dir_list[self.sclected][2]
class ynBox():
    def __init__(self,header:str,footer:str) -> None:
        self.header = header
        self.footer = footer 
    def start(self) -> bool:
        choices = SclectBox(self.header,self.footer,(("Yes. 确认",0),("No. 否",1)))
        if choices[1] == 0:
            return True
        else:
            return False
if __name__ == "__main__":
    def test_hook(x):
        # get key code and name
        print("current key code:  {}".format(x.scan_code))
        print("current key name:  {}".format(x.name))
    FileOpenBox(os.getcwd(),True).start()
    # keyboard.hook(test_hook)
    # keyboard.wait()