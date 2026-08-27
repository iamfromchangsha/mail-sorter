"""
邮件分类助手 - 主入口
支持桌面和移动端
"""

import flet as ft
from src.core.imap_client import QQMailClient
from src.core.classifier import MailClassifier, MailCategory
from src.utils.config import ConfigManager


class MailSorterApp:
    """邮件分类助手应用"""

    def __init__(self):
        self.config = ConfigManager()
        self.client: QQMailClient = None
        self.classifier = MailClassifier()

        # 状态
        self.is_connected = False
        self.is_classifying = False
        self.classification_results = {}

    def build(self):
        """构建界面"""
        # 状态引用
        status_ref = ft.Ref[str]()

        def on_connect(e):
            if self.is_classifying:
                return
            email = email_field.value
            auth_code = auth_field.value
            if not email or not auth_code:
                status_text.value = "请输入邮箱和授权码"
                page.update()
                return

            status_text.value = "正在连接..."
            page.update()

            self.client = QQMailClient(email, auth_code)
            if self.client.connect():
                self.is_connected = True
                self.config.save_credentials(email, auth_code)
                # 创建分类文件夹
                folders = ["简历分类", "报告分类", "广告分类", "通知分类", "验证码分类"]
                for folder in folders:
                    self.client.create_folder(folder)
                status_text.value = "连接成功"
                connect_btn.text = "已连接"
                connect_btn.disabled = True
            else:
                status_text.value = "连接失败，请检查凭据"
            page.update()

        def on_disconnect(e):
            if self.client:
                self.client.disconnect()
                self.client = None
            self.is_connected = False
            status_text.value = "已断开"
            connect_btn.text = "连接"
            connect_btn.disabled = False
            page.update()

        async def on_classify(e):
            if not self.is_connected:
                status_text.value = "请先连接邮箱"
                page.update()
                return
            if self.is_classifying:
                return

            self.is_classifying = True
            progress_bar.visible = True
            status_text.value = "正在分类..."
            page.update()

            try:
                # 拉取邮件
                emails = self.client.fetch_emails(limit=100)
                if not emails:
                    status_text.value = "收件箱为空"
                    return

                # 转换为分类器格式
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
                self.classification_results = self.classifier.classify_batch(email_dicts)

                # 更新结果卡片
                results_container.controls.clear()
                for category, category_emails in self.classification_results.items():
                    if not category_emails:
                        continue

                    category_name = category.value[0] if hasattr(category, 'value') else str(category)

                    results_container.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"{category_name}: {len(category_emails)} 封", weight=ft.FontWeight.W_600),
                            ]),
                            bgcolor="#F5F5F0",
                            border=ft.border.only(left=ft.border.BorderSide(2, "#111111")),
                            padding=15,
                        )
                    )

                status_text.value = f"分类完成，共 {len(emails)} 封邮件"

            except Exception as ex:
                status_text.value = f"分类失败: {str(ex)}"

            finally:
                self.is_classifying = False
                progress_bar.visible = False
                page.update()

        # 页面
        page = ft.Page()
        page.title = "邮件分类助手"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 400
        page.window_height = 700

        # 组件
        email_field = ft.TextField(label="邮箱地址", hint_text="your_email@qq.com")
        auth_field = ft.TextField(label="授权码", password=True, hint_text="QQ邮箱授权码")
        connect_btn = ft.ElevatedButton("连接", on_click=on_connect)
        disconnect_btn = ft.OutlinedButton("断开", on_click=on_disconnect)
        classify_btn = ft.ElevatedButton("开始分类", on_click=on_classify)
        progress_bar = ft.ProgressBar(visible=False)
        status_text = ft.Text("未连接", size=12, color="#6B6B66")
        results_container = ft.Column([])

        # 布局
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("邮件分类助手", size=24, weight=ft.FontWeight.W_700),
                    ft.Text("基于规则的智能 QQ 邮件分类", size=12, color="#6B6B66"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                alignment=ft.alignment.center,
            ),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    email_field,
                    auth_field,
                    ft.Row([connect_btn, disconnect_btn]),
                ], spacing=15),
                padding=20,
            ),
            ft.Container(
                content=ft.Column([
                    classify_btn,
                    progress_bar,
                    status_text,
                ], spacing=10),
                padding=20,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("分类结果", weight=ft.FontWeight.W_600),
                    results_container,
                ], spacing=10),
                padding=20,
            ),
        )

        return page


def main(page: ft.Page):
    """主入口"""
    app = MailSorterApp()
    app.build()


if __name__ == "__main__":
    ft.app(target=main)
