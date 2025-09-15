# ClassisTime

ClassisTime 是一个基于 PyQt6 的轻量级电子课表应用程序，具有主题更换功能和可扩展的 API，参考了 ClassIsland 的设计风格。

## 特性

- 轻量级设计，内存占用少（小于50MB）
- 快速启动和响应
- 低 CPU 占用
- 可更换主题
- 可扩展的 API
- 支持 ZIP 扩展安装和管理
- 屏幕顶部居中显示当天课表（类似 ClassIsland）
- 悬浮窗只显示课程名称，适用于教室环境
- 支持 Nuitka 编译

## 安装

```bash
pip install -e .
```

## 使用

```bash
python main.py
```

或者

```bash
classistime
```

## 屏幕顶部课表显示

ClassisTime 现在在屏幕顶部居中显示当天的课表信息，类似于 ClassIsland 的设计。这个功能具有以下特点：

- 半透明背景，不影响其他应用程序使用
- 实时高亮当前进行的课程
- 只显示课程名称，适合教室环境使用
- 可通过主界面菜单切换显示/隐藏

## 扩展管理

ClassisTime 支持通过 ZIP 文件安装扩展。扩展可以添加新功能、主题或 UI 组件。

安装扩展：
1. 打开 ClassisTime
2. 进入"扩展"菜单
3. 选择"安装扩展"
4. 选择 ZIP 文件进行安装

有关扩展开发的详细信息，请参阅 [EXTENSIONS.md](EXTENSIONS.md)。

## 开发

请查看 [DEVELOPMENT.md](DEVELOPMENT.md) 获取开发指南。

## 贡献

请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何为项目做贡献。

## 许可证

[MIT](LICENSE)