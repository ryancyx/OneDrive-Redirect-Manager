# Cloud Redirect Manager ☁️🔗

这是一款基于 Windows 11 操作系统的目录重定向管理工具。可以管理若干条：

```text
本地源文件夹 → Cloud 目标文件夹
```

的目录重定向关系。

软件会在本地原路径创建 Windows `junction` 链接，原软件可继续访问原来的本地路径，而真实数据保存在 Cloud 中，以借助本地云盘客户端 实现文件同步。

```text
原软件访问的本地路径
D:\Games\ExampleGame\SaveData
        ↓ junction 链接
Cloud 中保存真实数据的位置
%CloudDrive%\data\example-game
```

当前稳定版本为 **v1.0.5 绿色版**，主要面向游戏存档、软件配置目录和固定路径数据目录的 Cloud 重定向管理。

---

## 🚀 下载与运行

### Windows 绿色版

> 当前发布形式为 **v1.0.5 绿色版**。解压后即可运行。

在 GitHub Release 页面下载：

```text
CloudRedirectManager_v1.0.5_windows_x64_green.zip
```

使用方法：

1. 下载 `CloudRedirectManager_v1.0.5_windows_x64_green.zip`
2. 解压到任意文件夹
3. 进入解压后的目录
4. 双击运行 `CloudRedirectManager.exe`

注意：请不要只复制单个 `.exe` 文件。需要保留同目录下的 `_internal` 文件夹。


---

## 🎯 项目定位

Cloud Redirect Manager 只专注一个场景：

> 将原本只能保存在固定本地路径的数据，通过 junction 链接重定向到本机 Cloud 同步目录中，从而借助云盘客户端实现云端保存和同步。

软件当前重点支持：

* 单 Cloud 工作目录配置
* 多项目重定向关系管理
* 本地目录与 Cloud 目录状态检查
* junction 创建与删除
* 冲突检测与本地备份
* 恢复到本地并取消同步
* 删除时可选择是否删除 Cloud 目标和本地链接
* 中文路径与中文项目名
* 操作中 busy overlay
* Windows 绿色版封装运行

典型用途包括：

* 游戏存档同步
* 软件配置目录同步
* 项目数据目录同步
* 固定路径应用数据迁移到 Cloud
* 避免手动编写 `mklink /J` 命令

---

## 🖼️ 软件截图

### 主界面

![主界面](docs/images/main-window.png)

### 新建项目

![新建项目](docs/images/create-project.png)

### 删除项目

![删除项目](docs/images/delete-project.png)

### 设置页面

![设置页面](docs/images/settings.png)

---

## ✨ 主要功能

### 1. Cloud 工作目录设置

用户可以选择一个本机云盘同步目录内的文件夹作为软件工作目录，例如：

```text
D:\CloudDrive\Saved\CRM
```

软件会在该目录中维护：

```text
ODR
├─ config.json
└─ data
```

其中：

* `config.json` 保存项目配置
* `data` 保存真实同步数据

---

### 2. 重定向项目管理

每个项目表示一条目录重定向关系：

```text
本地源文件夹 → Cloud 目标文件夹
```

创建项目后，本地源路径会变成 junction 链接，真实数据保存在 Cloud 目标目录中。

项目主要包含：

| 字段 | 含义 |
|---|---|
| ID | 项目的唯一标识，例如 `game-save` |
| 名称 | 给用户查看的项目名称，例如 `游戏存档` |
| 本地源文件夹 | 原软件实际访问的数据路径 |
| Cloud 路径 | Cloud 工作目录下的相对路径，例如 `data/game-save` |

---

### 3. 常见目录状态自动处理

软件可以自动处理多种常见状态：

| 本地目录状态 | Cloud 目标状态 | 软件行为 |
|---|---|---|
| 本地有数据 | Cloud 不存在或为空 | 迁移本地数据到云端并创建 junction |
| 本地为空 | Cloud 有数据 | 删除本地空入口并创建 junction |
| 本地为空 | Cloud 为空 | 直接创建 junction |
| 本地不存在 | Cloud 已存在 | 创建 junction 指向云端 |
| 本地和 Cloud 都有数据 | 进入冲突处理 |

