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
    plugin_desc = "监控目录下新增文件并生成种子，方便PT站点发布"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/yujiajie01/MoviePilot-Plugins/refs/heads/main/icons/randompic.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "Author"
    # 作者主页
    author_url = "https://github.com/yujiajie01"
    # 插件配置项ID前缀
    plugin_config_prefix = "ptseeder_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _cron = "*/5 * * * *"  # 默认每5分钟执行一次
    _onlyonce = False
    _notify = False
    _scheduler = None
    _observer = None
    _running = False
    _lock = None
    
    # 监控目录
    _monitor_dir = ""
    # 种子保存目录
    _torrent_save_dir = ""
    # Tracker列表
    _trackers = ""
    # 下载器类型 (qbittorrent 或 transmission)
    _client_type = "qbittorrent"
    # QB 连接信息
    _qb_url = "http://localhost:8080"
    _qb_username = "admin"
    _qb_password = "adminadmin"
    # TR 连接信息
    _tr_host = "localhost"
    _tr_port = 9091
    _tr_username = "admin"
    _tr_password = "adminadmin"
    # 种子标签
    _tags = ""

    def init_plugin(self, config: Optional[dict] = None):
        self.stop_service()
        
        # 初始化锁
        self._lock = threading.Lock()
        
        # 加载配置
        if config:
            self._enabled = config.get("enabled", False)
            self._cron = config.get("cron", "*/5 * * * *")
            self._onlyonce = config.get("onlyonce", False)
            self._notify = config.get("notify", False)
            self._monitor_dir = config.get("monitor_dir", "")
            self._torrent_save_dir = config.get("torrent_save_dir", "")
            self._trackers = config.get("trackers", "")
            self._client_type = config.get("client_type", "qbittorrent")
            self._qb_url = config.get("qb_url", "http://localhost:8080")
            self._qb_username = config.get("qb_username", "admin")
            self._qb_password = config.get("qb_password", "adminadmin")
            self._tr_host = config.get("tr_host", "localhost")
            self._tr_port = config.get("tr_port", 9091)
            self._tr_username = config.get("tr_username", "admin")
            self._tr_password = config.get("tr_password", "adminadmin")
            self._tags = config.get("tags", "")
            
            # 更新配置
            self._update_config()
        
        # 处理立即运行一次的情况
        if self._onlyonce:
            try:
                if not self._scheduler:
                    self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                job_name = f"{self.plugin_name}服务_onlyonce"
                if self._scheduler.get_job(job_name):
                    self._scheduler.remove_job(job_name)
                logger.info(f"{self.plugin_name} 服务启动，立即运行一次")
                self._scheduler.add_job(func=self.run_job, trigger='date',
                                        run_date=datetime.now(),
                                        name=job_name, id=job_name)
                if not self._scheduler.running:
                    self._scheduler.start()
                self._onlyonce = False
                self._update_config()
            except Exception as e:
                logger.error(f"启动一次性 {self.plugin_name} 任务失败: {str(e)}")
        
        # 启动文件监控
        if self._enabled and self._monitor_dir and os.path.isdir(self._monitor_dir):
            self._start_file_monitor()

    def get_state(self) -> bool:
        return self._enabled

    def _update_config(self):
        self.update_config({
            "enabled": self._enabled,
            "cron": self._cron,
            "onlyonce": self._onlyonce,
            "notify": self._notify,
            "monitor_dir": self._monitor_dir,
            "torrent_save_dir": self._torrent_save_dir,
            "trackers": self._trackers,
            "client_type": self._client_type,
            "qb_url": self._qb_url,
            "qb_username": self._qb_username,
            "qb_password": self._qb_password,
            "tr_host": self._tr_host,
            "tr_port": self._tr_port,
            "tr_username": self._tr_username,
            "tr_password": self._tr_password,
            "tags": self._tags
        })

    def get_command(self) -> List[Dict[str, Any]]:
        """返回命令列表"""
        return [{
            "cmd": "/ptseeder",
            "desc": "手动扫描目录并生成种子",
            "category": "PT工具",
            "data": {}
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """注册API接口"""
        return [
            {
                "path": "/run",
                "endpoint": self.api_run,
                "methods": ["GET"],
                "summary": "立即运行种子生成任务"
            },
            {
                "path": "/generate",
                "endpoint": self.api_generate_torrent,
                "methods": ["POST"],
                "summary": "为指定路径生成种子文件"
            }
        ]

    def api_run(self):
        """API: 立即运行种子生成任务"""
        self.run_job()
        return {"code": 0, "message": "已开始扫描目录并生成种子"}
    
    def api_generate_torrent(self, path: str):
        """API: 为指定路径生成种子"""
        if not os.path.exists(path):
            return {"code": 1, "message": f"路径不存在: {path}"}
        
        try:
            torrent_file = self._create_torrent_for_path(path)
            if torrent_file:
                return {"code": 0, "message": f"种子文件已生成", "data": {"torrent_file": torrent_file}}
            else:
                return {"code": 1, "message": "种子文件生成失败"}
        except Exception as e:
            logger.error(f"{self.plugin_name} 生成种子时发生错误: {e}")
            return {"code": 1, "message": f"生成种子时发生错误: {e}"}

    def get_service(self) -> List[Dict[str, Any]]:
        """获取定时服务"""
        if self._enabled and self._cron:
            try:
                return [{
                    "id": "PTSeederService",
                    "name": f"{self.plugin_name}定时服务",
                    "trigger": CronTrigger.from_crontab(self._cron),
                    "func": self.run_job,
                    "kwargs": {}
                }]
            except Exception as err:
                logger.error(f"{self.plugin_name} 定时服务配置错误：{err}")
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """插件配置表单"""
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify',
                                            'label': '发送通知'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'onlyonce',
                                            'label': '立即运行一次'
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
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'monitor_dir',
                                            'label': '监控目录',
                                            'placeholder': '请输入需要监控的目录路径'
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
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'torrent_save_dir',
                                            'label': '种子保存目录',
                                            'placeholder': '请输入种子文件保存的目录路径'
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
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '执行周期'
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
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'trackers',
                                            'label': 'Tracker列表',
                                            'placeholder': '请输入Tracker URL，多个使用逗号分隔'
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
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tags',
                                            'label': '种子标签',
                                            'placeholder': '为种子添加的标签，多个使用逗号分隔'
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
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'client_type',
                                            'label': '下载器类型',
                                            'items': [
                                                {'title': 'qBittorrent', 'value': 'qbittorrent'},
                                                {'title': 'Transmission', 'value': 'transmission'}
                                            ]
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
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VDivider',
                                        'props': {
                                            'class': 'mt-2 mb-4'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-if': "client_type === 'qbittorrent'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_url',
                                            'label': 'qBittorrent地址',
                                            'placeholder': 'http://localhost:8080'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-if': "client_type === 'qbittorrent'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_username',
                                            'label': 'qBittorrent用户名',
                                            'placeholder': 'admin'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'qb_password',
                                            'label': 'qBittorrent密码',
                                            'placeholder': 'adminadmin',
                                            'type': 'password'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-if': "client_type === 'transmission'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_host',
                                            'label': 'Transmission主机',
                                            'placeholder': 'localhost'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_port',
                                            'label': 'Transmission端口',
                                            'type': 'number',
                                            'placeholder': '9091'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'props': {
                            'v-if': "client_type === 'transmission'"
                        },
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_username',
                                            'label': 'Transmission用户名',
                                            'placeholder': 'admin'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'tr_password',
                                            'label': 'Transmission密码',
                                            'placeholder': 'adminadmin',
                                            'type': 'password'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": self._enabled,
            "cron": self._cron,
            "onlyonce": self._onlyonce,
            "notify": self._notify,
            "monitor_dir": self._monitor_dir,
            "torrent_save_dir": self._torrent_save_dir,
            "trackers": self._trackers,
            "client_type": self._client_type,
            "qb_url": self._qb_url,
            "qb_username": self._qb_username,
            "qb_password": self._qb_password,
            "tr_host": self._tr_host,
            "tr_port": self._tr_port,
            "tr_username": self._tr_username,
            "tr_password": self._tr_password,
            "tags": self._tags
        }
    
    def run_job(self):
        """执行定时任务"""
        if not self._lock.acquire(blocking=False):
            logger.debug(f"{self.plugin_name} 已有任务正在执行，本次调度跳过")
            return
        
        try:
            self._running = True
            logger.info(f"{self.plugin_name} 开始执行任务...")
            
            if not self._monitor_dir or not os.path.isdir(self._monitor_dir):
                logger.error(f"{self.plugin_name} 监控目录不存在或未设置: {self._monitor_dir}")
                self._send_notification(f"监控目录不存在或未设置: {self._monitor_dir}", NotificationType.Error)
                return
            
            if not self._torrent_save_dir:
                self._torrent_save_dir = os.path.join(self._monitor_dir, "torrents")
                logger.info(f"{self.plugin_name} 未设置种子保存目录，将使用默认目录: {self._torrent_save_dir}")
            
            # 确保种子保存目录存在
            os.makedirs(self._torrent_save_dir, exist_ok=True)
            
            # 扫描目录
            logger.info(f"{self.plugin_name} 扫描目录: {self._monitor_dir}")
            for root, dirs, files in os.walk(self._monitor_dir):
                # 跳过种子保存目录
                if root == self._torrent_save_dir:
                    continue
                
                # 检查是否有媒体文件
                for file in files:
                    # 跳过种子文件
                    if file.endswith(".torrent"):
                        continue
                    
                    # 跳过小文件
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) < 10 * 1024 * 1024:  # 小于10MB的文件跳过
                        continue
                    
                    # 处理目录内容
                    self._process_directory(root)
                    break
            
            logger.info(f"{self.plugin_name} 任务执行完成")
        except Exception as e:
            logger.error(f"{self.plugin_name} 任务执行出错: {str(e)}")
            self._send_notification(f"任务执行出错: {str(e)}", NotificationType.Error)
        finally:
            self._running = False
            self._lock.release()
    
    def _process_directory(self, directory_path):
        """处理单个目录"""
        try:
            # 检查目录是否有对应的种子文件
            dir_name = os.path.basename(directory_path)
            torrent_name = f"{dir_name}.torrent"
            torrent_path = os.path.join(self._torrent_save_dir, torrent_name)
            
            if os.path.exists(torrent_path):
                logger.debug(f"{self.plugin_name} 目录 {dir_name} 已有对应种子文件，跳过")
                return
            
            # 创建种子文件
            torrent_file = self._create_torrent_for_path(directory_path)
            if torrent_file:
                logger.info(f"{self.plugin_name} 成功为 {dir_name} 创建种子文件: {torrent_file}")
                self._send_notification(f"成功创建种子文件: {torrent_file}", NotificationType.Success)
                
                # 添加到下载器
                if self._client_type == "qbittorrent":
                    self._add_to_qbittorrent(torrent_file, directory_path)
                elif self._client_type == "transmission":
                    self._add_to_transmission(torrent_file, directory_path)
            else:
                logger.error(f"{self.plugin_name} 为 {dir_name} 创建种子文件失败")
        except Exception as e:
            logger.error(f"{self.plugin_name} 处理目录 {directory_path} 时出错: {str(e)}")
    
    def _create_torrent_for_path(self, path):
        """为指定路径创建种子文件"""
        try:
            import bencodepy
            
            # 确保目录存在
            if not os.path.exists(path):
                logger.error(f"{self.plugin_name} 路径不存在: {path}")
                return None
            
            # 创建info字典
            info = {}
            info["name"] = os.path.basename(path)
            
            # 设置piece长度为1MB
            piece_length = 1024 * 1024  # 1MB
            info["piece length"] = piece_length
            
            # 获取文件列表和生成pieces
            if os.path.isdir(path):
                info["files"] = []
                pieces = bytearray()
                
                for root, dirs, files in os.walk(path):
                    # 按字母排序
                    files.sort()
                    dirs.sort()
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, path)
                        file_size = os.path.getsize(file_path)
                        
                        # 添加到files列表
                        file_info = {
                            "length": file_size,
                            "path": rel_path.replace("\\", "/").split("/")
                        }
                        info["files"].append(file_info)
                        
                        # 生成pieces
                        with open(file_path, "rb") as f:
                            while True:
                                chunk = f.read(piece_length)
                                if not chunk:
                                    break
                                pieces.extend(hashlib.sha1(chunk).digest())
            else:
                # 单文件
                info["length"] = os.path.getsize(path)
                pieces = bytearray()
                
                with open(path, "rb") as f:
                    while True:
                        chunk = f.read(piece_length)
                        if not chunk:
                            break
                        pieces.extend(hashlib.sha1(chunk).digest())
            
            # 设置pieces
            info["pieces"] = bytes(pieces)
            
            # 创建torrent字典
            torrent = {
                "info": info,
                "announce": self._trackers.split(",")[0] if self._trackers else "",
                "created by": f"MoviePilot PTSeeder {self.plugin_version}",
                "creation date": int(time.time()),
                "encoding": "UTF-8"
            }
            
            # 添加announce-list
            if "," in self._trackers:
                announce_list = [[tracker.strip()] for tracker in self._trackers.split(",") if tracker.strip()]
                if announce_list:
                    torrent["announce-list"] = announce_list
            
            # 确保种子保存目录存在
            os.makedirs(self._torrent_save_dir, exist_ok=True)
            
            # 生成种子文件路径
            torrent_name = f"{os.path.basename(path)}.torrent"
            torrent_path = os.path.join(self._torrent_save_dir, torrent_name)
            
            # 写入种子文件
            with open(torrent_path, "wb") as f:
                f.write(bencodepy.encode(torrent))
            
            return torrent_path
        except Exception as e:
            logger.error(f"{self.plugin_name} 创建种子文件时出错: {str(e)}")
            return None
    
    def _add_to_qbittorrent(self, torrent_file, content_path):
        """添加种子到qBittorrent"""
        if not qbittorrentapi:
            logger.error(f"{self.plugin_name} 未安装qBittorrent API库，无法添加种子")
            return False
        
        try:
            # 连接qBittorrent
            qb = qbittorrentapi.Client(
                host=self._qb_url,
                username=self._qb_username,
                password=self._qb_password
            )
            qb.auth_log_in()
            
            # 获取标签列表
            tags = [tag.strip() for tag in self._tags.split(",") if tag.strip()]
            
            # 添加种子
            result = qb.torrents_add(
                torrent_files=torrent_file,
                save_path=content_path,
                is_skip_checking=True,
                tags=tags if tags else None
            )
            
            if result == "Ok.":
                logger.info(f"{self.plugin_name} 成功添加种子到qBittorrent: {os.path.basename(torrent_file)}")
                return True
            else:
                logger.error(f"{self.plugin_name} 添加种子到qBittorrent失败: {result}")
                return False
        except Exception as e:
            logger.error(f"{self.plugin_name} 添加种子到qBittorrent时出错: {str(e)}")
            return False
    
    def _add_to_transmission(self, torrent_file, content_path):
        """添加种子到Transmission"""
        if not TransmissionClient:
            logger.error(f"{self.plugin_name} 未安装Transmission RPC库，无法添加种子")
            return False
        
        try:
            # 连接Transmission
            client = TransmissionClient(
                host=self._tr_host,
                port=self._tr_port,
                username=self._tr_username,
                password=self._tr_password
            )
            
            # 读取种子文件
            with open(torrent_file, "rb") as f:
                torrent_data = f.read()
            
            # 添加种子
            result = client.add_torrent(
                torrent=torrent_data,
                download_dir=content_path,
            )
            
            # 添加标签
            if hasattr(result, "id") and self._tags:
                tags = [tag.strip() for tag in self._tags.split(",") if tag.strip()]
                if tags:
                    for tag in tags:
                        try:
                            client.add_torrent_tags([result.id], [tag])
                        except Exception as e:
                            logger.warning(f"{self.plugin_name} 添加标签 {tag} 失败: {e}")
            
            logger.info(f"{self.plugin_name} 成功添加种子到Transmission: {os.path.basename(torrent_file)}")
            return True
        except Exception as e:
            logger.error(f"{self.plugin_name} 添加种子到Transmission时出错: {str(e)}")
            return False
    
    def _start_file_monitor(self):
        """启动文件监控"""
        try:
            if self._observer:
                self.stop_service()
                
            event_handler = FileCreatedHandler(self)
            self._observer = Observer()
            self._observer.schedule(event_handler, self._monitor_dir, recursive=True)
            self._observer.start()
            logger.info(f"{self.plugin_name} 开始监控目录: {self._monitor_dir}")
        except Exception as e:
            logger.error(f"{self.plugin_name} 启动文件监控失败: {e}")
    
    def _send_notification(self, msg, mtype=None):
        """发送通知"""
        if self._notify:
            self.send_message(
                title=f"{self.plugin_name} 通知",
                text=msg,
                mtype=mtype or NotificationType.Info
            )
    
    def _get_pt_form_info(self, file_path):
        """获取PT站点发布表单需要的信息"""
        try:
            result = {}
            
            # 提取目录名或文件名
            name = os.path.basename(file_path)
            result["标题"] = name
            
            # 匹配常见的视频分辨率
            resolutions = ["720p", "1080p", "2160p", "4K", "8K"]
            for res in resolutions:
                if res.lower() in name.lower():
                    result["分辨率"] = res
                    break
            
            # 匹配音频格式
            audio_formats = ["DTS", "DTS-HD", "TrueHD", "Atmos", "AC3", "AAC", "FLAC"]
            for fmt in audio_formats:
                if fmt.lower() in name.lower() or fmt in name:
                    result["音频格式"] = fmt
                    break
            
            # 匹配字幕信息
            if "简体" in name or "chs" in name.lower() or "zh" in name.lower():
                result["字幕"] = "中文字幕"
            elif "繁体" in name or "cht" in name.lower():
                result["字幕"] = "繁体字幕"
            elif "中英" in name:
                result["字幕"] = "中英字幕"
            elif "中日" in name:
                result["字幕"] = "中日字幕"
            
            # 计算文件大小
            if os.path.isdir(file_path):
                total_size = 0
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        total_size += os.path.getsize(os.path.join(root, file))
            else:
                total_size = os.path.getsize(file_path)
            
            # 转换为GB或MB
            if total_size > 1024 * 1024 * 1024:
                result["文件大小"] = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
            else:
                result["文件大小"] = f"{total_size / (1024 * 1024):.2f} MB"
            
            # 检查是否有NFO文件
            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        if file.endswith(".nfo"):
                            nfo_path = os.path.join(root, file)
                            try:
                                with open(nfo_path, "r", encoding="utf-8") as f:
                                    nfo_content = f.read()
                                    # 提取IMDB ID
                                    imdb_match = re.search(r'tt\d{7,8}', nfo_content)
                                    if imdb_match:
                                        result["IMDB链接"] = f"https://www.imdb.com/title/{imdb_match.group(0)}/"
                            except Exception as e:
                                logger.warning(f"{self.plugin_name} 读取NFO文件失败: {e}")
                            break
            
            return result
        except Exception as e:
            logger.error(f"{self.plugin_name} 获取PT站点发布信息失败: {e}")
            return {"错误": str(e)}
    
    def stop_service(self):
        """停止服务"""
        try:
            # 停止文件监控
            if self._observer:
                self._observer.stop()
                self._observer.join()
                self._observer = None
                
            # 停止定时任务
            if self._scheduler and self._scheduler.running:
                self._scheduler.shutdown()
                self._scheduler = None
                
            logger.info(f"{self.plugin_name} 服务已停止")
        except Exception as e:
            logger.error(f"{self.plugin_name} 停止服务失败: {e}")


class FileCreatedHandler(FileSystemEventHandler):
    """文件创建事件处理器"""
    
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
    
    def on_created(self, event):
        # 只处理文件创建事件
        if event.is_directory:
            logger.info(f"检测到新目录: {event.src_path}")
            # 检查是否是监控目录的直接子目录
            if os.path.dirname(event.src_path) == self.plugin._monitor_dir:
                # 稍等一会儿让文件复制完成
                threading.Timer(10.0, self.plugin._process_directory, [event.src_path]).start() 
