# KeyBear Companion Lightweight

KeyBear Companion 是一个轻量级 Windows 桌面小熊键盘伴侣。

它会在桌面上显示一只可爱的小熊和虚拟键盘。当用户按下真实键盘时，虚拟键盘会同步高亮，对应的小熊表情也会随输入状态变化，看起来像小熊正在陪你一起打字。

这个仓库当前上传的是轻量打包版：使用 Tkinter + pynput，避免 PySide6/Qt 带来的大体积依赖，更适合直接下载运行。

## 特点

- 悬浮桌面窗口，轻量、不占屏幕
- 虚拟键盘实时高亮
- 小熊根据按键切换站立、按键、开心、惊讶、伤心、睡觉等状态
- 支持 Windows 运行
- 打包体积更小，压缩包放在 `qinliang/`
- 不保存、不上传、不记录任何按键内容

## 直接使用

下载并解压：

```text
qinliang/KeyBearCompanion-qinliang-win64.zip
```

运行：

```text
KeyBearCompanion/KeyBearCompanion.exe
```

## 本地运行源码

```powershell
python main_tk_light.py
```

需要安装：

```powershell
pip install pynput
```

## 重新打包

本机当前脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_tk_qin.ps1
```

输出：

```text
KeyBearCompanion.exe
qinliang/KeyBearCompanion-qinliang-win64.zip
```

## 隐私说明

程序只实时监听按键用于动画同步，不保存、不上传、不记录任何按键内容。
