# 配置格式说明

## OneDrive 根目录结构

当前简化版 v0.1 使用单一 OneDrive 根目录：

```text
OneDriveRedirector/
├─ config.json
└─ data/
   ├─ project-001/
   └─ project-002/
```

其中：

- `config.json` 保存同步项目列表
- `data/` 保存每个项目在 OneDrive 中的真实数据目录

## `config.json`

位置：

```text
<OneDriveRoot>/OneDriveRedirector/config.json
```

示例：

```json
{
  "version": 1,
  "projects": [
    {
      "id": "fireaxe-backup",
      "name": "FireAxe Backup",
      "local_path": "D:/Games/FireAxe/backups",
      "cloud_relative_path": "data/fireaxe-backup",
      "enabled": true,
      "created_at": "2026-07-01T22:30:00+08:00",
      "last_checked_at": "2026-07-01T22:35:00+08:00"
    }
  ]
}
```

规则：

- `id` 必须唯一
- `local_path` 记录当前电脑上的本地源文件夹路径
- `cloud_relative_path` 必须是相对路径
- 路径分隔符统一使用 `/`
- `cloud_relative_path` 必须位于 `data/` 下
- 不允许绝对路径、盘符、`.`、`..`

## `settings.json`

位置：

```text
%APPDATA%/OneDriveRedirector/settings.json
```

示例：

```json
{
  "onedrive_root": "D:/RyanC/OneDrive/OneDriveRedirector"
}
```

规则：

- `onedrive_root` 保存当前软件使用的唯一 OneDrive 根目录
- 本机设置不保存在 OneDrive 中
- 日志默认写入 `%APPDATA%/OneDriveRedirector/logs/`
