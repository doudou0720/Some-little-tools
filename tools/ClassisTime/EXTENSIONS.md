# 扩展系统文档

ClassisTime 提供了一个灵活的扩展系统，允许开发者通过 ZIP 文件安装和管理扩展。

## 扩展结构

一个有效的扩展应该包含以下文件：

```
extension_name/
├── manifest.json     # 扩展元数据（必需）
├── main.py          # 扩展主入口（必需）
└── other_files...   # 其他资源文件（可选）
```

### manifest.json

这是扩展的元数据文件，必须包含以下信息：

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

字段说明：
- `name`: 扩展名称（必须唯一）
- `version`: 版本号
- `author`: 作者
- `description`: 描述
- `entry_point`: 入口文件
- `dependencies`: 依赖列表

### main.py

这是扩展的主入口文件，必须包含一个扩展类。示例：

```python
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class ExampleExtension:
    def __init__(self, app):
        self.app = app  # ClassisTime应用实例
        self.widget = None
        
    def get_name(self):
        return "扩展名称"
        
    def get_description(self):
        return "扩展描述"
        
    def create_widget(self):
        """创建并返回扩展的UI组件"""
        if self.widget is None:
            self.widget = QWidget()
            layout = QVBoxLayout()
            # 添加UI元素
            self.widget.setLayout(layout)
        return self.widget
        
    def on_load(self):
        """扩展加载时调用"""
        pass
        
    def on_unload(self):
        """扩展卸载时调用"""
        pass
```

## 扩展管理API

### ExtensionManager

扩展管理器负责扩展的安装、卸载和加载。

```python
from classistime.extensions.extension_manager import ExtensionManager

# 创建扩展管理器
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

## 扩展开发指南

1. 创建扩展目录结构
2. 编写 [manifest.json](file:///e:/doudou/github/ClassisTime/example_extension/manifest.json) 文件
3. 实现 [main.py](file:///e:/doudou/github/ClassisTime/example_extension/main.py) 中的扩展类
4. 将扩展目录打包为 ZIP 文件
5. 通过 ClassisTime 的扩展管理界面安装

## 扩展分发

扩展以 ZIP 文件格式分发。用户可以通过以下方式安装：

1. 打开 ClassisTime
2. 进入"扩展"菜单
3. 选择"安装扩展"
4. 选择 ZIP 文件进行安装

## 注意事项

1. 扩展会安装到用户目录下的 `.classistime/extensions/` 文件夹中
2. 同名扩展会被新版本覆盖
3. 删除扩展会完全移除其文件
4. 扩展应该处理好异常情况，避免影响主程序运行