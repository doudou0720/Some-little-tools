# Software Installer CLI 工具 (Urwid版本)

这是一个基于urwid库的命令行界面（CLI）软件安装工具，提供了丰富的交互式组件，包括选择框、文件选择器、输入框和进度条等。

与原始版本相比，这个版本使用urwid库重构了界面系统，提供了更好的用户体验和更稳定的跨平台支持。

## 功能组件

### 1. SelectBox（选择框）

提供基于键盘操作的交互式选择界面，支持单选和多选模式。

**特性：**
- 使用上下方向键选择选项
- 回车键确认选择
- 多选模式下使用空格键选择项目
- 支持自定义标题和页脚
- 支持单选和多选模式
- 跨平台支持

**使用示例：**
```python
from urwid_CLI import SelectBox

# 单选模式
choices = [("选项1", 1), ("选项2", 2), ("选项3", 3)]
selected = SelectBox("请选择一个选项", "这是页脚信息", choices).start()
print(f"你选择了: {selected}")

# 多选模式
selected_list = SelectBox("请选择多个选项", "这是页脚信息", choices, multi=True).start()
print(f"你选择了: {selected_list}")
```

### 2. FileOpenBox（文件选择框）

用于浏览和选择文件/文件夹的交互式界面。

**特性：**
- 浏览文件系统并选择文件或文件夹
- 支持多选文件
- 文件夹以蓝色高亮显示
- 支持返回上级目录
- 跨平台支持

**使用示例：**
```python
from urwid_CLI import FileOpenBox

# 单选模式
selected_file = FileOpenBox("/home").start()  # Linux示例路径
# selected_file = FileOpenBox("C:\\").start()  # Windows示例路径
print(f"你选择了: {selected_file}")

# 多选模式
selected_files = FileOpenBox("/home", multi=True).start()
print(f"你选择了这些文件: {selected_files}")
```

### 3. ynBox（确认框）

用于简单的Yes/No选择确认。

**特性：**
- 提供标准的确认对话框
- 返回布尔值表示用户选择
- 跨平台支持

**使用示例：**
```python
from urwid_CLI import ynBox

# 确认框
confirm = ynBox("确认执行操作吗？", "此操作不可撤销").start()
if confirm:
    print("用户选择了确认")
else:
    print("用户选择了取消")
```

### 4. ProgressBar（进度条）

用于显示任务进度，支持主进度条和多个子进度条。

**特性：**
- 主进度条和子进度条
- 自动清除并重绘界面
- 支持通过对象引用操作子进度条
- 跨平台兼容
- 自动处理长文本换行问题
- 支持子进度条添加描述信息
- 支持键盘交互查看详细信息和高亮显示
- 支持使用左右键展开/收起主进度条
- 支持嵌套进度条结构
- 支持权重计算（子进度条对父进度条的贡献）
- 支持任务依赖关系（通过depends_on参数）

**使用示例：**
```python
import time
from urwid_CLI import ProgressBar

# 创建主进度条
progress = ProgressBar(total=100, title="主任务")

# 添加带描述信息的子进度条，支持依赖关系
task1 = progress.add_sub_progress("下载文件", 50, "正在从服务器下载安装文件，这可能需要几分钟时间。")
task2 = progress.add_sub_progress("解压文件", 30, "解压下载的安装包，这可能需要一些时间。", depends_on=task1)

# 添加嵌套子进度条
nested = task1.add_sub_progress("网络连接", 20, "建立网络连接")
download = task1.add_sub_progress("实际下载", 30, "下载文件数据", depends_on=nested)

# 启动进度条界面（在单独的线程中）
import threading
progress_thread = threading.Thread(target=progress.start)
progress_thread.daemon = True
progress_thread.start()

# 模拟任务执行
for i in range(101):
    # 更新嵌套子进度条
    if i <= 20:
        nested.update(value=i)
    elif i <= 50:
        nested.finish()
        download.update(value=i-20)
    else:
        download.finish()
        task1.finish()
        task2.update(value=i-50)
    
    time.sleep(0.1)

# 完成进度条
progress.finish()
time.sleep(1)  # 等待最后一帧绘制完成
progress.stop()
print("所有任务完成!")
```

## 依赖库

- `urwid`：提供终端用户界面支持

## 使用方法

1. 将 `urwid_CLI.py` 文件导入到你的项目中
2. 根据需要使用相应的类创建交互式界面
3. 调用[start()](file:///E:/doudou/github/Some-little-tools/tools/Software_Installer/urwid_CLI.py#L64-L87)方法启动界面并等待用户操作

## 与原始版本的区别

1. **界面库**：使用urwid替代了原始的手动ANSI转义序列绘制方式，提供更稳定和美观的界面
2. **事件处理**：使用urwid的事件系统替代了原始的keyboard库，避免了跨平台兼容性问题
3. **布局管理**：urwid提供了强大的布局管理器，使界面组织更加灵活
4. **输入处理**：urwid内置了跨平台的输入处理机制，无需手动处理不同系统的差异
5. **代码结构**：使用urwid后代码结构更清晰，易于维护和扩展

## 跨平台支持

本工具支持以下平台：
1. **Windows**：完全支持所有功能
2. **Linux**：完全支持所有功能
3. **macOS**：完全支持所有功能

由于使用了urwid库，所有平台的兼容性都由urwid库保证，无需额外的平台特定代码。

## 注意事项

1. ProgressBar需要在单独的线程中运行，以避免阻塞主程序
2. 使用ProgressBar时，需要调用stop()方法来正确退出界面
3. urwid库在某些终端环境下可能显示效果不同，建议在标准终端中使用
4. 与原始版本相比，API基本保持一致，但部分细节可能有所不同