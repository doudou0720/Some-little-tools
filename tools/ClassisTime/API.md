# API 扩展文档

ClassisTime 提供了一套可扩展的 API，允许开发者添加新功能和自定义组件。

## 核心 API

### 主题系统

主题系统允许开发者创建和应用自定义主题。

```python
from classistime.themes.theme_manager import ThemeManager

# 创建主题管理器实例
theme_manager = ThemeManager()

# 获取可用主题列表
themes = theme_manager.list_themes()

# 应用主题
theme_manager.apply_theme(widget, "dark")
```

#### 创建自定义主题

要创建自定义主题，请在 `themes` 目录中添加新的主题文件：

```python
# themes/custom_theme.py
CUSTOM_THEME = {
    "name": "自定义主题",
    "primary_color": "#your_primary_color",
    "secondary_color": "#your_secondary_color",
    "background_color": "#your_background_color",
    "text_color": "#your_text_color",
    "accent_color": "#your_accent_color"
}
```

然后在 [theme_manager.py](file:///e:/doudou/github/ClassisTime/classistime/themes/theme_manager.py) 中注册该主题。

### 课表系统

课表系统允许操作课程数据。

#### ScheduleWidget

```python
from classistime.schedule import ScheduleWidget

# 创建课表组件
schedule = ScheduleWidget()

# 设置课程信息
# 参数: 课程名, 教室
cell.set_class("数学", "A101")

# 清除课程信息
cell.clear_class()
```

### 扩展系统

扩展系统允许通过 ZIP 文件安装和管理功能扩展。

```python
from classistime.extensions.extension_manager import ExtensionManager

# 创建扩展管理器实例
ext_manager = ExtensionManager(app)

# 安装扩展
ext_manager.install_extension("path/to/extension.zip")

# 卸载扩展
ext_manager.remove_extension("extension_name")

# 列出所有扩展
extensions = ext_manager.list_extensions()

# 加载扩展模块
module = ext_manager.load_extension_module("extension_name")
```

#### 扩展API

扩展必须实现以下接口：

```python
class Extension:
    def __init__(self, app):
        """初始化扩展"""
        self.app = app  # ClassisTime应用实例
        
    def get_name(self):
        """返回扩展名称"""
        return "Extension Name"
        
    def get_description(self):
        """返回扩展描述"""
        return "Extension Description"
        
    def create_widget(self):
        """创建并返回扩展的UI组件"""
        pass
        
    def on_load(self):
        """扩展加载时调用"""
        pass
        
    def on_unload(self):
        """扩展卸载时调用"""
        pass
```

## 数据结构

### 课程数据

课程数据以如下格式存储：

```json
{
  "period": 0,
  "day": 0,
  "name": "课程名称",
  "room": "教室",
  "teacher": "教师姓名",
  "start_time": "开始时间",
  "end_time": "结束时间"
}
```

### 主题数据

主题数据结构：

```json
{
  "name": "主题名称",
  "primary_color": "#HEX_COLOR",
  "secondary_color": "#HEX_COLOR",
  "background_color": "#HEX_COLOR",
  "text_color": "#HEX_COLOR",
  "accent_color": "#HEX_COLOR"
}
```

### 扩展元数据

扩展元数据结构（manifest.json）：

```json
{
  "name": "extension_name",
  "version": "1.0.0",
  "author": "Author Name",
  "description": "Extension description",
  "entry_point": "main.py",
  "dependencies": []
}
```

## 插件系统

ClassisTime 支持插件扩展。插件应放置在 `plugins` 目录中，并实现以下接口：

```python
# plugins/example_plugin.py
class ExamplePlugin:
    def __init__(self, app):
        self.app = app
    
    def activate(self):
        """激活插件"""
        pass
    
    def deactivate(self):
        """停用插件"""
        pass
```

## 性能考虑

为了保持应用程序的轻量和快速响应，请在开发扩展时注意以下几点：

1. 避免在 UI 线程中执行耗时操作
2. 使用异步操作处理大数据
3. 合理管理内存使用
4. 优化绘图操作

## 最佳实践

1. 遵循现有代码风格
2. 添加适当的错误处理
3. 提供用户友好的界面
4. 确保扩展与主题系统兼容
5. 编写清晰的文档