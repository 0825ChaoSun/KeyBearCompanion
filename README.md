# KeyBear Companion Lightweight

这是 KeyBear Companion 的轻量打包版，使用 Tkinter + pynput，避免 PySide6/Qt 体积过大。

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
