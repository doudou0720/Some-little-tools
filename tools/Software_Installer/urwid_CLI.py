import urwid
import threading
import time
import uuid
import os
import platform
from collections import deque


class SelectBox:
    """
    基于urwid的选择框类，提供交互式选择界面
    支持单选和多选模式
    """
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
        self.selected_list = set() if multi else None
        self.selected = default_number
        self.result = None
        self.event = threading.Event()

    def _create_widgets(self):
        """创建urwid界面组件"""
        # 标题
        header = urwid.Text(('header', self.header))
        
        # 操作提示
        if self.is_multi:
            instruction = urwid.Text("* 按 ↑ ↓ 选择  Space(空格)选中  Enter(回车) 确定")
        else:
            instruction = urwid.Text("* 按 ↑ ↓ 选择  Enter(回车) 确定")
        
        # 选项列表
        self.buttons = []
        self.group = []
        for i, choice in enumerate(self.choices):
            label = choice[0]
            if self.is_multi:
                button = urwid.CheckBox(label, state=False)
                self.buttons.append(button)
            else:
                button = urwid.RadioButton(self.group, label, state=(i == self.selected))
                if i == self.selected:
                    self.selected_button = button
                self.buttons.append(button)
        
        # 使用SimpleListWalker和ListBox来显示选项
        list_walker = urwid.SimpleFocusListWalker(self.buttons)
        list_box = urwid.ListBox(list_walker)
        
        # 页脚
        footer = urwid.Text(self.footer)
        
        # 组合界面
        pile = urwid.Pile([
            ('pack', header), 
            ('pack', instruction), 
            ('pack', urwid.Divider()), 
            ('weight', 1, urwid.LineBox(list_box)), 
            ('pack', urwid.Divider()), 
            ('pack', footer)
        ])
        return urwid.Filler(pile, valign='top')

    def _handle_input(self, key):
        """处理键盘输入"""
        if key == 'enter':
            if self.is_multi:
                self.result = [(self.choices[i][0], self.choices[i][1]) 
                              for i, button in enumerate(self.buttons) if button.state]
            else:
                # 找到选中的单选按钮
                for i, button in enumerate(self.buttons):
                    if button.state:
                        self.result = self.choices[i]
                        break
            self.event.set()
        
        elif key == 'esc':
            self.result = None
            self.event.set()

    def start(self):
        """
        启动选择框并等待用户选择
        
        Returns:
            list | str: 多选模式返回选项列表，单选模式返回选中项
        """
        # 创建界面
        main_widget = self._create_widgets()
        
        # 创建主循环
        self.loop = urwid.MainLoop(main_widget, 
                                  palette=[
                                      ('header', 'bold', ''),
                                      ('footer', 'light gray', ''),
                                  ],
                                  unhandled_input=self._handle_input)
        
        # 启动界面
        self.loop.run()
        
        # 等待结果
        self.event.wait()
        return self.result


