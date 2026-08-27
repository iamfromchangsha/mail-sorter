"""
配置管理
处理凭据存储和分类规则配置
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List


@dataclass
class EmailConfig:
    """邮箱配置"""
    email: str = ""
    auth_code: str = ""
    imap_server: str = "imap.qq.com"
    imap_port: int = 993


@dataclass
class FolderMapping:
    """文件夹映射"""
    category: str
    folder_name: str
    enabled: bool = True


@dataclass
class AppConfig:
    """应用配置"""
    email_config: EmailConfig = None
    folder_mappings: List[FolderMapping] = None
    auto_classify: bool = True
    max_emails_per_run: int = 100

    def __post_init__(self):
        if self.email_config is None:
            self.email_config = EmailConfig()
        if self.folder_mappings is None:
            # 默认文件夹映射
            self.folder_mappings = [
                FolderMapping("简历类", "简历分类"),
                FolderMapping("报告类", "报告分类"),
                FolderMapping("广告类", "广告分类"),
                FolderMapping("通知类", "通知分类"),
                FolderMapping("验证码类", "验证码分类"),
            ]


class ConfigManager:
    """配置管理器"""

    CONFIG_DIR = Path.home() / ".mail-sorter"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
    EXAMPLE_FILE = Path(__file__).parent.parent.parent / ".env.example"

    def __init__(self):
        self.config = AppConfig()
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._create_example_file()

    def _create_example_file(self):
        """创建示例配置文件"""
        if not self.EXAMPLE_FILE.exists():
            example_content = """# QQ邮箱分类助手 - 环境配置示例
# 复制此文件为 .env 并填入真实凭据

# QQ邮箱地址
MAIL_SORTER_EMAIL=your_email@qq.com

# QQ邮箱授权码（不是登录密码）
# 获取方式：QQ邮箱设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 -> 生成授权码
MAIL_SORTER_AUTH_CODE=your_auth_code_here

# IMAP服务器配置（通常不需要修改）
MAIL_SORTER_IMAP_SERVER=imap.qq.com
MAIL_SORTER_IMAP_PORT=993

# 每次最多处理邮件数
MAIL_SORTER_MAX_EMAILS=100
"""
            try:
                self.EXAMPLE_FILE.write_text(example_content, encoding='utf-8')
            except Exception:
                pass

    def load_config(self) -> bool:
        """
        加载配置

        Returns:
            是否加载成功
        """
        try:
            if self.CREDENTIALS_FILE.exists():
                with open(self.CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config.email_config = EmailConfig(**data.get('email_config', {}))
                    self.config.auto_classify = data.get('auto_classify', True)
                    self.config.max_emails_per_run = data.get('max_emails_per_run', 100)

            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    mappings = data.get('folder_mappings', [])
                    self.config.folder_mappings = [
                        FolderMapping(**m) for m in mappings
                    ] if mappings else self.config.folder_mappings

            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False

    def save_config(self) -> bool:
        """
        保存配置

        Returns:
            是否保存成功
        """
        try:
            # 保存凭据
            credentials_data = {
                'email_config': asdict(self.config.email_config),
                'auto_classify': self.config.auto_classify,
                'max_emails_per_run': self.config.max_emails_per_run,
            }
            with open(self.CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
                json.dump(credentials_data, f, ensure_ascii=False, indent=2)

            # 保存文件夹映射
            config_data = {
                'folder_mappings': [asdict(m) for m in self.config.folder_mappings]
            }
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def save_credentials(self, email: str, auth_code: str) -> bool:
        """
        保存邮箱凭据

        Args:
            email: 邮箱地址
            auth_code: 授权码

        Returns:
            是否保存成功
        """
        self.config.email_config.email = email
        self.config.email_config.auth_code = auth_code
        return self.save_config()

    def has_credentials(self) -> bool:
        """检查是否已有凭据"""
        return bool(
            self.config.email_config.email and
            self.config.email_config.auth_code
        )

    def clear_credentials(self):
        """清除凭据"""
        self.config.email_config = EmailConfig()
        try:
            if self.CREDENTIALS_FILE.exists():
                self.CREDENTIALS_FILE.unlink()
        except Exception:
            pass

    def get_folder_for_category(self, category: str) -> Optional[str]:
        """
        获取分类对应的文件夹名

        Args:
            category: 分类名称

        Returns:
            文件夹名称，未找到返回None
        """
        for mapping in self.config.folder_mappings:
            if mapping.category == category and mapping.enabled:
                return mapping.folder_name
        return None

    def update_folder_mapping(self, category: str, folder_name: str, enabled: bool = True):
        """更新文件夹映射"""
        for mapping in self.config.folder_mappings:
            if mapping.category == category:
                mapping.folder_name = folder_name
                mapping.enabled = enabled
                break
        self.save_config()

    @classmethod
    def get_example_path(cls) -> Path:
        """获取示例文件路径"""
        return cls.EXAMPLE_FILE
