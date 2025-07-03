import os
import random
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, List, Dict, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import re
import threading
import socket

import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase

# ====== 统计相关全局变量和锁（插入到 import 之后，class 之前）======
visit_lock = threading.Lock()
today_visit_count = 0
today_date = datetime.now().date()
# =========================================================

class ImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global today_visit_count, today_date
        # ====== 1. 处理 /stats 路由 ======
        if self.path.startswith('/stats'):
            self._handle_stats_request()
            return
        # ====== 2. 统计 /random 访问量 ======
        if self.path.startswith('/random'):
            with visit_lock:
                now = datetime.now().date()
                if now != today_date:
                    today_visit_count = 0
                    today_date = now
                today_visit_count += 1
        try:
            # logger.info(f"收到请求: {self.path}")
            
            if self.path.startswith('/preview') or self.path == '/':
                self._handle_preview_request()
                return
            
            # 只处理/random请求
            if not self.path.startswith('/random'):
                self.send_error(404, 'Not Found')
                return
                
            # 获取type参数
            type_param = None
            if '?' in self.path:
                type_param = re.search(r'type=(\w+)', self.path)
                if type_param:
                    type_param = type_param.group(1)
                    
            # 判断设备类型
            ua = self.headers.get('User-Agent', '')
            is_mobile = bool(re.search(r'(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)', ua, re.I))
            
            # logger.info(f"设备类型: {'移动端' if is_mobile else 'PC端'}")
            
            # 根据条件选择目录
            if type_param == 'mobile' or (not type_param and is_mobile):
                image_dir = self.server.mobile_path
                # logger.info(f"使用竖屏图片目录: {image_dir}")
            else:
                image_dir = self.server.pc_path
                # logger.info(f"使用横屏图片目录: {image_dir}")
                
            # 获取随机图片
            image_files = []
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp'):
                image_files.extend(Path(image_dir).glob(ext))
                
            if not image_files:
                logger.error(f"目录中没有找到图片: {image_dir}")
                self.send_error(404, 'No images found')
                return
                
            image_path = str(random.choice(image_files))
            # logger.info(f"选择的图片: {image_path}")
            
            try:
                # 获取文件类型和大小
                content_type, _ = mimetypes.guess_type(image_path)
                file_size = os.path.getsize(image_path)
                
                if not content_type or not content_type.startswith('image/'):
                    logger.error(f"不支持的文件类型: {content_type}")
                    self.send_error(415, 'Unsupported Media Type')
                    return
                    
                # 发送响应头
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(file_size))
                self.send_header('Access-Control-Allow-Origin', '*')
                # 添加缓存控制
                self.send_header('Cache-Control', 'no-store') #禁止缓存
                self.end_headers()
                
                # 分块发送图片内容
                with open(image_path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)  # 增大读取缓冲区到64KB
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                        except (BrokenPipeError, ConnectionResetError) as e:
                            logger.warning(f"客户端断开连接: {str(e)}")
                            return
                            
                logger.info(f"图片发送成功: {image_path}")
                    
            except Exception as e:
                logger.error(f'发送图片失败: {str(e)}')
                self.send_error(500, 'Internal Server Error')
                
        except Exception as e:
            logger.error(f'处理请求失败: {str(e)}')
            try:
                self.send_error(500, 'Internal Server Error')
            except:
                pass

    def log_message(self, format, *args):
        """重写日志方法,避免重复输出访问日志"""
        return

    def _handle_preview_request(self):
        """处理Web预览页面请求"""
        try:
            # 获取当前服务器信息
            host = self.headers.get('Host', 'localhost')
            
            # 读取HTML模板文件
            html_file_path = os.path.join(os.path.dirname(__file__), 'preview.html')
            
            if not os.path.exists(html_file_path):
                logger.error(f"HTML模板文件不存在: {html_file_path}")
                self.send_error(500, 'Template file not found')
                return
            
            try:
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except Exception as e:
                logger.error(f"读取HTML模板文件失败: {str(e)}")
                self.send_error(500, 'Failed to read template file')
                return
            
            # 替换模板中的占位符
            html_content = html_content.replace('{HOST}', host)
            
            # 发送HTML响应
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            
            self.wfile.write(html_content.encode('utf-8'))
            # logger.info("Web预览页面返回成功")
            
        except Exception as e:
            logger.error(f'处理Web预览页面请求失败: {str(e)}')
            try:
                self.send_error(500, 'Internal Server Error')
            except:
                pass

    def _handle_stats_request(self):
        """处理统计数据请求，返回图片数量和今日访问量"""
        try:
            pc_path = self.server.pc_path
            mobile_path = self.server.mobile_path
            # 统计横屏图片数量
            pc_count = sum(1 for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp') for _ in Path(pc_path).glob(ext))
            # 统计竖屏图片数量
            mobile_count = sum(1 for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp') for _ in Path(mobile_path).glob(ext))
            total = pc_count + mobile_count
            with visit_lock:
                today = today_visit_count
            # 返回 JSON
            import json
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "total": total,
                "pc": pc_count,
                "mobile": mobile_count,
                "today": today
            }).encode('utf-8'))
        except Exception as e:
            logger.error(f"统计接口异常: {str(e)}")
            try:
                self.send_error(500, 'Internal Server Error')
            except:
                pass


