# 配置格式

## 本机设置

位置：

```text
%APPDATA%\OneDriveRedirector\settings.json
```

示例：

```json
{
  "onedrive_root": "D:/OneDrive/OneDriveRedirector"
}
```

## OneDrive 工作目录

目录结构：

```text
OneDriveRedirector/
  config.json
  data/
  backups/
```

`config.json` 示例：

```json
{
  "version": 1,
  "projects": [
    {
      "id": "fireaxe",
      "name": "FireAxe 存档",
      "local_path": "D:/Games/FireAxe/backups",
      "cloud_relative_path": "data/fireaxe",
      "created_at": "2026-07-01T22:00:00+08:00",
      "updated_at": "2026-07-01T22:00:00+08:00"
    }
  ]
}
```
