# Software Installer CLI 工具

这是一个基于命令行界面（CLI）的软件安装工具，提供了丰富的交互式组件，包括选择框、文件选择器、输入框和进度条等。

## 功能组件

### 1. SelectBox（选择框）

提供基于键盘操作的交互式选择界面，支持单选和多选模式。

**特性：**
- 使用上下方向键选择选项
- 回车键确认选择
- 多选模式下使用空格键选择项目
- 支持自定义标题和页脚
- 支持单选和多选模式
- 跨平台支持（Windows/Linux/Termux）

**使用示例：**
```python
from CLI import SelectBox

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
- 可切换磁盘驱动器（仅Windows）
- 文件夹以蓝色高亮显示
- 支持返回上级目录
- 跨平台支持（Windows/Linux/Termux）

**使用示例：**
```python
from CLI import FileOpenBox

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
from CLI import ynBox

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
- 线程安全操作
- 自动清除并重绘界面
- 支持通过对象引用操作子进度条
- 跨平台兼容
- 自动处理长文本换行问题
- 支持子进度条添加描述信息
- 支持键盘交互查看详细信息和高亮显示
- 支持使用左右键展开/收起主进度条
- 支持嵌套进度条结构
- 支持权重计算（子进度条对父进度条的贡献）
- 显示和按键处理分离线程
- 与主程序分离线程
- 支持任务依赖关系（通过depends_on参数）

**使用示例：**
```python
import time
from CLI import ProgressBar

# 创建主进度条
progress = ProgressBar(total=100, title="主任务")

# 预留显示空间
print("\n" * 10)
progress._draw_main_progress()

# 添加带描述信息的子进度条，支持依赖关系
task1 = progress.add_sub_progress("下载文件", 50, "正在从服务器下载安装文件，这可能需要几分钟时间。")
task2 = progress.add_sub_progress("解压文件", 30, "解压下载的安装包，这可能需要一些时间。", depends_on=task1)

# 添加嵌套子进度条
nested = task1.add_sub_progress("网络连接", 20, "建立网络连接")
download = task1.add_sub_progress("实际下载", 30, "下载文件数据", depends_on=nested)

# 启用交互模式（允许用户通过键盘选择和查看详细信息）
progress.enable_interaction()

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
progress.disable_interaction()
print("所有任务完成!")
```

### 5. TerminalInput（终端输入处理类）

用于在无root的Linux/Termux环境下替代keyboard库的输入处理类。

**特性：**
- 在无root权限的Linux/Termux环境下提供键盘输入支持
- 自动检测系统平台并选择合适的输入处理方式
- 提供与keyboard库类似的API接口
- 支持特殊按键（方向键、回车、空格等）检测

**注意：** 这个类是为内部使用而设计的，通常不需要直接使用它。

## 依赖库

- `colorama`：提供终端颜色支持
- `keyboard`：处理键盘输入事件（仅Windows系统需要）

## 使用方法

1. 将 `CLI.py` 文件导入到你的项目中
2. 根据需要使用相应的类创建交互式界面
3. 调用[start()](file:///e:/doudou/github/Some-little-tools/tools/Software_Installer/CLI.py#L119-L137)方法启动界面并等待用户操作

## 跨平台支持

本工具支持以下平台：
1. **Windows**：完全支持所有功能，使用原生[keyboard](file:///e:/doudou/github/Some-little-tools/tools/Software_Installer/CLI.py#L2-L2)库处理键盘输入
2. **Linux（有root权限）**：完全支持所有功能，使用[keyboard](file:///e:/doudou/github/Some-little-tools/tools/Software_Installer/CLI.py#L2-L2)库处理键盘输入
3. **Linux/Termux（无root权限）**：支持所有功能，使用自定义的TerminalInput类处理键盘输入

在无root权限的Linux/Termux环境下，工具会自动切换到自定义的输入处理机制，无需额外配置。

## 注意事项

1. 在使用这些组件时，确保终端支持ANSI转义序列以获得最佳显示效果
2. FileOpenBox 和 SelectBox 会捕获全局键盘事件，请确保在适当的时候结束程序以释放键盘钩子
3. ProgressBar 在多线程环境中使用时具有线程安全性
4. 在Linux/Termux环境下，某些特殊按键可能无法识别，建议使用基本方向键、回车和空格键
5. 程序退出时会自动清理键盘钩子，但如果程序异常终止可能需要手动重置终端设置
6. 进度条会自动处理长标题和子任务名称，超过长度会自动截断并添加省略号
7. 子进度条支持添加描述信息，用户可以通过键盘交互查看详细信息
8. 使用交互式进度条时，通过上下方向键选择子进度条，按回车键查看详细信息
9. 可以使用左键(←)收起主进度条以节省屏幕空间，使用右键(→)重新展开主进度条
10. 进度条支持嵌套结构，可以通过add_sub_progress方法添加子进度条
11. 子进度条会自动更新父进度条，根据权重计算整体进度
12. 显示、按键处理和主程序分别运行在不同线程中，提高响应性
13. 依赖关系通过depends_on参数指定，支持单个或多个依赖（列表形式）
14. 依赖关系可以使用进度条对象引用或UUID字符串