class RandomPic(_PluginBase):
    # 插件名称
    plugin_name = "随机图库"
    # 插件描述
    plugin_desc = "随机图片API服务,支持横屏/竖屏图片分类"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/xijin285/MoviePilot-Plugins/refs/heads/main/icons/randompic.png"
    # 插件版本
    plugin_version = "1.0.3"
    # 插件作者
    plugin_author = "M.Jinxi"
    # 作者主页
    author_url = "https://github.com/xijin285"
    # 插件配置项ID前缀
    plugin_config_prefix = "randompic_"
    # 加载顺序
    plugin_order = 15
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None
    _server = None
    _server_thread = None
    _enabled = False
    _port = None
    _pc_path = None
    _mobile_path = None

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._port = config.get("port")
            self._pc_path = config.get("pc_path")
            self._mobile_path = config.get("mobile_path")

        self.stop_service()

        if self._enabled:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            # logger.info("随机图库服务启动中...")
            self._scheduler.add_job(
                func=self.__run_service,
                trigger="date",
                run_date=datetime.now(tz=pytz.timezone(settings.TZ))
                + timedelta(seconds=2),
                name="随机图库启动服务",
            )

            if self._scheduler.get_jobs():
                self._scheduler.print_jobs()
                self._scheduler.start()

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面
        """
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {
                                    "cols": 12,
                                    "md": 4
                                },
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enabled",
                                            "label": "启用插件"
                                        }
                                    }
                                ]
                            },
                            {
                                "component": "VCol",
                                "props": {
                                    "cols": 12,
                                    "md": 4
                                },
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "port",
                                            "label": "服务端口",
                                            "placeholder": "8002"
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {
                                    "cols": 12
                                },
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "pc_path",
                                            "label": "横屏图片目录",
                                            "placeholder": "/映射目录/横屏图片 (宽>高,如1920x1080)",
                                            "hint": "存放横屏/电脑尺寸的图片目录,要求图片宽度大于高度",
                                            "persistent-hint": True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {
                                    "cols": 12
                                },
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "mobile_path",
                                            "label": "竖屏图片目录",
                                            "placeholder": "/映射目录/竖屏图片 (高>宽,如1080x1920)",
                                            "hint": "存放竖屏/手机尺寸的图片目录,要求图片高度大于宽度",
                                            "persistent-hint": True
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "component": "VCard",
                "props": {
                    "elevation": 1,
                    "class": "mb-4",
                    "style": "border-radius: 12px; background: rgba(33,150,243,0.06);"
                },
                "content": [
                    {
                        "component": "VCardTitle",
                        "props": {"style": "font-size: 20px; font-weight: bold; color: #1976d2; display: flex; align-items: center;"},
                        "content": [
                            {
                                "component": "VIcon",
                                "props": {"color": "info", "size": 24},
                                "text": "mdi-information"
                            },
                            {
                                "component": "span",
                                "props": {"style": "margin-left: 8px;"},
                                "text": "插件使用与API说明"
                            }
                        ]
                    },
                    {
                        "component": "VCardText",
                        "content": [
                            {
                                "component": "VList",
                                "props": {"density": "compact", "style": "background:transparent;box-shadow:none;"},
                                "content": [
                                    {
                                        "component": "VListItem",
                                        "props": {"density": "compact", "style": "align-items:center;"},
                                        "content": [
                                            {"component": "VListItemIcon","content": [{"component": "VIcon", "props": {"color": "primary", "size": 18}, "text": "mdi-numeric-1-circle"}]},
                                            {"component": "span", "props": {"style": "display:inline-block;vertical-align:middle;white-space:nowrap;"}, "text": "配置服务端口(默认8002)"}
                                        ]
                                    },
                                    {
                                        "component": "VListItem",
                                        "props": {"density": "compact", "style": "align-items:center;"},
                                        "content": [
                                            {"component": "VListItemIcon","content": [{"component": "VIcon", "props": {"color": "primary", "size": 18}, "text": "mdi-numeric-2-circle"}]},
                                            {"component": "span", "props": {"style": "display:inline-block;vertical-align:middle;white-space:nowrap;"}, "text": "Docker环境需要映射端口和目录"}
                                        ]
                                    },
                                    {
                                        "component": "VListItem",
                                        "props": {"density": "compact", "style": "align-items:center;"},
                                        "content": [
                                            {"component": "VListItemIcon","content": [{"component": "VIcon", "props": {"color": "primary", "size": 18}, "text": "mdi-numeric-3-circle"}]},
                                            {"component": "span", "props": {"style": "display:inline-block;vertical-align:middle;white-space:nowrap;"}, "text": "支持jpg/jpeg/png/gif/webp格式"}
                                        ]
                                    },
                                    {
                                        "component": "VListItem",
                                        "props": {"density": "compact"},
                                        "content": [
                                            {"component": "VListItemIcon","content": [{"component": "VIcon", "props": {"color": "success", "size": 18}, "text": "mdi-numeric-1-circle"}]},
                                            {"component": "VListItemSubtitle", "text": "Web预览页面: ", "props": {"style": "display:inline;"}},
                                            {"component": "span", "props": {"style": "font-family:monospace;color:#388e3c;"}, "text": "http://IP:端口/preview"}
                                        ]
                                    },
                                    {
                                        "component": "VListItem",
                                        "props": {"density": "compact"},
                                        "content": [
                                            {"component": "VListItemIcon","content": [{"component": "VIcon", "props": {"color": "success", "size": 18}, "text": "mdi-numeric-2-circle"}]},
                                            {"component": "VListItemSubtitle", "text": "自动识别设备: ", "props": {"style": "display:inline;"}},
                                            {"component": "span", "props": {"style": "font-family:monospace;color:#388e3c;"}, "text": "http://IP:端口/random"}
                                        ]
                                    },
                                    {
                                        "component": "VListItem",
                                        "props": {"density": "compact"},
                                        "content": [
                                            {"component": "VListItemIcon","content": [{"component": "VIcon", "props": {"color": "success", "size": 18}, "text": "mdi-numeric-3-circle"}]},
                                            {"component": "VListItemSubtitle", "text": "指定横屏图片: ", "props": {"style": "display:inline;"}},
                                            {"component": "span", "props": {"style": "font-family:monospace;color:#388e3c;"}, "text": "http://IP:端口/random?type=pc"}
                                        ]
                                    },
                                    {
                                        "component": "VListItem",
                                        "props": {"density": "compact"},
                                        "content": [
                                            {"component": "VListItemIcon","content": [{"component": "VIcon", "props": {"color": "success", "size": 18}, "text": "mdi-numeric-4-circle"}]},
                                            {"component": "VListItemSubtitle", "text": "指定竖屏图片: ", "props": {"style": "display:inline;"}},
                                            {"component": "span", "props": {"style": "font-family:monospace;color:#388e3c;"}, "text": "http://IP:端口/random?type=mobile"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "port": "",
            "pc_path": "",
            "mobile_path": ""
        }

    def get_page(self) -> List[dict]:
        pass

    def __run_service(self):
        """
        运行服务
        """
        if not self._port:
            logger.error("未配置端口，无法启动服务")
            return

        if not self._pc_path or not self._mobile_path:
            logger.error("未配置图片目录，无法启动服务")
            return

        # 转换为绝对路径
        pc_path = os.path.abspath(self._pc_path)
        mobile_path = os.path.abspath(self._mobile_path)
        
        # logger.info(f"横屏图片目录: {pc_path}")
        # logger.info(f"竖屏图片目录: {mobile_path}")

        if not os.path.exists(pc_path):
            logger.error(f"横屏图片目录不存在: {pc_path}")
            return

        if not os.path.exists(mobile_path):
            logger.error(f"竖屏图片目录不存在: {mobile_path}")
            return

        try:
            port = int(self._port)
            # logger.info(f"尝试启动HTTP服务器在端口: {port}")
            
            # 检查端口是否被占用
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                logger.error(f"端口 {port} 已被占用")
                return
            sock.close()
            
            # 创建HTTP服务器
            self._server = HTTPServer(('0.0.0.0', port), ImageHandler)
            # 传递图片目录路径给Handler
            self._server.pc_path = pc_path
            self._server.mobile_path = mobile_path
            
            # 在新线程中启动服务器
            self._server_thread = threading.Thread(target=self._server.serve_forever)
            self._server_thread.daemon = True
            self._server_thread.start()
            
            # 获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            except:
                ip = '127.0.0.1'
            finally:
                s.close()
            
            # 启动服务器
            logger.info(f"随机图库服务启动成功! 访问地址: http://{ip}:{port}/random")
        except Exception as e:
            logger.error(f"启动服务失败: {str(e)}")
            logger.error(f"请检查端口 {port} 是否被占用")

    def stop_service(self):
        """
        停止服务
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
            if self._server:
                self._server.shutdown()
                self._server = None
            if self._server_thread:
                self._server_thread.join()
                self._server_thread = None
        except Exception as e:
            logger.error(f"停止服务失败: {str(e)}") 