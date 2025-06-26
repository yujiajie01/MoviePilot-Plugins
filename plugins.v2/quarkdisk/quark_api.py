import ast
import time
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

import pytz
import requests
import urllib.parse

import schemas
from app.core.config import settings
from app.log import logger


class QuarkApi:
    """
    夸克网盘基础操作
    """

    # FileId和路径缓存
    _id_cache: Dict[str, str] = {}
    
    # 请求重试次数
    _max_retries = 3
    
    # 请求超时时间(秒)
    _timeout = 30

    def __init__(self, cookie: str):
        try:
            self._cookie = cookie.strip()
            self._disk_name = "夸克网盘"
            self._base_url = "https://pan.quark.cn/1/clouddrive"
            logger.info(f"【夸克】初始化API客户端, Cookie长度: {len(cookie)}")
            
            # 解析Cookie
            try:
                cookie_dict = {}
                for item in cookie.split(";"):
                    if "=" in item:
                        key, value = item.strip().split("=", 1)
                        cookie_dict[key] = value
                # logger.info(f"【夸克】Cookie解析结果: {cookie_dict.keys()}")
                
                # 验证cookie是否有效
                try:
                    logger.info("【夸克】开始验证Cookie（通过list接口）")
                    from app import schemas
                    root_item = schemas.FileItem(
                        storage=self._disk_name,
                        fileid="0",
                        parent_fileid=None,
                        name="/",
                        basename="/",
                        extension=None,
                        type="dir",
                        path="/",
                        size=None,
                        modify_time=None,
                        pickcode=None
                    )
                    items = self.list(root_item)
                    if items is None:
                        raise Exception("Cookie验证失败: 无法获取根目录文件列表")
                    logger.info(f"【夸克】Cookie验证成功，根目录文件数: {len(items)}")
                except Exception as e:
                    logger.error(f"【夸克】Cookie验证失败: {str(e)}")
                    raise
                
            except Exception as e:
                logger.error(f"【夸克】解析Cookie失败: {str(e)}")
                raise
                
            # 生成设备ID
            device_id = str(int(time.time() * 1000))
            
            def filter_cookies(cookie_str, exclude_keys):
                filtered = []
                for item in cookie_str.split(';'):
                    if '=' in item:
                        key, value = item.strip().split('=', 1)
                        if key not in exclude_keys:
                            filtered.append(f"{key}={value}")
                return '; '.join(filtered)
            
            self._headers = {
                "Cookie": self._cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Content-Type": "application/json;charset=UTF-8",
                "Referer": "https://pan.quark.cn",
                "Origin": "https://pan.quark.cn",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "x-requested-with": "XMLHttpRequest",
                "x-device-id": device_id,
                "x-client-version": "3.1.0",
                "x-platform-version": "web",
                "x-platform-type": "web",
                "x-sdk-version": "3.1.0",
                "x-web-timestamp": str(int(time.time() * 1000)),
                "x-device-model": "web",
                "x-device-name": "Chrome",
                "x-device-platform": "web",
                "x-app-id": "30",
                "x-app-version": "3.1.0",
                "x-app-package": "com.quark.pan"
            }
            # 日志输出前过滤Cookie字段
            filtered_headers = self._headers.copy()
            filtered_headers["Cookie"] = filter_cookies(self._headers["Cookie"], ["_UP_A4A_11_", "_UP_D_", "_qk_bx_ck_v1", "tfstk"])
            # logger.info(f"【夸克】请求头: {filtered_headers}")
            
        except Exception as e:
            logger.error(f"【夸克】初始化API客户端失败: {str(e)}")
            raise

    def _path_to_id(self, path: str):
        """
        通过路径获取ID
        """
        try:
            logger.info(f"【夸克】开始获取路径 {path} 的ID")
            
            # 根目录
            if path == "/" or path == "":
                logger.info("【夸克】根目录ID为0")
                return "0"
                
            if len(path) > 1 and path.endswith("/"):
                path = path[:-1]
                
            # 检查缓存
            if path in self._id_cache:
                logger.info(f"【夸克】从缓存获取到ID: {self._id_cache[path]}")
                return self._id_cache[path]
                
            # 确保路径以/开头
            if not path.startswith("/"):
                path = "/" + path
                
            logger.info(f"【夸克】开始逐级查找路径: {path}")
            
            parts = [p for p in Path(path).parts if p != "/"]
            if not parts:
                return "0"
                
            current_id = "0"
            for part in parts:
                try:
                    logger.info(f"【夸克】查找目录 {part} (当前ID: {current_id})")
                    
                    # 更新时间戳和设备ID
                    current_time = int(time.time() * 1000)
                    device_id = f"web_{current_time}"
                    
                    headers = {
                        "Cookie": self._cookie,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Content-Type": "application/json;charset=UTF-8",
                        "Referer": "https://pan.quark.cn",
                        "Origin": "https://pan.quark.cn",
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "x-requested-with": "XMLHttpRequest",
                        "x-device-id": device_id,
                        "x-client-version": "3.1.0",
                        "x-platform-version": "web",
                        "x-platform-type": "web",
                        "x-sdk-version": "3.1.0",
                        "x-web-timestamp": str(current_time),
                        "x-device-model": "web",
                        "x-device-name": "Chrome",
                        "x-device-platform": "web",
                        "x-app-id": "30",
                        "x-app-version": "3.1.0",
                        "x-app-package": "com.quark.pan",
                        "x-web-timezone": "8",
                        "x-web-source": "pc",
                        "x-web-os": "web",
                        "x-web-browser": "Chrome",
                        "x-web-browser-version": "122.0.0.0"
                    }
                    
                    request_data = {
                        "pdir_fid": current_id,
                        "limit": 100,
                        "start": 0,
                        "with_audit": 1,
                        "filters": {"phase": "all"},
                        "orderBy": [{"field": "file_name", "order": "asc"}],
                        "_web_timestamp": current_time
                    }
                    
                    api_url = f"{self._base_url}/file/list"
                    logger.debug(f"【夸克】请求URL: {api_url}")
                    logger.debug(f"【夸克】请求头: {headers}")
                    logger.debug(f"【夸克】请求参数: {request_data}")
                    
                    # 添加重试机制
                    for retry in range(self._max_retries):
                        try:
                            resp = requests.post(
                                api_url,
                                headers=headers,
                                json=request_data,
                                timeout=self._timeout
                            )
                            logger.info(f"【夸克】第{retry + 1}次尝试请求文件列表")
                            logger.info(f"【夸克】API响应状态码: {resp.status_code}")
                            logger.debug(f"【夸克】API响应头: {dict(resp.headers)}")
                            
                            if resp.status_code == 200:
                                break
                            elif retry == self._max_retries - 1:
                                logger.error(f"【夸克】请求失败,状态码: {resp.status_code}")
                                return None
                            else:
                                time.sleep(1)
                                continue
                                
                        except requests.exceptions.RequestException as e:
                            if retry == self._max_retries - 1:
                                logger.error(f"【夸克】API请求失败: {str(e)}")
                                return None
                            else:
                                time.sleep(1)
                                continue
                    
                    try:
                        resp_text = resp.text
                        logger.debug(f"【夸克】API响应内容: {resp_text}")
                        resp_json = resp.json()
                    except ValueError as e:
                        logger.error(f"【夸克】解析响应JSON失败: {str(e)}")
                        logger.error(f"【夸克】响应内容: {resp_text}")
                        return None
                    
                    if resp_json.get("code") != 0:
                        error_msg = resp_json.get("message", "未知错误")
                        logger.error(f"【夸克】获取文件列表失败: {error_msg}")
                        logger.error(f"【夸克】完整响应: {resp_text}")
                        return None
                        
                    found = False
                    for item in resp_json.get("data", {}).get("list", []):
                        if item["file_name"] == part:
                            current_id = str(item["fid"])
                            found = True
                            logger.info(f"【夸克】找到目录 {part} 的ID: {current_id}")
                            break
                            
                    if not found:
                        logger.error(f"【夸克】未找到目录: {part}")
                        return None
                        
                except Exception as e:
                    logger.error(f"【夸克】查找目录ID失败: {str(e)}")
                    return None
                    
            # 缓存结果
            self._id_cache[path] = current_id
            logger.info(f"【夸克】路径 {path} 的最终ID为: {current_id}")
            return current_id
            
        except Exception as e:
            logger.error(f"【夸克】获取路径ID失败: {str(e)}")
            return None

    def list(self, fileitem: schemas.FileItem) -> List[schemas.FileItem]:
        """
        获取文件列表（新版，完全模拟网页端接口，GET方式）
        """
        try:
            items = []
            page = 1
            size = 50
            logger.info(f"【夸克】开始获取目录 {fileitem.path} 的文件列表（新版/sort接口）")
            parent_id = self._path_to_id(fileitem.path)
            if not parent_id:
                logger.error(f"【夸克】获取文件列表失败: 无法获取目录ID {fileitem.path}")
                return []
            logger.info(f"【夸克】目录 {fileitem.path} 的ID为 {parent_id}")
            while True:
                try:
                    logger.info(f"【夸克】请求第 {page} 页文件列表")
                    # 拼接url参数
                    params = {
                        "pr": "ucpro",
                        "fr": "pc",
                        "uc_param_str": "",
                        "pdir_fid": parent_id,
                        "_page": page,
                        "_size": size,
                        "_fetch_total": 1,
                        "_fetch_sub_dirs": 0,
                        "_sort": "file_type:asc,updated_at:desc"
                    }
                    url = "https://drive-pc.quark.cn/1/clouddrive/file/sort?" + urllib.parse.urlencode(params)
                    # 构造headers
                    headers = {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Cache-Control": "no-cache",
                        "Cookie": self._cookie,
                        "Origin": "https://pan.quark.cn",
                        "Pragma": "no-cache",
                        "Priority": "u=1",
                        "Referer": "https://pan.quark.cn/",
                        "Sec-Ch-Ua": '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"macOS"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
                    }
                    resp = requests.get(url, headers=headers)
                    logger.info(f"【夸克】API响应状态码: {resp.status_code}")
                    if resp.status_code != 200:
                        logger.error(f"【夸克】请求失败,状态码: {resp.status_code}")
                        return []
                    resp_json = resp.json()
                    if resp_json.get("code") != 0:
                        error_msg = resp_json.get("message", "未知错误")
                        logger.error(f"【夸克】获取文件列表失败: {error_msg}")
                        return []
                    data = resp_json.get("data", {})
                    item_list = data.get("list", [])
                    if not item_list:
                        logger.info("【夸克】没有更多文件")
                        break
                    for item in item_list:
                        try:
                            path = f"{fileitem.path}{item['file_name']}"
                            if not path.startswith("/"):
                                path = "/" + path
                            self._id_cache[path] = str(item["fid"])
                            file_path = path + ("/" if item["file_type"] == 0 else "")
                            file_item = schemas.FileItem(
                                storage=fileitem.storage,
                                fileid=str(item["fid"]),
                                parent_fileid=str(item["pdir_fid"]),
                                name=item["file_name"],
                                basename=path.split("/")[-1],
                                extension=None,
                                type="dir" if item["file_type"] == 0 else "file",
                                path=file_path,
                                size=item.get("size"),
                                modify_time=int(item.get("updated_at", 0)),
                                pickcode=str(item),
                            )
                            items.append(file_item)
                        except Exception as e:
                            logger.error(f"【夸克】处理文件项失败: {str(e)}")
                            continue
                    if len(item_list) < size:
                        break
                    page += 1
                except Exception as e:
                    logger.error(f"【夸克】获取文件列表失败: {str(e)}")
                    return []
            logger.info(f"【夸克】共获取到 {len(items)} 个文件")
            return items
        except Exception as e:
            logger.error(f"【夸克】获取文件列表失败: {str(e)}")
            return []

    def get_item(self, path: Path) -> Optional[schemas.FileItem]:
        """
        获取文件信息
        """
        try:
            file_id = self._path_to_id(str(path))
            if not file_id:
                return None
            resp = requests.post(
                f"{self._base_url}/file/info",
                headers=self._headers,
                json={
                    "fid": file_id
                }
            ).json()
            if resp.get("code") != 0:
                return None
            item = resp.get("data")
            if not item:
                return None
            return schemas.FileItem(
                storage=self._disk_name,
                fileid=str(item["fid"]),
                parent_fileid=str(item["parent_id"]),
                name=item["file_name"],
                basename=Path(item["file_name"]).stem,
                extension=Path(item["file_name"]).suffix[1:]
                if item["file_type"] == 1
                else None,
                type="dir" if item["file_type"] == 0 else "file",
                path=str(path),
                size=item["size"] if item["file_type"] == 1 else None,
                modify_time=int(item["modified_time"]),
                pickcode=str(item),
            )
        except Exception as e:
            logger.error(f"【夸克】获取文件信息失败: {str(e)}")
            return None

    def get_parent(self, fileitem: schemas.FileItem) -> Optional[schemas.FileItem]:
        """
        获取父目录
        """
        try:
            parent_path = str(Path(fileitem.path).parent)
            if parent_path == ".":
                parent_path = "/"
            return self.get_item(Path(parent_path))
        except Exception as e:
            logger.error(f"【夸克】获取父目录失败: {str(e)}")
            return None

    def create_folder(self, fileitem: schemas.FileItem, name: str) -> Optional[schemas.FileItem]:
        """
        创建文件夹
        """
        try:
            parent_id = self._path_to_id(fileitem.path)
            if not parent_id:
                return None
            resp = requests.post(
                f"{self._base_url}/file/create",
                headers=self._headers,
                json={
                    "parent_id": parent_id,
                    "file_name": name,
                    "file_type": 0
                }
            ).json()
            if resp.get("code") != 0:
                return None
            item = resp.get("data")
            if not item:
                return None
            path = f"{fileitem.path}{name}/"
            self._id_cache[path[:-1]] = str(item["fid"])
            return schemas.FileItem(
                storage=self._disk_name,
                fileid=str(item["fid"]),
                parent_fileid=str(item["parent_id"]),
                name=item["file_name"],
                basename=Path(item["file_name"]).stem,
                extension=None,
                type="dir",
                path=path,
                size=None,
                modify_time=int(item["modified_time"]),
                pickcode=str(item),
            )
        except Exception as e:
            logger.error(f"【夸克】创建文件夹失败: {str(e)}")
            return None

    def upload(self, fileitem: schemas.FileItem, path: Path, new_name: Optional[str] = None) -> Optional[schemas.FileItem]:
        """
        上传文件
        """
        try:
            parent_id = self._path_to_id(fileitem.path)
            if not parent_id:
                return None
            # 获取上传地址
            resp = requests.post(
                f"{self._base_url}/file/upload/init",
                headers=self._headers,
                json={
                    "parent_id": parent_id,
                    "file_name": new_name or path.name,
                    "size": path.stat().st_size
                }
            ).json()
            if resp.get("code") != 0:
                return None
            upload_data = resp.get("data")
            if not upload_data:
                return None
            # 上传文件
            with open(path, "rb") as f:
                resp = requests.put(
                    upload_data["url"],
                    headers={
                        "Content-Type": "application/octet-stream",
                    },
                    data=f
                )
                if resp.status_code != 200:
                    return None
            # 完成上传
            resp = requests.post(
                f"{self._base_url}/file/upload/complete",
                headers=self._headers,
                json={
                    "upload_id": upload_data["upload_id"]
                }
            ).json()
            if resp.get("code") != 0:
                return None
            item = resp.get("data")
            if not item:
                return None
            path = f"{fileitem.path}{new_name or path.name}"
            self._id_cache[path] = str(item["fid"])
            return schemas.FileItem(
                storage=self._disk_name,
                fileid=str(item["fid"]),
                parent_fileid=str(item["parent_id"]),
                name=item["file_name"],
                basename=Path(item["file_name"]).stem,
                extension=Path(item["file_name"]).suffix[1:],
                type="file",
                path=path,
                size=item["size"],
                modify_time=int(item["modified_time"]),
                pickcode=str(item),
            )
        except Exception as e:
            logger.error(f"【夸克】上传文件失败: {str(e)}")
            return None

    def download(self, fileitem: schemas.FileItem, path: Path = None) -> Optional[Path]:
        """
        下载文件
        """
        try:
            file_id = self._path_to_id(fileitem.path)
            if not file_id:
                return None
            # 获取下载地址
            resp = requests.post(
                f"{self._base_url}/file/download",
                headers=self._headers,
                json={
                    "fids": [file_id]
                }
            ).json()
            if resp.get("code") != 0:
                return None
            download_data = resp.get("data", [])
            if not download_data:
                return None
            # 下载文件
            resp = requests.get(
                download_data[0]["download_url"],
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                },
                stream=True
            )
            if resp.status_code != 200:
                return None
            # 保存文件
            if not path:
                path = Path(settings.TEMP_PATH) / fileitem.name
            with open(path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return path
        except Exception as e:
            logger.error(f"【夸克】下载文件失败: {str(e)}")
            return None

    def delete(self, fileitem: schemas.FileItem) -> Optional[bool]:
        """
        删除文件
        """
        try:
            file_id = self._path_to_id(fileitem.path)
            if not file_id:
                return None
            resp = requests.post(
                f"{self._base_url}/file/delete",
                headers=self._headers,
                json={
                    "fids": [file_id]
                }
            ).json()
            if resp.get("code") != 0:
                return None
            return True
        except Exception as e:
            logger.error(f"【夸克】删除文件失败: {str(e)}")
            return None

    def rename(self, fileitem: schemas.FileItem, name: str) -> Optional[bool]:
        """
        重命名文件
        """
        try:
            file_id = self._path_to_id(fileitem.path)
            if not file_id:
                return None
            resp = requests.post(
                f"{self._base_url}/file/rename",
                headers=self._headers,
                json={
                    "fid": file_id,
                    "file_name": name
                }
            ).json()
            if resp.get("code") != 0:
                return None
            return True
        except Exception as e:
            logger.error(f"【夸克】重命名文件失败: {str(e)}")
            return None

    def usage(self) -> Optional[schemas.StorageUsage]:
        """
        获取存储空间使用情况
        """
        try:
            resp = requests.post(
                "https://pan.quark.cn/1/clouddrive/capacity",
                headers=self._headers
            ).json()
            if resp.get("code") != 0:
                return None
            data = resp.get("data")
            if not data:
                return None
            return schemas.StorageUsage(
                total=data["total_capacity"],
                used=data["used_capacity"],
                free=data["total_capacity"] - data["used_capacity"]
            )
        except Exception as e:
            logger.error(f"【夸克】获取存储空间使用情况失败: {str(e)}")
            return None 