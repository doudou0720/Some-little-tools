import os
import threading
import sys
import platform
from colorama import Fore, Back, Style
import time
import uuid

# 只在非Windows系统上导入Unix特定的模块
if platform.system() != "Windows":
    import select
    import termios
    import tty

class TerminalInput:
    """
    在无root的Linux/Termux环境下替代keyboard库的功能
    该类提供与keyboard库类似的钩子机制，用于捕获键盘输入事件
    """
    
    def __init__(self):
        """
        初始化TerminalInput类
        """
        self.is_windows = platform.system().lower() == 'windows'
        self.hook_callback = None
        self.is_running = False
        self.input_thread = None
        self.old_settings = None
        self.fd = None
        
        # 如果是Windows系统，尝试导入keyboard库
        if self.is_windows:
            try:
                import keyboard
                self.keyboard_module = keyboard
            except ImportError:
                self.keyboard_module = None
        else:
            self.keyboard_module = None

    def hook(self, callback):
        """
        注册键盘事件钩子回调函数
        
        Args:
            callback: 回调函数，接受一个参数（键盘事件对象）
        """
        self.hook_callback = callback
        self.is_running = True
        
        # 如果是Windows系统且keyboard模块可用，使用原生keyboard库
        if self.is_windows and self.keyboard_module:
            self.keyboard_module.hook(callback)
        else:
            # 在Linux/Termux环境下使用自定义输入处理
            self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
            self.input_thread.start()
    
    def unhooks(self):
        """
        移除键盘事件钩子
        """
        self.is_running = False
        if self.is_windows and self.keyboard_module:
            self.keyboard_module.unhook_all()
        elif self.input_thread:
            self.input_thread.join(timeout=1)
            # 恢复终端设置
            if self.old_settings and self.fd:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
    
    def _input_loop(self):
        """
        在Linux/Termux环境下处理键盘输入的循环
        """
        try:
            # 设置终端为非阻塞模式
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)
            tty.setcbreak(sys.stdin.fileno())
            
            while self.is_running:
                # 检查是否有输入
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if self.hook_callback:
                        # 将字符转换为类似keyboard库的事件对象
                        event = self._char_to_event(char)
                        self.hook_callback(event)
        except Exception as e:
            pass
        finally:
            # 恢复终端设置
            if self.old_settings and self.fd:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
    
    def _char_to_event(self, char):
        """
        将字符转换为类似keyboard库的事件对象
        
        Args:
            char: 输入的字符
            
        Returns:
            SimpleNamespace: 类似keyboard.KeyboardEvent的事件对象
        """
        from types import SimpleNamespace
        
        # 定义常见按键的映射
        key_map = {
            '\x1b': 'esc',     # ESC键
            '\n': 'enter',     # 回车键
            '\r': 'enter',     # 回车键
            ' ': 'space',      # 空格键
            '\x7f': 'backspace', # 退格键
            '\x08': 'backspace', # 退格键
        }
        
        # 箭头键和其他特殊键的处理 (ANSI转义序列)
        if char == '\x1b':  # ESC键开头的序列
            # 尝试读取后续字符以识别箭头键
            if select.select([sys.stdin], [], [], 0.01)[0]:
                char2 = sys.stdin.read(1)
                if char2 == '[':
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        char3 = sys.stdin.read(1)
                        if char3 == 'A':
                            char = 'up'
                            key_map[char] = 'up'
                        elif char3 == 'B':
                            char = 'down'
                            key_map[char] = 'down'
                        elif char3 == 'C':
                            char = 'right'
                            key_map[char] = 'right'
                        elif char3 == 'D':
                            char = 'left'
                            key_map[char] = 'left'
        
        # 获取键名
        key_name = key_map.get(char, char if len(char) == 1 else f'key_{ord(char)}')
        
        # 创建事件对象
        event = SimpleNamespace()
        event.name = key_name
        event.scan_code = ord(char) if len(char) == 1 else 0
        event.event_type = 'down'
        return event

    class KeyboardEvent:
        """
        模拟keyboard.KeyboardEvent类
        """
        def __init__(self, event_type, scan_code, name):
            self.event_type = event_type
            self.scan_code = scan_code
            self.name = name

