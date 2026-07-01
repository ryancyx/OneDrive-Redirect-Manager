# OneDrive Redirector

OneDrive Redirector 是一个面向 Windows 的轻量桌面工具，用来安全管理 `OneDrive` 内真实数据目录与本机原路径之间的 `junction` 映射。

本项目不会让 OneDrive 同步 `symlink` 指向的外部目录。  
本项目采用反向设计：真实数据存放在 OneDrive 内，本机原路径通过 `junction` 指向 OneDrive 内真实目录。

## 当前版本形态

v0.1 当前简化为“单 OneDrive 根目录 + 同步项目列表”模型：

```text
OneDriveRedirector/
├─ data/
│  ├─ project-001/
│  └─ project-002/
└─ config.json
```

软件只保留一个全局 OneDrive 同步根目录设置，例如：

```text
D:\RyanC\OneDrive\OneDriveRedirector
```

主界面围绕同步项目列表展开，每个项目包含：

- `id`
- `name`
- `local_path`
- `cloud_relative_path`
- `enabled`
- `created_at`
- `last_checked_at`

## 项目定位

OneDrive Redirector 不是同步软件，不替代 OneDrive，也不实现双向同步算法。

它只做一件事：把用户原本需要手动执行的：

```cmd
mklink /J "本机原路径" "OneDrive 内真实目录"
```

封装成一个更安全、更可视化、更容易恢复的管理工具。

典型用途：

- 游戏存档同步
- 软件配置目录同步
- 插件配置目录同步
- 轻量数据目录同步

## 与其他方案的区别

- `GameSave Manager`：更偏游戏存档管理，功能更重，不是通用 OneDrive junction 管理器。
- `Link Shell Extension`：能手动创建链接，但不管理项目配置和状态。
- `FreeFileSync / GoodSync / SyncBackPro`：是同步/备份工具，不是原路径重定向管理器。
- `OneDriveBully`：尝试让 OneDrive 扫描外部链接目录，本项目不走这条路线。
- `Syncthing`：是独立同步系统，不依赖 OneDrive。

## 工作方式

主界面项目表格字段：

- 项目 ID
- 名称
- 本地源文件夹路径
- OneDrive 中的路径
- 运行状态

主界面按钮：

- 新建
- 编辑
- 删除
- 刷新
- 设置
- 恢复到本地并取消同步

## 同步处理规则

### 情况 A

本地有数据，云端不存在或为空：

- 直接将本地文件夹移动到 OneDrive 目标路径
- 在原本地路径创建 junction
- 状态变为“已正常同步”

### 情况 B

云端有数据，本地不存在或为空：

- 直接在本地路径创建 junction
- 链接到 OneDrive 目标路径
- 状态变为“已正常同步”

### 情况 C

云端有数据，本地也有数据：

- 显示冲突提示
- 不自动移动文件
- 让用户选择：
  - 备份本地文件夹并使用云端数据
  - 备份云端文件夹并使用本地数据
  - 取消

## 删除与恢复

删除同步项时：

- 默认只删除 `config.json` 中的项目记录
- 默认不删除 OneDrive 中的数据
- 默认不删除本地链接
- 用户可勾选“同时删除 OneDrive 中的目标文件夹”
- 删除云端目标文件夹前会再次确认

恢复到本地并取消同步时：

1. 如果本地路径是 junction，先删除 junction
2. 创建真实本地文件夹
3. 将云端目录内容复制回本地
4. 删除项目配置
5. 默认不删除云端目录

如果本地真实目录已存在且非空，会提示用户先备份。

## 安全承诺

- 不自动扫描游戏目录、`AppData`、`Documents` 或其他隐私目录。
- 所有本地目录都必须由用户显式选择。
- 不允许映射系统目录、用户主目录、OneDrive 根目录。
- 冲突时不会自动覆盖或删除用户数据。
- 所有替换/覆盖操作都会先创建备份。

## 已知限制

- 当前版本仅支持 Windows。
- 当前版本仅支持 `junction`。
- 不提供后台守护、托盘、开机自启。
- 不做实时文件监控。
- 不实现双向同步算法。

## 安装

建议使用 Python 3.11 或更高版本，并在 Windows 10 / 11 上运行。

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行

```bash
python run.py
```

## 检查与测试

```bash
python -m compileall run.py src tests
pytest
```

测试覆盖：

- 路径校验
- 配置读写
- 数据模型序列化
- 状态检测

## 未来计划

- 更完整的恢复向导
- 更细致的状态诊断
- 更完整的 Windows 链接目标检测
- 打包为安装程序
