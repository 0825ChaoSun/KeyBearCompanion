# KeyBear Companion

KeyBear Companion 是一个 Windows 桌面小熊键盘伴侣。

它会在桌面上显示一只可爱的小熊和虚拟键盘。当用户按下真实键盘时，虚拟键盘会同步高亮，对应的小熊表情也会随输入状态变化，看起来像小熊正在陪你一起打字。

当前仓库上传的是 `qinliang` 打包版：使用 PySide6 + pynput，并保留托盘图标、贴边吸附、临时隐藏和窗口位置保存等桌面体验。

## 特点

- 悬浮桌面窗口，轻量、不占屏幕
- 虚拟键盘实时高亮
- 小熊根据按键切换站立、按键、开心、惊讶、伤心、睡觉等状态
- 支持保存窗口位置、贴边吸附、系统托盘图标和临时隐藏
- 支持 Windows 运行
- 打包压缩包放在 `qinliang/`
- 不保存、不上传、不记录任何按键内容

## 直接使用

下载：

```text
qinliang/KeyBearCompanion-qinliang-win64.zip
```

解压后运行：

```text
KeyBearCompanion.exe
```

## 本地运行源码

```powershell
python main.py
```

需要安装：

```powershell
pip install -r requirements.txt
```

## 重新打包 qinliang

```powershell
powershell -ExecutionPolicy Bypass -File .\build_qinliang.ps1
```

输出：

```text
qinliang/KeyBearCompanion.exe
qinliang/KeyBearCompanion-qinliang-win64.zip
```

## 隐私说明

程序只实时监听按键用于动画同步，不保存、不上传、不记录任何按键内容。