如果本地路径已经是错误 junction、坏 junction，或路径关系存在风险，软件会拒绝自动处理，避免误删数据。

---

### 4. 冲突处理

当本地目录和 Cloud 目标目录中都存在数据时，软件不会直接覆盖任何一边，而是进入冲突处理流程。

当前支持：

* 取消操作
* 备份本地文件夹并使用 Cloud 数据

选择“备份本地文件夹并使用 Cloud 数据”后，软件会在**本地源文件夹旁边**创建一个 `_backup` 目录保存原本的本地数据。例如：

```text
D:\ODR_ManualTest\Local\conflict-backup
        ↓ 备份为
D:\ODR_ManualTest\Local\conflict-backup_backup
```

随后本地源路径会被替换为指向 Cloud 目标目录的 junction。

---

### 5. 删除项目

删除项目时可以选择不同策略：

| 选择 | 结果 |
|---|---|
| 不勾选任何选项 | 只删除配置记录，不删除本地链接，也不删除 Cloud 数据 |
| 删除 Cloud 目标文件夹 | 删除Cloud 真实数据，保留本地 junction |
| 删除本地链接 | 删除本地 junction 入口，保留 Cloud 数据 |
| 两个都勾选 | 先删除本地 junction，再删除 Cloud 目标目录，最后删除配置 |

推荐在彻底移除项目时同时勾选：

```text
删除 Cloud 目标文件夹
删除本地链接
```

这样可以避免留下失效 junction。

---

### 6. 恢复到本地并取消同步

恢复操作会将 Cloud 中的数据复制回本地，并删除本地 junction，使该目录重新成为普通本地文件夹。

该操作会：

1. 删除本地 junction
2. 创建真实本地目录
3. 将 Cloud 目标目录中的数据复制回本地
4. 删除项目配置
5. 默认保留 Cloud 中的数据目录

---

### 7. 操作中提示

对于新建、删除、恢复等可能耗时的操作，软件会显示全局 busy overlay。

该提示使用无限 busy 指示器，不显示虚假的百分比进度。操作期间主界面会暂时不可交互，避免重复提交。

---

## 🛠️ 技术栈

| 模块 | 技术 |
|---|---|
| 开发语言 | Python |
| 桌面界面 | PySide6 + QML |
| 链接机制 | Windows junction |
| 配置格式 | JSON |
| 测试工具 | pytest |
| 打包工具 | PyInstaller |
| 运行平台 | Windows 10 / Windows 11 |

---

## 🧱 软件架构

Cloud Redirect Manager 采用轻量分层结构，将文件系统逻辑、项目配置和 QML 界面分离。

```text
CloudRedirectManager/
├─ run.py
├─ assets/
│  └─ CloudRedirectManager.ico
├─ src/
│  └─ cloud_redirector/
│     ├─ app.py
│     ├─ core/
│     │  ├─ project_service.py
│     │  ├─ project_store.py
│     │  ├─ settings_store.py
│     │  ├─ file_ops.py
│     │  ├─ junction_ops.py
│     │  └─ models.py
│     └─ ui/
│        ├─ controller.py
│        ├─ main_window.py
│        └─ qml/
├─ tests/
├─ docs/
└─ dist/
```

核心逻辑集中在 `core/` 中，界面交互由 `ui/` 和 QML 文件负责。

---

## ⚡ 从源码运行

本教程面向开发者。

克隆项目：

