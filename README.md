- # 🎬 MoviePilot-Plugins

MoviePilot 第三方插件库，提供了一系列实用的插件来增强 MoviePilot 的功能。

> ⚠️ 注意：本插件库为个人维护，代码结构参考了其他开源项目。推荐优先使用[官方插件库](https://github.com/jxxghp/MoviePilot-Plugins)。

## 📖 使用说明

**本仓库为第三方插件库，需在 MoviePilot 中添加仓库地址使用**

1. 在 MoviePilot 的插件商店页面，点击"添加第三方仓库"
2. 添加本仓库地址：`https://github.com/yujiajie01/MoviePilot-Plugins`
3. 添加成功后，在插件列表中找到需要的插件
4. 安装并启用插件
5. 根据下方说明配置插件参数

## 📦 插件列表

#### <img src="https://raw.githubusercontent.com/xijin285/MoviePilot-Plugins/refs/heads/main/icons/randompic.png" width="32" style="vertical-align:middle;"> PT 种子生成器 (PTSeeder)

- **版本**: `v1.1.1`
- **作者**: [@NikoYu](https://github.com/yujiajie01)

**简介**：

> 监控目录下新增文件并生成种子，方便 PT 站点发布与做种。

**主要功能**：

- 📂 **目录监控**：自动监控指定目录下的新增文件/文件夹
- 🔄 **种子生成**：为媒体文件自动创建种子文件
- 🌐 **下载器集成**：
  - 支持 qBittorrent 和 Transmission
  - 自动添加种子到下载器做种
  - 自定义种子标签
- 🔍 **PT 信息提取**：自动提取发布种子时需要的信息（分辨率、音频格式、字幕等）
- ⏰ **定时扫描**：定期检查目录变化（默认 5 分钟执行一次）
- ⚡ **实时监控**：通过文件系统事件立即响应新文件
- 🔔 **通知支持**：种子创建成功后发送通知
- 🛠️ **灵活配置**：支持自定义 Tracker、保存路径、执行周期等

**最新更新**：

> `v1.0.0`
> 🎉 首个正式版本：支持监控目录、自动生成种子、qBittorrent 与 Transmission 集成、PT 站发布信息提取

## ⚠️ 注意事项

1. 本插件库中的插件均为个人维护，使用前请仔细阅读说明。
2. 部分插件需要特定权限或配置才能正常使用。
3. 如遇到问题，请先查看插件说明或提交 Issue。
4. 建议定期更新插件以获取最新功能和修复。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进插件。

## 📄 许可证

本项目采用 MIT 许可证，详见[LICENSE](LICENSE)文件。
