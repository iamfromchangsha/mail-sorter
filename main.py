"""
邮件分类助手 - 主入口
"""

import flet as ft
from src.ui.main_app import MainApp, DocumentHead, LaTeXTheme, STYLE
from src.core.imap_client import QQMailClient
from src.core.classifier import MailClassifier, MailCategory
from src.utils.config import ConfigManager
import asyncio


class MailSorterApp:
    """邮件分类助手应用"""

    def __init__(self):
        self.config = ConfigManager()
        self.client: QQMailClient = None
        self.classifier = MailClassifier()
        self.app: MainApp = None

    def run(self):
        """运行应用"""
        ft.app(target=self._main)

    def _main(self, page: ft.Page):
        """主界面"""
        self.app = MainApp(page)

        # 设置回调
        self.app.on_connect_callback = self._connect
        self.app.on_disconnect_callback = self._disconnect
        self.app.on_classify_callback = self._classify

        # 加载已有配置
        self.config.load_config()
        if self.config.has_credentials():
            self.app.email_input = self.config.config.email_config.email
            self.app.status_message = "已加载保存的配置"
            self.app.update_status()

    async def _connect(self, email: str, auth_code: str) -> bool:
        """连接邮箱"""
        try:
            self.client = QQMailClient(email, auth_code)
            success = self.client.connect()
            if success:
                self.config.save_credentials(email, auth_code)
                # 创建分类文件夹
                folders = ["简历分类", "报告分类", "广告分类", "通知分类", "验证码分类"]
                for folder in folders:
                    self.client.create_folder(folder)
            return success
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def _disconnect(self):
        """断开连接"""
        if self.client:
            self.client.disconnect()
            self.client = None

    async def _classify(self) -> dict:
        """执行分类"""
        if not self.client:
            return {}

        try:
            # 拉取邮件
            emails = self.client.fetch_emails(limit=100)
            if not emails:
                return {}

            # 转换为分类器需要的格式
            email_dicts = [
                {
                    "uid": m.uid,
                    "subject": m.subject,
                    "sender": m.sender,
                    "body_preview": m.body_preview,
                    "date": m.date,
                }
                for m in emails
            ]

            # 执行分类
            results = self.classifier.classify_batch(email_dicts)

            # 移动邮件到对应文件夹
            for category, category_emails in results.items():
                if category == MailCategory.UNKNOWN:
                    continue

                folder_name = self.config.get_folder_for_category(category.value[0])
                if not folder_name:
                    continue

                for email in category_emails:
                    self.client.move_email(
                        mail_uid=email["uid"],
                        source_folder="INBOX",
                        target_folder=folder_name
                    )

            return results

        except Exception as e:
            print(f"分类失败: {e}")
            return {}


def main():
    """主入口"""
    app = MailSorterApp()
    app.run()


if __name__ == "__main__":
    main()