class FileOpenBox:
    """
    基于urwid的文件选择框类，用于浏览和选择文件/文件夹
    """
    def __init__(self, path: str, multi: bool = False) -> None:
        """
        初始化文件选择框
        
        Args:
            path (str): 初始路径
            multi (bool): 是否为多选模式，默认为False
        """
        self.path = os.path.abspath(path) if path else os.getcwd()
        self.multi = multi
        self.selected_files = set() if multi else None
        self.result = None
        self.event = threading.Event()
        
    def _get_dir_contents(self):
        """获取当前目录内容"""
        try:
            items = os.listdir(self.path)
            items.sort()
            
            # 添加返回上级目录选项
            contents = [("..", True, os.path.dirname(self.path))]  # 是目录
            for item in items:
                item_path = os.path.join(self.path, item)
                is_file = os.path.isfile(item_path)
                contents.append((item, is_file, item_path))
            return contents
        except Exception as e:
            return [("..", True, os.path.dirname(self.path))]

    def _create_widgets(self):
        """创建urwid界面组件"""
        # 标题
        header_text = f"注: 蓝色为文件夹\n当前位置: {self.path}"
        header = urwid.Text(('header', header_text))
        
        # 操作提示
        if self.multi:
            instruction = urwid.Text("* 按 ↑ ↓ 选择  Space(空格)选中文件  Enter(回车) 确定/打开")
        else:
            instruction = urwid.Text("* 按 ↑ ↓ 选择  Enter(回车) 确定/打开")
        
        # 文件列表
        self.contents = self._get_dir_contents()
        self.buttons = []
        
        for name, is_file, path in self.contents:
            if is_file:
                # 文件显示为默认颜色
                button = urwid.Button(name)
            else:
                # 目录显示为蓝色
                button = urwid.Button(('directory', name))
            
            # 为按钮添加点击事件
            urwid.connect_signal(button, 'click', self._on_item_selected, (name, is_file, path))
            self.buttons.append(button)
        
        # 使用SimpleListWalker和ListBox来显示文件列表
        list_walker = urwid.SimpleFocusListWalker(self.buttons)
        self.list_box = urwid.ListBox(list_walker)
        
        # 已选文件（多选模式）
        if self.multi and self.selected_files:
            selected_text = "已选择的文件:\n" + "\n".join(sorted(self.selected_files))
            selected = urwid.Text(selected_text)
        else:
            selected = urwid.Text("")
        
        # 组合界面
        pile = urwid.Pile([
            ('pack', header), 
            ('pack', instruction), 
            ('pack', urwid.Divider()), 
            ('weight', 1, urwid.LineBox(self.list_box)), 
            ('pack', urwid.Divider()), 
            ('pack', selected)
        ])
        return urwid.Filler(pile, valign='top')
        
    def _on_item_selected(self, button, data):
        """处理项目选择"""
        name, is_file, path = data
        
        # 如果是返回上级目录
        if name == "..":
            self.path = path if path else os.path.dirname(self.path)
            self._refresh()
            return
            
        # 如果是目录，进入目录
        if not is_file:
            self.path = path
            self._refresh()
            return
            
        # 如果是文件
        if self.multi:
            # 多选模式，切换选择状态
            if path in self.selected_files:
                self.selected_files.remove(path)
            else:
                self.selected_files.add(path)
            self._refresh()
        else:
            # 单选模式，直接返回结果
            self.result = path
            self.event.set()
            
    def _refresh(self):
        """刷新界面"""
        # 重新创建界面组件
        new_widget = self._create_widgets()
        self.loop.widget = new_widget
        
    def _handle_input(self, key):
        """处理键盘输入"""
        if key == 'enter':
            # 获取当前选中的项目
            focus_widget, focus_pos = self.list_box.get_focus()
            if focus_widget and 0 <= focus_pos < len(self.contents):
                name, is_file, path = self.contents[focus_pos]
                
                # 如果是返回上级目录
                if name == "..":
                    self.path = path if path else os.path.dirname(self.path)
                    self._refresh()
                    return
                    
                # 如果是目录，进入目录
                if not is_file:
                    self.path = path
                    self._refresh()
                    return
                    
                # 如果是文件
                if self.multi:
                    # 多选模式，切换选择状态
                    if path in self.selected_files:
                        self.selected_files.remove(path)
                    else:
                        self.selected_files.add(path)
                    self._refresh()
                else:
                    # 单选模式，直接返回结果
                    self.result = path
                    self.event.set()
                    
        elif key == 'space' and self.multi:
            # 多选模式下使用空格键选择
            focus_widget, focus_pos = self.list_box.get_focus()
            if focus_widget and 0 <= focus_pos < len(self.contents):
                name, is_file, path = self.contents[focus_pos]
                # 不能选择目录和上级目录
                if is_file and name != "..":
                    if path in self.selected_files:
                        self.selected_files.remove(path)
                    else:
                        self.selected_files.add(path)
                    self._refresh()
                    
        elif key == 'esc':
            if self.multi:
                self.result = list(self.selected_files) if self.selected_files else []
            else:
                self.result = None
            self.event.set()

    def start(self):
        """
        启动文件选择框并等待用户选择
        
        Returns:
            list | str: 多选模式返回选中文件列表，单选模式返回选中文件路径
        """
        # 创建界面
        main_widget = self._create_widgets()
        
        # 创建主循环
        self.loop = urwid.MainLoop(main_widget, 
                                  palette=[
                                      ('header', 'bold', ''),
                                      ('directory', 'light blue', ''),
                                  ],
                                  unhandled_input=self._handle_input)
        
        # 启动界面
        self.loop.run()
        
        # 等待结果
        self.event.wait()
        return self.result