```powershell
git clone https://github.com/ryancyx/CloudRedirectManager.gitshell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

运行软件：

```powershell
python run.py
```

运行测试：

```powershell
python -m compileall run.py src tests
python -m pytest
```

---

## 📌 基本使用流程

建议按以下流程使用：

```text
设置 Cloud 工作目录 → 新建项目 → 创建 junction → 使用原软件 → 由云盘客户端同步数据
```

### 1. 设置 Cloud 工作目录

在设置页面中选择一个 Cloud 工作目录。

### 2. 新建项目

填写项目 ID、名称、本地源文件夹和 Cloud 路径。

### 3. 创建 junction

确认后，软件会根据本地和云端目录状态自动处理，并创建 junction。

### 4. 使用原软件

原软件继续访问原本的本地路径，不需要修改软件自身设置。

### 5. 删除或恢复

后续可以根据需要删除项目、保留 Cloud 数据，或恢复到本地并取消同步。

---

## 🧪 案例展示

### 游戏存档同步

假设某游戏存档位于：

```text
D:\Games\ExampleGame\SaveData
```

希望同步到 Cloud：

```text
D:\CloudDrive\Saved\CRM\data\example-game
```

使用本软件创建项目后：

```text
D:\Games\ExampleGame\SaveData
        ↓ junction
D:\CloudDrive\Saved\CRM\data\example-game
```

游戏仍然读写原路径，而真实数据由 Cloud 保存和同步。

---

## 📦 当前版本

当前稳定版本：**v1.0.5 绿色版**

### v1.0.5 绿色版已完成功能

* Cloud 工作目录设置
* 项目新建、编辑、删除和刷新
* 本地路径与 Cloud 路径状态检查
* junction 创建与删除
* 本地数据迁移到 Cloud
* Cloud 数据接管到本地路径
* 本地空目录与云端空目录直接建链
* 本地不存在时接管云端目录
* 冲突检测与本地 `_backup` 备份
* 恢复到本地并取消同步
* 四种删除组合
* 中文路径与中文项目名
* 真实 Cloud 目录删除 fallback
* 操作中 busy overlay
* Windows 绿色版封装

---

## ✅ 人工验收记录

v1.0.5 绿色版发布前已完成以下人工测试：

* 本地有数据，云端不存在
* 本地为空，Cloud 有数据
* 本地为空，Cloud 为空
* 本地不存在，Cloud 有数据
* 冲突时取消
* 冲突时备份本地并使用云端
* 恢复到本地并取消同步
* 只删除配置
* 只删除 Cloud 目标文件夹
* 只删除本地链接
* 同时删除 Cloud 目标文件夹和本地链接
* 中文项目名和中文路径
* 真实 Cloud 路径删除
* busy overlay 显示与自动退出
* PyInstaller one-dir 绿色版运行

---

## ⚠️ 当前限制

当前版本仍是轻量级目录重定向工具，主要限制包括：

* 当前仅面向 Windows 平台
* 当前仅使用 Windows junction 机制
* 当前不提供跨平台同步能力
* 当前不直接管理 云盘客户端登录和同步状态
* 当前不支持任务队列和批量自动修复
* 删除 Cloud 目标文件夹前仍需用户自行确认数据是否需要保留
* 如果 云盘客户端正在同步或文件被占用，部分操作可能需要等待

---

## 🧹 卸载方式

本软件是绿色版，卸载时直接删除软件文件夹即可。

如果想清理本机设置和日志，可以删除：

```text
%APPDATA%\CloudRedirectManager
```

如果想删除 Cloud 工作目录中的配置和数据，需要手动删除曾经选择的 Cloud 工作目录，例如：

```text
D:\CloudDrive\Saved\CRM
```

删除 Cloud 工作目录前请确认其中数据不再需要。

---

## 🗺️ 后续计划

后续版本可能继续扩展：

* 日志查看器
* 坏 junction 检测
* 一键清理失效项目
* 更详细的错误修复建议
* 更完善的新手引导
* 更正式的安装包
* 便携模式配置选项

---

## 📚 项目用途

本项目可用于：

* 游戏存档 Cloud 同步
* 软件配置目录同步
* 固定路径数据目录迁移
* Windows junction 图形化管理
* Python + QML 桌面软件开发实践
* 软件著作权材料展示
* 轻量级工具软件原型验证

---

## 👤 开发相关

* 开发者：Developed by [@ryancyx](https://github.com/ryancyx)
* 项目类型：Windows 桌面工具 / Cloud 目录重定向管理器

---

## 📄 License

MIT License
