# Image_Diff_Tool （见源码内 VERSION 常量）

> **一句话**：图像差异比较器：单图模式看细节、双图模式逐像素比出差异并高亮，支持直接粘贴图片、结果另存。改版前后对截图、确认渲染或压缩有没有真的改动画面时用。基于 OpenCV + PIL，PyQt5 界面。

---

## 目录

- [1. 这是什么](#1-这是什么)
- [2. 零基础入门（5 分钟跑起来）](#2-零基础入门5-分钟跑起来)
- [3. 功能与界面](#3-功能与界面)
- [4. 命令行参数](#4-命令行参数)
- [5. 配置文件与数据](#5-配置文件与数据)
- [6. 工作原理（技术参考）](#6-工作原理技术参考)
- [7. 排错手册](#7-排错手册)
- [8. 常见问题 FAQ](#8-常见问题-faq)
- [9. 目录结构](#9-目录结构)
- [10. 开发与构建](#10-开发与构建)
- [11. 已知限制与安全说明](#11-已知限制与安全说明)
- [12. 许可](#12-许可)

## 1. 这是什么

| 项目 | 说明 |
| --- | --- |
| 程序名 | `Image_Diff_Tool` |
| 当前版本 | （见源码内 VERSION 常量） |
| 主程序 | `Image_Diff_Tool.py` |
| 界面技术 | PyQt5（Qt5 社区绑定） |
| 语言 / 运行平台 | Python 3.10 / Windows |
| 源码规模 | 根目录及子模块共 2 个 .py 文件 |
| 仓库 | https://github.com/duma520/Image_Diff_Tool |

## 2. 零基础入门（5 分钟跑起来）

### 第 1 步：装 Python

1. 打开 <https://www.python.org/downloads/windows/>，下载 Python 3.10 或更新版本。
2. 安装时**务必勾选** `Add python.exe to PATH`（安装向导第一页最下方）。
3. 装完按 `Win + R` 输入 `cmd`，敲 `python --version`，能看到版本号就成功了。

### 第 2 步：拿到源码

- **下载压缩包**：在本仓库 Releases 页下载 `Image_Diff_Tool-*.zip`，解压到任意目录。
- **git 克隆**：`git clone https://github.com/duma520/Image_Diff_Tool.git`

### 第 3 步：装依赖

在源码目录打开命令行，执行：

```
pip install Pillow PyQt5 numpy opencv-python
```

> 清单是从源码的实际 import 汇总出来的；若某个包名不准确，以 pip 报错提示的正确包名为准。

### 第 4 步：启动

```bat
python Image_Diff_Tool.py
```

目录里还带了 `1.bat`，双击等同于上面的命令（前提是 Python 在 PATH 里）。

## 3. 功能与界面

> 本节只列源码里能确认的事实；具体按钮与交互以运行后的界面为准。

| 维度 | 实际情况 |
| --- | --- |
| 界面框架 | PyQt5（Qt5 社区绑定） |
| 是否有 main 入口 | 是，可直接 python 主程序.py 运行 |
| 第三方依赖数 | 4 个 |

## 4. 命令行参数

该程序没有定义命令行参数，直接运行即可（操作都在界面里完成）。

## 5. 配置文件与数据

程序把配置写在自身目录或用户目录下；.gitignore 已排除运行期产生的配置与日志，首次运行会自动生成。

## 6. 工作原理（技术参考）

```
用户操作 → PyQt5 → 业务逻辑 → 结果输出
```

- 入口文件 `Image_Diff_Tool.py`，带 if __name__ == '__main__' 保护。
- 依赖的第三方库：`Pillow`、`PyQt5`、`numpy`、`opencv-python`。
- 全部业务逻辑在仓库内可见，没有编译产物、没有联网下发代码。

## 7. 排错手册

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| python 不是内部或外部命令 | 安装时没勾 PATH | 重装 Python 并勾选 Add python.exe to PATH，或改用 py 命令 |
| ModuleNotFoundError: No module named xxx | 依赖没装 | 按第 3 步 pip install 对应包 |
| 双击 .bat 一闪而过 | 出错后窗口立即关闭 | 用 cmd 进入目录再执行命令，看清报错 |
| 界面显示乱码 | 控制台编码不是 UTF-8 | 先执行 chcp 65001，或用 python -X utf8 主程序.py |
| 杀毒软件拦截 | 未签名脚本被误判 | 加入信任/白名单；本项目只提供源码，可自行审阅 |

## 8. 常见问题 FAQ

**Q1：需要装 Visual Studio 之类的编译工具吗？**
A：不需要。这里只提供 Python 源码，pip 装的是预编译轮子。

**Q2：能在 macOS / Linux 上跑吗？**
A：本项目按 Windows 环境开发与验证；其他系统未测试，可能需要改路径与系统 API 调用。

**Q3：为什么 Releases 里只有源码 zip，没有 exe？**
A：只分发源码，避免二进制被误判；需要 exe 请按第 10 节自行打包。

**Q4：改了代码怎么运行？**
A：直接 python 主程序.py，改动立即生效，无需编译。

**Q5：数据存在哪？会不会被上传？**
A：只存在本机（程序目录或用户目录）。本程序不含上传逻辑。

**Q6：怎么反馈问题？**
A：到 https://github.com/duma520/Image_Diff_Tool/issues 提 Issue，附上报错原文与复现步骤。

## 9. 目录结构

```
Image_Diff_Tool/
0.bat
0_nuitka.bat
1.bat
9.bat
Image_Diff_Tool - 4.0.py
Image_Diff_Tool.py
Image_Diff_Tool.spec
README.md
icon.ico
图像差异比较工具.txt
Image_Diff_Tool\PIL/
Image_Diff_Tool\PyQt5/
Image_Diff_Tool\cv2/
Image_Diff_Tool\numpy/
Image_Diff_Tool\numpy.libs/
Image_Diff_Tool\pypinyin/
Image_Diff_Tool\Image_Diff_Tool.exe
Image_Diff_Tool\_bz2.pyd
Image_Diff_Tool\_ctypes.pyd
Image_Diff_Tool\_decimal.pyd
Image_Diff_Tool\_elementtree.pyd
Image_Diff_Tool\_hashlib.pyd
Image_Diff_Tool\_lzma.pyd
Image_Diff_Tool\_socket.pyd
Image_Diff_Tool\_sqlite3.pyd
Image_Diff_Tool\_ssl.pyd
Image_Diff_Tool\icon.ico
Image_Diff_Tool\image_diff_tool.db
Image_Diff_Tool\libcrypto-1_1.dll
Image_Diff_Tool\libeay32.dll
Image_Diff_Tool\libffi-7.dll
Image_Diff_Tool\libssl-1_1.dll
Image_Diff_Tool\msvcp140.dll
Image_Diff_Tool\msvcp140_1.dll
Image_Diff_Tool\pyexpat.pyd
Image_Diff_Tool\python3.dll
Image_Diff_Tool\python310.dll
Image_Diff_Tool\qt5core.dll
Image_Diff_Tool\qt5dbus.dll
Image_Diff_Tool\qt5gui.dll
Image_Diff_Tool\qt5multimedia.dll
Image_Diff_Tool\qt5network.dll
Image_Diff_Tool\qt5printsupport.dll
Image_Diff_Tool\qt5qml.dll
```

## 10. 开发与构建

- 直接运行（开发态）：`python Image_Diff_Tool.py`
- 语法自检：`python -m py_compile Image_Diff_Tool.py`
- 打包 exe（可选）：装 pyinstaller 后执行 `pyinstaller -F -w Image_Diff_Tool.py`

## 11. 已知限制与安全说明

- 只提供源码，不提供预编译二进制。
- 仓库不含任何凭据；.env / *.pem / *.key / 日志与运行期数据均在 .gitignore 中排除。
- 若程序需要联网，请在源码中确认目标地址后再运行。

## 12. 许可

AGPL-3.0，详见仓库根目录 LICENSE。