class ynBox:
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
        self.result = None
        self.event = threading.Event()
        
    def _create_widgets(self):
        """创建urwid界面组件"""
        # 标题
        header = urwid.Text(('header', self.header))
        
        # 按钮
        yes_button = urwid.Button("Yes. 确认")
        no_button = urwid.Button("No. 否")
        
        # 为按钮添加点击事件
        urwid.connect_signal(yes_button, 'click', self._on_yes)
        urwid.connect_signal(no_button, 'click', self._on_no)
        
        # 按钮行
        buttons = urwid.Columns([yes_button, no_button], dividechars=3)
        
        # 页脚
        footer = urwid.Text(('footer', self.footer))
        
        # 组合界面
        pile = urwid.Pile([
            ('pack', header), 
            ('pack', urwid.Divider()), 
            ('pack', buttons), 
            ('pack', urwid.Divider()), 
            ('pack', footer)
        ])
        return urwid.Filler(pile, valign='top')
        
    def _on_yes(self, button):
        """处理Yes按钮点击"""
        self.result = True
        self.event.set()
        
    def _on_no(self, button):
        """处理No按钮点击"""
        self.result = False
        self.event.set()
        
    def _handle_input(self, key):
        """处理键盘输入"""
        if key == 'esc':
            self.result = False
            self.event.set()
    
    def start(self) -> bool:
        """
        启动确认框并等待用户选择
        
        Returns:
            bool: 用户选择Yes返回True，选择No返回False
        """
        # 创建界面
        main_widget = self._create_widgets()
        
        # 创建主循环
        self.loop = urwid.MainLoop(main_widget, 
                                  palette=[
                                      ('header', 'bold', ''),
                                      ('footer', 'light gray', ''),
                                  ],
                                  unhandled_input=self._handle_input)
        
        # 启动界面
        self.loop.run()
        
        # 等待结果
        self.event.wait()
        return self.result