# 根据系统平台选择使用哪个输入处理模块
# 优先尝试使用keyboard库，只有在无法导入时才使用TerminalInput作为备用选项
try:
    import keyboard
    input_handler = keyboard
except ImportError:
    input_handler = TerminalInput()

class SelectBox():
    """
    选择框类，提供基于键盘操作的交互式选择界面
    支持单选和多选模式，通过上下方向键选择，回车确认，空格键多选
    """

    def hook(self, x):
        """
        键盘事件钩子函数，处理用户按键输入
        
        Args:
            x: 键盘事件对象
        """
        # 定义各种按键事件
        up = input_handler.KeyboardEvent(event_type='down', scan_code=72, name='up')
        down = input_handler.KeyboardEvent(event_type='down', scan_code=80, name='down')
        enter = input_handler.KeyboardEvent(event_type='down', scan_code=28, name='enter')
        space = input_handler.KeyboardEvent(event_type='down', scan_code=57, name='space')
        # # 获取按键代码和名称（调试用）
        # print("当前按键代码:  {}".format(x.scan_code))
        # print("当前按键名称:  {}".format(x.name))
        self.Last = ("你按下了 {}.".format(x.name))
        # 处理向上方向键
        if x.event_type == up.event_type and x.scan_code == up.scan_code:
            if self.selected <= 0:
                return
            self.selected -= 1
            self.flush_signal.set()
        # 处理向下方向键
        elif x.event_type == down.event_type and x.scan_code == down.scan_code:
            if self.selected >= self.length-1:
                return
            self.selected += 1
            self.flush_signal.set()
        # 处理回车键确认选择
        elif x.event_type == enter.event_type and x.scan_code == enter.scan_code:
            self.is_selected = True
            self.flush_signal.set()
        # 处理空格键多选（仅在多选模式下有效）
        elif x.event_type == space.event_type and x.scan_code == space.scan_code and self.is_multi:
            if self.selected in self.selected_list:
                self.selected_list.remove(self.selected)
            else:
                self.selected_list.append(self.selected)
            self.flush_signal.set()


    def __init__(self, header: str, footer: str, choices: list | tuple, multi: bool = False, default_number=0) -> None:
        """
        初始化选择框
        
        Args:
            header (str): 选择框顶部显示的标题
            footer (str): 选择框底部显示的信息
            choices (list | tuple): 可选项列表，每个选项为一个元组
            multi (bool): 是否为多选模式，默认为False
            default_number (int): 默认选中项的索引，默认为0
        """
        self.header = header
        self.footer = footer
        self.choices = choices
        self.is_multi = multi
        self.selected_list = []
        self.selected = default_number
        self.flush_signal = threading.Event()
        self.is_selected = False
        self.Last = ""
        self.length = len(self.choices)

        input_handler.hook(self.hook)

    
    def loop(self) -> None:
        """
        循环显示选择界面
        """
        print(self.header)
        # 根据是否多选模式显示不同操作提示
        if self.is_multi:
            print("* 按 ↑ ↓ 选择  Space(空格)选中  Enter(回车) 确定")
        else:
            print("* 按 ↑ ↓ 选择  Enter(回车) 确定")
        print(self.Last)
        print()
        # 显示所有选项
        for i in range(len(self.choices)):
            this_word = self.choices[i][0]
            # 处理多选模式下已选项的显示
            if i in self.selected_list:
                this_word = Fore.WHITE + Back.WHITE + self.choices[i][0] + Style.RESET_ALL
            # 处理当前选中项的显示（添加箭头标记）
            if i == self.selected:
                this_word = "> " + this_word
            else:
                this_word = "  " + this_word
            print(this_word)
        print()
        print(self.footer)   
    
    def start(self) -> list | str:
        """
        启动选择框并等待用户选择
        
        Returns:
            list | str: 多选模式返回选项列表，单选模式返回选中项
        """
        while True:
            os.system("cls")
            if self.is_selected:
                break
            self.loop()
            self.flush_signal.wait()
            self.flush_signal.clear()
        # 根据模式返回结果
        if self.is_multi:
            res = []
            for i in self.selected_list:
                res.append(self.choices[i])
            return res
        else:
            return self.choices[self.selected]

