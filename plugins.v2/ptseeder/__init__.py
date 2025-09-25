import os
import re
import time
import json
import hashlib
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import bencodepy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

try:
    import qbittorrentapi
except ImportError:
    qbittorrentapi = None

try:
    from transmission_rpc import Client as TransmissionClient
except ImportError:
    TransmissionClient = None

from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import NotificationType


class PTSeeder(_PluginBase):
    # 插件名称
    plugin_name = "PT种子生成器"
    # 插件描述
    plugin_desc = "監控目錄下新增文件並生成種子，方便PT站點發布與做種"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/yujiajie01/MoviePilot-Plugins/refs/heads/main/icons/randompic.png"
    # 插件版本
    plugin_version = "1.1.0"
    # 插件作者
    plugin_author = "NikoYu"
    # 作者主页
    author_url = "https://github.com/yujiajie01"
    # 插件配置项ID前缀
    plugin_config_prefix = "ptseeder_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 1

    # 私有属性 - 基础设置
    _enabled: bool = False
    _cron: str = "*/5 * * * *"  # 默认每5分钟执行一次
    _onlyonce: bool = False
    _notify: bool = True
    _scheduler = None
    _observer = None
    _running: bool = False
    _lock = None
    
    # 目录设置
    _monitor_dir: str = ""
    _torrent_save_dir: str = ""
    _exclude_dirs: str = "@eaDir,@Recycle,.DS_Store"  # 排除目录
    _include_exts: str = ".mkv,.mp4,.avi,.rmvb,.mov,.ts,.m2ts"  # 包含扩展名
    _min_file_size: int = 100  # 最小文件大小(MB)
    
    # 种子设置
    _trackers: str = ""
    _piece_size: int = 1  # 分片大小(MB), 0表示自动
    _private_torrent: bool = True  # 私有种子
    _source: str = ""  # 种子来源标识
    _comment: str = ""  # 种子注释
    
    # 下载器设置
    _client_type: str = "qbittorrent"
    _add_to_client: bool = True  # 是否添加到下载器
    _auto_start: bool = False  # 自动开始下载
    _skip_check: bool = True  # 跳过校验
    
    # qBittorrent 设置
    _qb_url: str = "http://localhost:8080"
    _qb_username: str = "admin"
    _qb_password: str = "adminadmin"
    _qb_category: str = ""  # qB 分类
    _qb_save_path: str = ""  # qB 保存路径
    
    # Transmission 设置
    _tr_host: str = "localhost"
    _tr_port: int = 9091
    _tr_username: str = ""
    _tr_password: str = ""
    _tr_download_dir: str = ""  # TR 下载目录
    
    # 种子标签和高级设置
    _tags: str = "PT,AutoSeed"  # 默认标签
    _upload_limit: int = 0  # 上传限速 (KB/s), 0表示无限制
    _download_limit: int = 0  # 下载限速 (KB/s), 0表示无限制
    _ratio_limit: float = 0.0  # 分享率限制, 0表示无限制
    _seed_time_limit: int = 0  # 做种时间限制(小时), 0表示无限制
    
    # PT信息提取设置
    _extract_info: bool = True  # 提取PT发布信息
    _copy_to_clipboard: bool = False  # 复制信息到剪贴板
    _generate_nfo: bool = False  # 生成NFO文件
    
    # 通知设置
    _notify_on_error: bool = True  # 错误通知
    _notify_on_success: bool = True  # 成功通知
    _notify_on_duplicate: bool = False  # 重复通知

    def init_plugin(self, config: Optional[dict] = None):
        """初始化插件"""
        self.stop_service()
        
        # 初始化锁
        self._lock = threading.Lock()
        
        # 加载配置
        if config:
            self._load_config(config)
        
        # 设置默认值
        self._set_defaults()
        
        # 更新配置
        self._update_config()
        
        # 处理立即运行一次的情况
        if self._onlyonce:
            self._run_onlyonce()
        
        # 启动服务
        if self._enabled:
            self._start_services()

    def _load_config(self, config: dict):
        """加载配置"""
        # 基础设置
        self._enabled = config.get("enabled", False)
        self._cron = config.get("cron", "*/5 * * * *")
        self._onlyonce = config.get("onlyonce", False)
        self._notify = config.get("notify", True)
        
        # 目录设置
        self._monitor_dir = config.get("monitor_dir", "")
        self._torrent_save_dir = config.get("torrent_save_dir", "")
        self._exclude_dirs = config.get("exclude_dirs", "@eaDir,@Recycle,.DS_Store")
        self._include_exts = config.get("include_exts", ".mkv,.mp4,.avi,.rmvb,.mov,.ts,.m2ts")
        self._min_file_size = config.get("min_file_size", 100)
        
        # 种子设置
        self._trackers = config.get("trackers", "")
        self._piece_size = config.get("piece_size", 1)
        self._private_torrent = config.get("private_torrent", True)
        self._source = config.get("source", "")
        self._comment = config.get("comment", "")
        
        # 下载器设置
        self._client_type = config.get("client_type", "qbittorrent")
        self._add_to_client = config.get("add_to_client", True)
        self._auto_start = config.get("auto_start", False)
        self._skip_check = config.get("skip_check", True)
        
        # qBittorrent
        self._qb_url = config.get("qb_url", "http://localhost:8080")
        self._qb_username = config.get("qb_username", "admin")
        self._qb_password = config.get("qb_password", "adminadmin")
        self._qb_category = config.get("qb_category", "")
        self._qb_save_path = config.get("qb_save_path", "")
        
        # Transmission
        self._tr_host = config.get("tr_host", "localhost")
        self._tr_port = config.get("tr_port", 9091)
        self._tr_username = config.get("tr_username", "")
        self._tr_password = config.get("tr_password", "")
        self._tr_download_dir = config.get("tr_download_dir", "")
        
        # 高级设置
        self._tags = config.get("tags", "PT,AutoSeed")
        self._upload_limit = config.get("upload_limit", 0)
        self._download_limit = config.get("download_limit", 0)
        self._ratio_limit = config.get("ratio_limit", 0.0)
        self._seed_time_limit = config.get("seed_time_limit", 0)
        
        # PT信息
        self._extract_info = config.get("extract_info", True)
        self._copy_to_clipboard = config.get("copy_to_clipboard", False)
        self._generate_nfo = config.get("generate_nfo", False)
        
        # 通知设置
        self._notify_on_error = config.get("notify_on_error", True)
        self._notify_on_success = config.get("notify_on_success", True)
        self._notify_on_duplicate = config.get("notify_on_duplicate", False)

    def _set_defaults(self):
        """设置默认值"""
        if not self._torrent_save_dir and self._monitor_dir:
            self._torrent_save_dir = os.path.join(self._monitor_dir, "torrents")
            
        if not self._qb_save_path and self._monitor_dir:
            self._qb_save_path = self._monitor_dir
            
        if not self._tr_download_dir and self._monitor_dir:
            self._tr_download_dir = self._monitor_dir

    def get_state(self) -> bool:
        """获取插件状态"""
        return self._enabled

    def _update_config(self):
        """更新配置"""
        config_data = {
            # 基础设置
            "enabled": self._enabled,
            "cron": self._cron,
            "onlyonce": self._onlyonce,
            "notify": self._notify,
            
            # 目录设置
            "monitor_dir": self._monitor_dir,
            "torrent_save_dir": self._torrent_save_dir,
            "exclude_dirs": self._exclude_dirs,
            "include_exts": self._include_exts,
            "min_file_size": self._min_file_size,
            
            # 种子设置
            "trackers": self._trackers,
            "piece_size": self._piece_size,
            "private_torrent": self._private_torrent,
            "source": self._source,
            "comment": self._comment,
            
            # 下载器设置
            "client_type": self._client_type,
            "add_to_client": self._add_to_client,
            "auto_start": self._auto_start,
            "skip_check": self._skip_check,
            
            # qBittorrent
            "qb_url": self._qb_url,
            "qb_username": self._qb_username,
            "qb_password": self._qb_password,
            "qb_category": self._qb_category,
            "qb_save_path": self._qb_save_path,
            
            # Transmission
            "tr_host": self._tr_host,
            "tr_port": self._tr_port,
            "tr_username": self._tr_username,
            "tr_password": self._tr_password,
            "tr_download_dir": self._tr_download_dir,
            
            # 高级设置
            "tags": self._tags,
            "upload_limit": self._upload_limit,
            "download_limit": self._download_limit,
            "ratio_limit": self._ratio_limit,
            "seed_time_limit": self._seed_time_limit,
            
            # PT信息
            "extract_info": self._extract_info,
            "copy_to_clipboard": self._copy_to_clipboard,
            "generate_nfo": self._generate_nfo,
            
            # 通知设置
            "notify_on_error": self._notify_on_error,
            "notify_on_success": self._notify_on_success,
            "notify_on_duplicate": self._notify_on_duplicate
        }
        self.update_config(config_data)

    def _run_onlyonce(self):
        """立即运行一次"""
        try:
            if not self._scheduler:
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            job_name = f"{self.plugin_name}服務_onlyonce"
            if self._scheduler.get_job(job_name):
                self._scheduler.remove_job(job_name)
            logger.info(f"{self.plugin_name} 服務啟動，立即運行一次")
            self._scheduler.add_job(func=self.run_job, trigger='date',
                                   run_date=datetime.now(),
                                   name=job_name, id=job_name)
            if not self._scheduler.running:
                self._scheduler.start()
            self._onlyonce = False
            self._update_config()
        except Exception as e:
            logger.error(f"啟動一次性 {self.plugin_name} 任務失敗: {str(e)}")

    def _start_services(self):
        """啟動服務"""
        # 啟動文件監控
        if self._monitor_dir and os.path.isdir(self._monitor_dir):
            self._start_file_monitor()
        else:
            logger.warning(f"{self.plugin_name} 監控目錄不存在或未設置: {self._monitor_dir}")

    def get_command(self) -> List[Dict[str, Any]]:
        """返回命令列表"""
        return [
            {
                "cmd": "/ptseeder",
                "desc": "手動掃描目錄並生成種子",
                "category": "PT工具",
                "data": {}
            },
            {
                "cmd": "/ptseeder_info",
                "desc": "獲取PT發布信息",
                "category": "PT工具", 
                "data": {"action": "get_info"}
            },
            {
                "cmd": "/ptseeder_status",
                "desc": "查看插件狀態",
                "category": "PT工具",
                "data": {"action": "status"}
            }
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        """注册API接口"""
        return [
            {
                "path": "/run",
                "endpoint": self.api_run,
                "methods": ["GET"],
                "summary": "立即運行種子生成任務"
            },
            {
                "path": "/generate",
                "endpoint": self.api_generate_torrent,
                "methods": ["POST"],
                "summary": "為指定路徑生成種子文件"
            },
            {
                "path": "/info",
                "endpoint": self.api_get_pt_info,
                "methods": ["POST"],
                "summary": "獲取PT發布信息"
            },
            {
                "path": "/status",
                "endpoint": self.api_get_status,
                "methods": ["GET"],
                "summary": "獲取插件狀態"
            }
        ]

    def api_run(self):
        """API: 立即运行种子生成任务"""
        self.run_job()
        return {"code": 0, "message": "已開始掃描目錄並生成種子"}

    def api_generate_torrent(self, path: str):
        """API: 为指定路径生成种子"""
        if not path:
            return {"code": 1, "message": "請提供路徑參數"}
            
        if not os.path.exists(path):
            return {"code": 1, "message": f"路徑不存在: {path}"}
        
        try:
            torrent_file = self._create_torrent_for_path(path)
            if torrent_file:
                info = self._get_pt_form_info(path) if self._extract_info else {}
                return {
                    "code": 0, 
                    "message": "種子文件已生成", 
                    "data": {
                        "torrent_file": torrent_file,
                        "pt_info": info
                    }
                }
            else:
                return {"code": 1, "message": "種子文件生成失敗"}
        except Exception as e:
            logger.error(f"{self.plugin_name} 生成種子時發生錯誤: {e}")
            return {"code": 1, "message": f"生成種子時發生錯誤: {e}"}

    def api_get_pt_info(self, path: str):
        """API: 获取PT发布信息"""
        if not path or not os.path.exists(path):
            return {"code": 1, "message": "路徑不存在"}
        
        try:
            info = self._get_pt_form_info(path)
            return {"code": 0, "data": info}
        except Exception as e:
            return {"code": 1, "message": f"獲取信息失敗: {e}"}

    def api_get_status(self):
        """API: 获取插件状态"""
        return {
            "code": 0,
            "data": {
                "enabled": self._enabled,
                "running": self._running,
                "monitor_dir": self._monitor_dir,
                "torrent_save_dir": self._torrent_save_dir,
                "client_type": self._client_type,
                "observer_running": self._observer is not None,
                "scheduler_running": self._scheduler and self._scheduler.running
            }
        }

    def get_service(self) -> List[Dict[str, Any]]:
        """獲取定時服務"""
        if self._enabled and self._cron:
            try:
                return [{
                    "id": "PTSeederService",
                    "name": f"{self.plugin_name}定時服務",
                    "trigger": CronTrigger.from_crontab(self._cron),
                    "func": self.run_job,
                    "kwargs": {}
                }]
            except Exception as err:
                logger.error(f"{self.plugin_name} 定時服務配置錯誤：{err}")
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """插件配置表单"""
        return [
            {
                'component': 'VForm',
                'content': [
                    # 基础设置组
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '監控目錄下新增文件並生成種子，方便PT站點發布與做種'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '啟用插件',
                                            'hint': '開啟或關閉插件功能',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify',
                                            'label': '發送通知',
                                            'hint': '生成種子時是否發送通知',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'onlyonce',
                                            'label': '立即運行一次',
                                            'hint': '保存配置後立即執行一次任務',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'extract_info',
                                            'label': '提取PT信息',
                                            'hint': '自動提取PT發布所需信息',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # 目录设置组
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': '目錄設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'monitor_dir',
                                            'label': '監控目錄',
                                            'placeholder': '/path/to/monitor',
                                            'hint': '需要監控的目錄路徑，支持絕對路徑',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'torrent_save_dir',
                                            'label': '種子保存目錄',
                                            'placeholder': '留空使用監控目錄/torrents',
                                            'hint': '生成的種子文件保存位置',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'exclude_dirs',
                                            'label': '排除目錄',
                                            'placeholder': '@eaDir,@Recycle,.DS_Store',
                                            'hint': '要排除的目錄，逗號分隔',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'include_exts',
                                            'label': '包含擴展名',
                                            'placeholder': '.mkv,.mp4,.avi,.rmvb',
                                            'hint': '要包含的文件擴展名，逗號分隔',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'min_file_size',
                                            'label': '最小文件大小(MB)',
                                            'type': 'number',
                                            'min': '0',
                                            'hint': '小於此大小的文件將被忽略',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # 执行设置
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': '執行設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '執行週期',
                                            'hint': '定時掃描目錄的執行週期',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # 种子设置组
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': '種子設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VTextarea',
                                        'props': {
                                            'model': 'trackers',
                                            'label': 'Tracker列表',
                                            'placeholder': 'http://tracker1.example.com:8080/announce\nhttp://tracker2.example.com:8080/announce',
                                            'hint': '種子的Tracker列表，每行一個',
                                            'persistent-hint': True,
                                            'rows': '3',
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'piece_size',
                                            'label': '分片大小',
                                            'items': [
                                                {'title': '自動', 'value': 0},
                                                {'title': '256KB', 'value': 0.25},
                                                {'title': '512KB', 'value': 0.5},
                                                {'title': '1MB', 'value': 1},
                                                {'title': '2MB', 'value': 2},
                                                {'title': '4MB', 'value': 4},
                                                {'title': '8MB', 'value': 8},
                                                {'title': '16MB', 'value': 16}
                                            ],
                                            'hint': '種子分片大小，影響種子文件大小',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'private_torrent',
                                            'label': '私有種子',
                                            'hint': 'PT站點通常需要私有種子',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'source',
                                            'label': '來源標識',
                                            'placeholder': 'Your Site',
                                            'hint': '種子來源標識，如站點名稱',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'comment',
                                            'label': '種子註釋',
                                            'placeholder': '製作說明或其他信息',
                                            'hint': '種子註釋信息',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # 下载器设置
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': '下載器設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'client_type',
                                            'label': '下載器類型',
                                            'items': [
                                                {'title': 'qBittorrent', 'value': 'qbittorrent'},
                                                {'title': 'Transmission', 'value': 'transmission'}
                                            ],
                                            'hint': '選擇要使用的下載器',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'add_to_client',
                                            'label': '添加到下載器',
                                            'hint': '是否自動添加種子到下載器',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'skip_check',
                                            'label': '跳過校驗',
                                            'hint': '添加時跳過文件校驗',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'auto_start',
                                            'label': '自動開始',
                                            'hint': '添加後自動開始做種',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # qBittorrent设置
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': "client_type === 'qbittorrent'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': 'qBittorrent 設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': "client_type === 'qbittorrent'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_url',
                                            'label': 'qBittorrent 地址',
                                            'placeholder': 'http://localhost:8080',
                                            'hint': 'qBittorrent WebUI 地址',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_category',
                                            'label': 'qBittorrent 分類',
                                            'placeholder': 'PT',
                                            'hint': '自動添加的分類標簽',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': "client_type === 'qbittorrent'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_username',
                                            'label': 'qBittorrent 用戶名',
                                            'placeholder': 'admin',
                                            'hint': 'WebUI 登錄用戶名',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_password',
                                            'label': 'qBittorrent 密碼',
                                            'placeholder': 'adminadmin',
                                            'type': 'password',
                                            'hint': 'WebUI 登錄密碼',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_save_path',
                                            'label': 'qBittorrent 保存路徑',
                                            'placeholder': '留空使用監控目錄',
                                            'hint': '種子下載保存路徑',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # Transmission设置
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': "client_type === 'transmission'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': 'Transmission 設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': "client_type === 'transmission'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_host',
                                            'label': 'Transmission 主機',
                                            'placeholder': 'localhost',
                                            'hint': 'Transmission 主機地址',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 2},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_port',
                                            'label': 'Transmission 端口',
                                            'type': 'number',
                                            'placeholder': '9091',
                                            'hint': 'RPC 端口號',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_download_dir',
                                            'label': 'Transmission 下載目錄',
                                            'placeholder': '留空使用監控目錄',
                                            'hint': '種子下載目錄',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': "client_type === 'transmission'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_username',
                                            'label': 'Transmission 用戶名',
                                            'placeholder': '無驗證請留空',
                                            'hint': 'RPC 用戶名',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_password',
                                            'label': 'Transmission 密碼',
                                            'placeholder': '無驗證請留空',
                                            'type': 'password',
                                            'hint': 'RPC 密碼',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # 高级设置
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': '高級設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tags',
                                            'label': '種子標籤',
                                            'placeholder': 'PT,AutoSeed,MyTag',
                                            'hint': '為種子添加的標籤，逗號分隔',
                                            'persistent-hint': True,
                                            'clearable': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'upload_limit',
                                            'label': '上傳限速(KB/s)',
                                            'type': 'number',
                                            'min': '0',
                                            'placeholder': '0',
                                            'hint': '0表示無限制',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'download_limit',
                                            'label': '下載限速(KB/s)',
                                            'type': 'number',
                                            'min': '0',
                                            'placeholder': '0',
                                            'hint': '0表示無限制',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'ratio_limit',
                                            'label': '分享率限制',
                                            'type': 'number',
                                            'step': '0.1',
                                            'min': '0',
                                            'placeholder': '0.0',
                                            'hint': '0表示無限制',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'seed_time_limit',
                                            'label': '做種時限(小時)',
                                            'type': 'number',
                                            'min': '0',
                                            'placeholder': '0',
                                            'hint': '0表示無限制',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # 通知设置
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': '通知設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify_on_success',
                                            'label': '成功通知',
                                            'hint': '種子生成成功時發送通知',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify_on_error',
                                            'label': '錯誤通知',
                                            'hint': '出現錯誤時發送通知',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify_on_duplicate',
                                            'label': '重複通知',
                                            'hint': '發現重複種子時發送通知',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },

                    # PT信息设置
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': 'extract_info'
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VDivider'
                                    },
                                    {
                                        'component': 'VCardSubtitle',
                                        'props': {
                                            'text': 'PT 信息設置'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-show': 'extract_info'
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'copy_to_clipboard',
                                            'label': '複製到剪貼板',
                                            'hint': '自動複製PT信息到剪貼板',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'generate_nfo',
                                            'label': '生成NFO文件',
                                            'hint': '為媒體生成NFO描述文件',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            # 返回当前配置值
            "enabled": self._enabled,
            "cron": self._cron,
            "onlyonce": self._onlyonce,
            "notify": self._notify,
            
            "monitor_dir": self._monitor_dir,
            "torrent_save_dir": self._torrent_save_dir,
            "exclude_dirs": self._exclude_dirs,
            "include_exts": self._include_exts,
            "min_file_size": self._min_file_size,
            
            "trackers": self._trackers,
            "piece_size": self._piece_size,
            "private_torrent": self._private_torrent,
            "source": self._source,
            "comment": self._comment,
            
            "client_type": self._client_type,
            "add_to_client": self._add_to_client,
            "auto_start": self._auto_start,
            "skip_check": self._skip_check,
            
            "qb_url": self._qb_url,
            "qb_username": self._qb_username,
            "qb_password": self._qb_password,
            "qb_category": self._qb_category,
            "qb_save_path": self._qb_save_path,
            
            "tr_host": self._tr_host,
            "tr_port": self._tr_port,
            "tr_username": self._tr_username,
            "tr_password": self._tr_password,
            "tr_download_dir": self._tr_download_dir,
            
            "tags": self._tags,
            "upload_limit": self._upload_limit,
            "download_limit": self._download_limit,
            "ratio_limit": self._ratio_limit,
            "seed_time_limit": self._seed_time_limit,
            
            "extract_info": self._extract_info,
            "copy_to_clipboard": self._copy_to_clipboard,
            "generate_nfo": self._generate_nfo,
            
            "notify_on_error": self._notify_on_error,
            "notify_on_success": self._notify_on_success,
            "notify_on_duplicate": self._notify_on_duplicate
        }
    
    def run_job(self):
        """執行定時任務"""
        if not self._lock.acquire(blocking=False):
            logger.debug(f"{self.plugin_name} 已有任務正在執行，本次調度跳過")
            return
        
        try:
            self._running = True
            logger.info(f"{self.plugin_name} 開始執行任務...")
            
            if not self._validate_config():
                return
            
            # 確保種子保存目錄存在
            os.makedirs(self._torrent_save_dir, exist_ok=True)
            
            # 掃描目錄
            processed_count = 0
            error_count = 0
            
            for root, dirs, files in os.walk(self._monitor_dir):
                # 跳過排除目錄
                dirs[:] = [d for d in dirs if not self._should_exclude_dir(d)]
                
                # 跳過種子保存目錄
                if root == self._torrent_save_dir:
                    continue
                
                # 檢查是否有符合條件的文件
                if self._has_valid_files(root, files):
                    result = self._process_directory(root)
                    if result:
                        processed_count += 1
                    else:
                        error_count += 1
            
            # 發送任務完成通知
            if processed_count > 0 or error_count > 0:
                msg = f"任務完成：成功處理 {processed_count} 個目錄"
                if error_count > 0:
                    msg += f"，失敗 {error_count} 個目錄"
                self._send_notification(msg, NotificationType.Success if error_count == 0 else NotificationType.Warning)
            
            logger.info(f"{self.plugin_name} 任務執行完成：處理 {processed_count} 個目錄，錯誤 {error_count} 個")
            
        except Exception as e:
            logger.error(f"{self.plugin_name} 任務執行出錯: {str(e)}")
            if self._notify_on_error:
                self._send_notification(f"任務執行出錯: {str(e)}", NotificationType.Error)
        finally:
            self._running = False
            self._lock.release()

    def _validate_config(self) -> bool:
        """驗證配置"""
        if not self._monitor_dir or not os.path.isdir(self._monitor_dir):
            logger.error(f"{self.plugin_name} 監控目錄不存在或未設置: {self._monitor_dir}")
            if self._notify_on_error:
                self._send_notification(f"監控目錄不存在或未設置: {self._monitor_dir}", NotificationType.Error)
            return False
        
        if not self._torrent_save_dir:
            self._torrent_save_dir = os.path.join(self._monitor_dir, "torrents")
            logger.info(f"{self.plugin_name} 未設置種子保存目錄，使用默認目錄: {self._torrent_save_dir}")
        
        return True

    def _should_exclude_dir(self, dirname: str) -> bool:
        """檢查是否應該排除目錄"""
        exclude_list = [d.strip() for d in self._exclude_dirs.split(',') if d.strip()]
        return dirname in exclude_list

    def _has_valid_files(self, root: str, files: List[str]) -> bool:
        """檢查目錄是否有有效文件"""
        if not files:
            return False
        
        include_exts = [ext.strip().lower() for ext in self._include_exts.split(',') if ext.strip()]
        min_size_bytes = self._min_file_size * 1024 * 1024  # MB to bytes
        
        for file in files:
            # 跳過種子文件
            if file.endswith('.torrent'):
                continue
            
            file_path = os.path.join(root, file)
            
            # 檢查擴展名
            if include_exts:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in include_exts:
                    continue
            
            # 檢查文件大小
            try:
                if os.path.getsize(file_path) >= min_size_bytes:
                    return True
            except OSError:
                continue
        
        return False

    def _process_directory(self, directory_path: str) -> bool:
        """處理單個目錄"""
        try:
            dir_name = os.path.basename(directory_path)
            torrent_name = f"{dir_name}.torrent"
            torrent_path = os.path.join(self._torrent_save_dir, torrent_name)
            
            # 檢查是否已有種子文件
            if os.path.exists(torrent_path):
                logger.debug(f"{self.plugin_name} 目錄 {dir_name} 已有對應種子文件，跳過")
                if self._notify_on_duplicate:
                    self._send_notification(f"目錄 {dir_name} 已有種子文件", NotificationType.Info)
                return True
            
            # 創建種子文件
            torrent_file = self._create_torrent_for_path(directory_path)
            if not torrent_file:
                logger.error(f"{self.plugin_name} 為 {dir_name} 創建種子文件失敗")
                return False
            
            logger.info(f"{self.plugin_name} 成功為 {dir_name} 創建種子文件: {torrent_file}")
            
            # 發送成功通知
            if self._notify_on_success:
                self._send_notification(f"成功創建種子文件: {os.path.basename(torrent_file)}", NotificationType.Success)
            
            # 添加到下載器
            if self._add_to_client:
                success = False
                if self._client_type == "qbittorrent":
                    success = self._add_to_qbittorrent(torrent_file, directory_path)
                elif self._client_type == "transmission":
                    success = self._add_to_transmission(torrent_file, directory_path)
                
                if success:
                    logger.info(f"{self.plugin_name} 成功添加種子到 {self._client_type}: {os.path.basename(torrent_file)}")
                else:
                    logger.warning(f"{self.plugin_name} 添加種子到 {self._client_type} 失敗: {os.path.basename(torrent_file)}")
            
            # 提取PT信息
            if self._extract_info:
                pt_info = self._get_pt_form_info(directory_path)
                if pt_info and self._notify_on_success:
                    info_text = "\n".join([f"{k}: {v}" for k, v in pt_info.items() if v])
                    self._send_notification(f"PT發布信息:\n{info_text}", NotificationType.Info)
            
            return True
            
        except Exception as e:
            logger.error(f"{self.plugin_name} 處理目錄 {directory_path} 時出錯: {str(e)}")
            if self._notify_on_error:
                self._send_notification(f"處理目錄失敗: {os.path.basename(directory_path)} - {str(e)}", NotificationType.Error)
            return False

    def _create_torrent_for_path(self, path: str) -> Optional[str]:
        """為指定路徑創建種子文件"""
        try:
            # 確保目錄存在
            if not os.path.exists(path):
                logger.error(f"{self.plugin_name} 路徑不存在: {path}")
                return None
            
            # 創建info字典
            info = {}
            info["name"] = os.path.basename(path).encode('utf-8')
            
            # 計算分片長度
            piece_length = self._calculate_piece_size(path)
            info["piece length"] = piece_length
            
            # 添加私有種子標識
            if self._private_torrent:
                info["private"] = 1
            
            # 添加來源標識
            if self._source:
                info["source"] = self._source.encode('utf-8')
            
            pieces = bytearray()
            
            if os.path.isdir(path):
                # 目錄模式
                info["files"] = []
                file_list = []
                
                for root, dirs, files in os.walk(path):
                    dirs.sort()  # 確保目錄按字母排序
                    files.sort()  # 確保文件按字母排序
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, path)
                        file_size = os.path.getsize(file_path)
                        
                        file_info = {
                            "length": file_size,
                            "path": [p.encode('utf-8') for p in rel_path.replace("\\", "/").split("/")]
                        }
                        info["files"].append(file_info)
                        file_list.append((file_path, file_size))
                
                # 生成pieces
                pieces = self._generate_pieces(file_list, piece_length)
            else:
                # 單文件模式
                info["length"] = os.path.getsize(path)
                pieces = self._generate_pieces([(path, info["length"])], piece_length)
            
            info["pieces"] = bytes(pieces)
            
            # 創建torrent字典
            torrent = {
                "info": info,
                "created by": f"MoviePilot PTSeeder {self.plugin_version}".encode('utf-8'),
                "creation date": int(time.time()),
                "encoding": "UTF-8".encode('utf-8')
            }
            
            # 添加註釋
            if self._comment:
                torrent["comment"] = self._comment.encode('utf-8')
            
            # 添加tracker
            if self._trackers:
                tracker_list = [t.strip() for t in self._trackers.strip().split('\n') if t.strip()]
                if tracker_list:
                    torrent["announce"] = tracker_list[0].encode('utf-8')
                    if len(tracker_list) > 1:
                        torrent["announce-list"] = [[t.encode('utf-8')] for t in tracker_list]
            
            # 生成種子文件路徑
            torrent_name = f"{os.path.basename(path)}.torrent"
            torrent_path = os.path.join(self._torrent_save_dir, torrent_name)
            
            # 寫入種子文件
            with open(torrent_path, "wb") as f:
                f.write(bencodepy.encode(torrent))
            
            return torrent_path
            
        except Exception as e:
            logger.error(f"{self.plugin_name} 創建種子文件時出錯: {str(e)}")
            return None

    def _calculate_piece_size(self, path: str) -> int:
        """計算合適的分片大小"""
        if self._piece_size > 0:
            return int(self._piece_size * 1024 * 1024)
        
        # 自動計算分片大小
        total_size = 0
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    total_size += os.path.getsize(os.path.join(root, file))
        else:
            total_size = os.path.getsize(path)
        
        # 根據文件大小自動選擇分片大小
        if total_size < 50 * 1024 * 1024:  # < 50MB
            return 256 * 1024  # 256KB
        elif total_size < 500 * 1024 * 1024:  # < 500MB
            return 512 * 1024  # 512KB
        elif total_size < 2 * 1024 * 1024 * 1024:  # < 2GB
            return 1024 * 1024  # 1MB
        elif total_size < 8 * 1024 * 1024 * 1024:  # < 8GB
            return 2 * 1024 * 1024  # 2MB
        else:
            return 4 * 1024 * 1024  # 4MB

    def _generate_pieces(self, file_list: List[Tuple[str, int]], piece_length: int) -> bytearray:
        """生成pieces哈希"""
        pieces = bytearray()
        current_piece = bytearray()
        
        for file_path, file_size in file_list:
            try:
                with open(file_path, "rb") as f:
                    while True:
                        need_bytes = piece_length - len(current_piece)
                        chunk = f.read(need_bytes)
                        if not chunk:
                            break
                        
                        current_piece.extend(chunk)
                        
                        if len(current_piece) == piece_length:
                            pieces.extend(hashlib.sha1(current_piece).digest())
                            current_piece = bytearray()
            except Exception as e:
                logger.error(f"{self.plugin_name} 讀取文件 {file_path} 時出錯: {e}")
                continue
        
        # 處理最後一個不完整的piece
        if current_piece:
            pieces.extend(hashlib.sha1(current_piece).digest())
        
        return pieces

    def _add_to_qbittorrent(self, torrent_file: str, content_path: str) -> bool:
        """添加種子到qBittorrent"""
        if not qbittorrentapi:
            logger.error(f"{self.plugin_name} 未安裝qBittorrent API庫，無法添加種子")
            return False
        
        try:
            # 連接qBittorrent
            qb = qbittorrentapi.Client(
                host=self._qb_url,
                username=self._qb_username,
                password=self._qb_password
            )
            qb.auth_log_in()
            
            # 準備添加參數
            add_params = {
                'torrent_files': torrent_file,
                'is_skip_checking': self._skip_check,
                'is_paused': not self._auto_start
            }
            
            # 設置保存路徑
            if self._qb_save_path:
                add_params['save_path'] = self._qb_save_path
            else:
                add_params['save_path'] = os.path.dirname(content_path)
            
            # 設置分類
            if self._qb_category:
                add_params['category'] = self._qb_category
            
            # 設置標籤
            if self._tags:
                tags = [tag.strip() for tag in self._tags.split(",") if tag.strip()]
                if tags:
                    add_params['tags'] = tags
            
            # 添加種子
            result = qb.torrents_add(**add_params)
            
            if result == "Ok.":
                # 設置限速
                if self._upload_limit > 0 or self._download_limit > 0:
                    torrent_hash = self._get_torrent_hash(torrent_file)
                    if torrent_hash:
                        if self._upload_limit > 0:
                            qb.torrents_set_upload_limit(limit=self._upload_limit * 1024, torrent_hashes=torrent_hash)
                        if self._download_limit > 0:
                            qb.torrents_set_download_limit(limit=self._download_limit * 1024, torrent_hashes=torrent_hash)
                
                logger.info(f"{self.plugin_name} 成功添加種子到qBittorrent: {os.path.basename(torrent_file)}")
                return True
            else:
                logger.error(f"{self.plugin_name} 添加種子到qBittorrent失敗: {result}")
                return False
                
        except Exception as e:
            logger.error(f"{self.plugin_name} 添加種子到qBittorrent時出錯: {str(e)}")
            return False

    def _add_to_transmission(self, torrent_file: str, content_path: str) -> bool:
        """添加種子到Transmission"""
        if not TransmissionClient:
            logger.error(f"{self.plugin_name} 未安裝Transmission RPC庫，無法添加種子")
            return False
        
        try:
            # 連接Transmission
            client = TransmissionClient(
                host=self._tr_host,
                port=self._tr_port,
                username=self._tr_username if self._tr_username else None,
                password=self._tr_password if self._tr_password else None
            )
            
            # 讀取種子文件
            with open(torrent_file, "rb") as f:
                torrent_data = f.read()
            
            # 準備添加參數
            add_params = {
                'torrent': torrent_data,
                'paused': not self._auto_start
            }
            
            # 設置下載目錄
            if self._tr_download_dir:
                add_params['download_dir'] = self._tr_download_dir
            else:
                add_params['download_dir'] = os.path.dirname(content_path)
            
            # 添加種子
            result = client.add_torrent(**add_params)
            
            if hasattr(result, 'id'):
                torrent_id = result.id
                
                # 設置限速
                if self._upload_limit > 0 or self._download_limit > 0:
                    client.change_torrent(
                        torrent_id,
                        uploadLimit=self._upload_limit if self._upload_limit > 0 else None,
                        downloadLimit=self._download_limit if self._download_limit > 0 else None,
                        uploadLimited=self._upload_limit > 0,
                        downloadLimited=self._download_limit > 0
                    )
                
                logger.info(f"{self.plugin_name} 成功添加種子到Transmission: {os.path.basename(torrent_file)}")
                return True
            else:
                logger.error(f"{self.plugin_name} 添加種子到Transmission失敗: 未獲取到種子ID")
                return False
                
        except Exception as e:
            logger.error(f"{self.plugin_name} 添加種子到Transmission時出錯: {str(e)}")
            return False

    def _get_torrent_hash(self, torrent_file: str) -> Optional[str]:
        """獲取種子哈希值"""
        try:
            with open(torrent_file, "rb") as f:
                torrent_data = bencodepy.decode(f.read())
            info_hash = hashlib.sha1(bencodepy.encode(torrent_data[b'info'])).hexdigest()
            return info_hash
        except Exception:
            return None

    def _get_pt_form_info(self, file_path: str) -> Dict[str, Any]:
        """獲取PT站點發布表單需要的信息"""
        try:
            result = {}
            
            # 提取目錄名或文件名
            name = os.path.basename(file_path)
            result["標題"] = name
            
            # 匹配常見的視頻分辨率
            resolutions = ["2160p", "1080p", "720p", "576p", "480p", "4K", "8K"]
            for res in resolutions:
                if res.lower() in name.lower():
                    result["分辨率"] = res
                    break
            
            # 匹配視頻編碼
            codecs = ["H.265", "H.264", "x265", "x264", "HEVC", "AVC"]
            for codec in codecs:
                if codec.lower() in name.lower():
                    result["視頻編碼"] = codec
                    break
            
            # 匹配音頻格式
            audio_formats = ["DTS-X", "DTS-HD", "DTS", "TrueHD", "Atmos", "AC3", "AAC", "FLAC", "PCM"]
            for fmt in audio_formats:
                if fmt.lower() in name.lower() or fmt in name:
                    result["音頻格式"] = fmt
                    break
            
            # 匹配HDR格式
            hdr_formats = ["HDR10+", "HDR10", "HDR", "Dolby Vision", "DV"]
            for hdr in hdr_formats:
                if hdr.lower() in name.lower():
                    result["HDR"] = hdr
                    break
            
            # 匹配來源
            sources = ["BluRay", "UHD BluRay", "WEB-DL", "WEBRip", "HDTV", "DVDRip", "Remux"]
            for source in sources:
                if source.lower() in name.lower():
                    result["來源"] = source
                    break
            
            # 匹配字幕信息
            if any(x in name.lower() for x in ["简体", "chs", "sc"]):
                result["字幕"] = "简体中文字幕"
            elif any(x in name.lower() for x in ["繁体", "繁體", "cht", "tc"]):
                result["字幕"] = "繁体中文字幕"
            elif "中英" in name:
                result["字幕"] = "中英字幕"
            elif "中日" in name:
                result["字幕"] = "中日字幕"
            elif any(x in name.lower() for x in ["eng", "english"]):
                result["字幕"] = "英文字幕"
            
            # 計算文件大小
            if os.path.isdir(file_path):
                total_size = 0
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            continue
            else:
                total_size = os.path.getsize(file_path)
            
            # 轉換為合適單位
            if total_size >= 1024 * 1024 * 1024 * 1024:  # TB
                result["文件大小"] = f"{total_size / (1024 * 1024 * 1024 * 1024):.2f} TB"
            elif total_size >= 1024 * 1024 * 1024:  # GB
                result["文件大小"] = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
            else:  # MB
                result["文件大小"] = f"{total_size / (1024 * 1024):.2f} MB"
            
            # 檢查是否有NFO文件並提取IMDB鏈接
            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        if file.lower().endswith('.nfo'):
                            nfo_path = os.path.join(root, file)
                            try:
                                with open(nfo_path, "r", encoding="utf-8", errors="ignore") as f:
                                    nfo_content = f.read()
                                    # 提取IMDB ID
                                    imdb_match = re.search(r'tt\d{7,8}', nfo_content)
                                    if imdb_match:
                                        result["IMDB鏈接"] = f"https://www.imdb.com/title/{imdb_match.group(0)}/"
                                    break
                            except Exception as e:
                                logger.warning(f"{self.plugin_name} 讀取NFO文件失敗: {e}")
                    if "IMDB鏈接" in result:
                        break
            
            return result
            
        except Exception as e:
            logger.error(f"{self.plugin_name} 獲取PT站點發布信息失敗: {e}")
            return {"錯誤": str(e)}

    def _start_file_monitor(self):
        """啟動文件監控"""
        try:
            if self._observer:
                self.stop_service()
                
            event_handler = FileCreatedHandler(self)
            self._observer = Observer()
            self._observer.schedule(event_handler, self._monitor_dir, recursive=True)
            self._observer.start()
            logger.info(f"{self.plugin_name} 開始監控目錄: {self._monitor_dir}")
            
        except Exception as e:
            logger.error(f"{self.plugin_name} 啟動文件監控失敗: {e}")

    def _send_notification(self, msg: str, mtype: NotificationType = None):
        """發送通知"""
        if self._notify:
            self.send_message(
                title=f"{self.plugin_name} 通知",
                text=msg,
                mtype=mtype or NotificationType.Info
            )

    def stop_service(self):
        """停止服務"""
        try:
            # 停止文件監控
            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=5)
                self._observer = None
                
            # 停止定時任務
            if self._scheduler and self._scheduler.running:
                self._scheduler.shutdown(wait=False)
                self._scheduler = None
                
            logger.info(f"{self.plugin_name} 服務已停止")
            
        except Exception as e:
            logger.error(f"{self.plugin_name} 停止服務失敗: {e}")


class FileCreatedHandler(FileSystemEventHandler):
    """文件創建事件處理器"""
    
    def __init__(self, plugin: PTSeeder):
        super().__init__()
        self.plugin = plugin

    def on_created(self, event):
        """處理文件創建事件"""
        try:
            if event.is_directory:
                logger.debug(f"{self.plugin.plugin_name} 檢測到新目錄: {event.src_path}")
                
                # 檢查是否是監控目錄的直接子目錄或需要處理的目錄
                if self._should_process_directory(event.src_path):
                    # 延遲處理，等待文件複製完成
                    threading.Timer(30.0, self._delayed_process, [event.src_path]).start()
            
        except Exception as e:
            logger.error(f"{self.plugin.plugin_name} 文件監控事件處理失敗: {e}")

    def _should_process_directory(self, dir_path: str) -> bool:
        """判斷是否應該處理該目錄"""
        # 跳過種子保存目錄
        if dir_path == self.plugin._torrent_save_dir:
            return False
        
        # 跳過排除目錄
        dir_name = os.path.basename(dir_path)
        if self.plugin._should_exclude_dir(dir_name):
            return False
        
        # 只處理監控目錄下的直接子目錄
        parent_dir = os.path.dirname(dir_path)
        return parent_dir == self.plugin._monitor_dir

    def _delayed_process(self, dir_path: str):
        """延遲處理目錄"""
        try:
            # 檢查目錄是否仍然存在且有有效文件
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                if self.plugin._has_valid_files(dir_path, files):
                    logger.info(f"{self.plugin.plugin_name} 開始處理新創建的目錄: {dir_path}")
                    self.plugin._process_directory(dir_path)
                else:
                    logger.debug(f"{self.plugin.plugin_name} 目錄 {dir_path} 沒有有效文件，跳過處理")
            
        except Exception as e:
            logger.error(f"{self.plugin.plugin_name} 延遲處理目錄失敗: {e}") 