class ProgressBar:
    """
    基于urwid的进度条类，用于显示任务进度
    支持主进度条和多个子进度条
    """
    def __init__(self, total=100, title="Progress", width=50, refresh_rate=0.1, weight=1.0, parent=None):
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
        self.lock = threading.RLock()  # 使用RLock支持重入
        self.is_finished = False
        self.refresh_rate = refresh_rate
        self.weight = weight
        self.parent = parent
        self.description = ""
        self.depends_on = None
        self.replaces = None
        self.uuid = str(uuid.uuid4())
        
        # urwid相关组件
        self.loop = None
        self.main_widget = None
        self.progress_text = None
        self.sub_progress_widgets = []
        self.refresh_callback = None
        self.main_progress_expanded = True
        self.show_full_tree = False
        self.selected_sub_progress = -1
        
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

    def _create_widgets(self):
        """创建urwid界面组件"""
        # 主进度条文本
        self.progress_text = urwid.Text(self._get_progress_text())
        
        # 子进度条列表
        self.sub_progress_widgets = []
        sub_progress_items = []
        
        # 获取所有子进度条
        all_sub_progress = self._get_all_sub_progress()
        
        # 根据显示模式添加子进度条
        for i, (sub_progress, level) in enumerate(all_sub_progress):
            # 只在简洁模式下显示没有被替代的任务
            if not self.show_full_tree and sub_progress.replaces:
                continue
                
            sub_text = urwid.Text(sub_progress._get_progress_text_with_level(level, i == self.selected_sub_progress))
            self.sub_progress_widgets.append((sub_text, sub_progress, level))
            sub_progress_items.append(sub_text)
        
        # 子进度条列表框
        if sub_progress_items:
            sub_list = urwid.Pile(sub_progress_items)
        else:
            sub_list = urwid.Text("暂无子任务")
            
        # 操作提示
        if self.main_progress_expanded:
            hint = "[←键收起主进度条 | M键切换: {}]".format(
                "显示完整树形结构" if not self.show_full_tree else "显示简洁树形结构")
        else:
            hint = "[→键展开主进度条 | M键切换: {}]".format(
                "显示完整树形结构" if not self.show_full_tree else "显示简洁树形结构")
        hint_text = urwid.Text(('hint', hint))
        
        # 组合界面
        if self.main_progress_expanded:
            pile = urwid.Pile([
                ('pack', self.progress_text), 
                ('pack', urwid.Divider()), 
                ('weight', 1, sub_list), 
                ('pack', urwid.Divider()), 
                ('pack', hint_text)
            ])
        else:
            pile = urwid.Pile([
                ('pack', self.progress_text), 
                ('pack', hint_text)
            ])
            
        self.main_widget = urwid.Filler(pile, valign='top')
        return self.main_widget
        
    def _get_progress_text(self):
        """获取主进度条文本"""
        percent = self.current / self.total if self.total > 0 else 0
        filled_width = int(self.width * percent)
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        
        status = "✓" if self.is_finished else "◐"
        # 限制标题长度以避免换行问题
        title = self.title if len(self.title) <= 50 else self.title[:47] + "..."
        return f"{title} [{bar}] {percent:.1%} {status}"
        
    def _get_progress_text_with_level(self, level, is_selected=False):
        """获取带层级信息的进度条文本"""
        percent = self.current / self.total if self.total > 0 else 0
        filled_width = int(self.width * percent)
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        
        status = "✓" if self.is_finished else "◐"
        # 限制标题长度以避免换行问题
        name = self.title if len(self.title) <= 40 else self.title[:37] + "..."
        
        # 添加依赖和替代信息
        dependency_info = ""
        if self.depends_on:
            dep_names = []
            deps = self.depends_on if isinstance(self.depends_on, list) else [self.depends_on]
            for dep in deps:
                if isinstance(dep, ProgressBar):
                    dep_names.append(dep.title)
                else:
                    # 尝试通过UUID查找依赖任务的名称
                    found = False
                    for sp, _ in self.parent._get_all_sub_progress() if self.parent else self._get_all_sub_progress():
                        if sp.uuid == dep:
                            dep_names.append(sp.title)
                            found = True
                            break
                    if not found:
                        dep_names.append(str(dep))
            dependency_info = f" [依赖: {', '.join(dep_names)}]"
                
        if self.replaces:
            # 尝试通过UUID查找替代任务的名称
            replace_name = self.replaces
            for sp, _ in self.parent._get_all_sub_progress() if self.parent else self._get_all_sub_progress():
                if sp.uuid == self.replaces:
                    replace_name = sp.title
                    break
            dependency_info += f" [替代: {replace_name}]"
        
        # 如果有描述信息，添加提示符
        has_description = " [i]" if self.description else ""
        
        # 根据层级添加树形前缀
        if level == 0:
            prefix = "| "
        else:
            prefix = "|- " + "  " * (level - 1)
        
        # 高亮显示选中的子进度条
        if is_selected:
            line = f"▶ {prefix}{name}:{has_description}{dependency_info} [{bar}] {percent:.1%} {status}"
        else:
            line = f"  {prefix}{name}:{has_description}{dependency_info} [{bar}] {percent:.1%} {status}"
            
        return line
        
    def _refresh(self, loop=None, data=None):
        """刷新界面"""
        if self.main_widget:
            with self.lock:
                # 更新主进度条
                if self.progress_text:
                    self.progress_text.set_text(self._get_progress_text())
                
                # 重新创建界面以更新子进度条
                new_widget = self._create_widgets()
                self.loop.widget = new_widget
        
        # 继续刷新循环
        if self.loop:
            self.loop.set_alarm_in(self.refresh_rate, self._refresh)
    
    def _handle_input(self, key):
        """处理键盘输入"""
        with self.lock:
            all_sub_progress = self._get_all_sub_progress()
            
            if key == 'up' and self.selected_sub_progress > 0:
                self.selected_sub_progress -= 1
            elif key == 'down' and self.selected_sub_progress < len(all_sub_progress) - 1:
                self.selected_sub_progress += 1
            elif key == 'enter' and self.selected_sub_progress >= 0 and all_sub_progress:
                # 显示子进度条详细信息
                selected_progress, _ = all_sub_progress[self.selected_sub_progress]
                self._show_detail(selected_progress)
            elif key.lower() == 'm':
                # 切换完整进度树显示模式
                self.show_full_tree = not self.show_full_tree
            elif key == 'left':
                # 收起主进度条
                self.main_progress_expanded = False
            elif key == 'right':
                # 展开主进度条
                self.main_progress_expanded = True
            elif key == 'esc':
                # 退出
                self.loop.stop()
    
    def _show_detail(self, sub_progress):
        """显示子进度条的详细信息"""
        # 创建详细信息界面
        detail_items = [
            urwid.Text(('header', "=" * 60)),
            urwid.Text(self._get_progress_text()),
            urwid.Text(('header', "=" * 60)),
            urwid.Divider(),
            urwid.Text(f"子进度条: {sub_progress.title}"),
            urwid.Text(f"UUID: {sub_progress.uuid}"),
            urwid.Text(f"进度: {sub_progress.current}/{sub_progress.total} ({sub_progress.current / sub_progress.total * 100:.1f}%)" 
                      if sub_progress.total > 0 else "进度: N/A"),
            urwid.Text(f"状态: {'已完成' if sub_progress.is_finished else '进行中'}"),
            urwid.Text(f"权重: {sub_progress.weight}"),
        ]
        
        if sub_progress.depends_on:
            dep_names = []
            deps = sub_progress.depends_on if isinstance(sub_progress.depends_on, list) else [sub_progress.depends_on]
            for dep in deps:
                if isinstance(dep, ProgressBar):
                    dep_names.append(dep.title)
                else:
                    # 尝试通过UUID查找依赖任务的名称
                    found = False
                    all_sub_progress = self._get_all_sub_progress()
                    for sp, _ in all_sub_progress:
                        if sp.uuid == dep:
                            dep_names.append(sp.title)
                            found = True
                            break
                    if not found:
                        dep_names.append(str(dep))
            detail_items.append(urwid.Text(f"依赖任务: {', '.join(dep_names)}"))
            
        if sub_progress.replaces:
            # 尝试通过UUID查找替代任务的名称
            replace_name = sub_progress.replaces
            all_sub_progress = self._get_all_sub_progress()
            for sp, _ in all_sub_progress:
                if sp.uuid == sub_progress.replaces:
                    replace_name = sp.title
                    break
            detail_items.append(urwid.Text(f"已完成并替代: {replace_name}"))
        
        if sub_progress.description:
            detail_items.extend([
                urwid.Divider(),
                urwid.Text("描述信息:"),
                urwid.Text(sub_progress.description)
            ])
        
        detail_items.extend([
            urwid.Divider(),
            urwid.Text("按任意键返回进度条视图...")
        ])
        
        detail_pile = urwid.Pile(detail_items)
        detail_widget = urwid.Filler(detail_pile, valign='top')
        
        # 临时替换主界面
        original_widget = self.loop.widget
        self.loop.widget = detail_widget
        
        # 等待按键
        pressed = [False]
        def detail_input(key):
            pressed[0] = True
            
        self.loop.unhandled_input = detail_input
        
        # 等待用户按键
        while not pressed[0]:
            self.loop.draw_screen()
            time.sleep(0.1)
            
        # 恢复原始界面
        self.loop.widget = original_widget
        self.loop.unhandled_input = self._handle_input
    
    def start(self):
        """
        启动进度条界面
        """
        # 创建界面
        main_widget = self._create_widgets()
        
        # 创建主循环
        self.loop = urwid.MainLoop(main_widget,
                                  palette=[
                                      ('header', 'bold', ''),
                                      ('hint', 'light cyan', ''),
                                  ],
                                  unhandled_input=self._handle_input)
        
        # 启动刷新循环
        self.loop.set_alarm_in(self.refresh_rate, self._refresh)
        
        # 启动界面
        self.loop.run()
        
    def stop(self):
        """
        停止进度条界面
        """
        if self.loop:
            self.loop.stop()


