# OneDrive 目录重定向管理器

这是一个面向 Windows 的轻量桌面工具，用来管理“本地源文件夹 -> OneDrive 目标文件夹”的目录重定向。

核心思路很简单：

- 真实数据存放在 OneDrive 工作目录中
- 原本的软件仍然访问本地旧路径
- 软件在旧路径创建 Windows junction
- 原软件看起来还在访问旧路径，实际读写的是 OneDrive 中的数据

这不是同步平台，也不是多设备配置系统。当前版本只保留一个 OneDrive 根目录和一张同步项目列表。

## 目录结构

```text
run.py
src/
  onedrive_redirector/
    __init__.py
    app.py
    main_window.py
    dialogs.py
    models.py
    settings_store.py
    project_store.py
    status_checker.py
    path_utils.py
    file_ops.py
    junction_ops.py
    logger_setup.py
tests/
docs/
```

## 配置位置

本机设置：

```text
%APPDATA%\OneDriveRedirector\settings.json
```

内容示例：

```json
{
  "onedrive_root": "D:/OneDrive/OneDriveRedirector"
}
```

OneDrive 工作目录：

```text
OneDriveRedirector/
  config.json
  data/
  backups/
```

## 主界面

主界面是一张表格，列为：

1. 项目 ID
2. 名称
3. 本地源文件夹路径
4. OneDrive 中的路径
5. 运行状态

按钮：

1. 新建
2. 编辑
3. 删除
4. 刷新
5. 设置
6. 恢复到本地并取消同步

## 测试与运行

```powershell
python -m compileall run.py src tests
pytest
python run.py
```