class InputBox():
    """
    输入框类，用于接收用户文本输入（开发中）
    """
    def __init__(self, header: str, footer: str, CompatibilityMode: bool = False) -> None:
        """
        初始化输入框
        
        Args:
            header (str): 输入框顶部显示的标题
            footer (str): 输入框底部显示的信息
            CompatibilityMode (bool): 兼容模式，默认为False
        """
        self.header = header
        self.footer = footer
        self.CompatibilityMode = CompatibilityMode
        # 如果不是兼容模式，则提示功能开发中
        if CompatibilityMode == False:
            del self
            print("该功能正在开发中！")
            return

class FileOpenBox():
    """
    文件选择框类，用于浏览和选择文件/文件夹
    支持多选文件，可切换磁盘驱动器
    """
    def get_available_drives(self):
        """
        获取系统中所有可用的磁盘驱动器
        
        Returns:
            list: 可用驱动器列表
        """
        drives = []
        for drive in range(ord('A'), ord('Z')+1):
            drive_name = chr(drive) + ":\\"
            if os.path.exists(drive_name):
                drives.append([drive_name])

        return drives
        
    def hook(self, x):
        """
        键盘事件钩子函数，处理文件选择界面的按键输入
        
        Args:
            x: 键盘事件对象
        """
        # 定义各种按键事件
        up = input_handler.KeyboardEvent(event_type='down', scan_code=72, name='up')
        down = input_handler.KeyboardEvent(event_type='down', scan_code=80, name='down')
        enter = input_handler.KeyboardEvent(event_type='down', scan_code=28, name='enter')
        space = input_handler.KeyboardEvent(event_type='down', scan_code=57, name='space')
        back = input_handler.KeyboardEvent(event_type='down', scan_code=14, name='back')
        # # 获取按键代码和名称（调试用）
        # print("当前按键代码:  {}".format(x.scan_code))
        # print("当前按键名称:  {}".format(x.name))
        self.Last = ("你按下了 {}.".format(x.name))
        # 处理向上方向键
        if x.event_type == up.event_type and x.scan_code == up.scan_code:
            if self.selected <= 0:
                return
            self.selected -= 1
            self.flush_signal.set()
        # 处理向下方向键
        elif x.event_type == down.event_type and x.scan_code == down.scan_code:
            if self.selected >= len(self.dir_list)-1:
                return
            self.selected += 1
            self.flush_signal.set()
        # 处理回车键
        elif x.event_type == enter.event_type and x.scan_code == enter.scan_code:
            self.is_selected = True
            self.flush_signal.set()
        # 处理空格键多选（仅在多选模式下有效）
        elif x.event_type == space.event_type and x.scan_code == space.scan_code and self.multi:
            try:
                if self.selected_list[self.path] != []:
                    pass
            except:
                self.selected_list[self.path] = []
            if self.dir_list[self.selected][2] in self.selected_list[self.path]:
                self.selected_list[self.path].remove(self.dir_list[self.selected][2])
            else:
                self.selected_list[self.path].append(self.dir_list[self.selected][2])
            self.flush_signal.set()
        # 处理退格键返回上级目录
        elif x.event_type == back.event_type and x.scan_code == back.scan_code:
            # 如果在根目录，则切换磁盘
            if os.path.split(self.path)[1] == '':
                self.change_disk = True
                self.flush_signal.set()
                return
            self.path = os.path.split(self.path)[0]
            self.selected = 0
            self.flush_signal.set()
            
    def __init__(self, path: str, multi: bool = False) -> None:
        """
        初始化文件选择框
        
        Args:
            path (str): 初始路径
            multi (bool): 是否为多选模式，默认为False
        """
        self.path = path
        self.multi = multi
        self.flush_signal = threading.Event()
        self.is_selected = False
        self.Last = ""
        self.change_disk = False
        self.dir_list = []
        self.selected = 0
        input_handler.hook(self.hook)
        # 如果是多选模式，初始化选中列表
        if multi:
            self.selected_list = {}
            
    def loop(self) -> None:
        """
        循环显示文件选择界面
        """
        selected_word = ""
        # 处理多选模式下已选文件显示
        if self.multi:
            selected_word = "你已选择的文件:\n"
            cnt = 0
            for v in self.selected_list.values():
                for i in v:
                    selected_word += i + "\n"
                    cnt += 1
                    if cnt >= 5:
                        selected_word += "... "
        self.footer = selected_word
        self.header = "注:蓝色字体为文件夹\n你当前的位置: " + self.path
        # 获取当前目录下的文件和文件夹列表
        res = os.listdir(self.path)
        self.dir_list = []
        for i in res:
            self.dir_list.append([i, os.path.isfile(os.path.join(self.path, i)), os.path.abspath(os.path.join(self.path, i))])
        print(self.header)
        # 根据是否多选模式显示不同操作提示
        if self.multi:
            print("* 按 ↑ ↓ 选择  Back(退格键) 返回上一层  Space(空格) 选中(文件)  Enter(回车) 确定(文件)/打开(文件夹)")
        else:
            print("* 按 ↑ ↓ 选择  Back(退格键) 返回上一层  Enter(回车) 确定(文件)/打开(文件夹)")
        print(self.Last)
        print()
        # 显示文件列表（只显示当前选中项附近的几项以减少界面长度）
        front = True
        back = True
        for i in range(len(self.dir_list)):
            this_word = self.dir_list[i][0]
            # 只显示当前选中项附近的几项
            if i-self.selected < -3:
                if front:
                    front = False
                    print("  ...")
                continue
            if i-self.selected > 3:
                if back:
                    back = False
                    print("  ...")
                continue
            # 处理多选模式下已选项的显示
            try:
                if self.dir_list[i][2] in self.selected_list[self.path]:
                    this_word = Fore.WHITE + Back.WHITE + self.dir_list[i][0] + Style.RESET_ALL
            except:
                pass
            # 文件夹以蓝色显示
            if not self.dir_list[i][1]:
                this_word = Fore.BLUE + self.dir_list[i][0] + Style.RESET_ALL
            # 处理当前选中项的显示（添加箭头标记）
            if i == self.selected:
                this_word = "> " + this_word
            else:
                this_word = "  " + this_word
            print(this_word)
        print()
        print(self.footer)   
    
    def start(self) -> list | str:
        """
        启动文件选择框并等待用户选择
        
        Returns:
            list | str: 多选模式返回选中文件列表，单选模式返回选中文件路径
        """
        while True:
            os.system("cls")
            if self.is_selected:
                # 处理切换磁盘的情况
                if self.change_disk:
                    self.is_selected = False
                    self.change_disk = False
                    continue
                # 如果选中的是文件夹，则进入该文件夹
                if self.dir_list[self.selected][1] == False:
                    self.is_selected = False
                    self.path = self.dir_list[self.selected][2]
                    self.selected = 0
                    continue
                break
            # 处理切换磁盘
            if self.change_disk:
                self.path = SelectBox("切换磁盘\n请选择你的盘符", "", self.get_available_drives()).start()[0]
            self.loop()
            self.flush_signal.wait()
            self.flush_signal.clear()
        res = []
        os.system("cls")
        # 根据模式返回结果
        if self.multi:
            for v in self.selected_list.values():
                for i in v:
                    res.append(i)
            return res
        else:
            return self.dir_list[self.selected][2]