# 测试代码
if __name__ == "__main__":
    # 测试SelectBox
    def test_select_box():
        choices = [("选项1", 1), ("选项2", 2), ("选项3", 3)]
        select_box = SelectBox("请选择一个选项", "这是页脚信息", choices)
        result = select_box.start()
        print(f"你选择了: {result}")
    
    # 测试多选SelectBox
    def test_multi_select_box():
        choices = [("选项1", 1), ("选项2", 2), ("选项3", 3)]
        select_box = SelectBox("请选择多个选项", "这是页脚信息", choices, multi=True)
        result = select_box.start()
        print(f"你选择了: {result}")
    
    # 测试ynBox
    def test_yn_box():
        yn_box = ynBox("确认执行操作吗？", "此操作不可撤销")
        result = yn_box.start()
        print(f"用户选择: {'确认' if result else '取消'}")
    
    # 测试FileOpenBox
    def test_file_open_box():
        file_box = FileOpenBox(".", multi=True)
        result = file_box.start()
        print(f"你选择了: {result}")
    
    # 测试ProgressBar
    def test_progress_bar():
        progress = ProgressBar(total=100, title="主任务进度")
        
        # 添加子任务
        sub1 = progress.add_sub_progress("子任务1", 50, "第一个子任务")
        sub2 = progress.add_sub_progress("子任务2", 30, "第二个子任务")
        
        # 在新线程中运行进度条界面
        import threading
        progress_thread = threading.Thread(target=progress.start)
        progress_thread.daemon = True
        progress_thread.start()
        
        # 模拟任务执行
        for i in range(101):
            if i <= 50:
                sub1.update(value=i)
            if i <= 30:
                sub2.update(value=i)
            progress.update(value=i)
            time.sleep(0.1)
        
        progress.finish()
        time.sleep(1)
        progress.stop()
        print("进度条测试完成")
    
    # 运行测试
    print("测试SelectBox:")
    test_select_box()
    
    print("\n测试多选SelectBox:")
    test_multi_select_box()
    
    print("\n测试ynBox:")
    test_yn_box()
    
    print("\n测试FileOpenBox:")
    test_file_open_box()
    
    print("\n测试ProgressBar:")
    test_progress_bar()