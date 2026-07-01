# 配置格式说明

当前版本只有两类配置。

## 1. 本机设置

位置：

```text
%APPDATA%\OneDriveRedirector\settings.json
```

示例：

```json
{
  "onedrive_root": "D:/ODR_CloudTest/OneDriveRedirector"
}
```

说明：

- `settings.json` 使用 UTF-8 编码
- JSON 写入使用 `ensure_ascii=False`
- 中文路径和中文名称会直接按原文保存

## 2. OneDrive 工作目录配置

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
      "id": "delete-both-test",
      "name": "删除两端入口测试",
      "local_path": "D:/ODR_LocalTest/DeleteBothTest",
      "cloud_relative_path": "data/delete-both-test",
      "created_at": "2026-07-02T10:00:00+08:00",
      "updated_at": "2026-07-02T10:00:00+08:00"
    }
  ]
}
```

说明：

- `config.json` 使用 UTF-8 编码
- JSON 写入使用 `ensure_ascii=False`
- 重新读取后中文项目名称应保持原文不变