class ynBox():
    """
    确认框类，用于简单的Yes/No选择
    """
    def __init__(self, header: str, footer: str) -> None:
        """
        初始化确认框
        
        Args:
            header (str): 确认框顶部显示的标题
            footer (str): 确认框底部显示的信息
        """
        self.header = header
        self.footer = footer 
        
    def start(self) -> bool:
        """
        启动确认框并等待用户选择
        
        Returns:
            bool: 用户选择Yes返回True，选择No返回False
        """
        choices = SelectBox(self.header, self.footer, (("Yes. 确认", 0), ("No. 否", 1)))
        if choices[1] == 0:
            return True
        else:
            return False

class ProgressBar:
    """
    进度条类，用于显示任务进度
    支持主进度条和多个子进度条，具有线程安全特性
    """
    def __init__(self, total=100, title="Progress", width=50, refresh_rate=0.01, weight=1.0, parent=None):
        """
        初始化进度条
        
        Args:
            total (int): 进度总量，默认为100
            title (str): 进度条标题，默认为"Progress"
            width (int): 进度条宽度，默认为50个字符
            refresh_rate (float): 刷新频率（秒），默认为0.1秒
            weight (float): 进度条权重，用于父进度条计算，默认为1.0
            parent (ProgressBar): 父进度条对象，用于嵌套结构
        """
        self.total = total
        self.current = 0
        self.title = title
        self.width = width
        self.sub_progress_bars = []
        self.lock = threading.Lock()
        self.is_finished = False
        self.selected_sub_progress = -1  # 当前选中的子进度条索引
        self.is_interactive = False  # 是否启用交互模式
        self.input_handler = None  # 输入处理句柄
        self.show_full_tree = False  # 是否显示完整进度树
        self.refresh_rate = refresh_rate  # 刷新频率
        self.refresh_thread = None  # 刷新线程
        self.need_refresh = threading.Event()  # 刷新信号
        self.is_refreshing = False  # 是否正在刷新
        self.main_progress_expanded = True  # 主进度条是否展开显示
        self.weight = weight  # 权重
        self.parent = parent  # 父进度条引用
        self.description = ""  # 描述信息
        self.depends_on = None  # 依赖关系
        self.replaces = None  # 替代关系
        self.uuid = str(uuid.uuid4())  # 唯一标识符

    def update(self, value=None, increment=1):
        """
        更新进度条
        
        Args:
            value: 直接设置的值
            increment: 增量值，默认为1
        """
        with self.lock:
            if self.is_finished:
                return
                
            if value is not None:
                self.current = value
            else:
                self.current += increment
                
            if self.current > self.total:
                self.current = self.total
                
            # 如果有父进度条，通知父进度条更新
            if self.parent:
                self.parent._on_sub_progress_update(self)
            else:
                # 只有根进度条才触发刷新
                self.need_refresh.set()

    def add_sub_progress(self, name, total=100, description="", depends_on=None, weight=1.0):
        """
        添加子进度条
        
        Args:
            name: 子进度条名称
            total: 子进度条总量，默认为100
            description: 子进度条描述信息
            depends_on: 依赖的前置任务ID或名称，可以是单个值或列表
            weight: 子进度条权重，默认为1.0
            
        Returns:
            ProgressBar: 子进度条对象
        """
        with self.lock:
            # 创建新的子进度条对象
            sub_progress = ProgressBar(
                total=total, 
                title=name, 
                weight=weight, 
                parent=self,
                refresh_rate=self.refresh_rate
            )
            sub_progress.description = description
            
            # 处理依赖关系，支持单个依赖或多个依赖
            if depends_on is not None:
                if isinstance(depends_on, (str, ProgressBar)):
                    # 单个依赖
                    depends_on_list = [depends_on]
                elif isinstance(depends_on, (list, tuple)):
                    # 多个依赖
                    depends_on_list = list(depends_on)
                else:
                    depends_on_list = None
            else:
                depends_on_list = None
                
            sub_progress.depends_on = depends_on_list
            
            # 添加子进度条
            self.sub_progress_bars.append(sub_progress)
            
            # 触发刷新
            if not self.parent:  # 只有根进度条才触发刷新
                self.need_refresh.set()
            
            return sub_progress
    
    def _on_sub_progress_update(self, sub_progress):
        """
        当子进度条更新时调用，用于计算加权进度
        
        Args:
            sub_progress: 更新的子进度条对象
        """
        with self.lock:
            if self.is_finished:
                return
                
            # 根据子进度条的权重计算对父进度条的影响
            if self.sub_progress_bars:
                total_weight = sum(sp.weight for sp in self.sub_progress_bars)
                if total_weight > 0:
                    weighted_progress = sum(
                        (sp.current / sp.total) * sp.weight 
                        for sp in self.sub_progress_bars 
                        if sp.total > 0
                    )
                    self.current = int((weighted_progress / total_weight) * self.total)
            
            # 如果有父进度条，继续向上传递
            if self.parent:
                self.parent._on_sub_progress_update(self)
            else:
                # 只有根进度条才触发刷新
                self.need_refresh.set()

    def finish_sub_progress(self, sub_progress):
        """
        完成子进度条
        
        Args:
            sub_progress: 子进度条对象
        """
        with self.lock:
            if sub_progress in self.sub_progress_bars:
                sub_progress.current = sub_progress.total
                sub_progress.is_finished = True
                
                # 处理替代逻辑
                for sp in self.sub_progress_bars:
                    if sp.depends_on:
                        deps = sp.depends_on if isinstance(sp.depends_on, list) else [sp.depends_on]
                        # 检查是否依赖当前完成的任务
                        for dep in deps:
                            if isinstance(dep, ProgressBar) and dep.uuid == sub_progress.uuid:
                                sp.replaces = sub_progress.uuid
                                break
                            elif dep == sub_progress.uuid:
                                sp.replaces = sub_progress.uuid
                                break
                
                # 更新主进度条
                self._on_sub_progress_update(sub_progress)

    def finish(self):
        """
        完成进度条
        """
        with self.lock:
            self.current = self.total
            self.is_finished = True
            # 如果有父进度条，通知父进度条
            if self.parent:
                self.parent._on_sub_progress_update(self)
            else:
                # 只有根进度条才触发刷新
                self.need_refresh.set()
    
    def enable_interaction(self):
        """
        启用交互模式，允许用户通过键盘选择和查看详细信息
        """
        # 只有根进度条才能启用交互模式
        if not self.parent:
            self.is_interactive = True
            self.selected_sub_progress = 0 if self._get_all_sub_progress() else -1
            self.input_handler = input_handler
            self.input_handler.hook(self._handle_key_event)
            # 启动刷新线程
            self._start_refresh_thread()
    
    def disable_interaction(self):
        """
        禁用交互模式
        """
        # 只有根进度条才能禁用交互模式
        if not self.parent:
            self.is_interactive = False
            if self.input_handler:
                # 根据不同的输入处理器调用相应的取消钩子方法
                if hasattr(self.input_handler, 'unhook_all'):
                    self.input_handler.unhook_all()
                elif hasattr(self.input_handler, 'unhooks'):
                    self.input_handler.unhooks()
            self.selected_sub_progress = -1
            # 停止刷新线程
            self._stop_refresh_thread()
    
    def _start_refresh_thread(self):
        """
        启动刷新线程
        """
        if not self.parent and not self.is_refreshing:  # 只有根进度条启动刷新线程
            self.is_refreshing = True
            self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
            self.refresh_thread.start()
    
    def _stop_refresh_thread(self):
        """
        停止刷新线程
        """
        if not self.parent:  # 只有根进度条停止刷新线程
            self.is_refreshing = False
            if self.refresh_thread:
                self.refresh_thread.join(timeout=1)
    
    def _refresh_loop(self):
        """
        刷新循环，在独立线程中运行
        """
        while self.is_refreshing:
            # 等待刷新信号或超时
            self.need_refresh.wait(self.refresh_rate)
            with self.lock:
                self._draw()
            self.need_refresh.clear()
    
    def _get_all_sub_progress(self, flat_list=None, level=0):
        """
        获取所有子进度条的扁平化列表
        
        Args:
            flat_list: 扁平化列表
            level: 当前层级
            
        Returns:
            list: 包含(子进度条, 层级)元组的列表
        """
        if flat_list is None:
            flat_list = []
            
        for sub in self.sub_progress_bars:
            flat_list.append((sub, level))
            sub._get_all_sub_progress(flat_list, level + 1)
            
        return flat_list
    
    def _handle_key_event(self, event):
        """
        处理键盘事件
        
        Args:
            event: 键盘事件对象
        """
        # 确保在主线程中更新UI
        all_sub_progress = self._get_all_sub_progress()
        if event.name == 'up' and self.selected_sub_progress > 0:
            self.selected_sub_progress -= 1
            self.need_refresh.set()
        elif event.name == 'down' and self.selected_sub_progress < len(all_sub_progress) - 1:
            self.selected_sub_progress += 1
            self.need_refresh.set()
        elif event.name == 'enter' and self.selected_sub_progress >= 0 and all_sub_progress:
            selected_progress, _ = all_sub_progress[self.selected_sub_progress]
            self.show_detail(selected_progress)
            # 使用更优雅的方式等待用户按键返回，避免换行问题
            try:
                import msvcrt
                msvcrt.getch()
            except ImportError:
                try:
                    import tty, sys, termios
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except:
                    # 最后的备选方案
                    input()
            self.need_refresh.set()
        elif event.name.lower() == 'm':  # 确保大小写不敏感
            # 切换完整进度树显示模式
            self.show_full_tree = not self.show_full_tree
            self.need_refresh.set()
        elif event.name == 'left':
            # 收起主进度条
            self.main_progress_expanded = False
            self.need_refresh.set()
        elif event.name == 'right':
            # 展开主进度条
            self.main_progress_expanded = True
            self.need_refresh.set()
    
    def show_detail(self, sub_progress):
        """
        显示子进度条的详细信息
        
        Args:
            sub_progress: 子进度条对象
        """
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 显示主进度条
        print("=" * 60)
        self._draw_main_progress()
        print("=" * 60)
        
        # 显示子进度条详细信息
        print(f"\n子进度条: {sub_progress.title}")
        print(f"UUID: {sub_progress.uuid}")
        print(f"进度: {sub_progress.current}/{sub_progress.total} ({sub_progress.current / sub_progress.total * 100:.1f}%)" if sub_progress.total > 0 else "进度: N/A")
        print(f"状态: {'已完成' if sub_progress.is_finished else '进行中'}")
        print(f"权重: {sub_progress.weight}")
        
        if sub_progress.depends_on:
            dep_names = []
            deps = sub_progress.depends_on if isinstance(sub_progress.depends_on, list) else [sub_progress.depends_on]
            for dep in deps:
                if isinstance(dep, ProgressBar):
                    dep_names.append(dep.title)
                else:
                    # 尝试通过UUID查找依赖任务的名称
                    found = False
                    for sp in self._get_all_sub_progress():
                        if sp[0].uuid == dep:
                            dep_names.append(sp[0].title)
                            found = True
                            break
                    if not found:
                        dep_names.append(str(dep))
            print(f"依赖任务: {', '.join(dep_names)}")
            
        if sub_progress.replaces:
            # 尝试通过UUID查找替代任务的名称
            replace_name = sub_progress.replaces
            for sp in self._get_all_sub_progress():
                if sp[0].uuid == sub_progress.replaces:
                    replace_name = sp[0].title
                    break
            print(f"已完成并替代: {replace_name}")
        
        if sub_progress.description:
            print(f"\n描述信息:")
            print(sub_progress.description)
        
        print(f"\n按任意键返回进度条视图...")

    def _draw(self):
        """
        绘制进度条
        """
        # 只有根进度条才绘制
        if self.parent:
            return
            
        # 直接清空整个屏幕而不是使用ANSI转义序列
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 绘制主进度条（如果展开）
        if self.main_progress_expanded:
            self._draw_main_progress()
        
        # 获取所有子进度条
        all_sub_progress = self._get_all_sub_progress()
        
        # 根据显示模式绘制子进度条
        if all_sub_progress:
            if self.show_full_tree:
                # 显示完整进度树
                for i, (sub_progress, level) in enumerate(all_sub_progress):
                    self._draw_sub_progress(sub_progress, i, level)
            else:
                # 显示常规进度条（前置任务完成后显示替代任务）
                for i, (sub_progress, level) in enumerate(all_sub_progress):
                    # 只显示没有被替代的任务
                    if not sub_progress.replaces:
                        self._draw_sub_progress(sub_progress, i, level)
            
            # 显示展开/收起提示
            if self.main_progress_expanded:
                print(f"{Fore.CYAN}[←键收起主进度条 | M键切换: 显示完整树形结构]{Style.RESET_ALL}" if not self.show_full_tree else f"{Fore.CYAN}[←键收起主进度条 | M键切换: 显示简洁树形结构]{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}[→键展开主进度条 | M键切换: 显示完整树形结构]{Style.RESET_ALL}" if not self.show_full_tree else f"{Fore.CYAN}[→键展开主进度条 | M键切换: 显示简洁树形结构]{Style.RESET_ALL}")
        else:
            # 没有子进度条时的提示
            if self.main_progress_expanded:
                print(f"{Fore.CYAN}[←键收起主进度条]{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}[→键展开主进度条]{Style.RESET_ALL}")

    def _draw_main_progress(self):
        """
        绘制主进度条
        """
        percent = self.current / self.total if self.total > 0 else 0
        filled_width = int(self.width * percent)
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        
        status = "✓" if self.is_finished else "◐"
        # 限制标题长度以避免换行问题
        title = self.title if len(self.title) <= 50 else self.title[:47] + "..."
        line = f"{title} [{bar}] {percent:.1%} {status}"
        # 确保主进度条不会换行
        terminal_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
        if len(line) > terminal_width:
            line = line[:terminal_width-1]
        print(line)
        
        # 显示模式提示
        mode_text = "[M键切换: 显示完整树形结构]" if not self.show_full_tree else "[M键切换: 显示简洁树形结构]"
        mode_line = f"{Fore.CYAN}{mode_text}{Style.RESET_ALL}"
        # 确保模式提示行不会换行
        if len(mode_line) > terminal_width:
            mode_line = mode_line[:terminal_width-1]
        print(mode_line)

    def _draw_sub_progress(self, sub_progress, index, level):
        """
        绘制子进度条
        
        Args:
            sub_progress: 子进度条对象
            index: 子进度条索引
            level: 树层级
        """
        percent = sub_progress.current / sub_progress.total if sub_progress.total > 0 else 0
        filled_width = int(self.width * percent)
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        
        status = "✓" if sub_progress.is_finished else "◐"
        # 限制子进度条名称长度以避免换行问题
        name = sub_progress.title if len(sub_progress.title) <= 40 else sub_progress.title[:37] + "..."
        
        # 添加依赖和替代信息
        dependency_info = ""
        if sub_progress.depends_on:
            dep_names = []
            deps = sub_progress.depends_on if isinstance(sub_progress.depends_on, list) else [sub_progress.depends_on]
            for dep in deps:
                if isinstance(dep, ProgressBar):
                    dep_names.append(dep.title)
                else:
                    # 尝试通过UUID查找依赖任务的名称
                    found = False
                    for sp in self._get_all_sub_progress():
                        if sp[0].uuid == dep:
                            dep_names.append(sp[0].title)
                            found = True
                            break
                    if not found:
                        dep_names.append(str(dep))
            dependency_info = f" [依赖: {', '.join(dep_names)}]"
                
        if sub_progress.replaces:
            # 尝试通过UUID查找替代任务的名称
            replace_name = sub_progress.replaces
            for sp in self._get_all_sub_progress():
                if sp[0].uuid == sub_progress.replaces:
                    replace_name = sp[0].title
                    break
            dependency_info += f" [替代: {replace_name}]"
        
        # 如果有描述信息，添加提示符
        has_description = " [i]" if sub_progress.description else ""
        
        # 根据层级添加树形前缀
        if level == 0:
            prefix = "| "
        else:
            prefix = "|- " + "  " * (level - 1)
        
        # 高亮显示选中的子进度条
        if index == self.selected_sub_progress:
            line = f"{Back.WHITE}{Fore.BLACK}▶ {prefix}{name}:{has_description}{dependency_info} [{bar}] {percent:.1%} {status}{Style.RESET_ALL}"
        else:
            line = f"  {prefix}{name}:{has_description}{dependency_info} [{bar}] {percent:.1%} {status}"
        print(line)

if __name__ == "__main__":
    def test_hook(x):
        # 获取按键代码和名称（调试用）
        print("当前按键代码:  {}".format(x.scan_code))
        print("当前按键名称:  {}".format(x.name))
    
    # 使用统一的输入处理
    input_handler.hook(test_hook)
    
    try:
        FileOpenBox(os.getcwd(), True).start()
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # 清理资源
        # 根据不同的输入处理器调用相应的取消钩子方法
        if hasattr(input_handler, 'unhook_all'):
            input_handler.unhook_all()
        elif hasattr(input_handler, 'unhooks'):
            input_handler.unhooks()