# PT 种子生成器

这个插件能够监控指定目录下的新增文件，自动为新文件生成种子文件，并可以选择添加到下载器（qBittorrent 或 Transmission）进行做种。同时，插件还能获取并显示 PT 站发布种子时需要填写的信息。

## 功能特性

- 监控指定目录下的新增文件/文件夹
- 自动为新文件/文件夹生成种子文件
- 支持添加到 qBittorrent 或 Transmission 做种
- 自动添加标签
- 支持设置 Tracker 列表
- 定时扫描目录（默认 5 分钟执行一次）
- 实时监控文件变化
- 提取 PT 发布所需信息

## 安装要求

- MoviePilot 环境
- Python 3.7+
- 必要的依赖包：
  - watchdog
  - apscheduler
  - bencodepy
  - qbittorrent-api（如使用 qBittorrent）
  - transmission-rpc（如使用 Transmission）

## 配置说明

### 基本配置

- **启用插件**：开启或关闭插件
- **发送通知**：是否在生成种子时发送通知
- **监控目录**：需要监控的目录路径，插件将监视该目录下的新增文件
- **种子保存目录**：生成的种子文件保存位置
- **执行周期**：定时任务执行间隔，默认为 5 分钟
- **Tracker 列表**：种子的 Tracker 列表，多个 Tracker 使用逗号分隔
- **种子标签**：添加到下载器中的标签，多个标签使用逗号分隔

### 下载器配置

#### qBittorrent

- **qBittorrent 地址**：qBittorrent Web UI 地址，如 `http://localhost:8080`
- **qBittorrent 用户名**：登录用户名
- **qBittorrent 密码**：登录密码

#### Transmission

- **Transmission 主机**：Transmission RPC 主机地址
- **Transmission 端口**：Transmission RPC 端口
- **Transmission 用户名**：登录用户名
- **Transmission 密码**：登录密码

## PT 站点发布信息提取

插件能够从文件/目录名称中提取以下信息：

- 标题
- 分辨率（720p、1080p、2160p、4K 等）
- 音频格式（DTS、TrueHD、Atmos、AC3 等）
- 字幕信息（中文字幕、繁体字幕等）
- 文件大小
- IMDB 链接（从 NFO 文件中提取）

这些信息可以帮助用户在 PT 站点发布种子时快速填写表单。

## 注意事项

- 监控目录必须设置正确且可访问
- 如果使用下载器功能，请确保下载器已正确配置并可访问
- 生成的种子文件将保存在指定的种子保存目录中

## 支持的下载器

- qBittorrent
- Transmission
