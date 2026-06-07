# KeyBear Companion

KeyBear Companion 是一款 Windows 桌面交互式虚拟键盘伴侣。程序通过悬浮小熊与虚拟键盘实时反馈用户的键盘输入状态。

## About

一个基于 Python、PySide6 和 pynput 开发的 Windows 桌面交互式虚拟键盘伴侣。支持实时按键高亮、角色状态反馈、睡眠唤醒、多显示器拖动、托盘管理和窗口位置保存。程序不会记录或上传任何键盘输入内容。

## 下载 Windows EXE

仓库提供可直接运行的 Windows 单文件版本：

```text
release/KeyBearCompanion.exe
```

[下载 KeyBearCompanion.exe](./release/KeyBearCompanion.exe)

下载后直接运行即可，无需安装 Python。Windows 首次运行未知来源程序时可能显示安全提示，请确认文件来自本仓库后再运行。

## 核心功能

- PySide6 无边框透明桌面悬浮窗口
- 使用 pynput 实时监听并高亮常用按键
- 区分左右 Shift、Ctrl 和 Alt
- 根据普通键、特殊键、Backspace 和空闲状态切换小熊图片
- 支持窗口位置保存、贴边吸附和多显示器拖动
- 支持系统托盘、临时隐藏和可选开机启动
- 不保存、不上传、不记录任何按键内容

## 环境要求

- Windows 10 / 11
- Python 3.10 或更高版本

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## 运行源码

```powershell
python main.py
```

右键悬浮窗口可以打开设置或退出程序。

## 项目结构

```text
main.py                         程序入口
app.py                          应用协调、Qt 信号桥与托盘管理
pet_keyboard_window.py          主窗口、拖动、吸附和多显示器逻辑
virtual_keyboard.py             虚拟键盘绘制与按键高亮
keyboard_layout.py              键位布局与热区计算
keyboard_listener.py            全局键盘监听与按键名称标准化
cat_widget.py                   小熊完整状态图显示
animation_controller.py         状态切换与睡眠逻辑
settings_manager.py             设置加载、保存与容错
settings_window.py              设置窗口
asset_generator.py              缺失素材的源码模式回退生成
transparent_processor.py        素材外围背景透明处理
icon_processor.py               应用图标预处理
assets/processed/               运行和打包使用的处理后素材
qa_regression_tests.py          回归测试
QA_TEST_REPORT.md               已验证缺陷与测试记录
KeyBearCompanionQinliang.spec   PyInstaller 打包配置
build_qinliang.ps1              Windows 打包脚本
release/KeyBearCompanion.exe    可直接运行的 Windows 发布版本
```

## 测试

```powershell
python -m unittest qa_regression_tests -v
python main.py --test-keys
```

`--test-keys` 会依次测试虚拟键盘高亮，不会记录输入内容。

## 打包 Windows EXE

打包脚本默认使用：

```text
D:\anaconda3\envs\tf\python.exe
```

首次打包前安装 PyInstaller：

```powershell
D:\anaconda3\envs\tf\python.exe -m pip install pyinstaller
```

执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_qinliang.ps1
```

输出文件位于本地 `dist/` 目录：

```text
dist/KeyBearCompanion.exe
dist/KeyBearCompanion-qinliang-win64.zip
```

`dist/` 是本地打包输出目录，不提交到源码仓库。需要上传的独立 EXE 放在 `release/` 目录中。

## 资源与设置

- 程序运行时优先读取 `assets/processed/` 中的角色和键盘素材。
- 默认设置保存在仓库中的 `settings.json`。
- 用户修改后的设置保存到 `%APPDATA%\KeyBearCompanion\settings.json`。
- 开机启动默认关闭，仅在用户主动开启后写入当前用户注册表。

## 隐私说明

程序仅实时使用按键事件驱动虚拟键盘和小熊状态，不生成按键日志，不保存输入内容，也不上传任何数据。
