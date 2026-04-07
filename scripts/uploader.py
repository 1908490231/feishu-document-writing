# -*- coding: utf-8 -*-
"""
飞书图片上传模块
"""

import hashlib
import json
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests
from requests_toolbelt import MultipartEncoder

from .auth import FeishuAuth


class FeishuImageUploader:
    """飞书图片上传模块"""

    UPLOAD_URL = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
    # 临时图片存储目录
    TEMP_IMAGE_DIR = Path(tempfile.gettempdir()) / "feishu_images"

    def __init__(self, auth: FeishuAuth, md_dir: Path = None):
        self.auth = auth
        self.md_dir = md_dir or Path.cwd()
        # 确保临时目录存在
        self.TEMP_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    def download_from_url(self, url: str) -> Optional[Path]:
        """
        从 URL 下载图片到本地临时目录

        Args:
            url: 图片 URL

        Returns:
            本地图片路径 或 None（失败时）
        """
        try:
            # 解析 URL 获取文件扩展名
            parsed_url = urlparse(url)
            url_path = parsed_url.path

            # 从 URL 或参数中提取扩展名
            ext = os.path.splitext(url_path)[1]
            if not ext or ext.lower() not in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}:
                # 尝试从 URL 参数中获取（微信公众号图片格式）
                if 'wx_fmt=' in url:
                    fmt = url.split('wx_fmt=')[-1].split('&')[0]
                    ext_map = {'jpeg': '.jpg', 'jpg': '.jpg', 'png': '.png',
                               'gif': '.gif', 'webp': '.webp', 'bmp': '.bmp'}
                    ext = ext_map.get(fmt, '.jpg')
                else:
                    ext = '.jpg'  # 默认

            # 生成唯一文件名（URL 的 hash 值）
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]
            filename = f"img_{url_hash}{ext}"
            local_path = self.TEMP_IMAGE_DIR / filename

            # 如果已存在，直接返回
            if local_path.exists():
                return local_path

            # 下载图片
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()

            # 保存到本地
            with open(local_path, 'wb') as f:
                f.write(resp.content)

            return local_path

        except Exception as e:
            print(f"警告: 图片下载失败 - {url}: {e}")
            return None

    def resolve_image_path(self, img_path: str) -> Optional[Path]:
        """
        解析图片路径，支持本地路径和网络 URL

        Args:
            img_path: 图片路径（本地相对/绝对路径 或 URL）

        Returns:
            本地图片路径 或 None（失败时）
        """
        # 网络图片
        if img_path.startswith(("http://", "https://")):
            print(f"正在下载网络图片: {img_path[:60]}...")
            return self.download_from_url(img_path)

        # 本地图片
        path = Path(img_path)
        if not path.is_absolute():
            path = self.md_dir / img_path

        if path.exists():
            return path

        print(f"警告: 图片不存在 - {path}")
        return None

    def upload_file(self, file_path: str, document_id: str) -> Optional[str]:
        """
        上传任意文件到飞书文档（用于文档附件）

        Args:
            file_path: 本地文件路径
            document_id: 目标文档 token（docx token）

        Returns:
            file_token 或 None（失败时）
        """
        path = Path(file_path)
        if not path.exists():
            print(f"警告: 文件不存在 - {file_path}")
            return None

        file_size = path.stat().st_size

        try:
            with open(path, "rb") as f:
                form = MultipartEncoder({
                    "file_name": path.name,
                    "parent_type": "docx_file",
                    "parent_node": document_id,
                    "size": str(file_size),
                    "file": (path.name, f, "application/octet-stream")
                })
                headers = {
                    "Authorization": f"Bearer {self.auth.get_token()}",
                    "Content-Type": form.content_type
                }
                resp = requests.post(self.UPLOAD_URL, headers=headers, data=form, timeout=30)
                resp.raise_for_status()
                result = resp.json()

                if result.get("code") != 0:
                    print(f"警告: 文件上传失败 - {file_path}: {result.get('msg')}")
                    return None

                return result.get("data", {}).get("file_token")
        except Exception as e:
            print(f"警告: 文件上传异常 - {file_path}: {e}")
            return None

    def upload_for_import(self, file_path: str, obj_type: str) -> Optional[str]:
        """
        上传文件到飞书，用于 import_tasks 导入流程

        Args:
            file_path: 本地文件路径
            obj_type: 目标文档类型（"docx" 或 "sheet"）

        Returns:
            file_token 或 None（失败时）
        """
        path = Path(file_path)
        if not path.exists():
            print(f"警告: 文件不存在 - {file_path}")
            return None

        ext = path.suffix.lstrip(".")
        file_size = path.stat().st_size
        extra = json.dumps({"obj_type": obj_type, "file_extension": ext})

        try:
            with open(path, "rb") as f:
                form = MultipartEncoder({
                    "file_name": path.name,
                    "parent_type": "ccm_import_open",
                    "size": str(file_size),
                    "extra": extra,
                    "file": (path.name, f, "application/octet-stream")
                })
                headers = {
                    "Authorization": f"Bearer {self.auth.get_token()}",
                    "Content-Type": form.content_type
                }
                resp = requests.post(self.UPLOAD_URL, headers=headers, data=form, timeout=30)
                resp.raise_for_status()
                result = resp.json()

                if result.get("code") != 0:
                    print(f"警告: 导入上传失败 - {file_path}: {result.get('msg')}")
                    return None

                return result.get("data", {}).get("file_token")
        except Exception as e:
            print(f"警告: 导入上传异常 - {file_path}: {e}")
            return None

    def upload(self, image_source: str, parent_node: str) -> Optional[str]:
        """
        上传图片到飞书（支持本地路径和网络 URL）

        Args:
            image_source: 图片路径（本地相对/绝对路径 或 URL）
            parent_node: 图片块的 block_id（必需）

        Returns:
            file_token 或 None（失败时）
        """
        if not parent_node:
            print("警告: 缺少 parent_node 参数")
            return None

        # 解析图片路径（支持本地和网络）
        path = self.resolve_image_path(image_source)
        if not path:
            return None

        # 获取 MIME 类型
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type:
            mime_type = "application/octet-stream"

        headers = {
            "Authorization": f"Bearer {self.auth.get_token()}"
        }

        with open(path, "rb") as f:
            files = {
                "file": (path.name, f, mime_type)
            }
            data = {
                "file_name": path.name,
                "parent_type": "docx_image",
                "parent_node": parent_node,
                "size": str(path.stat().st_size)
            }

            try:
                resp = requests.post(self.UPLOAD_URL, headers=headers, files=files, data=data, timeout=30)
                resp.raise_for_status()
                result = resp.json()

                if result.get("code") != 0:
                    print(f"警告: 图片上传失败 - {image_source}: {result.get('msg')}")
                    return None

                return result.get("data", {}).get("file_token")
            except Exception as e:
                print(f"警告: 图片上传异常 - {image_source}: {e}")
                return None
