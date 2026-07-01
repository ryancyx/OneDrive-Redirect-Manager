# OneDrive 目录重定向管理器

OneDrive 目录重定向管理器是一个面向 Windows 的轻量桌面工具，用来管理“本地源文件夹 -> OneDrive 目标文件夹”的目录重定向关系。

它不是文件同步平台，也不是多设备配置中心。它做的事情很简单：

- 真实数据放在 OneDrive 工作目录中
- 原软件继续访问原本的本地路径
- 软件在原路径创建 Windows junction
- 原软件看起来仍然访问旧路径，实际读写的是 OneDrive 中的数据

## 配置位置

本机设置保存在：

```text
%APPDATA%\OneDriveRedirector\settings.json
```

OneDrive 工作目录结构：

```text
OneDriveRedirector/
  config.json
  data/
  backups/
```

说明：

- `settings.json` 使用 UTF-8 编码保存
- `config.json` 使用 UTF-8 编码保存
- JSON 写入时使用 `ensure_ascii=False`，会直接保留中文，不会转成 `\uXXXX`

## 运行

在仓库根目录执行：

```powershell
python run.py
```

## 检查命令

```powershell
python -m compileall run.py src tests
pytest
python run.py
```
