# 开发指南

## 项目结构

```
ClassisTime/
├── classistime/           # 主应用代码
│   ├── app.py            # 应用程序主类
│   ├── schedule.py       # 课表组件
│   ├── themes/           # 主题相关
│   │   ├── theme_manager.py  # 主题管理器
│   ├── extensions/       # 扩展管理
│   │   ├── extension_manager.py  # 扩展管理器
│   ├── ui/               # UI 组件
│   │   ├── current_schedule.py   # 当天课表显示组件
│   └── utils/            # 工具函数
├── example_extension/    # 示例扩展
│   ├── manifest.json     # 扩展元数据
│   └── main.py           # 扩展主文件
├── main.py              # 程序入口点
├── README.md            # 项目说明
├── EXTENSIONS.md        # 扩展开发文档
├── CONTRIBUTING.md      # 贡献指南
├── DEVELOPMENT.md       # 开发指南
├── pyproject.toml       # 项目配置
├── build.py             # Nuitka 编译脚本
└── .github/workflows/   # GitHub Actions 工作流
```

## 环境设置

1. 确保你有 Python 3.12 或更高版本
2. 克隆项目:
   ```bash
   git clone https://github.com/yourusername/ClassisTime.git
   cd ClassisTime
   ```
3. 安装依赖:
   ```bash
   pip install -e .
   ```

## 代码规范

- 遵循 PEP 8 代码规范
- 使用类型提示
- 保持函数简洁，单一职责
- 添加适当的文档字符串

## 架构设计

### 核心组件

1. `ClassisTimeApp`: 应用程序主类，负责初始化和协调各组件
2. `MainWindow`: 主窗口类，包含菜单栏、标签页等
3. `ScheduleWidget`: 课表显示组件
4. `CurrentScheduleWidget`: 屏幕顶部当天课表显示组件（类似 ClassIsland）
5. `ThemeManager`: 主题管理器
6. `ExtensionManager`: 扩展管理器

### 扩展机制

应用程序设计为模块化和可扩展的:

1. **主题扩展**: 在 [themes](classistime/themes) 目录中添加新主题
2. **功能扩展**: 在 [extensions](classistime/extensions) 目录中管理扩展
3. **UI 扩展**: 在 [ui](classistime/ui) 目录中添加新组件
4. **工具扩展**: 在 [utils](classistime/utils) 目录中添加工具函数

## 扩展系统

ClassisTime 现在支持通过 ZIP 文件安装和管理扩展。扩展系统包括：

1. **扩展管理器**: [extension_manager.py](file:///e:/doudou/github/ClassisTime/classistime/extensions/extension_manager.py) 处理扩展的安装、卸载和加载
2. **扩展格式**: 扩展必须包含 [manifest.json](file:///e:/doudou/github/ClassisTime/example_extension/manifest.json) 和入口文件
3. **扩展API**: 提供标准接口供扩展实现

有关扩展开发的详细信息，请参阅 [EXTENSIONS.md](EXTENSIONS.md)。

## 屏幕顶部课表显示

参考 ClassIsland 的设计，ClassisTime 现在在屏幕顶部显示当天课表：

1. **CurrentScheduleWidget**: 实现在 [ui/current_schedule.py](file:///e:/doudou/github/ClassisTime/classistime/ui/current_schedule.py)
2. **特点**:
   - 半透明背景，不影响其他应用程序
   - 居中显示在屏幕顶部
   - 实时高亮当前课程
   - 可通过主程序菜单切换显示/隐藏

## 构建和发布

使用 Nuitka 进行编译:
```bash
python build.py
```

## 性能优化

为确保应用程序轻量和快速响应，我们遵循以下原则:

1. 按需加载模块
2. 避免不必要的计算
3. 使用高效的 PyQt6 组件
4. 优化 UI 更新逻辑
5. 合理使用线程处理耗时操作

## 测试

目前项目使用手动测试。未来计划添加单元测试和集成测试。

## 贡献

请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何为项目做贡献。